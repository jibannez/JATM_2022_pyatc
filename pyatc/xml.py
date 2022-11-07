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


import pickle
import random
import numpy as np
from collections import OrderedDict as OD
from lxml import etree as ET
from . import DEBUG

XSIURI = 'http://www.w3.org/2001/XMLSchema-instance'
ATCURI = 'http://www.humanfactors.uq.edu.au/atc/2006/atc-ns'
ATCNS = '{'+ATCURI+'}'
XSINS = '{'+XSIURI+'}'
FNAME = 'ATC_task' # default name used in the library
FNAMEXML = FNAME+'.xml'
ET.register_namespace('xsi', XSIURI)
ET.register_namespace('atc', ATCURI)


def addns(din, NS=ATCNS):
    """ Prepends namespace string to both dict keys and bare strings
    """
    if isinstance(din, str):
        return NS+din
    else:
        dout = OD()
        for k, v in din.items():
            dout[NS+k] = v
        return dout


def strip_ns(taskdict):
    """ Removes namespace string to all dict keys
    """
    outdict = OD()
    for key, value in taskdict.items():
        if key is ET.Comment:
            continue
        key = key.split('}')[-1]
        #print(key)
        #try:
        #    key = key.split('}')[-1]
        #except: # this must be a comment
        #    pass
        if isinstance(value, OD):
            value = strip_ns(value)
        outdict[key] = value
    return outdict


def get_xmlfilename_from_log(logfile):
    """Guess xml task file name: the filename pattern is [TRIALNAME]_[TASKNAME].xml.log"""
    return '_'.join(logfile.split('_')[1:])[:-4]


def generate_xml(taskdict, fname=FNAMEXML):
    taskxml = ATCXMLConfig(taskdict)
    taskxml.save(fname)


def load_xml(fname=FNAMEXML):
    return etree_to_ordereddict(ET.parse(fname))


def load_taskdict(fname=FNAMEXML, ext='.pkl'):
    with open(fname+ext, 'rb') as handle:
        b = pickle.load(handle)
    return b

def get_routenames_xml(fname):
    if isinstance(fname, OD):
        taskxml = fname
    else:
        taskxml = load_xml(fname)
    routes = taskxml['experiment']['data']['map']['route']
    if not isinstance(routes, list):
        routes = [routes]
    return [ r['idx'] for r in routes]

def get_aircrafts_xml(fname, phasename='set001', trialname='trial1'):
    if isinstance(fname, OD):
        taskxml = fname
    else:
        taskxml = load_xml(fname)

    skyname = None
    for phase in taskxml['experiment']['presentation']['phase']:
        if phase['idx'] == phasename:
            for trial in phase['trial']:
                if trial['idx'] == trialname:
                    skyname = trial['sky']
                    break
            if skyname is not None:
                break
    #for sky in taskxml['experiment']['data']['sky']:
    #    if sky['idx'] == skyname:
    #        aircrafts = sky['aircraft']
    #        break
    
    # Assume only one sky is present
    sky = taskxml['experiment']['data']['sky']
    aircrafts = sky['aircraft']
    
    # Single aircraft files produce error here, forcing list
    if not isinstance(aircrafts, list):
        aircrafts = [aircrafts]
        
    airdict = OD()       
    for aircraft in aircrafts:
        aircft = OD()
        aircft['type'] = aircraft['type']
        aircft['idx'] = aircraft['idx']
        aircft['start'] = int(aircraft['start'])
        aircft['altitude'] = float(aircraft['altitude'])
        aircft['velocity'] = float(aircraft['velocity'])
        try:
            aircft['altitude_end'] = float(aircraft['flightpath']['point'][0]['altitude'])
        except:
            aircft['altitude_end'] = aircft['altitude']

        aircft['flightpath'] = [(float(p['x']), float(p['y'])) for p in aircraft['flightpath']['point']]
        airdict[aircft['idx']] = aircft
    return airdict


def get_sector_vertex_xml(xmlname):
    xmlconf = load_xml(xmlname)
    points_dicts = xmlconf['experiment']['data']['map']['sector']['vertex']
    vertex =  [ (p['x'], p['y']) for p in points_dicts ]
    vertex.append(vertex[0]) # close the sector area
    return vertex


