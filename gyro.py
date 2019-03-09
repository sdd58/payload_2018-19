def initGyro():
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
    I2C.write_byte_data(xgAddr, CTRL_REG1_G, tempRegValue)

    # CTRL_REG2_G (Default value: 0x00)
	# [0][0][0][0][INT_SEL1][INT_SEL0][OUT_SEL1][OUT_SEL0]
	# INT_SEL[1:0] - INT selection configuration
	# OUT_SEL[1:0] - Out selection configuration
    I2C.write_byte_data(xgAddr, CTRL_REG2_G, 0x00)

	# CTRL_REG3_G (Default value: 0x00)
	# [LP_mode][HP_EN][0][0][HPCF3_G][HPCF2_G][HPCF1_G][HPCF0_G]
	# LP_mode - Low-power mode enable (0: disabled, 1: enabled)
	# HP_EN - HPF enable (0:disabled, 1: enabled)
	# HPCF_G[3:0] - HPF cutoff frequency
    tempRegValue = (1<<7) if settings.gyro.lowPowerEnable else 0
    if settings.gyro.HPFEnable:
        tempRegValue |= (1<<6) | (settings.gyro.HPFCutoff & 0x0F)
    I2C.write_byte_data(xgAddr, CTRL_REG3_G, tempRegValue)

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
    I2C.write_byte_data(xgAddr, CTRL_REG4, tempRegValue)

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
    I2C.write_byte_data(xgAddr, ORIENT_CFG_G, tempRegValue)