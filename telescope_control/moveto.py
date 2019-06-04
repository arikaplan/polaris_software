# move from some initial position to a final position

import planets
import config
import sys
sys.path.append('C:/Python27x86/lib/site-packages')
sys.path.append('data_acquisition')
import gclib
import get_pointing as gp
import time

def wait(c):
	#function to stall motion until previous motion is complete

	#MG _BG will read 0.0000 when motor is not moving
	while c('MG _BGA') != '0.0000' or c('MG _BGB') != '0.0000':
		#print c('MG _BGB'), c('MG _SCB')
		pass


def location(az1, el1, az, el, c):
	#function to move to absolute location
	
  
	try:

		c = c
		######################################

		# deg to ct conversion for each motor
		degtoctsAZ = config.degtoctsAZ
		degtoctsEl = config.degtoctsEl 

		#offset between galil and beam
		offsetAz = gp.galilAzOffset 
		offsetEl = gp.galilElOffset 

		#where you are currently
		P1AZ, P1El = az1 * degtoctsAZ, el1 * degtoctsEl
		print('AZ_0:', az1, 'Elev_0:', el1)

		# make position 2 = position 1 for unselected axis
		if az == None:
			az = az1
		if el == None:
			el =el1
		
		#keep telescope from pointing below horizon
		#if el < 0. or el > 90.:
		#	print('Warning, %.2f deg elevation is below the horizon, your going to break the telescope...' % el)
		#	return 

		#convert new coordinates to cts
		P2AZ = az % 360 * degtoctsAZ
		P2El = el % 360 * degtoctsEl
		
		#azimuth scan settings
		azSP = config.azSP # speed
		azAC = config.azAC # acceleration 
		azDC = config.azDC # deceleration
		
		azD = (P2AZ - P1AZ) # distance to desired az
		print 'requested distance of move (AZ): ', azD/degtoctsAZ
		
		#make it rotate the short way round
		if azD > 180. * degtoctsAZ:
			azD = azD - 360.*degtoctsAZ

		if azD < -180. * degtoctsAZ:
			azD = 360. * degtoctsAZ + azD

		#elevation settings
		elevSP = config.elevSP # x degrees/sec
		elevAC = config.elevAC # acceleration 
		elevDC = config.elevDC # deceleration

		elevD = (P2El - P1El) # distance to desired elev
		print 'requested distance of move (El): ', elevD/degtoctsEl

		#gclib/galil commands to move az motor
		c('SPA=' + str(azSP)) #speed, cts/sec
		c('ACA=' + str(azAC)) #speed, cts/sec
		c('DCA=' + str(azDC)) #speed, cts/sec
		c('PRA=' + str(azD)) #relative move

		#gclib/galil commands to move elevation motor
		c('SPB=' + str(elevSP)) #elevation speed
		c('ACB=' + str(elevAC)) #speed, cts/sec
		c('DCB=' + str(elevDC)) #speed, cts/sec
		c('PRB=' + str(elevD)) #relative move

		print('Moving to object location')
		time.sleep(0.4)
		c('BGA') #begin az motion 

		#wait till az axis is done moving
		wait(c)

		#if it hasnt reached its intended position, 
		#its because I stopped it and the function should end        
		if c('MG _SCA') != '1.0000':
			return
		time.sleep(0.4)
		c('BGB') # begin el motion

		#wait for el motor to finish moving
		wait(c)

		#if it hasnt reached its intended position, 
		#its because I stopped it and the function should end
		if c('MG _SCB') != '1.0000':
			return

		print(' done.')
	 
		del c #delete the alias

	###########################################################################
	# except handler
	###########################################################################  
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)

	return

def distance(az1, el1, az, el, c):
  #function to move relative distance
  
  try:

	print('Moving now...')

	c = c
	######################################

	# deg to ct conversion for each motor
	degtoctsAZ = config.degtoctsAZ
	degtoctsEl = config.degtoctsEl

	#offset between galil and beam
	offsetAz = gp.galilAzOffset 
	offsetEl = gp.galilElOffset 
	
	#where you are currently
	P1AZ, P1El = az1 * degtoctsAZ, el1 * degtoctsEl
	print('AZ_0:', az1, 'Elev_0:', el1)

	#keep telescope from pointing below horizon
	#if ((el1 + el) % 360.) < 0. or ((el1 + el) % 360.) > 90.:
	#	#print Elev_0, el, Elev_0 + el
	#	print('Warning, this elevation is below the horizon, your going to break the telescope...')
	#	return 
	
	#convert distance coordinates to cts
	P2AZ = az  * degtoctsAZ
	P2El = el  * degtoctsEl

	#azimuth scan settings
	azSP = config.azSP # 90 deg/sec
	azAC = config.azAC # acceleration 
	azDC = config.azDC # deceleration

	azD = P2AZ # distance to desired az
	
	#elevation settings
	elevSP = config.elevSP # x degrees/sec
	elevAC = config.elevAC # acceleration  
	elevDC = config.elevDC # deceleration 
 
	elevD = P2El # distance to move elev by
	
	#gclib/galil commands to move az motor
	c('SPA=' + str(azSP)) #speed, cts/sec
	c('ACA=' + str(azAC)) #speed, cts/sec
	c('DCA=' + str(azDC)) #speed, cts/sec
	c('PRA=' + str(azD)) #relative move

	#gclib/galil commands to move elevation motor
	c('SPB=' + str(elevSP)) #elevation speed
	c('ACB=' + str(elevAC)) #speed, cts/sec
	c('DCB=' + str(elevDC)) #speed, cts/sec
	c('PRB=' + str(elevD)) #relative move

	print(' Starting Motion...')

	c('BGA') #begin az motion 

	#wait for az motor to finish moving
	wait(c)

	#if it hasnt reached its intended position, 
	#its because I stopped it and the function should end
	if c('MG _SCA') != '1.0000':
		return

	c('BGB') # begin el motion

	#wait for el motor to finish moving
	wait(c)

	#if it hasnt reached its intended position, 
	#its because I stopped it and the function should end
	if c('MG _SCB') != '1.0000':
		return

	print(' done.')
 
	del c #delete the alias

  ###########################################################################
  # except handler
  ###########################################################################  
  except gclib.GclibError as e:
	print('Unexpected GclibError:', e)
  
  return

if __name__=="__main__":  
	
	g = gclib.py()
	g.GOpen('10.1.2.245 --direct -s ALL')
	c = g.GCommand

	az = 90
	el = 0

	#location(az, el, c)
	distance(az, el, c)
	