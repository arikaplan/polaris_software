import sys
import time
import traceback

from Phidget22.Devices.TemperatureSensor import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
from PhidgetHelperFunctions import *
sys.path.append('C:\\Program Files\\Phidgets\\Phidget22\\')
import time

"""
In order to ask the phidget for data, you have to, while the program is running,
use the function getTemperature() on the object 'ch'.
This would look something like:
ch.getTemperature()
"""

def attach_handler(self):
    # event handler for when the phidget is attached.
    ph = self
    try:
        ph.getChannelClassName()
        ph.getDeviceSerialNumber()
        ph.getChannel()
        ph.setTemperatureChangeTrigger(0.0)
    except PhidgetException as e:
        print("\nError in Attach Event:")
        DisplayError(e)
        traceback.print_exc()
        return


def error_handler(self, error_code, error_string):
    sys.stderr.write("[Phidget Error Event] -> " + error_string + " (" + str(error_code) + ")\n")


def main():
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
        ch.setOnAttachHandler(attach_handler)  # sets attach and error handlers
        ch.setOnErrorHandler(error_handler)
        try:
            ch.openWaitForAttachment(5000)  # waits for phidget attachment
        except PhidgetException as e:
            PrintOpenErrorMessage(e, ch)
            raise EndProgramSignal("Program Terminated: Open Failed")
        # I used input to have it wait (and not terminate), but I am not sure
        # if you will be able to poll the program while it is waiting for input
        temp = ch.getTemperature()
        print temp
        return temp
        #input('Press any key to end')
    except PhidgetException as e:
        sys.stderr.write("\nExiting with error(s)...")
        DisplayError(e)
        traceback.print_exc()
        print("Cleaning up...")
        ch.setOnTemperatureChangeHandler(None)
        ch.close()
        return 1
    '''
    except EndProgramSignal as e:
        print(e)
        print("Cleaning up...")
        ch.setOnTemperatureChangeHandler(None)
        ch.close()
        return 1
    '''

if __name__=='__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print t2-t1
