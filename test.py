from LSM9DS1 import *
import time

imu = LSM9DS1(1, 0x6b, 0x1e)
imu.begin()


imu.initAccel()
imu.setAccelScale(2)

while(1):

    if (imu.accelAvailable()):
        imu.readAccel()
    time.sleep(1)
    print("Acceleration: [",imu.calcAccel(imu.ax),",",imu.calcAccel(imu.ay),",",imu.calcAccel(imu.az),"]")
