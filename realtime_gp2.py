"""
set of scripts to run while taking data for first look analysis
(run from main ground_cofe directory so paths work out right"""
import sys
sys.path.append('../')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/VtoT')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/cofe-python-analysis-tools-master/utils_meinhold')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/cofe-python-analysis-tools-master/utils_zonca')
#sys.path.append('D://software_git_repos//greenpol//telescope_control//VtoT')
#sys.path.append('telescope_control\VtoT')
from glob import glob
import os
import matplotlib.pyplot as plt
import cofe_util as cu
import demod
import h5py
import cPickle
import numpy as np
from numpy.lib import recfunctions as recf
from plot_path import *
from prm_util import nps
import time
import scipy.interpolate
import numpy.ma as ma
import convert
from scipy.special import lambertw
import pickle
import datetime
import plot_path as p_p


samprate=27.  #assumed spin rate of pol modulator for rough time estimation inside files

def get_h5_pointing(filelist,startrev=None, stoprev=None,angles_in_ints=False,azel_era=3):
        """
                modify to fast version, dont' average the multiple values, just take the first one. will cause a little bias but its very fast.
        also implmented removal of erroneous endof h5 file crap, and az outliers
        azel_era determines what az/el offsets to use, 1 means before 9/26/2013, 2 means 9/26-10/3 (inclusive), 3 means after 10/4.
        """
        #filelist is complete path list to the h5 files
        elconversion=-360./40000.
        azconversion=-360./(2.**16)
        #eloffset=8.2-3.17382
        #eloffset=5.026 # correction from 2013/08/02 moon crossing for both az and el this for ch 3! 
        #azoffset=4.41496
        # on 2013/08/20, updated converter.py to include these offsets, in theory they should now be zero.
        eloffset =0.0
        azoffset=0.0
        #ch1 would be azoffset=198.7810-187.663   or 11.118
        #             eloffset= 8.2-5.69175  
        #             eloffset= 2.5082
        #note October 4, 2013. Just found that data from 9/26/13 through 10/04/13 used old converter.py. So special 
        #offsets needed:
        #update, 10/8/13. ran get_cofe_crossing on second sun crossing from 10/04 (after subtracting 
        #template estimate of satellites,important effect). delta offsets: az=2.10,el=0.934
        #these then would be future offsets
        #update, 11/19/13. Ran mapmaking on lots of days, found an offset in the two daily crossings of the Crab- used ephem
        #to find the crossings, found that should get a self-consistent solution for both if the azimth is reduced by 4.51 degrees
        #and the elevation is increased by  2.241 degrees.
        '''
        if azel_era==1:
                eloffset=5.026
                azoffset=4.41496+140.0
        if azel_era==2:
                eloffset=5.026+0.934
                azoffset=4.41496+140.0+2.1
        if azel_era==3:
                eloffset=0.934+2.241
                azoffset=2.10 -4.51
        '''
        


        errlimit=0.1
        if angles_in_ints==True:
                errlimit=10
        hpointing = []
        filelist.sort()
        for f in filelist:
                if f[79:88] != 'corrected':
                        slimit = 22144
                else:
                        slimit = 11512
                stats=os.stat(f)
                if stats.st_size<slimit:
                        print (f,stats.st_size)
                if stats.st_size >= slimit:
                        h=h5py.File(f)
                        hh=h['data']
                        hpointing.append(hh[hh['gpstime']>=hh['gpstime'][0]])
                        #print (hpointinng)
                        h.close()
        
        hpointing = np.concatenate(hpointing)

        #cut out blank lines from unfilled files
        if startrev != None:
                hpointing=hpointing[hpointing['gpstime'] > startrev]
        if stoprev != None:
                hpointing=hpointing[hpointing['gpstime'] < stoprev]

        hrevlist,inds=np.unique(hpointing['gpstime'],return_index=True)
        hrevlist = hrevlist/1000
        elmeans = hpointing['el'][inds]
        azmeans = hpointing['az'][inds]
        h1means = hpointing['H1'][inds]
        h2means = hpointing['H2'][inds]
        h3means = hpointing['H3'][inds]
        cryo1means = hpointing['Backend TSS'][inds]
        cryo2means = hpointing['Amplifier'][inds]
        cryo3means = hpointing['Cooler'][inds]
        cryo4means = hpointing['Calibrator'][inds]
        azlevmeans = hpointing['x tilt'][inds]
        ellevmeans = hpointing['y tilt'][inds]
        azoffsetmeans = hpointing['az offset'][inds]
        eloffsetmeans = hpointing['el offset'][inds]
        comptimemeans = hpointing['computer time'][inds]
        flagmeans = hpointing['flag'][inds]
        try:
                phtempmeans = hpointing['Phidget Temp'][inds]
        except:
                phtempmeans = []
        #("az offset", np.float), ("el offset", np.float), ("computer time", np.float), ("flag", np.int)])

        #get rid of az outliers:

        azmeans=np.mod(azmeans+azoffset,360.)
        elmeans=np.mod(elmeans+eloffset,90.)
        daz=np.diff(azmeans)

        maxstep = 5.
        badaz=np.unique(np.where(np.logical_and((np.abs(daz) > maxstep) , (np.abs(daz+359.5) > maxstep)))[0])
        if len(badaz) > 1:
                if (badaz[-1]-len(daz) < 3):
                        badaz=badaz[:-1]
                if (badaz[0] < 3):
                        badaz=badaz[1:]
                azmeans[badaz]=(azmeans[badaz-2]+azmeans[badaz+2])/2.0
        azmeans=np.mod(azmeans,360.)
        print("Backend_TSS", cryo1means)
        print("Calibrator",cryo4means)
        print('Phidget_Temp',phtempmeans)
        return {'el':elmeans,'az':azmeans,'gpstime':hrevlist, 'H1':h1means, 'H2':h2means, 'H3':h3means, 'Backend_TSS':cryo1means
                , 'Amplifier':cryo2means, 'Cooler':cryo3means, 'Calibrator':cryo4means
                , 'x_tilt':azlevmeans, 'y_tilt':ellevmeans, 'az offset':azoffsetmeans, 'el offset':eloffsetmeans, 'computer time':comptimemeans
                , 'flag':flagmeans, 'Phidget_Temp':phtempmeans}

