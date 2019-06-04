import storage_retrieval
import filter_processes
import numpy
calibration = 507.0
for i in range(1,5):
    dat = storage_retrieval.readPickle('7-24-15 Photon Reflection 35 amps test 1_Run_'+str(i)+'.pkl')
    
    dat[4] = dat[4] *1000
    dat[3] = dat[3]*975.83
    dat[0] = filter_processes.zeroDetector(dat[0])
    dat[2] = filter_processes.zeroDetector(dat[2])
    dat = filter_processes.calibrationFactorMult(dat,calibration,5,[3,4])
    dat = numpy.insert(dat, 0, numpy.arange(0,360,.1), axis=0)
    dat = numpy.transpose(dat)
    numpy.savetxt(str(i)+".csv", dat, delimiter=",")