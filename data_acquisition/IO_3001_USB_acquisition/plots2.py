"""
Interface with matplotlib to create pretty plots for each of the data sets we take.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

from storage_retrieval import handleFilenameConflicts, getServerName


def plotSingle(d,current, channelName,timestep,savename, title = None, outputfile = True, pressure=None, labelYAxisLeft = "Position (um)"):
    """
    Plots one single channel of data, with voltage and pressure graphed as well.
    d             - data to be plotted (one dimensional array only)
    current       - current data (1d array)
    channelName   - what to call d in the graph
    timestep      - time in seconds between each data point. Typically 0.1 , but our current daq can do at least 0.001
    savename      - the name the plot will be saved to
    title         - What will be at the top of the plot.
    outputfile    - boolean - if false no files will be created.
    pressure      - either none or a 1d array of the pressure values. 
    labelYAxisLeft- label for the axis data is plottted on. Defaults to "Position (um)"
    """
    print title
    if str(type(pressure)) != "<type 'NoneType'>" and len(pressure):    
        plotDataCustom([d],[current],[channelName],["Laser Current"], timestep, savename, title, outputfile, labelYAxisLeft, 
                       dataRight2=[pressure], labelsRight2= ["Pressure"])
    else:
        plotDataCustom([d],[current],[channelName],["Laser Current"], timestep, savename, title, outputfile, labelYAxisLeft)

def plotData(d,timestep,savename, title = None, outputfile = True, pressure = True):
    """
    Creates a plot of the data vs time according to the given inputs.
    Channel 00 - X-Axis
    Channel 01 - Light Intensity
    Channel 02 - Y-Axis
    Channel 03 - Laser Current
    Channel 04 - Pressure (optional)
    
    d - the data to be plotted. Must be a 2d numpy array.
    savename - the name the plot will be saved to
    title - What will be at the top of the plot.
    outputfile - boolean - if false no files will be created.
    """    
    if pressure:
        plotDataCustom(d[0:3],[d[3]],["X-Axis","Light Intensity","Y-Axis"],["Laser Current"], timestep, savename, 
                       title, outputfile,"Position (um)","Current (amps)","Time (Sec)",[d[4]], ["Pressure"])
    else:
        plotDataCustom(d[0:3],[d[3]],["X-Axis","Light Intensity","Y-Axis"],["Laser Current"], timestep, savename, 
                       title, outputfile)

def plotDataXandY(x, y, savename, labelLine, labelXAxis, labelYAxis, title = None, outputfile = True, logscaleY = False):
    """
    A shortcut that allows plotting an one x and one y array against one another.
    x          - a numpy array representing the x axis datapoints.
    y          - a numpy array representing the y axis datapoints
    savename   - the name the plot will be saved to.
    labelLine  - label to put in legend
    labelXAxis - label of the x axis. Eg something like 'Time (sec)'
    labelYAxis - label of the y axis. Eg something like 'displacement (mm)'
    title      - title at top of graph.
    outputfile - boolean, if false no output is saved.
    logscaleY  - if true, the y axis will be logrithmic.
    """    
    plotDataCustom([y],[],[labelLine],[], None, savename, title, outputfile, labelYAxis, None, labelXAxis,None, None, None, logscaleY, False, x=x)
    
def plotDataCustom(dataLeft, dataRight, labelsLeft, labelsRight, timestep,savename, title = None, 
                   outputfile = True, yAxisLeft = "Position (um)", yAxisRight="Current (amps)", xAxis="Time (Sec)", 
                   dataRight2 = [], labelsRight2 = [], yAxisRight2 = "Pressure (mTorr)",
                   logscaleYleft = False, logscaleYright = False, logscaleYright2 = None, x=None):
    """
    Used when the standard plot won't work. Contains options for what data to put on the left and right sides, as well as what to label them.       
    dataLeft      - Array of one or more channels each to be plotted on the left scale of the graph.
    dataRight     - Array of one or more channels each to be plotted on the right scale of the graph.
    lablelsLeft   - labels to put in legends corresponding with the sequential term on the left axis.
    labelsRight   - labels to put in legends corresponding with the sequential term on the right axis.
    timestep      - time in seconds between each data point. Typically 0.1 , but our current daq can do at least 0.001
    savename      - the name the plot will be saved to
    title         - What will be at the top of the plot.
    outputfile    - boolean - if false no files will be created.
    yAxisLeft     - the label on the y axis on the left side. Defaults to 'position (um)'
    yAxisRight    - the label on the y axis on the right side. Defaults to 'Current (amps)'
    xAxis         - the label on the x axis, defaults to 'time (sec)'.
    dataRight2    - 3rd axis if needed
    labelsRight2  - labels for said 3rd axis plots
    yAxisRight2   - Units on 3rd y axis, defaults to "Pressure (mTorr)"
    logscaleYleft - boolean if true y axis will be logarithmic
    logscaleYright- boolean if true y axis log
    logscaleYright2-log axis boolean
    x             - In some cases you may want to have a different xaxis than time. In this event specify the x to plot the various y's against.
    """    
    
    #timestep is difference in time calculated by subtracting value of previous row from any row
    plt.figure(figsize=[10,5])
    subplot = host_subplot(111, axes_class=AA.Axes)
    box = subplot.get_position()
    subplot.set_position([box.x0, box.y0, box.width * 0.65, box.height])
    if x == None:
        numRows = len(dataLeft[0])
        totalTime = timestep*numRows
        x = np.arange(0,totalTime,timestep)
    plt.cla()
    pList = []
    if len(dataLeft):
        for i in range(len(dataLeft)):
            pList += subplot.plot(x,dataLeft[i], label = labelsLeft[i])
    y2axis = subplot.twinx()
    
    if len(dataRight):    
        for i in range(len(dataRight)):
            pList += y2axis.plot(x,dataRight[i], label = labelsRight[i], color=(0,0,0))
        
        y2axis.set_autoscaley_on(False)
        minval = 9999999
        maxval = -9999999
    
        for i in range(len(dataRight[0])):
            maxval = max(dataRight[0][i],maxval) #This might need to be changed if you ever need more than one thing on right y axis.
            minval = min(dataRight[0][i],minval)
        rangeval = maxval - minval
        y2axis.set_ylim([minval-rangeval*.5,maxval+rangeval*8])    #Scale the graph so that the voltage is conistantly lower and out of the wa of the regular plots.
        
        if logscaleYright:
            y2axis.set_yscale('log')   
            
        y2axis.set_ylabel(yAxisRight)       
        
    if logscaleYleft:
        subplot.set_yscale('log')
        
    
    
    plt.xlabel(xAxis)
    subplot.set_ylabel(yAxisLeft)
    
    if dataRight2 and len(dataRight2):
        y3axis = subplot.twinx()
        new_fixed_axis = y3axis.get_grid_helper().new_fixed_axis
        y3axis.axis["right"] = new_fixed_axis(loc="right",
                                        axes=y3axis,
                                        offset=(60, 0))

        y3axis.axis["right"].toggle(all=True)
        for i in range(len(dataRight)):
            pList += y3axis.plot(x,dataRight2[i], label = labelsRight2[i], color=(.5,.75,1))
        
        y3axis.set_autoscaley_on(False)
        maxval = -9999999
    
        for i in range(len(dataRight[0])):
            maxval = max(dataRight2[0][i],maxval)
        y3axis.set_ylim([0,maxval*8])    #Scale the graph so that the voltage is conistantly lower and out of the wa of the regular plots.
        
        if logscaleYright2:
            y3axis.set_yscale('log')
    
        y3axis.set_ylabel(yAxisRight2)
    first_legend = plt.legend(handles=pList, loc=2,bbox_to_anchor=(1.3, 1.05),prop={'size':10})
    plt.gca().add_artist(first_legend)
    
    if title != None:
        plt.title(title)
    else:
        plt.title("Laser Data")
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