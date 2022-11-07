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
from collections import OrderedDict as OD

from .xml import addns, XSINS, ATCURI
from .geom import rotate_task, get_sector_center

DEFAULT = OD()

DEFAULT['experiment'] = OD([
    (addns('schemaLocation', XSINS), ATCURI+' atc_lab-2006-05.xsd'),
    (addns('idx'), 'CRIDA_001')
    ])

################################
# Global configurations
################################
DEFAULT['instructions'] = OD([
    ('consent', OD([
        ('text', """
        <qt>
          <center>
            <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
            <tr><td align="left"><font face="verdana" size="1">
              <p align="center"><font size="+4">Participation consent</font></p>
              <p align="center"><font size="+1">Participation in this study is entirely voluntary. Your data will remain confidential and anonymous. You have the right to withdraw at any time during the experiment without penalty. If you wish to withdraw from the study, please notify the researcher immediately. </font></p>
              <p align="center"><font size="+1">I have read and understand the information sheet and consent form and volunteer to participate in this research.</font></p>
              <p align="center"><font size="+1"><b>Press the [SPACE] key if you agree to volunteer to participate in this research<b></font></p>
              <p align="center"><font size="+1"><b>Inform the experimenter immediately if you do not agree to participate in this research<b></font></p>
            </font></td></tr>
            </table>
          </center>
        </qt>"""),
        ('keyEvent','Space'),
    ])),# end of consent
   ('demonstrationinstruction', OD([
        ('text', """
            <qt>
              <center>
                <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
                <tr><td align="left"><font face="verdana" size="1">
                  <p align="center"><font size="+1">The experimenter will now explain and demonstrate the use of the software involved.</font></p>
                  <p align="center"><font color="red"><b>something else<b></font></p>
                </font></td></tr>
                </table>
              </center>
            </qt>"""),
        ('keyEvent','Space'),
    ])),# end of demonstrationinstruction
    ('practicetrial', OD([
        ('text', """
            <qt>
              <center>
                <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
                <tr><td align="left"><font face="verdana" size="1">
                  <p align="center"><font size="+1">You will now begin a 2 min practice trial.</font></p>
                  <p align="center"><font color="red"><b>Please SPACE bar once you are ready<b></font></p>
                </font></td></tr>
                </table>
              </center>
            </qt>"""),
        ('keyEvent','Space'),
    ])),# end of practicetrial
    ('itrial1', OD([
        ('text', """
            <qt>
              <center>
                <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
                <tr><td align="left"><font face="verdana" size="1">
                  <p align="center"><font size="+1">You will now begin the actual experiment.</font></p>
                  <p align="center"><font color="red"><b>Please SPACE bar once you are ready<b></font></p>
                </font></td></tr>
                </table>
              </center>
            </qt>"""),
        ('keyEvent','Space'),
    ])),# end of itrial1
    ('itrial2', OD([
        ('text', """
            <qt>
              <center>
                <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
                <tr><td align="left"><font face="verdana" size="1">
                  <p align="center"><font size="+1">Press the Space Bar to start the 2nd trial.</font></p>
                </font></td></tr>
                </table>
              </center>
            </qt>"""),
        ('keyEvent','Space'),
    ])),# end of trial2
    ('itrial3', OD([
        ('text', """
            <qt>
              <center>
                <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
                <tr><td align="left"><font face="verdana" size="1">
                  <p align="center"><font size="+1">Press the Space Bar to start the 3rd trial.</font></p>
                </font></td></tr>
                </table>
              </center>
            </qt>"""),
        ('keyEvent','Space'),
    ])),# end of trial3
    ('blank', OD([
        ('text', "<qt><center></center></qt>"),
        ('keyEvent','Space'),
    ])),# end of blank
    ('endofphase', OD([
        ('text', """
        <qt>
          <center>
            <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
            <tr><td align="left"><font face="verdana" size="1">
              <p align="center"><font size="+1">Please inform the experimenter before continuing on to the next part of the experiment.</font></p>
            </font></td></tr>
            </table>
          </center>
        </qt>"""),
        ('keyEvent','Space'),
    ])),# end of endofphase
    ('thanks', OD([
        ('text', """
            <qt>
              <center>
                <table width="60%" bgcolor="darkCyan" border="0" cellspacing="0" cellpadding="50">
                <tr><td align="left"><font face="verdana" size="1">
                  <p align="center"><font size="+1">Thank you for your participation.</font></p>
                  <p align="center"><font color="red"><b>Please inform your experimenter that the experiment is complete.<b></font></p>
                </font></td></tr>
                </table>
              </center>
            </qt>"""),
        ('keyEvent','Space'),
    ])),# end of thanks
]) # end of instructions


