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
import pandas as pd
from collections import OrderedDict as OD

from .xml import FNAMEXML, load_taskdict
from . import eps

def get_routes_crossingpoints(routes, locs):
    """Computes the crossings between standard routes. Needs a revision
    for routes that form a Y"""
    out = OD()
    for r1, r1v in routes.items():
        for r2, r2v in routes.items():
            # Don't repeat yourself
            if (r2,r1) in out or r1 == r2:
                continue
            # Defaults to None
            out[(r1,r2)] = None
            # Fetch coordinates of the locations for each route
            r1locs = [locs[loc] for loc in r1v]
            r2locs = [locs[loc] for loc in r2v]
            # Iterate segments of the first route
            for i1 in range(1,len(r1locs)):
                a1, a2 = r1locs[i1-1:i1+1]
                # Iterate segments of the second route
                for i2 in range(1,len(r2locs)):
                    b1, b2 = r2locs[i2-1:i2+1]
                    # Filter special cases of routes that share waypoints
                    if (a1 == b1 and a2 == b2) or (a1 == b2 and a2 == b1):
                        # Routes share the same segment in both senses, skip
                        # This is quite incomplete, breaks with multiple shared segments
                        # For now, avoid Y shapes with more than one shared segment
                        continue
                    elif a1 == b1 or a1 == b2:
                        #If only one point is shared, take it as crossing point
                        out[(r1,r2)] = a1
                        break
                    elif a2 == b1 or a2 == b2:
                        out[(r1,r2)] = a2
                        break
                    else:
                        #ret = np_seg_intersect(a1,a2,b1,b2)
                        ret = find_intersection(a1,a2,b1,b2)
                        if ret is not None:
                            out[(r1,r2)] = ret
                            break
                # Only one intersection between standar flows allowed
                if out[(r1,r2)] is not None:
                    break
    # Remove empty intersects
    for k in list(out.keys()):
       if out[k] is None:
           out.pop(k)
    return out



def rotate_task(taskdict, center, alpha=0.5):
    """
    # Iterate elements in the tree
    # For each map
    #  Leave region constant
    #  Rotate section
    #  Rotate locations
    # For each sky
    #  Rotate aircraft locations
    #  Rotate flow locations
    #  Rotate area locations
    #
    # Formula for clockwise 2D rotation matrix
    # R = (np.cos(alpha)   -np.sin(alpha))
    #     (np.sin(alpha)    np.cos(alpha))
    # P_rotated = R * P # matrix product
    """
    # Create matrix for homogeneous transformation
    Rotation = np.array([[np.cos(alpha), -np.sin(alpha),  0],
                         [np.sin(alpha),  np.cos(alpha),  0],
                         [      0,             0,         1]])

    Translation = np.array([[1,  0, -center[0]],
                            [0,  1, -center[1]],
                            [0,  0,      1   ]])

    iTranslation = np.array([[1,  0,  center[0]],
                             [0,  1,  center[1]],
                             [0,  0,     1    ]])

    T = np.dot(iTranslation, np.dot(Rotation, Translation))

    # copy taskdict to avoid in-place modification of original taskdict
    newdict = taskdict.copy()
    # Rotate all spatial elements in all maps except the region
    for tmap in newdict['maps'].values():
        for sector in tmap['sectors'].values():
            # Get x,y coordinates, multiply by R, store back in taskdict
            if 'vertex' in sector:
                newvertices = list()
                for vertex in sector['vertex']:
                    v = np.array([[vertex[1],vertex[0],1]]).T
                    vrotated = np.dot(T, v)
                    newvertices.append((vrotated[1][0], vrotated[0][0]))
                sector['vertex'] = newvertices
            elif 'arc' in sector:
                sector['arc'] = (sector['arc'][0]+alpha, sector['arc'][1], sector['arc'][2])

        for loc in tmap['locations'].values():
            v = np.array([[float(loc['x']),float(loc['y']),1]]).T
            vrotated = np.dot(T, v)
            loc['x'] = str(vrotated[0][0])
            loc['y'] = str(vrotated[1][0])
    # Rotate all aircraft locations in all skies, areas are not supported yet
    # Flows depend on routes, no need to rotate them
    for sky in taskdict['skies'].values():
        if 'aircrafts' in sky:
            for aircraft in sky['aircrafts'].values():
                newpoints = list()
                for loc in aircraft['flightpath']:
                    v = np.array([[loc[1],loc[0],1]]).T
                    vrotated = np.dot(T, v)
                    newpoints.append((v[1][0], v[0][0]))
                aircraft['flightpath'] = newpoints
        if 'areas' in sky:
            for area in sky['areas']:
                pass # Areas are not implemented yet

    return newdict


