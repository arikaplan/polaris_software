import config
config.update_config()
import os
import sys
from mcculw import ul
from mcculw.enums import DigitalIODirection
sys.path.append('..\data_acquisition\mcculw-examples\console')
sys.path.append('..\data_acquisition\mcculw-examples\props')
import util as util
from digital import DigitalProps
from mcculw.ul import ULError
sys.path.append('C:/Python27/Lib/site-packages/')
sys.path.append('C:/Python27x86/lib/site-packages')
sys.path.append('../data_acquisition/IO_3001_USB_acquisition')
sys.path.append('../')
sys.path.append('../data_acquisition')
sys.path.append('../VtoT')
sys.path.append('../run_phidget')
from demod import datparsing
import get_pointing as gp
import gclib
import threading
import time
from time import strftime
import pickle
from datetime import datetime, timedelta
import numpy as np
#from tkinter import ttk #this is for python 3
#from tkinter import *   #this is for python 3
from Tkinter import *    #this is for python 2.7
import ttk #this is for python 2.7
import realtime_gp as rt
import matplotlib.pyplot as plt
from plot_path import *
import planets
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from daq import daqDevice
import daqh
import numpy.ma as ma
import warnings
import subprocess 
import convert
import serial


from Phidget22.Devices.TemperatureSensor import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
from PhidgetHelperFunctions import *
import run_phidget as rph
sys.path.append('C:\\Program Files\\Phidgets\\Phidget22\\')



#only do this stuff if your connected to the galil
try:
	
	import scan
	import moveto
	import connect

	g = connect.g
	c = g.GCommand
	##
	g2 = connect.g2
	#global c2
	c2 = g2.GCommand

	#offset between galil and beam
	offsetAz = gp.galilAzOffset 
	offsetEl = gp.galilElOffset

	degtoctsAZ = config.degtoctsAZ
	degtoctsEl = config.degtoctsEl

except gclib.GclibError as e:
	print('Unexpected GclibError:', e)

global_location = config.global_location

