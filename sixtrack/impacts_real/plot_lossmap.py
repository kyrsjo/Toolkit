#!/usr/bin/python
# ------------------------------------------------------------------------------
# USAGE: plot_lossmap.py B2 core tail
# or: plot_lossmap.py B2 to analyze in place without weights
# ------------------------------------------------------------------------------
import glob
import operator
import os
import re
import sys

import numpy as np
import matplotlib

from collections import defaultdict
from decimal import Decimal
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib import rcParams

from util import GetData


DPI = 300
#DPI = 1000

if len(sys.argv) == 6:
    print ' '
    print '>> Working with core and tail'
    dir_core = sys.argv[4]
    dir_tail = sys.argv[5]
elif len(sys.argv) == 4:
    print ' '
    print '>> Working in current directory'
else:
    print "USAGE: plot_lossmap.py {B1|B2} title getLossTurn (core_dir tail_dir)"
    exit(1)

beam  = sys.argv[1]
title = sys.argv[2]
getLossTurn=int(sys.argv[3])

# ------------------------------------------------------------------------------
# Plot characteristics
# ------------------------------------------------------------------------------
# font = {'family':'serif', 'serif': ['computer modern roman']}
# plt.rc('font',**font)
rcParams['figure.figsize'] = 4, 2
params = {'text.latex.preamble': [r'\usepackage{siunitx}', r'\usepackage{mathrsfs}']}
plt.rcParams.update(params)
rcParams['legend.frameon'] = 'True'
fig = plt.figure()

## Get the normalization
failTurn = 0
if len(sys.argv)==6:
    norm_core = {}
    norm_file = open(os.path.join(dir_core,"normalization.txt"),'r')
    for line in norm_file.xreadlines():
        ls = line.split("=")
        norm_core[ls[0]] = ls[1][:-1]
    norm_file.close()
    norm_tail = {}
    norm_file = open(os.path.join(dir_tail,"normalization.txt"),'r')
    for line in norm_file.xreadlines():
        ls = line.split("=")
        norm_tail[ls[0]] = ls[1][:-1]
    norm_file.close()

    assert norm_core["failTurn"]==norm_tail["failTurn"]
    failTurn = int(norm_core["failTurn"])
elif len(sys.argv)==4:
    norm = {}
    norm_file = open("normalization.txt",'r')
    for line in norm_file.xreadlines():
        ls = line.split("=")
        norm[ls[0]] = ls[1][:-1]
    norm_file.close()

    failTurn = int(norm["failTurn"])

# ------------------------------------------------------------------------------
# Function to deal with core and tail data files
# ------------------------------------------------------------------------------
def get_dist(data_file, dir_core, dir_tail, core_weight, tail_weight):

    if data_file == 'loss_maps.txt':
        col_1 = 1
        col_2 = 3
    elif data_file == 'aperture.txt':
        col_1 = 0
        col_2 = 2

    x = []
    y = []
    if os.path.isfile(dir_core + '/' + data_file) and os.path.isfile(dir_tail + '/' + data_file):
        print ' '
        print '>> File ' + data_file + ' present for core and tail'

        get_core = GetData(dir_core + '/' + data_file)
        data_core = get_core.data_column(dtype='string')
        xc_coll = data_core[col_1]
        yc_coll = data_core[col_2]

        get_tail = GetData(dir_tail + '/' + data_file)
        data_tail = get_tail.data_column(dtype='string')
        xt_coll = data_tail[col_1]
        yt_coll = data_tail[col_2]

        for i, k in zip(xc_coll, yc_coll):
            for j, l in zip(xt_coll, yt_coll):
                if i == j:

                    x.append(float(i))
                    y.append(core_weight * float(k) + tail_weight * float(l))
                    xc_coll.remove(i)
                    yc_coll.remove(k)
                    xt_coll.remove(j)
                    yt_coll.remove(l)

        for i, k in zip(xc_coll, yc_coll):
            x.append(float(i))
            y.append(core_weight * float(k))
        for j, l in zip(xt_coll, yt_coll):
            x.append(float(j))
            y.append(tail_weight * float(l))

    elif os.path.isfile(dir_core + '/' + data_file) == False:
        print ' '
        print '>> File ' + data_file + ' present only for tail'

        get_tail = GetData(dir_tail + '/' + data_file)
        data_tail = get_tail.data_column(dtype='string')
        xt_coll = data_tail[col_1]
        yt_coll = data_tail[col_2]
        for j, l in zip(xt_coll, yt_coll):
            x.append(float(j))
            y.append(tail_weight * float(l))

    elif os.path.isfile(dir_tail + '/' + data_file) == False:
        print ' '
        print '>> File ' + data_file + ' present only for core'

        get_core = GetData(dir_core + '/' + data_file)
        data_core = get_core.data_column(dtype='string')
        xc_coll = data_core[col_1]
        yc_coll = data_core[col_2]
        for j, l in zip(xc_coll, yc_coll):
            x.append(float(j))
            y.append(core_weight * float(l))
    return x, y

