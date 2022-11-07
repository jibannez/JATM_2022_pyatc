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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation, gridspec


def play_trial(trajectories, taskdict, cometadf, aircrafts_cometa=None, aname1=None, aname2=None):
    if aircrafts_cometa is None:
        return _play_trial(trajectories, taskdict, cometadf)
    else:
        return _play_trial_with_aircrafts(trajectories, taskdict, cometadf, aircrafts_cometa, aname1, aname2)


def _play_trial(trajectories, taskdict, cometadf):
    # Fetch data for animation
    visiblearea, sector, routes = fetch_sky_background(taskdict)
    aircraftnames, aircrafts = fetch_aircrafts_trajectories(trajectories)
    cometa_static, cometa_dynamic = fetch_cometa(cometadf)

    red = 2
    aircrafts = aircrafts[::red,:]
    cometa_static = cometa_static.loc[::red,:]
    cometa_dynamic = cometa_dynamic.loc[::red,:]
    
    tLen = cometa_static.shape[0]
    t = np.arange(cometa_dynamic.shape[0])
    dynamicnames = ['COMETA_Conflict','COMETA_Reduction','COMETA']
    dynamiccolors = ['r', 'b', 'k']
    staticnames = ['COMETA_Flow','COMETA_Non_Standard','COMETA_Evolution','COMETA_Total_Static']
    staticcolors = ['r', 'g', 'b', 'k']
    styles = [
        #(0, (1, 10)),
        (0, (1, 1)),
        #(0, (1, 1)),

        #(0, (5, 10)),
        (0, (5, 5)),
        (0, (5, 1)),

        #(0, (3, 10, 1, 10)),
        (0, (3, 5, 1, 5)),
        (0, (3, 1, 1, 1)),

        (0, (3, 5, 1, 5, 1, 5)),
        (0, (3, 10, 1, 10, 1, 10)),
        (0, (3, 1, 1, 1, 1, 1))]
        
    # Set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    gs = gridspec.GridSpec(3, 4)
    ax1 = fig.add_subplot(gs[:-1, :])
    ax2 = fig.add_subplot(gs[-1, :-2])
    ax3 = fig.add_subplot(gs[-1, 2:])
    
    ##########################################################
    # Plot background: Create artist for static elements
    ##########################################################
    # line plot of sector
    sector_lines = list()
    for i in range(len(sector)):
        x1, y1 = sector[i]
        if i == len(sector) - 1:
            x2, y2 = sector[0]
        else:
            x2, y2 = sector[i+1]
        sector_lines.extend(ax1.plot([], [], 'k'))
        
    # line plot of routes
    route_lines = list()
    for route in routes.values():
        for i in range(len(route)-1):
            x1, y1 = route[i]
            x2, y2 = route[i+1]
            route_lines.extend(ax1.plot([],[], 'r'))
            
    # Line plots for static COMETA
    static_lines = sum([ax2.plot([], [], label=name, color=staticcolors[i], linestyle=styles[i]) for i, name in enumerate(staticnames)], [])
    ax2.legend(fontsize=8)

    # Line plots for dynamic COMETA
    dynamic_lines = sum([ax3.plot([], [], label=name, color=dynamiccolors[i], linestyle=styles[i]) for i, name in enumerate(dynamicnames)], [])
    ax3.legend(fontsize=8)
    
    # Create emtpy artists that will be filled in init and animate functions
    # scatter plot of aircrafts initial state, just empty plot
    aircraft_dots = sum([ax1.plot([], [], 'b.') for aname in aircraftnames], [])
    aircraft_texts = [ax1.text(-10000, -10000, aname) for aname in aircraftnames]
    static_timeline = ax2.axvline(0, color='k')  
    dynamic_timeline = ax3.axvline(0, color='k')
    
    # set visible area limits
    ax1.set_xlim(visiblearea[0])
    ax1.set_ylim(visiblearea[1])
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax2.set_xlim([0, tLen])
    ax2.set_ylim([np.nanmin(cometa_static)-5, np.nanmax(cometa_dynamic)+5])
    ax3.set_xlim([0, tLen])
    ax3.set_ylim([np.nanmin(cometa_static)-5, np.nanmax(cometa_dynamic)+5])
    
    # Initialization function: defines the background for all frames
    def init():
        for i, line in enumerate(sector_lines):
            x1, y1 = sector[i]
            if i == len(sector) - 1:
                x2, y2 = sector[0]
            else:
                x2, y2 = sector[i+1]    
            line.set_data([x1,x2], [y1,y2])
            
        for i, line in enumerate(route_lines):
            counter = -1
            looping = True
            for route in routes.values():
                for loc in range(len(route)-1):
                    counter = counter + 1
                    if counter == i:
                        x1, y1 = route[loc]
                        x2, y2 = route[loc+1]
                        looping = False
                        break
                if looping == False:
                    break
            line.set_data([x1,x2],[y1,y2])
            
        for i, line in enumerate(static_lines):
            line.set_data(t, cometa_static[staticnames[i]])
        for i, line in enumerate(dynamic_lines):
            line.set_data(t, cometa_dynamic[dynamicnames[i]])
        for i, line in enumerate(aircraft_dots):
            idx = 1 + 2*i
            x = aircrafts[0, idx]
            y = aircrafts[0, idx+1]
            if np.isnan(x) or np.isnan(y):
                continue
            line.set_data(x, y)
        for i, text in enumerate(aircraft_texts):
            text.set_text(aircraftnames[i])
            idx = 1 + 2*i
            x = aircrafts[0, idx]
            y = aircrafts[0, idx+1]
            if np.isnan(x) or np.isnan(y):
                continue
            text.set_position((x, y))            
        return tuple(sector_lines) + tuple(route_lines) + tuple(static_lines) + tuple(dynamic_lines) + tuple(aircraft_dots) + tuple(aircraft_texts)

    # Animation function. This is called sequentially
    def update(tx):
        for i, (line, text) in enumerate(zip(aircraft_dots, aircraft_texts)):
            idx = 1 + 2*i
            x = aircrafts[tx, idx]
            y = aircrafts[tx, idx+1]
            if np.isnan(x) or np.isnan(y):
                x = -10000
                y = -10000
            line.set_data(x, y)
            text.set_position((x, y))
            text.set_text(aircraftnames[i])
        static_timeline.set_data([tx, tx], [0, 1])
        dynamic_timeline.set_data([tx, tx], [0, 1])
                    
        fig.canvas.draw()
        
        return tuple(sector_lines) + tuple(route_lines) + tuple(static_lines) + tuple(dynamic_lines) + tuple(aircraft_dots) + tuple(aircraft_texts) + (static_timeline,) + (dynamic_timeline,) 

    # Call the animator.
    return animation.FuncAnimation(fig, update, tLen, init_func=init, interval=10, blit=True, repeat=True)


