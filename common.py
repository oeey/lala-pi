#!/usr/bin/env python

#
# lala-pi - common.py
# Common project functions
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import os
import sys
import syslog
import signal

SYSLOG_SETUP = False

def common_noop():
    log("NO OP Shutdown")
    pass
SHUTDOWN_CALLBACK = common_noop

def setup_log(label):
    global SYSLOG_SETUP
    syslog.openlog('[{label}]'.format(label=label))
    SYSLOG_SETUP=True

def setup_syslog(label):
    setup_log(label)

def log(msg):
    global SYSLOG_SETUP
    if not SYSLOG_SETUP:
        setup_syslog('UNKNOWN')
    syslog.syslog(str(msg))

def kill_signal_handler(signal, frame):
    log("Being killed off by signal: {signal}".format(signal=signal))
    log("Calling shutdown callback...")
    SHUTDOWN_CALLBACK()
    log("Goodbye!")
    sys.exit(0)

def deamonize():
    log("Starting Daemon...")
    child_id = os.fork()
    if child_id:
        log("Daemonized!")
        sys.exit(0)
    os.setsid()
    # redirect stdin, stdout, stderr
    os.open('/dev/null', os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)
    signal.signal(signal.SIGTERM, kill_signal_handler)
    signal.signal(signal.SIGALRM, kill_signal_handler)

