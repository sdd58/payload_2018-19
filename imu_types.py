from imu_reg import *
from enum import Enum

# The LSM9DS1 functions over both I2C or SPI. This library supports both.
# But the interface mode used must be sent to the LSM9DS1 constructor. Use
# one of these two as the first parameter of the constructor.
class interface_mode(Enum):
    IMU_MODE_SPI = 0
    IMU_MODE_I2C = 1

# accel_scale defines all possible FSR's of the accelerometer:
class accel_scale(Enum):
    A_SCALE_2G = 0      #00: 2g
    A_SCALE_16G = 1     #01: 16g
    A_SCALE_4G = 2      #10: 4g
    A_SCALE_8G = 3      #11: 8g

# gyro_scale defines the possible full-scale ranges of the gyroscope:
class gyro_scale(Enum):
    G_SCALE_245DPS = 0  #00: 245 degrees per second
    G_SCALE_500DPS = 1  #01: 500dps
    G_SCALE_2000DPS = 2 #11: 2000dps

# mag_scale defines all possible FSR's of the magnetometer:
class mag_scale(Enum):
    M_SCALE_4GS = 0     #00: 4Gs
    M_SCALE_8GS = 1     #01: 8Gs
    M_SCALE_12GS = 2    #10: 12Gs
    M_SCALE_16GS = 3    #11: 16Gs

# gyro_odr defines all possible data rate/bandwidth combos of the gyro:
class gyro_odr(Enum):
    G_ODR_PD = 0
    G_ODR_149 = 1
    G_ODR_595 = 2
    G_ODR_119 = 3
    G_ODR_238 = 4
    G_ODR_476 = 5
    G_ODR_952 = 6

# accel_oder defines all possible output data rates of the accelerometer:
class accel_odr(Enum):
    XL_POWER_DOWN = 0
    XL_ODR_10 = 1
    XL_ODR_50 = 2
    XL_ODR_119 = 3
    XL_ODR_238 = 4
    XL_ODR_476 = 5
    XL_ODR_952 = 6

# accel_abw defines all possible anti-aliasing filter rates of the accelerometer:
class accel_abw(Enum):
    A_ABW_408 = 0
    A_ABW_211 = 1
    A_ABW_105 = 2
    A_ABW_50 = 3

# mag_odr defines all possible output data rates of the magnetometer:
class mag_odr(Enum):
    M_ODR_0625 = 0
    M_ODR_125 = 1
    M_ODR_250 = 2
    M_ODR_5 = 3
    M_ODR_10 = 4
    M_ODR_20 = 5
    M_ODR_40 = 6
    M_ODR_80 = 7

class interrupt_select(Enum):
    XG_INT1 = INT1_CTRL
    XG_INT2 = INT2_CTRL

class interrupt_generators(Enum):
    INT_DRDY_XL = (1<<0)
    INT_DRDY_G = (1<<1)
    INT1_BOOT = (1<<2)
    INT2_DRDY_TEMP = (1<<2)
    INT_FTH = (1<<3)
    INT_OVR = (1<<4)
    INT_FSS5 = (1<<5)
    INT_IG_XL = (1<<6)
    INT1_IG_G = (1<<7)
    INT2_INACT = (1<<7)

class accel_interrupt_generator(Enum):
    XLIE_XL = (1<<0)
    XHIE_XL = (1<<1)
    YLIE_XL = (1<<2)
    YHIE_XL = (1<<3)
    ZLIE_XL = (1<<4)
    ZHIE_XL = (1<<5)
    GEN_6D = (1<<6)

class gyro_interrupt_generator(Enum):
    XLIE_G = (1<<0)
    XHIE_G = (1<<1)
    YLIE_G = (1<<2)
    YHIE_G = (1<<3)
    ZLIE_G = (1<<4)
    ZHIE_G = (1<<5)

class mag_interrupt_generator(Enum):
    ZIEN = (1<<5)
    YIEN = (1<<6)
    XIEN = (1<<7)

class h_lactive(Enum):
    INT_ACTIVE_HIGH = 0
    INT_ACTIVE_LOW = 1

class pp_od(Enum):
    INT_PUSH_PULL = 0
    INT_OPEN_DRAIN = 1

class fifoMode_type(Enum):
    FIFO_OFF = 0
    FIFO_THS = 1
    FIFO_CONT_TRIGGER = 3
    FIFO_OFF_TRIGGER = 4
    FIFO_CONT = 5

class gyroSettings:
    # Gyroscsope settings:
    enabled = None
    scale = None        # Changed this to 16-bit
    sampleRate = None
    # New gyro stuff:
    bandwidth = None
    lowPowerEnable = None
    HPFEnable = None
    HPFCutoff = None
    flipX = None
    flipY = None
    flipZ = None
    orientation = None
    enableX = None
    enableY = None
    enableZ = None
    latchInterrupt = None

class deviceSettings:
    commInterface = None # Can be I2C, SPI 4-wire or SPI 3-wire
    agAddress = None # I2C address or SPI CS pin
    mAddress = None # I2C address or SPI CS pin

class accelSettings:
    # Accelerometer settings:
    enabled = None
    scale = None
    sampleRate = None
    # New accel stuff:
    enableX = None
    enableY = None
    enableZ = None
    bandwidth = None
    highResEnable = None
    highResBandwidth = None

class magSettings:
    # Magnetometer settings:
    enabled = None
    scale = None
    sampleRate = None
    # New mag stuff:
    tempCompensationEnable = None
    XYPerformance = None
    ZPerformance = None
    lowPowerEnable = None
    operatingMode = None

class temperatureSettings:
    # Temperature settings
    enabled = None

class IMUSettings:
    device = None

    gyro = None
    accel = None
    mag = None

    temp = None
