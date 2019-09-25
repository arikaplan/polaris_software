import sys
import os
sys.path.append('../utils_meinhold')
sys.path.append('../utils_zonca')
sys.path.append('../utils_zonca/pointing')
sys.path.append('../')
sys.path.append('../telescope_control')
sys.path.append('../VtoT')
import realtime_gp as rt
import numpy as np
import datetime
import h5py
import pandas as pd
from pointingtools import compute_parallactic_angle, altaz2ha
from planets import getlocation
import warnings
from astropy.coordinates import AltAz, Angle, EarthLocation, ICRS, SkyCoord, frame_transform_graph
from astropy import units as u
import ephem
import matplotlib.pyplot as plt
import time
import Tkinter,tkFileDialog
from Tkinter import *
import ttk
import pickle
import glob
import cPickle


chan = 'ch0'
var = 'Q'
LOCATION = 'UCSB'

#gain in kelvin per volt
changain = {'ch0':-3.58, 'ch4':-9.47, 'ch8':-11.1}

#offset between local time and utctime in hours
ltoffset = 0


def get_pointing_files(filelist=None):
    if filelist == None:
        root = Tkinter.Tk()
        filelist = list(tkFileDialog.askopenfilenames( \
            initialdir='D://software_git_repos/greenpol/telescope_control/data_aquisition/pointing_data/', parent=root,
            title='Choose a set of files'))
        root.destroy()
    filelist.sort()

    return filelist


def read_some_data(filelist=None):
    if filelist == None:
        root = Tkinter.Tk()
        filelist = list(tkFileDialog.askopenfilenames( \
            initialdir='D://software_git_repos/greenpol/telescope_control/data_aquisition/demod_data/', parent=root,
            title='Choose a set of files'))
        root.destroy()
    filelist.sort()

    dlist = []
    for f in filelist:
        hf = h5py.File(f)
        dlist.append(hf['demod_data'])
    d = np.concatenate(dlist)
    hf.close()

    datadict = d

    return datadict, filelist


def get_file_times(fld):
    startfile = fld[0][:24] + fld[0][30:-2] + 'dat'
    endfile = fld[-1][:24] + fld[-1][30:-2] + 'dat'
    # print startfile
    # starttime = os.path.getctime(startfile)
    starttime = os.stat(startfile).st_mtime
    starttime = datetime.datetime.fromtimestamp(starttime)

    # endtime = os.path.getctime(endfile)
    endtime = os.stat(endfile).st_mtime
    endtime = datetime.datetime.fromtimestamp(endtime)

    return starttime, endtime

def fileStruct(n_array, chan, starttime, endtime):

    #fpath = "D:/software_git_repos/greenpol/telescope_control/data_aquisition/level1"
    #os.chdir(fpath)
    yrmoday = starttime.strftime('%Y%m%d')
    path = '-'.join((starttime.strftime('%H_%M_%S'), endtime.strftime('%H_%M_%S')))
    path = '-'.join((chan, path))
    print('start time: ', starttime)
    print('end time: ', endtime)
    print('elapsed time: ', (endtime - starttime).total_seconds(), 'sec')
    if not os.path.exists(yrmoday):#this is the first file being created for that time
        os.makedirs(yrmoday)
        #set index to 0

    path = '/'.join((yrmoday,path))
    path = '.'.join((path,"h5"))
    with h5py.File(str(path).replace("pkl","h5"), mode="w") as f:
        f.create_dataset("data", data=n_array.to_records(index=False))

def round_fraction(number, res):
    amount = int(number/res)*res
    remainder = number - amount
    return amount if remainder < res/2. else amount+res


def convert_gpstime(starttime, gpstime, ltoffset=0, bits_to_ms=2 ** 24, format='seconds', ttype='utc',
                    singletime=False):
    # function to convert gpstime to UTC time or local time

    # universal time day
    ltoffset = ltoffset * 60 * 60
    utcday = starttime + datetime.timedelta(0, ltoffset)

    # days since last sunday
    idx = (utcday.weekday() + 1) % 7

    # date of previous sunday in universal coord
    sunday = utcday - datetime.timedelta(idx)

    syear = int(str(sunday)[:4])
    smonth = int(str(sunday)[5:7])
    sday = int(str(sunday)[8:10])

    sunday = datetime.datetime(syear, smonth, sday, 0, 0, 0)

    # seconds since last sunday
    sundaysec = (utcday - sunday).total_seconds()

    # convert to seconds
    bits_to_sec = bits_to_ms / 1000

    # number of wraps so far
    numwraps = int(sundaysec / bits_to_sec)

    # time of last wrap
    gpsstarttime = sunday + datetime.timedelta(0, numwraps * bits_to_sec)

    # convert gps starttime to timestamp
    # gpsstarttime = (gpsstarttime-datetime.datetime(1970,1,1)).total_seconds()
    gpsstarttime = time.mktime(gpsstarttime.timetuple())

    if singletime == False:
        # find all wrap points in current data set
        gpsdiff = np.diff(gpstime)
        iwrap = np.where(gpsdiff < -2 ** 24 / 1000 / 2)[0]
        # iwrap = np.where(abs(gpsdiff) > 2**24/1000/2)[0]

        # unwrap gpstime
        for w in iwrap:
            gpstime[w + 1:] = gpstime[w + 1:] + gpstime[w]

    if ttype == 'utc':
        ltoffset = 0
    # gpstime gives seconds since starting point
    dtime = gpsstarttime + gpstime - ltoffset

    if format == 'datetime':
        if singletime == False:
            t = []
            for i in range(len(dtime)):
                t.append(datetime.datetime.fromtimestamp(dtime[i]))
        else:
            t = datetime.datetime.fromtimestamp(dtime)

        return t, dtime

    else:
        return dtime


ddict={}
print('pick data files')
dd, fld = read_some_data()
print('pick pointing files')
flp = get_pointing_files()
pp = rt.get_h5_pointing(flp)
combined = rt.combine_cofe_h5_pointing(dd,pp)
starttime, endtime = get_file_times(fld)

#seconds since last sunday utc
gpstime = dd['rev']/1000#(combined['gpstime'])/1000
dtime, utime = convert_gpstime(starttime, gpstime, ltoffset, format = 'datetime')

AZ = combined['az']
EL = combined['el']

location = getlocation(LOCATION)

#create ra dec sky object
azel = SkyCoord(az = AZ, alt = EL, obstime = dtime, location = location, frame = 'altaz', unit='deg')
print('starting the conversion from horizontal to celestial coordinates')
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    #convert from ra dec to az/el for pointing
    radec = azel.icrs
ra = radec.ra.rad
dec = radec.dec.rad

AZ = np.radians(AZ)
EL = np.radians(EL)

lat = location.latitude.rad
ha = altaz2ha(EL, AZ, lat)
psi = compute_parallactic_angle(ha, lat, dec)

#h5data=pd.DataFrame({"THETA" : np.pi/2 - THETA })
h5data=pd.DataFrame({"TIME" : utime})
h5data["PHI"] = ra
h5data["THETA"] = np.pi/2 - dec
h5data["PSI"] = psi
h5data["FLAG"] = np.zeros(len(dtime))
h5data["TEMP"] = combined['sci_data'][chan]['T']*changain[chan]
h5data["Q"] = combined['sci_data'][chan]['Q']*changain[chan]
h5data["U"] = combined['sci_data'][chan]['U']*changain[chan]

fileStruct(h5data, chan, starttime, endtime)