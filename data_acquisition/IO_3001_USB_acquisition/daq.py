import sys
import ctypes as ct
from ctypes import wintypes as wt
from ctypes.util import find_library
from daqh import *

#initialize Daqx.dll
dll = find_library('daqx64')
daq = ct.OleDLL(dll)

class deviceProps(ct.Structure):
    """
    This class emulates a C struct for the device properties calls
    """
    _fields_ = [("deviceType", ct.c_ulong),
                ("basePortAddress", ct.c_ulong),
                ("dmaChannel", ct.c_ulong),
                ("socket", ct.c_ulong),
                ("interruptLevel", ct.c_ulong),
                ("protocol", ct.c_ulong),
                ("alias", ct.c_char*64),
                ("maxAdChannels", ct.c_ulong),
                ("maxDaChannels", ct.c_ulong),
                ("maxDigInputBits", ct.c_ulong),
                ("maxDigOutputBits", ct.c_ulong),
                ("maxCtrChannels", ct.c_ulong),
                ("mainUnitAdChannels", ct.c_ulong),
                ("mainUnitDaChannels", ct.c_ulong),
                ("mainUnitDigInputBits", ct.c_ulong),
                ("mainUnitDigOutputBits", ct.c_ulong),
                ("mainUnitCtrChannels", ct.c_ulong),
                ("adFifoSize", ct.c_ulong),
                ("daFifoSize", ct.c_ulong),
                ("adResolution", ct.c_ulong),
                ("daResolution", ct.c_ulong),
                ("adMinFreq", ct.c_float),
                ("adMaxFreq", ct.c_float),
                ("daMinFreq", ct.c_float),
                ("daMaxFreq", ct.c_float)]

class daqDeviceListT(ct.Structure):
    """
    This class emulates a C struct for the device name
    """
    _fields_ = [("devicename", ct.c_char * 64)]

#Device Initialization Functions

def GetDeviceCount():
    """Returns the number of currently configured devices"""

    deviceCount = ct.c_int(0)
    deviceCountpnt = ct.pointer(deviceCount)
    daq.daqGetDeviceCount(deviceCountpnt)

    return deviceCount.value

def GetDeviceList():
    """Returns a list of currently configured device names"""

    devices = []
    count = GetDeviceCount()
    countpnt = ct.pointer(ct.c_int(count))
    devlist = (daqDeviceListT*count)() #Iterable ctypes array

    daq.daqGetDeviceList(devlist, countpnt)

    for i in devlist:
        devices.append(i.devicename) #So the function returns a python type

    return devices

def GetDriverVersion():
    """Retrieves the revision level of the driver currently in use"""

    version = wt.DWORD(1)
    pversion = ct.pointer(version)
    daq.daqGetDriverVersion(pversion)

    return version.value

def GetDeviceProperties(deviceName):
    """Returns the properties for a specified device"""

    properties = {}

    deviceNamepnt = ct.c_char_p(deviceName)
    devProps = deviceProps()
    devicePropspnt = ct.pointer(devProps)
    err = daq.daqGetDeviceProperties(deviceNamepnt,devicePropspnt)
    if err != 0:
        raise DaqError(err)

    #Rather than return a class, device properties are put into
    # a python dictionary
    for i in dir(devProps):
        if not i.startswith('_'):
            val = getattr(devProps, i)
            properties[i]=val

    return properties

#Error Handling
class DaqError(Exception):

    def __init__(self, errcode):
        self.errcode = errcode
        self.msg = FormatError(errcode)
        self.args = (self.errcode, self.msg)

    def __str__(self):
        return '%i ' % self.errcode + self.msg

    def __getitem__(self,key):
        return self.args[key]

def FormatError(errNum):
    """Returns the text-string equivalent for the specified error condition code"""

    msg = (ct.c_char*64)() #Messages at minimum is 64 characters

    daq.daqFormatError(errNum, ct.byref(msg))

    return msg.value

###Handle Class definition

