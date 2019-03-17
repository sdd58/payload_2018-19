from imu_reg import *
from imu_types import *
from smbus import SMBus
from enum import Enum 


SENSITIVITY_ACCELEROMETER_2  = 0.000061
SENSITIVITY_ACCELEROMETER_4  = 0.000122
SENSITIVITY_ACCELEROMETER_8  = 0.000244
SENSITIVITY_ACCELEROMETER_16 = 0.000732
SENSITIVITY_GYROSCOPE_245    = 0.00875
SENSITIVITY_GYROSCOPE_500    = 0.0175
SENSITIVITY_GYROSCOPE_2000   = 0.07
SENSITIVITY_MAGNETOMETER_4   = 0.00014
SENSITIVITY_MAGNETOMETER_8   = 0.00029
SENSITIVITY_MAGNETOMETER_12  = 0.00043
SENSITIVITY_MAGNETOMETER_16  = 0.00058

class LSM9DS1:
	def __init__(self, interface, xgAddr, mAddr):

		I2Cbus = SMBus(1)
		settings = IMUSettings

		settings.device.commInterface = interface
		settings.device.agAddress = xgAddr
		settings.device.mAddress = mAddr
		
		settings.gyro.enabled = True
		settings.gyro.enableX = True
		settings.gyro.enableY = True
		settings.gyro.enableZ = True
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
		settings.gyro.lowPowerEnable = False
		settings.gyro.HPFEnable = False
		# Gyro HPF cutoff frequency: value between 0-9
		# Actual value depends on sample rate. Only applies
		# if gyroHPFEnable is true.
		settings.gyro.HPFCutoff = 0
		settings.gyro.flipX = False
		settings.gyro.flipY = False
		settings.gyro.flipZ = False
		settings.gyro.orientation = 0
		settings.gyro.latchInterrupt = True

		settings.accel.enabled = True
		settings.accel.enableX = True
		settings.accel.enableY = True
		settings.accel.enableZ = True
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
		settings.accel.highResEnable = False
		# accelHighResBandwidth can be any value between 0-3
		# LP cutoff is set to a factor of sample rate
		# 0 = ODR/50    2 = ODR/9
		# 1 = ODR/100   3 = ODR/400
		settings.accel.highResBandwidth = 0

		settings.mag.enabled = True
		# mag scale can be 4, 8, 12, or 16
		settings.mag.scale = 4
		# mag data rate can be 0-7
		# 0 = 0.625 Hz  4 = 10 Hz
		# 1 = 1.25 Hz   5 = 20 Hz
		# 2 = 2.5 Hz    6 = 40 Hz
		# 3 = 5 Hz      7 = 80 Hz
		settings.mag.sampleRate = 7
		settings.mag.tempCompensationEnable = False
		# magPerformance can be any value between 0-3
		# 0 = Low power mode      2 = high performance
		# 1 = medium performance  3 = ultra-high performance
		settings.mag.XYPerformance = 3
		settings.mag.ZPerformance = 3
		settings.mag.lowPowerEnable = False
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

		gRes = None
		aRes = None
		mRes = None

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
		#calcgRes() # Calculate DPS / ADC tick, stored in gRes variable
		#calcmRes() # Calculate Gs / ADC tick, stored in mRes variable
		calcaRes() # Calculate g / ADC tick, stored in aRes variable

		who_am_i_XG = I2Cbus.read_byte_data(xgAddr,reg.WHO_AM_I_XG)
		who_am_i_M  = I2Cbus.read_byte_data(mAddr, reg.WHO_AM_I_M)

		if ( who_am_i_XG != WHO_AM_I_AG_RSP | who_am_i_M != WHO_AM_I_M_RSP):
			return False

		#initGyro()
		initAccel()
		#initMag()

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

	def initGyro(self):
		tempRegValue = 0

		# CTRL_REG1_G (Default value: 0x00)
		# [ODR_G2][ODR_G1][ODR_G0][FS_G1][FS_G0][0][BW_G1][BW_G0]
		# ODR_G[2:0] - Output data rate selection
		# FS_G[1:0] - Gyroscope full-scale selection
		# BW_G[1:0] - Gyroscope bandwidth selection
		
		# To disable gyro, set sample rate bits to 0. We'll only set sample
		# rate if the gyro is enabled.
		if settings.gyro.enabled:
			tempRegValue = (settings.gyro.sampleRate & 0x07) << 5

		if settings.gyro.scale == 500:
			tempRegValue |= (0x1 << 3)
		elif settings.gyro.scale == 2000:
			tempRegValue |= (0x3 << 3)
		# Otherwise we'll set it to 245 dps (0x0 << 4)

		tempRegValue |= (settings.gyro.bandwidth & 0x3)
		I2Cbus.write_byte_data(xgAddr, CTRL_REG1_G, tempRegValue)

		# CTRL_REG2_G (Default value: 0x00)
		# [0][0][0][0][INT_SEL1][INT_SEL0][OUT_SEL1][OUT_SEL0]
		# INT_SEL[1:0] - INT selection configuration
		# OUT_SEL[1:0] - Out selection configuration
		I2Cbus.write_byte_data(xgAddr, CTRL_REG2_G, 0x00)

		# CTRL_REG3_G (Default value: 0x00)
		# [LP_mode][HP_EN][0][0][HPCF3_G][HPCF2_G][HPCF1_G][HPCF0_G]
		# LP_mode - Low-power mode enable (0: disabled, 1: enabled)
		# HP_EN - HPF enable (0:disabled, 1: enabled)
		# HPCF_G[3:0] - HPF cutoff frequency
		tempRegValue = (1<<7) if settings.gyro.lowPowerEnable else 0
		if settings.gyro.HPFEnable:
			tempRegValue |= (1<<6) | (settings.gyro.HPFCutoff & 0x0F)
		I2Cbus.write_byte_data(xgAddr, CTRL_REG3_G, tempRegValue)

		# CTRL_REG4 (Default value: 0x38)
		# [0][0][Zen_G][Yen_G][Xen_G][0][LIR_XL1][4D_XL1]
		# Zen_G - Z-axis output enable (0:disable, 1:enable)
		# Yen_G - Y-axis output enable (0:disable, 1:enable)
		# Xen_G - X-axis output enable (0:disable, 1:enable)
		# LIR_XL1 - Latched interrupt (0:not latched, 1:latched)
		# 4D_XL1 - 4D option on interrupt (0:6D used, 1:4D used)
		tempRegValue = 0
		if settings.gyro.enableZ:
			tempRegValue |= (1<<5)
		if settings.gyro.enableY:
			tempRegValue |= (1<<4)
		if settings.gyro.enableX:
			tempRegValue |= 1<<3
		if settings.gyro.latchInterrupt:
			tempRegValue |= (1<<1)
		I2Cbus.write_byte_data(xgAddr, CTRL_REG4, tempRegValue)

		# ORIENT_CFG_G (Default value: 0x00)
		# [0][0][SignX_G][SignY_G][SignZ_G][Orient_2][Orient_1][Orient_0]
		# SignX_G - Pitch axis (X) angular rate sign (0: positive, 1: negative)
		# Orient [2:0] - Directional user orientation selection
		tempRegValue = 0
		if settings.gyro.flipX:
			tempRegValue |= (1<<5)
		if settings.gyro.flipY:
			tempRegValue |= (1<<4)
		if settings.gyro.flipZ:
			tempRegValue |= (1<<3)
		I2Cbus.write_byte_data(xgAddr, ORIENT_CFG_G, tempRegValue)
		
	def accelAvailable(self):
		status = I2Cbus.read_byte_data(xgAddr, STATUS_REG_1)

		return (status & (1<<0))

	def gyroAvailable(self):
                status = I2Cbus.read_byte_data(xgAddr, STATUS_REG_1)
                return (status & (1<<0))

	def tempAvailable(self):
                status = I2Cbus.read_byte_data(xgAddr, STATUS_REG_1)
                return ((status & (1<<2)) >> 2)

	def calibrate(self, autoCalc):
	 	data = [0, 0, 0, 0, 0, 0]
	 	samples = 0

	 	aBiasRawTemp = [0, 0, 0]
	 	gBiasRawTemp = [0, 0, 0]

	 	enableFIFO(True)
	 	setFIFO(FIFO_THS, 0x1F)
	 	while (samples < 0x1F):
	 		samples = I2Cbus.read_byte_data(xgAddr, FIFO_SRC) & 0x3F
		
	 	for ii in samples:
	 		#readGyro()
	 		#gBiasRawTemp[0] += gx
	 		#gBiasRawTemp[1] += gy
	 		#gBiasRawTemp[2] += gz
	 		readAccel()
	 		aBiasRawTemp[0] += ax
	 		aBiasRawTemp[1] += ay
	 		aBiasRawTemp[2] += az - (1/aRes) #Assumes sensor facing up!

	 	for ii in range(3):
	 		#gBiasRaw[ii] = gBiasRawTemp[ii] / samples
	 		#gBias[ii] = calcGyro(gBiasRaw[ii])
	 		aBiasRaw[ii] = aBiasRawTemp[ii] / samples
	 		aBias[ii] = calcAccel(aBiasRaw[ii])

	 	enableFIFO(False)
	 	setFIFO(FIFO_OFF,0x00)

	 	if (autoCalc):
	 		_autoCalc = True

	def readAccel(self):
		temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_X_L_XL, 6)

		ax = (temp[1] << 8 | temp[0])
		ay = (temp[3] << 8 | temp[2])
		az = (temp[5] << 8 | temp[4])
	 	if (_autoCalc):
	 		ax -= aBiasRaw[0]
	 		ay -= aBiasRaw[1]
	 		az -= aBiasRaw[2]

	def readGyro(self):
		temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_X_L_G, 6) # We'll read six bytes from the gyro into temp

		gx = (temp[1] << 8) | temp[0] # Store x-axis values into gx
		gy = (temp[3] << 8) | temp[2] # Store y-axis values into gy
		gz = (temp[5] << 8) | temp[4] # Store z-axis values into gz
		if(_autoCalc):
			gx -= gBiasRaw[0]
			gy -= gBiasRaw[1]
			gz -= gBiasRaw[2]

	def readTemp(self):
		temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_TEMP_L, 2) # We'll read two bytes from the temperature sensor into temp	

		offset = 25 # Per datasheet sensor outputs 0 typically @ 25 degrees centigrade
		temperature = offset + ((((int)temp[1] << 8) | temp[0]) >> 8)

	def setGyroScale(self, gScl) :
	 	ctrl1RegValue = I2Cbus.read_byte_data(xgAddr, CTRL_REG1_G) & 0xE7

	 	if (gScl == 500):
	 		ctrl1RegValue |= (0x1 << 3)
	 		settings.gyro.scale = 500
	 	elif(gScl = 2000):
	 		ctrl1RegValue |= (0x3 << 3)
	 		settings.gyro.scale = 2000
	 	else:
	 		settings.gyro.scale = 245
	
	 	I2Cbus.write_byte_data(xgAddr, CTRL_REG1_G, ctrl1RegValue)

	 	calcgRes()

	def setGyroODR(self, gRate):
	 	if (gRate & 0x07 != 0):
	 		temp = I2Cbus.read_byte_data(xgAddr, CTRL_REG1_G)

	 		temp &= 0xFF^(0x7 << 5)
	 		temp |= (gRate & 0x07) << 5

	 		settings.gyro.sampleRate = gRate & 0x07

	 		I2Cbus.write_byte_data(xgAddr, CTRL_REG1_G, temp)

	def setAccelODR(self, aRate):
	 	if (aRate & 0x07 != 0):
	 		temp = I2Cbus.read_byte_data(xgAddr, CTRL_REG6_XL)

	 		temp &= 0x1F
	 		temp |= (aRate & 0x07) << 5

	 		settings.accel.sampleRate = aRate & 0x07

	 		I2Cbus.write_byte_data(xgAddr, CTRL_REG6_XL, temp)

	def setAccelScale(self, aScl):
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

	def calcAccel(self, accel):
		return aRes * accel

	def calcGyro(self, gyro):
                return gRes * gyro
	
	def calcaRes(self):
		if (settings.accel.scale == 2):
			aRes = SENSITIVITY_ACCELEROMETER_2
		elif (settings.accel.scale == 4):
			aRes = SENSITIVITY_ACCELEROMETER_4
		elif (settings.accel.scale == 8):
			aRes = SENSITIVITY_ACCELEROMETER_8
		elif (settings.accel.scale == 16):
			aRes = SENSITIVITY_ACCELEROMETER_16
		else:
			break
	
	def calcgRes(self):
                if settings.gyro.scale == 245:
                        gRes = SENSITIVITY_GYROSCOPE_245
                elif settings.gyro.scale == 500:
                        gRes = SENSITIVITY_GYROSCOPE_500
                elif settings.gyro.scale == 2000:
                        gRes = SENSITIVITY_GYROSCOPE_2000
                else:
                        return
	
	def calcmRes(self):
                if settings.mag.scale == 4:
                        mRes = SENSITIVTY_MAGNETOMETER_4
                elif settings.mag.scale == 8:
                        mRes = SENSITIVITY_MAGNETOMETER_8
                elif settings.mag.scale == 12:
                        mRes = SENSITIVITY_MAGNETOMETER_12
                elif settings.mag.scale == 16:
                        mRes = SENSITIVITY_MAGNETOMETER_16

	def enableFIFO(self, enable):
		temp = I2Cbus.read_byte_data(xgAddr, CTRL_REG9)
		if (enable):
			temp |= (1<<1)
		else
			temp &= ~(1<<1)
		I2Cbus.write_byte_data(xgAddr, CTRL_REG9, temp)

	def setFIFO(self, fifomode, fifoThs):
		threshold =  fifoThs if (fifoThs <= 0x1F) else 0x1F
		I2Cbus.write_byte_data(FIFO_CTRL, ((fifomode & 0x07) << 5) | (threshold & 0x1F))
	
	def getFIFOSamples(self):
		return I2Cbus.read_byte_data(xgAddr, FIFO_SRC & 0x3F)

	def constrainScales(self):
		if ( (settings.gyro.scale != 245) & (settings.gyro.scale != 500) & (settings.gyro.scale != 2000)):
			settings.gyro.scale = 245
		
		if ( (settings.accel.scale != 2) & (settings.accel.scale != 4) & (settings.accel.scale != 8) & (settings.accel.scale != 16)):
			settings.accel.scale = 2

		settings.mag.scale = 4
	

		
	


