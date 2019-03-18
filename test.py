from LSM9DS1 import *
import time




imu = LSM9DS1(1, 0x6b, 0x1e)
imu.begin()

imu.initAccel()
imu.initGyro()

imu.setAccelScale(2)
imu.setGyroScale(2)

a_x = None
a_y = None
a_z = None

g_x = None
g_y = None
g_z = None

while(1):

    if (imu.accelAvailable()):
        	imu.readAccel()

	        #Update the local variables
	        a_x = imu.calcAccel(imu.ax)
	    	a_y = imu.calcAccel(imu.ay)
	    	a_z = imu.calcAccel(imu.az)

    if (imu.gyroAvailable()):

    		imu.readGyro()

	    	#Update the local variables
			g_x = imu.calcGyro(imu.gx)
	    	g_y = imu.calcGyro(imu.gy)
	    	g_z = imu.calcGyro(imu.gz)
    
    print("Acceleration: [",a_x,",",a_y,",",a_z,"]")
    print("Gyroscope: [",g_x,",",g_y,",",g_z,"]")
	time.sleep(1)