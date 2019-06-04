#script for linear and horizontal scan patterns
import config
import moveto
import planets
import sys
sys.path.append('C:/Python27x86/lib/site-packages')
import gclib
#from datetime import datetime, timedelta
import time
import get_pointing as gp

def wait(c):
		#function to stall motion until previous motion is complete

		#MG _BG will read 0.0000 when motor is not moving
		while c('MG _BGA') != '0.0000' or c('MG _BGB') != '0.0000':
			#print c('MG _BGA'), c('MG _SCB')
			pass

def linearScan(location, cbody, numAzScans, MinAz, MaxAz, az1, el1, c):
	
	try:

		c = c

		# deg to ct conversion for each motor
		degtoctsAZ = config.degtoctsAZ
		degtoctsEl = config.degtoctsEl
		
		#azimuth scan settings
		azSP = config.azSP # az scan speed, 90 deg/sec
		azAC = config.azAC # acceleration 
		azDC = config.azDC # deceleration

		#gclib/galil commands to set az axis motor motion
		c('ACA=' + str(azAC)) #acceleration, cts/sec
		c('DCA=' + str(azDC)) #deceleration, cts/sec
	
		MinCT = MinAz * degtoctsAZ # min az scanned to
		MaxCT = MaxAz * degtoctsAZ # max az scanned to

		#find az, el of various sky objects
		az, el = planets.getpointing(location, cbody)

		moveto.location(az1, el1, az + MinAz, el, c)
		az1 = (az + MinAz) % 360
		el1 = el % 360

		#loop through back and forth azimuth scans
		for i in range(0, numAzScans):

			if i != 0:
				#find az, el of various sky objects
				az, el = planets.getpointing(location, cbody)

			print('%s az, el: ' % cbody, az, el)

			#keep telescope from pointing below horizon
			if el < 0. or el > 90.:
				print('Warning, %.2f deg elevation is below the horizon, your going to break the telescope...' % el)
				return 

			#forward scan
			if (i % 2) == 0:

				if i != 0:
					time.sleep(0.3)
					moveto.location(az1, el1, az + MinAz, el, c)

				#gclib/galil commands to move az axis motor
				c('SPA=' + str(azSP)) #speed, cts/sec
				c('PRA=' + str(MaxCT - MinCT)) #relative move
				print(' Starting forward pass: ' + str(i + 1))
				time.sleep(0.3)
				c('BGA') #begin az motion

				#wait till az axis is done moving
				wait(c)

				#if it hasnt reached its intended position, 
				#its because I stopped it and the function should end
				if c('MG _SCA') != '1.0000':
					return

				print(' done.')
				az1 = (az + MaxAz) % 360
			#backwards scan
			else:

				az, el = planets.getpointing(location, cbody)
				time.sleep(0.3)
				moveto.location(az1, el1, az + MaxAz, el, c)

				#gclib/galil commands to move az axis motor
				c('SPA=' + str(azSP)) #speed, cts/sec
				c('PRA=' + str(MinCT - MaxCT)) #relative move, 1024000 cts = 360 degrees
				print(' Starting backward pass: ' + str(i))
				time.sleep(0.3)
				c('BGA') #begin az motion
				
				#wait till az axis is done moving
				wait(c)

				#if it hasnt reached its intended position, 
				#its because I stopped it and the function should end
				if c('MG _SCA') != '1.0000':
					return

				print(' done.')
				az1 = (az + MinAz) % 360
		print 'finished scan'
			
		del c #delete the alias

	###########################################################################
	# except handler
	###########################################################################  
	except gclib.GclibError as e:

		print('Unexpected GclibError:', e)
	
	return

