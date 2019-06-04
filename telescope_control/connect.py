import sys
sys.path.append('C:/Python27x86/lib/site-packages')
import gclib

global g
#make an instance of the gclib python class
g = gclib.py()

#connect to network
g.GOpen('10.1.2.245 --direct -s ALL')
#g.GOpen('COM1 --direct')

global g2
#make it again for the output frame
g2 = gclib.py()

#connect to network
g2.GOpen('10.1.2.245 --direct -s ALL')
#g.GOpen('COM1 --direct')

#used for galil commands
c = g.GCommand

c('AB') #abort motion and program
c('MO') #turn off all motors
c('SH') #servo on
c('TW=-1') #disable timeout