def get_h5_pointing_old(filelist,startrev=None, stoprev=None,angles_in_ints=False,azel_era=3):
        """
                modify to fast version, dont' average the multiple values, just take the first one. will cause a little bias but its very fast.
        also implmented removal of erroneous endof h5 file crap, and az outliers
        azel_era determines what az/el offsets to use, 1 means before 9/26/2013, 2 means 9/26-10/3 (inclusive), 3 means after 10/4.
        """
        
        #filelist is complete path list to the h5 files
        elconversion=-360./40000.
        azconversion=-360./(2.**16)
        #eloffset=8.2-3.17382
        #eloffset=5.026 # correction from 2013/08/02 moon crossing for both az and el this for ch 3! 
        #azoffset=4.41496
        # on 2013/08/20, updated converter.py to include these offsets, in theory they should now be zero.
        eloffset =0.0
        azoffset=0.0
        #ch1 would be azoffset=198.7810-187.663   or 11.118
        #             eloffset= 8.2-5.69175  
        #             eloffset= 2.5082
        #note October 4, 2013. Just found that data from 9/26/13 through 10/04/13 used old converter.py. So special 
        #offsets needed:
        #update, 10/8/13. ran get_cofe_crossing on second sun crossing from 10/04 (after subtracting 
        #template estimate of satellites,important effect). delta offsets: az=2.10,el=0.934
        #these then would be future offsets
        #update, 11/19/13. Ran mapmaking on lots of days, found an offset in the two daily crossings of the Crab- used ephem
        #to find the crossings, found that should get a self-consistent solution for both if the azimth is reduced by 4.51 degrees
        #and the elevation is increased by  2.241 degrees.
        '''
        if azel_era==1:
                eloffset=5.026
                azoffset=4.41496+140.0
        if azel_era==2:
                eloffset=5.026+0.934
                azoffset=4.41496+140.0+2.1
        if azel_era==3:
                eloffset=0.934+2.241
                azoffset=2.10 -4.51
        '''
        
        errlimit=0.1
        if angles_in_ints==True:
                errlimit=10
        hpointing=[]
        filelist.sort()
        for f in filelist:
                stats=os.stat(f)
                if stats.st_size<22144:
                        print (f,stats.st_size)
                if stats.st_size >= 22144:
                        h=h5py.File(f)
                        hh=h['data']
                        hpointing.append(hh[hh['gpstime']>=hh['gpstime'][0]])
                        #print (hpointinng)
                        h.close()
        
        hpointing = np.concatenate(hpointing)
        #cut out blank lines from unfilled files
        if startrev != None:
                hpointing=hpointing[hpointing['gpstime'] > startrev]
        if stoprev != None:
                hpointing=hpointing[hpointing['gpstime'] < stoprev]

        hrevlist,inds=np.unique(hpointing['gpstime'],return_index=True)
        elmeans=hpointing['el'][inds]
        azmeans=hpointing['az'][inds]

        #("az offset", np.float), ("el offset", np.float), ("computer time", np.float), ("flag", np.int)])

        #get rid of az outliers:

        azmeans=np.mod(azmeans+azoffset,360.)
        elmeans=np.mod(elmeans+eloffset,90.)
        daz=np.diff(azmeans)

        maxstep = 5.
        badaz=np.unique(np.where(np.logical_and((np.abs(daz) > maxstep) , (np.abs(daz+359.5) > maxstep)))[0])
        if len(badaz > 1):
                if (badaz[-1]-len(daz) < 3):
                        badaz=badaz[:-1]
                if (badaz[0] < 3):
                        badaz=badaz[1:]
                azmeans[badaz]=(azmeans[badaz-2]+azmeans[badaz+2])/2.0
        azmeans=np.mod(azmeans,360.)
        return {'el':elmeans,'az':azmeans,'gpstime':hrevlist}


def get_demodulated_data_from_list(filelist,freq=10,supply_index=False,phase_offset=0): #***********
        filelist.sort() #just in case
        
        dd=[]
        for f in filelist:
                #only use full size files
                stats=os.stat(f)
                #print(stats.st_size)
                if stats.st_size >5000000: #full length is 10752000:
                        d=demod.demodulate_dat(f,freq,supply_index=False,phase_offset=phase_offset)
                        #filename is start of data taking (I think) and we'll just add 1/samprate seconds per rev
                        h=np.float64(f[-12:-10])
                        m=np.float64(f[-10:-8])
                        s=np.float64(f[-8:-6])
                        t=h+m/60.+(s+(d['rev']-d['rev'][0])/samprate)/3600.
                        d=recf.append_fields(d,'localtime',t)
                        ut=np.mod(t+7.,24.)
                        if len(f)>21:
                                y=np.zeros(len(d),dtype=np.int)+np.int(f[-21:-17])
                                mo=np.zeros(len(d),dtype=np.int)+np.int(f[-17:-15])
                                dy=np.zeros(len(d),dtype=np.int)+np.int(f[-15:-13])
                                ut=np.mod(t+7.,24.)
                                utt=t+7.
                                dy[utt>ut]=dy[utt>ut]+1
                                d=recf.append_fields(d,['year','month','day'],[y,mo,dy])
                        d=recf.append_fields(d,'ut',ut)
                        dd.append(d)

        return np.concatenate(dd)