# Types: validated_question, choice_question, scale_question, multi_question
### ONLY FOR WILSON VERSION!!!!
# DEFAULT['questions'] = OD([
#     ('age', OD([
#         ('type', 'validated_question'),
#         ('text', 'How old are you?'),
#         ('validator', OD([
#             ('min', 18),
#             ('max', 65),
#             ('text','* Please enter a value between '16' and '90' inclusive!'),
#         ])),
#     ])),
#     ('gender', OD([
#         ('type', 'choice_question'),
#         ('text', 'What is your gender?'),
#         ('choices', OD([
#             ('0', 'Male'),
#             ('1', 'Female'),
#         ])),
#     ])),
#     ('difficulty', OD([
#         ('type', 'validated_question'),
#         ('text', 'How difficult you think the previous block was?'),
#         ('validator', OD([
#             ('min', 1),
#             ('max', 5),
#             ('text','* Please enter a value between '1' and '5' inclusive!'),
#         ])),
#     ])),
# ])

# DEFAULT['inputs'] = OD([
#     ('inputAge', OD([
#         ('font', OD([
#             ('family', 'sans-serif'),
#             ('pointSize', 10),
#             ('weight', 70),
#             ('italic', 'false'),
#         ]),
#         ('ui_component', 'age'))
#     ])),
#     ('inputGender', OD([
#         ('font', OD([
#         ]),
#         ('ui_component', 'gender'))
#     ])),
#     ('inputDifficulty1', OD([
#         ('font', OD([
#             ('family', 'sans-serif'),
#             ('pointSize', 10),
#             ('weight', 70),
#             ('italic', 'false'),
#         ]),
#         ('ui_component', 'difficulty'))
#     ])),
#     ('inputDifficulty2', OD([
#         ('font', OD([
#             ('family', 'sans-serif'),
#             ('pointSize', 10),
#             ('weight', 70),
#             ('italic', 'false'),
#         ]),
#         ('ui_component', 'difficulty'))
#     ])),
#     ('inputDifficulty3', OD([
#         ('font', OD([
#             ('family', 'sans-serif'),
#             ('pointSize', 10),
#             ('weight', 70),
#             ('italic', 'false'),
#         ]),
#         ('ui_component', 'difficulty'))
#     ])),
# ])

DEFAULT['units'] = 'NM-FT'

DEFAULT['aircraft_models'] = ['SF34', 'A320','B737']

################################
# Sets of parameters
################################
DEFAULT['parameter_sets'] = OD([
    ('parameters001', OD([
        ('update_rate', 1000),
        ('scenario_tester', 1),
        #??('horizontal_doms', 5),
        #??('vertical_doms', 999),
        ('cs_none_colour', 'black'),
        ('cs_annonced_colour', 'blue'),
        ('cs_accepted_colour', 'darkGreen'),
        ('cs_handoff_colour', 'white'),
        ('cs_nomore_colour', 'black'),
        ('cs_overout_colour', '#FF8000'),
        ('cs_proposed_colour', OD([
            ('attrib', {'blink':'yes'}),
            ('text', '#FF8000'),
            ]))
    ])), # end of default
]) # end of parameters

################################
# Set of maps
################################
DEFAULT['maps'] = OD([
    ('map001', OD([
        ('region', ('250', '-50', '400', '-110')),
        ('locations', OD([
            # Location of points and routes of the map
            # Horizontal route
            ('R0', OD([('y', '75'), ('x', '-130'), ('visible','on')])),
            ('R1', OD([('y', '75'), ('x', '300'), ('visible','on')])),
            # Vertical route, commented out to reduce clutter
            #('R2', OD([('y', '-80'), ('x', '80'), ('visible','on')])),
            #('R3', OD([('y', '250'), ('x', '80'), ('visible','on')])),
            # Diag1 route
            ('R4', OD([('y', '-80'), ('x', '-130'), ('visible','on')])),
            ('R5', OD([('y', '250'), ('x', '300'), ('visible','on')])),
            # Diag2 route
            ('R6', OD([('y', '-80'), ('x', '300'), ('visible','on')])),
            ('R7', OD([('y', '250'), ('x', '-130'), ('visible','on')])),
        ])), # end of locations
        ('routes', OD([
            ('R_Horiz', ['R0', 'R1']),
            #('R_Vert', ['R2', 'R3']),
            ('R_Diag1', ['R4', 'R5']),
            ('R_Diag2', ['R6', 'R7']),
        ])), # end of routes
        ('sectors', OD([
            ('sector001', OD([
                ('status', 'active'),
                ('vertex', [(0, 0), (150, 0), (150, 180), (0, 180)]),
                #('vertex'-> y,x) Multiple points required
                #('arc'-> r,y,x) Only one line required
            ])), # end of default sector
        ])) # end of sectors
    ])), # end of map001
]) # end of maps

