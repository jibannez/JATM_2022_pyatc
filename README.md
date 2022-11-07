
# PYATC
## A library to produce ATClab configuration, parse simulation results and compute performance

### INSTALLATION

To install the library run the following from the root path of the package:

    pip3 install .

To install it in developer mode use this command:

    pip3 install -e .


### USAGE

This library can be used for three interrelated tasks in ATC experiments:
 1 - Parse log files produced by pact.exe after running an experimental trial.
 2 - Computation of COMETA index of complexity.
 3 - Programmatically create or create xml task files.

 Below I briefly describe each of these three tasks. Note that for the current experiments (which have manually
 defined xml tasks) you are only interested in the first two.

 In general, the library assumes that the log files are stored in one directory, and the xml task files and csv flow files are stored in another directory. The functions that operate in batch mode do not recursively scan the directory
 tree. Therefore, all the files that you want to process in a single run must reside in the same directory. For example:
  
  - Experiment1:
    - data:
        - High_6_PP1.xml.log
        - High_6_PP2.xml.log
        - High_6_PP3.xml.log
        - Low_6_PP1.xml.log
        - Low_6_PP2.xml.log
        - Low_6_PP3.xml.log
        - ...
    - task:
        - High_6.xml
        - Low_6.xml
        - Flows_High_6.xml.csv
        - Flows_Low_6.xml.csv

 Of course one can create complex hierarchies of directories to match experimental conditions and find a way to run the scripts for each and every file. This is something that we can adapt to better suit the state of affairs of a running experiment, but I would suggest to use something like the structure above, that greatly simplies the task.

### 1 - Parse log files produced by pact.exe after running an experimental trial.
Parsing is automatically performed by COMETA computation functions. However, if one desires to perform parsing
isolatedly on the log files, pyatc needs to know either a path to an specific log file, or a path that
contains multiple log files.

The syntax to parse a single file would be:
    logevents = pyatc.parse.run(logfilepath)

In addition, if we want to export the results of the parsing to matlab file, we would use:
    logevents = pyatc.parse.run(logfilepath, True)

The syntax to parse all files in directory would be:
    logevents = pyatc.parse.run_directory(logpath)

In its current form, the batch processing mode of log files does not allow to have matlab exported, though
this can be easily changed in the code. The name logevents is an arbitrary designation, one can choose other names.
This variable will contain the output of each of these calls (a more or less complex dictionary).


### 2 - Computation of COMETA index
To compute COMETA indexes, pyatc needs to know two paths of the local environment:
  - Log file path, the directory that stores the results of the experimental trials. 
  - Task file path, the directory that contains the task definition in xml, as well as the flows.

In all situations, when one uses batch processing these paths refer to directories that contains several
files to be processed, whereas in single file processing there path refer to the specific log and task files
that you want to process.

The syntax to compute a specific log file of a specific task is:
    res = pyatc.cometa.compute_cometa_file(logfilepath, taskfilepath, tmax, save2mat)

Using the example path structure presented above:
    res = pyatc.cometa.compute_cometa_file('Experiment1/data/High_6.xml.log', 'Experiment1/task/High_6.xml')

The syntax to compute all log files in a directory that match the tasks names defined in pyatc.cometa.TASKNAMES:
    res = pyatc.cometa.compute_cometa_dir(logpath, taskpath)

Using the example path structure presented above:
    res = pyatc.cometa.compute_cometa_file('Experiment1/data', 'Experiment1/task')

In this case, the variable res (again an arbitrary name) stores the return values of the functions. The cometa
computation functions return the following tables: cometa, cometa_aircrafts, conflicts, trjs. The most relevant 
in normal use is cometa table. The other tables are more usefull for debugging purposes and can typically be discarded.

Finally, the COMETA computation functions have an argument called save2mat that controls the exportation of the cometa results to a csv file that can be imported in matlab for further processing. The best method to load these csv into Matlab is to use readtable Matlab's function: [in matlab] cometatable = readtable('cometa_file.csv')

These csv files will be saved together with the logfiles that they come from, and its name is the logfile name + '_COMETA.csv'. To use file saving, simply add save2mat=True to the end of the function arguments, like this:
    res = pyatc.cometa.compute_cometa_file('Experiment1/data', 'Experiment1/task', save2mat=True)

### 3 - Programmatic creation of xml task files, as well as xml parsing [OUTDATED- NEEDS REFRESHMENT].

