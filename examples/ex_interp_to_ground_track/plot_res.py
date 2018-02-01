#!/usr/bin/env python

#    B a r a K u d a
#
#    L. Brodeau, 2017

import sys
import os
from string import replace
import numpy as nmp

from netCDF4 import Dataset

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#import matplotlib.font_manager as font_manager
import matplotlib.patches as patches
from mpl_toolkits.basemap import Basemap


import warnings
warnings.filterwarnings("ignore")

import matplotlib.dates as mdates

#import barakuda_orca   as bo
#import barakuda_ncio   as bnc
#import barakuda_colmap as bcm
#import barakuda_plot   as bp

import barakuda_tool as bt

r_max_amp_ssh = 1.5 # in meters

rcut_by_time = 5. # specify in seconds the time gap between two obs that means a discontinuity and therefore
#                 # should be considered as a cut!
nvalid_seq = 100  # specify the minimum number of values a sequence should contain to be considered and kept!

color_dark_blue = '#091459'
color_red = '#AD0000'
b_gre = '#3A783E'
b_prp = '#8C008C'
b_org = '#ED7C4C'

color_text_colorbar = 'k'
color_stff_colorbar = 'k'
#color_continents    = '#9C5536'
#color_continents    = '#EDD0AB'
color_continents    = '0.75'



rDPI=100.


title_satellite = 'SARAL/Altika'
title_model     = 'NATL60-CJM165'

#fig_ext='png'
fig_ext='svg'

jt1=0 ; jt2=0

narg = len(sys.argv)

print narg

if narg != 4 and narg != 6 :
    print 'Usage: '+sys.argv[0]+' <file> <variable model> <variable ephem> (<jt1> <jt2>)'; sys.exit(0)

cf_in = sys.argv[1] ; cv_mdl=sys.argv[2] ; cv_eph=sys.argv[3]
if narg == 6:
    jt1=int(sys.argv[4]) ; jt2=int(sys.argv[5])

bt.chck4f(cf_in)

id_in    = Dataset(cf_in)
vt_epoch = id_in.variables['time'][:]
vmodel   = id_in.variables[cv_mdl][:]
vephem   = id_in.variables[cv_eph][:]
vlon     = id_in.variables['longitude'][:]
vlat     = id_in.variables['latitude'][:]
id_in.close()
print "  => READ!"





font_corr = 1.2
params = { 'font.family':'Ubuntu',
           'font.weight':    'normal',
           'font.size':       int(12*font_corr),
           'legend.fontsize': int(12*font_corr),
           'xtick.labelsize': int(11*font_corr),
           'ytick.labelsize': int(12*font_corr),
           'axes.labelsize':  int(12*font_corr),
           'axes.titlesize' : 20,
           'lines.linewidth' : 8,
           'lines.markersize' : 10 }
#           'figure.facecolor': 'w' }
font_ttl= { 'fontname':'Helvetica Neue', 'fontweight':'light', 'fontsize':int(15.*font_corr) }
mpl.rcParams.update(params)












nbr = len(vt_epoch)




# Initial raw plot:
# Create Matplotlib time array:

vtime = nmp.zeros(nbr)
for jt in range(nbr): vtime[jt] = mdates.epoch2num(vt_epoch[jt])




ii=nbr/300
ib=max(ii-ii%10,1)
#print ' ii , ib =', ii, ib

xticks_d=30.*ib

fig = plt.figure(num = 1, figsize=(12,7), facecolor='w', edgecolor='k')
ax1 = plt.axes([0.07, 0.24, 0.9, 0.75])

ax1.set_xticks(vtime[::xticks_d])
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.xticks(rotation='60')


plt.plot(vtime, vephem, '-', color=color_dark_blue, linewidth=2, label=title_satellite+' ("'+cv_eph+'")', zorder=10)
plt.plot(vtime, vmodel, '-', color=b_org, linewidth=2,  label=title_model+' ("'+cv_mdl+'")', zorder=15)
ax1.set_ylim(-r_max_amp_ssh,r_max_amp_ssh) ; ax1.set_xlim(vtime[0],vtime[nbr-1])
plt.xlabel('Time [seconds since 1970]')
plt.ylabel('SSH [m]')
#cstep = '%5.5i'%(jpnij)
ax1.grid(color='k', linestyle='-', linewidth=0.3)

plt.legend(bbox_to_anchor=(0.55, 0.98), ncol=1, shadow=True, fancybox=True)


#ax2 = ax1.twinx()
#ax2.set_ylim(25.,68.)
#plt.plot(vtime, vlat, '--', color='0.4', linewidth=1.5, label='latitude', zorder=0.1)
#ax2.set_ylabel(r'Latitude [$^\circ$North]', color='0.4')
#[t.set_color('0.4') for t in ax2.yaxis.get_ticklabels()]

plt.savefig('fig_raw_data.'+fig_ext, dpi=120, transparent=True)
plt.close(1)






# Now 1 figure per sequence !

vmask = vmodel.mask

(idx_ok,) = nmp.where(vmask==False) # indexes with valid values!


print idx_ok

nbr_v = len(idx_ok)

print ' *** '+str(nbr_v)+' valid points out of '+str(nbr)+' !'

print vmask

# Will extract the N valid data sequences:
nb_seq=0
idx_seq_start = [] ; # index of first valid point of the sequence
idx_seq_stop  = [] ; # index of last  valid point of the sequence



print "len(vmask), len(vmodel), nbr =", len(vmask), nbr, len(vmodel)

