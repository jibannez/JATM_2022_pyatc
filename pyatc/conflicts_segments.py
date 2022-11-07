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
import itertools
import pandas as pd
import numpy as np

from collections import OrderedDict as OD

from . import util
from .geom import get_distance_to_sector, get_distance_to_crossing_points, find_intersection, get_angle_between_vectors
from .cometa_params import COMETAP, CALL_NAMES
from . import eps_route


##################################################################################

def compute_aircrafts_trjs(logdict, sector):
    if isinstance(logdict, pd.DataFrame):
        logdf = logdict
    else:
        logdf = pd.DataFrame(logdict['call_update'], columns=CALL_NAMES)

    # ROUND TIMES TO SECONDS
    logdf.time = (logdf.time/1000).round()

    # Compute aircrafts trajectories
    trajectories = OD()
    for name in logdf.name.unique():
        trajectories[name] = util.compute_aircraft_trjs(logdf, name, sector)
    return trajectories


def compute_conflicts(logdict, params, tmax=600, cometap=COMETAP):
    """Compute pairwise conflicts between aircrafts. A conflict can be empty
    if the two aircrafts do not encounter.
    """
    crossingpoints = params['crossingpoints']
    sector = params['sector']
    trajectories = compute_aircrafts_trjs(logdict, sector)

    # Compute all potential interactions between predefined aircraft trajectories
    potential_interactions = get_potential_interactions(params)

    # Compute aircrafts conflicts
    conflicts = OD()
    for aname1, air1_interactions in potential_interactions.items():
        # Fetch information from first aircraft
        if aname1 not in trajectories:
            continue
        air1 = trajectories[aname1]
        locs1 = params['aircrafts'][aname1]['flightpath']

        # Loop around all aircrafts that potentially conflict with air1
        for aname2, (crossings, overlaps) in air1_interactions.items():
            # Fetch information from second aircraft
            if aname2 not in trajectories:
                continue
            air2 = trajectories[aname2]
            locs2 = params['aircrafts'][aname2]['flightpath']

            # Crossing conflicts
            for i, crossing in enumerate(crossings.values()):
                # Create name of new conflict between two aircrafts
                name = '_'.join([aname1, aname2,'C'+str(i)])
                # compute and store conflict
                conflicts[name] = compute_crossing_conflict(crossing, air1, air2, locs1, locs2, sector, crossingpoints, tmax, cometap)

            # Overlap conflicts should be computed here
            for i, (overlapk, overlapv) in enumerate(overlaps.items()):
                # Create name of new conflict between two aircrafts
                name = '_'.join([aname1, aname2,'O'+str(i)])
                name2 = '_'.join([aname2, aname1,'O'])
                current_conflicts = conflicts.keys()
                flagcomputed = False
                for conname in current_conflicts:
                    if name2 in conname:
                        flagcomputed = True
                        break

                # compute and store conflict
                if flagcomputed == False:
                    conflicts[name] = compute_overlap_conflict(overlapk, overlapv, air1, air2, locs1, locs2, sector, crossingpoints, tmax, cometap)

    return conflicts, trajectories


def compute_crossing_conflict(crossing, air1, air2, locs1, locs2, sector, crossingpoints, tmax, cometap):
    # Merge dataframes to store properties of the conflicts between this two planes
    df = pd.merge(air1, air2, 'outer', 'time', suffixes=('_a1','_a2'))
    df = df.set_index(df.time.values)#.sort_index()

    def get_ttc_a1(df):
        return get_time_to_location(locs1, (df['x_a1'],df['y_a1']), (df['Xc'],df['Yc']), df['v_a1'])

    def get_ttc_a2(df):
        return get_time_to_location(locs2, (df['x_a2'],df['y_a2']), (df['Xc'],df['Yc']), df['v_a2'])

    # Compute_paired_conflicts
    df['Xc'] = crossing[0][0]
    df['Yc'] = crossing[0][1]
    df['Tc_a1'] = df.apply(get_ttc_a1, axis=1)
    df['Tc_a2'] = df.apply(get_ttc_a2, axis=1)
    df['Tc_max'] = df[['Tc_a1', 'Tc_a2']].max(axis=1)
    df['Tc_diff'] = np.abs(df['Tc_a1'] - df['Tc_a2'])

    # Add cometa-related conflic values, this does not depend on the type of conflict
    _add_cometa_values(df, sector, crossingpoints, tmax, cometap, crossing[1])

    return df