def _play_trial_with_aircrafts(trajectories, taskdict, cometadf, aircrafts_cometa, aname1, aname2):
    # Fetch data for animation
    visiblearea, sector, routes = fetch_sky_background(taskdict)
    aircraftnames, aircrafts = fetch_aircrafts_trajectories(trajectories)
    cometa_static, cometa_dynamic = fetch_cometa(cometadf)
    conflict_severity, acometa, severitynames = fetch_conflict(aircrafts_cometa, aname1, aname2)
    
    red = 5
    aircrafts = aircrafts[::red,:]
    cometa_static = cometa_static.loc[::red,:]
    cometa_dynamic = cometa_dynamic.loc[::red,:]
    conflict_severity = conflict_severity.loc[::red,:]
    acometa = acometa.loc[::red,:]
    tLen = cometa_static.shape[0]
    t = np.arange(cometa_dynamic.shape[0])
    dynamicnames = ['COMETA_Conflict','COMETA_Reduction','COMETA']
    dynamiccolors = ['r', 'b', 'k']
    staticnames = ['COMETA_Flow','COMETA_Non_Standard','COMETA_Evolution','COMETA_Total_Static']
    staticcolors = ['r', 'g', 'b', 'k']
    acometanames = ['COMETA_Flow','COMETA_Non_Standard','COMETA_Evolution','COMETA_Conflict', 'COMETA', 'COMETA_Reduction']
    color_sequence = [
        '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
        '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
        '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
        '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5',
        ]
        
    # Set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    gs = gridspec.GridSpec(4, 6)
    ax1 = fig.add_subplot(gs[:, :-2])
    ax2 = fig.add_subplot(gs[0, 4:])
    ax3 = fig.add_subplot(gs[1, 4:])
    ax4 = fig.add_subplot(gs[2, 4:])
    ax5 = fig.add_subplot(gs[3, 4:])
    
    
    ##########################################################
    # Plot background: Create artist for static elements
    ##########################################################
    # line plot of sector
    sector_lines = list()
    for i in range(len(sector)):
        x1, y1 = sector[i]
        if i == len(sector) - 1:
            x2, y2 = sector[0]
        else:
            x2, y2 = sector[i+1]
        sector_lines.extend(ax1.plot([], [], 'k'))
        
    # line plot of routes
    route_lines = list()
    for route in routes.values():
        for i in range(len(route)-1):
            x1, y1 = route[i]
            x2, y2 = route[i+1]
            route_lines.extend(ax1.plot([],[], 'r'))
            
    # Line plots for static COMETA
    static_lines = sum([ax2.plot([], [], label=name, color=staticcolors[i]) for i, name in enumerate(staticnames)], [])
    ax2.legend(fontsize=8)

    # Line plots for dynamic COMETA
    dynamic_lines = sum([ax3.plot([], [], label=name, color=dynamiccolors[i]) for i, name in enumerate(dynamicnames)], [])
    ax3.legend(fontsize=8)

    # Line plots for aircraft severities
    severity_lines = sum([ax4.plot([], [], label=name, color=color_sequence[i]) for i, name in enumerate(severitynames)], [])
    ax4.legend(fontsize=8)

    # Line plots for aircraft COMETA
    acometa_lines = sum([ax5.plot([], [], label=name, color=color_sequence[i]) for i, name in enumerate(acometanames)], [])
    ax5.legend(fontsize=8)
    
    # Create emtpy artists that will be filled in init and animate functions
    # scatter plot of aircrafts initial state, just empty plot
    aircraft_dots = sum([ax1.plot([], [], 'b.') for aname in aircraftnames], [])
    aircraft_texts = [ax1.text(-10000, -10000, aname) for aname in aircraftnames]
    static_timeline = ax2.axvline(0, color='k')  
    dynamic_timeline = ax3.axvline(0, color='k')
    severity_timeline = ax4.axvline(0, color='k')  
    acometa_timeline = ax5.axvline(0, color='k')
    
    # set visible area limits
    ax1.set_xlim(visiblearea[0])
    ax1.set_ylim(visiblearea[1])
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax2.set_xlim([0, tLen])
    ax2.set_ylim([np.nanmin(cometa_static)-5, np.nanmax(cometa_dynamic)+5])
    ax3.set_xlim([0, tLen])
    ax3.set_ylim([np.nanmin(cometa_static)-5, np.nanmax(cometa_dynamic)+5])
    ax4.set_xlim([0, tLen])
    ax4.set_ylim([np.nanmin(conflict_severity)-5, np.nanmax(conflict_severity)+5])
    ax5.set_xlim([0, tLen])
    ax5.set_ylim([np.nanmin(acometa)-5, np.nanmax(acometa)+5])

    # Initialization function: defines the background for all frames
    def init():
        for i, line in enumerate(sector_lines):
            x1, y1 = sector[i]
            if i == len(sector) - 1:
                x2, y2 = sector[0]
            else:
                x2, y2 = sector[i+1]    
            line.set_data([x1,x2], [y1,y2])
            
        for i, line in enumerate(route_lines):
            counter = 0
            looping = True
            for route in routes.values():
                for loc in range(len(route)-1):
                    counter = counter + 1
                    if counter == i:
                        x1, y1 = route[loc]
                        x2, y2 = route[loc+1]
                        looping = False
                        break
                if looping == False:
                    break
            line.set_data([x1,x2],[y1,y2])
            
        for i, line in enumerate(static_lines):
            line.set_data(t, cometa_static[staticnames[i]])
        for i, line in enumerate(dynamic_lines):
            line.set_data(t, cometa_dynamic[dynamicnames[i]])
        for i, line in enumerate(severity_lines):
            line.set_data(t, conflict_severity[severitynames[i]])
        for i, line in enumerate(acometa_lines):
            line.set_data(t, acometa[acometanames[i]])
        for i, line in enumerate(aircraft_dots):
            idx = 1 + 2*i
            x = aircrafts[0, idx]
            y = aircrafts[0, idx+1]
            if np.isnan(x) or np.isnan(y):
                continue
            line.set_data(x, y)
        for i, text in enumerate(aircraft_texts):
            text.set_text(aircraftnames[i])
            idx = 1 + 2*i
            x = aircrafts[0, idx]
            y = aircrafts[0, idx+1]
            if np.isnan(x) or np.isnan(y):
                continue
            text.set_position((x, y))            
        return tuple(sector_lines) + tuple(route_lines) + tuple(static_lines) + tuple(dynamic_lines) + tuple(severity_lines) + tuple(acometa_lines) + tuple(aircraft_dots) + tuple(aircraft_texts)

    # Animation function. This is called sequentially
    def update(tx):
        for i, (line, text) in enumerate(zip(aircraft_dots, aircraft_texts)):
            idx = 1 + 2*i
            x = aircrafts[tx, idx]
            y = aircrafts[tx, idx+1]
            if np.isnan(x) or np.isnan(y):
                continue
            line.set_data(x, y)
            text.set_position((x, y))
            text.set_text(aircraftnames[i])
        static_timeline.set_data([tx, tx], [0, 1])
        dynamic_timeline.set_data([tx, tx], [0, 1])
        severity_timeline.set_data([tx, tx], [0, 1])
        acometa_timeline.set_data([tx, tx], [0, 1])
                    
        fig.canvas.draw()
        
        return tuple(sector_lines) + tuple(route_lines) + tuple(static_lines) + tuple(dynamic_lines) + tuple(severity_lines) + tuple(acometa_lines) + tuple(aircraft_dots) + tuple(aircraft_texts) + (static_timeline,) + (dynamic_timeline,) + (severity_timeline,) + (acometa_timeline,)

    # Call the animator.
    return animation.FuncAnimation(fig, update, init_func=init, frames=tLen, interval=10, blit=True, repeat=True)


