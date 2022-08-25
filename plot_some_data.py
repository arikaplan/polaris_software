
from contextlib import contextmanager
import os
import datetime as dt
import numpy as np
import h5py
import time
import sys
#os.chdir('D:')
sys.path.append('../')
sys.path.append('utils_meinhold')
sys.path.append('utils_zonca')
from glob import glob
sys.path.append('VtoT/')
import Tkinter,tkFileDialog
import cofe_util as cu
import realtime_gp as rt
import datetime

from Tkinter import *
import ttk
import numpy as np
from matplotlib import pyplot as plt


def nametochan(name):
    #function to convert channel numbers to channel names

    #names of each channel
    chans = {
	'all': 'all',  'H1HiAC':'ch0',  'H1HiDC':'ch1',
	'H1LoAC':'ch2' ,  'H1LoDC':'ch3', 'H2HiAC':'ch4' ,
	'H2HiDC':'ch5' ,  'H2LoAC':'ch6',  'H2LoDC':'ch7',
	'H3HiAC':'ch8', 'H3HiDC':'ch9',  'H3LoAC':'ch10',
	 'H3LoDC':'ch11', 'HornTop':'ch12', 'Amplifier': 'ch13',
	'Cooler':'ch14', 'Transition':'ch15'}

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
    print('nlines',nlines)
    ns=nlines*sampsperline
    indata_ps=np.reshape(indata[:ns],(nlines,sampsperline))
    return indata_ps

