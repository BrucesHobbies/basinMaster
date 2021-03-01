#!/usr/bin/env python

"""
Copyright(C) 2021, BrucesHobbies
All Rights Reserved

AUTHOR: BrucesHobbies
DATE: 02/04/2021
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2021/02/10  BrucesHobbies   added pubScribe.py


OVERVIEW:
    This program supports multiple different types of range and pressure
    sensors to estimate water column depth. Logging of the pressure 
    measurements,

    Current list of sensors:
    - HC_SR04 Ultrasonic range finder measures range to surface of water
      Pros: low cost, simple
      Cons: potential reflection off other objects - solve using PVC pipe with holes
    - Honeywell ABP pressure sensors
      Pros: good accuracy
      Cons: pressure leaks from tubes, add bubbler pump to presurize before taking measurement
      (low-cost aquarium type bubbler (<2-watts) with a "T" in air supply hose to sensor)

    Future sensor options:
    - US-100 (3.3V, echo time serial)
    - GP2YOA21
    - VL53L3CX

LICENSE:
    This program code and documentation are for personal private use only. 
    No commercial use of this code is allowed without prior written consent.

    This program is free for you to inspect, study, and modify for your 
    personal private use. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import sys
import os
import time
import datetime
import math

import pubScribe


#
# === User configuration === RPi pins are defined in individual files
#
ENABLE_HC_SR04 = 1           # Ultra-sonic range finder option
ENABLE_HNY_ABP = 1           # Honeywell ABP pressure sensor option

# ABP for Amplified Basic Pressure sensor
# ABP_SENSOR = "060MG2"      # ABP sensor model, see sensorHnyAbp for details
ABP_SENSOR = "001PDS"        # ABP sensor model, see sensorHnyAbp for details

# US for UltraSonic ranging sensor
US_MEAS_AVERAGING = 11       # Number of ultra-sonic measurements to average
US_WELL_DEPTH     = 18       # Depth in inches from bottom of sump well to ultra-sonic sensor

# csv log file
depthGaugeLogEnable = 1

# inches of water column delta required before logging
US_GAUGE_DELTA_LOG  = 0.5
ABP_GAUGE_DELTA_LOG = 0.5
depthGaugeLogAll    = 1     # ignore delta log params and log all measurements

measTime    = 60            # Seconds between water depth measurements
pumpOnTime  = 5             # Seconds to run pump for ABP
pumpOffTime = 5             # Seconds to wait after running pump before reading pressure
PUMP_ON = True              # True = logic level high for on, False = low for on

#
# --- User Email Alerts Configuration ---
#
# First time program starts, it will ask you for the sender's email
# this should be an email that you have established for sending alerts from this program
# gmail is suggested with "Less Secure App Access" turned on. This is required for Python on the RPI.
# If you change passwords, please delete cfgData.json so that this program will again ask for the password.
#

alertMsgEnabled  = 0                        # non zero enables sending of email / SMS text messages
statusMsgEnabled = 1                        # non zero enables sending of email / SMS text messages
statusMsgHHMM    = [12, 30]                 # Status message time to send [hh, mm]

WATER_DEPTH_ALERT         = 9               # Send alert when water depth greater than this many inches
WATER_DEPTH_ALERT_ENABLE  = 1               # Enable sending alerts
minIntervalBtwWaterEmails = 24*3600         # seconds

#
# === END USER CONFIGURATION ===
#


if ENABLE_HC_SR04 or ENABLE_HNY_ABP:
    # Needed in both cases for gpio functions
    import hc_sr04_range

if ENABLE_HNY_ABP :
    import sensorHnyAbp


abp = []

measCnt    = 0            # updated in timer loop

pumpOnCnt  = 0            # Calculated during initialization
pumpOffCnt = 0            # Calculated during initialization

# Last readings
last_us_result  = -99.0
last_abp_result = -99.0

last_us_t = time.localtime()
last_abp_t = last_us_t

# Last log values
last_us_log  = -99.0
last_abp_log = -99.0


us_meas = []              # Ultrasonic measurements for averaging


#
# Initial range and depth sensors
#
def gaugeInit(tInterval) : 
    global abp, measCnt, pumpOnCnt, pumpOffCnt

    measCnt = int(measTime/tInterval) - 1

    pumpOffCnt = int(pumpOffTime/tInterval)
    if pumpOffTime % tInterval :
        pumpOffCnt += 1

    pumpOnCnt = int(pumpOnTime/tInterval)

    if pumpOffCnt < 1 :
        pumpOffCnt = 1

    if pumpOnCnt < 1 :
        pumpOnCnt = 1

    pumpOnCnt += pumpOffCnt
    if pumpOnTime % tInterval :
        pumpOnCnt += 1

    if measCnt < pumpOnCnt :
        measCnt = pumpOnCnt

    if measCnt <= US_MEAS_AVERAGING :
        measCnt = US_MEAS_AVERAGING + 1

    if ENABLE_HC_SR04 or ENABLE_HNY_ABP:
        hc_sr04_range.sensorInit()            # Needed in both cases for gpio functions

    if ENABLE_HNY_ABP :
        print("Water depth pressure sensor:")
        abp = sensorHnyAbp.SensorHnyAbp(ABP_SENSOR)

    return


#
# Called before program exits
#
def gaugeClose() : 
    if ENABLE_HC_SR04 or ENABLE_HNY_ABP :
        hc_sr04_range.sensorClose()           # Close gpio functions


#
# Read water depth sensors
#
def gaugeRead(tInterval) :
    global last_us_result, last_us_t, last_abp_result, last_abp_t
    global measCnt, us_meas
    global last_us_log, last_abp_log

    us_result = -99
    abp_result = -99

    csv_str = ""
    deltaLogResult = 0

    if measCnt :
        # Pump cycle on-off logic prior to measurement
        if ENABLE_HNY_ABP and (measCnt <= pumpOnCnt) :
            if (measCnt > pumpOffCnt) : 
                hc_sr04_range.pump(PUMP_ON)    # Low-cost aquarium bubbler pump to pressurize depth tube
            else :
                hc_sr04_range.pump(not PUMP_ON)

        if ENABLE_HC_SR04 and (measCnt <= US_MEAS_AVERAGING) :
            # Series of range measures to average
            dist = hc_sr04_range.sensorRead()
            if dist :
                us_meas.append(dist)

        measCnt -= 1

    else :
        measCnt = int(measTime/tInterval) - 1
        t = time.localtime()
        
        if ENABLE_HC_SR04 :
            # Average ultrasonic measurements
            cnt = len(us_meas)
            if cnt > (US_MEAS_AVERAGING // 2) :
                mean = sum(us_meas) / cnt
                # variance = sum([((x - mean) ** 2) for x in us_meas]) / cnt
                # res = variance ** 0.5
                us_result = round(US_WELL_DEPTH - mean, 2)

                if us_result != -99 :
                    last_us_result = us_result
                    last_us_t = t

                    if (abs(us_result - last_us_log) > US_GAUGE_DELTA_LOG) :
                        deltaLogResult = 1
                        last_us_log = us_result

            us_meas = []


        if ENABLE_HNY_ABP :
            # Get pressure reading
            status, result, tempC = abp.readAbpStatusTemp()
            if status == 0 :
                abp_result = round(abp.pres2inwc(result),2)

                if abp_result != -99 :
                    last_abp_result = abp_result
                    last_abp_t = t

                    if (abs(abp_result - last_abp_log) > ABP_GAUGE_DELTA_LOG) :
                        deltaLogResult = 1
                        last_abp_log = abp_result

            else :
               print("Water depth pressure sensor fault...")

        if (depthGaugeLogEnable and (deltaLogResult or depthGaugeLogAll)) :
            topic = "basinMaster/WaterDepth"
            data = {"Ultrasonic (in)": round(us_result,2), "ABP (in)": round(abp_result,2)}
            pubScribe.pubRecord(pubScribe.CSV_FILE, topic, data)

    return us_result, abp_result


#
# Send alert via email to another email or as SMS text
#
def sendAlert(subj, alertMsg) :
    topic = "basinMaster/Alert"
    pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, alertMsg)


#
# Send status via email to another email or as SMS text
#
def sendStatus() :
    s = time.strftime("\n%a, %d %b %Y %H:%M:%S ", last_us_t)
    s = s + "US: {: 6.2f}\n".format(last_us_result)

    s = s + time.strftime("%a, %d %b %Y %H:%M:%S ", last_abp_t)
    s = s + "ABP: {: 6.2f}\n".format(last_abp_result)

    topic = "basinMaster/Status"
    pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, s)


#
# Test / debug main
#
if __name__ == '__main__':

    # tInterval = 0.5
    # tInterval = 1
    tInterval = 2

    waterDepthLastEmailTime = 0
    lastStatusMsg = 0

    pubScribe.connectPubScribe()

    gaugeInit(tInterval)

    if statusMsgEnabled :
        topic = "basinMaster/Status"
        pubScribe.pubRecord(pubScribe.EMAIL_SMS, topic, "Program start")

    print("\nPress CTRL+C to exit...\n")
    print("First set of measurement will display in a few minutes...\n")

    try :
        while (True) :
            usMeas, abpMeas = gaugeRead(tInterval)
            if usMeas!=-99 or abpMeas!=-99 :
                s = time.strftime("%a, %d %b %Y %H:%M:%S ", time.localtime())
                print("{}Ultrasonic depth= {: 6.2f}, ABP depth= {: 6.2f}".format(s, usMeas, abpMeas))


                if WATER_DEPTH_ALERT_ENABLE :
                    if (usMeas != -99) and (usMeas > WATER_DEPTH_ALERT) :
                        tsec = time.time()
                        if (tsec > (minIntervalBtwWaterEmails + waterDepthLastEmailTime)) :
                            # Allowed to send email text message
                            waterDepthLastEmailTime = tsec
                            sendAlert("basinMaster Alert", "Water Depth: " + str(usMeas) + "\n")

                    if (abpMeas != -99) and (abpMeas > WATER_DEPTH_ALERT) :
                        tsec = time.time()
                        if (tsec > (minIntervalBtwWaterEmails + waterDepthLastEmailTime)) :
                            # Allowed to send email text message
                            waterDepthLastEmailTime = tsec
                            sendAlert("basinMaster Alert", "ABP Water Depth: " + str(abpMeas) + "\n")

            # send daily status email to email or to SMS text
            t = datetime.datetime.now()
            tsec = time.time()
            if (statusMsgEnabled and t.hour==statusMsgHHMM[0] and t.minute==statusMsgHHMM[1] and (tsec >= (lastStatusMsg+12*3600)) ) :
                lastStatusMsg = tsec
                sendStatus()

            time.sleep(tInterval)

    except KeyboardInterrupt :
        print(" Keyboard interrupt caught.")

    gaugeClose()
    print("GPIO cleaned up.")
    pubScribe.disconnectPubScribe()
