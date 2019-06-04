import sys
import h5py
import numpy as np
import logging
from multiprocessing import Process, Event
import os
import time
import shutil
def create_name(path):
    gettime=time.localtime()  
    getyear=gettime.tm_year-1  
    getmon=gettime.tm_mon-1  
    getday=gettime.tm_mday-1 
    if getmon==0:   
        getmon=12
    setpath=path+str(getyear)
    setpath2=setpath+"\\"+str(getmon)+"\\"+str(getday)
    print setpath2
   
    try:
        if(os.path.exists(setpath)):
            print u"exist"     
           
           # print u"subfolder",filelist
           # os.removedirs(setpath2); delete empty folder      
            filelist=os.listdir(setpath2)
            print "filelist",filelist         
            for i in filelist:
                filepath=os.path.join(setpath2,i)
                print u"filepath",filepath            
                if os.path.isfile(setpath2):
                   # os.remove(filepath)
                    os.removedirs(setpath2)#delete empty folder
                elif os.path.isdir(filepath):
                    print "5"
                    os.rmdir(filepath)
                    #shutil.rmtree(filepath,True)#
           
            '''
            for root,dirs,files in os.walk(filepath):
                for name in dirs:
                    os.rmdir(os.path.join(root,name))
                    print "2"
                for name in files:
                    os.remove(os.path.join(root,name))
                    print "3"
            #print u"exist, deleting"
            '''
        else:
            os.mkdir(path+str(getyear)) 
            os.chdir(path+str(getyear))
            os.mkdir(str(getmon))
            os.chdir(str(getmon))
            os.mkdir(str(getday))
            os.chdir(str(getday))
            filename=time.strftime('%H-%M-%S',time.localtime(time.time()))+".hdf5"
            return filename
    except Exception,e:
        print e

class Reader(Process):
    def __init__(self, event, rfname, rdsetname, timeout = 2.0):
        super(Reader, self).__init__()
        self._event = event
        self._fname = rfname
        self._dsetname = rdsetname
        self._timeout = timeout
        
    def run(self):
        self.log = logging.getLogger('reader')
        self.log.info("Waiting for initial event")
        assert self._event.wait( self._timeout )
        self._event.clear()
        
        self.log.info("Opening file %s", self._fname)
        f = h5py.File(self._fname, 'r', libver='latest', swmr=True)
        assert f.swmr_mode
        dset = f[self._dsetname]
        try:
            # monitor and read loop
            while self._event.wait( self._timeout ):
                self._event.clear()
                self.log.debug("Refreshing dataset")
                dset.refresh()

                shape = dset.shape
                self.log.info("Read dset shape: %s"%str(shape))
        finally:
            f.close()

class Writer(Process):
    def __init__(self, event, wfname, wdsetname):
        super(Writer, self).__init__()
        self._event = event
        self._fname = wfname
        self._dsetname = wdsetname
        
    def run(self):
        self.log = logging.getLogger('writer')
        self.log.info("Creating file %s", self._fname)
        f = h5py.File(self._fname, 'w', libver='latest')
        try:
            arr = np.array([1,2,3,4])
            dset = f.create_dataset(self._dsetname, chunks=(2,), maxshape=(None,), data=arr)
            assert not f.swmr_mode

            self.log.info("SWMR mode")
            f.swmr_mode = True
            assert f.swmr_mode
            self.log.debug("Sending initial event")
            self._event.set()        

            # Write loop
            for i in range(5):
                new_shape = ((i+1) * len(arr), )
                self.log.info("Resizing dset shape: %s"%str(new_shape))
                dset.resize( new_shape )
                self.log.debug("Writing data")
                dset[i*len(arr):] = arr
                #dset.write_direct( arr, np.s_[:], np.s_[i*len(arr):] )
                self.log.debug("Flushing data")
                dset.flush()
                self.log.info("Sending event")
                self._event.set()        
        finally:
            f.close()


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)10s  %(asctime)s  %(name)10s  %(message)s',level=logging.INFO)

    rfname = raw_input('Enter fname: ')+'.hdf5'
    rdsetname = raw_input('Enter dsetname: ')
    path=raw_input('Enter stroage path: ')
    wfname=create_name(path)
    wdsetname=wfname
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        print fname
    if len(sys.argv) > 2:
        dsetname = sys.argv[2]
        
    event = Event()
    reader = Reader(event, rfname, rdsetname)
    writer = Writer(event, wfname, wdsetname)
    
    logging.info("Starting reader")
    reader.start()
    logging.info("Starting reader")
    writer.start()
    
    logging.info("Waiting for writer to finish")
    writer.join()
    logging.info("Waiting for reader to finish")
    reader.join()