def get_file_times(fld):
        startfile = fld[0][:65] + fld[0][71:-2] + 'dat'
        endfile = fld[-1][:65] + fld[-1][71:-2] + 'dat'

        # starttime = os.path.getctime(startfile)
        starttime = os.stat(startfile).st_mtime
        starttime = datetime.datetime.fromtimestamp(starttime)

        # endtime = os.path.getctime(endfile)
        endtime = os.stat(endfile).st_mtime
        endtime = datetime.datetime.fromtimestamp(endtime)

        return starttime, endtime


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
        print('dd', type(dd))
        gpsdiff1 = np.diff(dd['rev'])
        gpsdiff2 = np.diff(prev)
        iwrap1 = np.where(gpsdiff1 < -2 ** 24 / 1000 / 2)[0]
        iwrap2 = np.where(gpsdiff2 < -2 ** 24 / 1000 / 2)[0]

        # unwrap gpstime
        for w in iwrap1:
                dd['rev'][w + 1:] = dd['rev'][w + 1:] + dd['rev'][w]
        for w in iwrap2:
                prev[w + 1:] = prev[w + 1:] + prev[w]

        pazw = np.where(abs(np.diff(paz) + 359.5) < 3)[
                0]  # find the wrapping points so we can unroll the az for interpolation
        for r in pazw:
                paz[r + 1:] = paz[r + 1:] + 360.  # unwrap az
        azout = np.interp(dd['rev'], prev, paz)
        azout = np.mod(azout, 360.)
        elout = np.interp(dd['rev'], prev, h5pointing['el'])
        #pazw = np.where(abs(np.diff(azout) + 359.5) < 3)[0]

        f = open(outfile, 'wb')
        combined_data = {'sci_data': dd, 'az': azout, 'el': elout, 'gpstime': dd['rev']}
        cPickle.dump(combined_data, f, protocol=-1)
        f.close()
        return combined_data
        
def bin_to_az_el(indata,nazbins=360,nelbins=90,chan='ch3',cmode='T',revlimits=[0,2**24]):
        """
        straight binning code for data that's been associated with H5 pointing
        assume combined_dict came from combine_cofe_h5_pointing, that az and el are in degrees
        """
        
        azhalfbin=360./(nazbins*2.0)
        elhalfbin=90./(nelbins*2.0)
        azlist=np.arange(nazbins)*360./nazbins
        ellist=np.arange(nelbins)*90./nelbins
        chandata=-indata['sci_data'][chan][cmode][np.logical_and(indata['sci_data']['rev'] > revlimits[0],indata['sci_data']['rev']< revlimits[1])]
        eldata=indata['el'][np.logical_and(indata['sci_data']['rev'] > revlimits[0],indata['sci_data']['rev']< revlimits[1])]
        azdata=360.-indata['az'][np.logical_and(indata['sci_data']['rev'] > revlimits[0],indata['sci_data']['rev']< revlimits[1])]
        # make empty output map
        outmap=np.zeros([nazbins,nelbins],dtype=np.float64) 
        for x,azi in enumerate(azlist):
                for y,eli in enumerate(ellist):
                        outmap[x,y]=np.mean(chandata[np.logical_and(abs(eldata-eli) < elhalfbin,abs(azdata-azi) < azhalfbin)])
        mapoffset=np.nanmin(outmap)
        outmap=np.nan_to_num(outmap-mapoffset)
        return outmap

def chantoname(chan):
    #function to convert channel numbers to channel names

    #names of each channel
    names = {
        'all': 'all', 'ch0': 'H1 Hi AC', 'ch1': 'H1 Hi DC',
        'ch2': 'H1 Lo AC', 'ch3': 'H1 Lo DC', 'ch4': 'H2 Hi AC',
        'ch5': 'H2 Hi DC', 'ch6': 'H2 Lo AC', 'ch7': 'H2 Lo DC',
        'ch8': 'H3 Hi AC', 'ch9': 'H3 Hi DC', 'ch10': 'H3 Lo AC',
        'ch11': 'H3 Lo DC', 'ch13':'Amplif','ch14':'Cooler'}

    name = names[chan]

    return name

def nametochan(name):
    #function to convert channel numbers to channel names

    #names of each channel
    chans = {
    'all': 'all',  'H1HiAC':'ch0',  'H1HiDC':'ch1',
    'H1LoAC':'ch2' ,  'H1LoDC':'ch3', 'H2HiAC':'ch4' ,
    'H2HiDC':'ch5' ,  'H2LoAC':'ch6',  'H2LoDC':'ch7',
    'H3HiAC':'ch8', 'H3HiDC':'ch9',  'H3LoAC':'ch10',
     'H3LoDC':'ch11','Amplif': 'ch13', 'Cooler':'ch14'}

    chan = chans[name]

    return chan

def get_demodulated_h5(filelist):
        demod_dd = []
        for f in filelist:
            h = h5py.File(f)
            demod_dd.append(h['demod_data'])

        demod_dd = np.concatenate(demod_dd)
        h.close()

        return demod_dd 