def etree_to_ordereddict(t, remove_namespaces=True):
    if isinstance(t, ET._ElementTree):
        t = t.getroot()
    d = OD()
    d[t.tag] = OD() if t.attrib else None
    children = list(t)
    if children:
        dd = OD()
        for dc in map(etree_to_ordereddict, children):
            for k, v in dc.items():
                if k not in dd and k is not ET.Comment:
                    dd[k] = list()
                dd[k].append(v)
        d = OD()
        d[t.tag] = OD()
        for k, v in dd.items():
            if len(v) == 1:
                d[t.tag][k] = v[0]
            else:
                d[t.tag][k] = v
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    if remove_namespaces:
        return strip_ns(d)
    else:
        return d


class ATCXMLConfig(object):

    def __init__(self, task, fname=FNAMEXML, add_flows=True):
        self.task = task
        self.fname = fname
        self.add_flows = add_flows # This configuration should be False if taskdict comes from an ondisk backup, in which flow aircrafts have been already added
        self.build_tree(task)

    def build_tree(self, task):
        # Create root element
        self.root = ET.Element(addns('experiment'), attrib=self.task['experiment'])

        # Create sections of the XML file sequentially
        self.set_global_config()
        self.set_data()
        self.set_presentation()

        # Wrap xml root into Tree object for higher order functions
        self.tree = ET.ElementTree(self.root)

    ########################################
    ## Highest level fields
    ########################################
    def set_global_config(self):
        self.t_config = ET.SubElement(self.root, addns('config'))
        self.set_units()
        self.set_aircraft_models()
        self.set_instructions()
        self.set_ui() # TODO!

    def set_data(self):
        self.t_data = ET.SubElement(self.root, addns('data'))
        self.set_params()
        self.set_maps()
        self.set_skies()

    def set_presentation(self):
        t_presentation = ET.SubElement(self.root, addns('presentation'))
        for phasename, phase in self.task['phases'].items():
            attr = {'idx': phasename}
            t_phase = ET.SubElement(t_presentation, addns('phase'), attrib=addns(attr))
            self.set_phase(t_phase, phase)

    ########################################
    ## Medium level global subfields
    ########################################
    def set_units(self):
        parent = self.t_config
        el1 = ET.SubElement(parent, addns('units'))
        el2 = ET.SubElement(el1, addns('input'))
        el2.text = self.task['units']

    def set_instructions(self):
        parent = self.t_config
        for iname, instruction in self.task['instructions'].items():
            attr = {'idx': iname}
            el1 = ET.SubElement(parent, addns('instruction'), addns(attr))
            el2 = ET.SubElement(el1, addns('text'))
            el2.text = ET.CDATA(instruction['text'])
            if 'keyEvent' in instruction:
                el3 = ET.SubElement(el1, addns('keyEvent'))
                el3.text = instruction['keyEvent']

    def set_aircraft_models(self):
        parent = self.t_config
        for model in self.task['aircraft_models']:
            attr = {'idx': model}
            ET.SubElement(parent, addns('aircraftParam'), addns(attr))

    def set_ui(self):
        parent = self.t_config
        # Process UI elements: TODO

    ########################################
    ## Medium level DATA subfields
    ########################################
    def set_params(self):
        for pname, parameters in self.task['parameter_sets'].items():
            attr = {'idx': pname}
            t_param = ET.SubElement(self.t_data, addns('param'), attrib=addns(attr))
            self.set_task_parameters(t_param, parameters)

    def set_maps(self):
        for mapname, mapdict in self.task['maps'].items():
            attr = {'idx': mapname}
            t_map = ET.SubElement(self.t_data, addns('map'), attrib=addns(attr))
            self.set_region(t_map, mapdict['region'])
            self.set_locations(t_map, mapdict['locations'])
            self.set_routes(t_map, mapdict['routes'])
            self.set_sectors(t_map, mapdict['sectors'])

    def set_skies(self):
        for skyname, sky in self.task['skies'].items():
            attr = {'idx': skyname}
            t_sky = ET.SubElement(self.t_data, addns('sky'), attrib=addns(attr))
            self.set_aircrafts(t_sky, sky['aircrafts'])
            if self.add_flows:
                self.set_flows(t_sky, sky['flows'], self.task['maps'])
            self.set_areas(t_sky, sky['areas'])


    ########################################
    ## Medium level PRESENTATION subfields
    ########################################
    def set_phase(self, parent, conf):
        for blkname, blk in conf.items():
            if blk['type'] == 'trial':
                attr = OD([('sky',blk['sky']), ('param',blk['param']), ('map',blk['map']), ('idx',blkname)])
                el1 = ET.SubElement(parent, addns('trial'), attrib=addns(attr))
                if 'events' in blk:
                    for evname, evtext in blk['events'].items():
                        el2 = ET.SubElement(el1, addns(evname))
                        if ~isinstance(evtext, str):
                            el2.text = str(evtext)
                        else:
                            el2.text = evtext
            elif blk['type'] == 'instruction':
                #attr = {'idx': v['name']}
                #el1 = ET.SubElement(parent, addns('phase'), attrib=addns(attr))
                attr = {'idxref': blk['idxref']}
                ET.SubElement(parent, addns('instruction'), attrib=addns(attr))

    ########################################
    ## Lowest level DATA subfields
    ##
    #### PARAMETERS subfields
    ########################################
    def set_task_parameters(self, parent, conf):
        for param, value in conf.items():
            if isinstance(value, OD):
                attr = value['attrib']
                el = ET.SubElement(parent, addns(param), attrib=addns(attr))
                el.text = str(value['text'])
            else:
                el = ET.SubElement(parent, addns(param))
                el.text = str(value)

    ########################################
    ## Lowest level DATA subfields
    ##
    #### MAP subfields
    ########################################
    def set_region(self, parent, conf):
        attrs=OD([('y_dim',conf[0]), ('y',conf[1]), ('x_dim',conf[2]), ('x', conf[3])])
        ET.SubElement(parent, addns('region'), attrib=addns(attrs))

    def set_locations(self, parent, conf):
        for locname, point in conf.items():
            point['idx'] = locname
            ET.SubElement(parent, addns('location'), attrib=addns(point))

    def set_routes(self, parent, conf):
        for route, waypoints in conf.items():
            attr = {'idx': route}
            el = ET.SubElement(parent, addns('route'), attrib=addns(attr))
            for point in waypoints:
                attr = {'location': point}
                ET.SubElement(el, addns('pointref'), attrib=addns(attr))

    def set_sectors(self, parent, conf):
        for sname, sector in conf.items():
            if 'status' in sector:
                attr = OD([('status',sector['status']), ('idx',sname)])
            else:
                attr = {'idx': sname}
            el = ET.SubElement(parent, addns('sector'), attrib=addns(attr))
            if 'vertex' in sector:
                vertices = sector['vertex']
                for y, x in vertices:
                    attr = OD([('y', str(y)), ('x', str(x))])
                    ET.SubElement(el, addns('vertex'), attrib=addns(attr))
            elif 'arc' in sector:
                arc = sector['arc']
                attr = OD([('r', str(arc['r'])), ('y', str(arc['y'])), ('x', str(arc['x']))])
                ET.SubElement(el, addns('arc'), attrib=addns(attr))

    ########################################
    ## Lowest level DATA subfields
    ##
    #### SKY subfields
    ########################################
    def set_aircrafts(self, parent, conf):
        for aname, aircraft in conf.items():
            attr = OD([('type', aircraft['type']), ('idx', aname)])
            el_air = ET.SubElement(parent, addns('aircraft'), attrib=addns(attr))
            eltmp = ET.SubElement(el_air, addns('start'))
            eltmp.text = str(aircraft['start'])
            eltmp = ET.SubElement(el_air, addns('altitude'))
            eltmp.text = str(aircraft['altitude'])
            eltmp = ET.SubElement(el_air, addns('velocity'))
            eltmp.text = str(aircraft['velocity'])
            el_path = ET.SubElement(el_air, addns('flightpath'))
            for i, (y, x) in enumerate(aircraft['flightpath']):
                attr = OD([('y', str(y)), ('x', str(x))])
                e_point = ET.SubElement(el_path, addns('point'), attrib=addns(attr))
                if i == 0:
                    # Add final altitude after first point. Needs testing.
                    # The samples show this use, but reading xsd file it seems
                    # that there are several other options to set in flightpath
                    eltmp = ET.SubElement(e_point, addns('altitude'))
                    eltmp.text = str(aircraft['altitude_end'])

    def set_flows(self, parent, flows, maps):
        std_flows = OD()
        for routename, flow in flows.items():
            # Each flow-route refers to a certain map where it is defined
            mapref = flow['map']
            routes = maps[mapref]['routes']
            locations = maps[mapref]['locations']
            route = routes[routename]
            waypoints = [(float(locations[p]['y']), float(locations[p]['x'])) for p in route]
            #basedict = {'altitude':flow['altitude'], 'velocity':flow['velocity'], 'altitude_end':flow['altitude_end']}
            basedict = {'velocity':flow['velocity']}
            cumdist = _compute_route_cumdist(waypoints)
            heading = _compute_route_heading(waypoints)
            route_time = cumdist[-1] / flow['velocity'] * 3600 # miles / (miles/hour) -> hour
            a2a_dist = flow['velocity'] / flow['occupation'] # (miles/hour) / (aircrafts/hour) -> miles/aircraft
            a2a_time = a2a_dist / flow['velocity'] * 3600 # (miles/aircraft) / (miles/hour) -> hours/aircraft * 3600 -> seconds/aircraft
            time_offset = flow['offset'] / flow['velocity'] * 3600 # compute the amount of time required for a certain spatial offset
            # Add initial set of aircrafts -> compute initial positions
            dist = 0
            for dist in np.arange(cumdist[-1]-a2a_dist, 0, -a2a_dist):
                aircraft = basedict.copy()
                aircraft['start'] = 0
                jitter = random.uniform(-flow['jitter'], flow['jitter']) / 100
                spatial_jitter = a2a_dist * jitter
                aircraft['flightpath'] = _compute_waypoints(dist, waypoints, cumdist, heading, flow['offset'], spatial_jitter)
                aircraft['type'] = random.choice(flow['types'])
                # Either random sample a pair (altitude, altitude_end) or pick the only value
                if isinstance(flow['altitude'], tuple):
                    # if it is tuple -two numbers enclosed by ()- assign them to the aircraft
                    aircraft['altitude'] = flow['altitude'][0]
                    aircraft['altitude_end'] = flow['altitude'][1]
                elif isinstance(flow['altitude'], list):
                    altitude = random.choice(flow['altitude'])
                    aircraft['altitude'] = altitude[0]
                    aircraft['altitude_end'] = altitude[1]
                else:
                    raise ValueError('Either tuple pairs or list of tuple pairs expected')

                # If the route is in evolution, aircrafts that start in the middle of the
                # route need to have a specific altitude for their start. This assumes linearity
                # in the altitude increase, so may be required a better testing. Also non-integer values
                # maybe conflictive
                if aircraft['altitude'] != aircraft['altitude_end']:
                    hdiff = aircraft['altitude_end'] - aircraft['altitude']
                    dist_fraction = float(dist)/float(cumdist[-1])
                    aircraft['altitude'] = aircraft['altitude'] + round(hdiff*dist_fraction)
                name = random.choice(flow['basenames']) + str(random.randint(100,999))
                std_flows[name] = aircraft
                if DEBUG:
                    print_aircraft(aircraft, name+'_space')
            rem_time = dist / flow['velocity'] * 3600
            # Add time-delayed set of aircrafts -> compute start time
            for init_time in np.arange(a2a_time, flow['time'], a2a_time):
                jitter = random.uniform(-flow['jitter'], flow['jitter']) / 100
                time_jitter = a2a_time * jitter
                time = init_time - rem_time + time_offset + time_jitter
                aircraft = basedict.copy()
                aircraft['flightpath'] = waypoints
                # Either random sample a pair (altitude, altitude_end) or pick the only value
                if isinstance(flow['altitude'], tuple):
                    # if it is tuple -two numbers enclosed by ()- assign them to the aircraft
                    aircraft['altitude'] = flow['altitude'][0]
                    aircraft['altitude_end'] = flow['altitude'][1]
                elif isinstance(flow['altitude'], list):
                    altitude = random.choice(flow['altitude'])
                    aircraft['altitude'] = altitude[0]
                    aircraft['altitude_end'] = altitude[1]
                else:
                    raise ValueError('Either tuple pairs or list of tuple pairs expected')

                aircraft['start'] = int(time) * 1000
                aircraft['type'] = random.choice(flow['types'])
                name = random.choice(flow['basenames']) + str(random.randint(100,999))
                std_flows[name] = aircraft
                if DEBUG:
                    print_aircraft(aircraft, name+'_time')

        # Commit computed aircrafts to the xml
        self.set_aircrafts(parent, std_flows)

    def set_areas(self, parent, conf):
        pass
        #TODO!


    def save(self, fname=None):
        # Generate appropriate filename
        if fname is None:
            fname = self.fname
        # Format root tree for output
        _indent(self.root)
        # Save xml file
        self.tree.write(fname)#, encoding='latin-1')
        # Save taskdict configuration used to generate this xml
        with open(fname+'.pkl', 'wb') as handle:
            pickle.dump(self.task, handle, protocol=pickle.HIGHEST_PROTOCOL)


