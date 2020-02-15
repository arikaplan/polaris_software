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
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/cofe-python-analysis-tools-master/utils_zonca/demod')
from glob import glob
sys.path.append('C:/Python27/Lib/site-packages/')
sys.path.append('C:/Python27x86/lib/site-packages')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data_aquisition')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/VtoT')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data')
sys.path.append('C:/Users/nlynn/Documents/Research/POLARIS/cosmology')
import tkFileDialog
import cofe_util as cu
import realtime_gp2 as rt
import datetime
import plot_path as p_p
from Tkinter import *
import ttk
import numpy as np
from matplotlib import pyplot as plt



def nametochan(name):
    #function to convert channel numbers to channel names

    #names of each channel (only reads first 6 letters--so amplifier = amplif, etc) 
    chans = {
	'all': 'all',  'H1HiAC':'ch0',  'H1HiDC':'ch1',
	'H1LoAC':'ch2' ,  'H1LoDC':'ch3', 'H2HiAC':'ch4' ,
	'H2HiDC':'ch5' ,  'H2LoAC':'ch6',  'H2LoDC':'ch7',
	'H3HiAC':'ch8', 'H3HiDC':'ch9',  'H3LoAC':'ch10',
	 'H3LoDC':'ch11','Amplif': 'ch13','Cooler':'ch14'}

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

    datalist = StringVar()

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
    lstbox8.grid(column=12, row=0, columnspan=2)

	#loading data
    lstbox9 = Listbox(frame, listvariable=datalist, selectmode=MULTIPLE, width=20, height = 38)
    lstbox9.grid(column=14, row=0, columnspan=2)	

    var2 = IntVar()
    checkbox = Checkbutton(text="x axis", variable=var2).grid(column=16, row=0)
    
	 
    netfilelist = {}
    netpp = {}
    netcombined = {}
    netmihour = {}
    netmiminute = {}
    netmxhour = {}
    netmxminute = {}
    yrmodaylist = {}
    utdict = {}
    ddict = {}
    taglist=[]

    


    def load_some_data(datatype='demod',plottype='toi',filelist=None,component='T',samprate=30,minfreq=.1):
		#instantiate listboxes for each column 


		if filelist==None:  #Initial window that asks for files
		    root=Tk()
		    if datatype=='demod':
		        filelist = list(tkFileDialog.askopenfilenames(initialdir='C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data/demod_data',parent=root,title='Choose a set of files'))
		    if datatype=='raw':
		        filelist = list(tkFileDialog.askopenfilenames(initialdir='C:/Users/nlynn/Documents/Research/POLARIS/cosmology/data/data',parent=root,title='Choose a set of files'))
		    
		    root.destroy()
		else:
		    filelist.sort()

		tag = ''
		tag_entry = StringVar('') #Tkinter passes everything as a stringvar for some reason--python treats strings as primatives and wont edit the actual string when passed into a fuction
		my_window=Tk()


		def name_some_data(tag_entry,my_window):
		    tag == ''
		    def name():
			    tag_entry.set(entry.get())
			    my_window.destroy()
			    print(tag_entry,'tag') 

		    print('tag2',tag_entry)
		    label=Label(my_window,text="Enter name of data set: ")
		    entry=Entry(my_window)
		    label.grid(row=0,column=0)
		    entry.grid(row=0,column=1)
		    btn = Button(my_window, text="Enter", command=name)
		    btn.grid(column=1, row=2)
		    my_window.wait_window(my_window)
		#main.mainloop()	
			    	
		name_some_data(tag_entry,my_window)
		tag = tag_entry.get()
		#main.wait_window(my_window)
		print('tag1',tag)

		tlist=[] 
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
		        #t=h+m/60.+(s+(hf['demod_data']['rev']-hf['demod_data']['rev'][0])/1000.)/3600. #Gives file times inbetween for one file
		        t = h*3600 +m*60+(s+(hf['demod_data']['rev']-hf['demod_data']['rev'][0])/1000.) #converts time to seconds
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
		    
		print('mihour',mihour)
		print('mxhour',mxhour)
		print('miminute',miminute)
		print('mxminute',mxminute)
		netmihour.update({tag:mihour})
		netmiminute.update({tag:miminute})
		netmxminute.update({tag:mxminute})
		netmxhour.update({tag:mxhour})
		
		    
		'''if datatype=='raw':
		    h=np.float64(filelist[0][-11:-9])
		    m=np.float64(filelist[0][-9:-7])
		    s=np.float64(filelist[0][-7:-5])
		    d=rt.demod.read_raw(filelist)
		    t=h+m/60.+(s+(d['rev']-d['rev'][0])/1000.)/3600.
		    tlist.append(t)'''
		ut=np.concatenate(tlist)
		ut = sorted(ut)
		utdict.update({tag:ut})
		ddict.update({tag:d})
		print('ddict1',ddict)
		
		

		netfilelist.update({tag:filelist})
		#print('netfilelist', netfilelist)


		taglist.append(tag)
		print('taglist',taglist)
		taglist2=""
		for tag in taglist:
			taglist2+=" "+tag
		print('taglist2',taglist2)
		datalist.set(taglist2)

		#start the plot
		fname=filelist[0]
		yyyy=os.path.dirname(filelist[0])[-8:-4]
		mm=os.path.dirname(filelist[0])[-4:-2]
		day=os.path.dirname(filelist[0])[-2:]
		yrmoday = ''+yyyy+mm+day
		#print('yrmoday', yrmoday)
		yrmodaylist.update({tag:yrmoday})
		#print('yrmodaylist',yrmodaylist)
		global fpath 
		fpath = os.path.dirname(os.path.dirname(os.path.dirname(fname)))
		#***********LOAD DATA
		flp=p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute)
		fld_demod =p_p.select_h5_sig(fpath,yrmoday,mihour,miminute,mxhour,mxminute)
		fld = []
		i=0
		while len(flp)<3:
			i+=1
			flp=p_p.select_h5(fpath,yrmoday,mihour,int(miminute)-i,mxhour,int(mxminute)+i)
		#print('flp', len(flp))	

		pp=rt.get_h5_pointing(flp)
		#print('pp', pp[gpstime])
	    #dd=get_demodulated_data_from_list(fld,supply_index=supply_index)
		dd=rt.get_all_demodulated_data(fld_demod, fld)
		combined=rt.combine_cofe_h5_pointing(dd,pp)

		yrmodaylist.update({tag:yrmoday})
		netcombined.update({tag:combined})
		netpp.update({tag:pp})

		#***********

		print('datalist',datalist.get())

    def shuffleaxes(reslist,ax1,ax2,ax3):
	    #the idea is to create a three character string representing the order of the axes, and then to use that to construct the dictionary that the axes are called from
	    order = ""
	    #looking at the first entry to see what the leftmost axis should be
	    print("thing", "az el x_tilt y_tilt".find(reslist[0])!=-1)
	    if "az el x_tilt y_tilt".find(reslist[0])!=-1:
	        order += "d"
	    elif "Amplifier Cooler Backend_TSS Calibrator Phidget_Temp".find(reslist[0])!=-1:
	        order += "t"
	    elif reslist[0] in "H1HiAC_T H1HiAC_Q H1HiAC_U H1HiDC H1LoAC_T H1LoAC_Q H1LoAC_U H1LoDC H2HiAC_T H2HiAC_Q H2HiAC_U H2HiDC H2LoAC H2LoDC\
                    H3HiAC_T H3HiAC_Q H3HiAC_U H3HiDC H3LoAC_T H3LoAC_Q H3LoAC_U H3LoDC":
	        order += "v"
	    #looking to see if there are items of other data types, but only checking for existance, not the number of
	    item=1
	    while (item<len(reslist) and len(order)<=2):
	        if reslist[item] in "az el x_tilt y_tilt" and order.find("d")==-1:
	            order+="d"
	        elif reslist[item] in "Amplifier Cooler Backend_TSS Calibrator Phidget_Temp" and order.find("t")==-1:
	            order+="t"
	        elif order.find("v")==-1 and reslist[item] in "H1HiAC_T H1HiAC_Q H1HiAC_U H1HiDC H1LoAC_T H1LoAC_Q H1LoAC_U H1LoDC\
                    H2HiAC_T H2HiAC_Q H2HiAC_U H2HiDC H2LoAC H2LoDC H3HiAC_T H3HiAC_Q H3HiAC_U H3HiDC H3LoAC_T H3LoAC_Q H3LoAC_U H3LoD":
	            order+="v"
	        print('order1',reslist[item],order)
	        item+=1
	    #if only one data type, shut the other axes off
	    if len(order)==1:
	        ax2.set_axis_off()
	        ax3.set_axis_off()
	        #however there still needs to be a place in the dict for the other data types
	        order+="".join(set(["v","d","t"]).difference(set([order[0]])))
	        print('order',order)
	    #the same with two data types
	    if len(order)==2:
	        ax3.set_axis_off()
	        order+="".join(set(["v","d","t"]).difference(set([order[0],order[1]])))
	        print('order',order)
	    #the string takes the form of "vdt" or some combo of that so the keys are v,d,t
	    return {order[0]:ax1,order[1]:ax2,order[2]:ax3}

    def use_some_data():
    	global reslist3
    	reslist3 = list()
    	selection = lstbox9.curselection()

        for i in selection:
			entry = lstbox9.get(i)
			reslist3.append(entry)
			print('reslist3', reslist3)
        return reslist3

    def normalize(lst):
    	list2 = np.copy(lst)
    	for n in range(len(list2)):
    		list2[n]=(lst[n]-lst[0])
    	if var2.get() is 1:
    		return list2
    	else:
    		return lst

    def multipleyaxis(ax1):
    	ax2=ax1.twinx()
        ax3=ax1.twinx()
        ax3.spines[u"right"].set_position(("outward",50))
        return ax1,ax2,ax3


    def select():
        reslist = list()
        selection = lstbox1.curselection()
        fig,ax1=plt.subplots(figsize=(9,9))
        ax1,ax2,ax3 = multipleyaxis(ax1)

        for i in selection:
		    entry = lstbox1.get(i)
		    reslist.append(entry)
        legends = []
        print('reslist',reslist)
        #print('typereslist', type(reslist),type(reslist[0]),reslist[0])
        axdict = shuffleaxes(reslist,ax1,ax2,ax3)
        for val in reslist:
			for j,i in enumerate(reslist3):
				print('j5',j)
				if "Backend_TSS Calibrator az el x_tilt y_tilt ".find(val[:6])!=-1:
				    y=netpp[taglist[j]][val]   
				    t=normalize(netpp[taglist[j]]['gpstime'])
				    display_pointing = rt.pointing_plot(val,y,t,fig,axdict["v"],axdict["t"],axdict["d"])

				elif "Phidget_Temp ".find(val[:6])!=-1:
				    try: 
				        y=netpp[taglist[j]][val]   
				        y = y + 273.15      
				        t=normalize(netpp[taglist[j]]['gpstime'])  
				        display_pointing=rt.pointing_plot(val,y,t,fig,axdict["v"],axdict["t"],axdict["d"])

				        
				    except:
				        print("Phidget_Temp does not work")        
				else: 
				    chan=nametochan(val[:6]) 
				    if datatype=='demod':
				        component=val[-1]

				        if ((component != 'T') and (component != 'Q') and (component != 'U')) and chan != 'ch16':
				            component='T'
				            axdict["v"].plot(normalize(utdict[taglist[j]]),ddict[taglist[j]][chan][component],label=val + " " +taglist[j])
				            axdict["v"].set_ylabel("voltage (V)")
				        
				        if val == 'Cooler' or val == 'Amplifier':
				            yaxis = 'K'
				            axdict["t"].plot(normalize(utdict[taglist[j]]),ddict[taglist[j]][chan][component],label=val + " " +taglist[j])
				            axdict["t"].set_ylabel("Temperature (K)")
				        else:
				            yaxis = 'V'
				            axdict["v"].plot(normalize(utdict[taglist[j]]),ddict[taglist[j]][chan][component],label=val + " " +taglist[j])
				            axdict["v"].set_ylabel("voltage (V)")
				        plt.xlabel('Hour')
				print('legends thing', val + ': ' + taglist[j])
				legends.append(val + ': ' + taglist[j])	


			plt.title(' TOI from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))	        
			fig.legend(labels=legends)
			plt.show(block=False)

            

    def selectfft():
        reslist2 = list()
        selection2 = lstbox2.curselection()
        plt.figure(figsize=(9,9))
        legends = []

        if datatype=='demod':
            plt.title('%s ASD from %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        if datatype=='raw':
            plt.title('ASD from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        for i in selection2:
            entry2 = lstbox2.get(i)
            reslist2.append(entry2)
        for val in reslist2:
        	for j,i in enumerate(reslist3):
        		legends.append(val + ': ' + taglist[j])	
        		if val != 'Phidget_Temp':
        			if 'az el Backend_TSS Calibrator x_tilt y_tilt gpstime'.find(val[:6])!=-1:
        				freq,psd=cu.nps(netpp[taglist[j]][val],samprate,minfreq=minfreq)
        			else:
        				chan=nametochan(val[:6])
        				if datatype=='demod':
        				    component=val[-1]
        				    if ((component != 'T') and (component != 'Q') and (component != 'U')):
        				    	component='T'
        				    freq,psd=cu.nps(ddict[i][chan][component],samprate,minfreq=minfreq)
        				    plt.plot(freq,np.sqrt(psd)*1e9,label=val)
        		else:
					try:
					    freq,psd = cu.nps(netpp[i]['Phidget_Temp'],samprate,minfreq=minfreq) 
					    plt.plot(freq,np.sqrt(psd)*1e9,label=val)
					except:
					    print("Phidget_Temp is not working yet")	
        		
        plt.xlabel('Frequency [Hz]')
        plt.ylabel(r"ASD [$\frac{nV}{\sqrt{Hz}}$]")
        plt.legend(labels = legends)
        plt.show(block=False)


           
    def selectsgram(): #must use more than 1084 data samples--so more than 1 h5 file
        selection3 = lstbox3.curselection()
        entry3 = lstbox3.get(selection3[0])
        val=entry3
    	for j,i in enumerate(reslist3):
            if val != 'Phidget_Temp':
                if 'az el Amplifier Cooler Backend_TSS Calibrator x_tilt y_tilt gpstime'.find(val[:6]) != -1:
                    spectrogram=mk_spectrogram(rt.get_h5_pointing(p_p.select_h5(fpath,yrmodaylist[taglist[j]],netmihour[taglist[j]],netmiminute[taglist[j]],netmxhour[taglist[j]],netmxminute[taglist[j]]))[val],sampsperspec=sampsperspec_sgram_d)
                    xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2.)/(np.shape(spectrogram)[1])  #estimated sample rate
                else:
                    chan=nametochan(val[:6])
                    component=val[-1]
                    if ((component != 'T') and (component != 'Q') and (component != 'U')):
                        component='T'
                    spectrogram=mk_spectrogram(ddict[i][chan].flatten()[component],sampsperspec=sampsperspec_sgram_d)
                    print('ddict',len(ddict[i][chan]))
                    print('spectrogram',spectrogram)
                    xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2.)/(np.shape(spectrogram)[1])  #estimated sample rate
            else:
                spectrogram=mk_spectrogram(rt.get_h5_pointing(p_p.select_h5(fpath,yrmodaylist[taglist[i]],mihour,miminute,mxhour,mxminute))['Phidget_Temp'],sampsperspec=sampsperspec_sgram_d)
                xfreq=np.arange(np.shape(spectrogram)[1])*(samprate/2.)/(np.shape(spectrogram)[1])  #estimated sample rate

        
        yspectra=np.arange(np.shape(spectrogram)[0])
        vcut=int(len(xfreq)/10)
        vmax=max(spectrogram[0,vcut:])
        plt.figure()
        if datatype=='demod':
            plt.title('%s Spectrogram from %s-%s-%s' %(val,yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Spectrum index')        
        plt.pcolormesh(xfreq,yspectra,spectrogram,vmax=vmax)
        plt.colorbar()
        plt.figure()
        if datatype=='demod':
            plt.title('%s Spectrogram from %s-%s-%s' %(val,yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
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
        
        if datatype=='demod':
        	for j,i in enumerate(reslist3):
	            component=val[-1]
	            if ((component != 'T') and (component != 'Q') and (component != 'U')):
	                component='T'
	            if val != 'Phidget_Temp':
	            	chan=nametochan(val[:6])
	                pseudomap=mk_pseudomap(ddict[taglist[j]][chan].flatten()[component],sampsperline=sampsperline_d)
	            else: 
	            	pseudomap=mk_pseudomap(rt.get_h5_pointing(p_p.select_h5(fpath,yrmodaylist[taglist[j]],netmihour[taglist[j]],netmiminute[taglist[j]],netmxhour[taglist[j]],netmxminute[taglist[j]]))['Phidget_Temp'],sampsperline=sampsperline_d)
	            	pseudomap = pseudomap + 273.15
        plt.figure()
        if datatype=='demod':
            plt.title('%s Pseudomap from %s-%s-%s' %(val,yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        if datatype=='raw':
            plt.title('%s Pseudomap from %s-%s-%s' %(val,yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
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
            plt.title('Sig vs. az vs. rev from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        if datatype=='raw':
            plt.title('Sig vs. az vs. rev from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))

        for i in selection:
            entry = lstbox5.get(i)
            reslist.append(entry)
            for val in reslist:
        		for j,i in enumerate(reslist3):
        			if "el Backend_TSS Calibrator x_tilt y_tilt gpstime".find(val[:6])!=-1:
        				rt.plotnow_azrevsig2(fpath=fpath,yrmoday=yrmodaylist[taglist[j]],chan=val,st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],ed_minute=netmxminute[taglist[j]],pp=pp)
        			elif "Phidget_Temp".find(val[:6])!=-1:
						try: 
						    rt.plotnow_azrevsig2(fpath=fpath,yrmoday=yrmodaylist[taglist[j]],chan=val,st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],ed_minute=netmxminute[taglist[j]],pp=pp)
						except:
						    print('error Phidget_Temp is not working with this data set')

        			else:
						chan=nametochan(val[:6])
						if datatype=='demod':
							component=val[-1]
				            if ((component != 'T') and (component != 'Q') and (component != 'U')) and chan != 'ch16':
				                component ='T'
			                rt.plotnow_azrevsig(fpath=fpath,yrmoday=yrmodaylist[taglist[j]],chan=chan,var=component,st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],ed_minute=netmxminute[taglist[j]],combined=combined)  

    def selectsigvsazvsel():
        reslist = list()
        selection = lstbox6.curselection()
        plt.figure(figsize=(30,25))
        if datatype=='demod':
            plt.title('Sig vs. az vs. el from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        if datatype=='raw':
            plt.title('Sig vs. az vs. el from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        
        for i in selection:
            entry = lstbox6.get(i)
            reslist.append(entry)
        for val in reslist:
                        #y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))[val]             
            #t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmoday,mihour,miminute,mxhour,mxminute))['az']   
            #display_pointing=rt.pointing_plotaz(val,y,t)
            #else:
            for j,i in reslist3:
	            if "az el Backend_TSS Calibrator x_tilt y_tilt gpstime Phidget_Temp".find(val[:6])!=-1:
	                if "Phidget_Temp".find(val[:6])!=-1:
	                    try:
	                        rt.plotnow_azelsig2(fpath=fpath,yrmoday=yrmodaylist[taglist[j]],chan=val,st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],pp=pp,ed_minute=netmxminute[taglist[j]])
	                    except:
	                        print('Phidget_Temp is not working')
	                else:
	                    rt.plotnow_azelsig2(fpath=fpath,yrmoday=yrmodaylist[taglist[j]],chan=val,st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],pp=pp,ed_minute=netmxminute[taglist[j]])
	            else:
	                chan=nametochan(val[:6])
	                if datatype=='demod':
	                    component=val[-1]
    					if (component != 'T') and (component != 'Q') and (component != 'U') and chan != 'ch16':
	                        component='T'
	                rt.plotnow_azelsig(fpath=fpath,yrmoday=yrmodaylist[taglist[j]],chan=chan,var=component,st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],combined=combined,ed_minute=netmxminute[taglist[j]])
	            
        #plt.show(block=False)  

    def selectpft(): #no listbox 7 currently since function is already taken care of
        reslist = list()
        selection = lstbox7.curselection()
        plt.figure()
        plt.title('%s TOI from %s %s' %(mm,day,yyyy))
        for i in selection:
            entry = lstbox7.get(i)
            reslist.append(entry)

        for val in reslist:
        	for j,i in reslist3:
	            y=rt.get_h5_pointing(p_p.select_h5(fpath,yrmodaylist[taglist[j]],netmihour[taglist[j]],netmiminute[taglist[j]],netmxhour[taglist[j]],netmxminute[taglist[j]]))[val]             
	            t=rt.get_h5_pointing(p_p.select_h5(fpath,yrmodaylist[taglist[j]],netmihour[taglist[j]],netmiminute[taglist[j]],netmxhour[taglist[j]],netmxminute[taglist[j]]))['gpstime']
	            t_0=t[0]
	            for i in range(len(t)):
	                t[i]=t[i]-t_0
	            display_pointing = rt.pointing_plot(val,y,t)
	            plt.show(block=False)

    def selectsigvsaz(): 
        reslist = list()
        selection = lstbox8.curselection()
        legends = []
        fig,ax1=plt.subplots(figsize=(9,9))
        ax1, ax2,ax3 = multipleyaxis(ax1)

        if datatype=='demod':
            plt.title('Sig vs. az from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))
        if datatype=='raw':
            plt.title('Sig vs. az from %s %s %s' %(yrmodaylist[taglist[0]][4:6],yrmodaylist[taglist[0]][6:],yrmodaylist[taglist[0]][0:4]))

        for i in selection:
            entry = lstbox8.get(i)
            reslist.append(entry)
        axdict = shuffleaxes(reslist,ax1,ax2,ax3)
        for val in reslist:  
        	for j, i in enumerate(reslist3):  
        	    legends.append(val + ': ' + taglist[j])        
	            if "az el Cooler Amplifier Backend_TSS Calibrator x_tilt y_tilt Phidget_Temp".find(val[:6])!=-1:
	                y=netpp[i][val]   
	                t=normalize(netpp[i]['az'])   
	                display_pointing=rt.pointing_plotaz(val,y,t,fig,axdict['v'],axdict['t'],axdict['d'])

	            else:
	                chan=nametochan(val[:6])
	                if datatype =='demod':
	                        component=val[-1]
	                        if ((component != 'T') and (component != 'Q') and (component != 'U')) and chan != 'ch16':
	                            component ='T'
	                netcombined[i]['az']=normalize(netcombined[i]['az'])
                	rt.plotnow(yrmoday=yrmodaylist[taglist[j]],chan=chan,var=component, xaxis = 'az',st_hour=netmihour[taglist[j]],st_minute=netmiminute[taglist[j]],ed_hour=netmxhour[taglist[j]],\
                		ed_minute=netmxminute[taglist[j]],combined=netcombined[i],ax1=axdict["v"],ax2=axdict["t"],ax3=axdict["d"])
        axdict["v"].set_ylabel("voltage (V)") 
        axdict["t"].set_ylabel("Temperature (K)")
        axdict["d"].set_ylabel("degrees")   	 
        print('legends scidata', legends)
        plt.legend(labels=legends)
        plt.show()

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
    btn8.grid(column=13, row=1) 

    btn9 = ttk.Button(frame, text="Use data", command=use_some_data)
    btn9.grid(column=15, row=2)
	
    btn10 = ttk.Button(frame,text='Load data', command=load_some_data)
    btn10.grid(column=15, row=1)


    main.mainloop()
    return
    
    

if __name__=="__main__":

	if len(sys.argv) > 1:
		dtype = sys.argv[1]
	else:
		dtype = 'demod'
	

	plot_some_chans2(datatype= dtype, component='T')