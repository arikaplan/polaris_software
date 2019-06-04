"""Helper functions that:
- aid in input and output from pickle files
- adding to the comment file
- saving files without overwriting and saving to server
"""

import time
import os
import cPickle

def get_date_filename():
    '''default filename using date and time. Typically unused in current setup
    creates a directory for each day and returns the file string to be used'''    
    now=time.localtime()[0:6]
    dirfmt = "%4d_%02d_%02d"
    dirname = dirfmt % now[0:3]
    filefmt = "%02d_%02d_%02d.pkl"
    filename= filefmt % now[3:6]
    ffilename=os.path.join(dirname,filename)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return(ffilename)    

def addComment(fname, comment, commentfilename = ".\\Laser Ablation Lab Data and Plots\\Raw_Output\\commentlist.txt"):
    """Adds a comment line to the comment file detailing the test to be done, as well as the time it was done at."""
    cf=open(commentfilename,'a')
    cf.writelines(time.strftime("%d %B %Y - %H:%M:%S")+"    "+fname+'    '+comment+'    '+'\n')
    cf.close()
    cf=open(getServerName(commentfilename),'a')
    cf.writelines(time.strftime("%d %B %Y - %H:%M:%S")+"    "+fname+'    '+comment+'    '+'\n')
    cf.close()
    
def saveToPickle(outdata,outfile= None):
    """Creates a pickle of outdata, avoiding overwriting a file if needed"""
    if outfile == None:
        outfile = get_date_filename()
    outfile = ".\\Laser Ablation Lab Data and Plots\\Raw_Output\\" + outfile 
    outfile = handleFilenameConflicts(outfile)
    f=open(outfile,'wb')
    cPickle.dump(outdata,f)
    f.close()
    f=open(getServerName(outfile),'wb')
    cPickle.dump(outdata,f)
    f.close()
    
def readPickle(infile):
    """Reads in a pickle file using cPickle"""
    filename = ".\\Laser Ablation Lab Data and Plots\\Raw_Output\\"+infile
    f = open(filename,'rb')
    data = cPickle.load(f)
    f.close()
    return data
    
def handleFilenameConflicts(filename, initial=True):
    """
    Recursive function that finds a valid name for a designated filename by adding _Run_## to the end to avoid overwriting.
    filename - file to be checked for conflicts, eg c:\\dstar\\Laser Ablation Lab Data and Plots\\Raw_Output\\filedata.pkl
    initial - used to determine which the top level recursive function is. When calling from outside, always set to True.
    returns: a string of the filename to be used to create a file that will not overwrite any others, eg c:\\dstar\\Laser Ablation Lab Data and Plots\\Raw_Output\\filedata_Run_1.pkl"""
    if not os.path.isfile(filename): #No conflicts, return now.
        return filename
    elif '_Run_' in filename: # If the file already has a number after it, we need to try the next number.
        
        l = filename.split('.')  # all this just increments the number and calls this function again.
        end = l[-1]
        filename = l[0]
        for i in range(len(l)-2):
            filename += '.'
            filename += l[i+1]
        filenamecopy = filename
        index = filename.find('_Run_')
        filename = filename[:index]
        num = int(filenamecopy[index+5:])
        filename = handleFilenameConflicts(filename+'_Run_'+str(num+1)+'.'+end,initial=False)
        if initial:
            print "Warning - File already exists. Using filename: " + filename
        return filename
    else: # The file exists, but it doesn't have a name like _Run_# at the end. We just try the file with _Run_1 added to end. 
        l = filename.split('.')  # all this just increments the number and calls this function again.
        end = "." + l[-1]
        filename = l[0]
        print filename
        for i in range(len(l)-2):
            filename += '.'
            filename += l[i+1]
        filename = handleFilenameConflicts(filename+'_Run_1'+end,initial=False)
        if initial:
            print "Warning - File already exists. Using filename: " + filename
        return filename
        
def getServerName(filename):
    """Converts filename to a string filename on the lab server.
       returns a filename starting with Q:\\Asteroid\\Lab Testing\\Laser DAQ Plotting, to save onto server"""
    return "Q:\\Asteroid\\Lab Testing\\Laser DAQ Plotting" + filename[filename.find("\\Laser Ablation Lab Data and Plots"):]