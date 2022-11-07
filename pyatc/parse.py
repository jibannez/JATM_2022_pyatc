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


############################################################################
#  SAMPLE LOG LINES
#  These are all the different types of log lines that I have found in Cañas logs.
#  If we find or need any new type of log line, the script must be modified.
############################################################################

"""
 -EXPERIMENT INFO [NO ELAPSED TIME, FIRST THREE LINES]
 <time>mié 7. oct 10:15:33 2015</time><info><log>start</log></info>
 <time>mié 7. oct 10:15:33 2015</time><info><experiment>selina_001</experiment></info>
 <time>mié 7. oct 10:15:33 2015</time><info><phase>test-initial</phase><type>trial</type><task_id>E000-T09</task_id></info>

 <time>mié 7. oct 12:16:04 2015</time><info><log>end</log></info>


 -CALL [RELATED TO SINGLE AIRCRAFTS]
   - update on aircraft info
     <time>mié 7. oct 10:15:38 2015</time><info><elapsed_time>4999</elapsed_time><call>QFA206</call><type>B744</type><control>1</control><xpos>213.495</xpos><ypos>34.5631</ypos><alt>22851.3</alt><vel>292.596</vel><head>2.98613</head><climb>-1777.21</climb><power>-0.736663</power></info>

   - SOLUTION
     - level_variation
     <time>mié 7. oct 10:16:36 2015</time><info><elapsed_time>62960</elapsed_time><call>VHSSI</call><solution>level_variation</solution><new_cfl>31000</new_cfl><old_cfl>35000</old_cfl></info>

     - speed_variation
     <time>mié 7. oct 12:15:39 2015</time><info><elapsed_time>7206189</elapsed_time><call>JP0115</call><solution>speed_variation</solution><new_velocity>260</new_velocity><new_throttle>-0.62128</new_throttle><old_velocity>233.892</old_velocity><old_throttle>-0.746003</old_throttle><altitude>15562.9</altitude></info>

     - vector
     <time>ma. 7. abr. 16:26:59 2020</time><info><elapsed_time>941922</elapsed_time><call>VOZ117</call><solution>vector</solution><new_heading>1.96773</new_heading><old_heading>0.197396</old_heading></info>

     - new_control
     <time>mié 7. oct 10:18:18 2015</time><info><elapsed_time>165060</elapsed_time><call>QFA336</call><new_control>accepted</new_control><old_control>2</old_control></info>


 - ACTION
   - rotate_callout
    <time>mié 7. oct 10:16:52 2015</time><info><elapsed_time>78762</elapsed_time><action>rotate_callout</action><callsign>VOZ892</callsign></info>

   - terminate
   <time>vi. 5. mar. 11:47:12 2021</time><info><elapsed>960748</elapsed><action>terminated</action></info>

 - VIEW (EXPERIMENT)

     - SOLUTION REQUEST
     <time>mié 7. oct 10:16:33 2015</time><info><elapsed_time>60273</elapsed_time><view>experiment</view><solution-request>cleared_flight_level</solution-request><callsign>VHSSI</callsign></info>

     - SOLUTION
     <time>mié 7. oct 10:16:36 2015</time><info><elapsed_time>62961</elapsed_time><view>experiment</view><solution>cleared_flight_level</solution><callsign>VHSSI</callsign><value>31000</value><result>1</result></info>

     <time>mié 7. oct 12:15:39 2015</time><info><elapsed_time>7206192</elapsed_time><view>experiment</view><solution>cleared_airspeed</solution><callsign>JP0115</callsign><value>260</value><result>1</result></info>

     - SOLUTION REQUIREMENT -> SKIP!!!  DON'T HAVE ANY IDEA WHAT THESE REFER TO
     <time>lu. 8. mar. 12:22:14 2021</time><info><elapsed_time>669769</elapsed_time><view>experiment</view><solution>requirement</solution><callsign>HDF364</callsign><level>3850</level><distance>10</distance><result>1</result></info>

     <time>lu. 8. mar. 12:22:30 2021</time><info><elapsed_time>685176</elapsed_time><call>HDF364</call><solution>requirement</solution><new_level>38500</new_level><old_level>3850</old_level><old_throttle>0.796482</old_throttle></info>

     
     - VECTOR TOOL
       - start
         <time>ma. 7. abr. 16:26:57 2020</time><info><elapsed_time>939313</elapsed_time><view>experiment</view><vector_tool>start</vector_tool></info>

       - move_to
         <time>ma. 7. abr. 16:26:59 2020</time><info><elapsed_time>941407</elapsed_time><view>experiment</view><vector_tool>move_to</vector_tool><x>906</x><y>248</y></info>

       - end_move
         <time>ma. 7. abr. 16:26:59 2020</time><info><elapsed_time>941922</elapsed_time><view>experiment</view><vector_tool>end_move</vector_tool></info>

     -EVENT
      - mouse_move
        <time>mié 7. oct 10:15:58 2015</time><info><elapsed_time>24599</elapsed_time><view>experiment</view><event>mouse_move</event><x>65.9</x><y>42.9</y></info>

      - mouse_up
        <time>mié 7. oct 10:15:58 2015</time><info><elapsed_time>25169</elapsed_time><view>experiment</view><event>mouse_up</event><x>65.6</x><y>42.6</y></info>

      - mouse_down
        <time>mié 7. oct 10:16:00 2015</time><info><elapsed_time>26795</elapsed_time><view>experiment</view><event>mouse_down</event><x>65.6</x><y>42.4</y></info>

      - mouse_double_click
        <time>mié 7. oct 10:17:17 2015</time><info><elapsed_time>103875</elapsed_time><view>experiment</view><event>mouse_double_click</event><x>205.7</x><y>36</y></info>
      - mouse press/release/move
        <time>mié 7. oct 10:39:06 2015</time><info><elapsed>1413422</elapsed><mouse>moved</mouse><x>949</x><y>764</y><button>0</button><state>1</state></info>
        <time>mié 7. oct 10:39:06 2015</time><info><elapsed>1413431</elapsed><mouse>released</mouse><x>949</x><y>764</y><button>1</button><state>1</state></info>
        <time>mié 7. oct 10:43:53 2015</time><info><elapsed>1700372</elapsed><mouse>pressed</mouse><x>1</x><y>472</y><button>1</button><state>0</state></info>

      - key_press
        <time>mié 7. oct 10:15:58 2015</time><info><elapsed_time>24677</elapsed_time><view>experiment</view><event>key_press</event><key>R</key></info>
        <time>mié 7. oct 10:18:08 2015</time><info><elapsed_time>155027</elapsed_time><view>experiment</view><event>key_press</event><key>Esc</key></info>


    -SCALE MOVEMENTS
        -move_to
        <time>jue 24. sep 12:32:13 2015</time><info><elapsed_time>6286130</elapsed_time><view>experiment</view><scale>move_to</scale><x>1110</x><y>265</y></info>

        -start_move
        <time>jue 24. sep 12:32:13 2015</time><info><elapsed_time>6286131</elapsed_time><view>experiment</view><scale>end_move</scale></info>

        -end_move
        <time>jue 24. sep 12:33:33 2015</time><info><elapsed_time>6365994</elapsed_time><view>experiment</view><scale>start_move</scale></info>



 -CLOCK
   - start_request
   <time>mié 7. oct 10:15:33 2015</time><info><elapsed_time>47</elapsed_time><clock>start_request</clock><interval>5000</interval></info>

   - tick
   <time>mié 7. oct 10:15:58 2015</time><info><elapsed_time>25067</elapsed_time><clock>tick</clock></info>


 -TOOL
   - route
     <time>mié 7. oct 10:16:00 2015</time><info><elapsed_time>26793</elapsed_time><tool>route</tool><active>0</active><callsign>VHSSI</callsign></info>
     <time>mié 7. oct 12:14:50 2015</time><info><elapsed_time>7157015</elapsed_time><tool>route</tool><active>1</active><callsign>LOZ889</callsign></info>

   - short_route
     <time>vi. 5. mar. 11:35:47 2021</time><info><elapsed_time>276370</elapsed_time><tool>short_route_probe</tool><value>1</value><callsign>LBN914</callsign></info>

   - history
     <time>mar 6. oct 14:34:34 2015</time><info><elapsed_time>6150441</elapsed_time><tool>history</tool><active>1</active><callsign>AZ0888</callsign></info>
     <time>mar 6. oct 14:34:47 2015</time><info><elapsed_time>6163493</elapsed_time><tool>history</tool><active>0</active><callsign>AZ0888</callsign></info>
   
"""

