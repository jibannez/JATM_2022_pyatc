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
import numpy as np
import pandas as pd

from copy import deepcopy
from collections import OrderedDict as OD

from . import util
from . import compute_conflicts
from . import performance as perf

from .cometa_params import COMETAP, PD_FLOAT_FORMAT, FLOW_COMPLEXITY_FACTOR, CONFLICT_COMPLEXITY_FACTOR


############################################################
### HIGHEST LEVEL API FOR COMETA
############################################################

def compute_cometa(taskdict, logdict, flowdict, params, save2mat=False, saveCometa=True):
    """Computes the cometa index using the information specified in the
    dictionaries passed as arguments. This function is used by both cometa_dir
    and cometa_file, which act as wrappers of cometa compution that take paths
    as inputs to generate the dictionaries required by this function.

    Arguments:

        taskdict [OrderedDict]:
            Description of the task stored in a hierarchical structure that replicates
            the one used in the xml description of the tasks. This dictionary can be
            manually created within python, or can be automatically created when loading
            an xml description of the task.

        logdict [OrderedDict]:
            Log events created by parse function.

        flowdict [OrderedDict]:
            Description of the flows present in the task. This dictionary is required
            because the xml description does not allow for flows (only individual aircrafts).
            To overcome this limitation we must use an additional

        params [OrderedDict]:
            flag to indicate if we want to disable parallel computation
            of log files.

        save2mat [boolean]:
            flag to indicate if we want the parsed events in the log to be
            saved in mat files for processing in Matlab.
    """
    #######################################################
    # Fetch variables necessary for the analysis:
    #  - conflicts
    #  - trajectories
    #  - flow_interactions
    #  - non_standard aircrafts
    #  - inevolution aircrafts
    #  - crossingpoints
    #######################################################
    print("\n\t"+"·"*30)
    print("\tComputing cometa indexes for log file " + params['logfile'])
    conflicts, trajectories = compute_conflicts(logdict, params, params['tmax'], COMETAP)
    flow_interactions = compute_flow_interactions(params['crossingpoints'], params['flows'])
    aircrafts = util.get_aircrafts_xml(taskdict)
    non_standard = util.get_non_standard_aircrafts(aircrafts, flowdict)
    inevolution = util.get_inevolution_aircrafts(aircrafts)
    crossingpoints = list(params['crossingpoints'].values())

    #######################################################
    # Compute per-aircraft COMETA
    #######################################################
    cometa_aircrafts = OD()
    tlen = 0
    for aname, aircraft in aircrafts.items():
        if aname not in trajectories:
            # Skip aircrafts that are defined in the xml, but does not appear in the log.
            print('\t\t [WARNING] Aircraft %s is defined in the xml, but has no data in the log, it may appear too late in the simulations' % aname)
            continue
        tmp = compute_aircraft_cometa(
            aircraft, conflicts.copy(), flowdict, flow_interactions, crossingpoints, non_standard, inevolution, trajectories)
        if tmp is not None:
            cometa_aircrafts[aname] = tmp
            newtlen = len(tmp['time'])
            if tlen < newtlen:
                tlen = newtlen
                longest = aname

    #######################################################
    # Compute overall COMETA
    #######################################################

    # If we got no aircraft, something is not OK
    if len(cometa_aircrafts) == 0:
        print('[ERROR] something is wrong with the log file. Could not compute anything.')
        return

    # Fetch first aircraft COMETA to use it as a template
    #aname = list(cometa_aircrafts.keys())[0]
    cometadf = cometa_aircrafts[longest][['time']].copy()

    # Fill in with COMETA fields mergin the data of all aircrafts in the sector
    cometadf['COMETA_Flow'] = join_cometa_dfs(cometa_aircrafts, 'COMETA_Flow')
    cometadf['COMETA_Evolution'] = join_cometa_dfs(cometa_aircrafts, 'COMETA_Evolution')
    cometadf['COMETA_Non_Standard'] = join_cometa_dfs(cometa_aircrafts, 'COMETA_Non_Standard')
    cometadf['COMETA_Conflict'] = join_cometa_dfs(cometa_aircrafts, 'COMETA_Conflict')
    cometadf['COMETA_Reduction'] = join_cometa_dfs(cometa_aircrafts, 'COMETA_Reduction')
    cometadf['COMETA'] = join_cometa_dfs(cometa_aircrafts, 'COMETA')
    cometadf = cometadf.set_index(cometadf.time)

    #######################################################
    # Add performance related variables
    #######################################################

    # Add Active conflicts
    cometadf['Active_conflicts'] = join_cometa_dfs(cometa_aircrafts, 'Active_conflicts') / 2

    # Add Active Aircrafts globally and in sector
    dfX = join_cometa_dfs(trajectories, 'x', False)
    dfY = join_cometa_dfs(trajectories, 'y', False)
    dfInsector = join_cometa_dfs(trajectories, 'insector', False)
    cometadf['Active_aircrafts'] = len(dfX.columns) - dfX.isnull().sum(axis=1)
    cometadf['Active_aircrafts_insector'] = dfInsector.sum(axis=1)

    # Add Aircrafts trajectories centroids
    cometadf['CentroidX'] = dfX.sum(axis=1) / cometadf['Active_aircrafts']
    cometadf['CentroidY'] = dfY.sum(axis=1) / cometadf['Active_aircrafts']
    ddfX = dfX.sub(cometadf['CentroidX'], axis=0)
    ddfY = dfY.sub(cometadf['CentroidY'], axis=0)
    cometadf['Distance2Centroid'] = np.sqrt(ddfX**2 + ddfY**2).mean(axis=1)

    # Add mouse clicks
    try:
        mevents = perf.get_mouse_press_events(logdict)
        dfclk = perf.get_windowed_mouse_press_events(mevents, bins=64) # every 30 seconds
        cometadf = cometadf.join(dfclk, rsuffix='_clicks')
        cometadf.clicks = cometadf.clicks.fillna(method='pad')
        cometadf.time_clicks = cometadf.time_clicks.fillna(method='pad')
        clickidxs = np.where(cometadf.clicks.diff())[0]
        cometadf['TotalClicks'] = cometadf.clicks[clickidxs].sum()
    except:
        # This is probably a pasive trial
        cometadf['TotalClicks'] = 0
        cometadf['clicks'] = 0
        cometadf['time_clicks'] =  0

    # Add user interventions
    [level, speed, total] = perf.get_interventions(logdict)
    cometadf['altitude_interventions'] = level
    cometadf['speed_interventions'] = speed

    # Add accept reaction times
    rtimes = perf.get_accept_reaction_time(logdict).set_index('time')
    cometadf['accept_RT'] = rtimes.rt

    # Add compliance with the exit speeds and altitudes specified in flightplan
    altitude_out = perf.altitude_out(params, trajectories)
    speed_out = perf.speed_out(params, trajectories)
    if len(altitude_out) == 0:
        cometadf['exit_altitude_success'] = 0
    else:
        cometadf['exit_altitude_success'] = altitude_out.altitude_ok.sum() / len(altitude_out)
    if len(speed_out) == 0:
        cometadf['exit_speed_success'] = 0
    else:
        cometadf['exit_speed_success'] = speed_out.speed_ok.sum() / len(speed_out)

    #######################################################
    # Save results to csv
    #######################################################
    if saveCometa:
        fname = params['logfile'] + '_COMETA.csv'
        fpath = os.path.join(params['pathname'], fname)
        cometadf.to_csv(fpath, index=False, sep=',', float_format=PD_FLOAT_FORMAT)

    return cometadf, cometa_aircrafts, conflicts, trajectories


