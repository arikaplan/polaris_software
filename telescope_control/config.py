#control paramters
import pickle
import os


def update_config():
    print os.getcwd()
    fpath='../configurations/motion_configuration'
    os.chdir(fpath)
    #function updates configuration parameters to be sent to galil
    with open('config.txt','r') as handle:
        config=pickle.loads(handle.read())

        global global_location
        global_location=config['location']

        # deg to ct conversion for each motor
        global degtoctsAZ 
        degtoctsAZ = config['degtoctsAZ']
        global degtoctsEl 
        degtoctsEl = config['degtoctsEL']
            
        #azimuth scan settings
        global azSP 
        azSP = config['azSP'] * degtoctsAZ # az scan speed, 90 deg/sec
        global azAC
        azAC =  config['azAC'] * degtoctsAZ # acceleration 
        global azDC
        azDC =  config['azDC'] * degtoctsAZ # deceleration

        #elevation settings
        global elevSP
        elevSP = config['elevSP'] * degtoctsEl # x degrees/sec
        global elevAC
        elevAC = config['elevAC'] * degtoctsEl # acceleration 
        global elevDC
        elevDC = config['elevDC'] * degtoctsEl # deceleration

        #offset settings (ffset between encoder and beam)
        global eloffset
        eloffset=config['eloffset']         #updated based on moon crossing 2013/08/02, cofe 10 ghz ch37
        global azoffset
        azoffset=config['azoffset']

    os.chdir('../../telescope_control')
