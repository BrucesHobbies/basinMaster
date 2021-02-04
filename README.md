# basinMaster™
Sump pump basin water depth monitor, logging, and alerts

Copyright(C) 2021, BrucesHobbies,
All Rights Reserved

Sump pump basin/well/pit monitoring is important as one tool for preventing basement flooding in homes and buildings. This is a DIY project for the Raspberry Pi or similar system using an inexpensive sensor with a couple of wires. The software is written in Python and runs under Linux. A number of different sensor types are supported.
# Preface
There are dozens of ultrasonic range finder based sump pump basin/well/pit monitoring programs written and on GitHub for the RPi. One common theme is that Ultrasonic range finders can be difficult to install in the basin due to the confined space since the basin has inside it a primary sump pump, in some cases a secondary pump in case the primary 
pump fails, pipes, and float switches. The ultrasonic signal will echo off the different objects making it difficult for the ultrasonic range finder to distinguish the intended return echo. Second, the programs that I looked at were not very robust since a simple polling loop could loop endlessly if the return signal was missed. This project takes a 
different approach with the use of an ultrasonic range finder using events instead of polling.

In addition this program implements a novel alternative approach to measuring water depth using a low-cost Honeywell pressure sensor. The pressure sensor looks at the water pressure at the bottom of the basin. The pressure sensor involves a little bit more work up front but is significantly easier to install and more reliable.

# basinMaster™ Project Overview
The Raspberry Pi looked like an ideal platform to monitor and log sump basin water depth. This open source project supports two different types of sensors. You may use either or compare both.
- Ultasonic range finder: HC-SR04
- Pressure sensor: Honeywell ABP series

This open source program logs the water depth and will send email alerts if the water depth exceeds an alert level. It can also send status reports on a periodic interval. The alerts and status messages can be an email or SMS message sent via email. Feel free to contribute with custom alert options such as MQTT, IFTT, etc. The program is written in Python and can be ported to additional platforms. The program runs from a terminal window or at boot.

plotBasinMaster.py plots the water depth log. You can view the plots and pan/zoom to specific time periods for the measurements. It uses MatPlotLib and is easy to customize to plot what is of interest to you.

Figure 1 shows the installation of the ultrasonic range finder on the sump basin lid and the pressure sensor tube for the recommended alternative approach.

![Figure 1: Depth Sensor Mounting](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure1.png)

For the two types of sensors, here are the results:

Trial Results|Ultrasonic|Pressure Sensor
-------------------------------------:|--------------:|--------------:|
Standard deviation of readings|0.62"|0.14"|
Minimum reading (delta from average)|-4.28"|-0.29"|
Maximum reading (delta from average)|+2.57|+0.39|

For the ultrasonic sensor, to solve the problems mentioned in the preface with echos from objects inside the basin, I placed the ultrasonic range finder inside an open ended PVC pipe that was put in the the basin. The open source code that I saw used polling which can easily be an endless loop if the echo pulse is not found. Event detection logic 
instead of polling is more robust which was implemented. We then use the average of 11 readings with a threshold of needing 6 good readings that passed a reasonablness distance test. 11% of the attempts failed to have sufficient measurements to average. We can see that the standard deviation is reasonably small but there are large outliers as 
evidenced by the large minimum and maximum reading. More sophisticated algorithms could be developed but the pressure sensor was a better choice to build on.

For the pressure sensor, I used a single reading without additional processing. The standard deviation is reasonably small and there are no large outliers as evidenced by the minimum and maximum readings. For the pressure sensor I used standard air supply tubing that is sold for aquariums. Unfortunately after several days, the pressure from the 
submerged tube leading to the above basin sensor would slowly leak. To solve this, I used an inexpensive aquarium pump to pressurize the system with a relay to turn it on and off. 