def horizontalScan(location, cbody, numAzScans, MinAz, MaxAz, MinEl, MaxEl, stepSize, az1, el1, c):
	
	try:

		c = c
		
		# deg to ct conversion for each motor
		degtoctsAZ = config.degtoctsAZ
		degtoctsEl = config.degtoctsEl
		
		#azimuth scan settings
		azSP = config.azSP # az scan speed, 90 deg/sec
		azAC = config.azAC # acceleration 
		azDC = config.azDC # deceleration

		#gclib/galil commands to set az axis motor motion
		c('ACA=' + str(azAC)) #acceleration, cts/sec
		c('DCA=' + str(azDC)) #deceleration, cts/sec
	
		MinCT = MinAz * degtoctsAZ # min az scanned to
		MaxCT = MaxAz * degtoctsAZ # max az scanned to

		#number of elevations to scan at, rounds to nearest integer
		#numElScans = int(round(((MaxEl - MinEl)/stepSize)))
		numElScans = int(round(((MaxEl - MinEl + stepSize)/stepSize)))

		#find az, el of various sky objects
		az, el = planets.getpointing(location, cbody)

		moveto.location(az1, el1, az + MinAz, el + MinEl, c)
		az1 = (az + MinAz) % 360
		el1 = (el + MinEl) % 360

		#loop through back and forth az scans at different elevations
		for j in range(0, numElScans):
			print('starting horizontal scan: ', j + 1)
			for i in range(0, numAzScans):

				if i != 0:
					#find az, el of varios sky objects
					az, el = planets.getpointing(location, cbody) 
			 	
				print('%s az, el: ' % cbody, az, el)

				#keep the telescope from pointing below the horizon
				if el + MinEl < 0.:
					print('Warning, %.2f deg min elevation is below the horizon, your going to break the telescope...' % (el + MinEl))
					return
		
				#keep the telescope from pointing below the horizon
				if el + MaxEl > 90.:
					print('Warning, %.2f deg max elevation is below the horizon, your going to break the telescope...' % (el + MaxEl))
					return

				#forward scan
				if (i % 2) == 0:

					if j != 0 or i != 0:
						time.sleep(0.4)
						moveto.location(az1, el1, az + MinAz, el + MinEl + j*stepSize, c)
						el1 = (el + MinEl + j*stepSize) % 360

					#gclib/galil commands to move az axis motor
					c('SPA=' + str(azSP)) #speed, cts/sec
					c('PRA=' + str(MaxCT - MinCT)) #relative move
					print(' Starting forward pass: ', i)
					time.sleep(0.4)
					c('BGA') #begin az motion

					#wait till az axis is done moving
					wait(c)

					#if it hasnt reached its intended position, 
					#its because I stopped it and the function should end
					if c('MG _SCA') != '1.0000':
						print 'stopped stepped el scan'
						return

					print(' done.')

					az1 = (az + MaxAz) % 360
				#backwards scan
				else:

					az, el = planets.getpointing(location, cbody)
					time.sleep(0.4)
					moveto.location(az1, el1, az + MaxAz, el + MinEl + j*stepSize, c)
					el1 = (el + MinEl + j*stepSize) % 360

					#gclib/galil commands to move az axis motor
					c('SPA=' + str(azSP)) #speed, cts/sec
					c('PRA=' + str(MinCT - MaxCT)) #relative move
					print(' Starting backward pass: ', i)
					time.sleep(0.4)
					c('BGA') #begin az motion

					#wait till az axis is done moving
					wait(c)

					#if it hasnt reached its intended position, 
					#its because I stopped it and the function should end
					if c('MG _SCA') != '1.0000':
						print 'stopped stepped el scan'
						return

					print(' done.')

					az1 = (az + MinAz) % 360

		print 'finished scan'	

		del c #delete the alias

	###########################################################################
	# except handler
	###########################################################################  
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
	 
	return

