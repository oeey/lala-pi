#!/usr/bin/env python

#
# lala-pi - door.py
# Monitor Magnetic Reed Door Switch
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

#import os
import time

import RPi.GPIO as GPIO

# pip install pyzmq
import zmq

import common
log = common.log

DOOR_PIN = 25
DOOR_STATE_FILE = "/tmp/door-state"
# 1 is open
# 0 is closed

# make pychecker safe
if __name__ == "__main__":

    common.setup_log('ZMQ_DOOR')

    common.deamonize()

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DOOR_PIN, GPIO.IN)
        
        GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(DOOR_PIN, GPIO.RISING)
        
        context = zmq.Context()
    
        # send messages to router
        z_send = context.socket(zmq.PUB)
        z_send.connect("tcp://localhost:5556")
    
        # receive messages from router
        z_recv = context.socket(zmq.SUB)
        z_recv.connect("tcp://localhost:5555")
        # listen only for keyboard server messages
        z_recv.setsockopt(zmq.SUBSCRIBE, 'DOORSERVER:')
    
        log("ZMQ Door Monitor Started!")

        state = GPIO.input(DOOR_PIN)
        log("SEND: DOOR: " + str(state))
        with open(DOOR_STATE_FILE, "w") as f:
            f.write(str(state))
        try:
            # send state to MQ router
            z_send.send('DOOR: ' + str(state))
        except zmq.ZMQError as err:
            log('Send error: ' + str(err))
        last_state = state
    
        while True:
    
            # Check for door event
            if GPIO.event_detected(DOOR_PIN):
                state = GPIO.input(DOOR_PIN)
                if state != last_state:
                    last_state = state
                    log("SEND: DOOR: " + str(state))
                    with open(DOOR_STATE_FILE, "w") as f:
                        f.write(str(state))    
                    try:
                        # send state to MQ router
                        z_send.send('DOOR: ' + str(state))
                    except zmq.ZMQError as err:
                        log('Send error: ' + str(err))
                else:
                    log('false alarm')                    

            # see if we receive any command from MQ router
            try:
                command = z_recv.recv(zmq.DONTWAIT)
                log("RECV: " + command)
                if command == "DOORSERVER: QUIT" or command == "DOORSERVER: STOP" or command == "DOORSERVER: DEATH":
                    log("Death received, shutting down...")
                    # terminate server
                    break
                else:
                    # assume very other command is a request for state update
                    try:
                        # send state to MQ router
                        log("SEND: DOOR: " + str(last_state))
                        z_send.send('DOOR: ' + str(last_state))
                    except zmq.ZMQError as err:
                        log('Send error: ' + str(err))
            except zmq.ZMQError as err:
                #log("recv err: " + str(err))
                pass
            
            # sleep a while
            time.sleep(.5)
                
    except Exception as err:
        log("FATAL EXCEPTION: " + err.__class__.__name__ + ": " + str(err))
    finally:
        log("Shutting down...")
        GPIO.cleanup()
        z_recv.close()
        z_send.close()
        context.term()
        log("Goodbye.")