def plot_some_chans2(datatype='demod',plottype='toi',filelist=None,component='T',samprate=30,minfreq=.1, numdatasets = None):

    if numdatasets == None:
        numdatasets = 1

    sampsperspec_sgram_d=1024
    sampsperspec_sgram_r=8192
    sampsperline_d=1800 #assume in demod data looking per file-ish or per rotation-ish
    sampsperline_r=256  #assume in raw data you want to see phase singnal per rev

    if filelist==None:
        filelist = {}
        for i in range(1, numdatasets+1):
            root=Tkinter.Tk()
            if datatype=='demod':
                filelist[i] = list(tkFileDialog.askopenfilenames(\
                initialdir='../polaris_data/demod_data/',parent=root,title='Choose a set of files'))
            if datatype=='raw':
                filelist[i] = list(tkFileDialog.askopenfilenames(\
                initialdir='../polaris_data/data/',parent=root,title='Choose a set of files'))
            root.destroy()

    for i in range(1, numdatasets+1):
        filelist[i].sort()
    main = Tk()
    main.title("Choose channels to plot")
    main.geometry("+50+150")
    frame = ttk.Frame(main, padding=(3, 3, 12, 12))
    frame.grid(column=0, row=0, sticky=(N, S, E, W))

    #set up the listbox to choose what chans to plot
    chan_labels = StringVar()
    chan_labels.set("H1HiAC_T H1HiAC_Q H1HiAC_U H1HiDC H1LoAC_T H1LoAC_Q H1LoAC_U H1LoDC\
                H2HiAC_T H2HiAC_Q H2HiAC_U H2HiDC H2LoAC H2LoDC\
                 H3HiAC_T H3HiAC_Q H3HiAC_U H3HiDC H3LoAC_T H3LoAC_Q H3LoAC_U H3LoDC HornTop Amplifier Cooler Transition")
    ut = {}
    d = {}
    for i in range(1, numdatasets + 1):
        tlist=[]
        if datatype=='demod':
            dlist=[]
            for f in filelist[i]:
                h=np.float64(f[-11:-9])
                m=np.float64(f[-9:-7])
                s=np.float64(f[-7:-5])
                hf=h5py.File(f)
                t=h+m/60.+(s+(hf['demod_data']['rev']-hf['demod_data']['rev'][0])/1000.)/3600.
                tlist.append(t)  #just generate a time to plot relative to
                dlist.append(hf['demod_data'])
            d[i]=np.concatenate(dlist)
            hf.close()

        if datatype=='raw':
            h=np.float64(filelist[i][0][-11:-9])
            m=np.float64(filelist[i][0][-9:-7])
            s=np.float64(filelist[i][0][-7:-5])
            d[i]=rt.demod.read_raw(filelist[i])
            t=h+m/60.+(s+(d[i]['rev']-d[i]['rev'][0])/1000.)/3600.
            tlist.append(t)
        ut[i]=np.concatenate(tlist)

    lstbox = Listbox(frame,listvariable=chan_labels, selectmode=MULTIPLE, width=20, height=16)
    lstbox.grid(column=0, row=0, columnspan=2)
    
    lstbox2 = Listbox(frame,listvariable=chan_labels, selectmode=MULTIPLE, width=20, height=16)
    lstbox2.grid(column=2, row=0, columnspan=2)
        
    lstbox3 = Listbox(frame,listvariable=chan_labels, selectmode=SINGLE, width=20, height=16)
    lstbox3.grid(column=4, row=0, columnspan=2)
    
    lstbox4 = Listbox(frame,listvariable=chan_labels, selectmode=SINGLE, width=20, height=16)
    lstbox4.grid(column=6, row=0, columnspan=2)
  
    
    #start the plot
    yyyy = {}
    mm = {}
    dd = {}
    for i in range(1, numdatasets + 1):
        fname=filelist[i][0]
        yyyy[i]=os.path.dirname(filelist[i][0])[-8:-4]
        mm[i]=os.path.dirname(filelist[i][0])[-4:-2]
        dd[i]=os.path.dirname(filelist[i][0])[-2:]

    def select():
        reslist = list()
        selection = lstbox.curselection()
        plt.figure()

        if numdatasets > 1:
            plt.title('TOI from multiple data sets')
        else:
            plt.title('TOI from %s %s %s' %(mm[1],dd[1],yyyy[1]))

        for i in selection:
            entry = lstbox.get(i)
            reslist.append(entry)
        for val in reslist:
            chan=nametochan(val[:6])

            for i in range(1, numdatasets + 1):

                if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')):
                        component='T'
                    if numdatasets == 1:
                        plt.plot(ut[i],d[i][chan][component],label=val)
                    else:
                        plt.plot(ut[i]-ut[i][0], d[i][chan][component], label=val+', dataset %d, start hour: %.2f' % (i, ut[i][0]))
                    plt.xlabel('Hour')
                if datatype=='raw':
                    if numdatasets == 1:
                        plt.plot(d[i][chan].flatten(),label=val)
                    else:
                        plt.plot(d[i][chan].flatten(), label=val+', dataset %d, start hour: %.2f' % (i, ut[i][0]))
                    plt.xlabel('Samples')
                plt.ylabel('Output [v]')
                plt.legend()
                plt.show(block=False)

    def selectfft():
        reslist2 = list()
        selection2 = lstbox2.curselection()
        plt.figure()

        if numdatasets > 1:
            plt.title('ASD from multiple data sets')
        else:
            plt.title('ASD from %s %s %s' %(mm[1],dd[1],yyyy[1]))

        for i in selection2:
            entry2 = lstbox2.get(i)
            reslist2.append(entry2)
        for val in reslist2:
            chan=nametochan(val[:6])

            for i in range(1, numdatasets + 1):
                if datatype=='demod':
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')):
                        component='T'
                    freq,psd=cu.nps(d[i][chan][component],samprate,minfreq=minfreq)
                if datatype=='raw':
                    freq,psd=cu.nps(d[i][chan].flatten(),samprate*256,minfreq=minfreq)
                if numdatasets == 1:
                    plt.plot(freq,np.sqrt(psd)*1e9,label=val)
                else:
                    plt.plot(freq, np.sqrt(psd) * 1e9, label=val + ', dataset %d' % i)
            plt.xlabel('Frequency [Hz]')
            plt.ylabel(r'ASD [$\frac{nV}{\sqrt{Hz}}$]')
            plt.legend()
	    plt.show(block=False)
            
    def selectsgram():
        selection3 = lstbox3.curselection()
        entry3 = lstbox3.get(selection3[0])
        val=entry3
        chan=nametochan(val[:6])
        for i in range(1, numdatasets+1):
            if datatype=='demod':
                component=val[-1]
                if ((component != 'T') and (component != 'Q') and (component != 'U')):
                    component='T'
                spectrogram=mk_spectrogram(d[i][chan].flatten()[component],sampsperspec=sampsperspec_sgram_d)
                xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2.)/(np.shape(spectrogram)[1])  #estimated sample rate
            if datatype=='raw':
                spectrogram=mk_spectrogram(d[i][chan].flatten(),sampsperspec=sampsperspec_sgram_r)
                xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2)*256/np.shape(spectrogram)[1]  #estimated sample rate
            yspectra=np.arange(np.shape(spectrogram)[0])
            vcut=int(len(xfreq)/10)
            vmax=max(spectrogram[0,vcut:])
            plt.figure()
            if numdatasets > 1:
                plt.title('%s Spectrogram from dataset %d' % (val, i))
            else:
                plt.title('%s Spectrogram from %s-%s-%s' %(val,mm[i],dd[i],yyyy[i]))
            plt.xlabel('Frequency [Hz]')
            plt.ylabel('Spectrum index')
            plt.pcolormesh(xfreq,yspectra,spectrogram,vmax=vmax)
            plt.colorbar()
            plt.show(block=False)

            plt.figure()
            if numdatasets > 1:
                plt.title('%s Spectrogram from dataset %d' % (val, i))
            else:
                plt.title('%s Spectrogram from %s-%s-%s' %(val,mm[i],dd[i],yyyy[i]))
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
        for i in range(1, numdatasets+1):
            if datatype=='demod':
                component=val[-1]
                if ((component != 'T') and (component != 'Q') and (component != 'U')):
                    component='T'
                pseudomap=mk_pseudomap(d[i][chan].flatten()[component],sampsperline=sampsperline_d)
            if datatype=='raw':
                pseudomap=mk_pseudomap(d[i][chan].flatten(),sampsperline=sampsperline_r)

            plt.figure()
            if numdatasets > 1:
                plt.title('%s Pseudomap from dataset %d' % (val, i))
            else:
                plt.title('%s Pseudomap from %s-%s-%s' %(val,mm[i],dd[i],yyyy[i]))

            plt.xlabel('Time [Samples]')
            plt.ylabel('Time index')
            plt.pcolormesh(pseudomap)
            plt.colorbar()
            plt.show(block=False)
	
    btn = ttk.Button(frame, text="Select for TOI", command=select)
    btn.grid(column=1, row=1)
    
    btn2 = ttk.Button(frame, text="Select for ASD", command=selectfft)
    btn2.grid(column=3, row=1)
    
    btn3 = ttk.Button(frame, text="Select for Spectrogram", command=selectsgram)
    btn3.grid(column=5, row=1)
    
    btn4 = ttk.Button(frame, text="Select for Pseudomap", command=selectpseudomap)
    btn4.grid(column=7, row=1) 
    
    main.mainloop()
    return

if __name__=="__main__":

    if len(sys.argv) > 1:
        dtype = sys.argv[1]
        if len(sys.argv) > 2:
            numdatasets = int(sys.argv[2])
        else:
            numdatasets = None
    else:
        dtype = 'demod'
        numdatasets = None

    plot_some_chans2(datatype= dtype, component='T', numdatasets = numdatasets)




