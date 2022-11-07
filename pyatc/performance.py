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

import os
import math
import numpy as np
import pandas as pd
from collections import OrderedDict as OD

from . import util
from .cometa_params import CALL_NAMES

def get_call_updates(logdict):
    """Fetches the call update lines in the log"""
    return pd.DataFrame(logdict['call_update'], columns=CALL_NAMES)


def get_mouse_clicks(logdict):
    """Fetches the number of actions performed to change aircrafts' altitude"""
    df = pd.DataFrame(logdict['view_mouse_down'], columns=['time', 'x', 'y'])
    df.time = df.time -1
    return df.set_index(df.time, drop=False, inplace=False, verify_integrity=True).sort_index()


def get_mouse_double_clicks(logdict):
    """Fetches the mouse double clicks events in a trial"""
    df = pd.DataFrame(logdict['view_mouse_double_click'], columns=['time', 'x', 'y'])
    df.time = df.time -1
    return df.set_index(df.time, drop=False, inplace=False, verify_integrity=True).sort_index()


def get_mouse_press_events(logdict):
    """Fetches the mouse clicks and double clicks"""
    clks = get_mouse_clicks(logdict)
    dclks = get_mouse_double_clicks(logdict)
    return pd.concat([clks, dclks]).sort_index()


def get_call_level(logdict):
    """Computes the number of actions performed to change aircrafts' altitude"""
    df = pd.DataFrame(logdict['call_level'], columns=['time', 'aircraft', '', 'end', 'start'])
    return len(df.index)


def get_call_speed(logdict):
    """Función número de cambios de velocidad"""
    df = pd.DataFrame(logdict['call_speed'], columns=['time', 'aircraft', '', 'end', '', 'start', '', 'level'])
    return len(df.index)


def get_interventions(logdict):
    """Compute the total number of user interventions on aircrafts' altitude and speed"""
    level = get_call_level(logdict)
    speed = get_call_speed(logdict)
    return [level, speed, level+speed]


def get_windowed_mouse_press_events(dfclks, bins=64):
    """Computes the windowed number mouse events"""
    evcount = dfclks['time'].value_counts(bins=bins,sort=False)
    idx = np.round(evcount.index.left/1000).astype(np.int)
    idx = idx - idx[0]# + 1
    data = np.hstack([idx.values.reshape((bins,1)), evcount.values.reshape((bins,1))])
    return pd.DataFrame(data,index=idx,columns=['time','clicks'])


def get_accept_reaction_time(logdict):
    """Computes the reaction time for all ACCEPT actions performed by the user"""
    df = get_call_updates(logdict)
    results = OD()
    results['aircraft'] = list()
    results['time'] = list()
    results['rt'] = list()
    for aname in df.name.unique():
        adf = df.loc[df.name == aname]
        control_states = adf.control.unique()
        #if (1 in control_states) and (2 in control_states) and (3 in control_states):
        if (2 in control_states) and (3 in control_states):
            i1 = np.where(adf.control==2)[0][0]
            i2 = np.where(adf.control==3)[0][0]
            #if adf.control.iloc[i2-1] == 2 and adf.control.iloc[i1-1] == 1:
            tdiff = ((adf.time.iloc[i2] - adf.time.iloc[i1])/1000).round()
            time = (adf.time.iloc[i1]/1000).round()
            # Avoid duplicated time stamps!! The exact timestamp
            # is not critical, just select a close one.
            if time in results['time']:
                for i in range(1,10):
                    if time+i not in results['time']:
                        time = time + i
                        break
            results['aircraft'].append(aname)
            results['time'].append(time)
            results['rt'].append(tdiff)
    return pd.DataFrame.from_dict(results)


