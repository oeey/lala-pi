#!/usr/bin/env python

#
# lala-pi - router.py
# ZeroMQ Message Router
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import time

# apt-get install python-zmq
import zmq

import common
log = common.log

# make Pychecker safe
if __name__ == "__main__":
    common.setup_log('ZMQ_SERVER')

    common.deamonize()

    context = zmq.Context()

    z_send = context.socket(zmq.PUB)
    z_send.bind("tcp://*:5555")

    z_recv = context.socket(zmq.SUB)
    z_recv.bind("tcp://*:5556")
    z_recv.setsockopt(zmq.SUBSCRIBE, '')

    #poller = zmq.Poller()
    #poller.register(s_recv, zmq.POLLIN)

    log("ZMQ Server Started!")

    record = open('router.log', 'w')

    def router_shutdown():
        global record
        global z_send
        global z_recv
        global context
        log("Router shutdown...")
        record.close()
        z_send.close()
        z_recv.close()
        context.term()
        log("Router shutdown complete.")
    common.SHUTDOWN_CALLBACK = router_shutdown

    last_time = time.time()
    count = 0
    while True:
        message = None

        #socks = dict(poller.poll())

        #if s_direct in socks and socks[s_direct] == zmq.POLLIN:
        #    message = s_direct.recv()
        try:
            message = z_recv.recv()
            #log('in: ' + message)
        except zmq.ZMQError as err:
            log('Receive error: ' + str(err))

        #log('out: ' + message)
        if message:

            #log(message)
            count += 1
            record.write(str(count) + ':' + message + '\n')
            #if (count % 10) == 0:
            #    record.flush()
            if time.time() > last_time + 2:
                record.flush()
                last_time = time.time()

            try:
                z_send.send(message)
            except zmq.ZMQError as err:
                log('Send error: ' + str(err))

            if message.strip() == "DEATH":
                log("DEATH RECEIVED!")
                break

    log('Shutting down...')
    router_shutdown()
    log('Goodbye.')