Next you can find several work flows that are enabled by the automatic task generation capabilities

#### A - Test default configuration

##### A.1 - Import library

    import pyatc

##### A.2 - Copy default task dict

    taskdict = pyatc.task.DEFAULT.copy()

##### A.3 - Generate xml

At any moment, you can generate a new xml file using the taskdict
with the configuration state at this time using the following command

    pyatc.generate_xml(taskdict, 'default_task.xml')
    
##### A.4 - Copy xml, run the simulation in atc, and move the xml.log back

The file genearated with the previous command is called default_task.xml and can be run
by patc.exe directly (to use it, copy the xml into the program folder).
Once the simulation has been run, copy the log file back into the directory where
python generates xml files.

##### A.5 - Compute cometa indexes

    conflicts, aircrafts, cometa_static, cometa_dynamic = pyatc.compute_cometa('default_task.xml')

##### A.6 - Show results of cometa indexes

    plt.plot(cometa_dynamic.sum(axis=1))

    totalcometa_static = sum([ v for k, v in cometa_static.items()])
    
    print("COMETA static complexity value: " + str(totalcometa_static))


####  B - Create a new route in a few steps

Test a different route:

##### B.1 - Create the waypoints if they are new

###### B.1.1 - Define new waypoints as a python list of tuples
 
    loc1 = [('y', '25'), ('x', '-110'), ('visible','on')]
    loc2 = [('y', '75'), ('x', '-190'), ('visible','on')]

###### B.1.2 - Add waypoints to the map 
You should use OrderedDict because pact.exe can be very picky with attribute order in xml.

    from collections import OrderedDict as OD
    taskdict['maps']['map001']['locations']['R8'] = OD(loc1)
    taskdict['maps']['map001']['locations']['R9'] = OD(loc2)

##### B.2 - Create a new route using your new waypoints

    taskdict['maps']['map001']['routes']['my_new_route'] = ['R8','R9']

##### B.3 - Add the new flow to the sky

###### B.3.1 - Copy flow 'R_Horiz' into 'my_new_route' to populate it with default properties

    taskdict['skies']['sky001']['flows']['my_new_route'] = taskdict['skies']['sky001']['flows']['R_Horiz'].copy()

###### B.3.2 - To remove a flow use pop() method of dictionaries

    taskdict['skies']['sky001']['flows'].pop('R_Horiz')

pop() returns the popped value, it can be discarded if left unassigned, to keep it you should do:

    route_dict = taskdict['skies']['sky001']['flows'].pop('R_Horiz')

After this command you have only 'R_Vert' 'R_Diag1', 'R_Diag2' and 'my_new_route' flows.
If you define a route in map001 but don't create a flow in sky001,
you will have the route painted but no aircraft flowing across.

##### B.4 - Eventually, change parameters of the flow

    taskdict['skies']['sky001']['flows']['my_new_route']['occupation'] = 4


####  C - Creating off-flow aircrafts

##### C.1 - Either create or copy an aircraft dictionary. Below I show how to create it.
    
    aircraft = {'type': 'SF34', 'start': 0, 'altitude': 14000, 'altitude_end': 24000, 'velocity': 240, 'flightpath': [(-15, 75), (100, 190)]}

##### C.2 - Assign the aircrat to the aircrafts dictionary. The key used will be the Call Name of the aircraft

    taskdict['skies']['sky001']['aircrafts']['VOZ961'] = aircraft


#### D - Creating multiple skies in a few steps

##### D.1 - Copy the first sky into the new skies
Define new skies that have the same property values as sky001 just copy sky001 into sky002 and sky003

    taskdict['skies']['sky002'] = taskdict['skies']['sky001'].copy()
    taskdict['skies']['sky003'] = taskdict['skies']['sky001'].copy()

##### D.2 - Modify properties of the new skies according to the desired experimental desing
Change ocuppations of the two flows in sky002 and sky003, that will create three complexity conditions
For the three trials that a participant would run.

    taskdict['skies']['sky002']['flows']['R_Diag1']['occupation'] = 4
    taskdict['skies']['sky002']['flows']['R_Diag2']['occupation'] = 4
    taskdict['skies']['sky002']['flows']['my_new_route']['occupation'] = 4
    taskdict['skies']['sky003']['flows']['R_Diag1']['occupation'] = 16
    taskdict['skies']['sky003']['flows']['R_Diag2']['occupation'] = 16
    taskdict['skies']['sky003']['flows']['my_new_route']['occupation'] = 16
    taskdict['skies']['sky003']['flows']['my_new_route']['altitude_end'] = 25000