def compute_overlap_conflict(overlapk, overlapv, air1, air2, locs1, locs2, sector, crossingpoints, tmax, cometap):
    # Merge dataframes to store properties of the conflicts between this two planes
    df = pd.merge(air1, air2, 'outer', 'time', suffixes=('_a1','_a2'))
    df = df.set_index(df.time.values)

    # Local instance of the start and end points of the overlap segment
    [(x0,y0),(x1,y1)] = overlapv

    # Detect if they follow the route in the same sense, pick first pair
    A1, B1 = locs1[overlapk[0]], locs1[overlapk[0]+1]
    A2, B2 = locs2[overlapk[1]], locs2[overlapk[1]+1]
    V1 = [B1[0]-A1[0], B1[1]-A1[1]]
    V2 = [B2[0]-A2[0], B2[1]-A2[1]]
    bopposite = np.dot(V1,V2) < 0
    df['bopposite'] = bopposite

    def get_ttc_solidary(df):
        # Local instances to avoid referencing overhead
        pos1 = (df['x_a1'],df['y_a1'])
        pos2 = (df['x_a2'],df['y_a2'])
        v1 = df['v_a1']
        v2 = df['v_a2']

        # Get relative position/timing with respect to the entry node.
        dtos_a1 = get_distance_to_location(locs1, pos1, (x0,y0))
        dtos_a2 = get_distance_to_location(locs2, pos1, (x0,y0))

        # Return NaN if any aircraft cannot reach entry point
        if np.isnan(dtos_a1) or np.isnan(dtos_a2):
            #print('1')
            return np.nan

        if dtos_a1<0 or dtos_a2<0:
            ##############################################################
            # Any of the aircrafts have crossed the initial crossing point,
            ##############################################################

            # Get relative position/timing with respect to the exit node.
            dtoe_a1 = get_distance_to_location(locs1, pos1, (x1,y1))
            dtoe_a2 = get_distance_to_location(locs2, pos2, (x1,y1))
            #print('Distance of short loc: '+str(dtoe_a2))

            # Return NaN if any aircrafts cannot reach exit point
            if np.isnan(dtoe_a1) or np.isnan(dtoe_a2):
                #print('2')
                return np.nan

            # If any of the two have crossed the final crossing point, then
            # no overlap is possible.
            if dtoe_a1 < 0 or dtoe_a2 < 0:
                #print('3')
                return np.nan

            # Otherwise, attempt to compute TTC
            if dtoe_a1 >= dtoe_a2:
                # Conflict is impossible if the further plane is faster
                if v2 >= v1:
                    #print('4')
                    return np.nan
                # Get relative distance
                ### This is problematic when aircrafts don't share trajectories!!!!!!!
                ## Overlap should not be computed if the two aircrafts
                ## are not in the same segment. If they are in different
                ## segments only crossing conflict is computed
                rdist = get_distance_to_location(locs1, pos1, pos2)

                # Return if one of the points is not in the provided trajectory
                if np.isnan(rdist) or rdist < 0:
                    #print('5')
                    return np.nan

                # Get the time that will take to cancel the gap
                tgap = rdist / (v1 - v2)

                # If the cancellation takes longer than the time until the
                # further aircraft leaves the overlap, return nan
                if tgap > dtoe_a2 / v2:
                    #print('6')
                    return np.nan
                else:
                    #print(80*':')
                    return tgap

            else:
                # Conflict is impossible if the further plane is faster
                if v1 >= v2:
                    #print('7')
                    return np.nan

                # Get relative distance
                rdist = get_distance_to_location(locs2, pos2, pos1)

                # Return if one of the points is not in the provided trajectory
                if np.isnan(rdist) or rdist < 0:
                    #print('8')
                    return np.nan

                # Get the time that will take to cancel the gap
                tgap = rdist / (v2-v1)
                # If the cancellation takes longer than the time until the
                # further aircraft leaves the overlap
                if tgap > dtoe_a1 / v1:
                    #print('9')
                    return np.nan
                else:
                    #print(80*'.')
                    return tgap

        else:
            ##############################################################
            # Both aircrafts have not entered the overlap segment yet
            ##############################################################

            # Compute the time it remains until both reach the segment
            ttos_a1 = dtos_a1 / v1
            ttos_a2 = dtos_a2 / v2

            # Check if the one that arrives later can catch up
            if ttos_a1 < ttos_a2:
                # Conflict is impossible if the further plane is faster
                if v1 >= v2:
                    #print('10')
                    return np.nan

                # Compute distance between aircrafts when the last one
                # is at the entry node of the overlap.
                newpos = get_location_at_time(locs1, pos1, v1, ttos_a2)
                if newpos is None:
                    #print('11')
                    return np.nan
                ttleave = get_time_to_location(locs1,newpos,(x1,y1),v1)
                rdist = get_distance_to_location(locs2, (x0,y0), newpos)

                # Return if one of the points is not in the provided trajectory
                if np.isnan(rdist) or rdist < 0:
                    #print('12')
                    return np.nan

                # Compute the time required to close a gap of rdist with a
                # relative velocity of v2-v1
                tgap = rdist / (v2-v1)
                if tgap > ttleave:
                    # The further aircraft cannot be overtaken in the overlap
                    #print('13')
                    return np.nan
                else:
                    #print(80*'-')
                    return tgap
            else:
                # Conflict is impossible if the further plane is faster
                if v2 >= v1:
                    #print('14')
                    return np.nan

                # Compute distance between aircrafts when the last one
                # is at the entry node of the overlap.
                newpos = get_location_at_time(locs2, pos2, v2, ttos_a1)
                if newpos is None:
                    #print('15')
                    return np.nan
                ttleave = get_time_to_location(locs2,newpos,(x1,y1),v2)

                rdist = get_distance_to_location(locs1, (x0,y0), newpos)

                # Return if one of the points is not in the provided trajectory
                if np.isnan(rdist) or rdist < 0:
                    #print('16')
                    return np.nan

                # Compute the time required to close a gap or rdist with a
                # relative velocity of v2-v1
                tgap = rdist / (v1-v2)
                if tgap > ttleave:
                    # The further aircraft cannot be overtaken in the overlap
                    #print('17')
                    return np.nan
                else:
                    #print(80*'+')
                    return tgap

    def get_ttc_opposite(df):
        # Get relative position/timing with respect to the entry node.
        rdist1 = get_distance_to_location(locs1, (df['x_a1'],df['y_a1']), (df['x_a2'],df['y_a2']))
        rdist2 = get_distance_to_location(locs2, (df['x_a2'],df['y_a2']), (df['x_a1'],df['y_a1']))
        if not (np.isnan(rdist1) or rdist1 < 0):
            return rdist1 / (df['v_a1']+df['v_a2'])
        elif not (np.isnan(rdist2) or rdist2 < 0):
            return rdist2 / (df['v_a1']+df['v_a2'])
        else:
            return np.nan

    def get_Xc(df):
        if np.any(np.isnan([df['x_a1'],df['y_a1'],df['v_a1'],df['Tc_a1']])):
            return np.NaN
        return get_location_at_time(locs1,(df['x_a1'],df['y_a1']),df['v_a1'],df['Tc_a1'])[0]

    def get_Yc(df):
        if np.any(np.isnan([df['x_a1'],df['y_a1'],df['v_a1'],df['Tc_a1']])):
            return np.NaN
        return get_location_at_time(locs1, (df['x_a1'],df['y_a1']), df['v_a1'], df['Tc_a1'])[1]

    # Compute_paired_conflicts
    if bopposite:
        df['Tc_a1'] = df.apply(get_ttc_opposite, axis=1)
    else:
        df['Tc_a1'] = df.apply(get_ttc_solidary, axis=1)

    df['Tc_a2'] = df['Tc_a1']
    df['Xc'] = df.apply(get_Xc, axis=1)
    df['Yc'] = df.apply(get_Yc, axis=1)
    df['Tc_max'] = df[['Tc_a1', 'Tc_a2']].max(axis=1)
    df['Tc_diff'] = np.abs(df['Tc_a1'] - df['Tc_a2'])

    _add_cometa_values(df, sector, crossingpoints, tmax, cometap, np.NaN, True)

    return df


