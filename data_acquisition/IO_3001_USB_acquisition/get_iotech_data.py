# function to grab specified data from iotech USB acquisition board.
# simple and not very general, assumes all channels set the same
# for now hardwire to differential

from daq import daqDevice
import daqh
import numpy as np
import time
import serial
import sys
import os






def get_data(nchan=4,freq=10,nseconds=5,comment='None',alerts=[58,59,60,118,119,120,178,179,180,238,239,240,298,299,300]):
    """
    function to simply aquire nchan a/d channels at rate freq
    for nseconds seconds
    """
    
    #outdata=np.zeros([nchan,nscans],dtype=float)
    dev=daqDevice('DaqBoard3001USB')
    gains=[]
    flags=[]
    chans=[]
    if nchan > 8:
        uchan=nchan-8
        for i in range(8):
            gains.append(daqh.DgainX1)
            flags.append(daqh.DafBipolar|daqh.DafDifferential)
            chans.append(i)
        for i in range(uchan):
            gains.append(daqh.DgainX1)
            flags.append(daqh.DafBipolar|daqh.DafDifferential)
            chans.append(256+i)   #HERE is the famous fix where DaqX refs upper level dif channels!
    elif nchan<9:      
        for i in range(nchan):
            gains.append(daqh.DgainX1)
            flags.append(daqh.DafBipolar|daqh.DafDifferential)
            chans.append(i)
    acqmode = daqh.DaamNShot
    dev.AdcSetAcq(acqmode, postTrigCount = nseconds*freq)
    dev.AdcSetScan(chans,gains,flags)
    dev.AdcSetFreq(freq)
    #use the driver buffer here user buffer was very limited (the way I tried anyway) 
    transMask = daqh.DatmUpdateBlock|daqh.DatmCycleOn|daqh.DatmDriverBuf

    buf=dev.AdcTransferSetBuffer(transMask, np.uint(nseconds*freq*nchan))
    #bufMask is for transferring the buffer
    bufMask = daqh.DabtmOldest | daqh.DabtmRetAvail

    timestart = (time.time())
    timenotify = timestart + 5

    dev.SetTriggerEvent(daqh.DatsImmediate,None, 0, np.array(gains[0],dtype=int), np.array(flags[0],dtype=int), daqh.DaqTypeAnalogLocal, 0, 0, daqh.DaqStartEvent)
    dev.SetTriggerEvent(daqh.DatsScanCount,None, 0, np.array(gains[0],dtype=int), np.array(flags[0],dtype=int), daqh.DaqTypeAnalogLocal, 0, 0, daqh.DaqStopEvent)
    dev.AdcTransferStart()
    dev.AdcArm()
    
    while True:
        
        
        alertscopy=alerts[:]
        timenotify = checkAlerts(timenotify, timestart, alerts,alertscopy)        
        
        stat = dev.AdcTransferGetStat()
        active = stat['active']
        if not (active & daqh.DaafAcqActive):
            break
    dev.AdcDisarm()
    outdata,ret=dev.AdcTransferBufData(nseconds*freq, nchan,bufMask)
    
    outdata=np.array(outdata,dtype=float)
    outdata=(outdata-2**15)*20./2**16
    outdata=np.transpose(np.reshape(outdata,[nseconds*freq,nchan]))
    print "Finished collecting data\n----------------------"
    dev.Close()
    

    
    return outdata
    
    
    
