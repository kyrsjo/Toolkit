#!/usr/bin/env python
import os
import re
import sys

import collections
import numpy as np

from collections import Counter
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib import rcParams

from util import GetData

simulated_particles = float(sys.argv[1])
bunches = 2748
beam_energy = 700
bunch_energy = beam_energy / bunches

# ------------------------------------------------------------------------------
# Associating name with collimator ID
# ------------------------------------------------------------------------------
infile_2 = 'coll_summary.dat'
get_2 = GetData(infile_2)
data_2 = get_2.data_column(dtype='string')

names_2 = data_2[1]
numbers = data_2[0]

numbers_dict = {}
for i in range(len(names_2)):
    numbers_dict[float(numbers[i])] = names_2[i]

# ------------------------------------------------------------------------------
# Associating name with position
# ------------------------------------------------------------------------------
infile_3 = 'CollPositionsHL.b1.dat'
get_3 = GetData(infile_3)
data_3 = get_3.data_column(dtype='string')

names = data_3[1]
position = data_3[2]

translator_dict = {}
for i in range(len(names)):
    translator_dict[names[i]] = float(position[i])

# Usage: translator_dict[numbers_dict[29]]

# ------------------------------------------------------------------------------
# Curating impacts real
# ------------------------------------------------------------------------------
infile = 'impacts_real.dat'


def is_header(line):
    return re.search(r'#|@|\*|%|\$|&', line) is not None


def get_impacts(infile, column):
    with open(infile, 'r') as data:
        for line in data:
            if is_header(line):
                continue
            line_list = line.strip('\n').split()
            if line_list[7] != 4:
                yield line_list[column]


coll_data = []
start_line = get_impacts(infile, 0)
for line in start_line:
    coll_data.append(translator_dict[numbers_dict[float(line)]])

impacts_dict = Counter(coll_data)

turn_data = []
start_line_t = get_impacts(infile, 9)
for line in start_line_t:
    turn_data.append(line)

turns_dict = Counter(turn_data)

# for i, j in zip(turns_dict.keys(), turns_dict.values()):
#     print i,j

particles_per_bunch = 2.2 * 1e11
normalization_factor = particles_per_bunch / simulated_particles

values = np.asarray(impacts_dict.values())

def get_tcp(infile, column):
    with open(infile, 'r') as data:
        for line in data:
            if is_header(line):
                continue
            line_list = line.strip('\n').split()
            if line_list[7] != 4:
                yield line_list[0], line_list[9]


tcp_data = []
start_line = get_tcp(infile, 0)
for line in start_line:
    tcp_data.append(line)

tcp_losses = []
for i, j in tcp_data:
    if i == '29':
        tcp_losses.append(j)

tcp_dict = collections.OrderedDict(sorted(Counter(tcp_losses).items()))

outfile = 'tcp.txt'
print ' '
print '>> Losses in the TCP per turn, non cumulative:'
with open(outfile, 'w') as f:
    for i, j in zip(tcp_dict.keys(), tcp_dict.values()):
        print i, round(float(j)*100 / simulated_particles,2), \
        '{:.2e}'.format((float(j)/ simulated_particles)*particles_per_bunch*bunches)
        print >> f, i,  round(float(j)*100 / simulated_particles,2)

print ' '
print '>> Losses in the TCP per turn, cumulative:'
percentage_tcp = 0
protons_tcp = 0
for i, j in zip(tcp_dict.keys(), tcp_dict.values()):
    percentage_tcp += float(j)*100 / simulated_particles
    protons_tcp += float(j)/ simulated_particles*particles_per_bunch*bunches
    print i, round(percentage_tcp, 2),'{:.2e}'.format(protons_tcp), \
        round(percentage_tcp*1e-2 * beam_energy, 2)



# tct_data = []
# start_line = get_tct(infile, 0)
# for line in start_line:
#     tct_data.append(line)

tct_losses = []
for i, j in tcp_data:
    if i == '54':
        tct_losses.append(j)

tct_dict = collections.OrderedDict(sorted(Counter(tct_losses).items()))

print ' '
print '>> Losses in the TCT per turn, non cumulative:'
for i, j in zip(tct_dict.keys(), tct_dict.values()):
    print i, round(float(j)*100 / simulated_particles,2), \
    '{:.2e}'.format((float(j)/ simulated_particles)*particles_per_bunch*bunches)

print ' '
print '>> Losses in the TCT per turn, cumulative:'
percentage_tct = 0
protons_tct = 0
for i, j in zip(tct_dict.keys(), tct_dict.values()):
    percentage_tct += float(j)*100 / simulated_particles
    protons_tct += float(j)/ simulated_particles*particles_per_bunch*bunches
    print i, round(percentage_tct, 2),'{:.2e}'.format(protons_tct)


