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
    
    

    