def get_all_demodulated_data(fld_demod, fld):

    if len(fld_demod) != 0 and len(fld) != 0:
        demod_dd = get_demodulated_h5(fld_demod)
        dd = get_demodulated_data_from_list(fld)
        
        return np.concatenate((demod_dd, dd), 0)
    
    elif len(fld_demod) != 0 and len(fld) == 0:
        demod_dd = get_demodulated_h5(fld_demod)
        return demod_dd
    
    elif len(fld_demod) == 0 and len(fld) != 0:
        dd = get_demodulated_data_from_list(fld)

        return dd
    
    else:
        print ('need at least one array!!!!!!!!!')

def get_file_times(fld):
        startfile = fld[0][:65] + fld[0][71:-2] + 'dat'
        endfile = fld[-1][:65] + fld[-1][71:-2] + 'dat'

        # starttime = os.path.getctime(startfile)
        starttime = os.stat(startfile).st_mtime
        starttime = datetime.datetime.fromtimestamp(starttime)

        # endtime = os.path.getctime(endfile)
        endtime = os.stat(endfile).st_mtime
        endtime = datetime.datetime.fromtimestamp(endtime)

        return starttime, endtime

def plotnow(yrmoday,chan,var, xaxis,st_hour,st_minute,ed_hour,ed_minute,combined,ax1,ax2,ax3,supply_index=False):
        """
        plots scidata vs az

        function to automatically read last 2 science files and last few pointing
        files, combine and plot signal vs azimuth. yrmoday should be a string
        '20130502' fpath should point to the 
        spot where acq_tel and converter.py were run
        """
        '''flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld = []
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)

        pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        dd=get_all_demodulated_data(fld_demod, fld)
        combined=combine_cofe_h5_pointing(dd,pp)'''
        
        xa = combined[xaxis]
        data = combined['sci_data'][chan][var]

        #sort data according to sorted azimuth
        data = [x for _,x in sorted(zip(xa,data))]
        xa = sorted(xa)
        
        #convert to temp for cryo sensors
        if chan == 12:
                data1 = data1*10. + 273.15
        if chan == 13:
                data1 = convert.convert(data1, 'e')
        if chan == 14:
                data1 = convert.convert(data1, 'h')
        if chan == 15:
                data1 = data1*10. + 273.15
        if chan == 'Phidget_Temp':
                data = data*10. + 273.15

        name = chantoname(chan)
        #change units on plot label
        if int(chan[2:]) == 12 or int(chan[2:])==13 or chan == 'Phidget_Temp':
                unit = 'K'
                ax2.plot(xa,data,label=name)
        else:
                unit = 'V' 
                ax1.plot(xa,data,label=name)


        #plt.plot(xa,data,label=name)
        if xaxis == 'gpstime':
                plt.xlabel('gpstime')
        else:
                plt.xlabel('%s angle, degrees' % xaxis)
        #plt.ylabel('Signal, %s' % unit)
        plt.title(name+' COFE %s data binned to %s, date: %s, %s:%d - %s:%d' % (var, xaxis, yrmoday, st_hour, int(st_minute), ed_hour, int(ed_minute))) 
        #plt.legend()
        plt.grid()
        #plt.show()
        return combined

def plotnow_all(fpath,yrmoday,chan,var, xaxis,st_hour,st_minute,ed_hour,ed_minute,supply_index=False):
        flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod=select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld = []
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)
        pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        dd=get_all_demodulated_data(fld_demod, fld)
        combined=combine_cofe_h5_pointing(dd,pp)

        for c in range(16):
                ch='ch%s' %str(c)
                name = chantoname(ch)
                xa = combined[xaxis]
                data = combined['sci_data'][ch][var]
                print (ch, 'maxvalue: ', data.max())

        
                #sort data according to sorted azimuth
                data = [x for _,x in sorted(zip(xa,data))]
                xa = sorted(xa)
                
                plt.plot(xa,data,label=name)
        if xaxis == 'gpstime':
                plt.xlabel('gpstime')
        else:
                plt.xlabel('%s angle, degrees' % xaxis)
        plt.ylabel('Signal, V')
        plt.title('All COFE %s data binned to %s, date %s, %s:%d - %s:%d ' % (var, xaxis, yrmoday, st_hour, int(st_minute), ed_hour, int(ed_minute)))
        plt.legend(bbox_to_anchor=(1,1),loc=2,borderaxespad=0)
        plt.grid()
        plt.show()
        return combined

#round number to nearest resolution
def round_fraction(number, res):
        amount = int(number/res)*res
        remainder = number - amount
        return amount if remainder < res/2. else amount+res
        
