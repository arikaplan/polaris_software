from hashlib import sha1
from shutil import copyfile
import ctypes
import os

DEST = "Q:\Asteroid\Lab Testing\Laser DAQ Plotting"
def shafile(filename):
    with open(filename, "rb") as f:
        return sha1(f.read()).hexdigest()

def isHidden(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result
    
def sync(basepath,addedpath):
    path = basepath + addedpath
    for filename in os.listdir(path):
        if not isHidden(path+"\\"+filename):
            if os.path.isfile(path+"\\"+filename):
                if os.path.isfile(DEST+addedpath+"\\"+filename):
                    if shafile(path+"\\"+filename) != shafile(DEST+addedpath+"\\"+filename):
                        copyfile(path+"\\"+filename, DEST+addedpath+"\\"+filename)
                        print path+"\\"+filename+" updated on server."
                else:
                    copyfile(path+"\\"+filename, DEST+addedpath+"\\"+filename)
                    print path+"\\"+filename+" created on server."
            else:
                if not os.path.isdir(DEST+addedpath+"\\"+filename):
                    os.mkdir(DEST+addedpath+"\\"+filename)
                sync(basepath, addedpath+"\\" + filename)
            
sync('C:\\dstar','')