def get_data_pressure(nchan=4,freq=10,nseconds=5,comment='None',alerts=[58,59,0]):
    """
    function to simply aquire nchan a/d channels at rate freq
    for nseconds seconds
    """
    alertscopy = alerts[:]
    try:    
        #setup pressure gauge.
        pressuregauge = serial.Serial("COM5") #Change based on machine - go into device manager and check where it is.
        pressuregauge.setBaudrate(9600)
        pressuregauge.setParity(serial.PARITY_NONE)
        pressuregauge.setStopbits(serial.STOPBITS_ONE)
        pressuregauge.setTimeout(1)    
        
        
        #outdata=np.zeros([nchan,nscans],dtype=float)
        dev=daqDevice('DaqBoard3031USB')
        gains=[]
        flags=[]
        chans=[]
        if nchan > 8:
            uchan=nchan-8
            for i in range(8):
                gains.append(daqh.DgainX1)
                flags.append(daqh.DafBipolar|daqh.DafDifferential)
                chans.append(i)
            for i in range(uchan):
                gains.append(daqh.DgainX1)
                flags.append(daqh.DafBipolar|daqh.DafDifferential)
                chans.append(256+i)   #HERE is the famous fix where DaqX refs upper level dif channels!
        elif nchan<9:      
            for i in range(nchan):
                gains.append(daqh.DgainX1)
                flags.append(daqh.DafBipolar|daqh.DafDifferential)
                chans.append(i)
        acqmode = daqh.DaamNShot
        dev.AdcSetAcq(acqmode, postTrigCount = nseconds*freq)
        dev.AdcSetScan(chans,gains,flags)
        dev.AdcSetFreq(freq)
        #use the driver buffer here user buffer was very limited (the way I tried anyway) 
        transMask = daqh.DatmUpdateBlock|daqh.DatmCycleOn|daqh.DatmDriverBuf
    
        buf=dev.AdcTransferSetBuffer(transMask, np.uint(nseconds*freq*nchan))
        #bufMask is for transferring the buffer
        bufMask = daqh.DabtmOldest | daqh.DabtmRetAvail
    
        timestart = (time.time())
        timenotify = timestart + 5
        timepressure = 0 
    
        dev.SetTriggerEvent(daqh.DatsImmediate,None, 0, np.array(gains[0],dtype=int), np.array(flags[0],dtype=int), daqh.DaqTypeAnalogLocal, 0, 0, daqh.DaqStartEvent)
        dev.SetTriggerEvent(daqh.DatsScanCount,None, 0, np.array(gains[0],dtype=int), np.array(flags[0],dtype=int), daqh.DaqTypeAnalogLocal, 0, 0, daqh.DaqStopEvent)
        dev.AdcTransferStart()
        dev.AdcArm()
        
        pressures = []    
        if pressuregauge.inWaiting() > 12:
            v = pressuregauge.readline().strip()
            currentpressure = float((str(v).split())[1])
        else:
            currentpressure = -1
        
        while True:
                    
            if pressuregauge.inWaiting() > 12:
                v = pressuregauge.readline().strip()
                currentpressure = float((str(v).split())[1])
            if time.time()-timestart > timepressure:
                pressures += [currentpressure]
                timepressure += 1.0/freq
            
            timenotify = checkAlerts(timenotify, timestart, alerts, alertscopy)        
            
            stat = dev.AdcTransferGetStat()
            active = stat['active']
            if not (active & daqh.DaafAcqActive):
                break
        dev.AdcDisarm()
        outdata,ret=dev.AdcTransferBufData(nseconds*freq, nchan,bufMask)
        
        outdata=np.array(outdata,dtype=float)
        outdata=(outdata-2**15)*20./2**16
        outdata=np.transpose(np.reshape(outdata,[nseconds*freq,nchan]))
        if len(outdata[0]) > len(pressures): # if we have too few datapoints, add some new ones. This can make the last ~second of data unreliable.
            pressures = np.append(pressures, (np.zeros(len(outdata[0]) - len(pressures)))+pressures[-1])
        elif len(outdata[0]) < len(pressures): #If we have too many, truncate and discard the end data points.
            pressures = pressures[:len(outdata[0])]
        outdata = np.vstack((outdata, np.array(pressures)))
        print "Finished collecting data\n----------------------"
        dev.Close()
        
        pressuregauge.close()
        
        return outdata
    except KeyboardInterrupt:
        pressuregauge.close()
        print "Keyboard interrupt! Shutting down pressure gauge COM system!"
        sys.exit(0)


    

def checkAlerts(timeupdate,timestart, alerts, alertscopy, updateincrement=5):
    timecheck = (time.time())
    if timecheck > timeupdate:
        print "Time: " + str(int(timecheck - timestart))
        timeupdate += updateincrement
    for alert in alerts:
        if (timecheck - timestart)%60 > alert:
            print "---- " + str(int(timecheck - timestart)) + " SECONDS ----"
            alerts.remove(alert)
    if 2<(timecheck -timestart%60)<3:
        alerts = alertscopy[:]
        
        
    return timeupdate