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


DATA_PATH = "data"


def not_a_number(str):
    """ Return true if string cannot be interpreted as a number """
    try:
        float(str), int(str)
    except ValueError:
        return True
    return False

def is_time(timestr):
    """ Check for valid time string, i.e. hh:mm:ss """
    tli = timestr.split(':')
    if len(tli) != 3:
        return False
    try:
        hms = [int(s) for s in tli]
    except ValueError:
        return False
    if hms[0] in range(24) and hms[1] in range(60) and hms[2] in range(60):
        return True
    else:
        return False

def procline(li):
    """ Takes one line, returns tuple:
    (time, events, energy, ani, animean, quality)
    or None if line cannot be parsed """
    # this is to work around irregularly formatted lines:
    # item separator can be either 2 or more whitespace chars OR a single tab
    # (not a single space, since event strings may contain a space...)
    lis = re.split('\s\s+|\t', li)
    lis = [s.strip() for s in lis]
    if not len(lis) in [6,7]:   # weird result of split, cannot parse
        return None
    time = lis[0]
    events = None
    # try to handle invalid time strings
    if not is_time(time):
        if len(time) > 8:  # time and event glued together?
            if is_time(time[:8]):  
                print('warning: overlong time string, splitting into time and event:', time)
                time = time[:8]
                events = time[8:]
            else:   # overlong time string, cannot parse
                return None
        else:   # normal or short time string, but cannot parse
            return None
    elif len(lis) == 7:  # valid time, followed by event
        events = lis[1].strip()
        lis.pop(1)  # so that indices below are always valid
    try:
        energy = float(lis[1])
        ani = int(lis[2])
        animean = int(lis[3])
        quality = float(lis[4])
    except ValueError:
        return None
    if events:
        assert not_a_number(events)
        events = events.upper()
    assert ani >= 0 and ani <= 100
    assert animean >= 0 and animean <= 100    
    return (time, events, energy, ani, animean, quality)

def ani_array(lines):
    """ Makes a numpy array from ani output lines,
    with columns: time (s) (from start of file), energy, ani, animean, quality.
    returns index of experiment start time + the array """
    EXP_START = ['ALKU', 'ALOITUS']  # magic strings indicating experiment start
    ar = []
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
            if events in EXP_START:
                t_exp_start = (timep-t0).seconds
            t = (timep - t0).seconds
            vals = [t, energy, ani, animean, quality]
            ar.append(vals)
            parsed_a_line = True
        else:
            # unparseable line in middle of file?
            if parsed_a_line:
                # ignore errors on last line
                if ind != len(lines) - 1:
                    #raise ValueError('Cannot parse line: ' + li)
                    print('warning: skipping unparseable line: ' + li)
    if not t_exp_start:
        raise ValueError('Cannot parse t_exp_start')
    # experiment start in seconds (hand in water) relative to file start
    nar = np.array(ar)
    if not np.all(np.diff(nar[:,0]) == 1):
        print('warning: time not uniformly sampled, delta_t stats: ', end='')
        print(np.unique(np.diff(nar[:,0]), return_counts=True))
    return t_exp_start, nar

T_BEFORE = 20  # sec before t0
T_AFTER = 160  # sec after t0
EXCLUDE_ZEROS = True  # exclude curves that fall to zero (errors?)
MAX_LINES = 800  # do not read more data than this
FN_EXCLUDE = 'exclude.txt'

""" Read exclude file """
f = open(FN_EXCLUDE, 'r')
fn_exclude = [fn.strip() for fn in f.readlines()]  # rm whitespace


""" Plot t vs ANI curves """
plt.figure()
parse_errors = 0
list_excluded = 0
files = glob.glob(DATA_PATH + '/' + '*txt')
nfiles = len(files)
avg = np.zeros(T_BEFORE+T_AFTER)
navg = 0
tvec = None
n_curves_zero = 0 

for fn in files[:-1]:
    fnbase = os.path.splitext(os.path.basename(fn))[0]
    if fnbase in fn_exclude:
        print('Name in exclude list, skipping:', fn)
        list_excluded += 1
        continue
    print('Parsing:', fn)
    f = open(fn, 'r')
    lines = []
    for k in range(MAX_LINES):
        lines.append(f.readline())
    try:
        t_start_ind, ar1 = ani_array(lines)
    except ValueError as e:
        print('Cannot parse', fn, ':')
        print(e)
        parse_errors += 1
        continue
    if ar1.shape[0] < t_start_ind + T_AFTER:
        raise ValueError('Not enough data was read! Increase MAX_LINES')
    # time vector may be unique for each curve due to nonuniform sampling
    tvec = ar1[t_start_ind-T_BEFORE:t_start_ind+T_AFTER, 0]
    tvec -= tvec[0]  # plot starts from zero time
    ani_data = ar1[t_start_ind-T_BEFORE:t_start_ind+T_AFTER, 2]
    # do not plot or include in average, if curve falls to zero
    if min(ani_data) == 0:
        n_curves_zero += 1
        if EXCLUDE_ZEROS:
            print('Data falls to zero, excluding file')
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
print('\nTotal files found:', nfiles)
print('Excluded by list:', list_excluded)
print('Files with parse errors:', parse_errors)
print('Curves with ANI falling to zero:', n_curves_zero)
print('Plotted curves:', navg)
   
#if __name__ == '__main__':
#    ani_plot()
    


        
    