def _add_cometa_values(df, sector, crossingpoints, tmax, cometap, THcrossing=np.NaN, isoverlap=False):
    ####################################################################
    # Compute angle between trajectories at the conflict
    # THIS EQUATION LACKS TESTING
    #tantheta = (df['m_a2']-df['m_a1']) / (1 + df['m_a1']*df['m_a2'])
    #df['THc'] = np.rad2deg(np.arctan(tantheta))
    df['THc'] = THcrossing

    ####################################################################
    #Compute spatial and temporal boundaries of the conflict
    df['isconflictinsector'] = util.is_conflict_insector(df, sector)
    df['intime'] = util.is_conflict_intime(df, tmax)

    ####################################################################
    # Compute the altitude of the two planes at the cross point
    #df['Zc_a1'] =  df['Tc_a1']*df['vz_deriv_a1'] + df['z_a1']
    #df['Zc_a2'] =  df['Tc_a2']*df['vz_deriv_a2'] + df['z_a2']
    df['Zc_a1'] =  df['Tc_a1']*df['vz_a1'] + df['z_a1']
    df['Zc_a2'] =  df['Tc_a2']*df['vz_a2'] + df['z_a2']

    ####################################################################
    # Compute conflict variables related with COMETA computation
    ####################################################################

    ####################################################################
    # A0: Check constraints: inside 10NM circle and less than 800 ft appart in altitude
    df['A0_vdist_a1_a2_conflict'] = np.abs(df['Zc_a1'] - df['Zc_a2'])
    df['A0_hdist_a1_conflict'] = np.sqrt((df['x_a1'] - df['Xc'])**2 + (df['y_a1'] - df['Yc'])**2)
    df['A0_hdist_a2_conflict'] = np.sqrt((df['x_a2'] - df['Xc'])**2 + (df['y_a2'] - df['Yc'])**2)

    binconflict_COMETA = (df['A0_vdist_a1_a2_conflict'] < cometap['umbral_altitud_conflicto']) &\
                         (df['A0_hdist_a1_conflict'] < cometap['umbral_distancia_conflicto']) &\
                         (df['A0_hdist_a2_conflict'] < cometap['umbral_distancia_conflicto']) &\
                          df['intime'] & df['isconflictinsector']

    df['A0_distA1A2nm'] = np.sqrt((df['x_a1'] - df['x_a2'])**2 + (df['y_a1'] - df['y_a2'])**2)
    binconflict_GIPYM =  (df['A0_vdist_a1_a2_conflict'] < cometap['umbral_altitud_conflicto']) &\
                         (df['A0_distA1A2nm'] < cometap['umbral_distancia_conflicto']) & df['intime'] & df['isconflictinsector']

    df['inconflictCOMETA'] = binconflict_COMETA
    df['inconflictGIPYM'] = binconflict_GIPYM

    if isoverlap:
        df['inconflict'] = df['inconflictGIPYM']
    else:
        df['inconflict'] = df['inconflictCOMETA']

    ####################################################################
    # A1: Horizontal distance in meters
    df['A1_dist_a1_a2'] = df['A0_distA1A2nm'] * cometap['nm2meters']

    ####################################################################
    # A2: Distance from conflict point to sector border
    df['A2_hdist_conflict_sector'] = get_distance_to_sector(sector[:-1], df['Xc'], df['Yc'])

    ####################################################################
    # A3: Convergence between routes
    df['A3_angle'] = df['THc']

    ####################################################################
    # A4: Proximity from conflict to standard flows crossing points
    df['A4_hdist_conflict_crossingpoints'] =    get_distance_to_crossing_points(crossingpoints, df['Xc'], df['Yc'])
    # When flows are not defined, crossing points may be missing
    bh1 = df['A4_hdist_conflict_crossingpoints'] == False
    bh2 = df['A4_hdist_conflict_crossingpoints'] < 0.5
    bh3 = np.isnan(df['A4_hdist_conflict_crossingpoints'])
    bhdist = np.logical_or(np.logical_or(bh1,bh2),bh3)
    df.loc[bhdist, 'A4_hdist_conflict_crossingpoints'] = 1

    ####################################################################
    # A5: Temporal distance to conflict
    df['A5_relative_time2conflict'] = df['Tc_diff'] / df['Tc_max']