jr=0
while jr < nbr:
    # Ignoring masked values and zeros...        
    if (not vmask[jr]) and (vmodel[jr]!=0.0) and (vmodel[jr]<100.):
        nb_seq = nb_seq + 1
        print '\n --- found seq #'+str(nb_seq)+' !'
        #np_s = 1
        idx_seq_start.append(jr)
        print ' => starting at jt='+str(jr)
        while (not vmask[jr+1]) and (vmodel[jr+1]!=0.0) and (vt_epoch[jr+1]-vt_epoch[jr] < rcut_by_time) and (vmodel[jr]<100.) :
            if nb_seq==25: print vt_epoch[jr+1]-vt_epoch[jr], vt_epoch[jr]
            jr = jr+1
            if jr==nbr-1: break
            #np_s = np_s+1
        idx_seq_stop.append(jr)
        print ' => and stoping at jt='+str(jr)
        
    jr = jr+1


if len(idx_seq_start) != nb_seq: print ' ERROR #1!'; sys.exit(1)

print '\n idx_seq_start =', idx_seq_start
print '\n idx_seq_stop =', idx_seq_stop

for js in range(nb_seq):
    it1 = idx_seq_start[js]
    it2 = idx_seq_stop[js]
    #print vmodel[it1:it2+1]
    nbp = it2-it1+1

    cseq = '%2.2i'%(js+1)

    # Only doing if more than nvalid_seq points !
    if nbp >= nvalid_seq:

        print '\n\n ###################################'
        print '  *** Seq #'+cseq+':'        
        print ' *** Considering '+str(nbp)+' points!\n'

        # Create Matplotlib time array:
        vtime = nmp.zeros(nbp)
        for jt in range(nbp): vtime[jt] = mdates.epoch2num(vt_epoch[it1+jt])



        # Maps:
        fig = plt.figure(num = 1, figsize=(12,8.3), facecolor='w', edgecolor='k')
        ax1 = plt.axes([0.01, 0.01, 0.98, 0.98])
        m = Basemap(projection='lcc', llcrnrlat=18, urcrnrlat=60, llcrnrlon=-77, urcrnrlon=+25, \
                    lat_0=45.,lon_0=-40., resolution='c', area_thresh=1000.)        
        m.bluemarble()
        m.drawcoastlines(linewidth=0.5)
        m.drawcountries(linewidth=0.5)
        m.drawstates(linewidth=0.5)

        x, y = m(vlon[it1:it2+1], vlat[it1:it2+1])

        plt.plot(x, y, 'r-')        
        plt.savefig('map_'+cseq+'.'+fig_ext, dpi=120, transparent=True)
        plt.close(1)
        #sys.exit(0)
        


        


        ii=nbp/300
        ib=max(ii-ii%10,1)
        print ' ii , ib =', ii, ib

        xticks_d=30.*ib

        # Finding appropriate amplitude as a multiple of 0.25:

        rmult = 0.2
        rmax    = max( nmp.max(vmodel[it1:it2+1]) , nmp.max(vephem[it1:it2+1])  )
        r_ssh_p = bt.round_to_multiple_of(rmax, prec=1, base=rmult)
        if rmax > r_ssh_p: r_ssh_p = r_ssh_p + rmult/2.

        rmin    = min( nmp.min(vmodel[it1:it2+1]) , nmp.min(vephem[it1:it2+1])  )
        r_ssh_m = bt.round_to_multiple_of(rmin, prec=1, base=rmult)
        if rmin < r_ssh_m: r_ssh_m = r_ssh_m - rmult/2.
        
        fig = plt.figure(num = 1, figsize=(12,7.4), facecolor='w', edgecolor='k')
        ax1 = plt.axes([0.07, 0.22, 0.88, 0.73])

        ax1.set_xticks(vtime[::xticks_d])
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.xticks(rotation='60')
        
        plt.plot(vtime, vtime*0., '-', color='k', linewidth=2, label=None)

        plt.plot(vtime, vephem[it1:it2+1], '-', color=color_dark_blue, linewidth=2, label=title_satellite+' ("'+cv_eph+'")', zorder=10)
        plt.plot(vtime, vmodel[it1:it2+1], '-', color=b_org, linewidth=2,  label=title_model+' ("'+cv_mdl+'")', zorder=15)

        plt.yticks( nmp.arange(r_ssh_m, r_ssh_p+0.1, 0.1) )
        ax1.set_ylim(r_ssh_m*1.05,r_ssh_p*1.05)
        plt.ylabel('SSH [m]')

        ax1.set_xlim(vtime[0],vtime[nbp-1])
        #plt.xlabel('Time [seconds since 1970]')

        #cstep = '%5.5i'%(jpnij)
        ax1.grid(color='k', linestyle='-', linewidth=0.3)
        
        #plt.legend(bbox_to_anchor=(0.55, 0.98), ncol=1, shadow=True, fancybox=True)
        plt.legend(loc="best", ncol=1, shadow=True, fancybox=True)

        cstart = str(round(bt.lon_180_180(vlon[it1]),2))+"$^{\circ}$E, "+str(round(vlat[it1],2))+"$^{\circ}$N"
        cstop  = str(round(bt.lon_180_180(vlon[it2]),2))+"$^{\circ}$E, "+str(round(vlat[it2],2))+"$^{\circ}$N"
        plt.title(r""+cstart+"  $\longrightarrow$ "+cstop, **font_ttl)
        
        #ax2 = ax1.twinx()
        #ax2.set_ylim(25.,68.)
        #plt.plot(vtime, vlat, '--', color='0.4', linewidth=1.5, label='latitude', zorder=0.1)
        #ax2.set_ylabel(r'Latitude [$^\circ$North]', color='0.4')
        #[t.set_color('0.4') for t in ax2.yaxis.get_ticklabels()]
        
        plt.savefig('fig_seq_'+cseq+'.'+fig_ext, dpi=120, transparent=False)
        plt.close(1)


    else:

        print '\n  *** Seq #'+cseq+' => Not enough points ! ('+str(nbp)+')\n'        
