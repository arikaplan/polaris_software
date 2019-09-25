import glob
import os
import sys


##keep format like "2017-05-16"; otherwise it returns "5" when you type "05"
def date_conv(year,month,day):
    m=[str(year),str(month),str(day)]
    for i in range(len(m)):
        if len(m[i])<2:
            m[i]=m[i].zfill(2)
    return m

##keep format like 01-02
def time_conv(st_hour,st_minute,ed_hour,ed_minute):
    n=[str(st_hour),str(st_minute),str(ed_hour),str(ed_minute)]
    for i in range(len(n)):
        if len(n[i])<2:
            n[i]=n[i].zfill(2)
    return n
    
'''            
##select a staring-time and an ending-time, it returns dat files in between
def select_dat(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute):
    
    #searching all dat files under selected path
    all_fname = glob.glob(fpath+'/data/'+yrmoday+'/*.dat')

    ftime=time_conv(st_hour,st_minute,ed_hour,ed_minute)  

    star=ftime[0]+ftime[1]
    end=ftime[2]+ftime[3]


    #search files between selected starting-time and ending-time
    sub_fname=[ i for i in all_fname
                if i[-12:][:4]>=star and i[-12:][:4]<=end]
    return sub_fname
'''
##select a staring-time and an ending-time, it returns dat files in between
def select_dat(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute, demod=True):

    #searching all dat/h5 files under selected path
    all_fname_demod = glob.glob(fpath+'demod_data/'+yrmoday+'/*.h5')
    all_fname = glob.glob(fpath+'/data/'+yrmoday+'/*.dat')
    ftime=time_conv(st_hour,st_minute,ed_hour,ed_minute)  
      
    star=ftime[0]+ftime[1]
    end=ftime[2]+ftime[3]

    #search files between selected starting-time and ending-time
    sub_fname=[ i for i in all_fname
                if i[-12:][:4]>=star and i[-12:][:4]<=end]

    if demod == False:
        return sub_fname
    
    sub_fname_demod = []
    sub_fname_mod = []
    for f in range(len(sub_fname)):

        #only include complete files
        if os.stat(sub_fname[f]).st_size == 10752000:
            #find the demodulated file from the time stampt corresponding to dat file

            fname = sub_fname[f][:16] + 'demod_data' + sub_fname[f][21:-4]+'.h5'
            
            #if demodulate file exists, add it
            if fname in all_fname_demod:
                sub_fname_demod.append(fname)
            #if demodulated file doesnt exist add undemodulated file
            else:
                sub_fname_mod.append(sub_fname[f])

    return sub_fname_demod, sub_fname_mod
    
##select a staring-time and an ending-time, it returns h5 files in between
def select_h5(fpath,yrmoday,st_hour,st_minute,ed_hour,ed_minute):

    #searching all hdf5 files under selected path
    all_fname=glob.glob(fpath+'/pointing_data/'+yrmoday[4:6]+'-'+yrmoday[6:8]+'-'+yrmoday[0:4]+'/*.h5')
    ftime=time_conv(st_hour,st_minute,ed_hour,ed_minute)
    
    star=ftime[0]+"-"+ftime[1]
    end=ftime[2]+"-"+ftime[3]

    sub_fname=[ i for i in all_fname
                if i[-11:][:5]>=star and i[-11:][:5]<=end]

    return sub_fname

if __name__=="__main__":
    fpath='../polaris_data/'

    yrmoday='20190520'
    print(len(select_dat(fpath,yrmoday,19,00,24,00)[0]))
    #print len(select_dat(fpath,yrmoday,19,00,24,00)[1])

    #print len(select_h5(fpath,yrmoday,19,00,24,00))