#######################################################
## Static functions of the module used by the class
#######################################################
def print_aircraft(a, name):
    print_lst = list()
    print_str = name
    for (y, x) in a['flightpath']:
        print_lst.append(y)
        print_lst.append(x)
        print_str = print_str + ' (%f, %f)'
    print(print_str % tuple(print_lst))


def _compute_waypoints(dist, waypoints, cumdist, heading, offset, jitter):
    # Compute difference vectors
    points = [_dist2coord_map(dist, waypoints, cumdist, heading)]
    bidx = np.where(dist < cumdist)[0]

    # Keep the index of the next waypoint with respect to the current point
    if len(bidx) == 0:
        idx = 1
    else:
        idx = bidx[0] + 1

    if len(waypoints) <= idx:
        points.append(waypoints[-1])
    else:
        points.extend(waypoints[idx:])

    # Should modify heading list to make sense of the next computations
    heading = heading[-len(points):]
    # Add jitter to the first point
    points[0] = (points[0][0] + np.sin(heading[0]) * jitter, points[0][1] + np.cos(heading[0]) * jitter)

    # Add offset to all points
    offpoints = list()
    for i, (y, x) in enumerate(points):
        if i == 0: # use first heading to backproject route for the first point
            y = y + np.sin(heading[i]) * offset
            x = x + np.cos(heading[i]) * offset
        else:
            y = y + np.sin(heading[i-1]) * offset
            x = x + np.cos(heading[i-1]) * offset
        offpoints.append((y,x))

    return offpoints


