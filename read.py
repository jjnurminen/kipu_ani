# -*- coding: utf-8 -*-
"""
TODO:
input files are irregular (items not always tab separated)
-> use regex for parsing? (2 or more spaces or tab?) + sanity checks
broken file e.g.
C:/Users/HUS20664877/projects/kipu_ani/data/208_261114.txt

@author: Jussi (jnu@iki.fi)
"""

import re
import glob
import matplotlib.pyplot as plt
import numpy as np

DATA_PATH = "C:/Users/HUS20664877/projects/kipu_ani/data"


fn = DATA_PATH + "/" + "21_160216.txt"


def procline(li):
    """ Takes one line, returns tuple:
    (time, events, energy, ani, animean, quality)
    or None if line cannot be parsed """
    # this is to work around irregular files:
    # item separator can be either 2 or more whitespace chars OR a single tab    
    lis = re.split('\s\s+|\t', li)
    lis = [s.strip() for s in lis]
    print lis
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
    """ Makes a numpy array from ani file,
    with columns: energy, ani, animean, quality 
    returns index of zero time + the array """
    ar = None
    t0 = None
    for ind,li in enumerate(lines):
        lip = procline(li)
        print lip
        if lip:
            (time, events, energy, ani, animean, quality) = lip
            if events == 'ALKU' or events == 'ALOITUS':
                t0 = ind
            vals = [energy, ani, animean, quality]
            if ar is not None:            
                ar = np.vstack((ar, vals))
            else:
                ar = np.array(vals)
    return t0, ar
        

plt.figure()
for fn in glob.glob(DATA_PATH + '/' + '*txt'):
    print(fn)
    f = open(fn, 'r')
    lines = f.readlines()
    t0, ar1 = ani_array(lines)        
    plt.plot(ar1[t0:t0+100,1])
    plt.draw()
    plt.waitforbuttonpress()
    


    
    