# ------------------------------------------------------------------------------
# Extracting losses in the aperture
# ------------------------------------------------------------------------------


def get_lpi(infile):
    with open(infile, 'r') as data:
        for line in data:
            if is_header(line):
                continue
            line_list = line.strip('\n').split()
            yield line_list[2]


infile_4 = 'LPI_test.s'
if os.stat(infile_4).st_size == 0:
    print '>> No losses in the aperture'
else:
    ap_data = []
    start_line = get_lpi(infile_4)
    for line in start_line:
        ap_data.append(float(line))
    lpi_dict = Counter(ap_data)
    lpi_values = np.asarray(lpi_dict.values())
    aperture_losses = sum(lpi_dict.values()) / simulated_particles

# ------------------------------------------------------------------------------
# Calculation of some parameters
# ------------------------------------------------------------------------------

percentage_lost_tcp = float(impacts_dict[translator_dict[numbers_dict[29]]]) \
    / simulated_particles

total_losses = sum(impacts_dict.values()) / simulated_particles
tct4h_losses = float(impacts_dict[translator_dict[
                     'TCTPH.4L1.B1']]) / simulated_particles
tct4v_losses = float(impacts_dict[translator_dict[
                     'TCTPV.4L1.B1']]) / simulated_particles

print ' '
print '>> Total losses:'
print '>> ' + str(round(total_losses * 100, 2)) + ' % lost in the collimation system'
if os.stat(infile_4).st_size != 0:
    print '>> ' + '{:.2e}'.format(float((aperture_losses * 100))) + ' % lost in the aperture'
print ' '
print '>> Primary:'
print '>> ' + str(round(percentage_lost_tcp * 100, 2)) + ' % lost in the ' + str(numbers_dict[29]) + \
    ', ' + '{:.2e}'.format(float((percentage_lost_tcp *
                                  particles_per_bunch * bunches))) + ' particles for the whole beam'
print '>> Corresponding to ' + str(round(percentage_lost_tcp * beam_energy, 2)) + ' MJ for the whole beam'
print '>> Can withstand 9.2e+11 direct proton impacts or 8 full bunches'
print ' '
print '>> Tertiaries:'
print '>> ' + str(tct4h_losses * 100) + ' % lost in TCTPH.4L1.B1, ' + \
    '{:.2e}'.format(float((tct4h_losses * particles_per_bunch *
                           bunches))) + ' particles for the whole beam'
print '>> ' + str(tct4v_losses * 100) + ' % lost in TCTPV.4L1.B1, ' + \
    '{:.2e}'.format(float((tct4v_losses * particles_per_bunch *
                           bunches))) + ' particles for the whole beam'
print '>> Damage limit is at 1.2e+11 secondary protons impacts'

# ------------------------------------------------------------------------------
# Plotting
# ------------------------------------------------------------------------------
font_spec = {"font.size": 10, }
rcParams.update(font_spec)
rcParams['figure.figsize'] = 4, 2
fig = plt.figure()
ax2 = fig.add_subplot(111)
plt.bar(impacts_dict.keys(), values * normalization_factor, align="center",
        linewidth=0, width=60, color="black", label="Collimation")
if os.stat(infile_4).st_size != 0:
    plt.bar(lpi_dict.keys(), lpi_values * normalization_factor, color="green",
            align="center", linewidth=0, width=60, label="Aperture")
plt.title("Losses from a single bunch, HL-LHC 1.2")
plt.xlabel("Position (m)")
plt.ylabel("Number of protons lost")
plt.xlim([0, 26658.883])
plt.legend(loc='upper left', prop={'size': 6})
ax2.set_yscale('log')
ax2.set_axisbelow(True)
ax2.yaxis.grid(color='gray', linestyle='-', which="minor", linewidth=0.3)

height = max(values * normalization_factor) / 30
text_size = 10
ax2.annotate('IP2', xy=(1, height), xytext=(3332.4, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')
ax2.annotate('IR3', xy=(1, height), xytext=(6664.721, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')
ax2.annotate('IR4', xy=(1, height), xytext=(9997, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')
ax2.annotate('IP5', xy=(1, height), xytext=(13329.28, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')
ax2.annotate('IR6', xy=(1, height), xytext=(16661.7, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')
ax2.annotate('IR7', xy=(1, height), xytext=(20000, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')
ax2.annotate('IP8', xy=(1, height), xytext=(23315.4, height),
             weight='bold', va='bottom', ha='center', size=text_size, color='red')

plt.subplots_adjust(left=0.16, bottom=0.19, right=0.94, top=0.88)
plt.savefig('loss_map.png', dpi=1000)
plt.savefig('loss_map.eps', format='eps', dpi=1000)
plt.clf()
