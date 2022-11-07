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

import pyatc

def get_sample_task():
    task = pyatc.DEFAULT_TASK.copy()

    task['region'] = ['250', '-50', '400', '-110']

    task['locations'] = OD([
    # Location of points and routes of the map
    # Horizontal route
    ('R0', OD([('y', '75'), ('x', '-110'), ('visible','on')])),
    ('R1', OD([('y', '75'), ('x', '0'), ('visible','on')])),
    ('R2', OD([('y', '75'), ('x', '180'), ('visible','on')])),
    ('R3', OD([('y', '75'), ('x', '290'), ('visible','on')])),
    # Vertical route
    ('R4', OD([('y', '-50'), ('x', '80'), ('visible','on')])),
    ('R5', OD([('y', '0'), ('x', '80'), ('visible','on')])),
    ('R6', OD([('y', '150'), ('x', '80'), ('visible','on')])),
    ('R7', OD([('y', '200'), ('x', '80'), ('visible','on')])),
    ])

    task['routes'] = OD([
        ('R_Horiz', ['R0', 'R1', 'R2', 'R3']),
        ('R_Vert', ['R4', 'R5', 'R6', 'R7']),
        ])

    task['sector'] = [(0, 0), (150, 0), (150, 180), (0, 180)]

    task['aircrafts'] = OD([
        ('VOZ111', OD([
            ('type', 'A320'),
            ('start', 0),
            ('altitude', 37000),
            ('velocity', 510),
            ('flightpath', [(-50, -110), (200, 290)])
            ])),
        ])

    task['flows'] = OD([
        ('R_Horiz', OD([
            ('type', 'A320'),
            ('basename', 'VOZ21'),
            ('altitude', 37000),
            ('velocity', 510),
            ('time', 30*60), # total time in seconds
            ('occupation', 20), # planes per hour
            ])),
        ('R_Vert', OD([
            ('type', 'A320'),
            ('basename', 'VOZ31'),
            ('altitude', 37000),
            ('velocity', 510),
            ('time', 30*60), # total time in seconds
            ('occupation', 20), # planes per hour
            ])),
        ])
    return task

def main():
    task = get_sample_task()
    fname = 'ATCSampleTask'
    xmltask = pyatc.ATCXMLConfig(task)
    xmltask.save(fname)

if __name__ == '__main__':
    main()