import re
import sys
import os
import scipy.io
import numpy as np


# Global flag to control the printing of several debugging information
DEBUG = False

# Atomic regular expressions that will be combined into more complex
# expressions to capture the relevant values of each log line

xpid = r"<experiment>(.+?)<\/experiment>"
taskid = r"<task_id>(.+?)<\/task_id>"
phase = r"<phase>(.+?)<\/phase>"
log_state = r"<log>(.+?)<\/log>"
time = r"<elapsed_time>(.+?)<\/elapsed_time>"
time2 = r"<elapsed>(.+?)<\/elapsed>"
filler = r".+?"
xy = r"<x>(.+?)<\/x><y>(.+?)<\/y>"
button = r"<elapsed>(.+?)<\/elapsed><mouse>(.+?)</mouse><x>(.+?)<\/x><y>(.+?)<\/y><button>(.+?)</button><state>(.+?)</state>"
key = r"<key>(.+?)<\/key>"
request = r"<solution-request>(.+?)<\/solution-request>"
callsign = r"<callsign>(.+?)<\/callsign>"
solution = r"<solution>(.+?)<\/solution>"
value = r"<value>(.+?)<\/value>"
result = r"<result>(.+?)<\/result>"
interval = r"<interval>(.+?)<\/interval>"
call = r"<call>(.+?)<\/call>"
typestr = r"<type>(.+?)<\/type>"
control = r"<control>(.+?)</control>"
xyz = r"<xpos>(.+?)</xpos><ypos>(.+?)</ypos><alt>(.+?)</alt>"
dyn = r"<vel>(.+?)</vel><head>(.+?)</head><climb>(.+?)</climb><power>(.+?)</power>"
level_variation = r"<new_cfl>(.+?)</new_cfl><old_cfl>(.+?)</old_cfl>"
speed_variation = r"<new_velocity>(.+?)</new_velocity><new_throttle>(.+?)</new_throttle><old_velocity>(.+?)</old_velocity><old_throttle>(.+?)</old_throttle><altitude>(.+?)</altitude>"
control_variation = r"<new_control>(.+?)</new_control><old_control>(.+?)</old_control>"
heading_variation = r"<new_heading>(.+?)</new_heading><old_heading>(.+?)</old_heading>"
active = r"<active>(.+?)</active>"