# ------------------------------------------------------------------------------
# Different options if core and tail directories are present or not
# ------------------------------------------------------------------------------
ax1 = fig.add_subplot(111)
b1 = {}
b2 = {}
ips = np.linspace(1, 8, 8)

b1_pos = [800, 3332.436584, 6664.7208, 9997.005016,
          13329.28923, 16661.72582, 19994.1624,  23315.37898]
for i, j in zip(ips, b1_pos):
    b1[i] = j

b2_pos = [800, 23326.59898,  19994.1624, 16661.72582,
          13329.28923,  9997.005016,  6664.7208,  3343.656584]
for i, j in zip(ips, b2_pos):
    b2[i] = j


def plot_ip_labels(thedict, height, size):
    for i, j in zip(thedict.keys(), thedict.values()):
        if i == 1 or i == 2 or i == 5 or i == 8:
            my_ip = 'IP'
        if i == 3 or i == 4 or i == 6 or i == 7:
            my_ip = 'IR'
        ax1.annotate(my_ip + str(int(i)), xy=(1, height), xytext=(j, height),
                     weight='bold', va='bottom', ha='center', size=size, color='red')


if len(sys.argv) == 6: #core & tail
    x_coll, y_coll = get_dist('loss_maps.txt', dir_core, dir_tail, 0.95, 0.05)
    x_ap, y_ap = get_dist('aperture.txt', dir_core, dir_tail, 0.95, 0.05)
    plt.bar(x_coll, y_coll, align="center",
            linewidth=0, width=60, color="black", label="Collimation: " + "{:.2E}".format(Decimal(np.sum(y_coll))) + " \%")
    plt.bar(x_ap, y_ap, color="green",
                align="center", linewidth=0, width=60, label="Aperture: " + "{:.2E}".format(Decimal(np.sum(y_ap))) + " \%")
    plt.xlabel("Position (m)")
    plt.ylabel(r'Percentage of bunch lost')
    plt.xlim([0, 26658.883])
    plt.title(title)
    plt.legend(loc='best', prop={'size': 5}).get_frame().set_linewidth(0.5)
    ax1.set_yscale('log')
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(color='gray', linestyle='-', which="minor", linewidth=0.1)

    height = max(y_coll) / 200
    text_size = 5
    if beam == 'B1':
        plot_ip_labels(b1, height, text_size)
    elif beam == 'B2':
        plot_ip_labels(b2, height, text_size)
    else:
        print '>> Please input B1 or B2 as first argument'

    plt.subplots_adjust(left=0.16, bottom=0.19, right=0.94, top=0.88)
    plt.savefig('loss_map.png', dpi=DPI)
    plt.savefig('loss_map.eps', format='eps', dpi=DPI)
    plt.clf()