def azScan2(tscan, elevations, az1, el1, c):
	
	try:

		c = c
		
		# deg to ct conversion for each motor
		degtoctsAZ = config.degtoctsAZ
		degtoctsEl = config.degtoctsEl

		#offset between galil and beam
		offsetAz = gp.galilAzOffset 
		offsetEl = gp.galilElOffset
		
		#azimuth scan settings
		azSP = config.azSP # az scan speed, 90 deg/sec
		azAC = config.azAC # acceleration 
		azDC = config.azDC # deceleration
		
		#gclib/galil commands to set az axis motor motion
		c('JGA=' + str(azSP)) #speed, cts/sec
		c('ACA=' + str(azAC)) #acceleration, cts/sec
		c('DCA=' + str(azDC)) #deceleration, cts/sec
		
		#elevation settings
		elevSP = config.elevSP # x degrees/sec
		elevAC = config.elevAC # acceleration 
		elevDC = config.elevDC # deceleration
		
		#gclib/galil commands to set az axis motor motion
		c('SPB=' + str(elevSP)) #elevation speed
		c('ACB=' + str(elevAC)) #acceleration, cts/sec
		c('DCB=' + str(elevDC)) #deceleration, cts/sec
		
		#initial position
		P1AZ = az1 * degtoctsAZ
		P1El = el1 * degtoctsEl
		print('AZ:', az1, 'Elev:', el1)

		if elevations == None:
			elevations = [el1]

		#maybe add this back in 
		#for i in range(0, iterations):

		#loop through iterations
		for e in elevations:

			moveto.location(az1, el1, None, float(e), c)

			#set start time
			#st = datetime.utcnow()
			st = time.time()
			#set current time to start time
			ct = st
			#duration of azimuth scan
			#dt = timedelta(0, tscan) 
			dt = tscan*60*60
			print(' Starting az Scan at elevation: ' + str(e))
			
			c('BGA') #begin motion
			#scan in azimuth while current time < start time + duration
			while ct < st + dt:
				#update current time
				#ct = datetime.utcnow()
				ct = time.time()

				#if it hasnt reached its intended position, 
				#its because I stopped it and the function should end
				if c('MG _BGA') == '0.0000':
					return


			c('ST') # stop when duration has passed

			#wait till az axis is done moving
			wait(c)

			print(' done with elevation %s.' % e)
		
		del c #delete the alias

	###########################################################################
	# except handler
	###########################################################################  
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
		
	return
	 
def helicalScan(tscan, lim1, lim2, az1, el1, c):
	
	try:

		c = c
		
		degtoctsEl = config.degtoctsEl
		offsetEl = gp.galilElOffset
		
		if lim1 < 0. or lim2 >  90.:
				print 'Warning, %.2f deg elevation is below the horizon, your going to break the telescope...' % P2El + deltaEl
				return
		
		#moving to starting elevation
		if el1 < lim1:
			print 'moving to starting elevation %f' % lim1
			moveto.location(az1, el1, None, lim1, c)
		
		if el1 > lim2:
			print 'moving to starting elevation %f' % lim2
			moveto.location(az1, el1, None, lim2, c)
	
		# deg to ct conversion for each motor
		degtoctsAZ = config.degtoctsAZ
		degtoctsEl = config.degtoctsEl

		#offset between galil and beam
		offsetAz = gp.galilAzOffset 
		offsetEl = gp.galilElOffset
		
		#azimuth scan settings
		azSP = config.azSP # az scan speed, 90 deg/sec
		azAC = config.azAC # acceleration 
		azDC = config.azDC # deceleration
		
		#gclib/galil commands to set az axis motor motion
		c('JGA=' + str(azSP)) #speed, cts/sec
		c('ACA=' + str(azAC)) #acceleration, cts/sec
		c('DCA=' + str(azDC)) #deceleration, cts/sec
		
		#elevation settings
		elevSP = config.elevSP # x degrees/sec
		elevAC = config.elevAC # acceleration 
		elevDC = config.elevDC # 
		
		elevD = (lim2 - lim1)*degtoctsEl # distance to desired elev
		elevDsmall = (lim2 - el1) * degtoctsEl # distance to desired elev
		
		#gclib/galil commands to set az axis motor motion
		c('SPB=' + str(elevSP)) #elevation speed
		c('ACB=' + str(elevAC)) #acceleration, cts/sec
		c('DCB=' + str(elevDC)) #deceleration, cts/sec
		
		#if your inside the specified range move to starting position
		if el1 < lim2 or el1 > lim1:
			c('PRB=' + str(elevDsmall))
		#if your at starting point just start moving
		else:
			c('PRB=' + str(elevD))
		
		#set start time
		st = time.time()
		#set current time to start time
		ct = st
		#duration of  scan
		dt = tscan * 60.  # scan time in minutes

		print(' Starting Helical Scan')

		c('BGA') #begin az motion
		c('BGB') # begin el motion

		#scan in azimuth while current time < start time + duration
		while ct < st + dt:

			if c('MG _SCB') == '1.0000':
				print 'changing direction'
				time.sleep(1.0)
				elevD = -elevD
				c('PRB=' + str(elevD))
				c('BGB')

			#update current time
			ct = time.time()

			#if  az stops moving exit while loop
			if c('MG _BGA') == '0.0000':
				return

		c('STX') # stop when duration has passed
		c('STY')

		print(' done.')
		
		del c #delete the alias

		###########################################################################
		# except handler
		###########################################################################  
	except gclib.GclibError as e:
			print('Unexpected GclibError:', e)

	return

 
