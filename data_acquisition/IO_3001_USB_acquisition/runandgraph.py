# -*- coding: utf-8 -*-
import graphprocesses
import storage_retrieval
import get_iotech_data
import filter_processes
import numpy as np
from IPython import get_ipython

"""THINGS THAT HAVE BEEN CHANGED:
5/28:New method in get_iotech_data - get_data_pressure(nchan,freq,nseconds,comment,alerts)
     This takes all the same data as get_data but also takes pressure sensor data as a fifth channel.
     To use pressure data use dat[4]. Pressure sensor only actually updates every ~1 second but for 
     ease of graphing we duplicate it to match the size of data.
     No graphs use pressure yet.
     Also, this tends to give errors about not having permission to use the COM5 port. If these come up:
     1) Run the program again. This has solved it every time I've tried it so far.
     2) Power on and off the inficon pressure display.
     3) Check the plugs in all the things.
     4) Open device manager and see if com5 is there. At this point it could be anything, you'll have to troubleshoot it yourself.

5/19 All data now syncs with the server in the location Q:\\Asteroid\\Lab Testing\\Laser DAQ Plotting. Plots should save automatically but
     manual changes - run sync.py to send to server.

5/14 Added force plots - take x axis and convert it to force.
     Added int-down plots. Use on noise data.
     Added resonance plots - use on noise data to find resonance frequency
     Also did major reworking of the backbone of the plotting system. There may still be some instability.
     if you get a bug with this, send me an email at kenyonprater314@gmail.com and I'll try to help sort it out
     I think force plots might be scaling wrong now, but I'm not sure. Let me know if you notice a problem.
     .

5/5 Added noise plots (raw - lowpass data.), and will probably change/add RMS plot to use
    this to get a better feel of noise amplitude
    Added preliminary spectrogram plot, but multiple issues still exist, and I 
    have not been able to get useful data out of it quite yet.
    Force vs power and force vs voltage plots are on hold for a bit.

4/28 Instead of commenting out unneeded tests, you can now toggle them by changing the booleans down below.
     In the commentlist file, time and date are now displayed along with test name
     Files will no longer overwrite one another, and duplicates will be shown as ..._Run_##.png

4/21 Added RMS (root mean square) and STD (standard deviation) plots. Both are moving averages.


4/14 Read the comment below about interactive mode and how to enable it, sorry about that.
tracked down some bugs in lowpass, if it doesn't smooth enough you can add lowpass to it.
Added a thing called XZoom Lowpass - this just zooms in on the X-axis and doesn't plot the others.
trying to add a method of adding multiple filters to the same graph, but this won't affect anything used currently."""


###
### IMPORTANT: interactive does not seem to work. If you want to enable seperate windows, type in the console (bottom right):
### In [##]: %matplotlib
### if you want to disable those seperate windows use:
### In [##]: %matplotlib inline
### When you next run the code, it should do what you want.
###    
loadfromfilename = '7-25-15 Photon recycling 35 amps test 4'
filename = "7-31-15 Asteroid De-spin discular asteroid 4.1 mtorr test 1"     #DateTypePressureTestnum, eg 1-23-15Ablation10torrtest1
comment = "Start asteroid with magnet, de-spin with laser, IR filter off."

loadfromfile= 0
outputfile =  1
showPressure =True
externalPlots=True

plotRaw          = 1
plotLowpass      = 0
plotLPZoomX      = 0
plotLPZoomY      = 0
plotRMS          = 0
plotSTD          = 0
plotXNoise       = 0
plotYNoise       = 0
plotIntDown      = 0
plotResonance    = 0
plotForceXAxis   = 0
plotPressureZoom = 0
plotVoltageZoom  = 0
plotDerivatives  = 0
plotRawX         = 0
plotSpeed        = 1
plotAcceleration = 1

'rare plots'
plotDampingLinearization = 1

#ipython = get_ipython()
#if externalPlots:
#    ipython.magic('matplotlib')
#else:
#    ipython.magic('matplotlib inline')
    

hz = 1000
time = 60*3 #seconds of data
calibration = 507.0


windowSize = 200 # Used in RMS and STD. Default should be around 100 samples (10 sec). To smooth data increase this, do sharpen it decrease.
lowpassCutoff = .35 #Cutoff in hz for the lowpass filter.

#Add actual support for 5 channel 


#Take data    
if not outputfile:
    inp = raw_input("WARNING: Data will not be saved. Enter (y) to confirm or (n) to turn on outputfile: ").lower()
    while inp[0] != 'y' and inp[0] != 'n':
        inp = raw_input("WARNING: Data will not be saved. Enter (y) to confirm or (n) to turn on outputfile: ").lower()
    if inp[0] == 'n':
        outputfile = True
        print "Outputfile set to true. Data will be saved as " + filename
    else:
        print "File will not be saved."
print 'starting data'


if loadfromfile:
    dat = storage_retrieval.readPickle(loadfromfilename+".pkl")
else:
    dat = get_iotech_data.get_data_pressure(4,hz,time,filename+comment) # Channels, hz, seconds, name of file

if outputfile:
    print "Saved run as " + filename + " : " + comment
    storage_retrieval.addComment(filename, comment)
    storage_retrieval.saveToPickle(dat,filename + ".pkl") # data,name
