from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
from numpy import zeros

""" 
functions to get DIO data and parse in to Az encoder, El encoder and 24 bit counter numbers
Mappings to DIO board  - modified to match Nic Rupert's new breakout board for greenpol summer 2017 PRM
    

****** Elevation Encoder (J4) ******

    el_bits=[43,18,42,17,41,16,40,15,39,91,66,90,65,89,64,88,63,87]
    elbin=[all[0][i] for i in el_bits]
    elint=bcd_to_int(''.join(elbin))
    el=np.mod(elgain*elint+eloffset,360.)
    
****** Azimuth Encoder (J2) ******

    az_bits=[23,47,22,46,21,45,20,44,71,95,70,94,69,93,68,92]
    azbin=[all[0][i] for i in az_bits]
    azint=bin_to_int(''.join(azbin))
    az=np.mod(azgain*azint+azoffset,360.)
    
****** 24 bit counter (J5) ******
		gps_bits=[24,48,0,73,25,49,1,74,26,50,2,75,27,51,3,76,28,52,4,77,29,53,5,78,30,54,6,79,31,55,7,80]
		gpsbin=[all[i] for i in gps_bits]
"""
class Eyeball(object):
	def __init__(self):
		self.data = numpy.zeros((97,), dtype=numpy.uint8)
		self.i = 0
		self.err=""
		self.read, self.bytesPerSamp=int32(), int32()
		DAQmxResetDevice('dev1')
		self.taskHandle=TaskHandle()
		
		DAQmxCreateTask("",byref(self.taskHandle))
		
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port0","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port1","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port2","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port3","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port4","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port5","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port6","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port7","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port8","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port9","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port10","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port11","",DAQmx_Val_ChanForAllLines)
		
		DAQmxStartTask(self.taskHandle)

	def close(self):
		print "bye"
		
		DAQmxStopTask(self.taskHandle)
		DAQmxClearTask(self.ta0kHandle)

	def __del__(self):
		#self.close()
		pass
	
	def getData(self):
		
		DAQmxReadDigitalLines(self.taskHandle,1,10.0,DAQmx_Val_GroupByChannel,self.data,100,byref(self.read),byref(self.bytesPerSamp),None)

		all = [self.data[d] for d in range(0,96)]
		all = map(str, all) 
		#el_bits=[43,18,42,17,41,16,40,15,39,91,66,90,65,89,64,88,63,87] #BEI encoder
		el_bits=[88,64,89,65,90,66,91,39,15,40,16,41,17,42,18,43] # gurley encoder
		#el_bits=el_bits[::-1]
		elbin=[all[i] for i in el_bits]
		az_bits=[23,47,22,46,21,45,20,44,71,95,70,94,69,93,68,92]
		azbin=[all[i] for i in az_bits]
		#gps_bits=[24,48,0,73,25,49,1,74,26,50,2,75,27,51,3,76,28,52,4,77,29,53,5,78,30,54,6,79,31,55,7,80]
		gps_bits=[80,7,55,31,79,6,54,30,78,5,53,29,77,4,52,28,76,3,51,27,75,2,50,26,74,1,49,25,73,0,48,24]
		#gps_bits=[80,7,55,31,79,6,54,30,78,5,53,29,77,4,52,28,76,3,51,27,75,2,50,26]
		gpsbin=[all[i] for i in gps_bits]
		#print gpsbin
		gpslock = all[72]
		#return  [''.join((all[2:8])[::-1])+''.join((all[10:16])[::-1])+''.join((all[18:24])[::-1]), ''.join((all[24:32])[::-1])+"".join((all[32:40])[::-1]), ''.join((all[40:48])[::-1])+''.join((all[48:56])[::-1])+''.join((all[56:64])[::-1])]
		return  [''.join(azbin),''.join(elbin),''.join(gpsbin), ''.join(gpslock)]
	
if __name__=='__main__':
	t = Eyeball()
	#t.getData()
	print t.getData()



		

		
		
		