# Dictionary with the set of complex regular expressions that match
# the relevant information of the different types of log lines.
regexstrings = dict(
    xpid = xpid,
    taskid = taskid,
    phase = phase,
    log_state = log_state,
    mouse_button_event = button,
    view_mouse_event = time + filler + xy,
    view_key_press = time + filler + key,
    view_solution_request = time + filler + request + callsign,
    view_solution = time + filler + solution + callsign + value + result,
    view_scale_move_start = time,
    view_scale_move_end = time,
    view_scale_move_to = time + filler + xy,
    view_vector_tool_start = time,
    view_vector_tool_end = time,
    view_vector_tool_move_to = time + filler + xy,
    clock_start = time + filler + interval,
    clock_tick = time,
    call_update = time + call + typestr + control + xyz + dyn,
    call_level = time + call + solution + level_variation,
    call_speed = time + call + solution + speed_variation,
    call_heading = time + call + solution + heading_variation,
    call_newcontrol = time + call + control_variation,
    tool_route_event = time + filler + active + callsign,
    tool_route_probe = time + filler + value + callsign,
    tool_history_event = time + filler + active + callsign,
    action_rotate_callout = time + filler + callsign,
    action_terminated = time2,
)

# Dictionary with the set of data types expected from each of
# the matches with the log lines. None stands for string.
regexdtypes = dict(
    xpid = None,
    taskid = None,
    phase = None,
    log_state = None,
    mouse_button_event = ('int', None, 'int', 'int', 'int', 'int'),
    view_mouse_event = ('int', 'float', 'float'),
    view_key_press = ('int', None),
    view_solution_request = ('float', None, None),
    view_solution = ('int', None, None, 'int', 'int'),
    view_scale_move_start = 'int',
    view_scale_move_end = 'int',
    view_scale_move_to = ('int','int','int'),
    view_vector_tool_start = 'int',
    view_vector_tool_end = 'int',
    view_vector_tool_move_to = ('int', 'float', 'float'),
    clock_start = ('int', 'int'),
    clock_tick = 'int',
    call_update = ('int', None, None, 'int', 'float', 'float', 'float', 'float', 'float', 'float', 'float'),
    call_level = ('int', None, None, 'int', 'int'),
    call_speed = ('int', None, None, 'float', 'float', 'float', 'float', 'float'),
    call_heading = ('int', None, None, 'float', 'float'),
    call_newcontrol = ('int', None, None, 'int'),
    tool_route_event = ('int', 'int', None),
    tool_route_probe = ('int', 'int', None),
    tool_history_event = ('int', 'int', None),
    action_rotate_callout = ('int', None),
    action_terminated = 'int',
)


