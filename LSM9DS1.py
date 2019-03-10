from imu_reg import *
from imu_types import *
from smbus import SMBus
from enum import Enum 

class LSM9DS1:

	xgAddr = 0x6B
	mAddr  = 0x1E
	interface = interface_mode.IMU_MODE_I2C
	I2Cbus = SMBus(1)
	settings = IMUSettings

	def __init__(self, interface, xgAddr, mAddr):
		
		settings.device.commInterface = interface
		settings.device.agAddress = xgAddr
		settings.device.mAddress = mAddr
		
		settings.gyro.enabled = true
		settings.gyro.enableX = true
		settings.gyro.enableY = true
		settings.gyro.enableZ = true
		# gyro scale can be 245, 500, or 2000
		settings.gyro.scale = 245
		# gyro sample rate: value between 1-6
		# 1 = 14.9    4 = 238
		# 2 = 59.5    5 = 476
		# 3 = 119     6 = 952
		settings.gyro.sampleRate = 6
		# gyro cutoff frequency: value between 0-3
		# Actual value of cutoff frequency depends
		# on sample rate.
		settings.gyro.bandwidth = 0
		settings.gyro.lowPowerEnable = false
		settings.gyro.HPFEnable = false
		# Gyro HPF cutoff frequency: value between 0-9
		# Actual value depends on sample rate. Only applies
		# if gyroHPFEnable is true.
		settings.gyro.HPFCutoff = 0
		settings.gyro.flipX = false
		settings.gyro.flipY = false
		settings.gyro.flipZ = false
		settings.gyro.orientation = 0
		settings.gyro.latchInterrupt = true

		settings.accel.enabled = true
		settings.accel.enableX = true
		settings.accel.enableY = true
		settings.accel.enableZ = true
		# accel scale can be 2, 4, 8, or 16
		settings.accel.scale = 2
		# accel sample rate can be 1-6
		# 1 = 10 Hz    4 = 238 Hz
		# 2 = 50 Hz    5 = 476 Hz
		# 3 = 119 Hz   6 = 952 Hz
		settings.accel.sampleRate = 6
		# Accel cutoff freqeuncy can be any value between -1 - 3. 
		# -1 = bandwidth determined by sample rate
		# 0 = 408 Hz   2 = 105 Hz
		# 1 = 211 Hz   3 = 50 Hz
		settings.accel.bandwidth = -1
		settings.accel.highResEnable = false
		# accelHighResBandwidth can be any value between 0-3
		# LP cutoff is set to a factor of sample rate
		# 0 = ODR/50    2 = ODR/9
		# 1 = ODR/100   3 = ODR/400
		settings.accel.highResBandwidth = 0

		settings.mag.enabled = true
		# mag scale can be 4, 8, 12, or 16
		settings.mag.scale = 4
		# mag data rate can be 0-7
		# 0 = 0.625 Hz  4 = 10 Hz
		# 1 = 1.25 Hz   5 = 20 Hz
		# 2 = 2.5 Hz    6 = 40 Hz
		# 3 = 5 Hz      7 = 80 Hz
		settings.mag.sampleRate = 7
		settings.mag.tempCompensationEnable = false
		# magPerformance can be any value between 0-3
		# 0 = Low power mode      2 = high performance
		# 1 = medium performance  3 = ultra-high performance
		settings.mag.XYPerformance = 3
		settings.mag.ZPerformance = 3
		settings.mag.lowPowerEnable = false
		# magOperatingMode can be 0-2
		# 0 = continuous conversion
		# 1 = single-conversion
		# 2 = power down
		settings.mag.operatingMode = 0

		settings.temp.enabled = False
		
		gBias = [0, 0, 0]
		aBias = [0, 0, 0]
		mBias = [0, 0, 0]

		gBiasRaw = [0, 0, 0]
		aBiasRaw = [0, 0, 0]
		mBiasRaw = [0, 0, 0]

		__gRes = None
		__aRes = None
		__mRes = None

		for i in range(3):
			gBias[i] = 0
			aBias[i] = 0
			mBias[i] = 0
			gBiasRaw[i] = 0
			aBiasRaw[i] = 0
			mBiasRaw[i] = 0

		_autoCalc = False

	def begin(self):
		
		constrainScales()
		# Once we have the scale values, we can calculate the resolution
		# of each sensor. That's what these functions are for. One for each sensor
		calcgRes() # Calculate DPS / ADC tick, stored in gRes variable
		calcmRes() # Calculate Gs / ADC tick, stored in mRes variable
		calcaRes() # Calculate g / ADC tick, stored in aRes variable

		who_am_i_XG = I2Cbus.read_byte_data(xgAddr,reg.WHO_AM_I_XG)
		who_am_i_M  = I2Cbus.read_byte_data(mAddr, reg.WHO_AM_I_M)

		if ( who_am_i_XG != WHO_AM_I_AG_RSP | who_am_i_M != WHO_AM_I_M_RSP):
			return False

		initGyro()
		initAccel()
		initMag()

		return True

	def initAccel(self):

		tempRegValue = 0

		if (settings.accel.enableZ):
			 tempRegValue |= (1<<5)
		if (settings.accel.enableY):
			 tempRegValue |= (1<<4)
		if (settings.accel.enableX):
			 tempRegValue |= (1<<3)

		I2Cbus.write_byte_data(xgAddr, CTRL_REG5_XL, tempRegValue)
		
		tempRegValue = 0

		if (settings.accel.enabled):
			tempRegValue |= (settings.accel.sampleRate & 0x07) << 5

		if (settings.accel.scale == 4):
			tempRegValue |= (0x2 << 3)
		elif(settings.accel.scale == 8):
			tempRegValue |= (0x3 << 3)
		elif(settings.accel.scale == 16):
			tempRegValue |= (0x1 << 3)
		
		if (settings.accel.bandwidth >= 0):
			tempRegValue |= (1<<2)
			tempRegValue |= (settings.accel.bandwidth & 0x03)
		
		I2Cbus.write_byte_data(xgAddr, CTRL_REG6_XL, tempRegValue)

		tempRegValue = 0
		if (settings.accel.highResEnable):
			tempRegValue |= (1<<7)
			tempRegValue |= (settings.accel.highResBandwidth & 0x3) << 5
		
		I2Cbus.write_byte_data(xgAddr, CTRL_REG7_XL, tempRegValue)

	def accelAvailable(self):
		status = I2Cbus.read_byte_data(xgAddr, STATUS_REG_1)

		return (status & (1<<0))

	# def calibrate(self, autoCalc):

	# 	data = [0, 0, 0, 0, 0, 0]
	# 	samples = 0

	# 	aBiasRawTemp = [0, 0, 0]
	# 	gBiasRawTemp = [0, 0, 0]

	# 	enableFIFO(True)
	# 	setFIFO(FIFO_THS, 0x1F)
	# 	while (samples < 0x1F):
	# 		samples = I2Cbus.read_byte_data(xgAddr, FIFO_SRC) & 0x3F
		
	# 	for ii in samples:
	# 		readGyro()
	# 		gBiasRawTemp[0] += gx
	# 		gBiasRawTemp[1] += gy
	# 		gBiasRawTemp[2] += gz
	# 		readAccel()
	# 		aBiasRawTemp[0] += ax
	# 		aBiasRawTemp[1] += ay
	# 		aBiasRawTemp[2] += az - (int16_t)(1./aRes) #Assumes sensor facing up!

	# 	for ii in range(3):
	# 		gBiasRaw[ii] = gBiasRawTemp[ii] / samples
	# 		gBias[ii] = calcGyro(gBiasRaw[ii])
	# 		aBiasRaw[ii] = aBiasRawTemp[ii] / samples
	# 		aBias[ii] = calcAccel(aBiasRaw[ii])

	# 	enableFIFO(False)
	# 	setFIFO(FIFO_OFF,0x00)

	# 	if (autoCalc):
	# 		_autoCalc = True

	def readAccel(self):
		
		temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_X_L_XL, 6)

		ax = (temp[1] << 8 | temp[0])
		ay = (temp[3] << 8 | temp[2])
		az = (temp[5] << 8 | temp[4])

		if (_autoCalc):
			ax -= aBiasRaw[X_AXIS]
			ay -= aBiasRaw[Y_AXIS]
			az -= aBiasRaw[Z_AXIS]

	# def setGyroScale(self, gScl) :

	# 	ctrl1RegValue = I2Cbus.read_byte_data(xgAddr, CTRL_REG1_G) & 0xE7

	# 	if (gScl == 500):
	# 		ctrl1RegValue |= (0x1 << 3)
	# 		settings.gyro.scale = 500
	# 	elif(gScl = 2000):
	# 		ctrl1RegValue |= (0x3 << 3)
	# 		settings.gyro.scale = 2000
	# 	else:
	# 		settings.gyro.scale = 245
	
	# 	I2Cbus.write_byte_data(xgAddr, CTRL_REG1_G, ctrl1RegValue)

	# 	calcgRes()

	# def setGyroODR(self, gRate):
	# 	if (gRate & 0x07 != 0):
	# 		temp = I2Cbus.read_byte_data(xgAddr, CTRL_REG1_G)

	# 		temp &= 0xFF^(0x7 << 5)
	# 		temp |= (gRate & 0x07) << 5

	# 		settings.gyro.sampleRate = gRate & 0x07

	# 		I2Cbus.write_byte_data(xgAddr, CTRL_REG1_G, temp)

	# def setAccelODR(self, aRate):
	# 	if (aRate & 0x07 != 0):
	# 		temp = I2Cbus.read_byte_data(xgAddr, CTRL_REG6_XL)

	# 		temp &= 0x1F
	# 		temp |= (aRate & 0x07) << 5

	# 		settings.accel.sampleRate = aRate & 0x07

	# 		I2Cbus.write_byte_data(xgAddr, CTRL_REG6_XL, temp)

	# def setAccelScale(self, aScl):
		#Input is a byte 

		tempRegValue = I2Cbus.read_byte_data(xgAddr, CTRL_REG6_XL)
		tempRegValue &= 0xE7

		if (aScl == 4):
			tempRegValue |= (0x2 << 3)
			settings.accel.scale = 4
		elif(aScl == 8):
			tempRegValue |= (0x3 << 3)
			settings.accel.scale = 8
		elif(aScl == 16):
			tempRegValue |= (0x1 << 3)
			settings.accel.scale =16
		else:
			settings.accel.scale = 2
		
		I2Cbus.write_byte_data(xgAddr, CTRL_REG6_XL, tempRegValue)

		calcaRes()
	


