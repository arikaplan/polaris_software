"""
automatically run through the data file directories (assuming a fixed directory strucuture) 
and demodulate all perfect size files, place in demod_data/yyyymmdd.h5 files
skip already created demod files
"""

from contextlib import contextmanager
import os
import datetime as dt
import numpy as np
import h5py
import time
import sys
os.chdir('../../polaris_data/')
sys.path.append('../')
sys.path.append('../utils_meinhold/')
sys.path.append('../utils_zonca/')
from glob import glob
sys.path.append('../VtoT/')
from realtime_gp import get_demodulated_data_from_list

singledate=False
if len(sys.argv)>1:
	datedir=sys.argv[1]
	singledate=True

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir('../../polaris_data/'+os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

with cd('data'):
    datelist=glob('*')

if singledate:
	datelist=[datedir]
    
    
for ddate in datelist:
    try:
        os.mkdir('../../polaris_data/demod_data/%s' %ddate)
        flist=glob('../../polaris_data/data/%s/*.dat' %ddate)
        for filename in flist:
            if os.stat(filename).st_size == 10752000:  #require complete files
                try:
                    ddata=get_demodulated_data_from_list([filename])
                except:
                    print 'failed on: ', filename
                if ddata!= -1:
                    demod_file=filename[:19]+'demod_'+filename[19:-3]+'h5'
                    with h5py.File(demod_file, 'w') as h5file:
                        h5file.create_dataset("demod_data", data=ddata)
    except:
        #print( 'already have a demod_data directory for %s' %ddate)
        flist=glob('../../polaris_data/data/%s/*.dat' %ddate)
        for filename in flist:
            demod_file=filename[:19]+'demod_'+filename[19:-3]+'h5'
            if not(os.path.exists(demod_file)):
                if os.stat(filename).st_size == 10752000:  #require complete files
                    try:
                        ddata=get_demodulated_data_from_list([filename])
                    except:
                        print 'failed on: ', filename
                    if ddata!= -1:
                        demod_file=filename[:19]+'demod_'+filename[19:-3]+'h5'
                        with h5py.File(demod_file, 'w') as h5file:
                            h5file.create_dataset("demod_data", data=ddata)
            else:
                #print('%s already exists' %demod_file)
                pass
