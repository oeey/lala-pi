#!/usr/bin/env python

#
# lala-pi - pianobar_ctl.py
# Control pianobar (Pandora) with wrapper script test
# Author: Kenneth Burgener <kenneth@oeey.com> (c) 2013
#

import sys
import select
import subprocess
import tty

cmd = "/usr/bin/pianobar"

p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# don't line buffer stdin - but it messes with output
old = tty.tcgetattr(sys.stdin.fileno())
tty.setraw(sys.stdin.fileno())

line = ''

# cycle while process continues alive
while p.poll() == None:

    # check if input
    if select.select([p.stdout.fileno()], [], [], 1)[0]:
        while select.select([p.stdout.fileno()], [], [], .1)[0]:
            # readline breaks when playing songs as a newline doesn't
            # occur until the end of the song
            #line = p.stdout.readline()
            ch = p.stdout.read(1)
            if not ch:
                sys.stdout.write("_ _ _")
                break
            i_ch = ord(ch)
            if i_ch == 10 or i_ch == 13:
                if line.startswith('(27)[2K#'):
                    sys.stdout.write('.')
                    sys.stdout.flush()
                else:
                    sys.stdout.write(line)
                    sys.stdout.write('\r\n')
                line = ''
            elif ord(ch) < 32 or ord(ch) > 126:
                line += "(" + str(ord(ch)) + ")"
            else:
                line += ch

    if select.select([sys.stdin.fileno()], [], [], .1)[0]:
        #line = sys.stdin.readline()
        #print ">> CONSOLE: %s" % line.strip()
        ch = sys.stdin.read(1)
        sys.stdout.write("[" + ch + "]")
        if ch == "q":
            p.stdin.write(ch)

    #sys.stdout.write("_")

# Restore stdin
#tty.tcsetattr(sys.stdin.fileno(), tty.TCSAFLUSH, old)
tty.tcsetattr(sys.stdin.fileno(), tty.TCSADRAIN, old)

# tcsetattr(fd, when, attributes) - The when argument determines when the
# attributes are changed:
#   TCSANOW to change immediately,
#   TCSADRAIN to change after transmitting all queued output
#   TCSAFLUSH to change after transmitting all queued output and
#             discarding all queued input.
    
# os.system("stty sane")