class interface:

	def __init__(self, master):#, interval = 0.2): 

		mainFrame = Frame(master)
		mainFrame.pack()

		nb = ttk.Notebook(mainFrame)
	
		##### scan patterns ######

		##### azimuth scan #####
		page1 = Frame(nb)

		topframe = Frame(page1)
		topframe.pack(side=TOP)
	
		labelAZ = Label(topframe, text = 'azimuth scan')
		labelAZ.pack()

		inputframe = Frame(page1)
		inputframe.pack(side=TOP)

		buttonframe = Frame(page1)
		buttonframe.pack()

		self.l1 = Label(inputframe, text='Scan Time (hours)')
		self.l1.grid(row = 0, column = 0, sticky=W)
		self.l2 = Label(inputframe, text='("inf" for continuous az scan)')
		self.l2.grid(row = 1, column = 1, sticky=W)
		self.l3 = Label(inputframe, text='Scan Elevations (deg)')
		self.l3.grid(row = 2, column = 0, sticky=W)
		self.l4 = Label(inputframe, text='Input: el1, el2, ...')
		self.l4.grid(row = 3, column = 1, sticky=W)
		self.l5 = Label(inputframe, text='or "none" to stay at current el')
		self.l5.grid(row = 4, column = 1, sticky=W)

		#user input
		self.tscan = Entry(inputframe)
		self.tscan.insert(END, 'inf')
		self.tscan.grid(row = 0, column = 1)

		self.ElScans = Entry(inputframe)
		self.ElScans.insert(END, 'None')
		self.ElScans.grid(row = 2, column = 1)

		self.scan = Button(buttonframe, 
			text='Start Scan', 
			command=self.scanAz)
		self.scan.pack(side=LEFT)
	
		###### helical scan #######
	
		secondframe = Frame(page1)
		secondframe.pack(side=TOP)
	
		labelhelical = Label(secondframe, text = 'helical scan')
		labelhelical.pack()

		inputframe2 = Frame(page1)
		inputframe2.pack(side=TOP)

		buttonframe2 = Frame(page1)
		buttonframe2.pack()

		self.l1 = Label(inputframe2, text='Scan Time (minutes)')
		self.l1.grid(row = 0, column = 0, sticky=W)
		self.l4 = Label(inputframe2, text='("inf" for continuous scan)')
		self.l4.grid(row = 1, column = 1, sticky=W)
		self.l2 = Label(inputframe2, text='min scan position')
		self.l2.grid(row = 2, column = 0, sticky=W)
		self.l3 = Label(inputframe2, text='max scan position')
		self.l3.grid(row = 3, column = 0, sticky=W)

		#user input
		self.tscan2 = Entry(inputframe2)
		self.tscan2.insert(END, 'inf')
		self.tscan2.grid(row = 0, column = 1)

		self.lim1 = Entry(inputframe2)
		self.lim1.insert(END, '40.0')
		self.lim1.grid(row = 2, column = 1)

		self.lim2 = Entry(inputframe2)
		self.lim2.insert(END, '50.0')
		self.lim2.grid(row = 3, column = 1)

		self.scanhelical = Button(buttonframe2, 
			text='Start Scan', 
			command=self.scanHelical)
		self.scanhelical.pack(side=LEFT)


		###### tracking  ######
		nb2 = ttk.Notebook(nb)

		###### linear scan ######
		page2 = Frame(nb2)
		self.inputframe_lin = Frame(page2)
		self.inputframe_lin.pack(side=TOP)

		buttonframe = Frame(page2)
		buttonframe.pack(side=BOTTOM)

		self.l2 = Label(self.inputframe_lin, text='Celestial Object')
		self.l2.grid(row = 1, column = 0, sticky=W)
		self.l3 = Label(self.inputframe_lin, text='# of Az Scans')
		self.l3.grid(row = 2, column = 0, sticky=W)
		self.l4 = Label(self.inputframe_lin, text='Relative Min Az (deg)')
		self.l4.grid(row = 3, column = 0, sticky=W)
		self.l5 = Label(self.inputframe_lin, text='Relative Max AZ (deg)')
		self.l5.grid(row = 4, column = 0, sticky=W)

		#user input

		self.numAzScans_lin = Entry(self.inputframe_lin,width=10)
		self.numAzScans_lin.insert(END, '2')
		self.numAzScans_lin.grid(row = 2, column = 1,sticky=W)

		self.MinAz_lin = Entry(self.inputframe_lin,width=10)
		self.MinAz_lin.insert(END, '-10.0')
		self.MinAz_lin.grid(row = 3, column = 1,sticky=W)

		self.MaxAz_lin = Entry(self.inputframe_lin,width=10)
		self.MaxAz_lin.insert(END, '10.0')
		self.MaxAz_lin.grid(row = 4, column = 1,sticky=W)


		##########linear tracking drop down#######
		self.planets = ['RADEC Sky-Coord', 'AZEL Sky-Coord','Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune']
		self.cbody_lin=StringVar(self.inputframe_lin)
		self.cbody_lin.set(self.planets[1])
		self.phouse=OptionMenu(self.inputframe_lin,self.cbody_lin,*self.planets,command=self.update_cbody_lin)
		self.phouse.grid(row = 1, column = 1,sticky=W)

		self.scan = Button(buttonframe, 
			text='Start Scan', 
			command=self.linear)
		self.scan.pack(side=LEFT)

		###### horizontal scan ######
		page3 = Frame(nb2)
		self.inputframe_hor = Frame(page3)
		self.inputframe_hor.pack(side=TOP)

		buttonframe = Frame(page3)
		buttonframe.pack(side=BOTTOM)

		self.l2 = Label(self.inputframe_hor, text='Celestial Object')
		self.l2.grid(row = 1, column = 0, sticky=W)
		self.l3 = Label(self.inputframe_hor, text='# of Az Scans')
		self.l3.grid(row = 2, column = 0, sticky=W)
		self.l4 = Label(self.inputframe_hor, text='Relative Min Az (deg)')
		self.l4.grid(row = 3, column = 0, sticky=W)
		self.l5 = Label(self.inputframe_hor, text='Relative Max AZ (deg)')
		self.l5.grid(row = 4, column = 0, sticky=W)
		self.l6 = Label(self.inputframe_hor, text='Relative Min El (deg)')
		self.l6.grid(row = 5, column = 0, sticky=W)
		self.l7 = Label(self.inputframe_hor, text='Relative Max El (deg)')
		self.l7.grid(row = 6, column = 0, sticky=W)
		self.l8 = Label(self.inputframe_hor, text='El Step Size (deg)')
		self.l8.grid(row = 7, column = 0, sticky=W)

		#user input
		self.numAzScans_hor = Entry(self.inputframe_hor,width=10)
		self.numAzScans_hor.insert(END, '2')
		self.numAzScans_hor.grid(row = 2, column = 1,sticky=W)

		self.MinAz_hor = Entry(self.inputframe_hor,width=10)
		self.MinAz_hor.insert(END, '-10.0')
		self.MinAz_hor.grid(row = 3, column = 1,sticky=W)

		self.MaxAz_hor = Entry(self.inputframe_hor,width=10)
		self.MaxAz_hor.insert(END, '10.0')
		self.MaxAz_hor.grid(row = 4, column = 1,sticky=W)

		self.MinEl = Entry(self.inputframe_hor,width=10)
		self.MinEl.insert(END, '-10.0')
		self.MinEl.grid(row = 5, column = 1,sticky=W)

		self.MaxEl = Entry(self.inputframe_hor,width=10)
		self.MaxEl.insert(END, '10.0')
		self.MaxEl.grid(row = 6, column = 1,sticky=W)

		self.stepSize = Entry(self.inputframe_hor,width=10)
		self.stepSize.insert(END, '10.0')
		self.stepSize.grid(row = 7, column = 1,sticky=W)

		##########horizontal tracking drop down#######
		self.planets = ['RADEC Sky-Coord', 'AZEL Sky-Coord', 'Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune']
		self.cbody_hor=StringVar(self.inputframe_hor)
		self.cbody_hor.set(self.planets[1])
		self.phouse=OptionMenu(self.inputframe_hor,self.cbody_hor,*self.planets,command=self.update_cbody_hor)  
		self.phouse.grid(row = 1, column = 1,sticky=W)

		self.scan = Button(buttonframe, 
			text='Start Scan', 
			command=self.horizontal)
		self.scan.pack(side=LEFT)

		####### move distance page #########
		movePage = Frame(nb)

		moveDFrame = Frame(movePage)
		moveDFrame.pack()

		movetoFrame = Frame(movePage)
		movetoFrame.pack(side=TOP)

		labelD = Label(moveDFrame, text = 'Move Distance (deg)')
		labelD.pack()

		inputframe = Frame(moveDFrame)
		inputframe.pack(side=TOP)

		buttonframe = Frame(moveDFrame)
		buttonframe.pack(side=BOTTOM)

		self.l1 = Label(inputframe, text='az')
		self.l1.grid(row = 0, column = 0, sticky=W)

		self.l2 = Label(inputframe, text='el')
		self.l2.grid(row = 2, column = 0, sticky=W)

		#user input
		self.az = Entry(inputframe,width=8)
		self.az.insert(END, '0.0')
		self.az.grid(row = 0, column = 1)

		self.el = Entry(inputframe,width=8)
		self.el.insert(END, '0.0')
		self.el.grid(row = 2, column = 1)

		
		plus_azdis = Button(inputframe, text="+",width=5, command=lambda:self.moveDist('+az')) 
		plus_azdis.grid(row=1, column=1, padx=2, pady=0, sticky="W")
		minus_azdis = Button(inputframe, text="-",width=5, command=lambda:self.moveDist('-az'))
		minus_azdis.grid(row=1, column=2, padx=2, pady=2, sticky="W")


		plus_eldis = Button(inputframe, text="+",width=5, command=lambda:self.moveDist('+el')) 
		plus_eldis.grid(row=3, column=1, padx=2, pady=0, sticky="W")
		minus_eldis = Button(inputframe, text="-",width=5, command=lambda:self.moveDist('-el'))
		minus_eldis.grid(row=3, column=2, sticky="W")

		########## move to #############

		labelto = Label(movetoFrame, text = 'Move to Location (deg)')
		labelto.pack()

		self.inputframe2 = Frame(movetoFrame)
		self.inputframe2.pack(side=TOP)

		self.buttonframe2 = Frame(movetoFrame)
		self.buttonframe2.pack(side=BOTTOM)

		self.mtl1 = Label(self.inputframe2, text='az')
		self.mtl1.grid(row = 0, column = 0, sticky=W)

		self.mtl2 = Label(self.inputframe2, text='el')
		self.mtl2.grid(row = 1, column = 0, sticky=W)

		#user input
		self.az2 = Entry(self.inputframe2,width=8)
		self.az2.insert(END, '0.0')
		self.az2.grid(row = 0, column = 1)

		self.el2 = Entry(self.inputframe2,width=8)
		self.el2.insert(END, '0.0')
		self.el2.grid(row = 1, column = 1)
	
		az2mt = Button(self.inputframe2, text="Move",width=6, command=lambda:self.moveTo('az')) 
		az2mt.grid(row=0, column=2, padx=2, pady=0, sticky="W")        

		el2mt = Button(self.inputframe2, text="Move",width=6, command=lambda:self.moveTo('el')) 
		el2mt.grid(row=1, column=2, padx=2, pady=0, sticky="W")

		self.convert=Button(self.buttonframe2,
							text='radec/azel',command=self.update_moveto)
		self.convert.pack(side=RIGHT)

		########### configuration page ###################
		configPage=Frame(nb)
		configFrame=Frame(configPage)
		configFrame.pack()
		
		self.loclabel=Label(configFrame, text='Location')
		self.loclabel.grid(row=0, column=0, sticky=W)
		self.location=Entry(configFrame)
		self.location.grid(row=0, column=1)

		self.degtoctsAZ_l=Label(configFrame, text='Az deg to counts')
		self.degtoctsAZ_l.grid(row=1, column=0, sticky=W)
		self.degtoctsAZ=Entry(configFrame)
		self.degtoctsAZ.grid(row=1, column=1)

		self.degtoctsEL_l=Label(configFrame, text='El deg to counts')
		self.degtoctsEL_l.grid(row=2, column=0, sticky=W)
		self.degtoctsEL=Entry(configFrame)
		self.degtoctsEL.grid(row=2, column=1)

		self.azSP_l=Label(configFrame, text='az scan speed (deg/sec)')
		self.azSP_l.grid(row=3, column=0, sticky=W)
		self.azSP=Entry(configFrame)
		self.azSP.grid(row=3, column=1)

		self.azAC_l=Label(configFrame, text='az acceleration (deg/sec^2)')
		self.azAC_l.grid(row=4, column=0, sticky=W)
		self.azAC=Entry(configFrame)
		self.azAC.grid(row=4, column=1)

		self.azDC_l=Label(configFrame, text='az deceleration (deg/sec^2)')
		self.azDC_l.grid(row=5, column=0, sticky=W)
		self.azDC=Entry(configFrame)
		self.azDC.grid(row=5, column=1)

		self.elevSP_l=Label(configFrame, text='el speed (deg/sec)')
		self.elevSP_l.grid(row=6, column=0, sticky=W)
		self.elevSP=Entry(configFrame)
		self.elevSP.grid(row=6, column=1)

		self.elevAC_l=Label(configFrame, text='el acceleration (deg/sec^2)')
		self.elevAC_l.grid(row=7, column=0, sticky=W)
		self.elevAC=Entry(configFrame)
		self.elevAC.grid(row=7, column=1)

		self.elevDC_l=Label(configFrame, text='el deceleration (deg/sec^2)')
		self.elevDC_l.grid(row=8, column=0, sticky=W)
		self.elevDC=Entry(configFrame)
		self.elevDC.grid(row=8, column=1)

		self.azoffset_l=Label(configFrame, text='az offset (deg)')
		self.azoffset_l.grid(row=9, column=0, sticky=W)
		self.azoffset=Entry(configFrame)
		self.azoffset.grid(row=9,column=1)

		self.eloffset_l=Label(configFrame, text='el offset (deg)')
		self.eloffset_l.grid(row=10, column=0, sticky=W)
		self.eloffset=Entry(configFrame)
		self.eloffset.grid(row=10,column=1)

		self.apply=Button(configFrame,text='Apply', command=self.global_config)
		self.apply.grid(row=11,column=1,sticky=W)
		
		#go to directory with saved configurations
		fpath='../configurations/motion_configuration'
		
		#automatically load previously saved configurations
		try:
			os.chdir(fpath)
			with open('config.txt', 'r') as handle:
				data=pickle.loads(handle.read())

				##configuration
				self.location.delete(0,'end')
				self.location.insert(END,data['location'])
				self.degtoctsAZ.delete(0,'end')
				self.degtoctsAZ.insert(END,data['degtoctsAZ'])
				self.degtoctsEL.delete(0,'end')
				self.degtoctsEL.insert(END,data['degtoctsEL'])
				self.azSP.delete(0,'end')
				self.azSP.insert(END,data['azSP'])
				self.azAC.delete(0,'end')
				self.azAC.insert(END,data['azAC'])
				self.azDC.delete(0,'end')
				self.azDC.insert(END,data['azDC'])
				self.elevSP.delete(0,'end')
				self.elevSP.insert(END,data['elevSP'])
				self.elevAC.delete(0,'end')
				self.elevAC.insert(END,data['elevAC'])
				self.elevDC.delete(0,'end')
				self.elevDC.insert(END,data['elevDC'])
				self.azoffset.delete(0,'end')
				self.azoffset.insert(END,data['azoffset'])
				self.eloffset.delete(0,'end')
				self.eloffset.insert(END,data['eloffset'])
		 	os.chdir('../../telescope_control')	
		except:
		   pass
		
		########### real time plot frame ##################
		
		realtimePage=Frame(mainFrame)
		realtimePage.pack(side=RIGHT)
		realtimeFrame=Frame(realtimePage)
		realtimeFrame.pack(side=TOP)
		self.pplotFrame = Frame(realtimePage)
		self.pplotFrame.pack(side=BOTTOM)
	
		#start with these off, necessary to turn pplot thread on
		self.sigthread = None
		self.plotting = False
		
		#set up a canvas for realtime plotting
		self.fig = plt.figure(figsize=(5,4))
		#ax= self.fig.add_axes([0.1,0.1,0.8,0.8])
		ax1=self.fig.add_subplot(2,1,1)
		ax2=self.fig.add_subplot(2,1,2)
		canvas=FigureCanvasTkAgg(self.fig,master=self.pplotFrame)
		canvas.get_tk_widget().grid(row=0,column=1)
	
		canvas.show()

		
		#real time plotting channel drop down selection
		self.rtchan=['H1 Hi AC','H1 Hi DC','H1 Lo AC','H1 Lo DC','H2 Hi AC','H2 Hi DC'
		,'H2 Lo AC','H2 Lo DC','H3 Hi AC','H3 Hi DC','H3 Lo AC','H3 Lo DC','Backend TSS'
		,'Amplifier','Cooler','Calibrator']
		'''
		#real time plotting channel drop down selection
		self.rtchan=['ch0', 'ch1', 'ch2', 'ch3', 'ch4','ch5','ch6','ch7','ch8',
		'ch9','ch10','ch11','ch12','ch13','ch14','ch15']
		'''
		self.rtvar=StringVar()
		self.rtvar.set('H1 Hi AC')
		self.rtoption=OptionMenu(realtimeFrame,self.rtvar,*self.rtchan)
		self.rtoption.grid(row=0,column=0,sticky=W)
		
		self.pplotbutton=Button(realtimeFrame, text="plot", command=lambda: self.pplot_thread(True,canvas,ax1,ax2))
		self.pplotbutton.grid(row=0,column=1)

		self.endbutton=Button(realtimeFrame, text="end", command=lambda: self.pplot_thread(False,canvas,ax1,ax2))
		self.endbutton.grid(row=0,column=2)
	
		####### notebook layout #########
		nb.add(movePage, text='Move')
		nb.add(page1, text='Continous AZ Scans')
		nb.add(nb2, text='Tracking')
		nb.add(configPage,text='Configuration')
		nb2.add(page2, text = 'Const EL Scan')
		nb2.add(page3, text = 'Stepped EL Scan')

		nb.pack(expand=1, fill="both")

		####### output frame ##### 

		outputframe = Frame(mainFrame)
		outputframe.pack()
		
		outputframe1 = Frame(outputframe)
		outputframe1.pack()

		outputframe2 = Frame(outputframe)
		outputframe2.pack()
		
		self.title = Label(outputframe1, text='Feedback')
		self.title.pack(side=LEFT)

		self.laz = Label(outputframe2, text='az (deg)')
		self.laz.grid(row = 0, column = 0, sticky = W)

		self.aztxt = Text(outputframe2, height = 1, width = 15)
		self.aztxt.grid(row = 0, column = 1)

		self.lalt = Label(outputframe2, text='el (deg)')
		self.lalt.grid(row = 1, column = 0, sticky = W)

		self.alttxt = Text(outputframe2, height = 1, width = 15)
		self.alttxt.grid(row = 1, column = 1)
	
		self.lvoltsh1high = Label(outputframe2, text='H1(V)')
		self.lvoltsh1high.grid(row = 2, column = 0, sticky = W)

		self.voltsh1high = Text(outputframe2, height = 1, width = 15)
		self.voltsh1high.grid(row = 2, column = 1)

		self.lgpscount = Label(outputframe2, text='GPS count')
		self.lgpscount.grid(row = 2, column = 2, sticky = W)

		self.gpscount = Text(outputframe2, height = 1, width = 15)
		self.gpscount.grid(row = 2, column = 3)
	
		self.lvoltsh2high = Label(outputframe2, text='H2(V)')
		self.lvoltsh2high.grid(row = 3, column = 0, sticky = W)

		self.voltsh2high = Text(outputframe2, height = 1, width = 15)
		self.voltsh2high.grid(row = 3, column = 1)
	
		self.lvoltsh3high = Label(outputframe2, text='H3(V)')
		self.lvoltsh3high.grid(row = 3, column = 2, sticky = W)

		self.voltsh3high = Text(outputframe2, height = 1, width = 15)
		self.voltsh3high.grid(row = 3, column = 3)
	
		self.lvoltscryo12 = Label(outputframe2, text='Backend TSS(K)')
		self.lvoltscryo12.grid(row = 4, column = 0, sticky = W)

		self.voltshcryo12 = Text(outputframe2, height = 1, width = 15)
		self.voltshcryo12.grid(row = 4, column = 1)
	
		self.lvoltscryo13 = Label(outputframe2, text='Amplifier(K)')
		self.lvoltscryo13.grid(row = 4, column = 2, sticky = W)

		self.voltshcryo13 = Text(outputframe2, height = 1, width = 15)
		self.voltshcryo13.grid(row = 4, column = 3)
	
		self.lvoltscryo14 = Label(outputframe2, text='Cooler(K)')
		self.lvoltscryo14.grid(row = 5, column = 0, sticky = W)

		self.voltshcryo14 = Text(outputframe2, height = 1, width = 15)
		self.voltshcryo14.grid(row = 5, column = 1)
	
		self.lvoltscryo15 = Label(outputframe2, text='Calibrator(K)')
		self.lvoltscryo15.grid(row = 5, column = 2, sticky = W)

		self.voltshcryo15 = Text(outputframe2, height = 1, width = 15)
		self.voltshcryo15.grid(row = 5, column = 3)

		self.lxlev = Label(outputframe2, text='x tilt (deg)')
		self.lxlev.grid(row = 6, column = 0, sticky = W)

		self.xlevtxt = Text(outputframe2, height = 1, width = 15)
		self.xlevtxt.grid(row = 6, column = 1)

		self.lylev = Label(outputframe2, text='y tilt (deg)')
		self.lylev.grid(row = 6, column = 2, sticky = W)

		self.ylevtxt = Text(outputframe2, height = 1, width = 15)
		self.ylevtxt.grid(row = 6, column = 3)

		self.gpslockl = Label(outputframe2, text = 'gps lock')
		self.gpslockl.grid(row = 7, column = 0, sticky = W)

		self.gpslocktxt = Text(outputframe2, height = 1, width = 15)
		self.gpslocktxt.grid(row = 7, column = 1)

		self.lcalibrator = Label(outputframe2, text = 'calibrator')
		self.lcalibrator.grid(row = 7, column = 2, sticky = W)

		self.calibratortxt = Text(outputframe2, height = 1, width = 15)
		self.calibratortxt.grid(row = 7, column = 3)

		self.lacquisition = Label(outputframe2, text = 'acquisition')
		self.lacquisition.grid(row = 8, column = 0, sticky = W)

		self.acquisitiontxt = Text(outputframe2, height = 1, width = 15)
		self.acquisitiontxt.grid(row = 8, column = 1)


		self.lphtemp = Label(outputframe2, text = 'Phidget Temp (C)')
		self.lphtemp.grid(row = 8, column = 2, sticky = W)

		self.phtemptxt = Text(outputframe2, height = 1, width = 15)
		self.phtemptxt.grid(row = 8, column = 3)
	
		#ra dec output
		self.lra = Label(outputframe2, text='ra (deg)')
		self.lra.grid(row = 0, column = 2, sticky = W)
		self.ratxt = Text(outputframe2, height = 1, width = 15)
		self.ratxt.grid(row = 0, column = 3)
		self.ldec = Label(outputframe2, text='dec (deg)')
		self.ldec.grid(row = 1, column = 2, sticky = W)
		self.dectxt = Text(outputframe2, height = 1, width = 15)
		self.dectxt.grid(row = 1, column = 3)
	
		'''
		#galil output
		self.lazG = Label(outputframe2, text='az Galil')
		self.lazG.grid(row = 0, column = 2, sticky = W)
		self.aztxtG = Text(outputframe2, height = 1, width = 15)
		self.aztxtG.grid(row = 0, column = 3)
		self.laltG = Label(outputframe2, text='el Galil')
		self.laltG.grid(row = 1, column = 2, sticky = W)
		self.alttxtG = Text(outputframe2, height = 1, width = 15)
		self.alttxtG.grid(row = 1, column = 3)
		'''
		#start board monitering thread
		self.monitering_boards = True
		self.mbthread = threading.Thread(target=self.moniter_boards, args=())
		self.mbthread.daemon = True
		self.mbthread.start()
		self.boardindex = False # using this to make sure at least one iteration of board thread has completed before starting 
						        # monitering function
	
		#start monitering thread, with realtime voltage output
		self.monitering = True
		self.mthread = threading.Thread(target=self.moniter, args=())
		self.mthread.daemon = True                            # Daemonize thread
		self.mthread.start()  

	
		#thread = threading.Thread(target=self.moniterGalil, args=())
		#thread.daemon = True                            # Daemonize thread
		#thread.start() 

		############# stop frame ###############

		self.stopbutton = Button(mainFrame, text='Stop Motion', command=self.stop)
		self.stopbutton.pack(side=LEFT)

		self.quitButton = Button(mainFrame, text='Exit GUI', command=self.exit)
		self.quitButton.pack(side=LEFT)

		self.motorTxt = Text(mainFrame, height = 1, width = 3)
		self.motorTxt.insert(END, 'ON')
		self.motorTxt.pack(side=RIGHT)
		
		self.motorButton = Button(mainFrame, text='Motor ON/OFF', command=self.motor)
		self.motorButton.pack(side=RIGHT)
	
		self.acqtelTxt = Text(mainFrame, height = 1, width = 3)
		self.acqtelTxt.insert(END, 'OFF')
		self.acqtelTxt.pack(side=RIGHT)
	
		exebutton=Button(mainFrame, text='acq_tel',command=self.acq_tel)
		exebutton.pack(side=RIGHT)
		
		###########Record and Load Configuration###########

		self.outputframe4 = Frame(outputframe)
		self.outputframe4.pack()

		self.backup_l = Entry(self.outputframe4, width=20)
		self.backup_l.grid(row=1,column=2,sticky=W)
		self.backup_l.insert(END,'Target Label')

		self.date_l=Entry(self.outputframe4, width=20)
		self.date_l.grid(row=1,column=1,sticky=W)
		labeltime=strftime("%Y-%m-%d")
		self.date_l.insert(END,labeltime)

		self.loadbutton = Button (self.outputframe4, text='Load', command=self.read_txt)
		self.loadbutton.grid(row=1,column=0,sticky=W)
		
		self.backup_r = Entry(self.outputframe4, width=20)
		self.backup_r.grid(row=0,column=1,sticky=W)
		self.backup_r.insert(END,'Your Label')

		self.recordbutton = Button (self.outputframe4, text='Record', command=self.write_txt)
		self.recordbutton.grid(row=0,column=0,sticky=W)
	
		#load latest saved entry settings
		try:
			path='../configurations/gui_configurations/'
			os.chdir(path)
			all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
			latest_subdir = max(all_subdirs, key=os.path.getmtime)
			os.chdir(latest_subdir)
			list_of_files = glob.glob('*.txt')
			latest_file = max(list_of_files, key=os.path.getctime)
			fname=os.path.splitext(latest_file)[0]
			self.read(fname=fname,date=latest_subdir)
			os.chdir('../../telescope_control')
		except:
			pass
		
	def checkexe(self):
		#function to check if you have pressed x button to close acq_tel window
		
		check = True

		while check == True:
			time.sleep(0.5)
			#if poll is not None, you have closed the acq_tel terminal manually
			if self.p.poll() != None:
				self.acqtelTxt.delete('1.0', END)
				self.acqtelTxt.insert('1.0', 'OFF')

				check = False

		#wait 1 second to give board connection time to close
		time.sleep(1)
		
		#temporarily stop moniter thread
		self.monitering = False
		self.mthread.join()
		self.monitering = None
		
		#restart moniter thread with realtime voltage numbers
		self.monitering = True
		self.mthread = threading.Thread(target=self.moniter,args=())
		self.mthread.start()
	
	def acq_tel(self):
		#function to run acq_tel data aquistion exe
	
		#redirect to folder so you can save files	
		fpath='../../polaris_data'
		os.chdir(fpath)
		
		#find current stats, on or off
		status = str(self.acqtelTxt.get('1.0',END))
		on = status[:2]
		off = status[:3]
	
		#if its off, turn it on
		if off == 'OFF':
	
			#temporarily stop moniter thread
			self.monitering = False
			self.mthread.join()
			self.monitering = None
			
			#restart moniter thread but without realtime voltage output
			self.monitering = True
			self.mthread = threading.Thread(target=self.moniter,args=(True,))
			self.mthread.start()
			
			#wait 1 second to give board connection time to close
			time.sleep(2)
			
			#start acq_tel in seperate terminal
			self.p = subprocess.Popen('acq_tel.exe', creationflags = subprocess.CREATE_NEW_CONSOLE)
			self.acqtelTxt.delete('1.0', END)
			self.acqtelTxt.insert('1.0', 'ON')  

			os.chdir('../polaris_software/telescope_control')
			
			#while acq_tel is running, check to see if the terminal window has been closed manually
			checkthread = threading.Thread(target=self.checkexe, args=())
			checkthread.daemon = True
			checkthread.start()
	
		#if its on, turn it off
		elif on == 'ON':
		
			#terminate acq_tel process with python
			self.p.terminate()
			self.acqtelTxt.delete('1.0', END)
			self.acqtelTxt.insert('1.0', 'OFF')
		
			#wait 1 second to give board connection time to close
			time.sleep(2)

			os.chdir('../polaris_software/telescope_control')
			
			#temporarily stop moniter thread
			self.monitering = False
			self.mthread.join()
			self.monitering = None
			
			#restart moniter thread with realtime voltage numbers
			self.monitering = True
			self.mthread = threading.Thread(target=self.moniter,args=())
			self.mthread.start()
		

	def global_config(self):
		#function to save current configurations

		global_location=self.location.get()
		degtoctsAZ=eval(self.degtoctsAZ.get())
		degtoctsEL=eval(self.degtoctsEL.get())
		azSP=eval(self.azSP.get())
		azAC=eval(self.azAC.get())
		azDC=eval(self.azDC.get())
		elevSP=eval(self.elevSP.get())
		elevAC=eval(self.elevAC.get())
		elevDC=eval(self.elevDC.get())
		azoffset=eval(self.azoffset.get())
		eloffset=eval(self.eloffset.get())       
		
		fpath='../configurations'
		os.chdir(fpath)
		folder='motion_configuration'

		#this is the first file being created for that time
		if not os.path.exists(folder):
			os.makedirs(folder)

		os.chdir(folder)
		configuration={'location':global_location,'degtoctsAZ':degtoctsAZ,'degtoctsEL':degtoctsEL,
				'azSP':azSP,'azAC':azAC,'azDC':azDC,'elevSP':elevSP,'elevAC':elevAC,'elevDC':elevDC,
				'azoffset':azoffset,'eloffset':eloffset}
		
		with open('config.txt', 'w') as handle:
				pickle.dump(configuration,handle)
		
		print 'Applying Configurations'

		#go back to working directory
		os.chdir('../../telescope_control')

		#send configurations commands to galil
		config.update_config()
		
	def write_txt(self):
		#function to save current entries to file

		#get celestial body for linear and horizontal scans
		cbody_lin=self.cbody_lin.get()
		cbody_hor=self.cbody_hor.get()
		mtlabel1=self.mtl1.cget('text')
		mtlabel2=self.mtl2.cget('text')

		if cbody_lin=='Sky-Coord':
			celestialcoor_lin=[cbody_lin, self.cor1_lin.get(), self.cor2_lin.get()]
		if cbody_lin!='Sky-Coord':
			celestialcoor_lin=cbody_lin

		if cbody_hor=='Sky-Coord':
			celestialcoor_hor=[cbody_hor, self.cor1_hor.get(), self.cor2_hor.get()]
		if cbody_hor!='Sky-Coord':
			celestialcoor_hor=cbody_hor
   
		data={'Move Distance':{'az':self.az.get(),'el':self.el.get()},
				   'Move to Location':{mtlabel1:self.az2.get(),mtlabel2:self.el2.get()},
				   'Az Scan':{'Scan Time':self.tscan.get(),'Scan Elevations':self.ElScans.get()},
		   'Helical Scan':{'Scan Time':self.tscan2.get(),'min el':self.lim1.get(),
				'max el':self.lim2.get()},
				   'Linear Scan':{'Celestial Object':celestialcoor_lin,
								  'Az Scan #':self.numAzScans_lin.get(),
								  'Min Az':self.MinAz_lin.get(),
								  'Max Az':self.MaxAz_lin.get()},
				   'Horizontal Scan':{'Celestial Object':celestialcoor_hor,
									  'Az Scan #':self.numAzScans_hor.get(),
									  'Min Az':self.MinAz_hor.get(),
									  'Max Az':self.MaxAz_hor.get(),
									  'Min El':self.MinEl.get(),
									  'Max El':self.MaxEl.get(),
									  'Step Size':self.stepSize.get()}}

		date = strftime("%Y-%m-%d")
		time=strftime("%H-%M-%S")
		fpath='../configurations'
		os.chdir(fpath)

		folder='gui_configuration'
		#this is the first file being created for that time
		if not os.path.exists(folder):
			os.makedirs(folder)
		os.chdir(folder)

		#this is the first file being created for that time
		if not os.path.exists(date):
			os.makedirs(date)
		os.chdir(date)
		
		#get label for save file
		fname=self.backup_r.get()

		if os.path.isfile(fname+'.txt')==True:
			print "LABEL EXISTS. Please change your label!"
		
		else:
			with open(fname+'.txt', 'w') as handle:
				pickle.dump(data,handle)

			print 'Recording a history config at '+ date+'/'+time +','+ 'naming: '+fname

		os.chdir('../../../telescope_control')

	def read_txt(self):
		#function to find saved configurations for given label and time

		fname=self.backup_l.get()
		date=self.date_l.get()
		self.read(fname,date)
		
	def read(self,fname,date):
		#function to load saved entries from a previous save into gui entry ouput

		fpath='../configurations/gui_configuration/'

		#read all the saved entries
		try:

			os.chdir(fpath+date)

			with open(fname+'.txt', 'r') as handle:
				data=pickle.loads(handle.read())
			#print data['Move to Location']
			print 'Loading a history config of: '+ date +','+ 'naming: '+ fname

			##Move Distance
			self.az.delete(0,'end')
			self.az.insert(END,data['Move Distance']['az'])
			self.el.delete(0,'end')
			self.el.insert(END,data['Move Distance']['el'])
			
			##Move to Location
			key1,value1 = data['Move to Location'].items()[0]
			if key1 == 'el':
				key2='az'
			if key1 == 'dec':
				key2='ra'
			self.mtl1.config(text=key2)
			self.mtl2.config(text=key1)
			self.az2.delete(0,'end')
			self.az2.insert(END,data['Move to Location'][key2])
			self.el2.delete(0,'end')
			self.el2.insert(END,data['Move to Location'][key1])

			##Az Scan
			self.tscan.delete(0,'end')
			self.tscan.insert(END,data['Az Scan']['Scan Time'])
			self.ElScans.delete(0,'end')
			self.ElScans.insert(END,data['Az Scan']['Scan Elevations'])
		
			##helical Scan
			self.tscan2.delete(0,'end')
			self.tscan2.insert(END,data['Helical Scan']['Scan Time'])
			self.lim1.delete(0,'end')
			self.lim1.insert(END,data['Helical Scan']['min el'])
			self.lim2.delete(0,'end')
			self.lim2.insert(END,data['Helical Scan']['max el'])

			##Linear Scan
			celestialcoord_lin=data['Linear Scan']['Celestial Object']
			#check if saved celestial coord entry is a string or a list
			if isinstance(celestialcoord_lin,str):
				self.cbody_lin.set(celestialcoord_lin)
				try:
					self.cor1_lin.grid_forget()
					self.cor2_lin.grid_forget()
					self.cor1l_label.grid_forget()
					self.cor2l_label.grid_forget()
				except:
					pass
			if isinstance(celestialcoord_lin,list):
				self.cbody_lin.set(celestialcoord_lin[0])
				self.update_cbody_lin(celestialcoord_lin[0])
				self.cor1_lin.delete(0,'end')
				self.cor2_lin.delete(0,'end')
				self.cor1_lin.insert(END,celestialcoord_lin[1])
				self.cor2_lin.insert(END,celestialcoord_lin[2])
			self.numAzScans_lin.delete(0,'end')
			self.numAzScans_lin.insert(END,data['Linear Scan']['Az Scan #'])
			self.MinAz_lin.delete(0,'end')
			self.MinAz_lin.insert(END,data['Linear Scan']['Min Az'])
			self.MaxAz_lin.delete(0,'end')
			self.MaxAz_lin.insert(END,data['Linear Scan']['Max Az'])

			##Horizontal Scan
			celestialcoord_hor=data['Horizontal Scan']['Celestial Object']
			#check if saved celestial coord entry is a string or a list
			if isinstance(celestialcoord_hor,str):
				self.cbody_hor.set(celestialcoord_hor)
				try:
					self.cor1_hor.grid_forget()
					self.cor2_hor.grid_forget()
					self.cor1h_label.grid_forget()
					self.cor2h_label.grid_forget()
				except:
					pass
			if isinstance(celestialcoord_hor,list):
				self.cbody_hor.set(celestialcoord_hor[0])
				self.update_cbody_hor(celestialcoord_hor[0])
				self.cor1_hor.delete(0,'end')
				self.cor2_hor.delete(0,'end')
				self.cor1_hor.insert(END,celestialcoord_hor[1])
				self.cor2_hor.insert(END,celestialcoord_hor[2])
			self.numAzScans_hor.delete(0,'end')
			self.numAzScans_hor.insert(END,data['Horizontal Scan']['Az Scan #'])
			self.MinAz_hor.delete(0,'end')
			self.MinAz_hor.insert(END,data['Horizontal Scan']['Min Az'])
			self.MaxAz_hor.delete(0,'end')
			self.MaxAz_hor.insert(END,data['Horizontal Scan']['Max Az'])
			self.MinEl.delete(0,'end')
			self.MinEl.insert(END,data['Horizontal Scan']['Min El'])
			self.MaxEl.delete(0,'end')
			self.MaxEl.insert(END,data['Horizontal Scan']['Max El'])
			self.stepSize.delete(0,'end')
			self.stepSize.insert(END,data['Horizontal Scan']['Step Size'])

			os.chdir('../../../telescope_control')

		except IOError:
			print 'No Labels Found'
				
	#tacking coordinate input        
	def update_cbody_lin(self,cbody):
		#update linear scan cbody entries to be either saved object or a sky location

		try:
			self.cor1_lin.grid_forget()
			self.cor2_lin.grid_forget()
			self.cor1l_label.grid_forget()
			self.cor2l_label.grid_forget()

		except:
			pass

		if cbody=='RADEC Sky-Coord':
			self.cor1_lin=Entry(self.inputframe_lin,width=5)
			self.cor1_lin.grid(row=1,column=3,sticky=W)
			self.cor2_lin=Entry(self.inputframe_lin,width=5)
			self.cor2_lin.grid(row=1,column=5,sticky=W)
			self.cor1l_label = Label(self.inputframe_lin, text='RA')
			self.cor1l_label.grid(row =1, column = 2, sticky=W)
			self.cor2l_label = Label(self.inputframe_lin, text='Dec')
			self.cor2l_label.grid(row =1, column = 4, sticky=W)

		if cbody=='AZEL Sky-Coord':
			self.cor1_lin=Entry(self.inputframe_lin,width=5)
			self.cor1_lin.grid(row=1,column=3,sticky=W)
			self.cor2_lin=Entry(self.inputframe_lin,width=5)
			self.cor2_lin.grid(row=1,column=5,sticky=W)
			self.cor1l_label = Label(self.inputframe_lin, text='AZ')
			self.cor1l_label.grid(row =1, column = 2, sticky=W)
			self.cor2l_label = Label(self.inputframe_lin, text='EL')
			self.cor2l_label.grid(row =1, column = 4, sticky=W)
	   
	def update_cbody_hor(self,cbody):
		#update horizontal scan cbody entries to be either saved object or a sky location

		try:
			self.cor1_hor.grid_forget()
			self.cor2_hor.grid_forget()
			self.cor1h_label.grid_forget()
			self.cor2h_label.grid_forget()

		except:
			pass

		if cbody=='RADEC Sky-Coord':
			self.cor1_hor=Entry(self.inputframe_hor,width=5)
			self.cor1_hor.grid(row=1,column=3,sticky=W)
			self.cor2_hor=Entry(self.inputframe_hor,width=5)
			self.cor2_hor.grid(row=1,column=5,sticky=W)
			self.cor1h_label = Label(self.inputframe_hor, text='RA')
			self.cor1h_label.grid(row =1, column = 2, sticky=W)
			self.cor2h_label = Label(self.inputframe_hor, text='Dec')
			self.cor2h_label.grid(row =1, column = 4, sticky=W)

		if cbody=='AZEL Sky-Coord':
			self.cor1_hor=Entry(self.inputframe_hor,width=5)
			self.cor1_hor.grid(row=1,column=3,sticky=W)
			self.cor2_hor=Entry(self.inputframe_hor,width=5)
			self.cor2_hor.grid(row=1,column=5,sticky=W)
			self.cor1h_label = Label(self.inputframe_hor, text='AZ')
			self.cor1h_label.grid(row =1, column = 2, sticky=W)
			self.cor2h_label = Label(self.inputframe_hor, text='EL')
			self.cor2h_label.grid(row =1, column = 4, sticky=W)


	#keep this in case I want to compare encoder postion to galil position
	# i.e. moniter both at the same time
	def moniterGalil(self):
		#function to moniter galil position 

		t1 = time.time()

		while True:
			t2 = time.time()
			dt = t2 - t1

			if dt >= 2:
				Paz = (float(c2('TPX'))/ degtoctsAZ + offsetAz) % 360.
				Palt = (float(c2('TPY'))/ degtoctsEl + offsetEl) % 360.
				self.aztxtG.delete('1.0', END)
				self.aztxtG.insert('1.0', Paz)
				self.alttxtG.delete('1.0', END)
				self.alttxtG.insert('1.0', Palt)


	def moniter_boards(self):
		try:
			#open com port for level sensor
			ser = serial.Serial()
			ser.baudrate = 9600
			ser.timeout = 1
			ser.port = 'COM11'
			ser.open()
		except:
			print 'Check COM port for lvl senor. Nucie: COM13, NUClear: COM11'
			pass

		#set up monitering for calibrator in/out and emulator/encoder
		use_device_detection=True
		board_num = 1

		#locate device
		if use_device_detection:
			ul.ignore_instacal()
			if not util.config_first_detected_device(board_num):
				print 'Could not find DIO device'

		digital_props = DigitalProps(board_num)

		#Find the first port that supports input, defaulting to None 
		#if one is not found.
		port = next((port for port in digital_props.port_info
			if port.supports_input), None)

		#for some reason it fails every other time, so if port = none
		# once try again, then if it still fails give error message
		if port == None:
			
			ul.release_daq_device(board_num)
    		if use_device_detection:
        		ul.ignore_instacal()
        		if not util.config_first_detected_device(board_num, printstatement=False):
        			print 'Could not find DIO device'

    		digital_props = DigitalProps(board_num)
    
    		port = next((port for port in digital_props.port_info 
    			if port.supports_input), None)
			
    		if port == None:
    			util.print_unsupported_example(board_num)
    			print 'no port found on DIO device'
    		
			#util.print_unsupported_example(board_num)
			#print 'no port found on DIO device'
		
		#set up phidget
		try:
			try:
			    ch = TemperatureSensor() # tries to open up channel to the sensor
			except PhidgetException as e:
			   	sys.stderr.write("Runtime Error: Creating TemperatureSensor: \n\t")
			   	DisplayError(e)
			   	raise
			except RuntimeError as e:
			   	sys.stderr.write("Runtime Error: Creating TemperatureSensor: \n\t" + e)
			   	raise
			ch.setDeviceSerialNumber(424828)
			ch.setChannel(0)    # sets channel # and serial #
			ch.setOnAttachHandler(rph.attach_handler)  # sets attach and error handlers
			ch.setOnErrorHandler(rph.error_handler)
			try:
			   	ch.openWaitForAttachment(5000)  # waits for phidget attachment
			except PhidgetException as e:
			   	PrintOpenErrorMessage(e, ch)
			   	raise EndProgramSignal("Program Terminated: Open Failed")
			# I used input to have it wait (and not terminate), but I am not sure
			# if you will be able to poll the program while it is waiting for input

			#input('Press any key to end')
		except PhidgetException as e:
			sys.stderr.write("\nExiting with error(s)...")
			DisplayError(e)
			traceback.print_exc()
			print("Cleaning up...")
			ch.setOnTemperatureChangeHandler(None)
			ch.close()
			#return 1
		except EndProgramSignal as e:
			print(e)
			print("Cleaning up...")
			ch.setOnTemperatureChangeHandler(None)
			ch.close()
			#return 1

		count = 0
		while self.monitering_boards:
			
			try:
				#get level information
				lev = ser.readline()

			except:
				lev = 'nan'
			
			if len(lev) != 19 or lev[0] != 'X':
				xlev = float('nan')
				ylev = float('nan')
			else:
				xlev = float(lev[3:8])
				ylev = float(lev[11:])
			
			try:
				phidgetTemp = ch.getTemperature()

			except:
				phidgetTemp = float('nan')

			global gphidgetTemp
			gphidgetTemp = phidgetTemp

			global gxlev, gylev
			gxlev, gylev = xlev, ylev

			#get status bits for calibrator in/out and emulator/encoder
			global gcalin
			gcalin = ul.d_bit_in(board_num, port.type, 16)
			global gcalout
			gcalout = ul.d_bit_in(board_num, port.type, 17)
			global gacqtype
			gacqtype = ul.d_bit_in(board_num, port.type, 18)

			#making sure this thread completes once before next threads loop starts
			if count == 0:
				count += 1
				self.boardindex = True


	def moniter(self, acq_tel = False):
		#function to moniter absolute encoder position, horn voltage, and cryo sensor temp

		#time to wait between writing files
		write_time = 60


		if len(sys.argv)>1: #this is the defualt no argument write time
			write_time=sys.argv[-1] #this sets how long it takes to write a file
		
		#this is where data will be stored
		Data = gp.datacollector()

		time_a = time.time()
		#starttime = time.time()

		#only try to connect to aquisition board if acq_tel is not running
		if acq_tel == False:
			
			# Device name as registered with the Windows driver.
			self.dev = daqDevice('DaqBoard3031USB')

			# Programmable amplifier with gain of 1.
			gain = daqh.DgainX1

			# Bipolar-voltage differential input, unsigned-integer readout.
			flags = (
				daqh.DafAnalog | daqh.DafUnsigned  # Default flags.
				| daqh.DafBipolar | daqh.DafDifferential  # Nondefault flags.
				)
			
			# max_voltage and bit_depth are device specific.
			# Our device's bipolar voltage range is -10.0 V to +10.0 V.
			max_voltage = 10.0
			# Our device is a 16 bit ADC.
			bit_depth = 16

		else:
			#if acq_tel is running close previous connection
			self.dev.Close()

		
		#start moniter loop
		while self.monitering:

			#let board thread complete one iteration before starting
			if not self.boardindex:
				continue

			#t1 = time.time()
			#get az,el & gpstime from absolute encoder, set as global variables to be used in other functions
			global gaz, gel, ggpstime
			gaz, gel, ggpstime = gp.getAzEl() [:3]

			#get gps haslock to make sure it is actually obtaining gpstime
			gpslock = gp.getAzEl()[3]
			'''
			#elevation encoder sometimes gives nonsense values, if this happens skip loop iteration
			if gel < 0. or gel > 99.:
			   #print 'skipping bad data point, el=', gel
			   continue
			'''
			#telescope can go over 90 degrees, if it does correct pointing
			if gel > 90.:
			  gel = 180. - gel
			  gaz = (gaz + 180.) % 360.
			
			az, el, gpstime = gaz, gel, ggpstime

			#only convert to radec if acq_tel isnt running because it slows down aquisition
			if acq_tel == False:
				#convert to radec

				#ra, dec = 0.0, 0.0
				ra, dec = planets.azel_to_radec(az, el, global_location)
			else:
				ra = 'Off for acq_tel'
				dec = 'Off for acq_tel'

			time_d = time.time()
			#absolute counter, this is a bug that I fixed but im putting it back to how it was because it fucks with gps time, or makes code unstable
			delta2 = time_d-time_a


			#if acq_tel is not running, get raw data directly
			if acq_tel == False:

				# Read one sample of DC high channels + cryo sensors
				datah1high = self.dev.AdcRd(1, gain, flags)
				datah2high = self.dev.AdcRd(5, gain, flags)
				datah3high = self.dev.AdcRd(256 + 9 - 8, gain, flags)
				datacryo12 = self.dev.AdcRd(256 + 12 - 8, gain, flags)
				datacryo13 = self.dev.AdcRd(256 + 13 - 8, gain, flags)
				datacryo14 = self.dev.AdcRd(256 + 14 - 8, gain, flags)
				datacryo15 = self.dev.AdcRd(256 + 15 - 8, gain, flags)
			
				# Convert sample from unsigned integer value to bipolar voltage.
				vh1high = datah1high*max_voltage*2/(2**bit_depth) - max_voltage
				vh2high = datah2high*max_voltage*2/(2**bit_depth) - max_voltage
				vh3high = datah3high*max_voltage*2/(2**bit_depth) - max_voltage
				vcryo12 = datacryo12*max_voltage*2/(2**bit_depth) - max_voltage
				vcryo13 = datacryo13*max_voltage*2/(2**bit_depth) - max_voltage
				vcryo14 = datacryo14*max_voltage*2/(2**bit_depth) - max_voltage
				vcryo15 = datacryo15*max_voltage*2/(2**bit_depth) - max_voltage
				
				#convert from volts to temperature    
				tcryo12 = vcryo12*10. + 273.15 # Backend TSS
				tcryo13 = convert.convert(vcryo13, 'e') # Amplifier
				tcryo14 = convert.convert(vcryo14, 'h') # Cooler
				tcryo15 = vcryo15*10. + 273.15 # Calibrator

				
			#if acq_tel is running, get average of latest saved file rather than realtime feedback
			else:

				yrmoday = strftime("%Y%m%d")
				fpath = '../../polaris_data/data/' + yrmoday
				fld=glob.glob(fpath+'/*.dat')

				#check if folder exists and that there is more than one file
				if os.path.exists(fpath) and len(fld) > 1:
					stats = os.stat(fld[-2])
					fsize = stats.st_size
				else:
					fsize = None
				
				#give new file time to complete and check that last completed file is full
				if fsize > 10752000/2 and delta2 > (write_time-1.):

					fld.sort()

					#get latest (complete) data file
					dr=datparsing.read_raw([fld[-2]], printstatements = False)

					vh1high = dr['ch1'].mean()
					vh2high = dr['ch5'].mean()
					vh3high = dr['ch9'].mean()
					vcryo12 = dr['ch12'].mean()
					vcryo13 = dr['ch13'].mean()
					vcryo14 = dr['ch14'].mean()
					vcryo15 = dr['ch15'].mean()
					
					#convert from volts to temperature
					tcryo12 = vcryo12*10. + 273.15
					tcryo13 = convert.convert(vcryo13, 'e')
					tcryo14 = convert.convert(vcryo14, 'h')
					tcryo15 = vcryo15*10. + 273.15

				else:
					#if no data file exits output/save nan value
					vh1high = float('nan')
					vh2high = float('nan')
					vh3high = float('nan')
					tcryo12 = float('nan')
					tcryo13 = float('nan')
					tcryo14 = float('nan')
					tcryo15 = float('nan')
				
			#get status bits for calibrator in/out and emulator/encoder
			cal_in = gcalin
			cal_out = gcalout
			acq_type = gacqtype

			#get current az/el offset to save to file
			ELoffset = config.eloffset
			AZoffset = config.azoffset

			#add current computer time for when gpspointing cuts out and for use in finding wrap point for single gpstime data point
			comptime = time.time()

			#set up column for flags in h5 file, can expand on this later
			if acq_tel == False:
				acq_tel_status = 0
			else:
				acq_tel_status = 1

			#add flags as a binary number with following order:
			#cal in
			#cal out
			#emulator (1) vs encoder(0)
			#gps lock
			#acq_tel on/off
			#note until I figure this out cal_in isnt saved when its 0, it is saved when its one, so if the flag is 4 digits it means cal_in=0
			flag = str(cal_in)+str(cal_out)+str(acq_type)+str(gpslock)+str(acq_tel_status)

			#get global level sensor data
			xlevel = gxlev
			ylevel = gylev

			try:
				#get relative galil encoder positions
				relaz = (float(c2('TPX'))/ degtoctsAZ + offsetAz) % 360.
				relalt = (float(c2('TPY'))/ degtoctsEl + offsetEl) % 360.
			except:
				relaz = 0.0
				relalt = 0.0

			#get global phidget temperature data
			phTemp = gphidgetTemp

			#save pointing + science data to Data object
			Data.add(az,el,gpstime, vh1high, vh2high, vh3high, tcryo12, tcryo13, tcryo14, tcryo15, xlevel, ylevel, AZoffset, ELoffset, comptime, flag, relaz, relalt, phTemp)
			
			time_b = time.time()
			#wrapped counter
			delta = time_b-time_a
			#print 'data added every: ', delta, ' sec'

			#if its been more than 2 seconds start outputting feedback
			if (delta2>=2):

				self.aztxt.delete('1.0', END)
				self.aztxt.insert('1.0', az)
				self.alttxt.delete('1.0', END)
				self.alttxt.insert('1.0', el)

				self.gpscount.delete('1.0', END)
				self.gpscount.insert('1.0', gpstime)
				
				if gpslock == 1:
					self.gpslocktxt.delete('1.0', END)
					self.gpslocktxt.insert('1.0', 'Has lock')
				if gpslock == 0:
					self.gpslocktxt.delete('1.0', END)
					self.gpslocktxt.insert('1.0', 'No lock')

				if cal_in == 1 and cal_out == 0:
					self.calibratortxt.delete('1.0', END)
					self.calibratortxt.insert('1.0', 'IN')

				elif cal_in == 0 and cal_out == 1:
					self.calibratortxt.delete('1.0', END)
					self.calibratortxt.insert('1.0', 'OUT')
				else:
					self.calibratortxt.delete('1.0', END)
					self.calibratortxt.insert('1.0', 'Moving')

				if acq_type == 0:
					self.acquisitiontxt.delete('1.0', END)
					self.acquisitiontxt.insert('1.0', 'Encoder')
				if acq_type == 1:
					self.acquisitiontxt.delete('1.0', END)
					self.acquisitiontxt.insert('1.0', 'Emulator')
				
				self.ratxt.delete('1.0', END)
				self.ratxt.insert('1.0', ra)
				self.dectxt.delete('1.0', END)
				self.dectxt.insert('1.0', dec)
				
				if np.isnan(xlevel) != True:
					self.xlevtxt.delete('1.0', END)
					self.xlevtxt.insert('1.0', xlevel)
				if np.isnan(ylevel) != True:
					self.ylevtxt.delete('1.0', END)
					self.ylevtxt.insert('1.0', ylevel)

				if np.isnan(phTemp) != True:
					self.phtemptxt.delete('1.0', END)
					self.phtemptxt.insert('1.0', phTemp)
				
				if acq_tel == False:
					self.voltsh1high.delete('1.0', END)
					self.voltsh1high.insert('1.0', vh1high)
					self.voltsh2high.delete('1.0', END)
					self.voltsh2high.insert('1.0', vh2high)		
					self.voltsh3high.delete('1.0', END)
					self.voltsh3high.insert('1.0', vh3high)		
					self.voltshcryo12.delete('1.0', END)
					self.voltshcryo12.insert('1.0', tcryo12)		
					self.voltshcryo13.delete('1.0', END)
					self.voltshcryo13.insert('1.0', tcryo13)		
					self.voltshcryo14.delete('1.0', END)
					self.voltshcryo14.insert('1.0', tcryo14)
					self.voltshcryo15.delete('1.0', END)
					self.voltshcryo15.insert('1.0', tcryo15)
				
				elif acq_tel == True and delta2 > write_time and fsize == 10752000:
					self.voltsh1high.delete('1.0', END)
					self.voltsh1high.insert('1.0', vh1high)
					self.voltsh2high.delete('1.0', END)
					self.voltsh2high.insert('1.0', vh2high)		
					self.voltsh3high.delete('1.0', END)
					self.voltsh3high.insert('1.0', vh3high)		
					self.voltshcryo12.delete('1.0', END)
					self.voltshcryo12.insert('1.0', tcryo12)		
					self.voltshcryo13.delete('1.0', END)
					self.voltshcryo13.insert('1.0', tcryo13)		
					self.voltshcryo14.delete('1.0', END)
					self.voltshcryo14.insert('1.0', tcryo14)
					self.voltshcryo15.delete('1.0', END)
					self.voltshcryo15.insert('1.0', tcryo15)
				
			#write data to file
			if(delta>=int(write_time)):
				gp.fileStruct(Data.getData(), Data)
				time_a=time.time()
				print("file written")
			time.sleep(0.02)
			#print 'sampling at %f Hz: ' % (1.0/(time.time()-t1))
		try:
			print("data collected at " + str(1.0/delta) +"HZ")
		except:
			pass


	def scanAz(self):
		#function to start azimuthal scan

		#get azimuthal scan duration
		tscan = self.tscan.get()

		if tscan == 'inf':
			tscan = np.inf
		else:
			tscan = float(tscan)

		#get how much elevation will change by in each iteration
		ElScans = self.ElScans.get()

		if ElScans == 'None':
			ElScans = None
		else:
			ElScans = ElScans.split(',')

		#start azimuthal scan as a thread
		#thread = threading.Thread(target=scan.azScan2, args=(tscan, ElScans, gaz, gel, c))
		thread = threading.Thread(target=scan.azScan, args=(tscan, 1, 0, gaz, gel, c))

		thread.daemon = True
		thread.start()
	
	def scanHelical(self):
		#function to start a helical scan

		#get duration for helical scan
		tscan = self.tscan2.get()

		if tscan == 'inf':
			tscan = np.inf
		else:
			tscan = float(tscan)

		#get upper and lower elevation limit for scan
		lim1 = float(self.lim1.get())
		lim2 = float(self.lim2.get())

		#start helical scan as a thread
		thread = threading.Thread(target=scan.helicalScan, args=(tscan, lim1, lim2, gaz, gel, c))
		thread.daemon = True
		thread.start()

	def linear(self):
		#function to start a linear scan around a celestial target

		#get observer location from global configurations
		location = global_location
		#get celestial target
		cbody = self.cbody_lin.get()
		#number of sweeps to do around target (back and forth is 2)
		numAzScans = int(self.numAzScans_lin.get())
		#minimum and maximum azimuthal distance for each sweep
		MinAz = float(self.MinAz_lin.get())
		MaxAz = float(self.MaxAz_lin.get())

		if cbody == 'Sky-Coord':
			#get radec values for sky location target
			RA = self.cor1_lin.get()
			DEC = self.cor2_lin.get()
			cbody = [RA, DEC]

		if cbody == 'AZEL Sky-Coord':
			AZ = self.cor1_lin.get()
			EL = self.cor2_lin.get()
			cbody = [AZ, EL, 'AZEL']	

		#start linear scan as a thread
		thread = threading.Thread(target=scan.linearScan, args=(location, cbody, numAzScans, MinAz, MaxAz, gaz, gel, c))
		thread.daemon = True
		thread.start()

	def horizontal(self):
		#function to start a horzontal scan around a celestial target

		#get observer location from global configurations
		location = global_location
		#get celestial target
		cbody = self.cbody_hor.get()
		#number of sweeps to do around target for each azimuthal scan(back and forth is 2)
		numAzScans = int(self.numAzScans_hor.get())
		#minimum and maximum az/el for horizontal scan
		MinAz = float(self.MinAz_hor.get())
		MaxAz = float(self.MaxAz_hor.get())
		MinEl = float(self.MinEl.get())
		MaxEl = float(self.MaxEl.get())
		#step size for changing elevation
		stepSize = float(self.stepSize.get())

		if cbody == 'RADEC Sky-Coord':
			#get radec values for sky location target
			RA = self.cor1_hor.get()
			DEC = self.cor2_hor.get()
			cbody = [RA, DEC, 'RADEC']  

		if cbody == 'AZEL Sky-Coord':
			AZ = self.cor1_hor.get()
			EL = self.cor2_hor.get()
			cbody = [AZ, EL, 'AZEL']		      

		#star horizontal scan as thread
		thread = threading.Thread(target=scan.horizontalScan, args=(location, cbody, numAzScans, MinAz, MaxAz, MinEl, MaxEl, stepSize, gaz, gel, c))
		thread.daemon = True
		thread.start()

	def moveDist(self,x):
		#function to start relative move

		if x=='+az':
			az=float(self.az.get())
			el=0
		if x=='-az':
			az=-float(self.az.get())
			el=0
		if x=='+el':
			az=0
			el=float(self.el.get())
		if x=='-el':
			az=0
			el=-float(self.el.get())
	
		#start relative move as thread
		thread = threading.Thread(target=moveto.distance, args=(gaz, gel, az, el, c))
		thread.daemon = True
		thread.start()

	#moveto ra-dec displaying option
	def update_moveto(self):
		#function to switch moveto display between azel & radec 

		label=self.mtl1.cget('text')

		#check if label is ra or az
		if label=='az':
			#switch to radec when button is pressed
			self.mtl1.grid_forget()
			self.mtl1=Label(self.inputframe2,text='ra')
			self.mtl1.grid(row=0,column=0,sticky=W)
			self.mtl2.grid_forget()
			self.mtl2=Label(self.inputframe2,text='dec')
			self.mtl2.grid(row=1,column=0,sticky=W)

		if label=='ra':
			#switch to azel when button is pressed
			self.mtl1.grid_forget()
			self.mtl1=Label(self.inputframe2,text='az')
			self.mtl1.grid(row=0,column=0,sticky=W)
			self.mtl2.grid_forget()
			self.mtl2=Label(self.inputframe2,text='el')
			self.mtl2.grid(row=1,column=0,sticky=W)

	def moveTo(self,tag):
		#function to start move to absolute position

		#check if coordinates are az/el or ra/dec
		label=self.mtl1.cget('text')

		#if az/el just carry on
		if label=='az':

			#logic to only move in az or el at one time
			if tag == 'az':
				az = float(self.az2.get())
				el = None
			if tag == 'el':
				az = None
				el = float(self.el2.get())

		# if ra/dec, convert to az/el
		if label=='ra':

			location = global_location

			#logic to only move to ra or dec position
			if tag == 'az':
				ra = float(self.az2.get())
				dec = planets.azel_to_radec(gaz, gel, location)[1]
			if tag == 'el':
				ra = planets.azel_to_radec(gaz, gel, location)[0]
				dec = float(self.el2.get())

			print ra, dec
			az,el=planets.radec_to_azel(ra,dec, location)

		#start absolute move as thread
		thread = threading.Thread(target=moveto.location, args=(gaz, gel, az, el, c))
		thread.daemon = True
		thread.start()

	def nametochan(self, name):
	    #function to convert channel names to channel numbers
	    
	    #names of each channel
	    channels = {
	        'all': 'all', 'H1 Hi AC': 'ch0','H1 Hi DC': 'ch1',
	        'H1 Lo AC': 'ch2','H1 Lo DC': 'ch3','H2 Hi AC': 'ch4',
	        'H2 Hi DC': 'ch5','H2 Lo AC': 'ch6','H2 Lo DC': 'ch7',
	        'H3 Hi AC': 'ch8','H3 Hi DC': 'ch9','H3 Lo AC': 'ch10',
	        'H3 Lo DC': 'ch11','Backend TSS': 'ch12','Amplifier': 'ch13',
	        'Cooler': 'ch14','Calibrator': 'ch15'}
	     
	    channel = channels[name]

	    return channel
			 
	def pplot_thread(self, plotting, canvas, ax1,ax2):
		#function to start real time plotting thread

		acqtelStatus = str(self.acqtelTxt.get('1.0',END))[:3]
		if acqtelStatus == 'OFF':

			#if there is currently a plot running, stop it
			if self.sigthread != None:
				self.plotting = False
				self.sigthread.join()
				self.sigthread = None
			
			#give board time to disconnect
			time.sleep(0.5)
			
			#temporarily stop moniter thread
			self.monitering = False
			self.mthread.join()
			self.monitering = None
			
			#restart moniter thread but without realtime voltage output
			self.monitering = True
			self.mthread = threading.Thread(target=self.moniter,args=())
			self.mthread.start()
			
			if plotting:

				self.plotting = True

				if self.sigthread == None:
				
					#temporarily stop moniter thread
					self.monitering = False
					self.mthread.join()
					self.monitering = None
				
					#restart moniter thread but without realtime voltage output
					self.monitering = True
					self.mthread = threading.Thread(target=self.moniter,args=(True,))
					self.mthread.start()
			
					time.sleep(0.5)
					
					#start real time plotting thread
					self.sigthread = threading.Thread(target=self.pplot,args=(canvas,ax1,ax2))
					self.sigthread.start()
		else:
		  print 'turn off acq_tel first'

	def round_fraction(self, number, res):
		#round number to nearest resolution
		amount = int(number/res)*res
		remainder = number - amount
		return amount if remainder < res/2. else amount+res

	def pplot(self,canvas,ax1,ax2):
		#function to display realtime plotting

		#clean the former plot
		plt.clf()
		canvas.show()

		# Device name as registered with the Windows driver.
		dev=daqDevice('DaqBoard3031USB')
		
		# Input channel number
		name = self.rtvar.get()
		chan = self.nametochan(name)

		if len(chan) < 4:
			chan = int(chan[-1])
		else:
			chan = int(chan[2:])
			
		channel = chan
		
		if channel > 7:
			channel = 256 + channel - 8
			
		# Programmable amplifier with gain of 1.
		gain = daqh.DgainX1

		# Bipolar-voltage differential input, unsigned-integer readout.
		flags = (
			daqh.DafAnalog | daqh.DafUnsigned  # Default flags.
			| daqh.DafBipolar | daqh.DafDifferential  # Nondefault flags.
			)
		
		# max_voltage and bit_depth are device specific.
		# Our device's bipolar voltage range is -10.0 V to +10.0 V.
		max_voltage = 10.0
		# Our device is a 16 bit ADC.
		bit_depth = 16
		
		#plot resolution
		dx = 10.
		#add this as arg later
		#dx = res
		dy = dx/4.
		
		#sky boundaries
		x, y = np.arange(0., 360. + dx, dx), np.arange(0., 90. + dy, dy)
		az, el = np.meshgrid(x, y)
		
		#set up signal matrix to add values to
		z = np.zeros(len(x)*len(y))
		sig = np.reshape(z, (len(y),len(x)))
		sig = ma.masked_where(sig == 0.0, sig)
		
		#set up matrix for keeping track of data points in single bin for averaging
		z2 = np.zeros(len(x)*len(y))
		count = np.reshape(z2, (len(y), len(x)))
		
		i = 0
		epsilon = 1e-6
		
		#change units on plot label
		if chan < 12:
			unit = 'V'
		else:
			unit = 'K'
		
		#real time voltage
		ax2=self.fig.add_subplot(2,1,2)
		plt.xlabel('Time(s)')
		plt.ylabel('%s, %s' % (name, unit))
		plt.grid(True)
		ax2.set_position([0.15, 0.11, 0.7, 0.3])
		
		#az vs. el vs. voltage
		ax1=self.fig.add_subplot(2,1,1)
		plt.axis([x.min(), x.max(), y.min(), y.max()])
		plt.ylabel('Elevation (deg)')
		plt.xlabel('Azimuth (deg)')
		
		time1 = time.time()
		
		while self.plotting:
			
			# Read one sample.
			data = dev.AdcRd(channel, gain, flags)
			# Convert sample from unsigned integer value to bipolar voltage.
			data = data*max_voltage*2/(2**bit_depth) - max_voltage
			#volts = randint(0,10)
			
			#convert to temp for cryo sensors
			if chan == 12:
				data = convert.convert(data, 'i')
			if chan == 13:
				data = convert.convert(data, 'e')
			if chan == 14:
				data = convert.convert(data, 'h')
			if chan == 15:
				data = convert.convert(data, 'l')
			
			#time interval
			time2=time.time()
			t=time2-time1
			ax2.scatter(t,data, c='b', marker='.')
				
			#get pointing information
			AZ, EL = gaz, gel
			
			if EL < 0. or EL > 90.:
				continue
			
			#round pointing info to resolution
			AZ = self.round_fraction(AZ, dx)
			EL = self.round_fraction(EL, dy) 
			
			#find index in matrix corresponding to position
			iel = np.where(abs(el - EL) < epsilon)[0][0]
			iaz = np.where(abs(az.T - AZ) < epsilon)[0][0]
			
			#dont add to data count if masked
			if count[iel][iaz] is ma.masked:
				count.mask[iel][iaz] = False
			
			#count number of data entries for averaging	
			count[iel][iaz] += 1
			
			#assign voltage value to az el position in matrix
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
				sig.mask[iel][iaz] = False
				sig[iel][iaz] = sig[iel][iaz] + data
			
			#take average of all data in one bin				
			Z = sig/count
			
			plt.pcolormesh(az, el, Z)
			
			#keep loop from making infinite colorbars
			if i == 0:
				cb = plt.colorbar(label = '%s, %s' % (name, unit))
			else:
				cb.remove()
				cb = plt.colorbar(label = '%s, %s' % (name, unit))
				plt.clim(Z.min(), Z.max())

			canvas.draw()

			if i < 1:
				i += 1	

		#save figure when you end loop
		path='../data_acquisition/plots/live_plots'
		os.chdir(path)
		cwd=os.getcwd()
		fname=str(time.strftime('%Y%m%d%H%M%S'))
		plt.savefig(os.path.join(cwd,fname+'.png'))
		txtname='signal'+fname
		np.savetxt(txtname+'.txt',sig)
		os.chdir('../../../telescope_control')

	def stop(self):
		#function to stop motion
		print('stopping motion...')
		c('STX')
		c('STY')
	
	def motor(self):
		#function to turn motor on and off

		status = str(self.motorTxt.get('1.0',END))
		print len(status)
		#print status[0], ',', status[1], ',', status[2]
		on = status[:2]
		off = status[:3]

		#if its on, turn it off
		if on == 'ON':
			c('MO')
			self.motorTxt.delete('1.0', END)
			self.motorTxt.insert('1.0', 'OFF')
			print 'motor off'

		#if its off, turn it on
		elif off == 'OFF':
			c('SH')
			self.motorTxt.delete('1.0', END)
			self.motorTxt.insert('1.0', 'ON')  
			print 'motor on'

		
	def exit(self):
		#function to close gui

		#if there is currently a thread running, stop it
		if self.sigthread != None:
			self.plotting = False
			self.sigthread.join()
			self.sigthread = None
		if self.mthread != None:
			self.monitering = False
			self.mthread.join()
			self.monitering = None

		#If galil is on this will stop motion before closing gui
		try:
			#stop any ongoing motion before closing
			c('STX')
			c('STY')
			c('AB')  # abort motion and program
			#c('MO')  # turn off all motors
		except:
			pass

		root.destroy()
		
root = Tk()
root.title("Telescope Control")

b = interface(root)

#start gui
root.mainloop()

try:
	g.GClose() #close connections
	print 'closed galil connections'
except:
	pass


