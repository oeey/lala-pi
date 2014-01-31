#!/usr/bin/env python

#
# lala-pi - keypad.py
# USB Keypad
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import os

# pip install pyzmq
import zmq

import common
log = common.log

# apt-get install python-setuptools python-dev
# easy_install pip
# pip install evdev
from evdev import InputDevice
from evdev import ecodes
from select import select

# look for a /dev/input/by-id/usb...kbd or similar
DEVICE = "/dev/input/by-id/usb-ORTEK_USB_Keyboard_Hub-event-kbd"

# keypad layout:
# NL /  *  BS
# 7  8  9  -
# 4  5  6  +
# 1  2  3  EN
# 0  00 .  EN

# keymapping determined by trial and error
keys = {
    69: "NL",  # Num Lock
    79: "1",
    80: "2",
    81: "3",
    75: "4",
    76: "5",
    77: "6",
    71: "7",
    72: "8",
    73: "9",
    82: "0",
    83: ".",
    28: "ENTER",
    78: "+",
    74: "-",
    14: "BS",  # Back Space
    55: "*",
    98: "/",

    # non num lock keys:
    111: "_.",  # Del
    110: "_0",  # Ins
    107: "_1",  # End
    108: "_2",  # Down
    109: "_3",  # PgDn
    105: "_4",  # Left
    # notice the missing N5 - better to use num lock mode
    106: "_6",  # Right
    102: "_7",  # Home
    103: "_8",  # Up
    104: "_9",  # PgUp
}

# make Pychecker safe
if __name__ == "__main__":

    common.setup_log('ZMQ_KEYPAD')

    common.deamonize()

    dev = InputDevice(DEVICE)

    context = zmq.Context()

    # send messages to router
    z_send = context.socket(zmq.PUB)
    z_send.connect("tcp://localhost:5556")

    # receive messages from router
    z_recv = context.socket(zmq.SUB)
    z_recv.connect("tcp://localhost:5555")
    # listen only for keyboard server messages
    z_recv.setsockopt(zmq.SUBSCRIBE, 'KEYSERVER:')

    log("ZMQ Keyboard Started!")

    # is [('LED_NUML', 0)] or []
    log("LED state: " + str(dev.leds(verbose=True)))
    # is [0] or []
    log("LED statea: " + str(dev.leds()))

    #log("Turning on num lock")
    ## turn on num lock
    #dev.set_led(ecodes.LED_NUML, 1)
    #log("LED state: " + str(dev.leds(verbose=True)))
    #log("LED statea: " + str(dev.leds()))
    #
    #dev.set_led(ecodes.LED_NUML, 0)
    #log("LED state: " + str(dev.leds(verbose=True)))
    #log("LED statea: " + str(dev.leds()))
    #
    #dev.set_led(ecodes.LED_NUML, 1)
    #log("LED state: " + str(dev.leds(verbose=True)))
    #log("LED statea: " + str(dev.leds()))

    i = 0
    while True:

        # wait for keyboard command, 5 sec timeout
        r, w, x = select([dev], [], [], 5)

        # see if we receive any command from MQ router
        try:
            command = z_recv.recv(zmq.DONTWAIT)
            log(command)
            # assume any command to server is death
            break
        except zmq.ZMQError as err:
            #log("recv err: " + str(err))
            pass

        # if our keyboard object was not ready for reading, skip read
        if not r:
            continue

        # read keyboard
        for event in dev.read():
            # event.code 69 means return to idle
            #if event.type == 1 and event.value == 1 and event.code != 69:
            if event.type == 1 and event.value == 1:
                log("K" + str(event.code))
                if event.code in keys:
                    log("KEY: " + keys[event.code])
                    try:
                        # send key press to MQ router
                        z_send.send('KEY: ' + keys[event.code])
                    except zmq.ZMQError as err:
                        log('Send error: ' + str(err))

                log("led:" + str(dev.leds()))
                #if i == 1:
                #    log('sed num 0')
                #    dev.set_led(ecodes.LED_NUML, 0)
                #    i = 0
                #else:
                #    log('sed num 1')
                #    dev.set_led(ecodes.LED_NUML, 1)
                #    i = 1

        log(".")

        #led = dev.leds()
        #if len(led) >= 1 and led[0] == 0:
        #    log("re-enabling num lock")
        #    # turn on num lock
        #    dev.set_led(ecodes.LED_NUML, 1)

    log("Shutting down...")
    z_recv.close()
    z_send.close()
    context.term()
    log("Goodbye.")
