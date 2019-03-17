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

	I2Cbus = SMBus(1)
	settings = IMUSettings

	gBias = None
	aBias = None
	mBias = None
	
	gBiasRaw = None
	aBiasRaw = None
	mBiasRaw = None

	gRes = None
	aRes = None
	mRes = None

	_autoCalc = False

	ax = None
	ay = None
	az = None

	gx = None
	gy = None
	gz = None

	mx = None
	my = None
	mz = None


	xgAddr = None
	mAddr = None

	Temperature = None

	def __init__(self, interface, a, b):

		

		self.settings.device.commInterface = interface
		self.settings.device.agAddress = a
		self.settings.device.self.mAddress = b
		
		self.xgAddr = self.settings.device.agAddress
		self.mAddr = self.settings.device.self.mAddress

		self.settings.gyro.enabled = True
		self.settings.gyro.enableX = True
		self.settings.gyro.enableY = True
		self.settings.gyro.enableZ = True
		# gyro scale can be 245, 500, or 2000
		self.settings.gyro.scale = 245
		# gyro sample rate: value between 1-6
		# 1 = 14.9    4 = 238
		# 2 = 59.5    5 = 476
		# 3 = 119     6 = 952
		self.settings.gyro.sampleRate = 6
		# gyro cutoff frequency: value between 0-3
		# Actual value of cutoff frequency depends
		# on sample rate.
		self.settings.gyro.bandwidth = 0
		self.settings.gyro.lowPowerEnable = False
		self.settings.gyro.HPFEnable = False
		# Gyro HPF cutoff frequency: value between 0-9
		# Actual value depends on sample rate. Only applies
		# if gyroHPFEnable is true.
		self.settings.gyro.HPFCutoff = 0
		self.settings.gyro.flipX = False
		self.settings.gyro.flipY = False
		self.settings.gyro.flipZ = False
		self.settings.gyro.orientation = 0
		self.settings.gyro.latchInterrupt = True

		self.settings.accel.enabled = True
		self.settings.accel.enableX = True
		self.settings.accel.enableY = True
		self.settings.accel.enableZ = True
		# accel scale can be 2, 4, 8, or 16
		self.settings.accel.scale = 2
		# accel sample rate can be 1-6
		# 1 = 10 Hz    4 = 238 Hz
		# 2 = 50 Hz    5 = 476 Hz
		# 3 = 119 Hz   6 = 952 Hz
		self.settings.accel.sampleRate = 6
		# Accel cutoff freqeuncy can be any value between -1 - 3. 
		# -1 = bandwidth determined by sample rate
		# 0 = 408 Hz   2 = 105 Hz
		# 1 = 211 Hz   3 = 50 Hz
		self.settings.accel.bandwidth = -1
		self.settings.accel.highResEnable = False
		# accelHighResBandwidth can be any value between 0-3
		# LP cutoff is set to a factor of sample rate
		# 0 = ODR/50    2 = ODR/9
		# 1 = ODR/100   3 = ODR/400
		self.settings.accel.highResBandwidth = 0

		self.settings.mag.enabled = True
		# mag scale can be 4, 8, 12, or 16
		self.settings.mag.scale = 4
		# mag data rate can be 0-7
		# 0 = 0.625 Hz  4 = 10 Hz
		# 1 = 1.25 Hz   5 = 20 Hz
		# 2 = 2.5 Hz    6 = 40 Hz
		# 3 = 5 Hz      7 = 80 Hz
		self.settings.mag.sampleRate = 7
		self.settings.mag.tempCompensationEnable = False
		# magPerformance can be any value between 0-3
		# 0 = Low power mode      2 = high performance
		# 1 = medium performance  3 = ultra-high performance
		self.settings.mag.XYPerformance = 3
		self.settings.mag.ZPerformance = 3
		self.settings.mag.lowPowerEnable = False
		# magOperatingMode can be 0-2
		# 0 = continuous conversion
		# 1 = single-conversion
		# 2 = power down
		self.settings.mag.operatingMode = 0

		self.settings.temp.enabled = False
		
		self.gBias = [0, 0, 0]
		self.aBias = [0, 0, 0]
		self.mBias = [0, 0, 0]

		self.gBiasRaw = [0, 0, 0]
		self.aBiasRaw = [0, 0, 0]
		self.mBiasRaw = [0, 0, 0]

		self.gRes = None
		self.aRes = None
		self.mRes = None

		for i in range(3):
			self.gBias[i] = 0
			self.aBias[i] = 0
			self.mBias[i] = 0
			self.gBiasRaw[i] = 0
			self.aBiasRaw[i] = 0
			self.mBiasRaw[i] = 0

		self._autoCalc = False

	def begin(self):
		self.constrainScales()
		# Once we have the scale values, we can calculate the resolution
		# of each sensor. That's what these functions are for. One for each sensor
		#calcgRes() # Calculate DPS / ADC tick, stored in gRes variable
		#calcmRes() # Calculate Gs / ADC tick, stored in mRes variable
		self.calcaRes() # Calculate g / ADC tick, stored in aRes variable

		who_am_i_XG = self.I2Cbus.read_byte_data(self.xgAddr,reg.WHO_AM_I_XG)
		who_am_i_M  = self.I2Cbus.read_byte_data(self.mAddr, reg.WHO_AM_I_M)

		if ( who_am_i_XG != WHO_AM_I_AG_RSP | who_am_i_M != WHO_AM_I_M_RSP):
			return False

		#initGyro()
		self.initAccel()
		#initMag()

		return True

	def initAccel(self):
		tempRegValue = 0

		if (self.settings.accel.enableZ):
			 tempRegValue |= (1<<5)
		if (self.settings.accel.enableY):
			 tempRegValue |= (1<<4)
		if (self.settings.accel.enableX):
			 tempRegValue |= (1<<3)

		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG5_XL, tempRegValue)
		
		tempRegValue = 0

		if (self.settings.accel.enabled):
			tempRegValue |= (self.settings.accel.sampleRate & 0x07) << 5

		if (self.settings.accel.scale == 4):
			tempRegValue |= (0x2 << 3)
		elif(self.settings.accel.scale == 8):
			tempRegValue |= (0x3 << 3)
		elif(self.settings.accel.scale == 16):
			tempRegValue |= (0x1 << 3)
		
		if (self.settings.accel.bandwidth >= 0):
			tempRegValue |= (1<<2)
			tempRegValue |= (self.settings.accel.bandwidth & 0x03)
		
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG6_XL, tempRegValue)

		tempRegValue = 0
		if (self.settings.accel.highResEnable):
			tempRegValue |= (1<<7)
			tempRegValue |= (self.settings.accel.highResBandwidth & 0x3) << 5
		
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG7_XL, tempRegValue)

	def initGyro(self):
		tempRegValue = 0

		# CTRL_REG1_G (Default value: 0x00)
		# [ODR_G2][ODR_G1][ODR_G0][FS_G1][FS_G0][0][BW_G1][BW_G0]
		# ODR_G[2:0] - Output data rate selection
		# FS_G[1:0] - Gyroscope full-scale selection
		# BW_G[1:0] - Gyroscope bandwidth selection
		
		# To disable gyro, set sample rate bits to 0. We'll only set sample
		# rate if the gyro is enabled.
		if self.settings.gyro.enabled:
			tempRegValue = (self.settings.gyro.sampleRate & 0x07) << 5

		if self.settings.gyro.scale == 500:
			tempRegValue |= (0x1 << 3)
		elif self.settings.gyro.scale == 2000:
			tempRegValue |= (0x3 << 3)
		# Otherwise we'll set it to 245 dps (0x0 << 4)

		tempRegValue |= (self.settings.gyro.bandwidth & 0x3)
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG1_G, tempRegValue)

		# CTRL_REG2_G (Default value: 0x00)
		# [0][0][0][0][INT_SEL1][INT_SEL0][OUT_SEL1][OUT_SEL0]
		# INT_SEL[1:0] - INT selection configuration
		# OUT_SEL[1:0] - Out selection configuration
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG2_G, 0x00)

		# CTRL_REG3_G (Default value: 0x00)
		# [LP_mode][HP_EN][0][0][HPCF3_G][HPCF2_G][HPCF1_G][HPCF0_G]
		# LP_mode - Low-power mode enable (0: disabled, 1: enabled)
		# HP_EN - HPF enable (0:disabled, 1: enabled)
		# HPCF_G[3:0] - HPF cutoff frequency
		tempRegValue = (1<<7) if self.settings.gyro.lowPowerEnable else 0
		if self.settings.gyro.HPFEnable:
			tempRegValue |= (1<<6) | (self.settings.gyro.HPFCutoff & 0x0F)
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG3_G, tempRegValue)

		# CTRL_REG4 (Default value: 0x38)
		# [0][0][Zen_G][Yen_G][Xen_G][0][LIR_XL1][4D_XL1]
		# Zen_G - Z-axis output enable (0:disable, 1:enable)
		# Yen_G - Y-axis output enable (0:disable, 1:enable)
		# Xen_G - X-axis output enable (0:disable, 1:enable)
		# LIR_XL1 - Latched interrupt (0:not latched, 1:latched)
		# 4D_XL1 - 4D option on interrupt (0:6D used, 1:4D used)
		tempRegValue = 0
		if self.settings.gyro.enableZ:
			tempRegValue |= (1<<5)
		if self.settings.gyro.enableY:
			tempRegValue |= (1<<4)
		if self.settings.gyro.enableX:
			tempRegValue |= 1<<3
		if self.settings.gyro.latchInterrupt:
			tempRegValue |= (1<<1)
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG4, tempRegValue)

		# ORIENT_CFG_G (Default value: 0x00)
		# [0][0][SignX_G][SignY_G][SignZ_G][Orient_2][Orient_1][Orient_0]
		# SignX_G - Pitch axis (X) angular rate sign (0: positive, 1: negative)
		# Orient [2:0] - Directional user orientation selection
		tempRegValue = 0
		if self.settings.gyro.flipX:
			tempRegValue |= (1<<5)
		if self.settings.gyro.flipY:
			tempRegValue |= (1<<4)
		if self.settings.gyro.flipZ:
			tempRegValue |= (1<<3)
		self.I2Cbus.write_byte_data(self.xgAddr, ORIENT_CFG_G, tempRegValue)
		
	def accelAvailable(self):
		status = self.I2Cbus.read_byte_data(self.xgAddr, STATUS_REG_1)
		return (status & (1<<0))

	def gyroAvailable(self):
        	status = self.I2Cbus.read_byte_data(self.xgAddr, STATUS_REG_1)
        	return (status & (1<<0))

	def tempAvailable(self):
        	status = self.I2Cbus.read_byte_data(self.xgAddr, STATUS_REG_1)
        	return ((status & (1<<2)) >> 2)

	def calibrate(self, autoCalc):
	 	data = [0, 0, 0, 0, 0, 0]
	 	samples = 0

	 	self.aBiasRawTemp = [0, 0, 0]
	 	self.gBiasRawTemp = [0, 0, 0]

	 	self.enableFIFO(True)
	 	self.setFIFO(FIFO_THS, 0x1F)
	 	while (samples < 0x1F):
	 		samples = self.I2Cbus.read_byte_data(self.xgAddr, FIFO_SRC) & 0x3F
		
	 	for ii in samples:
	 		self.readGyro()
	 		self.gBiasRawTemp[0] += self.gx
	 		self.gBiasRawTemp[1] += self.gy
	 		self.gBiasRawTemp[2] += self.gz
	 		self.readAccel()
	 		self.aBiasRawTemp[0] += self.ax
	 		self.aBiasRawTemp[1] += self.ay
	 		self.aBiasRawTemp[2] += self.az - (1/self.aRes) #Assumes sensor facing up!

	 	for ii in range(3):
	 		self.gBiasRaw[ii] = self.gBiasRawTemp[ii] / samples
	 		self.gBias[ii] = self.calcGyro(gBiasRaw[ii])
	 		self.aBiasRaw[ii] = self.aBiasRawTemp[ii] / samples
	 		self.aBias[ii] = self.calcAccel(self.aBiasRaw[ii])

	 	self.enableFIFO(False)
	 	self.setFIFO(FIFO_OFF,0x00)

	 	if (autoCalc):
	 		self._autoCalc = True

	def readAccel(self):
		temp = self.I2Cbus.read_i2c_block_data(self.xgAddr, OUT_X_L_XL, 6)

		self.ax = (temp[1] << 8 | temp[0])
		self.ay = (temp[3] << 8 | temp[2])
		self.az = (temp[5] << 8 | temp[4])
		if (self._autoCalc):
                    self.ax -= self.aBiasRaw[0]
                    self.ay -= self.aBiasRaw[1]
                    self.az -= self.aBiasRaw[2]

	def readGyro(self):
		temp = self.I2Cbus.read_i2c_block_data(self.xgAddr, OUT_X_L_G, 6) # We'll read six bytes from the gyro into temp

		self.gx = (temp[1] << 8) | temp[0] # Store x-axis values into gx
		self.gy = (temp[3] << 8) | temp[2] # Store y-axis values into gy
		self.gz = (temp[5] << 8) | temp[4] # Store z-axis values into gz
		if(self._autoCalc):
			self.gx -= self.gBiasRaw[0]
			self.gy -= self.gBiasRaw[1]
			self.gz -= self.gBiasRaw[2]

	def readTemp(self):
		temp = self.I2Cbus.read_i2c_block_data(self.xgAddr, OUT_TEMP_L, 2) # We'll read two bytes from the temperature sensor into temp	

		offset = 25 # Per datasheet sensor outputs 0 typically @ 25 degrees centigrade
		self.Temperature = offset + (((temp[1] << 8) | temp[0]) >> 8)

	def setGyroScale(self, gScl) :
	 	ctrl1RegValue = self.I2Cbus.read_byte_data(self.xgAddr, CTRL_REG1_G) & 0xE7

	 	if (gScl == 500):
	 		ctrl1RegValue |= (0x1 << 3)
	 		self.settings.gyro.scale = 500
	 	elif(gScl == 2000):
	 		ctrl1RegValue |= (0x3 << 3)
	 		self.settings.gyro.scale = 2000
	 	else:
	 		self.settings.gyro.scale = 245
	
	 	self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG1_G, ctrl1RegValue)

	 	self.calcgRes()

	def setGyroODR(self, gRate):
	 	if (gRate & 0x07 != 0):
	 		temp = self.I2Cbus.read_byte_data(self.xgAddr, CTRL_REG1_G)

	 		temp &= 0xFF^(0x7 << 5)
	 		temp |= (gRate & 0x07) << 5

	 		self.settings.gyro.sampleRate = gRate & 0x07

	 		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG1_G, temp)

	def setAccelODR(self, aRate):
	 	if (aRate & 0x07 != 0):
	 		temp = self.I2Cbus.read_byte_data(self.xgAddr, CTRL_REG6_XL)

	 		temp &= 0x1F
	 		temp |= (aRate & 0x07) << 5

	 		self.settings.accel.sampleRate = aRate & 0x07

	 		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG6_XL, temp)

	def setAccelScale(self, aScl):
		#Input is a byte 

		tempRegValue = self.I2Cbus.read_byte_data(self.xgAddr, CTRL_REG6_XL)
		tempRegValue &= 0xE7

		if (aScl == 4):
			tempRegValue |= (0x2 << 3)
			self.settings.accel.scale = 4
		elif(aScl == 8):
			tempRegValue |= (0x3 << 3)
			self.settings.accel.scale = 8
		elif(aScl == 16):
			tempRegValue |= (0x1 << 3)
			self.settings.accel.scale =16
		else:
			self.settings.accel.scale = 2
		
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG6_XL, tempRegValue)

		self.calcaRes()

	def calcAccel(self, accel):
		return self.aRes * accel

	def calcGyro(self, gyro):
        return self.gRes * gyro
	
	def calcaRes(self):
		if (self.settings.accel.scale == 2):
			self.aRes = SENSITIVITY_ACCELEROMETER_2
		elif (self.settings.accel.scale == 4):
			self.aRes = SENSITIVITY_ACCELEROMETER_4
		elif (self.settings.accel.scale == 8):
			self.aRes = SENSITIVITY_ACCELEROMETER_8
		elif (self.settings.accel.scale == 16):
			self.aRes = SENSITIVITY_ACCELEROMETER_16
		else:
                        return
	
	def calcgRes(self):
                if self.settings.gyro.scale == 245:
                    self.gRes = SENSITIVITY_GYROSCOPE_245
                elif self.settings.gyro.scale == 500:
                    self.gRes = SENSITIVITY_GYROSCOPE_500
                elif self.settings.gyro.scale == 2000:
                    self.gRes = SENSITIVITY_GYROSCOPE_2000
                else:
                    return
	
	def calcmRes(self):
                if self.settings.mag.scale == 4:
                    self.mRes = SENSITIVTY_MAGNETOMETER_4
                elif self.settings.mag.scale == 8:
                    self.mRes = SENSITIVITY_MAGNETOMETER_8
                elif self.settings.mag.scale == 12:
                    self.mRes = SENSITIVITY_MAGNETOMETER_12
                elif self.settings.mag.scale == 16:
                    self.mRes = SENSITIVITY_MAGNETOMETER_16

	def enableFIFO(self, enable):
		temp = self.I2Cbus.read_byte_data(self.xgAddr, CTRL_REG9)
		if (enable):
			temp |= (1<<1)
		else:
			temp &= ~(1<<1)
		self.I2Cbus.write_byte_data(self.xgAddr, CTRL_REG9, temp)

	def setFIFO(self, fifomode, fifoThs):
		threshold =  fifoThs if (fifoThs <= 0x1F) else 0x1F
		self.I2Cbus.write_byte_data(FIFO_CTRL, ((fifomode & 0x07) << 5) | (threshold & 0x1F))
	
	def getFIFOSamples(self):
		return self.I2Cbus.read_byte_data(self.xgAddr, FIFO_SRC & 0x3F)

	def constrainScales(self):
		if ( (self.settings.gyro.scale != 245) & (self.settings.gyro.scale != 500) & (self.settings.gyro.scale != 2000)):
			self.settings.gyro.scale = 245
		
		if ( (self.settings.accel.scale != 2) & (self.settings.accel.scale != 4) & (self.settings.accel.scale != 8) & (self.settings.accel.scale != 16)):
			self.settings.accel.scale = 2

		self.settings.mag.scale = 4
	

		
	


