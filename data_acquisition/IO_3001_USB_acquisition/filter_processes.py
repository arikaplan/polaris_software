from scipy.signal import butter,filtfilt
import numpy as np
import math
import matplotlib.mlab

def lowpass(d,hz=10,cutoff=.25):
    '''
    Allows low frequency signal through while removing high frequency noise.
    hz - filtering rate
    cutoff - value in hz, frequencies above this are filtered out.
    
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html#scipy.signal.filtfilt
    just stuff in an example from scipy to get this functional
    '''
    frac_cutoff=cutoff/(hz/2.)
    b,a=butter(3,frac_cutoff)
    #b,a=iirdesign(frac_cutoff-.001,frac_cutoff+.1,.9,.1)
    filtered_d = filtfilt(b,a,d)
    return(filtered_d)

def lowpassMult(d, hz, cutoff=.25, channels = 4, exclude = [3]):
    """Lowpass multiple channels.
    d - a 2D array of channels channels all the same length, such as one taken by get_iotech_data
    hz - defaults to 10 hz, the sample rate of the data.
    cutoff - in hz, the point below which all frequencies are damped out
    channels - number of channels in the first dimension of the 2d array. Default is 4 channels.
    exclude - for some cases, you may not want to lowpass all data. By default this excludes 3, voltage/current"""
    arr = []
    for i in range(channels):
        if i in exclude:
            arr += [d[i]]
        else:
            arr += [lowpass(d[i], hz, cutoff)]
    return np.array(arr)

def zeroDetector(d, startSample=100, endSample=500):
    """Shifts the data so that the average of points in range [startSample, endSample] is zero.
    Equivalent to zeroing a scale or such.
    startSample and endSample should be during a period of no laser ablation when the system is at rest.
    d - the data to be zeroed. 1D aray only
    startSample - defaults to 100 (10 secs), the sample number to begin taking the average for the zero
    endSample - defaults to 500 (50 secs), average stops here."""
    return d - np.average(d[100:500])
    
def zeroDetectorMult(d, channels = 4, exclude = [3]):
    """Applies zeroDetector to multiple channels of an array."""
    arr = []
    for i in range(channels):
        if i in exclude:
            arr += [d[i]]
        else:
            arr += [zeroDetector(d[i])]
    return np.array(arr)
    
def calibrationFactor(d, factor):
    """Multiply an entire array by a constant. Used to calibrate with experimentally determined results."""
    return d * factor
    

    

def calibrationFactorMult(d, factor, channels = 5, exclude = [3,4]):
    """Multiply a multiple channeled array by a constant."""
    arr = []
    for i in range(channels):
        if i in exclude:
            arr += [d[i]]
        else:
            arr += [calibrationFactor(d[i], factor)]
    return np.array(arr)
    
def rms(d, windowsize=100):
    """Take a sliding RMS plot (Root mean square) of a channel. Use to measure amplitude of a function."""
    rmsdata = []
    for i in range(len(d)):
        rmspoint = 0
        for j in range(min(windowsize, len(d)-i)):
            rmspoint += d[i+j]**2
        rmspoint /= min(windowsize, len(d)-i) # if we bleed off the screen just use less data
        rmspoint = rmspoint**.5
        rmsdata += [rmspoint]
    
    return np.array(rmsdata)
    
def rmsMult(d, windowsize=100, channels = 4, exclude = [3]):
    """Take a sliding RMS measure of various channels of an array"""
    arr = []
    for i in range(channels):
        if i in exclude:
            arr += [d[i]]
        else:
            arr += [rms(d[i], windowsize)]
    arr = np.array(arr)
    return arr
    
def std(d, windowsize=100):
    """Take a sliding standard deviation measure of the array"""
    stddata = []
    for i in range(len(d)):
        subset = np.array(d[i:min(len(d), i+windowsize)])
        stddata += [np.std(subset)]
    
    return np.array(stddata)
    
def stdMult(d, windowsize=100, channels = 4, exclude = [3]):
    """Take a sliding standard deviation measure of the various channels of array"""
    arr = []
    for i in range(channels):
        if i in exclude:
            arr += [d[i]]
        else:
            arr += [std(d[i], windowsize)]
    arr = np.array(arr)
    return arr
   