################################
# Set of skies
################################
DEFAULT['skies'] = OD([
    ('sky001', OD([
        # Set of out of flow aircrafts
        ('aircrafts', OD([
            ('LTL111', OD([
                ('type', 'SF34'),
                ('start', 0),
                ('altitude', 17000),
                ('altitude_end', 17000),
                ('velocity', 240),
                ('flightpath', [(95, 75), (200, 290)])
                # <atc:pointref atc:location='pointNE' /> for flightpaths not supported yet
            ])), # end of LTL111
            ('LTL112', OD([
                ('type', 'SF34'),
                ('start', 0),
                ('altitude', 11000),
                ('altitude_end', 11000),
                ('velocity', 240),
                ('flightpath', [(150, 160), (115, 75)])
                # <atc:pointref atc:location='pointNE' /> for flightpaths not supported yet
            ])), # end of LTL111
        ])), # end of aircrafts
        ('areas',OD([])), # for coulds and stuff like that
        # Parameters to define standard flows
        ('flows', OD([
            ('R_Horiz', OD([
                ('map', 'map001'),
                ('types', ['A320', 'B737']),
                ('basenames', ['VOZ','QCA','JSN']),
                ('altitude', (37000, 37000) ), # only one altitude pair (no random sampling), and same start and end altitude
                ('jitter', 10), # percentaje -> +/- 5% of randomness
                ('offset', 10),  # nautic miles
                ('velocity', 480),
                ('time', 15*60), # total time in seconds
                ('occupation', 18), # planes per hour
            ])), # end of R_Horiz flow
            ('R_Diag1', OD([
                ('map', 'map001'),
                ('types', ['A320','B737']),
                ('basenames', ['VOZ','QCA','JSN']),
                ('altitude', [(37000, 37000), (35000, 30000)] ), # two altitude pairs to choose from, one in evolution
                ('jitter', 10), # percentaje -> +/- 5% of randomness
                ('offset', 10),  # nautic miles
                ('velocity', 500),
                ('time', 15*60), # total time in seconds
                ('occupation', 12), # planes per hour
            ])),# end of R_Diag1 flow
            ('R_Diag2', OD([
                ('map', 'map001'),
                ('types', ['A320','B737']),
                ('basenames', ['VOZ','QCA','JSN']),
                ('altitude', [(37000, 37000), (35000, 35000)] ), # two altitude pairs to choose from, both stablished
                ('jitter', 10), # percentaje -> +/- 5% of randomness
                ('offset', 10),  # nautic miles
                ('velocity', 500),
                ('time', 15*60), # total time in seconds
                ('occupation', 12), # planes per hour
            ])),# end of R_Diag2 flow
        ])) # end of flows
    ])), #end of sky001
]) # end of skies

DEFAULT['phases']    = OD([
    ('set001', OD([
        ('wellcome', OD([
            ('type','instruction'),
            ('idxref','consent')
        ])),
        #('inputAge', OD(['type', 'input'])),
        #('inputGender', OD(['type', 'input'])),
        # ('demonstrationinstruction', OD([
        #     ('type','instruction'),
        #     ('idxref','consent')
        # ])),
        # ('practicetrial', OD([
        #     ('type','instruction'),
        #     ('idxref','consent')
        # ])),
        # ('itrial1', OD([
        #     ('type','instruction'),
        #     ('idxref','itrial1')
        # ])),
        ('trial1', OD([
            ('type', 'trial'),
            ('sky', 'sky001'),
            ('param', 'parameters001'),
            ('map', 'map001'),
            ('events', OD([
                ('timeEvent',15*60), # lasts 5 minutes
            ])),
        ])),
        # ('inputDifficulty1', OD(['type', 'input'])),
        # ('itrial2', OD([
        #     ('type','instruction'),
        #     ('idxref','itrial2')
        # ])),
        # ('trial2', OD([
        #     ('type', 'trial'),
        #     ('sky','sky002'),
        #     ('param','parameters001'),
        #     ('map','map001'),
        #     ('events', OD([
        #         ('timeEvent',15*60), # lasts 15 minutes
        #     ])),
        # ])),
        # ('inputDifficulty2', OD(['type', 'input'])),
        # ('itrial3', OD([
        #     ('type','instruction'),
        #     ('idxref','itrial3')
        # ])),
        # ('trial3', OD([
        #     ('type', 'trial'),
        #     ('sky','sky003'),
        #     ('param','parameters001'),
        #     ('map','map001'),
        #     ('events', OD([
        #         ('timeEvent',15*60), # lasts 15 minutes
        #     ])),
        # ])),
        # ('inputDifficulty3', OD(['type', 'input'])),
        # ('endofphase', OD([
        #     ('type','instruction'),
        #     ('idxref','endofphase')
        # ])),
        ('terminate', OD([
            ('type','instruction'),
            ('idxref','thanks')
        ])),
    ])), # end of set001
])


# Apply a default rotation of 1/2 radian to avoid perfectly vertical routes
DEFAULT = rotate_task(DEFAULT, center=get_sector_center(DEFAULT['maps']['map001']['sectors']['sector001']), alpha=.20)
