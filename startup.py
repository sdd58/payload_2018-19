
import time
import sys

t = time.gmtime(time.time())
f_PATH = '/home/pi/startup/logs/'
f_NAME = 'startuplog({0}:{1}:{2}).txt'.format(t[2],t[1],t[0])


f = open(f_PATH+f_NAME,'a+')
f.write(time.ctime(time.time()) + '\n')
f.write('startup sucess')
f.close()