def compute_aircraft_cometa(aircraft, conflicts, flowdict, flow_interactions, crossingpoints, non_standard, inevolution, trajectories):
    """Compute complexity values obtained with cometa equations for a given
    aircraft.
    This function follows step by step the computations exposed in CRIDA's
    lastest technical report of COMETA.
    """
    #################################################################
    #0a - Use conflicts dataframe as template to store all cometa values
    #################################################################
    #tmpdf = util.fetch_largest_conflict(conflicts)
    #if tmpdf is None:
    #    print('WARNING: No conflicts provided!!!')
    #    tmpdf = trajectories[aircraft['idx']]
    #cometadf = tmpdf.loc[:,['time']].copy()
    dfX = join_cometa_dfs(trajectories, 'x', False)
    cometadf = dfX.index.to_frame(name='time')
    cometadf['inregion'] = ~dfX[aircraft['idx']].isnull()

    #################################################################
    #0b - Use trajectory of this plane to fill insector column
    #################################################################
    cometadf['insector'] = trajectories[aircraft['idx']]['insector']
    cometadf.loc[cometadf['insector'].isnull(),'insector'] = False

    #################################################################
    # 1 - Add flow-interaction related complexities
    #################################################################
    flowname = None
    for (flow1, flow2), severity in flow_interactions.items():
        # If the aircraft does not belong to any of the two flows, skip
        if util.is_in_flow(aircraft['idx'], flowdict[flow1]):
            flowname = flow1
        elif util.is_in_flow(aircraft['idx'], flowdict[flow2]):
            # At this point, this should be a taulogy
            flowname = flow2
        else:
            continue

        # Create a name for the new column that will store the values
        colname = 'COMETA_Flow_%s_%s' % (flow1,flow2)
        scolname = 'Severity_%s_%s' % (flow1,flow2)
        # Store severity separatedly
        cometadf[scolname] = severity

        # Fetch the invalid indexes due to COMETA constraints
        # Assign complexity value according to severities and thresholds
        if severity < COMETAP['umbral_i2']:
            cometadf[colname] = COMETAP['i3']

        elif severity > COMETAP['umbral_i1']:
            cometadf[colname] = COMETAP['i1']

        else:
            cometadf[colname] = COMETAP['i2']

        # Parameter to reduce the weight of flows in complexity
        cometadf[colname] =  cometadf[colname] * FLOW_COMPLEXITY_FACTOR

    # Compute total complexity due to flow interactions
    if flowname is None:
        # Non-standart flight here
        cometadf['COMETA_Flow'] = 0
    else:
        cometadf['COMETA_Flow'] = cometadf.filter(regex='COMETA_Flow_').sum(axis=1)

    #################################################################
    # 2 - Add non-standard aircrafts related complexities
    #################################################################
    if aircraft['idx'] in non_standard:
        cometadf['COMETA_Non_Standard'] = COMETAP['noestandar']
    else:
        cometadf['COMETA_Non_Standard'] = 0

    #################################################################
    # 3 - Add inevolution related complexities
    #################################################################
    if aircraft['idx'] in inevolution:
        cometadf['COMETA_Evolution'] = COMETAP['evolucion']
    else:
        cometadf['COMETA_Evolution'] = 0

    #################################################################
    # 4 - Add conflict-related complexities
    #################################################################
    for cname, df in conflicts.items():
        air1, air2 = cname.split('_')[:2]
        lastsuffix = cname.split('_')[-1]
        if lastsuffix in [air1, air2]:
            lastsuffix = None

        # Skip conflicts unrelated to the current aircraft
        if aircraft['idx'] == air1:
            suffix = 'a1'
            suffix2 = air2
        elif aircraft['idx'] == air2:
            suffix = 'a2'
            suffix2 = air1
        else:
            continue

        if lastsuffix is not None:
            suffix2 = '_'.join([suffix2, lastsuffix])

        # Copy df because we'll be modifying it
        df = df.copy()

        # Check constraints
        """
        if flowname is not None and util.is_in_flow(air1, flowdict[flowname]) and util.is_in_flow(air2, flowdict[flowname]):
            # Skip conflicts of aircrafts in the same flow (as per CRIDA specification)
            continue
        """
        # Set template for new column names
        template = 'Severity_Conflict_A%d_%s'

        # Update indexes if the conflict is shorter than the total simulation
        if len(df.time) != len(cometadf.time):
            #df = df.merge(cometadf[['time']],on='time',how='right',suffixes=(None, "_LARGER"))
            df = df.join(cometadf[['time']], how='outer', rsuffix="_LARGER")
            df.loc[df['inconflict'].isnull(),'inconflict'] = False
            df.loc[df['isconflictinsector'].isnull(),'isconflictinsector'] = False

        # Store conflict-specific flags
        cometadf['isconflictinsector_'+suffix2] = df['isconflictinsector']
        cometadf['inconflict_'+suffix2] = df['inconflict']
        cometadf['inconflictGIPYM_'+suffix2] = df['inconflictGIPYM']
        cometadf['inconflictCOMETA_'+suffix2] = df['inconflictCOMETA']

        # Get boolean to remove timestamps without conflict or with the aircraft outside sector/range
        bnoconflict = df['inconflict'] == False  #or cometadf['isconflictinsector'] == False

        # A1: Conflict severity due to horizontal distance in meters
        colname1 = template % (1,cname)
        cometadf[colname1] = df['A1_dist_a1_a2'] # Apparently they use the meters verbatim
        cometadf.loc[bnoconflict, colname1] = 0

        # A2: Conflict severity due to distance from conflict point to sector
        colname2 = template % (2, cname)
        cometadf[colname2] = COMETAP['A2_nofrontera']
        bsectordist = df['A2_hdist_conflict_sector'] < COMETAP['umbral_distancia_conflicto']
        cometadf.loc[bsectordist, colname2] = COMETAP['A2_frontera']
        cometadf.loc[bnoconflict, colname2] = 0

        # A3: Conflict severity due to convergence between routes
        colname3 = template % (3,cname)
        cometadf[colname3] = COMETAP['A3_noconvergente']
        bconvergence = df['THc'] < COMETAP['umbral_angulo']
        cometadf.loc[bconvergence, colname3] = COMETAP['A3_convergente']
        boverlap = np.isnan(df['THc'])
        cometadf.loc[boverlap, colname3] = 1
        cometadf.loc[bnoconflict, colname3] = 0

        # A4: Conflict severity due to proximity to standard flows crossing points
        colname4 = template % (4,cname)
        cometadf[colname4] = COMETAP['A4_nocritico']
        # Again seems odd to have critial conflicts with higher than threshold distances
        bcrossing = df['A4_hdist_conflict_crossingpoints'] > COMETAP['umbralcritico']
        cometadf.loc[bcrossing, colname4] = COMETAP['A4_critico']
        cometadf.loc[bnoconflict, colname4] = 0

        # A5: Conflict severity due to relative temporal proximity
        """

        THIS FACTOR IS NOT USED IN THE EXTENDED VERSION OF COMETA

        colname5 = template % (5,cname)
        #cometadf[colname4] = COMETAP['A4_nocritico']
        #bcrossing = df['A4_hdist_conflict_crossingpoints'] > COMETAP['umbralcritico']
        #cometadf.loc[bcrossing, colname4] = COMETAP['A4_critico']
        # The exponential goes from 1 to 0, because the range of the relative time to conflict
        # goes from 1 (the timing difference at the critical point is equal to the maximum
        # difference, which implies that one aircraft is already at the critical point)
        # to 0 (the timing difference is exactly the same, they will collide at time)
        # so the factor should be higher than 1, somewhere between 2 and 4 I guess.
        #cometadf[colname5] = np.exp(-df['A5_relative_time2conflict']) * COMETAP['A5_factor']
        cometadf[colname5] = df['A5_relative_time2conflict'] * COMETAP['A5_factor']
        cometadf.loc[bnoconflict, colname5] = 0
        """

        # Overall conflict severity for this event
        colnameS = 'Total_Conflict_Severity_'+cname
        cometadf[colnameS] = cometadf[colname1] * cometadf[colname2] * cometadf[colname3] * cometadf[colname4] #* cometadf[colname5]

        # Conflict complexity
        colnameC = 'COMETA_Conflict_'+cname
        cometadf[colnameC] = COMETAP['c2']
        bumbralc1 = cometadf[colnameS] > COMETAP['umbral_c1']
        cometadf.loc[bumbralc1, colnameC] = COMETAP['c1']
        bumbralc2 = cometadf[colnameS] < COMETAP['umbral_c2']
        cometadf.loc[bumbralc2, colnameC] = COMETAP['c3']
        cometadf.loc[bnoconflict, colnameC] = 0

        # Parameter to increase the weight of conflicts in complexity
        cometadf[colnameC] =  cometadf[colnameC] * CONFLICT_COMPLEXITY_FACTOR

    #################################################################
    # Compute overall conflict related complexity
    #################################################################
    cometadf['COMETA_Conflict'] = cometadf.filter(regex='COMETA_Conflict_').sum(axis=1)

    #################################################################
    # Remove complexity from timestamps where the aircraft is not in sector
    #################################################################
    cometadf.loc[cometadf['insector'] == False, 'COMETA_Flow'] = 0
    cometadf.loc[cometadf['insector'] == False, 'COMETA_Non_Standard'] = 0
    cometadf.loc[cometadf['insector'] == False, 'COMETA_Evolution'] = 0
    cometadf.loc[cometadf['insector'] == False, 'COMETA_Conflict'] = 0

    #################################################################
    # Compute overall COMETA
    #################################################################
    cometadf['COMETA'] = COMETAP['a'] * cometadf['COMETA_Flow'] +\
                         COMETAP['b'] * cometadf['COMETA_Evolution'] +\
                         COMETAP['c'] * cometadf['COMETA_Non_Standard'] +\
                         COMETAP['d'] * cometadf['COMETA_Conflict'] + 1

    #################################################################
    # Reduce complexity if all factors are zero
    #################################################################
    cometadf['COMETA_Reduction'] = 0
    cometadf.loc[cometadf['COMETA'] == 1, 'COMETA_Reduction'] = COMETAP['reduccion']
    cometadf['COMETA'] -= cometadf['COMETA_Reduction']

    #################################################################
    # Remove any cometa related value if aircraft is not region
    #################################################################
    cometadf.loc[cometadf['inregion'] == False, 'COMETA'] = 0
    cometadf.loc[cometadf['inregion'] == False, 'COMETA_Reduction'] = 0

    ####################################################################
    # Add performance related variables
    ####################################################################
    cometadf['Active_conflicts'] = cometadf.filter(regex='inconflict_').sum(axis=1).values

    return cometadf


