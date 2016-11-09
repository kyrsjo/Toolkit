#!/usr/bin/env python
from __future__ import division

import os

import numpy as np

max_tau = 4
taus = []
for value in range(1, max_tau + 1):
    taus.append(value)

min_turn = 150
max_turn = 200

turns = []
for value in range(min_turn + 1, max_turn + 1):
    turns.append(value)
    
turns_const = []
for value in range(2, min_turn + 1):
    turns_const.append(value)

def decay(voltage, turn, min_turn, tau):
    return float(voltage*np.exp(-(turn - min_turn)/tau))

voltages = dict(zip(['voltage'], [1]))


for key, val in voltages.items():
    outfile = '{}'.format(key)
    try:
        os.remove(outfile)
    except OSError:
        pass
    f = open(outfile, 'w')
    f.write('1 0.0\n')
    for turn_const in turns_const:
        f.write('%.0f %.15f\n'%(turn_const, val))
    for turn in turns:
        f.write('%.0f %.15f\n'%(turn, decay(val, turn, min_turn, max_tau)))
    f.close()

