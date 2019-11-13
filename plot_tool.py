import sys
#sys.path.append('D:/software_git_repos/greenpol')
sys.path.append('C:/Python27/Lib/site-packages/')
sys.path.append('C:/Python27x86/lib/site-packages')
sys.path.append('data_acquisition/IO_3001_USB_acquisition')
#sys.path.append('data_acquisition')
#sys.path.append('telescope_control')
sys.path.append('VtoT')
import os
#sys.path.append('VtoT')
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
import numpy.ma as ma
import warnings
import subprocess
import convert

class interface:

	def __init__(self, master):#, interval = 0.2): 

		mainFrame = Frame(master)
		mainFrame.pack()

		outputframe = Frame(mainFrame)
		outputframe.pack()

		########## plot data ##########

		self.outputframe1 = Frame(outputframe)
		self.outputframe1.pack()

		self.plotButton = Button(self.outputframe1, 
			text='Plot', command=self.plot)
		self.plotButton.grid(row = 0, column = 0, sticky=W)
	
		self.l1 = Label(self.outputframe1, text='Date')
		self.l1.grid(row = 0, column = 2, sticky =W)
	
		self.date = Entry(self.outputframe1, width = 10)
		self.date.insert(END, '2017-06-02')
		self.date.grid(row = 0, column = 3)

		self.l2 = Label(self.outputframe1, text='From')
		self.l2.grid(row = 0, column = 4, sticky=W)

		self.beg = Entry(self.outputframe1, width = 5)
		self.beg.insert(END, '18-17')
		self.beg.grid(row = 0, column = 5)

		self.l3 = Label(self.outputframe1, text='To')
		self.l3.grid(row = 0, column = 6, sticky=W)
	
		self.end = Entry(self.outputframe1, width = 5)
		self.end.insert(END, '22-07')
		self.end.grid(row = 0, column = 7, sticky=W)

		self.l4 = Label(self.outputframe1, text='yyyy-mm-dd')
		self.l4.grid(row = 1, column = 3, sticky=W)
	
		self.l5 = Label(self.outputframe1, text='HH-MM')
		self.l5.grid(row = 1, column = 5, sticky=W)

		self.l6 = Label(self.outputframe1, text='HH-MM')
		self.l6.grid(row = 1, column =7, sticky=W)

		############# plot drop down menu ###############
		#For Move Plot
		self.choice1=['az','el', 'H1', 'H2', 'H3', 'Backend TSS', 
						 'Amplifier', 'Cooler', 'Calibrator', 'x tilt', 'y tilt', 'gpstime', 'Phidget Temp','sci_data']
		self.bar1=StringVar()
		self.bar1.set(self.choice1[0])
		self.option1=OptionMenu(self.outputframe1,self.bar1,*self.choice1,command=self.update_ch)
		self.option1.grid(row=0,column=1,sticky=W)     

		############# exit frame ###############

		self.quitButton = Button(mainFrame, text='Exit GUI', command=self.exit)
		self.quitButton.pack(side=LEFT)
	
		#load latest saved entry settings
		#try:
		path='configurations/plot_tool_config/'
		os.chdir(path)
		all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
		latest_subdir = max(all_subdirs, key=os.path.getmtime)
		os.chdir(latest_subdir)
		list_of_files = glob.glob('*.txt')
		latest_file = max(list_of_files, key=os.path.getctime)
		fname=os.path.splitext(latest_file)[0]
		self.read(fname=fname,date=latest_subdir)
		os.chdir('../../../')

		#except:
		#	pass
	
	def write_txt(self):
		#function to save current plot times to file

		data={'Plot':{'Date':self.date.get(),
				  'From':self.beg.get(),
				  'To':self.end.get()}}

		date = strftime("%Y-%m-%d")
		time=strftime("%H-%M-%S")
		fpath='configurations'
		#fpath='D:/software_git_repos/greenpol/telescope_control/configurations'
		os.chdir(fpath)

		folder='plot_tool_config'
		#this is the first file being created for that time
		if not os.path.exists(folder):
			os.makedirs(folder)
		os.chdir(folder)

		#this is the first file being created for that time
		if not os.path.exists(date):
			os.makedirs(date)
		os.chdir(date)
		
		#get label for save file
		fname='latestconfig'
		
		
		with open(fname+'.txt', 'w') as handle:
			pickle.dump(data,handle)

			print 'Recording a history config at '+ date+'/'+time +','+ 'naming: '+fname

		os.chdir('../../../')

	def read_txt(self):
		#function to find saved configurations for given label and time

		fname=self.backup_l.get()
		date=self.date_l.get()
		self.read(fname,date)
		
	def read(self,fname,date):
		#function to load saved entries from a previous save into gui entry ouput


		#read all the saved entries
		try:

			with open(fname+'.txt', 'r') as handle:
				data=pickle.loads(handle.read())
			#print data['Move to Location']
			print 'Loading a history config of: '+ date +','+ 'naming: '+ fname

			##plot
			self.date.delete(0,'end')
			self.date.insert(END,data['Plot']['Date'])
			self.beg.delete(0,'end')
			self.beg.insert(END,data['Plot']['From'])
			self.end.delete(0,'end')
			self.end.insert(END,data['Plot']['To'])

		except IOError:
			print 'No Labels Found'
		
	####channel options for sci_data
	def update_ch(self,value):
		#function to update drop down menu output based on whether you are plotting acq_tel data 

		if value==self.choice1[13]:

			self.choice2=['all', 'H1 Hi AC','H1 Hi DC','H1 Lo AC','H1 Lo DC','H2 Hi AC','H2 Hi DC'
			,'H2 Lo AC','H2 Lo DC','H3 Hi AC','H3 Hi DC','H3 Lo AC','H3 Lo DC','Backend TSS'
			,'Amplifier','Cooler','Calibrator']
	
			self.bar2=StringVar()
			self.bar2.set('H1 Hi AC')
			self.option2=OptionMenu(self.outputframe1,self.bar2,*self.choice2)
			self.option2.grid(row=2,column=1,sticky=W)

			self.choice3=['T','Q','U','PSD(T)','PSD(Q)','PSD(U)']
			self.bar3=StringVar()
			self.bar3.set('T')
			self.option3=OptionMenu(self.outputframe1,self.bar3,*self.choice3)
			self.option3.grid(row=1,column=1,sticky=W)

			self.choice4=['sig v az', 'sig v gpstime', 'sig v az v el', 'sig v az v rev']
			self.bar4=StringVar()
			self.bar4.set('sig v az')
			self.option4=OptionMenu(self.outputframe1,self.bar4,*self.choice4)
			self.option4.grid(row=3,column=1,sticky=W)

		else:
			try:
				self.option2.grid_forget()
				self.option3.grid_forget()
				self.option4.grid_forget()
			except AttributeError:
				pass

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

	def plot(self):
		#function to plot saved data
	
		#close anything that is already open
		plt.close('all')
	
		fpath='../polaris_data/'

		#get start and end time for plotting
		var1 = self.bar1.get()
		date = self.date.get()
		beg = self.beg.get()
		end = self.end.get()
	
		#parse date into seperate strings
		date = date.split('-')
		year = date[0]
		month = date[1]
		day = date[2]
		yrmoday=year+month+day

		#parse time into seperate strings
		time1 = beg.split('-')
		hour1 = str(time1[0])
		minute1 = str(time1[1])
		time2 = end.split('-')
		hour2 = str(time2[0])
		minute2 = str(time2[1])

		#if your not plotting acq_tel data
		if var1 != 'sci_data':

			y=rt.get_h5_pointing(select_h5(fpath,yrmoday,hour1,minute1,
											hour2,minute2))[var1]
		
			t=rt.get_h5_pointing(select_h5(fpath,yrmoday,hour1,minute1,
											hour2,minute2))['gpstime']

			display_pointing = rt.pointing_plot(var1,y,t)

		else:
			#get channel, variable, and plot type
			var2 = self.nametochan(self.bar2.get())
			var3 = self.bar3.get()
			var4 = self.bar4.get()

			#variable and plot type options
			psd=['PSD(T)','PSD(Q)','PSD(U)']
			parameter=['T','Q','U']
			ptype = ['sig v az', 'sig v gpstime','sig v az v el', 'sig v az v rev']
			
			#plot signal vs az for all channels
			if var2=='all' and var3 in parameter and var4 == ptype[0]:
				rt.plotnow_all(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3, xaxis = 'az',
									 st_hour=hour1,st_minute=minute1,
									 ed_hour=hour2,ed_minute=minute2)
			
			#plot signal vs gpstime for all channels
			elif var2=='all' and var3 in parameter and var4 == ptype[1]:
				rt.plotnow_all(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3, xaxis = 'gpstime',
									 st_hour=hour1,st_minute=minute1,
									 ed_hour=hour2,ed_minute=minute2)
			
			#plot power spectral density for all channels
			elif var2=='all' and var3 in psd:
				indx=psd.index(var3)
				var3=parameter[indx]
				rt.plotnow_psd_all(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3,
									 st_hour=hour1,st_minute=minute1,
									 ed_hour=hour2,ed_minute=minute2)
			
			#plot power spectral density for single channel
			elif var2 != 'all' and var3 in psd:
				indx=psd.index(var3)
				var3=parameter[indx]
				rt.plotnow_psd(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3,
									 st_hour=hour1,st_minute=minute1,
									 ed_hour=hour2,ed_minute=minute2)
			
			#cant plot multiple channels on 3D plot	     
			elif var2 == 'all' and (var4 != ptype[0] or ptype[1]):
			  print 'Can only plot one channel at a time for 3D plots'
			  return
			   
			else:
				#plot signal vs azimuth
				if var4 == ptype[0]:
					rt.plotnow(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3, xaxis = 'az',
									 st_hour=hour1,st_minute=minute1,
									 ed_hour=hour2,ed_minute=minute2)
				
				#plot signal vs gpstime
				if var4 == ptype[1]:
					rt.plotnow(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3, xaxis = 'gpstime',
									 st_hour=hour1,st_minute=minute1,
									 ed_hour=hour2,ed_minute=minute2)
				
				#plot signal vs elevation vs azimuth		     
				if var4 == ptype[2]:
					rt.plotnow_azelsig(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3,
								 st_hour=hour1,st_minute=minute1,
								 ed_hour=hour2,ed_minute=minute2)
				
				#plot signal vs revolution vs azimuth
				if var4 == ptype[3]:
					rt.plotnow_azrevsig(fpath=fpath,yrmoday=yrmoday,chan=var2,var=var3,
								 st_hour=hour1,st_minute=minute1,
								 ed_hour=hour2,ed_minute=minute2)

		
	def exit(self):
		#function to close gui

		#save latest plot times
		self.write_txt()

		root.destroy()

		
root = Tk()
root.title("Plot Data")

b = interface(root)

#start gui
root.mainloop()

try:
	g.GClose() #close connections
	print 'closed galil connections'
except:
	pass