def plotnow_azrevsig(fpath,yrmoday,chan,var,st_hour,st_minute,ed_hour,ed_minute,combined,supply_index=False):
        '''flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld=[]
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)
        pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        dd=get_all_demodulated_data(fld_demod, fld)
        combined=combine_cofe_h5_pointing(dd,pp)'''
        print('combined',combined)
        az1= combined['az']
        data1 = combined['sci_data'][chan][var]
        print("data1", data1)
        steps = len(data1)
        
        #convert to temp for cryo sensors
        if chan == 12:
                data1 = data1*10. + 273.15
        if chan == 13:
                data1 = convert.convert(data1, 'e')
        if chan == 14:
                data1 = convert.convert(data1, 'h')
        if chan == 15:
                data1 = data1*10. + 273.15
        
        #resolution
        dx = 1.0
        dy = 1.0
        
        #set up empty lists to append each revolution to
        data = []
        az = []
        iaz = [0]
        rev = 0
        
        #determine indices in azimuth/data array which correspond to a new revolution of the telescope
        for i in range(steps):
            #round values to resolution for comparison later
            az1[i] = round_fraction(az1[i], dx)
            if i > 0:
                if abs(az1[i] - az1[i-1]) >= 180.:
                    iaz.append(i)
                    rev += 1
        
        #append each revolution array to a list     
        for j in range(rev):
                az.append(az1[iaz[j]:iaz[j+1]])
                data.append(data1[iaz[j]:iaz[j+1]])
        
        #append the last revolution
        data.append(data1[iaz[-1]:])
        az.append(az1[iaz[-1]:])
        rev += 1

        data = np.asarray(data)
        az = np.asarray(az)
        
        #create grid for plotting
        x, y = np.arange(0., 360.+dx, dx), np.arange(0., rev - 1 + dy, dy)
        AZ, REV = np.meshgrid(x, y)
        
        #set up empty array
        z = np.zeros(len(x)*len(y))
        sig = np.reshape(z, (len(y), len(x)))
        
        #small number for comparing floats
        epsilon = 1e-6
        
        #fill signal array with data points
        for r in range(rev):
                for a in range(len(x)):
                        #find indices where combined azimuth data fits on x grid
                        idx = np.where(abs(az[r] - x[a]) < epsilon)[0]
                        #if idx length is 0 this will create a mask on that point, in idx len > 1, avg data points in the same bin
                        sig[r][a] = data[r][idx].mean()
        
        #mask invalid values, i.e. where there are no data points
        sig = ma.masked_invalid(sig)
                
        #change units on plot label
        if int(chan[2:]) < 12:
                unit = 'V'
        else:
                unit = 'K' 

        name = chantoname(chan)
        print("AZ",AZ)
        print("REV",REV)
        print('sig',sig)

        plt.pcolormesh(AZ, REV, sig)
        plt.colorbar(label = 'Signal, %s' % unit)
        plt.clim(data1.min(),data1.max())
        plt.axis([0., 360., 0., rev - 1])
        plt.ylabel('revolution #')
        plt.xlabel('azimuth (deg)')
        plt.title('%s %s data binned to azimuth and revolution #, date %s, %s:%d - %s:%d' % (name, var, yrmoday, st_hour, int(st_minute), ed_hour, int(ed_minute)))
        plt.grid()
        plt.show()

def plotnow_azrevsig2(fpath,yrmoday,chan,st_hour,st_minute,ed_hour,ed_minute,pp,supply_index=False):
        '''flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld = []
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)

        pp=get_h5_pointing(flp)'''
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        #dd=get_all_demodulated_data(fld_demod, fld)
        #combined=combine_cofe_h5_pointing(dd,pp)
        
        #synchronized data and az values
        az1 = pp['az']
        data1 = pp[chan]   
        steps = len(data1)
        
        #convert to temp for cryo sensors
        if chan == 12:
                data1 = data1*10. + 273.15
        if chan == 13:
                data1 = convert.convert(data1, 'e')
        if chan == 14:
                data1 = convert.convert(data1, 'h')
        if chan == 15:
                data1 = data1*10. + 273.15
        if chan == 'Phidget_Temp':
                data = data + 273.15

        
        #resolution
        dx = 1.0
        dy = 1.0
        
        #set up empty lists to append each revolution to
        data = []
        az = []
        iaz = [0]
        rev = 0
        
        #determine indices in azimuth/data array which correspond to a new revolution of the telescope
        for i in range(steps):
                #round values to resolution for comparison later
                az1[i] = round_fraction(az1[i], dx)
                if i > 0:
                        if abs(az1[i] - az1[i-1]) >= 180.:
                                iaz.append(i)
                                rev += 1
        
        #append each revolution array to a list     
        for j in range(rev):
                az.append(az1[iaz[j]:iaz[j+1]])
                data.append(data1[iaz[j]:iaz[j+1]])
        
        #append the last revolution
        data.append(data1[iaz[-1]:])
        az.append(az1[iaz[-1]:])
        rev += 1

        data = np.asarray(data)
        az = np.asarray(az)
        
        #create grid for plotting
        x, y = np.arange(0., 360.+dx, dx), np.arange(0., rev - 1 + dy, dy)
        AZ, REV = np.meshgrid(x, y)
        
        #set up empty array
        z = np.zeros(len(x)*len(y))
        sig = np.reshape(z, (len(y), len(x)))
        
        #small number for comparing floats
        epsilon = 1e-6
        
        #fill signal array with data points
        for r in range(rev):
                for a in range(len(x)):
                        #find indices where combined azimuth data fits on x grid
                        idx = np.where(abs(az[r] - x[a]) < epsilon)[0]
                        #if idx length is 0 this will create a mask on that point, in idx len > 1, avg data points in the same bin
                        sig[r][a] = data[r][idx].mean()
        
        #mask invalid values, i.e. where there are no data points
        sig = ma.masked_invalid(sig)
                
        #change units on plot label
        if chan != 'Phidget_Temp':
                unit = 'deg'

        else:
                unit = 'K' 
        
        name = chan 

        plt.pcolormesh(AZ, REV, sig)
        plt.colorbar(label = 'Signal, %s' % unit)
        plt.clim(data1.min(),data1.max())
        plt.axis([0., 360., 0., rev - 1])
        plt.ylabel('revolution #')
        plt.xlabel('azimuth (deg)')
        plt.title('%s data binned to azimuth and revolution #, date %s, %s:%d - %s:%d' % (name, yrmoday, st_hour, int(st_minute), ed_hour, int(ed_minute)))
        plt.grid()
        plt.show()

