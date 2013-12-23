#!/usr/bin/env python

#
# lala-pi - temperature-test.py
# TEMPer USB Thermometer
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import sys
import time

sys.path.append('/opt/PyTEMPer')
import temper
temp = temper.Temper()

if not temp.devices:
    print "Error: not TEMPer devices found!"
    sys.exit(1)
device = temp.devices[0]

while True:
    # get temperature
    tempc = temp.getTemperature(device)
    print "TEMP: " + str(tempc)

    # only check temperatures every 10 seconds
    time.sleep(10)