elif len(sys.argv) == 4: #This folder
    files = glob.glob('*.txt')
    for txt in files:
        if txt == 'loss_maps.txt':
            print ' '
            print '>> File ' + txt + ' present'
            get = GetData(txt)
            data = get.data_column(dtype='string')
            x_coll = np.asarray(data[1], dtype='float64')
            y_coll = np.asarray(data[3], dtype='float64')
        elif txt == 'aperture.txt':
            print ' '
            print '>> File ' + txt + ' present'
            get = GetData(txt)
            data = get.data_column(dtype='string')
            x_ap = np.asarray(data[0], dtype='float64')
            y_ap = np.asarray(data[2], dtype='float64')
    # ------------------------------------------------------------------------------
    # Plotting lossmaps
    # ------------------------------------------------------------------------------
    if os.path.exists('loss_maps.txt') == False and os.path.exists('aperture.txt') == False:
        print '>> No losses, plot_lossmap.py exiting.'
        exit(0)
    else:
        if os.path.exists('loss_maps.txt') and os.path.exists('aperture.txt') == False:
            plt.bar(x_coll, y_coll, align="center",
                    linewidth=0, width=60, color="black", label="Collimation: " + "{:.2E}".format(Decimal(np.sum(y_coll)))  + " \%")
            plt.xlabel("Position (m)")
            plt.ylabel(r'Percentage of bunch lost')
            plt.xlim([0, 26658.883])
            plt.legend(loc='best', prop={'size': 5}).get_frame().set_linewidth(0.5)
            ax1.set_yscale('log')
            plt.title(title)
            ax1.set_axisbelow(True)
            ax1.yaxis.grid(color='gray', linestyle='-', which="minor", linewidth=0.1)
        elif os.path.exists('aperture.txt') and os.path.exists('loss_maps.txt') == False:
            plt.bar(x_ap, y_ap, color="green",
                        align="center", linewidth=0, width=60, label="Aperture: " + "{:.2E}".format(Decimal(np.sum(y_ap))) + " \%")
            plt.xlabel("Position (m)")
            plt.ylabel(r'Percentage of bunch lost')
            plt.xlim([0, 26658.883])
            plt.title(title)
            plt.legend(loc='best', prop={'size': 5}).get_frame().set_linewidth(0.5)
            ax1.set_yscale('log')
            ax1.set_axisbelow(True)
            ax1.yaxis.grid(color='gray', linestyle='-', which="minor", linewidth=0.1)
        elif os.path.exists('aperture.txt') and os.path.exists('loss_maps.txt'):
            plt.bar(x_coll, y_coll, align="center",
                    linewidth=0, width=60, color="black", label="Collimation: " + "{:.2E}".format(Decimal(np.sum(y_coll)))  + " \%")
            plt.bar(x_ap, y_ap, color="green",
                        align="center", linewidth=0, width=60, label="Aperture: " + "{:.2E}".format(Decimal(np.sum(y_ap))) + " \%")
            plt.xlabel("Position (m)")
            plt.ylabel(r'Percentage of bunch lost')
            plt.xlim([0, 26658.883])
            plt.title(title)
            plt.legend(loc='best', prop={'size': 5}).get_frame().set_linewidth(0.5)
            ax1.set_yscale('log')
            ax1.set_axisbelow(True)
            ax1.yaxis.grid(color='gray', linestyle='-', which="minor", linewidth=0.1)
            
            height = max(y_coll) / 200
            text_size = 5
            if beam == 'B1':
                plot_ip_labels(b1, height, text_size)
            elif beam == 'B2':
                plot_ip_labels(b2, height, text_size)
            else:
                print '>> Please input B1 or B2 as first argument'

            plt.subplots_adjust(left=0.16, bottom=0.19, right=0.94, top=0.88)
            plt.savefig('loss_map.png', dpi=DPI)
            plt.savefig('loss_map.eps', format='eps', dpi=DPI)
            plt.clf()
    

