#!bin/bash

sudo cat /proc/cpuinfo >> ~/startup/logs/start_log.txt
sudo i2cdetect -y 1 >> ~/startup/logs/start_log.txt
sudo python3 /home/pi/startup/startup.py
python3 /home/pi/startup/radio_test.py >> /home/pi/startup/logs/radio_test_results.txt
sudo python3 /home/pi/startup/logs/shutdown.py
