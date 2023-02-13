# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Grouping

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
from visualize import _visualize_data_for_objs
from visualize import VisualizeUserDataByGrouping
from utilsbl import *

##------------------ PUBLIC FUNCTIONS

def SaveGroupingAs():
    """
    Saves the current bim light group setup under a name parameter
    """
    group_names = get_bl_groups()
    if len(group_names) == 0:
        print ("BIM LIGHT Error: No BL groups existing")
        return
    param_name = rs.StringBox("Enter grouping name (Do not use existing parameters)", "Grouping01", "HdM BIM Light")
    if param_name == None:
        return

    all_objects = rs.AllObjects()
    objUserDatas = get_data_for_objs(all_objects)

    param_exists = False
    for data in objUserDatas:
        for key in data:
            if key == param_name:
                param_exists = True
    if param_exists == True:
        rs.MessageBox("Parameter already exists", 0, "HdM BIM Light")
        return



    allobjs = []

    count = 0
    gr_table = create_bl_group_table()
    for group in gr_table:
        count += 1
        objs = objects_by_bl_group(group, gr_table)
        if objs == None:
            continue

        for obj in objs:
            color = rs.ObjectColor(obj)
            test_color = _convert_color_to_tuple(color)
            if test_color != NOT_DEFINED_COLOR and rs.ObjectType(obj) != 8192:
                found_color = color
                break
            found_color = NOT_DEFINED_COLOR


        for obj in objs:
            if obj not in allobjs:
                allobjs.append(obj)
                rs.SetUserText(obj, param_name, param_name + BL_GROUPING_NAME + str(count).zfill(3))
                _set_bl_grouping_color (obj, param_name, found_color)

    VisualizeUserDataByGrouping(False, allobjs, param_name)
    return


def AssignGroupColor():
    """
    sets a new color for a group
    """
    #get objects

    objs_raw = rs.SelectedObjects()
    if not objs_raw:
        objs_raw = user_object_selection(True)
        if not objs_raw:
            return
    objs = []
    for obj in objs_raw:
        if rs.GetUserText(obj, BL_TEMP) != "True":
            objs.append(obj)

    grouping_values = []
    for obj in objs:
        if not rs.GetUserText(obj, BL_TEMP) == "True":
            group_key_value = get_bl_grouping_key_info(obj)
            if not group_key_value:
                rs.MessageBox("Create and save grouping first.", 0, "HdM BIM LIGHT")
                return
            grouping_value = rs.GetUserText(obj, group_key_value)
            grouping_value = parse_user_text_function_value(grouping_value, obj)
            if len(grouping_values) == 0:
                grouping_values.append(grouping_value)
                data_vis_value = get_bl_key_info(obj)
                color = _get_bl_grouping_color(obj, group_key_value)
            else:
                if grouping_value in grouping_values:
                    grouping_values.append(grouping_value)
                else:
                    rs.MessageBox("Select only one group to assign color.", 0, "HdM BIM LIGHT")
                    return

    if not color:
        new_color = rs.GetColor()
    else:
        new_color = rs.GetColor(color)
    if not new_color:
        return

    for obj in objs:
        _set_bl_grouping_color(obj, group_key_value, new_color)

    rs.EnableRedraw(False)
    _visualize_data_for_objs(objs, group_key_value, data_vis_value, new_color)
    rs.EnableRedraw(True)
    return
    

def RenameGroup():
    """
    sets a new name for a group
    """
    #get objects

    objs_raw = rs.SelectedObjects()
    if not objs_raw:
        objs_raw = user_object_selection(True)
        if not objs_raw:
            return
    objs = []
    for obj in objs_raw:
        if rs.GetUserText(obj, BL_TEMP) != "True":
            objs.append(obj)

    grouping_values = []
    for obj in objs:
        if not rs.GetUserText(obj, BL_TEMP) == "True":
            group_key_value = get_bl_grouping_key_info(obj)
            if not group_key_value:
                rs.MessageBox("Create and save grouping first.", 0, "HdM BIM LIGHT")
                return
            grouping_value = rs.GetUserText(obj, group_key_value)
            grouping_value = parse_user_text_function_value(grouping_value, obj)
            if len(grouping_values) == 0:
                data_vis_value = get_bl_key_info(obj)
                grouping_values.append(grouping_value)
                color = _get_bl_grouping_color(obj, group_key_value)
                if not color:
                    color = _convert_color_to_tuple(rs.ObjectColor(obj))
            else:
                if grouping_value in grouping_values:
                    grouping_values.append(grouping_value)
                else:
                    rs.MessageBox("Select only one group to assign color.", 0, "HdM BIM LIGHT")
                    return

    param_value = rs.StringBox("Enter group name (Do not use existing parameters)", grouping_value, "HdM BIM Light")
    if param_value == None:
        return

    for obj in objs:
        _set_bl_grouping_key_value(obj, param_value)

    rs.EnableRedraw(False)
    _visualize_data_for_objs(objs, group_key_value, data_vis_value, color)
    rs.EnableRedraw(True)
    return

##------------------------ PRIVATE FUNCTIONS

def _set_bl_grouping_key_value(obj, group_val):
    """
    gets BIM LIGHT visualization value
    """
    key = get_bl_grouping_key_info(obj)
    if not key:
        print ("BL: Error: Object does not have the requested key")
        return "NoKey"
    else:
        uT = rs.SetUserText(obj, key, group_val)
    if uT == None:
        return None
    else:
        return uT

def _convert_color_to_tuple(col):

    if not col:
        return None
    else:
        return (col.R,col.G,col.B)

def _set_bl_grouping_color(obj, grouping_key, col):
    """
    saves the grouping color
    """
    colorValue = col
    colorValue = str(col[0]) + DELIMITER + str(col[1]) + DELIMITER + str(col[2])
    rs.SetUserText(obj, BL_INFO + grouping_key + BL_COLOR_SUFFIX, colorValue)
    return

def _get_bl_grouping_color(obj, grouping_key):
    """
    get the color tuple for a grouping of an object
    """
    value_color = rs.GetUserText(obj, BL_INFO + grouping_key + BL_COLOR_SUFFIX)
    if value_color:
        try:
            color_tuple = color_str_to_tuple(value_color)
        except:
            print ("HdM-BL: Color value probably has wrong format")
        return color_tuple
    else:
        return None


        