# ------------------------------------------------------------------------------
# Losses per turn
# ------------------------------------------------------------------------------
#ax2 = fig.add_subplot(111)


def get_turns(infile):
    get = GetData(infile)
    data = get.data_column()
    x = np.asarray(data[0], dtype='float64')
    y = np.asarray(data[2], dtype='float64')
    if 'b1' in infile:
        name = txt.replace('b1.txt', '').upper()
    elif 'b2' in infile:
        name = txt.replace('b2.txt', '').upper()
    elif infile == 'data_turn.txt':
        name = 'Collimation system'
    elif 'aperture' in infile:
        name = "Aperture"
    return x, y, name

if len(sys.argv) == 6:
    files_ccoll = glob.glob(dir_core + '/t*.txt')
    print ' '
    print '>>', len(files_ccoll), 'collimator files have been found in ' + dir_core
    if len(files_ccoll) != 0:
        d_core = {}
        for txt in files_ccoll:
            xc, yc, namec = get_turns(txt)
            d_core[namec.replace(dir_core.upper() + '/', '')] = yc
    files_tcoll = glob.glob(dir_tail + '/t*.txt')
    print ' '
    print '>>', len(files_tcoll), 'collimator files have been found in ' + dir_tail
    if len(files_tcoll) != 0:
        d_tail = {}
        for txt in files_tcoll:
            xt, yt, namet = get_turns(txt)
            d_tail[namet.replace(dir_tail.upper() + '/', '')] = yt

    d = {}

    if len(files_ccoll) != 0 and len(files_tcoll) != 0:
        for i, j in zip(d_core.keys(), d_core.values()):
            for k, l in zip(d_tail.keys(), d_tail.values()):
                if i == k:
                    d[i] = np.asarray(j) * 0.95 + np.asarray(l) * 0.05
                    
        for k, l in zip(d_core.keys(), d_core.values()):
            if not k in d.keys():
                d[k] = np.asarray(l) * 0.95
        for k, l in zip(d_tail.keys(), d_tail.values()):
            if not k in d.keys():
                d[k] = np.asarray(l) * 0.05
                
    elif len(files_ccoll) != 0 and len(files_tcoll) == 0:
        for k, l in zip(d_core.keys(), d_core.values()):
            d[k] = np.asarray(l) * 0.95

    elif len(files_ccoll) == 0 and len(files_tcoll) != 0:
        for k, l in zip(d_tail.keys(), d_tail.values()):
            d[k] = np.asarray(l) * 0.05

    #Aperture
    xc,yc,namec = get_turns(dir_core + '/data_turn_aperture.txt')
    xt,yt,namet = get_turns(dir_tail + '/data_turn_aperture.txt')
    x_ap = xc
    y_ap = np.asarray(yc)*0.95 + np.asarray(yt)*0.05
    
    # ap_outfile = open("data_turn_aperture_weighted.txt",'w')
    # ap_outfile.write("# Turn lossfraction[\%]\n")
    # for (i_x_ap,i_y_ap) in zip(x_ap,y_ap):
    #     ap_outfile.write(str(i_x_ap)+ " " + str(i_x_ap)+"\n")
    # ap_outfile.close()
    
elif len(sys.argv) == 4:
    files_coll = glob.glob('t*.txt')
    d = {}
    for txt in files_coll:
        x, y, name = get_turns(txt)
        d[name] = y
    #Aperture
    x_ap,y_ap,name = get_turns('data_turn_aperture.txt')

# After this part, a dictionary named "d" must contain the information of losses
#  per turn for each collimator.

# ------------------------------------------------------------------------------
# Sort the created dictionary by number of losses
# ------------------------------------------------------------------------------
sorted_d = sorted(d.items(), key=lambda x: sum(x[1]), reverse=True)
x_t = np.linspace(1, len(d[d.keys()[0]]), len(d[d.keys()[0]]))  # turns

