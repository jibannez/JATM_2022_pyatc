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
import pathlib
import random

src_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
test_path = src_path.parent.joinpath('tests')


# Assure the same pseudorandom sequence is produced for similar runs
# of the algorithm, setting an arbitrary but fixed seed.
random.seed(2047)

eps_route = .1 # For two aircrafts to overlap they must be closer than eps_route nautical miles
eps = 0.01     # Amount to jitter perfectly perpendicular vectors

DEBUG = False

from . import util
from . import performance
from . import task
from . import xml
from . import geom
from . import conflicts_segments as conflicts
from .conflicts_segments import compute_conflicts

from . import plot
from . import parse

from . import anim
from . import cometa
from . import cometa_params
from . import runners
from . import test

from .task import DEFAULT as DEFAULT_TASK
from .xml import ATCXMLConfig, generate_xml, load_xml, load_taskdict
from .parse import run_directory as parse_log_dir
from .parse import run as parse_log
from .runners import *
from . import exp1


try:
    import pkg_resources.py2_warn #Fixes bug in pyinstaller with setuptools>14
except ImportError:
    pass