############################################################
### COMETA UTILITY FUNCTIONS
############################################################

def join_cometa_dfs(cometa_aircrafts, field, do_sum=True, index=None):
    names = cometa_aircrafts.keys()
    cometa_lst = [cometa_aircrafts[k][field] for k in names]
    cometa_df = pd.concat(cometa_lst, axis=1)#.sort_index()
    cometa_df.columns = names
    #if 'time' in cometa_df and np.any(cometa_df.time.diff()>1):
    #    cometa_df = cometa_df.sort_index()
    #cometa_df = cometa_df.set_index('time').sort_index()
    if index is not None:
        cometa_df = cometa_df.set_index(index)

    if do_sum:
        return cometa_df.sum(axis=1)
    else:
        return cometa_df


def compute_flow_interactions(crossingpoints, flows):
    interactions = OD()
    for flow1, flow2 in crossingpoints:
        # Fetch flows
        f1 = flows[flow1]
        f2 = flows[flow2]

        # Fetch flow occupations
        Oc1 = f1['occupation']
        Oc2 = f2['occupation']

        # Fetch elevation change for flow1
        if f1['altitude'] > f1['altitude_end']:
            elevation1 = -1
        elif f1['altitude'] < f1['altitude_end']:
            elevation1 = 1
        else:
            elevation1 = 0

        # Fetch elevation change for flow2
        if f2['altitude'] > f2['altitude_end']:
            elevation2 = -1
        elif f2['altitude'] < f2['altitude_end']:
            elevation2 = 1
        else:
            elevation2 = 0

        # Compute interaction type
        if elevation1 == 0 and elevation2 == 0:
            # T = 0 for equal sense not used, though not likely happening in our tasks
            T = COMETAP['interaccion1']
        elif (elevation1 == 0 and elevation2 != 0) or (elevation2 == 0 and elevation1 != 0):
            T = COMETAP['interaccion2']
        elif (elevation1 < 0 and elevation2 < 0) or (elevation1 > 0 and elevation2 > 0):
            T = COMETAP['interaccion3']
        elif (elevation1 < 0 and elevation2 > 0) or (elevation1 > 0 and elevation2 < 0):
            T = COMETAP['interaccion4']

        # Store in dictionary
        interactions[(flow1, flow2)] = T * Oc1 * Oc2

    return interactions