def get_potential_interactions(params, force_self=False):
    interactions = OD()
    for aname1, aircraft1 in params['aircrafts'].items():
        interactions[aname1] = OD()
        for aname2, aircraft2 in params['aircrafts'].items():
            # avoid double and self computation of conflicts
            if aname1 == aname2 and not force_self:
                continue
            is_shared_route = is_same_flow(aname1, aname2, params['flows'])
            # get potential interactions between the two locations
            ret = get_trajectories_interactions(aircraft1['flightpath'], aircraft2['flightpath'], is_shared_route)
            if len(ret[0]) > 0 or len(ret[1]) > 0:
                interactions[aname1][aname2] = ret
    return interactions


def get_trajectories_interactions(locs1, locs2, same_route=False):
    overlaps = OD()
    crossings = OD()
    for i, p1a in enumerate(locs1[:-1]):
        p1b = locs1[i+1]
        for j, p2a in enumerate(locs2[:-1]):
            p2b = locs2[j+1]
            S1 = (p1a, p1b)
            S2 = (p2a, p2b)
            bp1a = is_point_in_segment(p1a, S2)
            bp1b = is_point_in_segment(p1b, S2)
            bp2a = is_point_in_segment(p2a, S1)
            bp2b = is_point_in_segment(p2b, S1)

            ##########################################
            # Check for overlapping trajectories
            ##########################################
            if (bp1a and bp1b) and (bp2a and bp2b):
                # Total overlap between segments
                overlaps[(i,j)] = [p1a,p1b]
            else:
                # Partial overlap: one segment contains the other
                # Need to manually compute the most appropiate overlap
                if (bp1a and bp2a):
                    # The starting point is shared
                    startp = p1a
                elif bp1a:
                    # The locs1 starting point is included in locs2
                    startp = p1a
                elif bp2a:
                    # The locs2 starting point is included in locs1
                    startp = p2a
                else:
                    startp = None

                if (bp1b and bp2b):
                    # The end point is shared
                    endp = p1b
                elif bp1b:
                    # The locs1 starting point is included in locs2
                    endp = p1b
                elif bp2b:
                    # The locs2 starting point is included in locs1
                    endp = p2b
                else:
                    endp = None

                #Add the points if they fullfill constraints
                if (startp is not None) and\
                   (endp is not None) and\
                   (not is_same_point(startp, endp)):
                    overlaps[(i,j)] = [startp, endp]

            ##########################################
            # Check for crossing trajectories
            ##########################################
            # Do not check for crossings if they belong to same route
            if same_route:
                continue

            # Compute segments intersection
            ret = find_intersection(p1a,p1b,p2a,p2b)

            # Reduce redundant crossings, they should only appear once
            cvalues = [crossing[0] for crossing in crossings.values()]
            if ret is not None and ret not in cvalues:
                if is_same_point(p1a, ret):
                    p1a = locs1[i-1]
                if is_same_point(p2a, ret):
                    p2a = locs2[j-1]
                v1 = [p1a[0] - ret[0], p1a[1] - ret[1]]
                v2 = [p2a[0] - ret[0], p2a[1] - ret[1]]
                th = get_angle_between_vectors(v1, v2)
                crossings[(i,j)] = (ret, np.rad2deg(th))

    return crossings, merge_overlaps(overlaps)


