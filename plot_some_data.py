#!/usr/bin/env python
# coding: utf-8

# In[8]:


from contextlib import contextmanager
import os
import datetime as dt
import numpy as np
import h5py
import time
import sys
os.chdir('C:')
sys.path.append('../')
#sys.path.append('/software_git_repos/cofe-python-analysis-tools/utils_meinhold/')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/cofe-python-analysis-tools-master/utils_meinhold')
#sys.path.append('/software_git_repos/cofe-python-analysis-tools/utils_zonca/')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/cofe-python-analysis-tools-master/utils_zonca/demod')
from glob import glob
#sys.path.append('../../')
#sys.path.append('../../../')
sys.path.append('C:/Python27/Lib/site-packages/')
sys.path.append('C:/Python27x86/lib/site-packages')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data_aquisition')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/VtoT')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology')
import tkFileDialog
import cofe_util as cu
import realtime_gp as rt
import datetime
import plot_path as p_p
from Tkinter import *
import ttk
import numpy as np
from matplotlib import pyplot as plt


# In[ ]:


def nametochan(name):
    #function to convert channel numbers to channel names

    #names of each channel (only reads first 6 letters--so amplifier = amplif, etc) 
    chans = {
	'all': 'all',  'H1HiAC':'ch0',  'H1HiDC':'ch1',
	'H1LoAC':'ch2' ,  'H1LoDC':'ch3', 'H2HiAC':'ch4' ,
	'H2HiDC':'ch5' ,  'H2LoAC':'ch6',  'H2LoDC':'ch7',
	'H3HiAC':'ch8', 'H3HiDC':'ch9',  'H3LoAC':'ch10',
	 'H3LoDC':'ch11','Amplif': 'ch12',
	'Cooler':'ch13','az':'ch14', 'el':'ch15',
    'Backen':'ch16', 'Calibr':'ch17','x_tilt':'ch18',
    'y_tilt':'ch19','Phidge':'ch20'}

    chan = chans[name]
    return chan

def mk_spectrogram(indata,sampsperspec=1024):
    """
    make simple spectrogram, uses nps
    """
    n=len(indata)
    nspec=np.int(n/sampsperspec)
    ns=nspec*sampsperspec
    indata=np.reshape(indata[:ns],(nspec,sampsperspec))
    sgram=[]
    for i in range(nspec):
        z=rt.nps(indata[i,:],sampsperspec)
        zlen=len(z[0])
        sgram.append(z[1])
    sgram=np.array(sgram)
    return sgram

def mk_pseudomap(indata,sampsperline=256):
    """
    make simple pseudomap
    """
    n=len(indata)
    nlines=np.int(n/sampsperline)
    ns=nlines*sampsperline
    indata_ps=np.reshape(indata[:ns],(nlines,sampsperline))
    return indata_ps