class daqDevice():

    def __init__(self, deviceName):

        #Turn off the dll error handler to allow for python exceptions
        daq.daqSetDefaultErrorHandler(None)
        self.deviceName = deviceName
        pdeviceName = ct.c_char_p(deviceName)
        self.handle = daq.daqOpen(pdeviceName)
        self.props = self.GetDeviceProperties()

    def Online(self):
        """Determines if a device is online"""

        online = ct.c_bool(False)
        onlinepnt = ct.pointer(online)
        err = daq.daqOnline(self.handle, onlinepnt)
        if err != 0:
            raise DaqError(err)

        return online.value

    def Close(self):
        """Used to close a device"""

        err = daq.daqClose(self.handle)
        if err != 0:
            raise DaqError(err)

    def GetDeviceProperties(self):
        """Returns the properties for a specified device"""

        properties = {}

        deviceNamepnt = ct.c_char_p(self.deviceName)
        devProps = deviceProps()
        devicePropspnt = ct.pointer(devProps)
        err = daq.daqGetDeviceProperties(deviceNamepnt,devicePropspnt)
        if err != 0:
            raise DaqError(err)

        #Rather than return a class, device properties are put into
        # a python dictionary
        for i in dir(devProps):
            if not i.startswith('_'):
                val = getattr(devProps, i)
                properties[i]=val

        return properties

    def ADConvert(self, request):
        """Converts returned 16bit integer to a voltage of a Dbk2000 Bipolar no gain"""
        cal = 5.0/(2**16)
        val = request*cal - 2.5
        return val

    #Error handling functions
    def SetErrorHandler(self, function=None):
        """Specifies the routine to call when an error occurs in any function for the specified device"""

        if function == None:
            function = self._ErrorHandler
        funcPrototype = ct.WINFUNCTYPE(ct.c_int, ct.c_int)
        errorFunction = funcPrototype(function)
        #errorFunction = ct.prototype(function)
        err = daq.daqSetErrorHandler(self.handle, errorFunction)
        if err != 0:
            raise DaqError(err)

    def ProcessError(self, errCode):
        """Initiaties an error for processing by the driver"""

        err = daq.daqProcessError(self.handle, errCode)

        if err != 0:
            raise DaqError(err)

    def GetLastError(self):
        """Retrieves the last error condition code registered by the driver"""

        errCode = ct.c_int(0)

        err = daq.daqGetLastError(self.handle, ct.byref(errCode))

        if err != 0:
            raise DaqError(err)

        return errCode.value

    #Event Handling Functions

    def SetTimeout(self, mSecTimeout):
        """Sets the time-out for waiting on either a single event or
            multiple events"""

        mSecTimeout = wt.DWORD(mSecTimeout)
        err = daq.daqSetTimeout(self.handle, mSecTimeout)

        if err != 0:
            raise DaqError(err)

    def WaitForEvent(self, event):
        """Waits on a specific event to occur on the specified event"""

        err = daq.daqWaitForEvent(self.handle, event)

        if err != 0:
            raise DaqError(err)

    #ADC Acquisition Functions

    def AdcSetAcq(self, mode, preTrigCount = 0, postTrigCount = 0):
        """Configures the acquisition mode and the pre- and post-trigger scan durations"""

        if preTrigCount != None:
            preTrigCount = wt.DWORD(preTrigCount)
        if postTrigCount != None:
            postTrigCount = wt.DWORD(postTrigCount)

        err = daq.daqAdcSetAcq(self.handle, mode, preTrigCount, postTrigCount)

        if err != 0:
            raise DaqError(err)

    def AdcSetTrig(self, triggerSource, rising, level, hysteresis, channel):
        """Configures the device for enhanced triggering"""

        level = wt.WORD(level)
        hysteresis = wt.DWORD(hysteresis)
        channel = wt.DWORD(channel)

        err = daq.daqAdcSetTrig(self.handle, triggerSource, rising, level,
                hysteresis, channel)

        if err != 0:
            raise DaqError(err)

    def AdcSoftTrig(self):
        """Used to send a software trigger command to the device"""

        err = daq.daqAdcSoftTrig(self.handle)

        if err != 0:
            raise DaqError(err)

    #ADC Direct-to-Disk

    def AdcSetDiskFile(self, filename, openMode, preWrite):
        """Sets a destination file for ADC data transfers.  ADC direct-to-disk
        transfers will be directed to the specified disk file"""

        preWrite = wt.DWORD(preWrite)

        err = daq.daqAdcSetDiskFile(self.handle, filename, openMode, preWrite)

        if err != 0:
            raise DaqError(err)


    #ADC Rate Functions

    def AdcSetRate(self, mode, state, reqValue):
        """Configures the acquisition scan rate"""

        reqValue = ct.c_float(reqValue)
        actValue = ct.c_float(0.0)
        pactValue = ct.pointer(actValue)

        err = daq.daqAdcSetRate(self.handle, mode, state, reqValue, pactValue)

        if err != 0:
            raise DaqError(err)

        return actValue.value

    #Utility Functions

    def GetInfo(self, chan, whichInfo):
        """Retrieves hardware information for the specified device"""

        chan = ct.c_int(chan)
        info = ct.c_float(0)
        pinfo = ct.pointer(info)
        err = daq.daqGetInfo(self.handle, chan, whichInfo, pinfo)

        if err != 0:
            raise DaqError(err)

        return info.value

    def GetHardwareInfo(self, whichInfo):
        """Retrieves hardware information for the specified device"""

        info = ct.c_float(0.0)
        pinfo = ct.pointer(info)
        err = daq.daqGetHardwareInfo(self.handle, whichInfo, pinfo)

        if err != 0:
            raise DaqError(err)

        return info.value

    #Custom ADC Aquisition Functions

    def AdcSetScan(self, channels, gains, flags):
        """Configures an aquisition scan group consisting of multiple channels"""

        chanCount = len(channels)
        if type(flags) != list:
            flags = [flags]

        #Making ctypes iterable arrays

        chan_array = (wt.DWORD * chanCount)()
        gain_array = (wt.DWORD * chanCount)()
        flag_array = (wt.DWORD * chanCount)()

        #Take the values of a python list and put them in a Ctypes array
        for i in range(chanCount):
            chan_array[i] = channels[i]
        for i in range(chanCount):
            gain_array[i] = gains[i]
        for i in range(chanCount):
            flag_array[i] = flags[i]

        pchan_array = ct.pointer(chan_array)
        pgain_array = ct.pointer(gain_array)
        pflag_array = ct.pointer(flag_array)

        err = daq.daqAdcSetScan(self.handle, pchan_array, pgain_array, pflag_array,
                          wt.DWORD(chanCount))
        if err != 0:
            raise DaqError(err)

    def AdcGetScan(self, num_channels):
        """Reads the current scan group, which consists of all configured\
            channels"""

        channels,gains,flags = [],[],[]

        #Iterable Ctypes array and pointers to them
        chan_array = (wt.DWORD*num_channels)()
        pchan_array = ct.pointer(chan_array)
        gain_array = (wt.DWORD*num_channels)()
        pgain_array = ct.pointer(gain_array)
        flag_array = (wt.DWORD*num_channels)()
        pflag_array = ct.pointer(flag_array)

        chanCount = wt.DWORD(num_channels)
        pchanCount = ct.pointer(chanCount)

        err = daq.daqAdcSetScan(self.handle, pchan_array, pgain_array, pflag_array, pchanCount)
        if err != 0:
            raise DaqError(err)

        #Take a ctypes array and make a list.
        for i in gain_array:
            gains.append(i)
        for i in flag_array:
            flags.append(i)
        for i in chan_array:
            channels.append(i)

        vals = {'Channels' : channels, 'Gains' : gains,
                'Flags' : flags, 'Channelcount' : chanCount}
        return vals

    def AdcSetFreq(self, freq):
        """Calculates and sets the frequency of the interal scan pacer clock of
            the device using the frequency specified in Hz
        """

        freq = ct.c_float(freq)

        err = daq.daqAdcSetFreq(self.handle, freq)

        if err != 0:
            raise DaqError(err)

    def AdcSetRate(self, mode, state, reqValue):
        """Configures the acquisition scan rate using the selected device's
            built-in acquisition pacer clock.
        """

        reqValue = ct.c_float(reqValue)
        actualValue = ct.c_float(0.0)
        pactualValue = ct.pointer(actualValue)

        err = daq.daqAdcSetRate(self.handle, mode, state, reqValue, pactualValue)

        if err != 0:
            raise DaqError(err)

        return actualValue.value


    #One-Step ADC functions

    def AdcRd(self, chan, gain, flags, convert = None):
        """Takes a single reading from the given local A/D channel using a software trigger"""

        sample = ct.c_long(0)
        psample = ct.pointer(sample)

        err = daq.daqAdcRd(self.handle, chan, psample, wt.DWORD(gain),
                     flags)
        if err != 0:
            raise DaqError(err)

        #Allow values to be converted through one call of the function
        #Or just return the value from the daqboard
        if convert == None:
            sample = sample.value
        else:
            sample = convert(sample.value)

        return sample

    def AdcRdScan(self, startChan, endChan, gain, flags, convert = None):
        """Immediately activates a software trigger to acquire one scan on each channel

            The scan begins with startChan and ends with endChan"""

        #Buffer length is always the number of channels
        bufLength = endChan - startChan + 1
        buf = (wt.WORD * bufLength)()
        pbuf = ct.pointer(buf)

        err = daq.daqAdcRdScan(self.handle, wt.DWORD(startChan), wt.DWORD(endChan),
                         pbuf, wt.DWORD(gain), flags[0])

        if err != 0:
            raise DaqError(err)

        vals = []
        #Convert return values using a function passed to convert
        #or just return the bit values from the daqboard
        if convert == None:
            vals = list(buf)
        else:
            vals = map(convert, buf)

        return vals

    #ADC Acquisition Trigger

    def SetTriggerEvent(self, trigSource, trigSensitivity, channel, gainCode,
                        flags, channelType, level, variance, event):
        """Sets an acquisition trigger start event or stop event"""

        if level != None:
            level = ct.c_float(level)

        if variance != None:
            variance = ct.c_float(variance)

        err = daq.daqSetTriggerEvent(self.handle, trigSource, trigSensitivity,
                               wt.DWORD(channel), wt.DWORD(gainCode), wt.DWORD(flags), channelType,
                               level, variance, event)

        if err != 0:
            raise DaqError(err)

    #ADC Transfer Buffer
    def AdcTransferBufData(self, scanCount, chanCount, bufMask):
        """Requests a transfer of scanCount scans from the driver allocated buffer
            to the linear data retrieval buffer (buf)"""

        buf = (wt.WORD * (scanCount*chanCount))()
        pbuf = ct.pointer(buf)

        scanCount = wt.DWORD(scanCount)

        retCount = wt.DWORD(0)
        pretCount = ct.pointer(retCount)

        err = daq.daqAdcTransferBufData(self.handle, pbuf, scanCount, bufMask, pretCount)

        if err != 0:
            raise DaqError(err)

        return list(buf), retCount.value

    def AdcTransferSetBuffer(self, transferMask, scanCount, buf = 1):
        """Configure transfer buffer for acquired data"""

        #Buffer has a length of the number of scans
        if buf:
            buf = (wt.WORD * scanCount)()
            pbuf = ct.pointer(buf)
        else:
            pbuf = None

        scanCount = wt.DWORD(scanCount)
        err = daq.daqAdcTransferSetBuffer(self.handle, pbuf, scanCount, transferMask)

        if err != 0:
            raise DaqError(err)

        return buf

    def AdcTransferStart(self):
        """Initiates an ADC acquisition transfer"""

        err = daq.daqAdcTransferStart(self.handle)

        if err != 0:
            raise DaqError(err)

    def AdcTransferStop(self):
        """Stops a current ADC buffer transfer, if one is active"""

        daq.daqAdcTransferStop(self.handle)

    def AdcTransferGetStat(self):
        """Retrieves the current state of an acquisition transfer"""

        active = wt.DWORD(0)
        retCount = wt.DWORD(0)
        pactive = ct.pointer(active)
        pretCount = ct.pointer(retCount)

        err = daq.daqAdcTransferGetStat(self.handle, pactive, pretCount)
        if err != 0:
            raise DaqError(err)

        a = active.value
        return {'active':a & DaafAcqActive,
                'triggered':a & DaafAcqTriggered,
                'transfer': a & DaafTransferActive,
                'retCount':retCount.value}

    #ADC Acquisition Control

    def AdcArm(self):
        """Arms an ADC acquisition by enabling the currently defined ADC"""

        err = daq.daqAdcArm(self.handle)

        if err != 0:
            raise DaqError(err)

    def AdcDisarm(self):
        """Disarms an ADC acquisition, if one is currently active"""

        err = daq.daqAdcDisarm(self.handle)

        if err != 0:
            raise DaqError(err)

    #One step DAC functions

    def DacWt(self, deviceType, chan, dataVal):
        """Sets the output value of a local or expansion DAC channel"""

        #Very specific to the daqboard2k series...should be fixed
        #Setup so you can just pass a voltage in.
        if dataVal >= 10.0:
            dataVal = 65535
        if dataVal <= -10.0:
            dataVal = 0
        else:
            dataVal = (dataVal+10.0)/(20.0/65535)

        err = daq.daqDacWt(self.handle, deviceType, chan, wt.WORD(int(dataVal)))

        if err != 0:
            raise DaqError(err)

if __name__ == '__main__':
    print GetDeviceList()
    dev = daqDevice('DaqBoard2K0')
    dev.AdcSetScan([0,1],[DgainX1,DgainX64],[DafBipolar,DafSingleEnded])
    for k,v in dev.AdcGetScan(2):
        print k, v