# Required Hardware 
As an Amazon Associate I earn a small commission from qualifying purchases. I appreciate your support, if you purchase using the links below.
## Ultrasonic Range Sensor Option
- HC-SR04  [Amazon: HC-SR04](https://amzn.to/2O45koR)
- 1k ohm and 2K ohm resistors to divide 5 volt signal down to 3.3 volts input for RPi
- Wire, heat shrink tubing, soldering iron, and solder

## Pressure Sensor Option - SPI or I2C
- Honeywell ABPMAND001PG2A3, ABPDRRV001PDSA3 or ABPMRRV060MG2A3 pressure sensor available from Digikey, Mouser, Arrow, Newark, etc. for around $13 USD
  - [Digikey: ABPMAND001PG2A3](https://www.digikey.com/en/products/detail/honeywell-sensing-and-productivity-solutions/ABPMAND001PG2A3/5322843?s=N4IgTCBcDaICwA4AMBaAbGArKgdgExAF0BfIA)
  - [Mouser: ABPDRRV001PDSA3](https://www.mouser.com/ProductDetail/Honeywell/ABPDRRV001PDSA3?qs=%2Fha2pyFadui6v3NmLJXcNaJhDLtsWyFpilGTkFr3RAit4EGjj7MIDQ%3D%3D)
- [Amazon: Plastic tube 1.6mm ID]( https://amzn.to/3myZdVW)
- [Amazon: Standard Airline Tubing](https://amzn.to/2O6fUf1)
- Optional [Amazon: Air-pump with check valve](https://amzn.to/3towGGn)
- Optional [Amazon: Air line adapters including tee](https://amzn.to/36GaaPp)
- Optional [Amazon: 5Vdc Relay](https://amzn.to/3cQQJaP)
- Wire, heat shrink tubing, soldering iron, and solder

The ABPMRR060MG2A3 which is a 2-wire I2C bus interface but in a surface mount package which requires soldering.  The I2C pull up resistors are not required when used with the RPI. The ABPDRRV001PDSA3 which is a 3-wire SPI bus interface in a DIP package (Dual-Inline Package used with prototype/breadboards).  Both are 3.3 Vdc supply voltage.

## Raspberry Pi system (if you don’t already own one)
- Raspberry Pi (any of the following)
  - [RPI-Zero]( https://amzn.to/3ly0mM0)
  - [RPI 3B+]( https://amzn.to/3lyPBJe)
  - [RPI 4B]( https://amzn.to/2Vwulto)
- Power adapter for your Raspberry Pi
- Heatsinks (optional)
- SD-Card

For installing the Raspberry Pi operating system, you may want a USB keyboard and USB mouse along with an HDMI cable and monitor. If using the RPI4, a Micro-HDMI to HDMI adapter may be needed. It is possible to install the operating system without a keyboard, mouse, and monitor, but simpler is sometimes better. Once installed and configured you may 
want to switch to SSH or remote desktop so that you can remove the monitor, mouse, and keyboard.

# Sensor wiring and installation
## Ultrasonic Range Sensor Wiring

RPI|HC-SR04
----------------:|-------|
Pin  2 (5Vdc)|Vcc|
Pin  6 (GND)|GND|
Pin 16 (GPIO23)|TRIG|

RPi inputs cannot be exposed to voltages less than 0 or greater than 3.3 volts.For ECHO out of the sensor the voltage is 5 volts. One approach of converting it to 3.3 volts is to feed the ECHO out to a voltage divider. This can be made from 1K ohm and 2K ohm resistors in series with the 1K ohm to the ECHO and the 2K ohm to ground. The RPi pin 18 
(GPIO24) goes to the 1K and 2K ohm center tap as shown below.

    ECHO >--+
            |
           1K ohm
            |
            +---> RPi p18
            |
           2K ohm
            |
    GND ----+---- RPi GND

![Figure 2: Ultrasonic Range Sensor Wiring](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure2.png)

Figure 2: Ulrasonic Range Sensor Wiring

## Pressure Sensor Wiring
Each Honeywell pressure sensor is either i2c or SPI, but not both. The ABPDRRV001PDSA3 which is a 3-wire SPI bus interface is recommended as it is a DIP package.

**RASPBERRY PI SPI PINS to ABP PRESSURE SENSOR (5-wires total):**
RPI 40-pin|SPI ABP (From Table 8 in Honeywell Data Sheet)|
-------------:|------------------------------------------|
Pin 17 (+3.3 VDC) =|Pin 2 (+3.3 Vsupply)|
Pin 21 (SPI_MISO) =|Pin 5 (MISO)|
Pin 23 (SPI_CLK) =|Pin 6 (SCLK)|
Pin 24 (SPI_CE0_N) =|Pin 3 (SS)|
Pin 25 (GND) =|Pin 1 (GND)|
  
**RASPBERRY PI PINS to ABP I2C PRESSURE SENSOR (4-wires total):**
RPI 40-pin|I2C ABP (From Table 8 in Honeywell Data Sheet)|
-------------:|------------------------------------------|
Pin  1 (+3.3 VDC) =| Pin 2 (Vsupply)|
Pin  3 (SDA1) =| Pin 5 (SDA)|
Pin  5 (SCL1) =| Pin 6 (SCL)|
Pin  6 (GND) =| Pin 1 (GND)|

The 3.3 VDC pressure sensors are recommended but, if you purchased a 5.0 VDC pressure sensor then the 5 VDC supply on the pressure sensor pin 2 would go to the RPI Pin 2 (+5.0 VDC). You will need to convert the ABP’s 5 volt bus signals to the RPI bus 3.3 volt levels so this is not as straight forward as using the 3.3 VDC pressure sensor.

RPI|Pump relay driver
----------------:|----------|
Pin 12 (GPIO18)|Trigger|
Pin 14 (GND)|Driver- / Gnd|
Pin  4 (5Vdc)|Driver+ / Power|

## Wiring photo at pressure sensor and RPI
You will purchase either an SPI or I2C pressure sensor, not both. The SPI version is recommended but both sets of 

photos are included to provide choices.

![Figure 3: SPI Pressure Sensor Wiring](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure3.png)

Figure 3: SPI Pressure Sensor


![Figure 4: SPI Wiring on RPI – Note white wire looks gray in this photo.](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure4.png)

Figure 4: SPI Wiring on RPI


![Figure 5: I2C power pins](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure5.png)

Figure 5: Alternative I2C Pressure Sensor Power Pins


![Figure 6: I2C bus pins](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure6.png)

Figure 6: Alternative Pressure Sensor I2C Bus


![Figure 7: I2C Wiring on RPI](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure7.png)

Figure 7: Alternative I2C Wiring on RPI

### Pressure Sensor Plumbing
If your standard airline tubing has a slow leak like mine, consider buying an aquarium bubbler. Connect the air supply hose to an aquarium bubbler pump, then the one-way check valve that is included with the bubbler, then a "tee" with one side going to the ABP pressure sensor and the other side into the sump basin. The relay can be used to turn the 
pump on and off, but the pump draws only 2 watts (less than half the power of a nightlite).

![Figure 8: Pressure sensor installation](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure8.png)

Figure 8: Pressure Sensor Installation

# Software Installation
## Step 1: Setup the Raspberry Pi Operating System.
Here are the instructions to install the Raspberry Pi Operating System.
[Raspberry Software Install Procedure](https://www.raspberrypi.org/software/operating-systems/)

Before continuing make sure your operating system has been updated with the latest updates.

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot now

## Step 2: Install the I2C bus library
If using a Honeywell I2C pressure sensor you will need this library. I would recommend installing it as you may want to use I2C in this project or others. If you don’t install python3-smbus, you will need to comment out the appropriate lines in the program code.

    sudo apt-get install python3-smbus

## Step 3: Enable SPI and/or I2C buses on RPI 
    sudo raspi-config
    
Under interface options, enable either or both the SPI and I2C interfaces depending on the Honeywell ABP pressure sensor that you purchased. In general it is better to enable both so that the interfaces are available for use with projects.

To verify i2c operation, if you have an i2c Honeywell pressure sensor type the following command which should result in the i2c device address 0x28 being displayed:

    sudo i2cdetect –y 1
    
To verify SPI operation, type the following command which should result in the SPI bus being listed:

    ls /dev/*spi*

## Step 4: Download basinMaster software
There are several python source files: basinMaster, sensorHnyAbp, hc_sr04_range, sendEmail, and cfgData. To get a copy of the source files type in the following git command assuming you have already installed git:

    git clone https://github.com/BrucesHobbies/basinMaster

## Step 5: Software Configuration
If you desire, you may edit basinMaster.py and change the user configuration section at the beginning of the file.

### Pressure Sensor Configuration
Edit the basinMaster.py program file if you used a different sensor than the ABPDRRV001PDSA3. Then change the statement to match the variable range, units, and output type of the sensor you purchased. For example if you purchased the ABPMRRV060MG2A3 change from “001PDS” to “060MG2”. Again, this statement is in the basinMaster.py file. More complete details are found in  “sensorHnyAbp.py”.

    sensor = sensorHnyAbp.SensorHnyAbp("001PDS")
    
### Alert Options Configuration
If alerts are enabled (statusMsgEnabled=1) and you have entered valid email information you can choose to have a status message sent for a RPI well-being check. To change the time of day for the status message from noon local time, edit the hour and minute. Entering values outside the expected values will allow you to disable status messages. Range 
for HH is 0 -23 and for MM is 0 – 59.

If using the ultrasonic sensor, set the basin/well/pit depth.

Set the WATER_DEPTH_ALERT level to the water depth at which to send alert messages. If alerts are enabled, you can choose to throttle the alerts. The interval can be as short or long as you like. Default is 24*3600 seconds which is one day.

    #
    # --- User Email Alerts Configuration ---
    #
    # First time program starts, it will ask you for the sender's email
    # this should be an email that you have established for sending alerts from this program
    # gmail is suggested with "Less Secure App Access" turned on. This is required for Python on the RPI.
    # If you change passwords, you will need to delete cfgData.json so that this program will again ask for the password.
    #
    statusMsgEnabled = 1                        # non zero enables sending of email / SMS text messages
    statusMsgHHMM    = [12, 10]                 # Status message time to send [hh, mm]
    alertMsgEnabled  = 0                        # non zero enables sending of email / SMS text messages
    WATER_DEPTH_ALERT         = 9               # Send alert when water depth greater than this many inches
    WATER_DEPTH_ALERT_ENABLE  = 1               # Enable sending alerts
    minIntervalBtwWaterEmails = 24*3600         # seconds

## Step 6: Gmail Configuration
You can use Google Gmail to send status and alert emails. Others have also used Microsoft Live/Outlook/Hotmail, Yahoo, Comcast, ATT, Verizon, and other email servers. Currently, status and alert messages are sent by email which can also be sent as an SMS text to your cell phone. Gmail works with Python on the Raspberry Pi if you set the Gmail security 
settings to low. As such, you can create a separate Gmail account to send messages from. Under your Gmail account settings you will need to make the following change to allow “Less secure app access”.

![Figure 9: Gmail Less Secure App Access](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure9.png)

Then click on “Turn on access (not recommended)” by moving the slider to ON. Then click the back arrow.

![Figure 10: Enable Less Secure App Access](https://github.com/BrucesHobbies/basinMaster/blob/main/figures/figure10.png)

# Running The Program From A Terminal Window 
When your first email is sent at program startup, Google will ask you to confirm that it is you. You will need to sign into the device email account that you created and go to the critical security email that Google sent you and confirm you originated the email before Google will allow emails to be sent from your Python program.

Once you have created an account, start the basinMaster™ program. Type:

    python3 basinMaster.py

The first time the program starts up it will ask you for your gmail user id and password for the account that you just created to work with this program. The password will be saved to a file called cfgData.json.  Please be careful to not send that file to others. If you ever change your password you will need to delete cfgData.json so that the program will ask you for your password again. 

    Enter sender’s device email userid (sending_userid@gmail.com):
    sending_userid@gmail.com

    Enter password:
    password

Next the program will ask you for the recipient email address.  This can either be the same email address, your primary email address or your SMS cell number carrier’s gateway.  To email an SMS to your cell phone construct the recipient email depending on your cell phone carrier:

Carrier|Format
-------|-------|
AT&T|number@txt.att.net|
Verizon|number@vtext.com|
Sprint PCS|number@messaging.sprintpcs.com|
T-Mobile|number@tmomail.net|
VirginMobile|number@vmobl.com|

    Enter recipient’s device email userid (receiving_userid@something.com):
    Receiving_userid@something.com
 
# Future Alert and Status Options
Please feel free to fork and contribute or provide feedback on priorities and features

- Relay / buzzer
- MQTT
  - OpenHab
  - Home Assistant
  - Domoticz
- IFTT
- PubNub
- Twilio
- Cellular
- APRS

# Test Your Configuration and Email Setup
On the first time basinMaster™ program starts, it will ask you for your email userid and password for the email account that you created to use for the alerts and status messages. Once you have entered a password the program will send an email message indicating the program has started up. basinMaster™ will then display the first readings according to the type of sensor you selected. To test the status feature, wait for the status time and verify that you received a status message.

# Plotting Log Files
Simply open a new terminal window. Switch to the directory. 

    python3 plotBasinMaster.py

Use the buttons on the bottom of the plot windows to zoom and pan to the specific months, weeks, days, or hours of interest.

# Auto Start at Boot
Type the following command:

    sudo crontab –e
    
Select the type of editor you are familiar with. I used nano. Add the following line at the end of the file and then press ctrl+O to write the file and ctrl+X to exit the nano editor.

    @reboot sleep 60 && cd basinMaster && python3 basinMaster.py

# Feedback
Let us know what you think of this project and any suggestions for improvements. Feel free to contribute to this open source project.