else:
    print "DID NOT SAVE OUTPUT FILES - outputfile set to false"


'''Do preconversions on data.
Convert dat to plotting data types: 
torr to mtorr 
volts to amps
voltage of centroid detector to um'''
dat[4] = dat[4] *1000
dat[3] = dat[3]*975.83
dat = filter_processes.calibrationFactorMult(dat,calibration,5,[3,4])

if plotRaw:
    #Raw, unfiltered data.
    graphprocesses.plotRawData(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_Raw\\" +filename + ".png", calibration,filename+ " Raw", outputfile,showPressure) # data, timestep (1/hz), filename, calibration, cutoff for lowpass, title, interactive
if plotRawX:
    #Raw, unfiltered data.
    graphprocesses.plotRawXData(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_Spin\\RawX-" +filename + ".png", calibration,filename+ " RawX", outputfile,showPressure) # data, timestep (1/hz), filename, calibration, cutoff for lowpass, title, interactive
if plotDampingLinearization:
    graphprocesses.plotDampingLinearization(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_Misc\\linearization-" +filename + ".png", calibration,filename+ " ", outputfile,showPressure) # data, timestep (1/hz), filename, calibration, cutoff for lowpass, title, interactive
if plotLowpass:
    #Lowpass
    graphprocesses.plotLPData(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_Lowpass\\Lowpass-" +filename + ".png", calibration,lowpassCutoff,filename+ " Lowpass", outputfile,showPressure) # data, timestep (1/hz), filename, calibration, cutoff for lowpass, title, interactive
if plotLPZoomX:
    #Lowpass with only x-axis
    graphprocesses.plotLPDataXZoom(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_xZoom_Lowpass\\xZoom-" +filename + ".png", calibration,lowpassCutoff,filename+ " XZoom Lowpass", outputfile,showPressure) # data, timestep (1/hz), filename, calibration, cutoff for lowpass, title, interactive
if plotLPZoomY:
    #Lowpass with only y-axis
    graphprocesses.plotLPDataYZoom(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_yZoom_Lowpass\\yZoom-" +filename + ".png", calibration,lowpassCutoff,filename+ " YZoom Lowpass", outputfile,showPressure) # data, timestep (1/hz), filename, calibration, cutoff for lowpass, title, interactive

if plotRMS:
    #Root Mean Square plot, for reference see here http://www.delsys.com/amplitude-analysis-root-mean-square-emg-envelope/
    graphprocesses.plotRMSData(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Sliding_RMS\\RMS-" + filename + ".png", calibration, lowpassCutoff, windowSize, filename + " RMS", outputfile,showPressure)
if plotSTD:
    #Standard deviation plot
    graphprocesses.plotSTDData(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Sliding_STD\\STD-" + filename + ".png", calibration, windowSize, filename + " STD", outputfile,showPressure)
  
if plotXNoise: # Plots raw data minus lowpass of same data
    graphprocesses.plotXNoiseData(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_xNoise\\xNoise-" +filename + ".png", calibration,lowpassCutoff,filename+ " XZoom Noise", outputfile,showPressure)

if plotYNoise: # Plots raw data minus lowpass of same data
    graphprocesses.plotYNoiseData(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_xNoise\\xNoise-" +filename + ".png", calibration,lowpassCutoff,filename+ " XZoom Noise", outputfile,showPressure)

if plotIntDown:
    graphprocesses.plotIntDown(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_Integration_Down\\IntDown-" +filename + ".png", calibration,lowpassCutoff,filename+ " Integration Down", outputfile)
  
if plotResonance:
    graphprocesses.plotResonanceData(dat[:], 1.0/hz,".\\Laser Ablation Lab Data and Plots\\Plots_Resonance\\Resonance-" +filename + ".png", calibration,lowpassCutoff,filename+ " Resonance", outputfile)
  
if plotForceXAxis:#Plots force using torsion balance equation, F = k/(d) * (arctan(x/y) - arctan(-dat+x/ y))/2, see spreadsheet
    graphprocesses.plotLPZoomDataForceXAxis(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_xForce\\Force-" + filename + ".png", calibration, lowpassCutoff, filename + " XZoom Force", outputfile,showPressure)
    
if plotPressureZoom: #Plots pressure data
    graphprocesses.plotPressureZoom(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Pressure\\Pressure-" + filename + ".png", lowpassCutoff, filename + " Pressure", outputfile)

if plotVoltageZoom: #Plots pressure data
    graphprocesses.plotVoltageZoom(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Voltage\\Voltage-" + filename + ".png", lowpassCutoff, filename + " Pressure", outputfile)

    
if plotDerivatives: #Plots derivative data
    graphprocesses.plotDerivativeData(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Derivative\\Derivative-" + filename + ".png", lowpassCutoff, filename + " Derivatives", outputfile)
    
if plotSpeed: #used for rotational data, when mounted on spindle mount.
    graphprocesses.plotSpeedData(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Spin\\Spin-" + filename + ".png", lowpassCutoff, filename + " Spin", outputfile)
    
if plotAcceleration:
    graphprocesses.plotAccelerationData(dat[:], 1.0/hz, ".\\Laser Ablation Lab Data and Plots\\Plots_Spin\\Acceleration-" + filename + ".png", lowpassCutoff, filename + " Acceleration", outputfile)