def search(key, line):
    """
    Finds matches of regular expression 'key' into string 'line',
    and formats the results accordingly
    """
    if DEBUG:
        print(regexstrings[key])

    matches = re.search(regexstrings[key], line)

    # Return if no match was found. This probably indicates an error and
    # should raise an exception. For now, just continue.
    if matches is None:
        print('\t[WARNINIG] Incorrect match for handled log line:')
        print(line)
        return

    matches = matches.groups()

    if DEBUG:
        print(matches)

    if len(matches) > 1:
        retlst = list()
        for (dtype, match) in zip(regexdtypes[key], matches):
            if dtype is None or dtype in ['string', 'str']:
                retlst.append(match)

            elif dtype == 'int':
                retlst.append(int(match))

            elif dtype == 'float':
                retlst.append(float(match))

            else:
                print('\t[Error] This data type is not valid: ' + dtype)

        return retlst

    elif len(matches) == 1:
        dtype = regexdtypes[key]
        if dtype is None or dtype in ['string', 'str']:
            return matches[0]

        elif dtype == 'int':
            return int(matches[0])

        elif dtype == 'float':
            return float(matches[0])

        else:
            print('\t[Error] This data type is not valid: ' + dtype)

    else:
        print('Error, no matches for this line: \n ' + line)
        return None


