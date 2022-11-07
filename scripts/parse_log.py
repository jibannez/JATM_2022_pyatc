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
    # Process the file passed as command line argument
    # if none is passed, use the default test file
    if len(sys.argv) > 1:

        if os.path.isdir(sys.argv[1]):
            pyatc.parse_log_dir(sys.argv[1])

        elif os.path.isfile(sys.argv[1]):
            pyatc.parse_log(sys.argv[1], export2matlab=True)

    else:
        pyatc.parse_log("./tests/1FATIGUE_2H_Task6.xml.log", export2matlab=True)


if __name__ == '__main__':
    main()
