# -*- coding: utf-8 -*-

import plots2
import filter_processes
import numpy as np
import matplotlib.pyplot as plt
import util
from storage_retrieval import handleFilenameConflicts
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

def plotLPData(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showpressure = True):
    d = filter_processes.zeroDetectorMult(d, 5, [3,4])
    d = filter_processes.lowpassMult(d, 1.0/timestep, cutoff, 5, [3,4]) #Lowpass filter
    plots2.plotData(d, timestep, savename, title, outputfile,showpressure)
    
def plotLPDataYZoom(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showPressure = True):
    dcopy = d
    d1 = d[2]
    d2 = d[3]
    d = [d1,d2] #Create a new data using only channels 0 and
    d1 = filter_processes.zeroDetector(d1)
    d1 = filter_processes.lowpass(d1, 1.0/timestep, cutoff)
    if showPressure:
        plots2.plotSingle(d1,d2,"Y-axis", timestep, savename, title, outputfile, dcopy[4])
    else:
        plots2.plotSingle(d1,d2,"Y-axis", timestep, savename, title, outputfile)
 
def plotLPDataXZoom(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showPressure = True):
    dcopy = d
    d1 = d[0]
    d2 = d[3]
    d = [d1,d2] #Create a new data using only channels 0 and 3.
    d1 = filter_processes.zeroDetector(d1)
    d1 = filter_processes.lowpass(d1, 1.0/timestep, cutoff)
    if showPressure:
        plots2.plotSingle(d1,d2,"X-axis", timestep, savename, title, outputfile, dcopy[4])
    else:
        plots2.plotSingle(d1,d2,"X-axis", timestep, savename, title, outputfile)

def plotPressureZoom(d,timestep, savename, cutoff=.1, title = None, outputfile = True):
    d1 = d[4]
    d2 = d[3]
    plots2.plotSingle(d1,d2,"Pressure", timestep, savename, title, outputfile,None, "Pressure (mTorr)")

def plotVoltageZoom(d,timestep, savename, cutoff=.1, title = None, outputfile = True):
    d1 = d[3]
    plots2.plotSingle(d1,d1,"Current", timestep, savename, title, outputfile,None, "Current (amps)")

   
def plotRawData(d,timestep,savename, calibration=.507, title = None, outputfile = True, showpressure = True): # No filters except calibration    
    '''This is the most basic of the plotting functions. It takes data and puts it up on the screen.
    When I say 'Arguments standard' on another function it means it is the same as the arguments here.
    d - 4 or 5 channel np array with channel setup:
        0 - x-axis
        1 - light intensity
        2 - y-axis
        3 - voltage shunt
        4 - pressure (optional)
    timestep - default is 0.1. The time between each sample on the daq board. 
    savename - Name to be saved as. The default is something like .\\Laser Ablation Lab Data and Plots\\Plots_Raw\\[insertnamehere].png
    calibration - Static multiplier to multiply data to correct for DAQ output
    title - Title of plot. If none, defaults to savename.
    outputfile - boolean of whether to save the file or not
    showpressure - if true, use channel [4] to plot pressure. If data has no channel 4 set to false
    '''
    plots2.plotData(d, timestep, savename, title, outputfile, showpressure)

def plotRawXData(d, timestep, savename, calibration = .507, title = None, outputfile = True, showPressure = True):
    '''
    Sometimes you need to look at the raw data but don't want y and light intensity clogging our view.
    For this application, use plotRawXData.
    Arguments standard.
    '''    
    dcopy = d
    d1 = d[0]
    d2 = d[3]
    if showPressure:
        plots2.plotSingle(d1,d2,"X-axis", timestep, savename, title, outputfile, dcopy[4])
    else:
        plots2.plotSingle(d1,d2,"X-axis", timestep, savename, title, outputfile)

    
def plotRMSData(d, timestep, savename, calibration=.507, cutoff=.1, windowsize = 1000, title = None, outputfile = True,showpressure = True):
    '''Plots a the moving RMS of the data. 
    RMS is typically used when you want to measure the 
    magnitude of the noise in the data.
    Arguments standard
    '''
    d = filter_processes.zeroDetectorMult(d, 5, [3,4])
    dLP = filter_processes.lowpassMult(d, 1.0/timestep, cutoff, 5, [3,4])
    noise = d-dLP
    d = filter_processes.rmsMult(noise, windowsize, 5, [3,4])
    plots2.plotData(d, timestep, savename, title, outputfile,showpressure)