def parse_global_info(line):
    """
    Parse log lines without timestamps, these typically contain
    global information about the trial.
    """
    if 'experiment' in line:
        return ('info', search('xpid', line))

    elif 'task' in line:
        return ('info', (search('taskid', line), search('phase', line)))

    elif 'log' in line:
        return ('info', search('log_state', line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def parse_tool(line):
    """
    Parse 'tool' type of log line. I have only found one subtype of 'tool',
    that is 'route'. I'm not sure if this a user generated event, or an
    automatic change of state in the program.
    """
    if '<tool>route</tool>' in line:
        return ('tool_route_event', search('tool_route_event', line))

    elif 'short_route_probe' in line:
        return ('tool_route_probe', search('tool_route_probe', line))
        
    elif 'history' in line:
        return ('tool_history_event', search('tool_history_event', line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def parse_action(line):
    """
    Parse 'action' type of log line. I have only found one subtype of 'action',
    that is 'rotate_callout'. I'm not sure if this a user generated action, or an
    automatic change of state in the program.
    """
    if 'rotate_callout' in line:
        return ('action_rotate_callout', search('action_rotate_callout', line))

    elif 'terminated' in line:
        return ('action_terminated', search('action_terminated', line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def parse_clock(line):
    """
    Parse 'clock' type of log lines.
    """
    if 'start_request' in line:
        return ('info', search('clock_start',line))

    elif 'tick' in line:
        return ('clock_tick', search('clock_tick',line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def parse_experiment_view(line):
    """
    Parse 'view' type of log line. They seem to be related with
    user-generated events. I'm not totally sure about the difference between
    'solution-request' and 'solution' types of log lines.
    """
    if 'mouse_up' in line:
        return ('view_mouse_up', search('view_mouse_event',line))

    elif 'mouse_down' in line:
        return ('view_mouse_down', search('view_mouse_event',line))

    elif 'mouse_double_click' in line:
        return ('view_mouse_double_click', search('view_mouse_event',line))

    elif 'mouse_move' in line:
        return ('view_mouse_move', search('view_mouse_event',line))

    elif '<key>' in line:
        return ('view_key_press', search('view_key_press',line))

    elif '<solution-request>' in line:
        return ('view_solution_request', search('view_solution_request',line))

    elif '<solution>' in line:
        return ('view_solution', search('view_solution',line))

    elif '<scale>move_to' in line:
        return ('view_scale_move_to',search('view_scale_move_to',line))

    elif '<scale>start_move' in line:
        return ('view_scale_move_start',search('view_scale_move_start',line))

    elif '<scale>end_move' in line:
        return ('view_scale_move_end',search('view_scale_move_end',line))

    elif '<vector_tool>move_to' in line:
        return ('view_vector_tool_move_to',search('view_vector_tool_move_to',line))

    elif '<vector_tool>start' in line:
        return ('view_vector_tool_start',search('view_vector_tool_start',line))

    elif '<vector_tool>end_move' in line:
        return ('view_vector_tool_end',search('view_vector_tool_end',line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def parse_call(line):
    """
    Parse 'call' type of log line. They seem to display information
    derived of user generated events, and also related with automatic
    clock events every 5 seconds. I don't understand 'new_control' type.
    """
    if '<type>' in line:
        return ('call_update', search('call_update',line))

    elif 'level_variation' in line:
        return ('call_level', search('call_level',line))

    elif 'speed_variation' in line:
        return ('call_speed', search('call_speed',line))

    elif '<solution>vector' in line:
        return ('call_heading', search('call_heading',line))

    elif '<new_control>' in line:
        return ('call_newcontrol', search('call_newcontrol',line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def parse_mouse_button(line):
    """
    Parse 'mouse' type of log line. I have no idea of what it means,
    or the different between the mouse events logged as <experiment><view>
    type of log.
    """
    if '<button>' in line:
        return ('mouse_button', search('mouse_button_event', line))

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)


def write_output(outdict, filename="test.xml.log"):
    """
    Exports a python dictionary of lists as a matlab
    struct of cell arrays. To load it back in matlab do:
        data = load(filename)
            data
                field1 = {}
                ...
                fieldn = {}

    """

    # First, convert lists of lists into numpy object arrays
    # These numpy object arrays are loaded as cell arrays in matlab,
    # which matches perfectly our usecase.
    cleaned_dict = dict()
    for key, value in outdict.items():
        cleaned_dict[key] = np.array(value, np.object)

    # Save to disk, takes loooooooooots of time.
    scipy.io.savemat(filename, cleaned_dict, do_compression=True)


def clear_nones(outdict):
    for key, values in outdict.items():
        newvalues = list()
        for value in values:
            if value is None:
                continue
            elif isinstance(value, list) and None in value:
                continue
            else:
                newvalues.append(value)
        outdict[key] = newvalues

    
def create_dicts():
    outdict = dict()
    outdict['info'] = list()
    outdict['call_update'] = list()
    outdict['call_level'] = list()
    outdict['call_speed'] = list()
    outdict['call_heading'] = list()
    outdict['call_newcontrol'] = list()
    outdict['mouse_button'] = list()
    outdict['view_mouse_up'] = list()
    outdict['view_mouse_down'] = list()
    outdict['view_mouse_double_click'] = list()
    outdict['view_mouse_move'] = list()
    outdict['view_key_press'] = list()
    outdict['view_solution_request'] = list()
    outdict['view_solution'] = list()
    outdict['view_scale_move_start'] = list()
    outdict['view_scale_move_end'] = list()
    outdict['view_scale_move_to'] = list()
    outdict['view_vector_tool_start'] = list()
    outdict['view_vector_tool_end'] = list()
    outdict['view_vector_tool_move_to'] = list()
    outdict['clock_tick'] = list()
    outdict['action_rotate_callout'] = list()
    outdict['action_terminated'] = list()
    outdict['tool_route_event'] = list()
    outdict['tool_route_probe'] = list()
    outdict['tool_history_event'] = list()
    return outdict    


def run(logname="test.xml.log", export2matlab=False):
    """
    Opens a log file and parses all the lines. The output
    is stored as a dictionary, in which each key is the name
    that best represents the type/s of log line/s that is/are
    stored, and the value is a list of lists. Each line ends up
    as a list of the different values. An example to show this
    structure more explicitly:

        outdict[key] = value

        key is a string, the valid values are determined below

        value is a list of records: [record1, ..., recordN]

        Each record type is a specific collection of values. Data
        type and amount of values per record depend on the type
        of log line, and they are defined in regexdtypes dict.
        record1 = [value1, ..., valueM]
    """

    # Create dictionary to store the different types of log lines
    outdict = create_dicts()

    # Open log file and iterate over its lines
    with open(logname, 'rb') as logfile:
        for line in logfile:
            # This codification may change depending on the locale of
            # the experimental computer. This sucks, windows-style. We may
            # need to preprocess the whole file to reencode it.
            # If locale is english, it may work with out reencoding, for
            # that it is simpler to load it as text file ('r' argument in open
            # function), or decode it as 'utf-8' in line.decode argument
            line = line.decode('latin-1')

            if DEBUG:
                print(line)

            # Skip requirement-type log lines, unknown function
            if 'requirement' in line:
                continue
                
            # This is the global triaging for the type of log line.
            # If specific sequences are find in a line, it is parsed
            # by a predetermined parser function that is prepared to
            # deal with the different values associated.
            # It could be done all in one big function, but the log file
            # has also a certain hierarchy that this methods respects.
            # I haven't found, though, much sense or use to this hierarchy.
            if '<elapsed_time>' not in line and '<elapsed>' not in line:
                # '<elapsed>' is only used for mouse_button type of line.
                # This seems to indicate that this type of log line is an
                # product of arcaic code in the source that may not apply
                # to our use case. Hoewever, it may be indicating a relevant
                # event, but using an arcaic code path that uses uncommon
                # labels and timestamps.
                # '<elapsed_time>' is used for all other events logged, but
                # it is not present in global information log lines, which are
                # parsed by this function, that has neither elapsed nor elapsed_time
                otup = parse_global_info(line)

            elif '<mouse>' in line:
                otup = parse_mouse_button(line)

            elif '<view>' in line:
                otup = parse_experiment_view(line)

            elif '<call>' in line:
                otup = parse_call(line)

            elif '<tool>' in line:
                otup = parse_tool(line)

            elif '<action>' in line:
                otup = parse_action(line)

            elif '<clock>' in line:
                otup = parse_clock(line)

            else:
                print('\t[WARNING] Unhandled log line:')
                print(line)

            # Append the record to its specific type of line
            if otup is not None:
                outdict[otup[0]].append(otup[1])

    # Clear bad matched due to misrecognized log lines.
    clear_nones(outdict)
    
    # Export the dictionary into matlab struct and store to disk
    # This step takes 99% of the time, so if you are using only
    # python, you should disable exporting, and simply pass the
    # dictionary between functions.
    if export2matlab:
        write_output(outdict, logname+'.mat')

    return outdict


def run_directory(path='./tests'):
    """
    Parse all files ending with .xml.log in the specified path.
    """
    import os
    import subprocess

    for file in os.listdir(path):
        if file.endswith(".xml.log"):
            fpath = os.path.join(path, file)
            print('\t Processing log file: ' + fpath)
            subprocess.call(['python3', './parselog.py', fpath])



def parse_line(line):
    line = line.decode('latin-1')
    
    if DEBUG:
        print(line)

    # Skip requirement-type log lines, unknown function
    if 'requirement' in line:
        return
        
    if '<elapsed_time>' not in line and '<elapsed>' not in line:
        otup = parse_global_info(line)

    elif '<mouse>' in line:
        otup = parse_mouse_button(line)

    elif '<view>' in line:
        otup = parse_experiment_view(line)

    elif '<call>' in line:
        otup = parse_call(line)

    elif '<tool>' in line:
        otup = parse_tool(line)

    elif '<action>' in line:
        otup = parse_action(line)

    elif '<clock>' in line:
        otup = parse_clock(line)

    else:
        print('\t[WARNING] Unhandled log line:')
        print(line)
        otup = None

    return otup
