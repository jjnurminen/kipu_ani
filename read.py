# -*- coding: utf-8 -*-
"""
Created on Wed Jun 01 15:02:43 2016

@author: hus20664877
"""

import glob
import matplotlib.pyplot as plt
import numpy as np

DATA_PATH = "C:/Users/HUS20664877/projects/kipu_ani/data"


fn = DATA_PATH + "/" + "21_160216.txt"


def procline(li):
    """ Takes one line, returns tuple:
    (time, events, energy, ani, animean, quality)
    or None if line cannot be parsed """
    lis = li.split('\t')
    lis = [s.strip() for s in lis]        
    if not len(lis) == 7:
        return None
    time = lis[0]
    if not (len(time) == 8 and time[2] == ':'):  # check for correct time string
        return None
    events = lis[1].strip()
    energy = float(lis[2])
    ani = int(lis[3])
    animean = int(lis[4])
    quality = float(lis[5])
    return (time, events, energy, ani, animean, quality)

def ani_array(lines):
    """ Makes a numpy array from ani file.
    Columns: energy, ani, animean, quality """
    ar = None
    for li in lines:
        lip = procline(li)
        if lip:
            (time, events, energy, ani, animean, quality) = lip
            vals = [energy, ani, animean, quality]
            if ar is not None:            
                ar = np.vstack((ar, vals))
            else:
                ar = np.array(vals)
    return ar
        

plt.figure()
#for fn in glob.glob(DATA_PATH + '/' + '*txt'):
print(fn)
f = open(fn, 'r')
lines = f.readlines()
ar1 = ani_array(lines)        
plt.plot(ar1[:,1])
plt.show()
raw_input('press enter...')


    
    