def merge_overlaps(overlaps):
    # If we have one or none overlaps
    noverlaps = len(overlaps)
    if noverlaps <= 1:
        return overlaps

    # Iterate over overlaps to merge those whose starting point is the
    # the end point of the previous
    okeys = list(overlaps.keys())
    ovalues = list(overlaps.values())
    newoverlaps = OD()
    for i in range(noverlaps-1):
        startp = ovalues[i][0]
        endp = ovalues[i][1]
        # Iterate over additional segments in overlap
        for j in range(i+1,noverlaps):
            (jstartp, jendp) = ovalues[j]
            if is_same_point(endp, jstartp):
                endp = jendp
            else:
                break
        newoverlaps[okeys[i]] = [startp, endp]
    return newoverlaps


def get_location_at_distance(locs, p, d):
    # Validate input
    if d is None or np.isnan(d) or p[0] is None or p[1] is None:
        return None

    # Locate the point in the trajectory
    sno = get_segment_in_trajectory(locs, p)
    if sno is None:
        #print("The point provided is not part of the trajectory!!")
        return None
    else:
        # We are interested in this index, the end of starting segment
        sno = sno + 1

    # Get first distance
    x1,y1 = p
    x2,y2 = locs[sno]
    d1 = np.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))

    # Check if location is within the current segment
    if d < d1:
        theta = np.arctan2(y2-y1, x2-x1)
        return x1 + d*np.cos(theta), y1 + d*np.sin(theta)
    else:
        distances = [d1]

    # CAREFUL WITH INDEXES HERE!!!!
    # Iterate over segments until the last before
    #for i, (x1,y1) in enumerate(locs[sno:-1]):
    for (x1,y1), (x2,y2) in zip(locs[sno:-1], locs[sno+1:]):
        #(x2,y2) = locs[sno+i+1]
        distances.append(np.sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) ))

    # CAREFUL WITH INDEXES HERE!!!!
    # Compute cumulative distances and compare with required distance
    cumdist = np.cumsum(distances)
    if d > cumdist[-1]:
        # If the distance if beyond the last location, return last location
        return locs[-1]
    else:
        # Get the segment in which the location lies
        idx = np.where(cumdist > d)[0][0]
        x1,y1 = locs[idx]
        x2,y2 = locs[idx+1]
        # Project the remaining distance onto the segment to get coords
        theta = np.arctan2(y2-y1, x2-x1)
        drem = d - cumdist[idx-1]
        return x1 + drem*np.cos(theta), y1 + drem*np.sin(theta)


