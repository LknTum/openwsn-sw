#!/usr/bin/python

import os
import time
import sys

if len(sys.argv) != 2:
    exit("Usage: %s SERVER_ADDR" % sys.argv[0])

ip = sys.argv[1]

send_period = 100  # s

silence_period = 100 # s

while True:
    print("Starting download for %d sec..." % send_period)
    os.system('iperf -c %s -u -b 100m -t %d -i 1' % (ip, send_period))
    print("Going to sleep for %d sec..." % silence_period)
    time.sleep(silence_period)





