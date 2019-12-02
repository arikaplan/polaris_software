yhimport numpy as np
import sys
import matplotlib.pyplot as plt

def flagging(channel, samples_per_rev):
    '''
    Read time stream and apply flagging
    '''

    tod_len = np.size(channel)
    
    flags = np.ones(tod_len, dtype=bool)


    baseline = np.std(channel)
    baseline = 0.02    

    
    for i in range(int(tod_len/samples_per_rev)):
        i_low  = i*samples_per_rev 
        i_high = i*samples_per_rev + samples_per_rev-1

        sigma  = np.std(channel[i_low:i_high+1])

        threshold = baseline/sigma 
        
        median = np.median(channel[i_low:i_high+1])
                
        mask1  = np.array(np.where(channel[i_low:i_high+1]>median+threshold*sigma)) + i_low
        mask2  = np.array(np.where(channel[i_low:i_high+1]<median-threshold*sigma)) + i_low

                
        flags[mask1] = False
        flags[mask2] = False
                
    return(flags)


def apply_flags(channel,flags,decimation):
    '''
    Apply flags (of down-sampled time-stream) on original time-stream(s).
    '''

    for i in range(np.size(flags)):
        if (flags[i]==False):
            fr = i*decimation
            to = i*decimation + decimation - 1
            print(fr,to)
            channel[fr:to+1] = np.nan

    
