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
import csv

import numpy as np
import pandas as pd
import matplotlib.path as mplPath

from scipy.spatial.distance import euclidean
from collections import OrderedDict as OD

from .parse import run as parse_log
from .xml import load_xml, get_aircrafts_xml, get_routenames_xml
from .geom import get_routes_crossingpoints

cnames1 = ['x_a1', 'y_a1','x_a2', 'y_a2','insector_a1','intime','isconflictinsector','Tc_a1', 'Tc_a2', 'Xc', 'Yc','A0_vdist_a1_a2_conflict', 'A0_hdist_a1_conflict','A1_dist_a1_a2','A2_hdist_conflict_sector', 'A3_angle','A4_hdist_conflict_crossingpoints','inconflict',]
cnames2 = ['x_a1', 'y_a1','x_a2', 'y_a2','insector_a1','insector_a2']
cnames3 = ['insector', 'COMETA_Flow', 'COMETA_Non_Standard','COMETA_Evolution', 'COMETA_Conflict', 'COMETA','COMETA_Reduction', 'Active_conflicts']
cnames4 = ['COMETA_Flow',  'COMETA_Evolution' ,'COMETA_Non_Standard' ,'COMETA_Conflict' ,'COMETA_Reduction' ,'COMETA' ,'Active_conflicts']

########################################################################
## Dataframe and pandas related functions
########################################################################

def set_pandas_display():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.float_format','{:,.2f}'.format)
    pd.set_option("display.max_colwidth",7)
    pd.set_option("expand_frame_repr",False)


def reset_pandas_display():
    pd.reset_option('^display.', silent=True)


def deduplicate_df_column(df, col='time'):
    """
    Fuzz duplicate start times from a frame so we can stack and unstack
    this frame.
    """
    dups = df.duplicated(subset=col) & ~pd.isnull(df[col])

    if not dups.any():
        return df
    else:
        #print("Removing %i duplicates", dups.sum())
        return df.loc[~dups, :]


########################################################################
## Aircraft trajectory computation
########################################################################

def compute_aircraft_trjs(df, name, sector):
    """The units of the physical magnitudes present in calls dataframe are as follow:
    x = nautic miles
    y = nautic miles
    z = feet
    speed = nautic miles per hour
    heading = radians
    climb = feets per minute
    power = proportion of the total speed i think, between 0 and 1

    The trajectory equations are obtained by solving the parametric equation of (x, y)
    with respect to time:
        | x = x0 + vx*t
        | y = y0 + vy*t

    so that we end with an equation that relates directly x and y:
        y = f(x) = m*x + b

    With this representation, computing conflicts requires a simple algebraic expression:
        | y_c = m1*x_c + b1
        |               --> m1*x_c + b1 = m2*x_C + b2
        | y_c = m2*x_c + b2

    Solving this system for x_c, and substituting to obtain y_c yields the conflict point
    (the intersection between lines). Any two lines in a 2D plane have exactly one intersection
    (except parallel lines, with zero intersections, and equal lines, with infinite intersections)
    """

    # select current aircraft data in the dataframe
    df = df[df.name == name]

    # set time as index to allow comparison between different aircrafts later on
    if df.duplicated(subset='time').sum() > 0:
        df = deduplicate_df_column(df, 'time')

    # Set start at 0
    df.time -= 1
    df = df.set_index(df.time, drop=False, inplace=False, verify_integrity=True).sort_index()
    #df = df.set_index('time', drop=False, inplace=False, verify_integrity=True).sort_index()

    # Attempt to fix issue with recent pandas versions
    df.index.name = ''

    # get movement parameters
    df['v'] = df['speed'] / 3600 # nautic miles per second
    df['vx'] = df['v'] * np.cos(df['heading'])
    df['vy'] = df['v'] * np.sin(df['heading'])
    # Fix zero x speed issue
    df['vx'][df['vx'] == 0] = 0.0001
    df['vz'] = df['climb'] / 60 # feet per second
    df['vz_deriv'] = df['z'].diff() / df['time'].diff()

    # compute aircraft predicted trajectory equations
    df['m'] = df['vy'] / df['vx']
    df['b'] = df['y'] - df['m']*df['x']

    # Set insector property for the trajectory of this aircraft
    #sector = sector[:]
    #sector.append(sector[0])
    df['insector'] = is_point_insector(df['x'], df['y'], sector)

    # Fill the dataframe for scenarios with empty conflicts, a weird case
    # than only tends to appears in test scenarios.
    # DISABLED BECAUSE IT CREATES TOO MUCH NOISE FOR NO REASON
    # REENABLE IT IF YOU WANT TO RUN TOO SIMPLE TESTS
    #df['Tc_a1'] = np.NaN
    #df['Tc_a2'] = np.NaN
    #df['inconflict'] = False
    #df['intime'] = False
    return df


