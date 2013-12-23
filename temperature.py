#!/usr/bin/env python

#
# lala-pi - temperature-test.py
# TEMPer USB Thermometer
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import sys
import time

import zmq

### PyTEMPer Installation:
# cd /opt/
# sudo git clone https://github.com/kiloforce/PyTEMPer
# cd PyTEMPer
### Get PyUSB (if you do not already have installed)
# sudo git clone https://github.com/walac/pyusb
# sudo ln -s pyusb/usb usb

sys.path.append('/opt/PyTEMPer')
import temper
temp = temper.Temper()

import common
log = common.log

# make pychecker safe
if __name__ == "__main__":

    if not temp.devices:
        print "Error: not TEMPer devices found!"
        sys.exit(1)
    device = temp.devices[0]

    common.setup_log('ZMQ_TEMPER')

    common.deamonize()

    context = zmq.Context()

    z_send = context.socket(zmq.PUB)
    z_send.connect("tcp://localhost:5556")

    z_recv = context.socket(zmq.SUB)
    z_recv.connect("tcp://localhost:5555")
    z_recv.setsockopt(zmq.SUBSCRIBE, 'TEMPSERVER:')

    log("ZMQ TEMPER Started!")

    last_temp = 0
    force_send = False
    while True:

        # get temperature
        tempc = temp.getTemperature(device)
        # too noisy... # log("TEMP: " + str(tempc))

        # check for inbound commands
        try:
            command = z_recv.recv(zmq.DONTWAIT)
            log(command)
            if command == "TEMPSERVER: STOP":
                log("Kill command received, shutting down..")
                break
            else:
                log("Forcing temp send")
                force_send = True
        except zmq.ZMQError as err:
            #log("recv err: " + str(err))
            pass

        # only broadcast if your temperature changes
        if tempc != last_temp or force_send:
            last_temp = tempc
            force_send = False
            # send temperature to server
            try:
                log("TEMP SEND: " + str(tempc))
                z_send.send('TEMP: ' + str(tempc))
            except zmq.ZMQError as err:
                log('Send error: ' + str(err))

        # only check temperatures every 10 seconds
        time.sleep(10)

    log("Shutting down...")
    z_recv.close()
    z_send.close()
    context.term()
    log("Goodbye.")
