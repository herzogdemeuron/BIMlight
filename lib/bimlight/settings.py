# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Settings

    Created on 29. June 2022 by j.hoell, y.schindel

'''

##------------------ IMPORTS
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
from datetime import datetime
import time
import os
import os.path as op
import math
import json
import csv
import shutil # standard module to copy a file
import subprocess
from variablesbl import *
from utilsbl import *

##------------------ FUCTIONS

def SettingsBimLight():
    """
    Creates Parameters from geometery
    """

    wipe_layer(BL_LAYER_GEO)

    setting_options = []
    for entry in BL_SETTINGS:
        setting_options.append(entry[2])

    setting_vars = BL_SETTINGS#bl mass calculation variables


    user_setting_selection = rs.ListBox(setting_options,
    "Settings", "HdM BIM LIGHT")
    if user_setting_selection == None:
        return


    ### CONVERSION
    conversion_factor = get_unit_conversion_factor()
    if user_setting_selection == setting_options[0]:
        conversion_unit = get_unit_conversion()
        user_input = rs.GetString(MSG_PREFIX + "set conversion unit (current: %s)" %conversion_unit, conversion_unit, list(CONVERSION_LOOKUP_TABLE.keys()))
        conversion_factor = set_unit_conversion_factor(user_input)
        return


    ### ROUNDING ####
    if user_setting_selection == setting_options[1]:
        round_ow = get_round_dig_overwrite()
        if round_ow == None:
            round_ow = ROUND_DIGIT_STD_STR
        else: round_ow = str(round_ow)
        user_input = rs.GetString(MSG_PREFIX + "set number of decimals for decimals", round_ow, [ROUND_DIGIT_STD_STR])
        dig_overwrite = set_round_dig_overwrite(user_input)
        if dig_overwrite == None:\
            rs.MessageBox("Not valid. Please enter a positiv number.", 0, "HdM BIM LIGHT")

        
    return

