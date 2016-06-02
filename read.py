# -*- coding: utf-8 -*-
"""

parse & plot ANI cold water immersion data

@author: Jussi (jnu@iki.fi)
"""

from __future__ import print_function

import re
import glob
import matplotlib.pyplot as plt
import numpy as np
import datetime
import dateutil


DATA_PATH = "C:/Users/HUS20664877/projects/kipu_ani/data"


def not_a_number(str):
    """ Return true if string cannot be interpreted as a number """
    try:
        float(str), int(str)
    except ValueError:
        return True
    return False
   
def procline(li):
    """ Takes one line, returns tuple:
    (time, events, energy, ani, animean, quality)
    or None if line cannot be parsed """
    # this is to work around irregularly formatted lines:
    # item separator can be either 2 or more whitespace chars OR a single tab    
    lis = re.split('\s\s+|\t', li)
    lis = [s.strip() for s in lis]
    #print(lis)
    if not len(lis) in [6,7]:
        return None
    time = lis[0]
    # check for time string
    if not (len(time) == 8 and time[2] == ':' and time[5] == ':'):
        return None
    if len(lis) == 7:  # we have an event
        events = lis[1].strip()
        lis.pop(1)
    else:
        events = None
    energy = float(lis[1])
    ani = int(lis[2])
    animean = int(lis[3])
    quality = float(lis[4])
    if events:
        assert not_a_number(events)
    assert ani >= 0 and ani <= 100
    assert animean >= 0 and animean <= 100    
    return (time, events, energy, ani, animean, quality)

def ani_array(lines):
    """ Makes a numpy array from ani file,
    with columns: time (s) (from start of file), energy, ani, animean, quality.
    returns index of experiment start time + the array """
    ar = None
    t0 = None
    parsed_a_line = False
    t_exp_start = None
    for ind, li in enumerate(lines):
        if li.strip() == '':  # ignore blank lines
            continue
        lip = procline(li)
        if lip:
            (time, events, energy, ani, animean, quality) = lip
            timep = dateutil.parser.parse(time)
            if not parsed_a_line:
                t0 = timep   # file start time
            # indicates experiment start (hand immersion)
            if events == 'ALKU' or events == 'ALOITUS':
                t_exp_start = (timep-t0).seconds
            t = (timep - t0).seconds
            vals = [t, energy, ani, animean, quality]
            if ar is not None:            
                ar = np.vstack((ar, vals))
            else:
                ar = np.array(vals)
            parsed_a_line = True
        else:
            # unparseable line in middle of file?
            if parsed_a_line:
                # ignore errors on last line
                if ind != len(lines) - 1:
                    raise ValueError('Cannot parse line: ' + li)
    if not t_exp_start:
        raise ValueError('Cannot parse t_exp_start')
    # experiment start in seconds (hand in water) relative to file start
    return t_exp_start, ar

T_BEFORE = 20  # sec before t0
T_AFTER = 160  # sec after t0
EXCLUDE_ZEROS = True  # exclude curves that fall to zero (errors?)

""" Plot t vs ANI curves """
plt.figure()
parse_errors = 0
files = glob.glob(DATA_PATH + '/' + '*txt')
nfiles = len(files)
avg = np.zeros(T_BEFORE+T_AFTER)
navg = 0
n_curves_zero = 0 
for fn in files:
    print('Parsing:', fn)
    f = open(fn, 'r')
    lines = f.readlines()
    try:
        t_start_ind, ar1 = ani_array(lines)        
    except ValueError as e:
        print(e)
        parse_errors += 1
        continue
    tvec = ar1[t_start_ind-T_BEFORE:t_start_ind+T_AFTER, 0]
    tvec -= tvec[0]  # plot starts from zero
    ani_data = ar1[t_start_ind-T_BEFORE:t_start_ind+T_AFTER, 2]
    # do not plot or include in average, if curve falls to zero
    if min(ani_data) == 0:
        n_curves_zero += 1
        if EXCLUDE_ZEROS:
            continue
    avg += ani_data
    navg += 1
    plt.plot(tvec, ani_data)
    plt.draw()
    #plt.waitforbuttonpress()

avg /= navg
plt.plot(tvec, avg, linewidth=3, color='k')
plt.axvline(T_BEFORE, linestyle='--', color='k')
plt.xlabel('Time (s)')
plt.ylabel('ANI index')
print('\nTotal files:', nfiles)
print('Files with parse errors:', parse_errors)
print('Curves with ANI falling to zero:', n_curves_zero)
print('Plotted curves:', navg)
    


    
    

