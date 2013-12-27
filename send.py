#!/usr/bin/env python

#
# lala-pi - send.py
# ZeroMQ Test Client - quick send a single line
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#


import os
import sys
import time

import zmq

import common
from common import log

common.setup_log('ZMQ_TEST')

context = zmq.Context()

z_send = context.socket(zmq.PUB)
z_send.connect("tcp://localhost:5556")

#z_recv = context.socket(zmq.SUB)
#z_recv.connect("tcp://localhost:5555")
#z_recv.setsockopt(zmq.SUBSCRIBE, '')  # subscribe to everything


log("ZMQ Client Started!")

if True:
#while True:
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
    elif not sys.stdin.isatty():
        message = sys.stdin.readline().strip()
    else:
        sys.stdout.write("Message: ")
        message = raw_input().strip()

    if message:
        try:
            print "Send: " + message
            log('SEND:' + message)
            z_send.send(message)
        except zmq.ZMQError as err:
            log('Send error: ' + str(err))

    #try:
    #    in_message = z_recv.recv(zmq.DONTWAIT)
    #    log('RECV:' + in_message)
    #except zmq.ZMQError as err:
    #    #pass
    #    log('Receive error: ' + str(err))