########################################################################
## Helpers for data and parameters extraction
########################################################################

def prepare_data(logpath='./data/file.xml.log', taskpath='./task', tmax=600, save2mat=False):
    # Extract filename and pathname of log file
    (logparent, logfile) = os.path.split(logpath)

    # Parse log file
    logdict = parse_log(logpath, save2mat)

    # Guess xml task file name: the filename pattern of log files is [TRIALNAME]_[TASKNAME].xml.log
    if taskpath is None:
        taskpath = logparent

    if os.path.isfile(taskpath):
        (taskparentdir, taskfilename) = os.path.split(taskpath)
        taskfilepath = taskpath
        taskpath = taskparentdir
    else:
        # This is broken for a lot of file name conventions...
        # It is much preferred to provide the task file path rather than relying on guessing.
        taskfilename = '_'.join(logfile.split('_')[1:])[:-4]
        taskfilepath = os.path.join(taskpath, taskfilename)
    #else:
    #    (taskparent, taskfilename) = os.path.split(taskfilepath)

    # Load the task dict from xml
    taskdict = load_xml(taskfilepath)

    # Extract the name of the task from the xml filename (remove everything after the last dot)
    taskname = '.'.join(taskfilename.split('.')[:-1])

    # Check whether flows file exists
    flowsname = 'Flows_' + taskname + '.xml.csv'
    flowspath = os.path.join(taskpath, flowsname)
    if os.path.isfile(flowspath):
        flowdict = parse_flows_file(flowspath, taskdict)
    else:
        #return None
        # To try without flows at all, uncomment the following line and comment the previous
        print('Warning, the flows file %s does not exists' % flowspath)
        flowdict = OD()

    # Fetch paramters fo the simulation
    params = get_sky_parameters(taskdict, flowdict, tmax, taskpath, logfile)

    return taskdict, logdict, flowdict, params


def prepare_data_onthefly(taskpath='./task.xml', tmax=600):
    (taskparentdir, taskfilename) = os.path.split(taskpath)
    taskfilepath = taskpath
    taskpath = taskparentdir

    # Load the task dict from xml
    taskdict = load_xml(taskfilepath)

    # Extract the name of the task from the xml filename (remove everything after the last dot)
    taskname = '.'.join(taskfilename.split('.')[:-1])

    # Check whether flows file exists
    flowsname = 'Flows_' + taskname + '.xml.csv'
    flowspath = os.path.join(taskpath, flowsname)
    if os.path.isfile(flowspath):
        flowdict = parse_flows_file(flowspath, taskdict)
    else:
        #return None
        # To try without flows at all, uncomment the following line and comment the previous
        print('Warning, the flows file %s does not exists' % flowspath)
        flowdict = OD()

    # Fetch paramters fo the simulation
    params = get_sky_parameters(taskdict, flowdict, tmax, taskpath, taskfilename+'.log')

    return taskdict, flowdict, params


def parse_flows_file(filename, taskdict):
    flows = OD()
    aircrafts = get_aircrafts_xml(taskdict)
    routenames = get_routenames_xml(taskdict)
    if not os.path.isfile(filename):
        print('The flows file %s does not exist' % filename)
        return flows

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #print('='*20)
        for row in reader:
            # Skip empty lines
            if len(row) == 0:
                continue
            # Skip comments
            if row[0].startswith('#'):
                continue
            # Skip flows assigned to routes not defined in xml
            if not (row[0] in routenames):
                print('\n\t\t[WARNING] Incorrect flows file: route %s does not exist in task xml file!!!' % row[0])
                print('\t\t\tAvailable routes in the task xml are: ' + ' '.join(routenames))
                continue
            else:
                n = row[0]
            flows[n] = OD()
            flows[n]['occupation'] = int(row[1][1:-1]) # Remove brackets before conversion
            flows[n]['aircrafts'] = row[2:]
            # Select one of the aircraft in the flow, fetch flow data from it
            aircraft = flows[n]['aircrafts'][0]
            flows[n]['altitude'] = aircrafts[aircraft]['altitude']
            flows[n]['altitude_end'] = aircrafts[aircraft]['altitude_end']
            flows[n]['velocity'] = aircrafts[aircraft]['velocity']
            #flows[n]['types'] = 0 # Most likely not necessary
    return flows