def plotnow_azelsig(fpath,yrmoday,chan,var,st_hour,st_minute,ed_hour,ed_minute,combined,supply_index=False):
        '''flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld = []
        #print('flp',flp)
        #print('fld_demod', fld_demod)
        #print('fld',fld)
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)

        pp=get_h5_pointing(flp)'''
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        #dd=get_all_demodulated_data(fld_demod, fld) 
        #print('dd', dd)    
        #combined=combine_cofe_h5_pointing(dd,pp) #definitely needed to combine pointing and demod data--no reference to raw data?
        
        #synchronized data az and el values
        az1, el1 = combined['az'], combined['el']
        data = combined['sci_data'][chan][var]
           
        
        #convert to temp for cryo sensors
        if chan == 12:
                data = data*10. + 273.15
        if chan == 13:
                data = convert.convert(data, 'e')
        if chan == 14:
                data = convert.convert(data, 'h')
        if chan == 15:
                data = data*10. + 273.15
        steps = len(data)
        
        #set az/el resolution
        dx = 1.0
        dy = 1.0
        
        #set up bins/grid
        x, y = np.arange(0., 360.+dx, dx), np.arange(0., 90. + dy, dy)
        AZ, EL = np.meshgrid(x, y)
        
        #small number for comparing floats
        epsilon = 1e-6
        
        #set up matrix for signal 
        z1 = np.zeros(len(x)*len(y))
        sig = np.reshape(z1, (len(y), len(x)))
        
        #set up matrix for keeping track of data points in single bin for averaging
        z2 = np.zeros(len(x)*len(y))
        count = np.reshape(z2, (len(y), len(x)))

        for i in range(steps):
         
                #round az/el points for comparison with grid        
                el1[i] = round_fraction(el1[i], dy)
                az1[i] = round_fraction(az1[i], dx)  
        
                #find where data points belong in grid
                iel = np.where(abs(y - el1[i]) < epsilon)[0][0]
                iaz = np.where(abs(x - az1[i]) < epsilon)[0][0]
        
                #add 1 each time data point lands in same bin
                count[iel][iaz] += 1
        
                #add total number of data values in bin
                sig[iel][iaz] = sig[iel][iaz] + data[i]  

        #mask 0 count values so they dont show up in color plot
        count = ma.masked_where(count == 0.0, count)
        
        #take average of all data points in single bin
        sig = sig/count
        
        #change units on plot label
        if int(chan[2:]) < 12:
                unit = 'V'

        else:
                unit = 'K' 
        
        name = chantoname(chan)

        plt.pcolormesh(AZ, EL, sig)
        plt.colorbar(label = 'Signal, %s' % unit)
        plt.clim(data.min(),data.max())
        plt.axis([AZ.min(), AZ.max(), EL.min(), EL.max()])
        #plt.axis([0., 360., 0., 90.])
        plt.ylabel('elevation (deg)')
        plt.xlabel('azimuth (deg)')
        plt.title('%s %s data binned to azimuth and elevation, date %s, %s:%d - %s:%d' % (name, var, yrmoday, st_hour, int(st_minute), ed_hour, int(ed_minute)))
        plt.grid()
        plt.show()

def plotnow_azelsig2(fpath,yrmoday,chan,st_hour,st_minute,ed_hour,ed_minute,pp,supply_index=False): #added to try to fix ploting 
        '''flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld = []
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)'''

        
        #pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        #dd=get_all_demodulated_data(fld_demod, fld) 
        #print('dd', dd)    
        #combined=combine_cofe_h5_pointing(dd,pp) #definitely needed--see paper notes (NL)
        
        #synchronized data az and el values
        #az1, el1 = combined['az'], combined['el']
        #data = combined['sci_data'][chan][var]            
        #pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        #dd=get_all_demodulated_data(fld_demod, fld)     
        #combined=combine_cofe_h5_pointing(dd,pp)
        
        #synchronized data az and el values
        az1, el1 = get_h5_pointing(p_p.select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute))['az'], get_h5_pointing(p_p.select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute))['el']
        
        data = get_h5_pointing(p_p.select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute))[chan]   
        
        #convert to temp for cryo sensors
        if chan == 12:
                data = data*10. + 273.15
        if chan == 13:
                data = convert.convert(data, 'e')
        if chan == 14:
                data = convert.convert(data, 'h')
        if chan == 15:
                data = data*10. + 273.15
        if chan == 'Phidget_Temp':
                data = data*10. + 273.15

        steps = len(data)
        
        #set az/el resolution
        dx = 1.0
        dy = 1.0
        
        #set up bins/grid
        x, y = np.arange(0., 360.+dx, dx), np.arange(0., 90. + dy, dy)
        AZ, EL = np.meshgrid(x, y)
        
        #small number for comparing floats
        epsilon = 1e-6
        
        #set up matrix for signal 
        z1 = np.zeros(len(x)*len(y))
        sig = np.reshape(z1, (len(y), len(x)))
        
        #set up matrix for keeping track of data points in single bin for averaging
        z2 = np.zeros(len(x)*len(y))
        count = np.reshape(z2, (len(y), len(x)))

        for i in range(steps):
         
                #round az/el points for comparison with grid        
                el1[i] = round_fraction(el1[i], dy)
                az1[i] = round_fraction(az1[i], dx)  
        
                #find where data points belong in grid
                iel = np.where(abs(y - el1[i]) < epsilon)[0][0]
                iaz = np.where(abs(x - az1[i]) < epsilon)[0][0]
        
                #add 1 each time data point lands in same bin
                count[iel][iaz] += 1
        
                #add total number of data values in bin
                sig[iel][iaz] = sig[iel][iaz] + data[i]  

        #mask 0 count values so they dont show up in color plot
        count = ma.masked_where(count == 0.0, count)
        
        #take average of all data points in single bin
        sig = sig/count
        
        #change units on plot label
        if chan != 'Phidget_Temp':
                unit = 'deg'

        else:
                unit = 'K' 
        
        name = chan

        plt.pcolormesh(AZ, EL, sig)
        plt.colorbar(label = 'Signal, %s' % unit)
        plt.clim(data.min(),data.max())
        plt.axis([AZ.min(), AZ.max(), EL.min(), EL.max()])
        #plt.axis([0., 360., 0., 90.])
        plt.ylabel('elevation %s' % (unit))
        plt.xlabel('azimuth (deg)')
        plt.title('%s data binned to azimuth and elevation, date %s, %s:%d - %s:%d' % (name, yrmoday, st_hour, int(st_minute), ed_hour, int(ed_minute)))
        plt.grid()
        plt.show()

