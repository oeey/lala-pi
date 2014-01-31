#!/usr/bin/env python

#
# lala-pi - test.py
# ZeroMQ Test Client
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#


#import os
import sys
import time
#import signal
import subprocess

import zmq

import common
log = common.log

TIMEOUT = 60 * 60  # 60 minutes

# apt-get install pianobar
# mkdir -p ~/.config/pianobar
# mkfifo ~/.config/pianobar/ctl
# vim ~/.config/pianobar/config
#   user = [USERNAME]
#   password = [PASSWORD]
#   tls_fingerprint = 2D0AFDAFA16F4B5C0A43F3CB1D4752F9535507C0

# make Pychecker safe
if __name__ == "__main__":

    common.setup_log('ZMQ_PANDORA')

    log("Starting ZMQ Pandora...!")

    common.deamonize()

    context = zmq.Context()

    z_recv = context.socket(zmq.SUB)
    z_recv.connect("tcp://localhost:5555")
    z_recv.setsockopt(zmq.SUBSCRIBE, 'KEY:')  # subscribe to everything
    z_recv.setsockopt(zmq.SUBSCRIBE, 'PANDORA:')  # subscribe to everything

    z_send = context.socket(zmq.PUB)
    z_send.connect("tcp://localhost:5556")

    p = subprocess.Popen('/usr/bin/pianobar', shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    def clean_shutdown():
        global z_send
        global z_recv
        global context
        global p
        log('Quitting...')
        log('Closing ZQM...')
        z_send.close()
        z_recv.close()
        context.term()
        log('Closing Pandora...')
        p.kill()
        #p.terminate()
        #os.kill(p.pid, signal.SIGTERM)
        log('Goodbye.')
        sys.exit(0)
    common.SHUTDOWN_CALLBACK = clean_shutdown

    poller = zmq.Poller()
    poller.register(z_recv, zmq.POLLIN)

    start_time = time.time()
    log("ZMQ Pandora Started!")
    while p.poll() is None:

        message = None
        #log('.')

        try:
            #in_message = z_recv.recv(zmq.DONTWAIT)
            # wait 10 seconds for incomming message
            evts = poller.poll(10000)
            if evts:
                message = z_recv.recv()
                log('RECV: ' + message)
        except zmq.ZMQError as err:
            #pass
            log('Receive error: ' + str(err))

        if message:
            # go to next song
            if message == "KEY: 6" or message == "KEY: N6":
                log('Next Song...')
                with open('/root/.config/pianobar/ctl', 'a') as f:
                    f.write('n')
            else:
                # assume we need to quit
                log('Quit message received...')
                with open('/root/.config/pianobar/ctl', 'a') as f:
                    f.write('q')
                time.sleep(1)
                clean_shutdown()

            #try:
            #    log('SEND:' + message)
            #    z_send.send(message)
            #except zmq.ZMQError as err:
            #    log('Send error: ' + str(err))

        if time.time() > start_time + TIMEOUT:
            log('1 hour timeout, quitting...')
            with open('/root/.config/pianobar/ctl', 'a') as f:
                f.write('q')
            time.sleep(1)
            clean_shutdown()

    log("Pandora quit unexpectedly...")
    clean_shutdown()

sys.exit(0)