The parameter altitude_end controls whether the flow is in evolution or stablished
Be warned that some values for the aircrafts or flows parameters are forbiden due to
operating conditions of the specific aircraft selected. patc.exe is quite clear
in reporting the exact error and the valid range of values when running such an xml.

##### D.3 - Modify the presentation to add these new trials
Because presentation needs strict ordering, it is better to create it from scratch using OrderedDict

###### D.3.1 Import OrderedDict, shortening its name improves readibility

from collections import OrderedDict as OD

###### D.3.2 Create experimental phase dictionary, just copy-paste and modify to suit

It may be interesting to add information blocks after each trial ends.
All the elements required are already in task.py phases definition.

    my_new_phase =  OD([
        ('wellcome', OD([
            ('type','instruction'),
            ('idxref','consent')
        ])),
        ('trial1', OD([
            ('type', 'trial'),
            ('sky', 'sky001'),
            ('param', 'parameters001'),
            ('map', 'map001'),
            ('events', OD([
                ('timeEvent',15*60), # lasts 15 minutes
            ])),
        ])),
        ('trial2', OD([
            ('type', 'trial'),
            ('sky', 'sky002'),
            ('param', 'parameters001'),
            ('map', 'map001'),
            ('events', OD([
                ('timeEvent',15*60), # lasts 15 minutes
            ])),
        ])),
        ('trial3', OD([
            ('type', 'trial'),
            ('sky', 'sky003'),
            ('param', 'parameters001'),
            ('map', 'map001'),
            ('events', OD([
                ('timeEvent',15*60), # lasts 15 minutes
            ])),
        ])),
        ('terminate', OD([
            ('type','instruction'),
            ('idxref','thanks')
        ])),
    ])

###### D.3.3 - Add the created phase to the dictionary. Replace the old phase stored in 'set001' with my_new_phase

    taskdict['phases']['set001'] = my_new_phase


#### E - Rotate the scenario

##### E.1 - Compute the center of the active sector, 

As rotation is performed around a point and we are usually interested in a "pure" rotation with
respect to the point of view, you should first find the center of the sector to to rotate around that point

    center = pyatc.get_sector_center(taskdict['maps']['map001']['sectors']['sector001'])

##### E.2 - Apply a rotation on all spatial elements in the scenario.

The angle is measured in radians. By default, a rotation of +-5 degrees
is applied to the DEFAULT taskdict to avoid purely vertical routes, as they
break the computation of conflicts.

    taskdict = pyatc.rotate_task(taskdict, center=center, alpha=-0.50) # rotates half radian clockwise


#### F. Testing new task

Finally, you would generate a new xml to test with pact.exe with the same command as before:
Generate xml file for pact.exe as done above

    pyatc.generate_xml(taskdict, 'name_of_task_002')


#### Plot scenario with python/matplotlib

In case you need to see the routes before creating the xml,
a trick to quickly plot all waypoints in a map using python is:

import plotting library
    
    import matplotlib.pylab as plt

Use a shortcut to locations,sector, and route just to reduce the length of the line
    
    locations = taskdict['maps']['map001']['locations']
    sector = taskdict['maps']['map001']['sectors']['sector001']['vertex']
    routes = taskdict['maps']['map001']['routes']

Create lists of x, y and labels

    x_locations = [ loc['x'] for loc in locations.values()]
    y_locations = [ loc['y'] for loc in locations.values()]
    labels = list(locations.keys())

Create sector coordinates for plotting

    x_sector = [x for (y,x) in sector]
    y_sector = [y for (y,x) in sector]

Repeat first point to close rect. Could also use Rect patch
    
    x_sector.append(x_sector[0])
    y_sector.append(y_sector[0])

Do the scatter plot
    
    fig, ax = plt.subplots()
    ax.scatter(x_locations, y_locations)
    for i, text in enumerate(labels):
        ax.annotate(text, (x_locations[i], y_locations[i]))
    ax.plot(x_sector, y_sector, 'b')

Add route lines
    for route in routes.values():
        route_x = [ float(locations[loc]['x']) for loc in route]
        route_y = [ float(locations[loc]['y']) for loc in route]
        ax.plot(route_x, route_y)

