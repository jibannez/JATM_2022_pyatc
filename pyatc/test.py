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

from collections import OrderedDict as OD

from . import test_path
from . import util
from .cometa import compute_cometa, COMETAP


def run_test(testno=1, conflict_dist=4.0, tmax=60):
    """
    """
    # Store results in a dict
    res = OD()
    res['tmax'] = tmax
    res['conflict_dist'] = conflict_dist

    # Change value of distance to conflict
    default_dist = COMETAP['umbral_distancia_conflicto']
    COMETAP['umbral_distancia_conflicto'] = conflict_dist
    
    # Prepare paths
    res['taskname'] = "T%d.xml" % testno
    res['logname'] = res['taskname'] + '.log'
    res['logpath'] = str(test_path.joinpath('logs', res['logname']))
    res['taskpath'] = str(test_path.joinpath('tasks', res['taskname']))
    
    # Fetch task properties
    res['taskdict'], res['logdict'], res['flowdict'], res['params'] = util.prepare_cometa_data(
        res['logpath'], res['taskpath'], res['tmax'], False)
    
    res['cometadf'], res['aircrafts_cometa'], res['conflicts'], res['trajectories'] = compute_cometa(
        res['taskdict'], res['logdict'], res['flowdict'], res['params'], False)

    # Restore distance value
    COMETAP['umbral_distancia_conflicto'] = default_dist
    
    return res


def run_all_tests(conflict_dist=4.0, tmax=30):
    res = OD()
    for testno in range(1,17):
        res[testno] = run_test(testno, conflict_dist, tmax)
    return res


def debug_cometa_computations(cometa, aircrafts, conflicts, trjs, rows=range(0,50), aircraft=None):
    """This is an old function, not very usefull right now
    """
    # Fetch one aircraft to do the detailed debugging
    if isinstance(aircrafts,OD) and (aircraft is None or aircraft not in aircrafts):
        aname = util.fetch_any_key(aircrafts)
        aircraft = aircrafts[aname]
    print(cometa_aircrafts[aircraft].loc[rows, :])
    print(trjs[aircraft].loc[rows, :])
    for cname in conflicts.keys():
        air1, air2 = cname.split('_')
        # Skip conflicts unrelated to the current aircraft
        if aircraft['idx'] != air1 and aircraft['idx'] != air2:
            continue
        elif aircraft['idx'] == air1:
            suffix = '_a1'
        elif aircraft['idx'] == air2:
            suffix = '_a2'
        print(conflicts[cname].loc[rows,:])
