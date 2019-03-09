
from imu_reg import *

xgAddr = 0x6B
mAddr  = 0x1E

def LSM9DS1_init(interface, xgAddr, mAddr):
    
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
    
    for i in range(3):
        gBias[i] = 0
		aBias[i] = 0
		mBias[i] = 0
		gBiasRaw[i] = 0
		aBiasRaw[i] = 0
		mBiasRaw[i] = 0

    _autoCalc = false

def LSM9DS1_begin():

    constrainScales()
	# Once we have the scale values, we can calculate the resolution
	# of each sensor. That's what these functions are for. One for each sensor
	calcgRes() # Calculate DPS / ADC tick, stored in gRes variable
	calcmRes() # Calculate Gs / ADC tick, stored in mRes variable
	calcaRes() # Calculate g / ADC tick, stored in aRes variable

    I2C = initI2C()

    who_am_i_XG = I2C.read_byte_data(xgAddr,WHO_AM_I_XG)
    who_am_i_M  = I2C.read_byte_data(mAddr, WHO_AM_I_M)

    if ( who_am_i_XG != WHO_AM_I_AG_RSP | who_am_i_M != WHO_AM_I_M_RSP):
        return False

    initGyro()
    initAccel()
    initMag()

    return True

def initGyro():

    tempRegValue = 0

    if (settings.gyro.enabled):
        tempRegValue = (settings.gyro.sampleRate & 0x07) << 5

    if (settings.gyro.scale == 500):
        tempRegValue |= (0x1 << 3)
        break
    if (settings.gyro.scale == 2000):
        tempRegValue |= (0x3 << 3)
        break
    
def initI2C():
    bus = SMBus(1)
    return bus