def plot_some_chans2(datatype='demod',plottype='toi',filelist=None,component='T',samprate=30,minfreq=.1): #function that creates the tkinter module and plots everything
    sampsperspec_sgram_d=1024  #samples per spectrogram demod data?
    sampsperspec_sgram_r=8192  #samples per spectrogram raw data?
    sampsperline_d=1800 #assume in demod data looking per file-ish or per rotation-ish
    sampsperline_r=256  #assume in raw data you want to see phase singnal per rev
 
    if filelist==None:  #Initial window that asks for files
        root=Tk()
        if datatype=='demod':
            filelist = list(tkFileDialog.askopenfilenames(initialdir='C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data/demod_data',parent=root,title='Choose a set of files'))
        if datatype=='raw':
            filelist = list(tkFileDialog.askopenfilenames(initialdir='C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data/data',parent=root,title='Choose a set of files'))
        
        root.destroy()
    else:
        filelist.sort()
    main = Tk() #instantiates tkinter as 'main'
    main.title("Choose channels to plot") #title of tkinter window
    main.geometry("+50+150") #size of window?
    frame = ttk.Frame(main, padding=(3, 3, 12, 12)) #instantiates frame and size 
    frame.grid(column=0, row=0, sticky=(N, S, E, W)) #instantiates grid 

    #set up the listbox to choose what chans to plot
    chan_labels = StringVar()
    chan_labels.set("H1HiAC_T H1HiAC_Q H1HiAC_U H1HiDC H1LoAC_T H1LoAC_Q H1LoAC_U H1LoDC\
                    H2HiAC_T H2HiAC_Q H2HiAC_U H2HiDC H2LoAC H2LoDC\
                    H3HiAC_T H3HiAC_Q H3HiAC_U H3HiDC H3LoAC_T H3LoAC_Q\
                    H3LoAC_U x_tilt y_tilt Phidget_Temp")
    chan_labels2 = StringVar()
    chan_labels2.set("H1HiAC_T H1HiAC_Q H1HiAC_U H1HiDC H1LoAC_T H1LoAC_Q H1LoAC_U H1LoDC\
                    H2HiAC_T H2HiAC_Q H2HiAC_U H2HiDC H2LoAC H2LoDC\
                    H3HiAC_T H3HiAC_Q H3HiAC_U H3HiDC H3LoAC_T H3LoAC_Q\
                    H3LoAC_U H3LoDC Amplifier Cooler az el Backend_TSS\
                    Calibrator x_tilt y_tilt Phidget_Temp")  #all of these need to be 6 characters at least
    chan_labels3 = StringVar()
    chan_labels3.set("H1HiAC_T H1HiAC_Q H1HiAC_U H1HiDC H1LoAC_T H1LoAC_Q H1LoAC_U H1LoDC\
                    H2HiAC_T H2HiAC_Q H2HiAC_U H2HiDC H2LoAC H2LoDC\
                    H3HiAC_T H3HiAC_Q H3HiAC_U H3HiDC H3LoAC_T H3LoAC_Q\
                    H3LoAC_U H3LoDC Amplifier Cooler Backend_TSS Calibrator Phidget_Temp")
    
    tlist=[] #figure out what all this formula stuff is doing
    if datatype=='demod':
        dlist=[]
        mxminute = 0
        miminute = 60 
        mxhour = 0
        mihour = 24
        for f in filelist:
            h=np.float64(f[-11:-9])
            m=np.float64(f[-9:-7])
            s=np.float64(f[-7:-5])
            if h>=mxhour:
                if m>=mxminute:
                    mxhour = int(h)
                    mxminute = int(m)
                
            if h<=mihour:
                if m<=miminute:
                    mihour = int(h)
                    miminute = int(m )
            hf=h5py.File(f) #opens file
            t=h+m/60.+(s+(hf['demod_data']['rev']-hf['demod_data']['rev'][0])/1000.)/3600. #Gives file times inbetween for one file
            tlist.append(t)  #just generate a time to plot relative to   Time list
            dlist.append(hf['demod_data']) #data list
        d=np.concatenate(dlist) #d is full data list
        hf.close()
        miminute = miminute -1
        mxminute = mxminute +1
        if miminute<0:
            mihour = mihour-1
            miminute = 59
        if mxminute>59:
            mxhour = mxhour+1
            mxminute = 0
        
        
        
    if datatype=='raw':
        h=np.float64(filelist[0][-11:-9])
        m=np.float64(filelist[0][-9:-7])
        s=np.float64(filelist[0][-7:-5])
        d=rt.demod.read_raw(filelist)
        t=h+m/60.+(s+(d['rev']-d['rev'][0])/1000.)/3600.
        tlist.append(t)
    ut=np.concatenate(tlist)
    ut = sorted(ut)

