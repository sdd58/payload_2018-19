# def initGyro(self):
#     tempRegValue = 0

#     # CTRL_REG1_G (Default value: 0x00)
#     # [ODR_G2][ODR_G1][ODR_G0][FS_G1][FS_G0][0][BW_G1][BW_G0]
#     # ODR_G[2:0] - Output data rate selection
#     # FS_G[1:0] - Gyroscope full-scale selection
#     # BW_G[1:0] - Gyroscope bandwidth selection
	
#     # To disable gyro, set sample rate bits to 0. We'll only set sample
#     # rate if the gyro is enabled.
#     if settings.gyro.enabled:
#         tempRegValue = (settings.gyro.sampleRate & 0x07) << 5

#     if settings.gyro.scale == 500:
#         tempRegValue |= (0x1 << 3)
#     elif settings.gyro.scale == 2000:
#         tempRegValue |= (0x3 << 3)
#     # Otherwise we'll set it to 245 dps (0x0 << 4)

#     tempRegValue |= (settings.gyro.bandwidth & 0x3)
#     I2Cbus.write_byte_data(xgAddr, CTRL_REG1_G, tempRegValue)

#     # CTRL_REG2_G (Default value: 0x00)
# 	# [0][0][0][0][INT_SEL1][INT_SEL0][OUT_SEL1][OUT_SEL0]
# 	# INT_SEL[1:0] - INT selection configuration
# 	# OUT_SEL[1:0] - Out selection configuration
#     I2Cbus.write_byte_data(xgAddr, CTRL_REG2_G, 0x00)

# 	# CTRL_REG3_G (Default value: 0x00)
# 	# [LP_mode][HP_EN][0][0][HPCF3_G][HPCF2_G][HPCF1_G][HPCF0_G]
# 	# LP_mode - Low-power mode enable (0: disabled, 1: enabled)
# 	# HP_EN - HPF enable (0:disabled, 1: enabled)
# 	# HPCF_G[3:0] - HPF cutoff frequency
#     tempRegValue = (1<<7) if settings.gyro.lowPowerEnable else 0
#     if settings.gyro.HPFEnable:
#         tempRegValue |= (1<<6) | (settings.gyro.HPFCutoff & 0x0F)
#     I2Cbus.write_byte_data(xgAddr, CTRL_REG3_G, tempRegValue)

#     # CTRL_REG4 (Default value: 0x38)
# 	# [0][0][Zen_G][Yen_G][Xen_G][0][LIR_XL1][4D_XL1]
# 	# Zen_G - Z-axis output enable (0:disable, 1:enable)
# 	# Yen_G - Y-axis output enable (0:disable, 1:enable)
# 	# Xen_G - X-axis output enable (0:disable, 1:enable)
# 	# LIR_XL1 - Latched interrupt (0:not latched, 1:latched)
# 	# 4D_XL1 - 4D option on interrupt (0:6D used, 1:4D used)
#     tempRegValue = 0
#     if settings.gyro.enableZ:
#         tempRegValue |= (1<<5)
#     if settings.gyro.enableY:
#         tempRegValue |= (1<<4)
#     if settings.gyro.enableX:
#         tempRegValue |= 1<<3
#     if settings.gyro.latchInterrupt:
#         tempRegValue |= (1<<1)
#     I2Cbus.write_byte_data(xgAddr, CTRL_REG4, tempRegValue)

# 	# ORIENT_CFG_G (Default value: 0x00)
# 	# [0][0][SignX_G][SignY_G][SignZ_G][Orient_2][Orient_1][Orient_0]
# 	# SignX_G - Pitch axis (X) angular rate sign (0: positive, 1: negative)
# 	# Orient [2:0] - Directional user orientation selection
#     tempRegValue = 0
#     if settings.gyro.flipX:
#         tempRegValue |= (1<<5)
#     if settings.gyro.flipY:
#         tempRegValue |= (1<<4)
#     if settings.gyro.flipZ:
#         tempRegValue |= (1<<3)
#     I2Cbus.write_byte_data(xgAddr, ORIENT_CFG_G, tempRegValue)

# def gyroAvailable(self):
#     status = I2Cbus.read_byte_data(xgAddr, STATUS_REG_1)

#     return (status & (1<<0))

# def tempAvailable(self):
#     status = I2Cbus.read_byte_data(xgAddr, STATUS_REG_1)

#     return ((status & (1<<2)) >> 2)

# # def readTemp(self):
# #     temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_TEMP_L, 2) # We'll read two bytes from the temperature sensor into temp	

# #     offset = 25 # Per datasheet sensor outputs 0 typically @ 25 degrees centigrade
# #     temperature = offset + ((((int)temp[1] << 8) | temp[0]) >> 8)

# # def readGyro(self):
# #     temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_X_L_G, 6) # We'll read six bytes from the gyro into temp

# #     gx = (temp[1] << 8) | temp[0] # Store x-axis values into gx
# #     gy = (temp[3] << 8) | temp[2] # Store y-axis values into gy
# #     gz = (temp[5] << 8) | temp[4] # Store z-axis values into gz
# #     if(_autoCalc):
# #         gx -= gBiasRaw[0]
# #         gy -= gBiasRaw[1]
# #         gz -= gBiasRaw[2]

# # def readGyro(self, axis):
# #     temp = I2Cbus.read_i2c_block_data(xgAddr, OUT_X_L_G, 2)
# #     if len(temp) == 2:
# #         value = (temp[1] << 8) | temp[0]

# #         if(_autoCalc):
# #             value -= gBiasRaw[axis]
        
# #         return value
# #     return 0

# # def calcGyro(self, gyro):
# #     return gRes * gyro

# # def calcgRes(self):
# #     if settings.gyro.scale == 245:
# #         gRes = SENSITIVITY_GYROSCOPE_245
# #     elif settings.gyro.scale == 500:
# #         gRes = SENSITIVITY_GYROSCOPE_500
# #     elif settings.gyro.scale == 2000:
# #         gRes = SENSITIVITY_GYROSCOPE_2000
# #     else:
# #         return

# # def calcmRes(self):
#     # if settings.mag.scale == 4:
#     #     mRes = SENSITIVTY_MAGNETOMETER_4
#     # elif settings.mag.scale == 8:
#     #     mRes = SENSITIVITY_MAGNETOMETER_8
#     # elif settings.mag.scale == 12:
#     #     mRes = SENSITIVITY_MAGNETOMETER_12
#     # elif settings.mag.scale == 16:
#     #     mRes = SENSITIVITY_MAGNETOMETER_16