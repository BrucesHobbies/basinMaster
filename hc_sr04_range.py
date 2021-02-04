#!/usr/bin/env python

"""
Copyright(C) 2021, BrucesHobbies
All Rights Reserved

AUTHOR: BrucesHobbies
DATE: 02/01/2021
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------

GENERAL INFO
  Sump/well water level
    - Ultrasonic depth sensor  HC-SR04 (5V, echo time using GPIO)

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


ECHO goes to a voltage divider of 2/3 (5kOhm and 10kOhm) to convert 5 V output to 3.3 V
RPi inputs cannot be exposed to voltages less than 0 or greater than 3.3 volts.

RPI			          HC-SR04
----------------          -------
Pin  2 (5Vdc)             Vcc
Pin  6 (GND)	          GND
Pin 16 (GPIO23)           TRIG
Pin 18 (GPIO24)   
 from 2kOhm divider and 1kOhm divider -    ECHO (5V -> 3.3V)

RPI			          Pump relay driver
----------------          -------
Pin 12 (GPIO18)           Trigger
Pin 14 (GND)              Driver- / Gnd
Pin  2 (5Vdc)             Driver+ / Power
 -or-
Pin  4 (5Vdc)             Driver+ / Power
Pin  1 (3.3Vdc)           3.3Vdc Power

"""

import RPi.GPIO as GPIO
import time
import sys

PUMP = 18    # GPIO18 RPi3 pin 12
TRIG = 23    # GPIO23 RPi3 pin 16
ECHO = 24    # GPIO24 RPi3 pin 18


#
# Initialize GPIO and wait for ultrasonic sensor to stabilize
#
def sensorInit() :
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP,GPIO.OUT)
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG, False)
    GPIO.output(PUMP, False)
    print("Waiting for sensor to settle")
    time.sleep(2)   # wait for sensor to settle


#
# Send trigger to ultrasonic range finder and measure echo return pulse width
#
def sensorRead() :
    distance = 0
    tout = 50                    # timeout in milli-seconds

    # Send trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Measure echo pulse width
    result = GPIO.wait_for_edge(ECHO, GPIO.RISING, timeout=tout)
    if result is not None:
        pulse_start = time.time()

        result = GPIO.wait_for_edge(ECHO, GPIO.FALLING, timeout=tout)
        if result is not None:
            distance = round((time.time() - pulse_start) * 17150.0, 2)    # cm
            if distance < 2.0 or distance > 100.0 :
                distance = 0

    return distance    # inches


#
# Used for ABP pressure sensor to control air pump on-off
#
def pump(state) :
    GPIO.output(PUMP, state)


#
# Close RPi GPIO
#
def sensorClose() :
    GPIO.cleanup()



#
# Test / debug
#
if __name__ == '__main__':

    sensorInit()

    pump(True)
    print("Pump on...")
    time.sleep(5)
    pump(False)
    print("Pump off.")
    time.sleep(5)

    try :
        while (True) :
            depth = sensorRead()
            print("Range= " + str(round(depth,2)) + " inches")
            time.sleep(1)

    except KeyboardInterrupt :
       sensorClose()
       sys.exit(" Exit")