def get_distance_to_location(locs, p0, p1):
    """Computes the distance between a certain target point or vector
    of points and a vector of current locations.
    """
    # First, determine the segment of trajectory in which p0 and p1 lie
    s0 = get_segment_in_trajectory(locs, p0)
    s1 = get_segment_in_trajectory(locs, p1)

    # If any of the points do not lie in the segments, return NaN
    if s0 is None or s1 is None:
        return np.NaN

    ####################################################################
    # DEPENDING ON THE RELATIVE LOCATION, PREPARE DATA
    ####################################################################
    if s0 == s1:
        # If the two points lie in the same segment, get relative distance
        p = locs[s0]
        dist1 = np.sqrt( (p[0]-p0[0]) * (p[0]-p0[0]) + (p[1]-p0[1]) * (p[1]-p0[1]) )
        dist2 = np.sqrt( (p[0]-p1[0]) * (p[0]-p1[0]) + (p[1]-p1[1]) * (p[1]-p1[1]) )
        return dist2 - dist1
    elif s0 > s1:
        # Sort the points so that p0 always comes first in the trajectory
        tmp=p0; p0=p1; p1=tmp
        tmp=s0; s0=s1; s1=tmp
        d = -1
    else: # s0 < s1
        d = 1

    ####################################################################
    # COMPUTE THE GENERAL CASE: POINTS IN DIFERENT SEGMENTS
    ####################################################################
    # Get the distance from initial point to first segment end
    (x0,y0) = p0
    (x1,y1) = locs[s0+1]
    dist = np.sqrt( (x0-x1) * (x0-x1) + (y0-y1) * (y0-y1) )

    # Add the length of the intermediate segments
    for (x0,y0), (x1,y1) in zip(locs[s0+1:s1], locs[s0+2:s1+1]):
        dist += np.sqrt( (x0-x1) * (x0-x1) + (y0-y1) * (y0-y1) )

    # Add the distance to the target point along the last segment
    (x0,y0) = p1
    (x1,y1) = locs[s1]
    dist += np.sqrt( (x0-x1) * (x0-x1) + (y0-y1) * (y0-y1) )

    return d*dist


def get_location_at_time(locs, p0, v, t):
    """ Computes the location of aircraft after a given time considering
    the locations list, a vector of starting point and a vector of speeds
    """
    return get_location_at_distance(locs,p0,v*t)


def get_time_to_location(locs, p0, p1, v):
    """ Computes the time to a certain location for an aircraft considering
    the locations list, a vector of starting points, a single end point
    and a vector of speeds.
    """
    dist = get_distance_to_location(locs, p0, p1)
    if dist is None:
        return np.NaN
    else:
        return dist / v


def is_point_in_trajectory(locs, p):
    """Checks wether a certain point lies in a given trajectory"""
    for s in zip(locs[:-1],locs[1:]):
        if is_point_in_segment(p, s):
            return True
    return False


def is_point_in_segment(p, s):
    x,y = p; x1,y1=s[0]; x2,y2=s[1]
    AB = np.sqrt( (x2-x1) * (x2-x1) + (y2-y1) * (y2-y1) );
    AP = np.sqrt( (x-x1) * (x-x1) + (y-y1) * (y-y1) );
    PB = np.sqrt( (x2-x) * (x2-x) + (y2-y) * (y2-y) );
    if abs(AB - (AP + PB)) < eps_route:
        return True
    else:
        return False


def get_segment_in_trajectory(locs, p):
    """Checks wether a certain point lies in a given trajectory"""
    for i, s in enumerate(zip(locs[:-1],locs[1:])):
        if is_point_in_segment(p, s):
            return i

def is_same_point(a, b):
    if a[0] == b[0] and a[1] == b[1]:
        return True
    else:
        return False


def is_same_flow(aname1, aname2, flows):
    for rname, rvalues in flows.items():
        if aname1 in rvalues['aircrafts'] and aname2 in rvalues['aircrafts']:
            return True
    return False


