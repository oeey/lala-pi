#!/usr/bin/env python

import os

# pip install pyzmq
import zmq

import common
log = common.log

# pip install evdev
from evdev import InputDevice
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
    14: "BS",
    55: "*",
    98: "/",
    # Numlock keys:
    111: "N.",
    110: "N0",
    107: "N1",
    108: "N2",
    109: "N3",
    105: "N4",
    # notice the missing N5
    106: "N6",
    102: "N7",
    103: "N8",
    104: "N9",
}

# make Pychecker safe
if __name__ == "__main__":

    common.setup_log('ZMQ_KEYBOARD')

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
            if event.type == 1 and event.value == 1 and event.code != 69:
                if event.code in keys:
                    log("KEY: " + keys[event.code])
                    try:
                        # send key press to MQ router
                        z_send.send('KEY: ' + keys[event.code])
                    except zmq.ZMQError as err:
                        log('Send error: ' + str(err))

    log("Shutting down...")
    z_recv.close()
    z_send.close()
    context.term()
    log("Goodbye.")