def plotSTDData(d, timestep, savename, calibration=.507, windowsize = 1000, title = None, outputfile = True,showpressure = True):
    '''
    Plots the standard deviation of a moving envelope of the data.
    Arguments standard, but work best for noise data   
    '''
    d = filter_processes.zeroDetectorMult(d, 5, [3,4])
    d = filter_processes.stdMult(d, windowsize, 5, [3,5])
    plots2.plotData(d, timestep, savename, title, outputfile,showpressure)
    
def plotLPZoomDataForceXAxis(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showpressure = True):
    '''
    Plots the zoom of the x axis, converted into force. 
    This is highly dependant on filter_processes.convertToForceTorsionbalanceAblation working right.
    If anything changes it could easily stop working.
    '''
    d1 = d[0]
    d2 = d[3]
    d3 = d[4]
    d1 = filter_processes.zeroDetector(d1)
    d1 = filter_processes.lowpass(d1, 1.0/timestep, cutoff)
    d1 = filter_processes.convertToForceTorsionBalanceAblation(d1)
    if showpressure:
        plots2.plotSingle(d1,d2,"X-axis Force", timestep, savename, title, outputfile, d3, "Force (uN)")
    else:
        plots2.plotSingle(d1,d2,"X-axis Force", timestep, savename, title, outputfile, "Force (uN)")

def plotDampingLinearization(d, timestep, savename, calibration = .507,  title = None, outputfile = True, showPressure = True):
    dcopy = d
    d1 = d[0]
    #d1 -= np.max(d1)
    d1 *= .113 #convert to force.
    d1 = np.log(d1/209.8)
    d2 = d[3]
    if showPressure:
        plots2.plotSingle(d1,d2,"X-axis", timestep, savename, title, outputfile, dcopy[4])
    else:
        plots2.plotSingle(d1,d2,"X-axis", timestep, savename, title, outputfile)

    
def plotXNoiseData(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showpressure = True):
    '''
    Plots the xRaw - xLowpass. Useful for looking at the size of the noise in the data.
    Args: All standard.
    '''
    d1 = d[0]
    d2 = d[3]
    d1 = filter_processes.zeroDetector(d1)
    dLP = filter_processes.lowpass(d1, 1.0/timestep, cutoff)#Todo: average of first 10-50 seconds
    noise = d1-dLP
    if showpressure:
        plots2.plotSingle(noise,d2,"X-axis Noise", timestep, savename, title, outputfile, d[4])
    else:
        plots2.plotSingle(noise,d2,"X-axis Noise", timestep, savename, title, outputfile)

def plotYNoiseData(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showpressure = True):
    '''
    See plotXNoiseData(). Plots the y raw - y lowpass.
    Args: All standard
    '''    
    d1 = d[2]
    d2 = d[3]
    d1 = filter_processes.zeroDetector(d1)
    dLP = filter_processes.lowpass(d1, 1.0/timestep, cutoff)#Todo: average of first 10-50 seconds
    noise = d1-dLP
    if showpressure:
        plots2.plotSingle(noise,d2,"X-axis Noise", timestep, savename, title, outputfile, d[4])
    else:
        plots2.plotSingle(noise,d2,"X-axis Noise", timestep, savename, title, outputfile)

                          
def plotResonanceData(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True):
    '''
    Plots a graph of the PSD (Power Spectrum Density) of the data.
    Used to determine where the resonance of the noise is.
    Typically used to set the lowpass cutoff after changing the setup
    Args: All standard, but d must be of noise data.'''
    d1 = d[0]
    d2 = d[3]
    d1 = filter_processes.zeroDetector(d1)
    dLP = filter_processes.lowpass(d1, 1.0/timestep, cutoff) 
    noise = d1-dLP
    freqs, pxx = util.nps(noise, 1/timestep)
    plots2.plotDataXandY(freqs, pxx, savename, "x-axis noise (mm)", "Frequency (hz)", "Amplitude (um/hz^.5)", title, outputfile, True)#TODO Confirm that
    
def plotPowerSpectrum(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True):
    '''
    Plots a graph of the PSD (Power Spectrum Density) of the data.
    Used to determine where the resonance of the noise is.
    Typically used to set the lowpass cutoff after changing the setup
    Args: All standard, but d must be of noise data.'''
    d1 = d[0]
    d2 = d[3]
    freqs, pxx = util.nps(d1, 1/timestep)
    plots2.plotDataXandY(freqs, pxx, savename, "x-axis noise (mm)", "Frequency (hz)", "Amplitude (um/hz^.5)", title, outputfile, True)#TODO Confirm that
    
    