#instantiate listboxes for each column 

    #sig vs time
    lstbox1 = Listbox(frame,listvariable=chan_labels2, selectmode=MULTIPLE, width=20, height=38)
    lstbox1.grid(column=0, row=0, columnspan=2)

    #power spectrum vs time
    lstbox2 = Listbox(frame,listvariable=chan_labels3, selectmode=MULTIPLE, width=20, height=38)
    lstbox2.grid(column=2, row=0, columnspan=2)

    #spectrogram    
    lstbox3 = Listbox(frame,listvariable=chan_labels3, selectmode=SINGLE, width=20, height=38)
    lstbox3.grid(column=4, row=0, columnspan=2)
    
    #psudomap
    lstbox4 = Listbox(frame,listvariable=chan_labels, selectmode=SINGLE, width=20, height=38)
    lstbox4.grid(column=6, row=0, columnspan=2)

    #sig vs az vs rev
    lstbox5 = Listbox(frame,listvariable=chan_labels, selectmode=MULTIPLE, width=20, height=38)
    lstbox5.grid(column=8, row=0, columnspan=2)

    #sig vs az vs el
    lstbox6 = Listbox(frame,listvariable=chan_labels, selectmode=MULTIPLE, width=20, height=38)
    lstbox6.grid(column=10, row=0, columnspan=2)

    #pointing file info
    #lstbox7 = Listbox(frame,listvariable=chan_labels2, selectmode=MULTIPLE, width=20, height=38)
    #lstbox7.grid(column=12, row=0, columnspan=2)
  
    #scidata vs az
    lstbox8 = Listbox(frame,listvariable=chan_labels2, selectmode=MULTIPLE, width=20, height=38)
    lstbox8.grid(column=14, row=0, columnspan=2)
    #start the plot

    fname=filelist[0]
    yyyy=os.path.dirname(filelist[0])[-8:-4]
    mm=os.path.dirname(filelist[0])[-4:-2]
    dd=os.path.dirname(filelist[0])[-2:]
    yrmoday = ''+yyyy+mm+dd
    #print('yrmoday',yrmoday)
    fpath = os.path.dirname(os.path.dirname(os.path.dirname(fname)))


    def select():
        reslist = list()
        selection = lstbox1.curselection()
        plt.figure()
        if datatype=='demod':
            plt.title(' TOI from %s %s %s' %(mm,dd,yyyy))
        if datatype=='raw':
            plt.title('TOI from %s %s %s' %(mm,dd,yyyy))

        for i in selection:
            entry = lstbox1.get(i)
            reslist.append(entry)
        for val in reslist:
            if "el Backend_TSS Calibrator x_tilt y_tilt gpstime".find(val[:6])!=-1:
                y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))[val]             
                t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['gpstime']   
                display_pointing=rt.pointing_plot(val,y,t)
                yaxis = "V" 

            elif "Phidget_Temp".find(val)!=-1:
                
                y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))[val]             
                t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['gpstime']  
                display_pointing=rt.pointing_plot(val,y,t)
                yaxis = 'K'
             
                    
            else:
                chan=nametochan(val[:6])
                if datatype=='demod':
                    component=val[-1]

                    if ((component != 'T') and (component != 'Q') and (component != 'U')) and chan != 'ch16':
                        component='T'
                    plt.plot(ut,d[chan][component],label=val)
                    if chan == 'Cooler' or 'Amplifier':
                        yaxis = 'K'
                    
                if datatype=='raw':
                    plt.plot(d[chan].flatten(),label=val)
                    plt.xlabel('Samples')

            plt.xlabel('Hour')
            plt.ylabel('Output %s'  % yaxis)
            plt.legend()
            plt.show(block=False)

    def selectfft():
        reslist2 = list()
        selection2 = lstbox2.curselection()
        plt.figure()
        if datatype=='demod':
            plt.title('%s ASD from %s %s' %(mm,dd,yyyy))
        if datatype=='raw':
            plt.title('ASD from %s %s %s' %(mm,dd,yyyy))
        for i in selection2:
            entry2 = lstbox2.get(i)
            reslist2.append(entry2)
        for val in reslist2:
            if val != 'Phidget_Temp':
                chan=nametochan(val[:6])
                if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')):
                        component='T'
                    freq,psd=cu.nps(d[chan][component],samprate,minfreq=minfreq)
                if datatype=='raw':
                    freq,psd=cu.nps(d[chan].flatten(),samprate*256,minfreq=minfreq)
            else:
                chan=nametochan(val[:6])
                if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')):
                        component='T'
                    freq,psd=cu.nps(rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['Phidget_Temp'],samprate,minfreq=minfreq)
                if datatype=='raw':
                    print("Raw data is not compatible yet")

            plt.plot(freq,np.sqrt(psd)*1e9,label=val)
            plt.xlabel('Frequency [Hz]')
            plt.ylabel(r'ASD [$\frac{nV}{\sqrt{Hz}}$]')
            plt.legend()
	    plt.show(block=False)
            
    def selectsgram():
        selection3 = lstbox3.curselection()
        entry3 = lstbox3.get(selection3[0])
        val=entry3
        chan=nametochan(val[:6])
        if datatype=='demod':
            if val != 'Phidget_Temp':
                component=val[-1]
                if ((component != 'T') and (component != 'Q') and (component != 'U')):
                    component='T'
                spectrogram=mk_spectrogram(d[chan].flatten()[component],sampsperspec=sampsperspec_sgram_d)
                xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2.)/(np.shape(spectrogram)[1])  #estimated sample rate
            else:
                spectrogram=mk_spectrogram(rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['Phidget_Temp'],sampsperspec=sampsperspec_sgram_d)
                xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2.)/(np.shape(spectrogram)[1])  #estimated sample rate
        if datatype=='raw':
            if val != 'Phidget_Temp':
                spectrogram=mk_spectrogram(d[chan].flatten(),sampsperspec=sampsperspec_sgram_r)
                xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2)*256/np.shape(spectrogram)[1]  #estimated sample rate
            else:
                print('Raw data is not compatible yet')
        yspectra=np.arange(np.shape(spectrogram)[0])
        vcut=int(len(xfreq)/10)
        vmax=max(spectrogram[0,vcut:])
        plt.figure()
        if datatype=='demod':
            plt.title('%s Spectrogram from %s-%s-%s' %(val,mm,dd,yyyy))
        if datatype=='raw':
            plt.title('%s Spectrogram from %s-%s-%s' %(val,mm,dd,yyyy))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Spectrum index')        
        plt.pcolormesh(xfreq,yspectra,spectrogram,vmax=vmax)
        plt.colorbar()
        plt.show(block=False)
        plt.figure()
        if datatype=='demod':
            plt.title('%s Spectrogram from %s-%s-%s' %(val,mm,dd,yyyy))
        if datatype=='raw':
            plt.title('%s Spectrogram from %s-%s-%s' %(val,mm,dd,yyyy))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Spectrum index') 
        lsg=np.log(spectrogram/vmax)
        plt.pcolormesh(xfreq,yspectra,lsg,vmax=0)
        plt.colorbar()
        plt.show(block=False)
	
    def selectpseudomap():
        selection4 = lstbox4.curselection()
        entry4 = lstbox4.get(selection4[0])
        val=entry4
        chan=nametochan(val[:6])

        if datatype=='demod':
            component=val[-1]
            if ((component != 'T') and (component != 'Q') and (component != 'U')):
                component='T'
            if val != 'Phidget_Temp':
                pseudomap=mk_pseudomap(d[chan].flatten()[component],sampsperline=sampsperline_d)
            else: 
                pseudomap=mk_pseudomap(rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['Phidget_Temp'],sampsperline=sampsperline_d) 
        if datatype=='raw':
            pseudomap=mk_pseudomap(d[chan].flatten(),sampsperline=sampsperline_r)
        plt.figure()
        if datatype=='demod':
            plt.title('%s Pseudomap from %s-%s-%s' %(val,mm,dd,yyyy))
        if datatype=='raw':
            plt.title('%s Pseudomap from %s-%s-%s' %(val,mm,dd,yyyy))
        plt.xlabel('Time [Samples]')
        plt.ylabel('Time index')        
        plt.pcolormesh(pseudomap)
        plt.colorbar()
        plt.show(block=False)

    def selectsigvsazvsrev():
        reslist = list()
        selection = lstbox5.curselection()
        plt.figure()
        if datatype=='demod':
            plt.title('Sig vs. az vs. rev from %s %s %s' %(mm,dd,yyyy))
        if datatype=='raw':
            plt.title('Sig vs. az vs. rev from %s %s %s' %(mm,dd,yyyy))

        for i in selection:
            entry = lstbox5.get(i)
            reslist.append(entry)
        for val in reslist:
            chan=nametochan(val[:6])
            if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')) and chan != 'ch16':
                        component ='T'
            #rt.plotnow_azrevsig(fpath=fpath,yrmoday=yrmoday,chan=chan,var=component, st_hour=00,st_minute=00,
            #                    ed_hour=23,ed_minute=59)

            if "el Backend_TSS Calibrator x_tilt y_tilt gpstime".find(val[:6])!=-1:
                rt.plotnow_azrevsig2(fpath=fpath,yrmoday=yrmoday,chan=val,var=component,st_hour=mihour,st_minute=miminute,ed_hour=mxhour,ed_minute=mxminute)
            elif "Phidget_Temp".find(val[:6])!=-1:
                try: 
                    rt.plotnow_azrevsig2(fpath=fpath,yrmoday=yrmoday,chan=val,var=component,st_hour=mihour,st_minute=miminute,ed_hour=mxhour,ed_minute=mxminute)
                except:
                    print('error Phidget_Temp is not working with this data set')
            else:       
                rt.plotnow_azrevsig(fpath=fpath,yrmoday=yrmoday,chan=chan,var=component,st_hour=mihour,st_minute=miminute,ed_hour=mxhour,ed_minute=mxminute)
            
        plt.show(block=False)

    def selectsigvsazvsel():
        reslist = list()
        selection = lstbox6.curselection()
        plt.figure()
        if datatype=='demod':
            plt.title('Sig vs. az vs. el from %s %s %s' %(mm,dd,yyyy))
        if datatype=='raw':
            plt.title('Sig vs. az vs. el from %s %s %s' %(mm,dd,yyyy))
        
        for i in selection:
            entry = lstbox6.get(i)
            reslist.append(entry)
        for val in reslist:
            chan=nametochan(val[:6])
            if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')) and chan != 'ch16':
                        component ='T'

            #y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))[val]             
            #t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['az']   
            #display_pointing=rt.pointing_plotaz(val,y,t)
            #else:
            if "el Backend_TSS Calibrator x_tilt y_tilt gpstime Phidget_Temp".find(val[:6])!=-1:
                rt.plotnow_azelsig2(fpath=fpath,yrmoday=yrmoday,chan=val,var=component,st_hour=mihour,st_minute=miminute,ed_hour=mxhour,ed_minute=mxminute)
            else:
                rt.plotnow_azelsig(fpath=fpath,yrmoday=yrmoday,chan=chan,var=component,st_hour=mihour,st_minute=miminute,ed_hour=mxhour,ed_minute=mxminute)
            
        plt.show(block=False)  

    def selectpft(): #no listbox 7 currently since function is already taken care of
        reslist = list()
        selection = lstbox7.curselection()
        plt.figure()
        plt.title('%s TOI from %s %s' %(mm,dd,yyyy))
        for i in selection:
            entry = lstbox7.get(i)
            reslist.append(entry)

        for val in reslist:
            y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))[val]             
            t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['gpstime']
            t_0=t[0]
            for i in range(len(t)):
                t[i]=t[i]-t_0
            display_pointing = rt.pointing_plot(val,y,t)
            plt.show(block=False)

    def selectsigvsaz(): 
        reslist = list()
        selection = lstbox8.curselection()
        plt.figure()
        if datatype=='demod':
            plt.title(' Sig vs. az from %s %s %s' %(mm,dd,yyyy))
        if datatype=='raw':
            plt.title('Sig vs. az from %s %s %s' %(mm,dd,yyyy))

        for i in selection:
            entry = lstbox8.get(i)
            reslist.append(entry)
        for val in reslist:
            if "el Backend_TSS Calibrator x_tilt y_tilt gpstime Phidget_Temp".find(val[:6])!=-1:
            #    None
            #else:
                chan = nametochan(val[:6])
            
            if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')):
                        component ='T'
            if "el Backend_TSS Calibrator x_tilt y_tilt gpstime Phidget_Temp".find(val[:6])!=-1:
                y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))[val]             
                t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['az']   
                display_pointing=rt.pointing_plotaz(val,y,t)
            else:
                rt.plotnow(fpath=fpath,yrmoday=yrmoday,chan='ch1',var=component, xaxis = 'az',st_hour='00',st_minute='00',ed_hour='23',ed_minute='59')
                plt.show(block=False)
	
    btn = ttk.Button(frame, text="Select for TOI", command=select)
    btn.grid(column=1, row=1)
    
    btn2 = ttk.Button(frame, text="Select for ASD", command=selectfft)
    btn2.grid(column=3, row=1)
    
    btn3 = ttk.Button(frame, text="Select for Spectrogram", command=selectsgram)
    btn3.grid(column=5, row=1)
    
    btn4 = ttk.Button(frame, text="Select for Pseudomap",  command=selectpseudomap)
    btn4.grid(column=7, row=1) 

    btn5 = ttk.Button(frame, text="Select for sig vs az vs rev",  command=selectsigvsazvsrev)
    btn5.grid(column=9, row=1) 

    btn6 = ttk.Button(frame, text="Select for sig vs az vs el",  command=selectsigvsazvsel)
    btn6.grid(column=11, row=1)

    #btn7 = ttk.Button(frame, text="Select for pointing file info",  command=selectpft)
    #btn7.grid(column=13, row=1)

    btn8 = ttk.Button(frame, text="Select for scidata vs az", command=selectsigvsaz)
    btn8.grid(column=15, row=1) 
    
    main.mainloop()
    return

if __name__=="__main__":

	if len(sys.argv) > 1:
		dtype = sys.argv[1]
	else:
		dtype = 'demod'
	

	plot_some_chans2(datatype= dtype, component='T')


# In[ ]:




