#!/usr/bin/python3

import time

f_PATH    = "/home/pi/startup/logs/"
radio_log = "radio_test_results.txt"
start_log = "start_log.txt"

f = open(f_PATH + radio_log,"a+")
f.write("\n")
f.write("------------------------SHUTDOWN-----------------------------------")
f.write("\n")
f.close()

f = open(f_PATH + start_log,"a+")
f.write("\n")
f.write("------------------------SHUTDOWN-----------------------------------")
f.write("\n")
f.close()
