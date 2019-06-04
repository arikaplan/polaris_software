"""
automatically run through the data file directories (assuming a fixed directory strucuture)
and demodulate all perfect size files, place in demod_data/yyyymmdd.h5 files
skip already created demod files
"""

import sys
import os
import sys
import os
#os.chdir('../../polaris_data')
sys.path.append('../telescope_control/')
sys.path.append('../')
sys.path.append('../utils_meinhold/')
sys.path.append('../utils_zonca/')
sys.path.append('../utils_zonca/pointing')
from glob import glob
import numpy as np
import datetime
import h5py
import pandas as pd
from pointingtools import compute_parallactic_angle, altaz2ha
from planets import getlocation
import warnings
from astropy.coordinates import AltAz, Angle, EarthLocation, ICRS, SkyCoord, frame_transform_graph
from astropy import units as u
import pickle
import math
from contextlib import contextmanager
import realtime_gp as rt

#%pylab

LOCATION = 'UCSB' #this will need to be changed when we are in Greenland, obviously
ltoffset = 7 #offset between local time and universal time in hours, eventually this should become redundant when were always working in utc time

#figure out how to use subsequent logic and run run_demod.py before hand without interference
# (os.system('python hello.py sys.argv[1]'))
singledate=False
if len(sys.argv)>1:
	datedir=sys.argv[1]
	singledate=True

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

with cd('demod_data'):
    datelist=glob('*')

if singledate:
	datelist=[datedir]

channels = ['H1HiDC']#, 'H1HiAC','H2HiAC','H3HiAC']
#gain in kelvin per volt based on last calibration
changain = {'ch1':-1.48,'ch0':-1.48, 'ch4':-1.74, 'ch8':-1.4}

for chan in channels:
    print 'starting channel: ', chan
    chan = rt.nametochan(chan)
    for ddate in datelist:

        if not os.path.exists('./level1/%s' %ddate):
            os.mkdir('../../polaris_data//level1/%s' %ddate)

        iend = 0
        fl1 = glob('../../polaris_data/level1/%s/%s*.h5' % (ddate, chan))

        fld = glob('../../polaris_data/demod_data/%s/*.h5' % ddate)

        #check to see if there is a file already in lvl1, create files after that
        if len(fl1)>0:
            prevendfile = fl1[-1][-11:-3]
            for f in range(len(fld)):
                if fld[f][-11:-3] == prevendfile:
                    iend = f

            fld = fld[iend+1:]

        modayyr = ddate[4:6] + '-' + ddate[-2:] + '-' + ddate[:4]
        flp = glob('../../polaris_data/pointing_data/%s/*.h5' % modayyr)

        dd = rt.get_demodulated_h5(fld)
        pp = rt.get_h5_pointing(flp)

        combined = rt.combine_cofe_h5_pointing(dd, pp)

        print 'you need to fix these string numbers since you changed file structure !!!!!!!!!!!!!!!!!!!!'
        startfile = fld[0][6:-3]+'.dat'
        starttime = os.path.getctime(startfile)
        starttime = datetime.datetime.fromtimestamp(starttime)

        endfile = fld[-1][6:-3] + '.dat'
        endtime = os.path.getctime(endfile)
        endtime = datetime.datetime.fromtimestamp(endtime)

        gpstime = combined['gpstime'] / 1000

        utcdatetime, utctime = rt.convert_gpstime(starttime, gpstime, ltoffset)

        AZ = combined['az']
        EL = combined['el']

        location = getlocation(LOCATION)

        # create ra dec sky object
        azel = SkyCoord(az=AZ, alt=EL, obstime=utcdatetime, location=location, frame='altaz', unit='deg')

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # convert from ra dec to az/el for pointing
            radec = azel.icrs

        ra = radec.ra.rad
        dec = radec.dec.rad

        for a in range(len(AZ)):
            AZ[a] = math.radians(AZ[a])
            EL[a] = math.radians(EL[a])

        lat = location.latitude.rad
        ha = altaz2ha(EL, AZ, lat)
        psi = compute_parallactic_angle(ha, lat, dec)

        h5data = pd.DataFrame({"TIME": utctime})
        h5data["PHI"] = ra
        h5data["THETA"] = np.pi / 2 - dec
        h5data["PSI"] = psi
        h5data["FLAG"] = np.zeros(len(utctime))
        h5data["TEMP"] = combined['sci_data'][chan]['T']*changain[chan]
        h5data["Q"] = combined['sci_data'][chan]['Q']*changain[chan]
        h5data["U"] = combined['sci_data'][chan]['U']*changain[chan]

        #yrmoday = starttime.strftime('%Y%m%d')
        print 'start time: ', starttime
        print 'end time: ', endtime
        telapsed = (endtime - starttime).total_seconds()
        if telapsed < 60:
            print 'elapsed time: ', telapsed, 'seconds'
        elif telapsed < 60.*60.:
            telapsed = telapsed/60.
            print 'elapsed time: ', telapsed, 'minutes'
        else:
            telapsed = telapsed/60./60.
            print 'elapsed time: ', telapsed, 'hours'

        lvl1_file = '%s-%s-%s.h5' % (
        chan, startfile[-12:-4], endfile[-12:-4])

        fpath = "../../polaris_data/level1"
        path = '/'.join((fpath, ddate))
        path = '/'.join((path, lvl1_file))

        with h5py.File(str(path).replace("pkl", "h5"), mode="w") as f:
           f.create_dataset("data", data=h5data.to_records(index=False))

        fl1 = glob('../../polaris_data/level1/%s/%s*.h5' % (ddate, chan))

        if len(fl1) > 1:
            prevstartfile = fl1[-1][-20:-12]
            prevh5data = h5py.File(fl1[0])['data']
            newh5data = h5py.File(fl1[-1])['data']
            h5data = np.concatenate([prevh5data, newh5data])
            lvl1_file = '%s-%s-%s.h5' % (
                chan, prevstartfile, endfile[-12:-4])

            fpath = "../../polaris_data/level1"
            path = '/'.join((fpath, ddate))
            path = '/'.join((path, lvl1_file))

            with h5py.File(path, 'w') as h5file:
                h5file.create_dataset("data", data=h5data)


        '''
        #print( 'already have a demod_data directory for %s' %ddate)
        fl1=glob('level1/%s/*.h5' %ddate)[-1]
        fld=glob('demod_data/%s/*.h5' %ddate)
        flp = glob('pointing_data/%s/*.h5' % modayyr)

        makelvl1(chan, date, fld, flp)
        else:
            #print('%s already exists' %demod_file)
            pass
        '''