def convertToForceTorsionBalanceAblation(dat, distMirror = .3175, torsionConst= 0.121330411, spotDist = 0.09):
    """
    Converts X-axis displacement to force. Do not use with Y-axis.
      dat - distance on detector x axis in microns, normalized to zero. (microns)
      distMirror - distance from detector to mirror in y axis (m)
      torsionConst - Determined torsion constant of torsion fiber. (N*m/rad)
      spotDist - distance from laser spot to center. (m)
    """
    return 1000*(dat/2)/distMirror * torsionConst/(spotDist)

def convertToForceTorsionBalanceAblation(dat, mass = 0.203,endmass=0.161,detectordistance=0.3175):
    """
    Converts y-axis displacement to force. Do not use with Y-axis.
      dat - distance on detector x axis in microns, normalized to zero. (microns)
      distMirror - distance from detector to mirror in y axis (m)
      torsionConst - Determined torsion constant of torsion fiber. (N*m/rad)
      spotDist - distance from laser spot to center. (m)
    """
    return 1000000*(mass+2*endmass)*9.8*(dat*0.000001/2)/detectordistance





def convertToTorqueTorsionConstantCalibration(dat, ydist = .112, xdist = .06985, torsionconst = .4877):
    """Do not use for laser data"""
    dat *= 1000
    y=ydist
    x=xdist
    k=torsionconst
    f = k * (np.arctan2(x,y) - np.arctan2(-dat+x, y))/2
    return f
    
    
#Do not use for laser data
def convertToForceTorsionConstantCalibration(dat, ydist = .112, xdist = .06985, torsionconst = .4877, torsionDist = .18,): 
    """Do not use for laser data"""   
    dat *= 1000 # Dat is given in mm and we want this in microns.
    d=torsionDist
    y=ydist
    x=xdist
    k=torsionconst
    f = k/(d) * (np.arctan2(x,y) - np.arctan2(-dat+x, y))/2
    return f
    
def intDown(inarray):
    '''
    Copy-pasted pretty much exactly from Travis' notebook.
    function to test if data set integrates down with increasing number of samples
    input is 1 dim array, output is a dictionary
    '''
    ncuts=np.int(np.fix(np.log2(len(inarray))))
    #first take max power of 2 subset of input array
    d=inarray[:2**ncuts]
    outstds=[]
    outnpts=[]
    out={}
    for i in range(ncuts):
        d=np.reshape(d,(2**i,2**(ncuts-i)))
        outstds.append(np.std(np.mean(d,axis=1)))
        outnpts.append(2**(ncuts-i))
    out['stdev']=np.array(outstds)
    out['npoints']=np.array(outnpts)
    return out
    
def derivative(dat, dt):
    '''takes the numerical derivative of a '''
    dat = np.diff(dat)
    dat = np.append(dat, dat[-1])
    dat /= dt
    return dat

def interp(d1,d2,alpha):
    return d1*alpha + d2*(1-alpha)
    
def findRotationSpeed(dat,dt):
    xmovement = dat[0]
    sweepbegin = []
    sweepend = []
    below = True
    for i in range(len(xmovement)):
        if(i%6000 == 0 and i+6000 < len(xmovement)):
            xlmax = np.max(xmovement[i:i+6000])
            xlavg = np.average(xmovement[i:i+6000])
            bar = (xlmax +xlavg)/2.0
            print i, xlmax,xlavg,bar
        if xmovement[i] > bar and below:
            sweepbegin += [i]
            below = False
        elif not below and xmovement[i] < bar:
            below = True
            sweepend += [i]
    
    sweepbegin= np.array(sweepbegin)
    sweepend  = np.array(sweepend)
    peakspeeds = [1.0/((sweepbegin[1]-sweepbegin[0])*dt)]
    for peak in range(len(sweepbegin)-1):
        peakspeeds += [1.0/((sweepbegin[peak+1]-sweepbegin[peak])*dt)]
    peakspeeds = np.array(peakspeeds)
    data = []
    speed =  peakspeeds[0]
    count = 0
    for i in range(len(xmovement)):
        
        if(count+1 < len(sweepbegin) and i > sweepbegin[count]):
            count += 1
        if count < len(sweepbegin):
            alpha = (i-sweepbegin[count-1])*1.0/(sweepbegin[count]-sweepbegin[count-1])
            data += [interp(peakspeeds[count],peakspeeds[count-1],alpha)]
        else:
            alpha = 1
            data += [peakspeeds[-1]]
    return np.array(data)