def plotnow_psd(fpath,yrmoday,chan,var,st_hour,st_minute,ed_hour,ed_minute,supply_index=False):
        """
        function to automatically read last 2 science files and last few pointing
        files, combine and plot signal vs azimuth. yrmoday should be a string
        '20130502' fpath should point to the 
        spot where acq_tel and converter.py were run
        """
        fs=30
        flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod, fld =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)

        pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        dd=get_all_demodulated_data(fld_demod, fld)
        combined=combine_cofe_h5_pointing(dd,pp)
        
        name = chantoname(chan)

        freqs,pxx=nps(combined['sci_data'][chan][var],Fs=fs)
        plt.plot(freqs,np.sqrt(pxx),label=name)
        plt.legend(bbox_to_anchor=(1,1),loc=2,borderaxespad=0)
        plt.ylabel('V/$\sqrt{Hz}$')
        plt.xlabel('Hz')
        plt.yscale('log')
        #plt.xscale('log')
        plt.show()
        return freqs,pxx

def plotnow_psd_all(fpath,yrmoday,chan,var,st_hour,st_minute,ed_hour,ed_minute,supply_index=False):
        flp=select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        fld_demod, fld =select_h5_sig(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute)
        i=0
        while len(flp)<3:
                i+=1
                flp=select_h5(fpath,yrmoday,st_hour,int(st_minute)-i,ed_hour,int(ed_minute)+i)

        pp=get_h5_pointing(flp)
        #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
        dd=get_all_demodulated_data(fld_demod, fld)
        combined=combine_cofe_h5_pointing(dd,pp)
        fs=30
        for c in range(16):
                ch='ch%s' %str(c)
                name = chantoname(ch)
                #plt.psd(combined['sci_data'][ch][var])
                freqs,pxx=nps(combined['sci_data'][ch][var],Fs=fs)
                plt.plot(freqs,np.sqrt(pxx),label=name)
        plt.ylabel('V/$\sqrt{Hz}$')
        plt.xlabel('Hz')
        plt.yscale('log')
        plt.xscale('log')
        plt.legend(bbox_to_anchor=(1,1),loc=2,borderaxespad=0)
        plt.show()
        return freqs,pxx
                
def plotrawnow(yrmoday,chan,var,fpath,rstep=50,supply_index=False):
        """
        function to automatically read last science file plot raw data vs encoder
        yrmoday should be a string '20130502' fpath should point to the 
        directory where acq_tel and converter.py were run
        rstep determines how many revolutions to skip between plotted revolutions
        """
        fld=glob.glob(fpath+'data/'+yrmoday+'/*.dat')
        fld.sort()
        stats=os.stat(fld[-1])
        if stats.st_size == 10752000:
                dr=demod.read_raw([fld[-1]],supply_index=supply_index)
                for i in range(0,np.shape(dr[chan])[0],rstep):
                        plt.plot(dr[chan][i,:],label='rev '+str(i))
                plt.xlabel('encoder position')
                plt.ylabel('Signal V')
                plt.title(chan+' Raw data, every '+str(rstep) + ' revs, file: '+fld[-1])
                plt.legend()
                plt.grid()
                plt.show()
        return dr
        
def psmapcurrent(cdata,chan='ch2',cmode='T',nbins=360):
        """
        function to combine already read science files and pointing
        files, and create pseudomap. chan is 'ch2', cmode is 'T'
        """
        combined = combine_cofe_h5_pointing(cdata['dd'],cdata['pp'])
        psmap=cu.phasebin(nbins,combined['az'],combined['sci_data'][chan][cmode])
        pcolormesh(psmap.T)
        return psmap
        
def getdatanow(yrmoday,fpath='',combined=True,phase_offset=0):
        """
        function to automatically read all science files and pointing
        files, save for future use, also save last h5 and .dat filenamesc
        yrmoday should be a string
        '20130502' fpath should point to the  spot where acq_tel and converter.py were run
        chan is 'ch2', cmode is 'T'
        """
        fld=glob(fpath+'data/'+yrmoday+'/*.dat')
        fld.sort()
        flp=glob(fpath+yrmoday[4:6]+'-'+yrmoday[6:8]+'-'+yrmoday[0:4]+'/*.h5')
        flp.sort()
        pp=get_h5_pointing(flp)
        dd=get_demodulated_data_from_list(fld,phase_offset=phase_offset)
        curr_data={'pp':pp,'dd':dd,'lastpfile':flp[-1],'lastdfile':fld[-1],'yrmoday':yrmoday,'fpath':fpath}
        if combined:
                curr_data=combine_cofe_h5_pointing(curr_data['dd'],curr_data['pp'],outfile='combined_data'+yrmoday+'.pkl')
        return curr_data
        
