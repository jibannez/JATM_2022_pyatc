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

from collections import OrderedDict as OD

from . import util
from .runners import runparallel
from .plot import plot_cometa_timeseries, plot_cometa_barplots


########################################################################
## OLD SAMPLE experimental design related functions
########################################################################

def get_exp_design(lognames, logpath, taskpath='./task', tmax=600, save2mat=False):
    cometa = OD()
    configs = list()
    # Prepare configurations for parallel batch processing of trials
    for logfile in lognames:
        # Fetch data and model specfications for COMETA compute
        logfilepath = os.path.join(logpath,logfile)
        taskdict, logdict, flowdict, params = util.prepare_data(logfilepath, taskpath, tmax, save2mat)
        configs.append([logfile, taskdict, logdict, flowdict, params, save2mat])

    # Run the worker function in parallel
    res = runparallel(_cometa_file_worker, configs)

    # Store the results
    for (logfile, tr_cometa, tr_cometa_aircrafts, tr_conflicts, tr_trjs) in res:
        cometa[logfile] = tr_cometa

    # Plot time series
    plot_cometa_timeseries(cometa)

    #Plot barplots of average cometa values
    plot_cometa_barplots(cometa)

    return cometa


def get_exp_design_compare(logpath='./data', taskpath='./task', tmax=600, save2mat=False):
    """Custom function to show COMETA index values for the different levels of the experimental
    task in passive and active conditions (without or with intervention)"""
    passive_lognames = [ 'Pasivo_%s.log' % task for task in TASKNAMES]
    active_lognames = [ 'Activo_%s.log' % task for task in TASKNAMES]
    passive_cometa = get_exp_design(passive_lognames, logpath, taskpath, tmax, save2mat)
    active_cometa = get_exp_design(active_lognames, logpath, taskpath, tmax, save2mat)
    return passive_cometa, active_cometa
