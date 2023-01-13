# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Utils

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


##------------------ PACKAGE UTILITY FUNCITONS

def user_object_selection(filter_dots = False, display_message="Select Objects"):
    """
    asks user to select objects - takes selected objects - warns if nothing is selected
    """
    objs = rs.SelectedObjects()
    if not objs or len(objs)==0:
        objs = rs.GetObjects(display_message)

    if not objs or len(objs) == 0:
        rs.MessageBox("No objects selected.", 0, "HdM BIM LIGHT")
        return None

    rs.UnselectAllObjects()

    rel_objs = []
    if filter_dots == True:
        for obj in objs:
            if BL_TEMP in rs.GetUserText(obj):
                continue
            else:
                rel_objs.append(obj)
    else:
        rel_objs = objs

    return rel_objs

def create_bl_layer(layer):
    """creates bim light layer if it does not exist"""
    if not rs.IsLayer(layer):
        layer = rs.AddLayer(layer, BL_LAYER_COLOR, True)
    return

def wipe_layer(layer):
    """deletes all objects on layer and layer itself"""
    if rs.IsLayer(layer):
        obj_ids = rs.ObjectsByLayer(layer)
        rs.DeleteObjects(obj_ids)
        rs.DeleteLayer(layer)
    return

def get_unit_conversion_factor():
    conversion_factor = rs.GetDocumentUserText(DOC_KEY_UNIT_CONVERSION_FACTOR)
    if conversion_factor == None:
        return 1
    elif is_float(conversion_factor):
        return float(conversion_factor)
    else:
        return 1

def set_unit_conversion_factor(user_input):
    if user_input:
        conversion_factor = CONVERSION_LOOKUP_TABLE.get(user_input)
        rs.SetDocumentUserText(DOC_KEY_UNIT_CONVERSION_FACTOR, str(conversion_factor))
        rs.SetDocumentUserText(DOC_KEY_DISPLAY_UNIT, user_input)
        return conversion_factor
    else:
        return None

def get_unit_conversion():
    conversion_unit = rs.GetDocumentUserText(DOC_KEY_DISPLAY_UNIT)
    if conversion_unit == None:
        return None
    else:
        return conversion_unit

def get_round_dig_overwrite():
    """
    gets the number stored in the document user text under DOC_KEY_ROUND_DIGIT
    """
    round_overwrite = rs.GetDocumentUserText(DOC_KEY_ROUND_DIGIT)
    if is_int(round_overwrite):
        return int(round_overwrite)
    else:
        return None

def set_round_dig_overwrite(digits):
    """
    sets the number stored in the document user text under DOC_KEY_ROUND_DIGIT
    """
    if digits == ROUND_DIGIT_STD_STR:
        rs.SetDocumentUserText(DOC_KEY_ROUND_DIGIT)
        return True

    if not is_int(int(digits)) or int(digits) < 0:
        return None
    else:
        rs.SetDocumentUserText(DOC_KEY_ROUND_DIGIT, digits)
    return True

def is_float(value):
    """checks if value is float"""
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_int(value):
    """checks if value is an integer"""
    if value != None:
        try:
            int(value)
            return True
        except ValueError:
            return False
    else:
        return None

def process_exists(process_name):
    # checks if a process is running or not
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def prepare_file_path(file_name, dir_path):
    # check if directory exists, if not create it
    if not op.exists(dir_path):
        os.makedirs(dir_path)
    # create a file path from a file name and a directory path
    csv_name = "{}.csv".format(file_name)
    csv_path = op.join(dir_path, csv_name)
    return csv_path

def color_str_to_tuple(colorString):
    """
    converts UserText to tuple with color info for BIM LIGHT
    """
    rgbValues = colorString.split(DELIMITER)
    return (int(rgbValues[0]), int(rgbValues[1]), int(rgbValues[2]))

##--------------------- USER TEXT FUNCTIONS

def get_data_for_objs(objs):
    """gets all keys for the objects and returns a list of string"""

    obj_user_datas = []

    for obj in objs:
        data = {}
        keys = rs.GetUserText(obj)

        for ke in keys:
            data[ke] = rs.GetUserText(obj, ke)
            data[ke] = parse_user_text_function_value(data[ke], obj)

        obj_user_datas.append(data)
    return obj_user_datas

def parse_user_text_function_value(uTxt, objID):
    """
    tries to parse a user text function from rhino.
    checks start and end of string to identify it
    """
    if not uTxt:
        return uTxt
    if uTxt[:2] == "%<" and uTxt[-2:] == ">%":
        obj = rs.coercerhinoobject(objID)
        uTxt = Rhino.RhinoApp.ParseTextField(uTxt, obj, None)
    return uTxt

def create_bl_group_table():
    """
    Creates bl group table.
    Rhino group table gets corrupted when using undo.
    """

    all_objects = rs.AllObjects()
    all_groups = rs.GroupNames()
    group_table = {}

    for obj in all_objects:
        groups = rs.ObjectGroups(obj)
        for group in groups:
            if BL_PREFIX in group:
                if not group in group_table:
                    group_table[group] = [obj]
                else:
                    group_table[group].append(obj)
    return group_table

def objects_by_bl_group(group_name, group_table=False):
    """
    replaces rs.ObjectsByGroup.
    Reason: Group table corruption when undoing.
    """
    if not group_table:
        group_table = create_bl_group_table()
    if group_name not in group_table:
        return None

    objects_by_group = group_table[group_name]
    return objects_by_group

def get_bl_group(obj):
    """
    Saves the bl group for a BIM LIGHT object as User Text
    """
    allGroups = rs.ObjectGroups(obj)
    blGroups = []
    if not allGroups or len(allGroups) == 0:
        return None
    for gr in allGroups:
        if BL_PREFIX in gr:
            blGroups.append(gr)
    if len(blGroups) == 1:
        return blGroups[0]
    elif len(blGroups) == 0:
        return None
    else:
        print ("HdM-BL: Too many BL groups. Contact DT")
        return

##--------------------- VISUALIZE AND GROUPING FUNCTIONS (Idea: Convert to classes / use class inheritance)

def get_bl_groups():
    """
    gets the current bl groups
    """
    allGroups = rs.GroupNames()
    bl_group_names = []
    if allGroups:
        for gr in allGroups:
            if BL_PREFIX in gr:
                bl_group_names.append(gr)

    return bl_group_names

def get_bl_grouping_key_info(obj):
    """
    sets the bl_info user text to identify the data that is shown
    """
    uT = rs.GetUserText(obj, KEY_GROUP_KEY)
    if not uT:
        return None
    return uT

def get_bl_key_info(obj):
    """
    sets the bl_info user text to identify the data that is shown
    """
    uT = rs.GetUserText(obj, KEY_KEY)
    if not uT:
        return None
    return uT

def set_bl_key_info(obj, value):
    """
    sets the bl_info user text to identify the data that is shown
    """
    rs.SetUserText(obj, KEY_KEY, value)
    return True