def fetch_conflict(aircrafts_cometa, aname1, aname2,conflictno='O0'):
    suffix = '_'+aname1+'_'+aname2+'_'+conflictno
    df = aircrafts_cometa[aname1]
    names = [ 'Conflict_Severity_A'+i+suffix for i in ['1','2','3','4']]
    names.append('Total_Conflict_Severity'+suffix)
    conflict_severity = df.loc[:,names]
    aircraft_cometa = df.loc[:,['COMETA_Flow','COMETA_Non_Standard','COMETA_Evolution','COMETA_Conflict', 'COMETA', 'COMETA_Reduction']]
    return conflict_severity, aircraft_cometa, names


def fetch_sky_background(taskdict):
    trmap = taskdict['experiment']['data']['map']

    # Fetch visible area
    reg = trmap['region']
    x1 = float(reg['x'])
    y1 = float(reg['y']) 
    x2 = x1 + float(reg['x_dim'])
    y2 = y1 + float(reg['y_dim'])
    visiblearea = [(x1, x2), (y1, y2)]
    
    # Fetch sector
    sector = [ (float(p['x']), float(p['y'])) for p in trmap['sector']['vertex']]

    # Fetch routes
    routes = dict()
    locations = dict([(l['idx'], [float(l['x']), float(l['y'])]) for l in trmap['location']])
    if not isinstance(trmap['route'], list):
        trmap['route'] = [trmap['route']]
    for route in trmap['route']:
        routes[route['idx']] = [locations[p['location']] for p in route['pointref']]

    return visiblearea, sector, routes


def fetch_aircrafts_trajectories(trajectories):
    for i, (aname, adf) in enumerate(trajectories.items()):
        if i == 0:
            df = adf[['time','x','y']]
        else:
            df = pd.merge(df, adf[['time','x','y']], 'outer', 'time', suffixes=('', '_'+aname))
    df = df.set_index('time',drop=False).sort_index()
    return (list(trajectories.keys()), df.as_matrix())

    
def fetch_cometa(cometadf):
    cometa_static = cometadf[['COMETA_Flow','COMETA_Non_Standard','COMETA_Evolution']]
    cometa_static['COMETA_Total_Static'] = cometadf['COMETA_Flow'] + cometadf['COMETA_Non_Standard'] + cometadf['COMETA_Evolution']
    cometa_static['COMETA_Flow']  = cometa_static['COMETA_Flow']  - .1
    cometa_dynamic = cometadf[['COMETA_Conflict','COMETA_Reduction','COMETA']]
    return cometa_static, cometa_dynamic