def _dist2coord_map(dist, waypoints, cumdist, heading):
    # find the route segment at this distance
    bidx = np.where(dist < cumdist)[0]
    # Keep the index of the last waypoint with less distance than the current point
    if len(bidx) == 0:
        idx = 0
    else:
        idx = bidx[-1]

    # compute the length of vector within this segment of the route
    if idx == 0:
        dmodule = dist
    else:
        dmodule = dist - cumdist[idx-1]
    # compute the (y,x) global coordinates of this point of the route
    (y0, x0) = waypoints[idx] # base point
    y = y0 + dmodule*np.sin(heading[idx])   # y component
    x = x0 + dmodule*np.cos(heading[idx])   # y component
    return (y, x)


def _compute_route_cumdist(waypoints):
    # Compute difference vectors
    dists = list()
    for i in range(1,len(waypoints)):
        y = waypoints[i][0] - waypoints[i-1][0]
        x = waypoints[i][1] - waypoints[i-1][1]
        dists.append(np.sqrt(x**2 + y**2))
    route_cumdist = np.cumsum(dists)

    # return the computed distance, and the pointer to the mapping function
    return route_cumdist


def _compute_route_heading(waypoints):
    # Compute difference vectors
    heading = list()
    for i in range(1,len(waypoints)):
        y = waypoints[i][0] - waypoints[i-1][0]
        x = waypoints[i][1] - waypoints[i-1][1]
        heading.append(np.arctan2(y, x))
    return heading


# in-place prettyprint formatter
def _indent(elem, level=0, spacer="    "):
    i = "\n" + level*spacer
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + spacer
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i