def get_sky_parameters(fname, flowdict=None, tmax=600, pathname='.', logfile='logfile_name_not_set.xml.log'):
    """ Fetches simulation parameters from the different information sources required.
    This funtions is part of the public API because the values obtained here can be
    useful for other computations such as performace related measures"""

    param = OD()
    if isinstance(fname, str):
        taskdict = load_xml(fname)
    else:
        taskdict = fname
    trmap = taskdict['experiment']['data']['map']
    sky = taskdict['experiment']['data']['sky']
    # This does not consider multiple active sectors or arc defined sectors
    param['sector'] = [ (float(p['x']), float(p['y'])) for p in trmap['sector']['vertex']]
    param['sector'].append(param['sector'][0])
    if isinstance(flowdict, str):
        param['flows'] = parse_flows_file(flowdict,taskdict)
    else:
        param['flows'] = flowdict
    param['tmax'] = tmax
    param['locations'] = OD()
    for loc in trmap['location']:
        param['locations'][loc['idx']] = (float(loc['x']), float(loc['y']))
    param['routes'] = OD()
    # Single route scenario fail here, forcing a list with a single element
    if not isinstance(trmap['route'], list):
        trmap['route'] = [trmap['route']]
    for route in trmap['route']:
        if flowdict is None or route['idx'] not in flowdict:
            # Skip loading routes that are not flows
            continue
        param['routes'][route['idx']] = [p['location'] for p in route['pointref']]

    param['aircrafts'] = get_aircrafts_xml(taskdict)
    param['crossingpoints'] = get_routes_crossingpoints(param['routes'], param['locations'])
    param['pathname'] = pathname
    param['logfile'] = logfile
    return param


def get_non_standard_aircrafts(aircrafts, flows):
    non_standard_aircrafts = list()
    #Iterate over all aircraft names
    for aircraft in aircrafts.keys():
        nsflag = True
        # Check all flows in search for this aircraft name
        for flow in flows.values():
            if aircraft in flow['aircrafts']:
                nsflag = False
        # If the flag is still True, the aircraft is non standard
        if nsflag:
            non_standard_aircrafts.append(aircraft)

    return non_standard_aircrafts


def get_inevolution_aircrafts(aircrafts):
    inevolution_aircrafts = list()
    #Iterate over all aircrafts
    for aname, aircraft in aircrafts.items():
        if aircraft['altitude'] != aircraft['altitude_end']:
            inevolution_aircrafts.append(aname)
    return inevolution_aircrafts


############################################################
### MISCELANEOUS UTILITY FUNCTIONS
############################################################

def is_in_flow(aircraft, flow):
    return (aircraft in flow['aircrafts'])


def is_conflict_intime(df, tmax=600):
    in_time_a1 = np.logical_and(df['Tc_a1'] < tmax, df['Tc_a1'] >= 0)
    in_time_a2 = np.logical_and(df['Tc_a2'] < tmax, df['Tc_a2'] >= 0)
    return np.logical_and(in_time_a1, in_time_a2)


def is_conflict_insector(df, vertex):
    """Check whether spatial boundaries are fullfilled.
    """
    bbPath = mplPath.Path(vertex, closed=True)
    points = np.array([df['Xc'],df['Yc']]).T
    return bbPath.contains_points(points, radius=1e-9)


def is_point_insector(x, y, vertex):
    """Check whether spatial boundaries are fullfilled.
    """
    bbPath = mplPath.Path(vertex, closed=True)
    points = np.array([x,y]).T
    return bbPath.contains_points(points, radius=1e-9)


def fetch_any_key(indict):
    return np.random.choice(list(indict.keys()))


def fetch_largest_conflict(conflicts):
    sz = 0
    conflict = None
    for c in conflicts.values():
        if len(c) > sz:
            sz = len(c)
            conflict = c
    if conflict is None:
        return None
    else:
        return conflict.copy()


def fetch_smallest_conflict(conflicts):
    sz = 1000000
    conflict = None
    for c in conflicts.values():
        if len(c) < sz:
            sz = len(c)
            conflict = c
    return conflict.copy()
