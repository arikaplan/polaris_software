# function to grab specified data from iotech USB acquisition board.
# simple and not very general, assumes all channels set the same
# for now hardwire to differential

from daq import daqDevice
import daqh
import os
dev=daqDevice('DaqBoard3001USB')
import daq
import ctypes as ct
from ctypes import wintypes as wt
import numpy as np
import time
jnk=np.zeros([2,3],dtype=float)
help,jnk

def get_date_filename():
    now=time.localtime()[0:6]
    #dirfmt = "c:\\cofe\\ground_data\\testdata\\%4d_%02d_%02d"
    dirfmt = "c:\\cofe\\ground_data\\testdata\\%4d_%02d_%02d"
    dirname = dirfmt % now[0:3]
    filefmt = "%02d_%02d_%02d.dat"
    filename= filefmt % now[3:6]
    ffilename=os.path.join(dirname,filename)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return(ffilename)
def read_io_file(filename,nchan=1):
    f=open(filename,'rb')
    d=np.fromfile(f,dtype=np.uint16)
    f.close()
    d=np.reshape(d,[len(d)/nchan,nchan])
    d=(np.array(d,dtype=float)-(2.**15))*20./(2.**16)
    return d
    
    
def get_data(nchan=1,freq=1000,nseconds=10):
    """
    function to simply acquire nchan a/d channels at rate freq
    for nseconds. divide into 1 sec buffers and try to get it all.
    """
    #outdata=np.zeros([nchan,nscans],dtype=float)
    outfile=get_date_filename()
    dev=daqDevice('DaqBoard3001USB')
    startChan=0
    endChan=nchan-1
    gains=[]
    flags=[]
    chans=[]
    for i in range(nchan):
        gains.append(daqh.DgainX1)
        flags.append(daqh.DafBipolar|daqh.DafDifferential)
        chans.append(i)
    acqmode=daqh.DaamInfinitePost
    dev.AdcSetAcq(acqmode,postTrigCount=nseconds*freq)
    dev.AdcSetScan(chans,gains,flags)
    
    transMask = daqh.DatmUpdateBlock|daqh.DatmCycleOn|daqh.DatmUserBuf
    dev.AdcSetTrig(daqh.DatsSoftware,0,0,0,0)
    dev.AdcSetRate(daqh.DarmFrequency,daqh.DaasPostTrig,freq)
    print freq*nchan*nseconds
    buf=dev.AdcTransferSetBuffer(transMask,freq*nchan*2)
    disk=dev.AdcSetDiskFile(outfile,daqh.DaomWriteFile,10)
    print disk
    print buf
    
    dev.AdcTransferStart()
    stat1=dev.AdcArm()
    print stat1
    dev.AdcSoftTrig()
    
    for i in range(nseconds):
        stat=dev.AdcTransferGetStat()
        print stat
        time.sleep(1)
    time.sleep(1)     
    #print '74'
    dev.AdcDisarm()
    return outfile
    
    
    
    