#!/usr/bin/env python

#
# lala-pi - keypad.py
# USB Keypad
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import string
import os
import sys
import time

# pip install evdev
from evdev import InputDevice
from select import select

# look for a /dev/input/by-id/usb...kbd or something similar
DEVICE = "/dev/input/by-id/usb-ORTEK_USB_Keyboard_Hub-event-kbd"

dev = InputDevice(DEVICE)

while True:

    # wait for keyboard command
    r, w, x = select([dev], [], [])

    # read keyboard
    for event in dev.read():
        # event.code 69 means return to idle
        if event.type == 1 and event.value == 1:
            if event.code in keys:
                print "KEY CODE: " + event.code
                # do something with this key press
                # ...