def combine_cdata(curr_data):
        """
        convenience function to use curr_data info to get combined data
        """
        combined=combine_cofe_h5_pointing(curr_data['dd'],curr_data['pp'],outfile='combined_data'+curr_data['yrmoday']+'.pkl')
        return combined

def updatedata(cdata):
        """
        function to automatically read all science files and pointing
        files, save for future use, also save last h5 and .dat filenamesc
        yrmoday should be a string
        '20130502' fpath should point to the  spot where acq_tel and converter.py were run
        chan is 'ch2', cmode is 'T'
        """
        fld=glob(cdata['fpath']+'data/'+cdata['yrmoday']+'/*.dat')
        fld.sort()
        flda=np.array(fld)
        flp=glob(cdata['fpath']+cdata['yrmoday'][4:6]+'-'+cdata['yrmoday'][6:8]+'-'+cdata['yrmoday'][0:4]+'/*.h5')
        flp.sort()
        flpa=np.array(flp)
        if fld[-1]>cdata['lastdfile']:
                dd=get_demodulated_data_from_list(flda[flda>cdata['lastdfile']])
                cdata['dd']=np.concatenate([cdata['dd'],dd])
                cdata['lastdfile']=fld[-1]
        if flp[-1]>cdata['lastpfile']:
                pp=get_h5_pointing(flpa[flpa>cdata['lastpfile']])
                cdata['pp']['az']=np.concatenate([cdata['pp']['az'],pp['az']])
                cdata['pp']['el']=np.concatenate([cdata['pp']['el'],pp['el']])
                cdata['pp']['rev']=np.concatenate([cdata['pp']['rev'],pp['rev']])
                cdata['lastpfile']=flp[-1]
        return cdata

def pointing_plot(var,vector,gpstime,fig,ax1,ax2,ax3):
        
        #plt.plot(gpstime,vector,label=str(var) )
        plt.xlabel('gpstime')
        if var == 'az' or var == 'el' or var == 'x_tilt' or var == 'y_tilt':
           unit = 'deg'
           ax3.plot(gpstime,vector,label=str(var))

        elif var == 'H1' or var== 'H2' or var == 'H3':
           unit = 'V'
           ax1.plot(gpstime,vector,label=str(var))
        elif var == 'gpstime':
                unit = ''
        else:
           unit = 'K'
           ax2.plot(gpstime,vector,label=str(var))
        #plt.legend()
        plt.grid()
        

def pointing_plotaz(var,vector,gpstime, fig,ax1,ax2,ax3):
        #plt.plot(gpstime,vector,label=str(var))
        plt.xlabel('azimuth')
        if var == 'el' or var == 'az' or var == 'x_tilt' or var == 'y_tilt':
           unit = 'deg'
           ax3.plot(gpstime,vector,label=str(var))
        elif var == 'H1' or var== 'H2' or var == 'H3':
           unit = 'V'
           ax1.plot(gpstime,vector,label=str(var))
        elif var == 'gpstime':
                unit = ''
        else:
           unit = 'K'
           ax2.plot(gpstime,vector,label=str(var))

        #plt.ylabel(str(var) + ' (%s)' % unit)
        #plt.title(str(var)+' ' + 'vs. azimuth')
        #plt.legend()
        plt.grid()
        #plt.show()

def linearize_Vexp(Vexp,horn,params='2'):

        fpath='D:/software_git_repos/greenpol/telescope_control/configurations/calibrations/'
        os.chdir(fpath)
        
        #read all the saved entries
        if not isinstance(params,basestring):
                params = str(params)

        with open('fit_params%s' % params +'.txt', 'r') as handle:
                pars=pickle.loads(handle.read())
           
        m  = pars['linpars%d' % horn][1]
        B  = pars['linpars%d' % horn][0]
        P0 = pars['expars%d' % horn][0]
        P1 = pars['expars%d' % horn][1]
        P2 = pars['expars%d' % horn][2]
        P3 = pars['expars%d' % horn][3]    
    
        Vlin = (-P0*P3 -B*P1*P3 - P1*lambertw(np.exp(P3*(Vexp - P0)/P1)*P2*P3/P1)
        + P3*Vexp)/m/P1/P3
    
        return Vlin.real


def convert_gpstime(starttime, gpstime, ltoffset=0, bits_to_ms=2 ** 24, format='seconds', ttype='utc'):
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
                t = []
                for i in range(len(dtime)):
                        t.append(datetime.datetime.fromtimestamp(dtime[i]))

                return t, dtime

        else:
                return dtime

if __name__=="__main__":
        yrmoday='20171208'
        hour1 = '11'
        minute1 = '33'
        hour2 = '11'
        minute2 = '41'
        fpath='D:/software_git_repos/greenpol/telescope_control/data_aquisition/'
        chan='ch1'
        var='H1'
        #plotnow_psd(fpath,yrmoday,chan,var,hour1,minute1,hour2,minute2)
        #get_h5_pointing(select_h5(fpath,yrmoday,18,15,24,22))
        #plotnow_aztimesig(fpath,yrmoday,chan,var,18,15,23,59)
        #plotrawnow(yrmoday,chan,var,fpath,rstep=50,supply_index=False)
        #plotnow(fpath,yrmoday,chan,var,18,15,23,59)
        #y=get_h5_pointing(select_h5(fpath,yrmoday,hour1,minute1,
        #                                        hour2,minute2))[var]
        print (linearize_Vexp(np.array([-0.7, -0.25, -1.8]), 1)         )                       
        #t=get_h5_pointing(select_h5(fpath,yrmoday,hour1,minute1,
        #                                        hour2,minute2))['gpstime']

        #pointing_plot(var,y,t)