def plot_coll(coll_name, d, sorted_d, x_t, doStack=False):
    print ">> Plotting '"+coll_name+"'",
    if doStack:
        print "(stacking)"
    else:
        print
        
    number = 0
    for name in d.keys():
        if name.startswith(coll_name):
            number += 1
    if coll_name == 'TCP':
        my_map = matplotlib.cm.terrain
    elif coll_name == 'TCS':
        my_map = matplotlib.cm.terrain
    elif coll_name == 'TCT':
        my_map = matplotlib.cm.terrain
    
    counter = 0
    loss_cumulative = np.zeros_like(x_t)
    for i in range(0, int(len(sorted_d))):
        if sorted_d[i][0].startswith(coll_name):
            counter += 1
            cmap = my_map

            plt.bar(x_t, sorted_d[i][1], bottom=loss_cumulative, label=str(sorted_d[i][0]),width=1.0,
                    color=cmap((float(counter)) / (1.7 * float(number))), linewidth=0)

            if doStack:
                loss_cumulative += np.asarray(sorted_d[i][1])
    if counter==0:
        return
    
    plt.legend(bbox_to_anchor=(1, 0.5), loc='center left',
               prop={'size': 4}).get_frame().set_linewidth(0.5)
    plt.xlabel('Turns')
    plt.ylabel(r'Percentage of bunch lost')
    plt.xlim([failTurn, max(x_t)])
    plt.title(title)
    
    basename = coll_name
    if doStack:
        basename += "_stack"
        
    plt.yscale('log')
    # plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.subplots_adjust(left=0.16, bottom=0.19, right=0.94, top=0.88)
    # plt.savefig(coll_name + '.png', dpi=1000)
    fig.savefig(basename + '_log.png', dpi=DPI, bbox_inches='tight')
    plt.savefig(basename + '_log.eps', format='eps', dpi=DPI)
    plt.yscale('linear')
    ymin,ymax=plt.ylim()
    plt.ylim((0.0,ymax))
    fig.savefig(basename + '_lin.png', dpi=DPI, bbox_inches='tight')
    plt.savefig(basename + '_lin.eps', format='eps', dpi=DPI)
    plt.clf()

#Plots that take a lot of time, but are not really all that usefull...
plot_coll('TCP', d, sorted_d, x_t)
plot_coll('TCP', d, sorted_d, x_t, True)
plot_coll('TCS', d, sorted_d, x_t)
plot_coll('TCS', d, sorted_d, x_t, True)
plot_coll('TCT', d, sorted_d, x_t)
plot_coll('TCT', d, sorted_d, x_t, True)

# --------------
# Aperture losses
# --------------
if max(y_ap) > 0: #Skip if no data to plot
    plt.bar(x_ap,y_ap, linewidth=0,width=1.0);

    plt.title(title)
    plt.xlabel("Turns")
    plt.ylabel("Percentage of bunch lost")
    plt.xlim([failTurn,max(x_ap)])
    
    basename="aperture"
    plt.yscale('log')
    # plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.subplots_adjust(left=0.16, bottom=0.19, right=0.94, top=0.88)
    # plt.savefig(coll_name + '.png', dpi=1000)
    fig.savefig(basename + '_log.png', dpi=DPI, bbox_inches='tight')
    plt.savefig(basename + '_log.eps', format='eps', dpi=DPI)
    plt.yscale('linear')
    ymin,ymax=plt.ylim()
    plt.ylim((0.0,ymax))
    fig.savefig(basename + '_lin.png', dpi=DPI, bbox_inches='tight')
    plt.savefig(basename + '_lin.eps', format='eps', dpi=DPI)
    plt.clf()
else:
    print ">> No aperture losses found."

