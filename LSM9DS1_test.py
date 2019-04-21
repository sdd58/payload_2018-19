from LSM9DS1 import *
import time

#Initialize LSM and variables
print("Initializing...\n")
imu = LSM9DS1(IMU_MODE_I2C, 0x6b, 0x1e)
if not imu.begin():
    print("Failed to communicate with LSM9DS1.")
    exit()
    
imu.initAccel()
imu.initGyro()

imu.setAccelScale(2)
imu.setGyroScale(2)

imu.calibrate(True)

a_x = None
a_y = None
a_z = None

g_x = None
g_y = None
g_z = None

delay_time = 0.100

#Read accelerometer values
print("Reading accelerometer (x,y,z)...\n")

for i in range(0,4):
    if(imu.accelAvailable()):
        a_x = imu.calcAccel(imu.ax)
        a_y = imu.calcAccel(imu.ay)
        a_z = imu.calcAccel(imu.az)
        print("Accel(" + str(i) + "): [" + str(a_x) + "," + str(a_y) + "," + str(a_z) + "]")
    else:
        print("Accel(" + str(i) + "): Accelerometer not available.")
    time.sleep(delay_time)

print()

#Read gyroscope values
print("Reading gyroscope (x,y,z)...\n")

for i in range(0,4):
    if(imu.gyroAvailable()):
        g_x = imu.calcGyro(imu.gx)
        g_y = imu.calcGyro(imu.gy)
        g_z = imu.calcGyro(imu.gz)
        print("Gyro(" + str(i) + "): [" + str(g_x) + "," + str(g_y) + "," + str(g_z) + "]")
    else:
        print("Gyro(" + str(i) + "): Gyroscope not available.")
    time.sleep(delay_time)
        
print()
