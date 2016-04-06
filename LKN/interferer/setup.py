#!/usr/bin/python

import os
import sys

if len(sys.argv)!=3:
    exit("Usage: %s SSID PSK" % sys.argv[0])

ssid = sys.argv[1]
psk = sys.argv[2]

print("========== Configuring network ... ===========")

f = "/etc/wpa_supplicant/wpa_supplicant.conf"

text = "network={\nssid=\"%s\"\npsk=\"%s\"\n}" % (ssid, psk)

os.system("sudo echo '%s' >> %s" % (text, f))
os.system("sudo ifdown wlan0")
os.system("sudo ifup wlan0")

print("========== Network configured, installing prerequisites... ===========")

os.system("sudo apt-get install iperf")

print("========== Warning: do not use the script twice! ===========")
print("========== Finished ===========")