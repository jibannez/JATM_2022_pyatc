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

import sys
import pyatc

def main():
    if len(sys.argv) > 1:
        res = pyatc.parse_log(sys.argv[1])
    else:
        res = pyatc.parse_log('GIPYM_EscenarioA4_CargaBaja.xml.log')

    conflicts, aircrafts = pyatc.compute_conflicts(res)
    cometa = pyatc.compute_cometa(conflicts)

    # The next line is way too heavy because it creates more than 100 figures.
    # To avoid clutter, I comment this out. The purpose of this main section
    # is simply to illustrate how to use this library.
    #pyatc.plot_cometa_scores(conflicts)


if __name__ == '__main__':
    main()