def plotIntDown(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True):
    """
    Plots the integration down of the x axis of a given data
    Integration down plots are similar to an allan variance plot.
    Basically, you expect that as you take the standard deviation of 
    the average of points you would get a lower deviation than all of those
    points seperately. int down tests that.
    Ask Phil Lubin if you need more info.
    Arguments: All standard, must be a noise plot (no laser on target)
    """    
    dset = filter_processes.intDown(d[0]) # take x axis
    x = dset['npoints']
    y1 = dset['stdev']*25/48
    y2 = 1/np.sqrt(x)
    y2adj = y2*y1[-1]/y2[-1]
    
    plt.figure(figsize=[10,5])
    subplot = host_subplot(111, axes_class=AA.Axes)
    box = subplot.get_position()
    subplot.set_position([box.x0, box.y0, box.width * 0.65, box.height])
    plt.cla()
    pList = plt.plot(x,y1,'-o',label = 'stdev')
    print pList
    pList += plt.plot(x,y2adj,label = '1/sqrt(npoints)')
    plt.xlabel('npoints')
    plt.ylabel('stdev (mm)')
    plt.title(title)
    plt.xscale('log')
    plt.yscale('log')
    first_legend = plt.legend(handles=pList, loc=2,bbox_to_anchor=(1.3, 1.05),prop={'size':10})
    plt.gca().add_artist(first_legend)
    plt.title(title)
    if(outputfile):
        savename = handleFilenameConflicts(savename) #Ensures we don't overwrite a file
        try:
            plt.savefig(savename)
        except:
            print 'Could not save', savename, 'to local disk.'
        try:
            plt.savefig(getServerName(savename))
        except:
            print 'Could not save', savename, 'to server.'
    plt.show()

def plotDerivativeData(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True, showpressure = True):
    """
    Plots the numerical derivative of the x,y, and light intensity. Volts/amps and pressure constant.
    For details on implementation see filterprocesses.derivative()
    Arguments: All standard
    """
    d = [filter_processes.derivative(d[0],timestep), filter_processes.derivative(d[1],timestep), filter_processes.derivative(d[2],timestep), d[3], d[4]]

    plots2.plotData(d, timestep, savename, title, outputfile,showpressure)

def plotSpeedData(d, timestep, savename, calibration = .507, title = None, outputfile = True, showpressure = True):
    """
    Designed for Aiden Gilkes' RMP project 2015.
    This plot only works on data that has a freely rotating asteroid with mirrors mounted to it. When the mirrors rotate
    the laser sweeps across the centroid detector. This counts the time between those sweeps and produces a graph
    rotational speed.
    Typically there is a fair bit of noise in this - spikes easily hundreds of the base value. You'll
    have to use interactive plots to get real data.
    Arguments: All standard, but d must be of a rotational test run
    """
    d1 = filter_processes.findRotationSpeed(d,timestep)
    print len(d1), len(d[3])
    if showpressure:
        plots2.plotSingle(d1,d[3],"Rotational Speed", timestep, savename, title, outputfile, d[4], "Revolutions per second")
    else:
        plots2.plotSingle(d1,d[3],"Rotational Speed", timestep, savename, title, outputfile, None, "Revolutions per second")

def plotAccelerationData(d, timestep, savename, calibration = .507, title = None, outputfile = True, showpressure = True):
    '''
    Designed for Aiden Gilkes' RMP project 2015
    This plot only works on data that has a freely rotating asteroid with mirrors mounted to it. When the mirrors rotate
    the laser sweeps across the centroid detector. This counts the time between those sweeps and produces a graph
    rotational speed.
    This plot takes the derivative of the rotational speed, IE acceleration.
    Typically there is a fair bit of noise in this - spikes easily hundreds of the base value. You'll
    have to use interactive plots to get real data.
    Arguments: All standard, but d must be of a rotational test run
    '''
    d1 = filter_processes.findRotationSpeed(d,timestep)
    d1 = filter_processes.derivative(d1, timestep)
    print title
    if showpressure:
        plots2.plotSingle(d1,d[3],"Rotational Speed", timestep, savename, title, outputfile, d[4], "Revolutions per second^2")
    else:
        plots2.plotSingle(d1,d[3],"Rotational Speed", timestep, savename, title, outputfile, "Revolutions per second^2")


#def plotSpectroData(d, timestep, savename, calibration = .507, cutoff=.1, title = None, outputfile = True):
#    d = d[0]    
#    d = filter_processes.calibrationFactor(d, calibration) #Add calibration factor
#    d2 = filter_processes.lowpass(d, 1.0/timestep, cutoff) #Lowpass filter
#    d = d-d2
#    plots2.plotSpectro(d,timestep, savename, title, outputfile)