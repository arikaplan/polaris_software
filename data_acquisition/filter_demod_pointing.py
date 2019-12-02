import sys
import numpy as np
import matplotlib.pyplot as plt
import h5py
import healpy as hp
import os
import filter_raw_mod as fm
import pandas as pd
import pickle

def combine_cofe_h5_pointing(dd, h5pointing, outfile='combined_data.pkl'):
    """
    combine demodulated data (output of get_demodulated_data_from_list) with H5 pointing data
    (output of get_h5_pointing), dump to a pkl file by default (this takes a long time to run)
    """
    paz = h5pointing['az'].copy()
    prev = h5pointing['gpstime'].copy()

    # need to use only 24 bits for comparison with science data gpstime- probably a better way to do this, bitmasking?
    prev &= 0x00ffffff

    # find all gpstime wrap points in current data set
    gpsdiff1 = np.diff(dd['rev'])
    gpsdiff2 = np.diff(prev)
    iwrap1 = np.where(gpsdiff1 < -2 ** 24 / 1000 / 2)[0]
    iwrap2 = np.where(gpsdiff2 < -2 ** 24 / 1000 / 2)[0]

    # unwrap gpstime
    for w in iwrap1:
        dd['rev'][w + 1:] = dd['rev'][w + 1:] + dd['rev'][w]
    for w in iwrap2:
        prev[w + 1:] = prev[w + 1:] + prev[w]

    pazw = np.where(abs(np.diff(paz) + 359.5) < 3)[0]
      # find the wrapping points so we can unroll the az for interpolation
    for r in pazw:
        paz[r + 1:] = paz[r + 1:] + 360.  # unwrap az

    flagout = np.interp(dd['rev'], prev, h5pointing['flag'])
    azout = np.interp(dd['rev'], prev, paz)
    azout = np.mod(azout, 360.)
    elout = np.interp(dd['rev'], prev, h5pointing['el'])
    pazw = np.where(abs(np.diff(azout) + 359.5) < 3)[0]

    f = open(outfile, 'wb')
    combined_data = {'sci_data': dd, 'az': azout, 'el': elout, 'gpstime': dd['rev'], 'flags': flagout}
    pickle.dump(combined_data, f, protocol=-1)
    f.close()
    return combined_data



day   = '06'
month = '08'
year  = '2018'
channel2clean = 'ch0'


demod_dir  = '/home/harald/Documents/UiO/GreenPol/data/demod_data/'
demod_day = year + month + day + '/'
pointing_dir = '/home/harald/Documents/UiO/GreenPol/data/pointing_data/'
pointing_day = month + '-' + day + '-' + year + '/'
dumpdir  = '/home/harald/Documents/UiO/GreenPol/clean_data/demod_data/'
calibration_file = 'calibration_list.txt'

demod_path = demod_dir + demod_day
pointing_path = pointing_dir + pointing_day

channel_list = ['ch0','ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','ch9','ch10','ch11','ch12','ch13','ch14','ch15']



# AC: Science; DC: Calibration
channel_info = {'ch0': 'H1 Hi AC',
                'ch1': 'H1 Hi DC',
                'ch2': 'H1 Lo AC',
                'ch3': 'H1 Lo DC',
                'ch4': 'H2 Hi AC',
                'ch5': 'H2 Hi DC',
                'ch6': 'H2 Lo AC',
                'ch7': 'H2 Lo DC',
                'ch8': 'H3 Hi AC',
                'ch9': 'H3 Hi DC',
                'ch10': 'H3 Lo AC',
                'ch11': 'H3 Lo DC',
                'ch12': 'Backend TSS',
                'ch13': 'Amplifier',
                'ch14': 'Cooler',
                'ch15': 'Calibrator'}

horn1 = {'ch0', 'ch1', 'ch2', 'ch3'}
horn2 = {'ch4', 'ch5', 'ch6', 'ch7'}
horn3 = {'ch8', 'ch9', 'ch10', 'ch11'}
science = {'ch0', 'ch4', 'ch8'}
housekeeping = {'ch12', 'ch13', 'ch14', 'ch15'}
dead = {'ch2,+ ch6'}

channels = {}


# Read demod data
dlist = []
d = []
counter = 0
for filename in sorted(os.listdir(demod_path)):
    if (filename[-2:]!='h5'):
        continue
    counter += 1
    hf = h5py.File(demod_path+filename)
    dlist.append(hf['demod_data'])

    if (counter==50):
        dtemp = np.concatenate(dlist)
        d.append(dtemp)
        hf.close()
        dlist = []
        counter = 0

dtemp = np.concatenate(dlist)
d.append(dtemp)
hf.close()

demod_data = np.concatenate(d)


# Open pointing files
dlist = []
d = []
counter = 0
for filename in sorted(os.listdir(pointing_path)):
    counter += 1
    if (filename[-2:]!='h5'):
        continue
    hf = h5py.File(pointing_path+filename)
    key = list(hf.keys())[0]
    dlist.append(hf[key][hf[key]['gpstime']>=hf[key]['gpstime'][0]])

    if (counter==50):
        dtemp = np.concatenate(dlist)
        d.append(dtemp)
        hf.close()
        dlist = []
        counter = 0

dtemp = np.concatenate(dlist)
d.append(dtemp)
hf.close()

pointing_data = np.concatenate(d)
hrevlist,inds = np.unique(pointing_data['gpstime'],return_index=True)
pointing_data = pointing_data[:][inds]

combined_data = combine_cofe_h5_pointing(demod_data, pointing_data)

samples_per_rev = 2122
flags = fm.flagging(combined_data['sci_data'][channel2clean]['T'],samples_per_rev)
flags[np.where(combined_data['flags']>9999)] = False
flags[np.where(combined_data['flags']>9999)] = False



# Plot results
# T
plt.figure(1)
plt.plot(combined_data['sci_data'][channel2clean]['T'])
combined_data['sci_data'][channel2clean]['T'][np.where(flags==False)] = np.nan
plt.plot(combined_data['sci_data'][channel2clean]['T'])
plt.title("T")
plt.show()

# Q
plt.figure(2)
plt.plot(combined_data['sci_data'][channel2clean]['Q'])
combined_data['sci_data'][channel2clean]['Q'][np.where(flags==False)] = np.nan
plt.plot(combined_data['sci_data'][channel2clean]['Q'])
plt.title("Q")
plt.show()

# U
plt.figure(3)
plt.plot(combined_data['sci_data'][channel2clean]['U'])
combined_data['sci_data'][channel2clean]['U'][np.where(flags==False)] = np.nan
plt.plot(combined_data['sci_data'][channel2clean]['U'])
plt.title("U")
plt.show()

T = combined_data['sci_data'][channel2clean]['T'][np.where(flags==True)]
Q = combined_data['sci_data'][channel2clean]['Q'][np.where(flags==True)]
U = combined_data['sci_data'][channel2clean]['U'][np.where(flags==True)]
gpstime = combined_data['gpstime'][np.where(flags==True)]
elevation = combined_data['el'][np.where(flags==True)]
azimuth = combined_data['az'][np.where(flags==True)]


hf = h5py.File(dumpdir+'clean_data_'+year+month+day+'_'+channel2clean+'.h5', "w")
hf.create_dataset("T", data=T)
hf.create_dataset("Q", data=Q)
hf.create_dataset("U", data=U)
hf.create_dataset("gpstime", data=gpstime)
hf.create_dataset("el", data=elevation)
hf.create_dataset("az", data=azimuth)
hf.close()





