def get_sector_center(sector):
    x = np.nanmean([ p[1] for p in sector['vertex'] ])
    y = np.nanmean([ p[0] for p in sector['vertex'] ])
    return (x, y)


def get_distance_to_sector(sector, x, y):
    p3 = np.vstack([x,y]).T
    vertexno = len(sector)
    for i in range(vertexno):
        p1 = np.asarray(sector[i])
        if i == (vertexno - 1):
            p2 = np.asarray(sector[0])
        else:
            p2 = np.asarray(sector[i+1])

        d=np.abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
        if i==0:
            mindist = d
        else:
            bdist = mindist > d
            mindist[bdist] = d[bdist]
    return mindist


def get_distance_to_crossing_points(crossingpoints, Xc, Yc):
    mindist=np.NaN
    for i, (Xcr, Ycr) in enumerate(crossingpoints.values()):
        d =  np.sqrt((Xc - Xcr)**2 + (Yc - Ycr)**2)
        if i == 0:
            mindist = d
        else:
            bdist = mindist < d
            mindist[bdist] = d[bdist]
    return mindist


def np_seg_intersect(a0, a1, b0, b1, considerCollinearOverlapAsIntersect = False):
    # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect/565282#565282
    # http://www.codeproject.com/Tips/862988/Find-the-intersection-point-of-two-line-segments
    r = np.array(a1) - np.array(a0)
    s = np.array(b1) - np.array(b0)
    v = np.array(b0) - np.array(a0)

    num = np_cross_product(v, r)
    denom = np_cross_product(r, s)
    # If r x s = 0 and (q - p) x r = 0, then the two lines are collinear.
    if np.isclose(denom, 0) and np.isclose(num, 0):
        # 1. If either  0 <= (q - p) * r <= r * r or 0 <= (p - q) * s <= * s
        # then the two lines are overlapping,
        if(considerCollinearOverlapAsIntersect):
            vDotR = np.dot(v, r)
            aDotS = np.dot(-v, s)
            if (0 <= vDotR  and vDotR <= np.dot(r,r)) or (0 <= aDotS  and aDotS <= np.dot(s,s)):
                return True
        # 2. If neither 0 <= (q - p) * r = r * r nor 0 <= (p - q) * s <= s * s
        # then the two lines are collinear but disjoint.
        # No need to implement this expression, as it follows from the expression above.
        return None
    if np.isclose(denom, 0) and not np.isclose(num, 0):
        # Parallel and non intersecting
        return None
    u = num / denom
    t = np_cross_product(v, s) / denom
    if u >= 0 and u <= 1 and t >= 0 and t <= 1:
        res = b0 + (s*u)
        return res
    # Otherwise, the two line segments are not parallel but do not intersect.
    return None


def find_intersection(p0, p1, p2, p3):
    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]

    denom = float(s10_x * s32_y - s32_x * s10_y)

    if denom == 0:
        return None # collinear

    denom_is_positive = denom > 0

    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]

    s_numer = s10_x * s02_y - s10_y * s02_x
    if (s_numer < 0) == denom_is_positive:
        return None # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x
    if (t_numer < 0) == denom_is_positive:
        return None # no collision
    elif (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive :
        return None # no collision
    else:
        # collision detected
        t = t_numer / denom
        return ( p0[0] + (t * s10_x), p0[1] + (t * s10_y) )

def np_perp( a ) :
    b = np.empty_like(a)
    b[0] = a[1]
    b[1] = -a[0]
    return b


def np_cross_product(a, b):
    return np.dot(a, np_perp(b))


def get_angle_between_vectors(v1, v2):
    v1u = v1 / np.linalg.norm(v1)
    v2u = v2 / np.linalg.norm(v2)
    dot_product = np.dot(v1u, v2u)
    return np.arccos(dot_product)
