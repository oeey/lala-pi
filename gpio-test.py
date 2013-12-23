#!/usr/bin/env python

import sys
import time

import RPi.GPIO as GPIO

pin = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN)

try:
  while True:
    input_value = GPIO.input(pin)
    if input_value:
      sys.stdout.write('-')
    else:
      sys.stdout.write('.')
    sys.stdout.flush()
    time.sleep(.01)
finally:
  GPIO.cleanup()
