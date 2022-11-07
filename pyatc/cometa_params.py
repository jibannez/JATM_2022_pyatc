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

from collections import OrderedDict as OD

# Small trick to force pandas to show full dataframe contents. Useful for debugging.
# Comment these two lines to get the original, prettier, behavior.
#pd.options.display.max_rows = None
#pd.options.display.width = 0
PD_FLOAT_FORMAT = "%.2f"

# Get rid of useless warnings
np.warnings.filterwarnings('ignore')

# Global names
FIGPATH = './figures'

# Hacks to reduce the weight of flow interactions
# A better approach would be to use the insector aircrafts at each point
# This is not valid either, but at least would be closer
FLOW_OCCUPATION_FACTOR = 1
FLOW_COMPLEXITY_FACTOR = 1
CONFLICT_COMPLEXITY_FACTOR = 1

############################################################
### COMETA PARAMETER VALUES, OBTAINED DIRECTLY FROM
### CRIDA'S REPORT
############################################################
COMETAP = OD([
    ('interaccion1', 1.0),
    ('interaccion2', 2.0),
    ('interaccion3', 3.0),
    ('interaccion4', 4.0),
    ('i1', .2),
    ('i2', .1),
    ('i3', .05),
    ('umbral_i1', 32.0),
    ('umbral_i2', 25.0),
    ('noestandar', .15),
    ('evolucion', .1),
    ('c1', .1),
    ('c2', .2),
    ('c3', .3),
    ('umbral_c1', 9260.0),
    ('umbral_c2', 4630.0),
    ('umbral_altitud_conflicto', 800),
    ('umbral_distancia_conflicto', 10),
    ('A2_frontera', 1.02),
    ('A2_nofrontera', .9),
    ('umbral_angulo', 90),
    ('A3_convergente', 1.1),
    ('A3_noconvergente', .8),
    ('umbralcritico', 1500.0),
    ('A4_critico', 1.05),
    ('A4_nocritico', .9),
    ('A5_factor', 3),
    ('reduccion', .5),
    ('a', 1),
    ('b', 10),
    ('c', 5),
    ('d', 20),
    ('nm2meters', 1852),
    ])

COMETA_NAMES = ['COMETA_Flow','COMETA_Evolution','COMETA_Non_Standard','COMETA_Conflict','COMETA_Reduction','COMETA']

# Default parameters used in performance computations
# Better load them using get_cometa_simulation_parameters
PARAM = {
    'xmin': -200,
    'xmax': 300,
    'ymin': -200,
    'ymax': 300,
    'tmax': 600, # forecast trajectories for 10 minutes
    'locations': dict(),
    'routes': dict(),
    'flows': dict(),
    'aircrafts': dict(),
    }

CALL_NAMES = ['time', 'name', 'model', 'control', 'x', 'y', 'z', 'speed', 'heading', 'climb', 'power']


