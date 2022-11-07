#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file is part of pyatc library
#
# Authors:
# Jorge Ibáñez Gijón <jorge.ibannez@uam.es> [2020-2022]
# Departamento de Psicología Básica, Facultad de Psicología
# Universidad Autónoma de Madrid
#
# © Copyright 2022 Jorge Ibáñez Gijón. All rights reserved
#

import matplotlib.pylab as plt

############################################################
### PLOTTING FUNCTIONS FOR COMETA RESULTS
############################################################

def plot_cometa_timeseries(cometadf, plottype='plot'):
    if isinstance(cometadf, OD):
        (cols, rows) = get_closest_pair(len(cometadf))
        fig = plt.figure()
        for i, (logfile, df) in enumerate(cometadf.items()):
            ax = fig.add_subplot(rows, cols, i + 1)
            row = i // cols + 1
            col = i + 1 - (row - 1) * cols
            if col == 1:
                addylabel = True
            else:
                addylabel = False
            if row == rows:
                addxlabel = True
            else:
                addxlabel = False
            if row == 1 and col == cols:
                addlegend = True
            else:
                addlegend = False
            addtitle = True
            _plot_cometa_timeseries(df, ax, logfile, addtitle, addlegend, addxlabel, addylabel, plottype)
    else:
        _plot_cometa_timeseries(cometadf, plottype='plot')


def plot_cometa_barplots(cometadf):
    #Plot barplots of average cometa values
    if isinstance(cometadf, OD):
        (cols, rows) = get_closest_pair(len(cometadf))
        fig = plt.figure()
        for i, (logfile, df) in enumerate(cometadf.items()):
            ax = fig.add_subplot(rows, cols, i + 1)
            row = i // cols + 1
            col = i + 1 - (row - 1) * cols
            if col == 1:
                addylabel = True
            else:
                addylabel = False
            if row == rows:
                addxlabel = True
            else:
                addxlabel = False
            if row == 1 and col == cols:
                addlegend = True
            else:
                addlegend = False
            addtitle = True
            _plot_cometa_barplots(df, ax, logfile, addtitle, addlegend, addxlabel, addylabel)
    else:
        _plot_cometa_barplots(cometadf, plottype='plot')


def _plot_cometa_barplots(df, ax=None, title='Cometa Time Series', addtitle=False, addlegend=True, addxlabel=True, addylabel=True):
    y = df[COMETA_NAMES].mean()
    yerr = df[COMETA_NAMES].std()
    x = range(1,len(y)+1)
    bars = [ax.bar(i, y[i], yerr=yerr[i]) for i in range(len(y))]

    # Decorate figure
    if addxlabel:
        ax.set_xlabel('Time (min)')
        ax.set_xticks(np.arange(0, len(x)) - 0.5 )
        ax.set_xticklabels(COMETA_NAMES, rotation=25)
    else:
        ax.set_xticklabels([])

    if addylabel:
        ax.set_ylabel('COMETA Index')

    if addlegend:
        #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, mode="expand", borderaxespad=0.)
        #ax.legend(bars, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        ax.legend(bars, COMETA_NAMES, fontsize='small',loc='upper right')
    if addtitle:
        ax.set_title(title)


def _plot_cometa_timeseries(cometadf, ax=None, title='Cometa Time Series', addtitle=False, addlegend=True, addxlabel=True, addylabel=True, plottype='plot'):
    # Fetch time and convert to minutes
    t = cometadf['time'] / 60
    # Create new axisi if not passed as argument
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    ax.hold(True)

    #Plot cometa variables to axis
    for name in COMETA_NAMES:
        if plottype == 'scatter':
            ax.scatter(t, cometadf[name], label=name)
        elif plottype == 'plot':
            ax.plot(t, cometadf[name], label=name)

    # Decorate figure
    if addxlabel:
        ax.set_xlabel('Time (min)')
    else:
        ax.set_xticklabels([])

    if addylabel:
        ax.set_ylabel('COMETA Index')

    if addlegend:
        #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, mode="expand", borderaxespad=0.)
        ax.legend(fontsize='small',loc='upper right')#bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True)
    if addtitle:
        ax.set_title(title)


def get_closest_pair(n):
    root = np.ceil(np.sqrt(n));
    #p0 = root*root;
    p1 = (root-1)*root
    if p1 < n:
        rs = root
    else:
        rs = root-1
    return (rs, root)


def plot_cometa_scores(conflicts, savefig=False):
    """Plot per-conflict cometa scores, detailed to help debugging
    """
    clrs = OD()
    clrs['x_a1'] = 'k'
    clrs['y_a1'] = 'r'
    clrs['x_a2'] = 'k--'
    clrs['y_a2'] = 'r--'
    for conflict_name, c in conflicts.items():
        fig = plt.figure()
        ax1 = fig.add_subplot(3,1,1)

        ax1.set_title(conflict_name)
        for cometa_name in COMETA_NAMES:
            ax1.plot(c['time']/1000, c[cometa_name], label=cometa_name)
        ax1.set_xlim([c['time'].values[0]/1000, c['time'].values[-1]/1000])
        ax1.legend()

        ax2 = fig.add_subplot(3,1,2)
        for coord in ['x_a1', 'y_a1', 'x_a2', 'y_a2']:
            ax2.plot(c['time']/1000, c[coord], clrs[coord], label=coord)
        ax2.legend()

        ax3 = fig.add_subplot(3,1,3)
        for coord in ['z_a1', 'z_a2']:
            ax3.plot(c['time']/1000, c[coord], label=coord)
        ax3.legend()

        if savefig:
            fname = os.path.join(FIGPATH, conflict_name+'.png')
            plt.savefig(fname)
            plt.close()