def speed_out(params, trajectories):
    """Computes the match with the exit speeds specified in the flightplan"""
    d = OD()

    for name in params['aircrafts']:
        key = params['aircrafts'][name]['idx']
        d.setdefault(key, [])
        d[key].append(params['aircrafts'][name]['velocity'])

    for name in trajectories:
        arr = np.nonzero(trajectories[name].insector == True)[0]
        if len(arr) > 0:
            i = arr[-1]
            if i < (len(trajectories[name])-1):
                key = trajectories[name]['name'][i]
                d[key].append(trajectories[name]['speed'][i])
        else:
            pass

    df = pd.DataFrame.from_dict(d, orient = 'index')

    if 1 in df.columns:
        df = df.drop(df[df[1].isnull()].index)
        array = []
        for i in range(0, len(df)):
            array.append(math.isclose(df.iloc[i][0], df.iloc[i][1], abs_tol = 0.1))
        df.insert(2, 'speed_ok', array)
    else:
        df = pd.DataFrame(columns = ['speed_ok'])
        print("----------No aircrafts----------")

    return df


def altitude_out(params, trajectories):
    """Computes the match with exit altitudes specified in the flightplan"""
    d = OD()

    for name in params['aircrafts']:
        key = params['aircrafts'][name]['idx']
        d.setdefault(key, [])
        d[key].append(params['aircrafts'][name]['altitude_end'])

    for name in trajectories:
        arr = np.nonzero(trajectories[name].insector == True)[0]
        if len(arr) > 0:
            i = arr[-1]
            if i < (len(trajectories[name])-1):
                key = trajectories[name]['name'][i]
                d[key].append(trajectories[name]['z'][i])
        else:
            pass

    df = pd.DataFrame.from_dict(d, orient = 'index')

    if 1 in df.columns:
        df = df.drop(df[df[1].isnull()].index)
        arr = []
        for i in range(0, len(df)):
            arr.append(math.isclose(df.iloc[i][0], df.iloc[i][1], abs_tol = 0.1))
        df.insert(2, 'altitude_ok', arr)
    else:
        df = pd.DataFrame(columns = ['altitude_ok'])
        print("----------No aircrafts----------")

    return df


def out_sector(velocity, altitude):
    """Computes the match with exit speeds and altitudes specified in the flightplan"""
    df1 = velocity
    df2 = altitude
    results = [0, 0, 0, 0]

    if df1.empty and df2.empty:
        print("----------No aircrafts----------")
    else:
        df = pd.merge(df1, df2, left_index=True, right_index=True)
        df.rename(columns={'0_x':'expected_speed', '1_x':'speed_out','0_y':'expected_altitude','1_y':'altitude_out'}, inplace=True)
        arr = []
        for i in range(0, len(df)):
            arr.append((df.iloc[i]['speed_ok'] == True) and (df.iloc[i]['altitude_ok'] == True))
        df.insert(6, 'out_ok', array)
        results = [len(df.index), len(df[df['speed_ok'] == False].index), len(df[df['altitude_ok'] == False].index), len(df[df['out_ok'] == False].index)]

    return results


# def get_aircrafts_xml(taskxml):
    # skyname = None
    # for phase in taskxml['experiment']['presentation']['phase']:
        # if phase['idx'] == phasename:
            # for trial in phase['trial']:
                # if trial['idx'] == trialname:
                    # skyname = trial['sky']
                    # break
            # if skyname is not None:
                # break
    # #for sky in taskxml['experiment']['data']['sky']:
    # #    if sky['idx'] == skyname:
    # #        aircrafts = sky['aircraft']
    # #        break

    # # Assume only one sky is present
    # sky = taskxml['experiment']['data']['sky']
    # aircrafts = sky['aircraft']

    # # Single aircraft files produce error here, forcing list
    # if not isinstance(aircrafts, list):
        # aircrafts = [aircrafts]

    # airdict = OD()
    # for aircraft in aircrafts:
        # aircft = OD()
        # aircft['type'] = aircraft['type']
        # aircft['idx'] = aircraft['idx']
        # aircft['start'] = int(aircraft['start'])
        # aircft['altitude'] = float(aircraft['altitude'])
        # aircft['velocity'] = float(aircraft['velocity'])
        # try:
            # aircft['altitude_end'] = float(aircraft['flightpath']['point'][0]['altitude'])
        # except:
            # aircft['altitude_end'] = aircft['altitude']

        # # aircft['altitude_out']
        # # aircft['velocity_out']
        # aircft['flightpath'] = [(float(p['x']), float(p['y'])) for p in aircraft['flightpath']['point']]
        # airdict[aircft['idx']] = aircft
    # return airdict