# ------------------------------------------------------------------------------
# Losses per collimator group
# ------------------------------------------------------------------------------
print ">> Plotting all_colls"
def get_cumulative_loss(sorted_d, name):
    "Sum of the collimators starting with 'name'"
    cumulated = []
    d = defaultdict(list)
    for i in range(0, int(len(sorted_d))):
        if sorted_d[i][0].startswith(name):
            for t in range(0, len(sorted_d[i][1])):
                d[t].append(sorted_d[i][1][t])
    for t in range(0, len(sorted_d[i][1])):
        cumulated.append(sum(d[t]))
    return cumulated

## all_colls
names = ['tcp', 'tcs', 'tct', 'tcl']
ax = fig.add_subplot(111)
themap = matplotlib.cm.terrain

number = 0
for n in names:
    number += 1
    tc = get_cumulative_loss(sorted_d, n.upper())
    if sum(tc) != 0:
        ax.bar(x_t, tc, label=n.upper(),width=1.0,
               color=themap(float(number) / (1.5 * float(len(names)))), linewidth=0)
if max(y_ap) > 0:
    number +=1
    ax.bar(x_ap,y_ap, label="Aperture",width=1.0,
           color=themap(float(number) / (1.5 * float(len(names)))),
           linewidth=0);

lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
                prop={'size': 4}).get_frame().set_linewidth(0.5)
plt.xlabel('Turns')
plt.ylabel(r'Percentage of bunch lost')
plt.xlim([failTurn, max(x_t)])
plt.title(title)

plt.yscale('log')
fig.savefig('all_colls_log.png', dpi=DPI, bbox_inches='tight')
plt.savefig('all_colls_log.eps', format='eps', dpi=DPI)
plt.yscale('linear')
ymin,ymax=plt.ylim()
plt.ylim((0.0,ymax))
fig.savefig('all_colls_lin.png', dpi=DPI, bbox_inches='tight')
plt.savefig('all_colls_lin.eps', format='eps', dpi=DPI)
plt.clf()

## all_colls (STACKED)
names = ['tct', 'tcl', 'tcs', 'tcp']
ax = fig.add_subplot(111)
themap = matplotlib.cm.terrain

number = 0
all_colls_cumulative = np.zeros_like(x_t)
for n in names:
    number += 1
    tc = np.asarray(get_cumulative_loss(sorted_d, n.upper()))
    if sum(tc) != 0:
        ax.bar(x_t, tc, bottom=all_colls_cumulative, label=n.upper(),
               color=themap(float(number) / (1.5 * float(len(names)))),
               linewidth=0, width=1.0)
        all_colls_cumulative += np.asarray(tc)
if max(y_ap) > 0:
    number +=1
    ax.bar(x_ap,y_ap, label="Aperture", bottom=all_colls_cumulative,
           color=themap(float(number) / (1.5 * float(len(names)))),
           linewidth=0, width=1.0);
lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
                prop={'size': 4}).get_frame().set_linewidth(0.5)
plt.xlabel('Turns')
plt.ylabel(r'Percentage of bunch lost')
plt.xlim([failTurn, max(x_t)])
plt.title(title)

plt.yscale('log')
fig.savefig('all_colls_cumulative_log.png', dpi=DPI, bbox_inches='tight')
plt.savefig('all_colls_cumulative_log.eps', format='eps', dpi=DPI)
plt.yscale('linear')
ymin,ymax=plt.ylim()
plt.ylim((0.0,ymax))
fig.savefig('all_colls_cumulative_lin.png', dpi=DPI, bbox_inches='tight')
plt.savefig('all_colls_cumulative_lin.eps', format='eps', dpi=DPI)
plt.clf()

print
print "Total cumulative loss = ", all_colls_cumulative[-1]+y_ap[-1],"%"
assert int(x_ap[getLossTurn-1]) == getLossTurn
print "Total cumulative loss (turn=",getLossTurn,") = ", all_colls_cumulative[getLossTurn-1]+y_ap[getLossTurn-1],"%"
print 