#old method
def azScan(tscan, iterations, deltaEl, az1, el1, c):
	
	try:

		c = c
		
		# deg to ct conversion for each motor
		degtoctsAZ = config.degtoctsAZ
		degtoctsEl = config.degtoctsEl

		#offset between galil and beam
		offsetAz = gp.galilAzOffset 
		offsetEl = gp.galilElOffset
		
		#azimuth scan settings
		azSP = config.azSP # az scan speed, 90 deg/sec
		azAC = config.azAC # acceleration 
		azDC = config.azDC # deceleration
		
		#gclib/galil commands to set az axis motor motion
		c('JGA=' + str(azSP)) #speed, cts/sec
		c('ACA=' + str(azAC)) #acceleration, cts/sec
		c('DCA=' + str(azDC)) #deceleration, cts/sec
		
		#elevation settings
		elevSP = config.elevSP # x degrees/sec
		elevAC = config.elevAC # acceleration 
		elevDC = config.elevDC # deceleration
		elevD = deltaEl * degtoctsEl # move elevation x degrees each iteration
		
		#gclib/galil commands to set az axis motor motion
		c('SPB=' + str(elevSP)) #elevation speed
		c('ACB=' + str(elevAC)) #acceleration, cts/sec
		c('DCB=' + str(elevDC)) #deceleration, cts/sec
		c('PRB=' + str(elevD)) # change the elevation by x deg
		
		#initial position
		P1AZ = az1 * degtoctsAZ
		P1El = el1 * degtoctsEl
		print('AZ:', az1, 'Elev:', el1)

		#loop through iterations
		for i in range(0, iterations):

			#set start time
			#st = datetime.utcnow()
			st = time.time()
			#set current time to start time
			ct = st
			#duration of azimuth scan
			#dt = timedelta(0, tscan) 
			dt = tscan

			print(' Starting az Scan: ' + str(i + 1))
			
			c('BGA') #begin motion

			#scan in azimuth while current time < start time + duration
			while ct < st + dt:

				#update current time
				#ct = datetime.utcnow()
				ct = time.time()

				#if it hasnt reached its intended position, 
				#its because I stopped it and the function should end
				if c('MG _BGA') == '0.0000':
					return


			c('ST') # stop when duration has passed

			#wait till az axis is done moving
			wait(c)

			print(' done.')
			
			if el1 + (i+1)*deltaEl < 0. or el1 + (i+1)*deltaEl > 90.:
				print 'Warning, %.2f deg elevation is below the horizon, your going to break the telescope...' % P2El + deltaEl
				return

			#change elevation for next az scan
			if i < iterations - 1:
				print('changing elevation')
				
				c('BGB') #begin el motion
				
				#wait till el axis is done moving
				wait(c)

				#if it hasnt reached its intended position, 
				#its because I stopped it and the function should end
				if c('MG _SCB') != '1.0000':
					return

				print('done')
		
		del c #delete the alias

	###########################################################################
	# except handler
	###########################################################################  
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
		
	return
	 
	 

if __name__ == "__main__":
	g = gclib.py()
	g.GOpen('10.1.2.245 --direct -s ALL')
	c = g.GCommand

	tscan = np.inf
	lim1 = 15
	lim2 = 80
	az1, el1 = gp.getAzEl() [:2]
	helicalScan(tscan, lim1, lim2, az1, el1, c)