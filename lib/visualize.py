# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Visualize

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

##------------------ PUBLIC FUNCTIONS

def VisualizeUserDataByColor(   chose_color = False,
                                color_one = STANDARD_COLOR_1,
                                color_two = STANDARD_COLOR_2,
                                defined_input = False,
                                objects_input = None,
                                key_input= None):

    # chose_color:
    #       False: color manually set by global paramter or color_one, color_two arguments)
    #       True: color chosen by user in rhino UI
    # color_one, color_two:
    #       format: (R,G,B)
    #       defines the color gradiant from color_one to color_two
    # defined_input:
    #       True: input objects and,or key defined by argument
    #       False: input objects chosen by user in rhino UI
    # objects_input:
    #       [guids] - argument containing rhino object guids
    # key_input:
    #       str - user text key
    """
    Visualizes User Data by Color for BIM LIGHT
    """
    wipe_layer(BL_LAYER_GEO)

    #user object selection
    if defined_input == True and objects_input != None:
        objs_raw = objects_input
    else:
        objs_raw = user_object_selection()

    if not objs_raw:
        return

    objs = []
    print ("BL: TextDots are not considered")
    for obj in objs_raw:
        if rs.GetUserText(obj, BL_TEMP) != "True":
            objs.append(obj)

    rs.EnableRedraw(False)

    validKeys = []

    objUserDatas = get_data_for_objs(objs)

    for data in objUserDatas:
        for key in data:
            if key not in validKeys and BL_TEMP not in key and BL_INFO not in key:
                validKeys.append(key)

    if len(validKeys) == 0:
        rs.MessageBox("No information to visualize. \nApply UserText information first.", 0, "HdM BIM LIGHT")
        return

    #sorting single keys
    validKeys = sorted(validKeys)

    if defined_input == True and key_input in validKeys:
        userDataSelection = key_input
    else:
        userDataSelection = rs.ListBox(validKeys,
        "You have selected %i objects. \nWhich information do you want to visualize?" %len(objs), "HdM BIM LIGHT")
    if userDataSelection == None:
        return

    chosenData = []
    uniqueData = []
    for i in range(len(objs)):
        if userDataSelection in objUserDatas[i]:
            val = objUserDatas[i][userDataSelection]
            chosenData.append(val)
            if val not in uniqueData:
                uniqueData.append(val)
        else:
            chosenData.append(None)

    if chose_color == True:
        color1 = rs.GetColor(color_one)
        if color1 == None:
            return
        color2 = rs.GetColor(color_two)
        if color2 == None:
            return
    else:
        color1 = color_one
        color2 = color_two

    relColorDictonary = _value_color_range(uniqueData, color1, color2)

    #create color dictonary of different values

    #reset visualization
    _reset_visualization(objs)

    #get group count to avoid duplicat group names
    currentGroupCount = _get_bl_group_count()

    for i in range(len(objs)):

        _set_bl_info_original_color(objs[i])
        set_bl_key_info (objs[i], userDataSelection)

        if chosenData[i] == None or chosenData[i] == VALUE_ERROR:

            rs.ObjectColor(objs[i], NOT_DEFINED_COLOR)

            groupName = BL_PREFIX + DELIMITER + str(currentGroupCount + i + 1)
            rs.AddGroup(groupName)
            rs.AddObjectsToGroup([objs[i]], groupName)

        else:
            groupName = BL_PREFIX + DELIMITER + str(currentGroupCount + i + 1)
            rs.ObjectColor(objs[i], relColorDictonary[chosenData[i]])

            rs.AddGroup(groupName)
            rs.AddObjectsToGroup([objs[i]], groupName)

    #Info visualization
    _visualize_user_data_by_object(objs)

    rs.EnableRedraw(True)
    print ("HdM-BL: Visualization color applied")
    return True


def VisualizeUserDataReset(all_auto = False):
    """
    resets group by removing the obj from the group and deleting all associated items
    """


    if all_auto == False:
        all_flag = 0

        if rs.SelectedObjects():
            rs.EnableRedraw(False)
            result = _reset_visualization(rs.SelectedObjects())
            rs.EnableRedraw(True)
            return result

        msgObj = rs.MessageBox("Do you want to reset all? \nPress <No> for selection", 3 | 256, "HdM BIM LIGHT")
        if msgObj == 7:
            objs = rs.GetObjects("Select objects for visualiztion reset")
            if not objs:
                return
        elif msgObj == 6:
            objs = rs.AllObjects()
            all_flag = 1
        else:
            return
    else:
        objs = rs.AllObjects()
        all_flag = 1

    #RESET PROCESS
    rs.EnableRedraw(False)
    if all_flag == 1:
        result = _reset_visualization(objs, True)
    else:
        result = _reset_visualization(objs, False)
    rs.EnableRedraw(True)

    return result


def VisualizeUserDataBySum():
    """
    Visualizes User Data sum for BIM LIGHT
    """
    wipe_layer(BL_LAYER_GEO)
    #user object selection
    objs_raw = user_object_selection()

    if not objs_raw:
        return

    objs = []
    print ("BL: TextDots are not considered")
    for obj in objs_raw:
        if rs.GetUserText(obj, BL_TEMP) != "True":
            objs.append(obj)

    rs.EnableRedraw(False)

    validKeys = []

    objUserDatas = get_data_for_objs(objs)

    for data in objUserDatas:
        for key in data:
            if key not in validKeys and BL_TEMP not in key and BL_INFO not in key:
                validKeys.append(key)

    #sorting single keys
    validKeys = sorted(validKeys)

    validKeys.insert(0, BL_NONE)
    userDataSelection = rs.ListBox(validKeys,
    "You have selected %i objects. \nWhich information do you want to visualize? <None> for Grouping" %len(objs), "HdM BIM LIGHT", BL_NONE)
    if userDataSelection == None:
        return

    chosenData = []
    uniqueData = []
    for i in range(len(objs)):
        if userDataSelection in objUserDatas[i]:
            val = objUserDatas[i][userDataSelection]
            chosenData.append(val)
            if val not in uniqueData:
                uniqueData.append(val)
        else:
            chosenData.append(None)


    chosen_color = rs.GetColor(STANDARD_COLOR_1)
    if chosen_color == None:
        return

    #Reset visualization
    _reset_visualization(objs)

    #get group count to avoid duplicat group names
    currentGroupCount = _get_bl_group_count()

    #block implementation
    block_bbxs = []

    for i in range(len(objs)):

        _set_bl_info_original_color(objs[i])
        set_bl_key_info (objs[i], userDataSelection)
        block_bbx = None

        if chosenData[i] == None:
            rs.ObjectColor(objs[i], NOT_DEFINED_COLOR)
            #block implementation
            block_bbx = _block_bbx_color(objs[i], NOT_DEFINED_COLOR)
        else:
            rs.ObjectColor(objs[i], chosen_color)
            #block implementation
            block_bbx = _block_bbx_color(objs[i], chosen_color)
        if block_bbx:
            block_bbxs.append(block_bbx)



    groupName = BL_PREFIX + DELIMITER + str(currentGroupCount + i + 1)

    rs.AddGroup(groupName)
    rs.AddObjectsToGroup(objs, groupName)

    # value calc
    bl_sum = 0
    flag = 0
    flag_concat = 0
    concat_list = []
    for obj in objs:
        value = rs.GetUserText(obj, userDataSelection)
        value = parse_user_text_function_value(value, obj)
        if not value:
            flag_concat = 1
            if VALUE_ERROR in concat_list:
                continue
            else:
                concat_list.append(VALUE_ERROR)
            continue

        else:
            if is_float(value):
                if str(value) not in concat_list:
                    concat_list.append(str(value))
            else:
                if value not in concat_list:
                    concat_list.append(value)
                flag_concat = 1
                continue
            flag = 1
            bl_sum += float(value)
    if flag == 0:
        print ("HdM-BL: No numbers to sum up")
    if flag_concat == 1:
        bl_sum = ""
        for t in range(len(concat_list)):
            if t == 0:
                bl_sum = concat_list[t]
            else:
                bl_sum += (STR_DELIMITER + concat_list[t])
    else:
        bl_text = _unit_value_text(userDataSelection, bl_sum)
        if bl_text:
            bl_sum = bl_text

    bbox = rs.BoundingBox(objs)
    point = Rhino.Geometry.Line(bbox[0], bbox[6]).PointAt(0.5)
    textDot = rs.AddTextDot(bl_sum, point)
    rs.TextDotFont(textDot, BL_FONT)
    rs.TextDotHeight(textDot, BL_TEXTDOT_HEIGHT)
    rs.SetUserText(textDot, BL_TEMP,True)
    rs.AddObjectToGroup(textDot, groupName)
    #block implementation
    rs.AddObjectsToGroup(block_bbxs, groupName)

    create_bl_layer(BL_LAYER)

    rs.ObjectColor(textDot, BL_GROUP_DOT_COLOR)
    rs.ObjectLayer(textDot,BL_LAYER)

    rs.EnableRedraw(True)
    print ("HdM-BL: BIM Light sum calculated")
    return


def VisualizeUserDataByGrouping(chose_color = False, objects = False, show_grouping_value = False):
    """
    First parameter: Grouping
    Second parameter: Data to visualize
    """

    """
    Visualizes User Data sum for BIM LIGHT
    """
    wipe_layer(BL_LAYER_GEO)
    #user object selection
    if objects == False:
        objs_raw = user_object_selection()
        if not objs_raw:
            return
    else:
        objs_raw = objects
    objs = []
    print ("HdM-BL: TextDots are not considered")


    for obj in objs_raw:
        if rs.GetUserText(obj, BL_TEMP) != "True":
            objs.append(obj)

    rs.EnableRedraw(False)

    validKeys = []

    objUserDatas = get_data_for_objs(objs)

    for data in objUserDatas:
        for key in data:
            if key not in validKeys and BL_TEMP not in key and BL_INFO not in key:
                validKeys.append(key)

    #GROUPING SELECTION
    if len(validKeys) == 0:
        rs.MessageBox("No information to visualize. \nApply UserText information first.", 0, "HdM BIM LIGHT")
        return


    if show_grouping_value:
        gr_userDataSelection = show_grouping_value
        userDataSelection = show_grouping_value
    else:
        #sorting single keys
        validKeys = sorted(validKeys)
        gr_userDataSelection = rs.ListBox(validKeys,
        "You have selected %i objects. \nWhich Group do you want to visualize?" %len(objs), "HdM BIM LIGHT", BL_NONE)
        if gr_userDataSelection == None:
            return

        #DATA SELECTION
        userDataSelection = rs.ListBox(validKeys,
        "You have selected %i objects. \nWhich information do you want to visualize for the group?" %len(objs), "HdM BIM LIGHT", BL_NONE)
        if userDataSelection == None:
            return

    objs_groups = {}
    chosen_data = []
    unique_data = []

    for i in range(len(objs)):
            if gr_userDataSelection in objUserDatas[i]:
                val = objUserDatas[i][gr_userDataSelection]
                chosen_data.append(val)
                if val not in unique_data:
                    unique_data.append(val)
            else:
                chosen_data.append(None)

    for i in range(len(objs)):
        if chosen_data[i] and chosen_data[i] != VALUE_ERROR:
            if chosen_data[i] in objs_groups:
                objs_groups[chosen_data[i]].append(objs[i])
            else:
                objs_groups[chosen_data[i]] = [objs[i]]
        else:
            continue

    # color

    if chose_color == True:
        color1 = rs.GetColor(STANDARD_COLOR_1)
        if color1 == None:
            return
        color2 = rs.GetColor(STANDARD_COLOR_2)
        if color2 == None:
            return
    else:
        color1 = STANDARD_COLOR_1
        color2 = STANDARD_COLOR_2

    relColorDictonary = _value_color_range(unique_data, color1, color2)

    # create groups
    rs.EnableRedraw(False)
    for group in objs_groups:
        _visualize_data_for_objs(objs_groups[group], gr_userDataSelection, userDataSelection, relColorDictonary[group])
    rs.EnableRedraw(True)


##------------------ PRIVATE FUNCTIONS

def _visualize_data_for_objs(objs, group_user_data_selection, userDataSelection, color):
    chosenData = []
    uniqueData = []
    objUserDatas = get_data_for_objs(objs)
    for i in range(len(objs)):
        if userDataSelection in objUserDatas[i]:
            val = objUserDatas[i][userDataSelection]
            chosenData.append(val)
            if val not in uniqueData:
                uniqueData.append(val)
        else:
            chosenData.append(None)

    #RESET OLD VALUES
    _reset_visualization(objs)

    #get group count to avoid duplicat group names
    currentGroupCount = _get_bl_group_count()

    for i in range(len(objs)):

        _set_bl_info_original_color(objs[i])
        set_bl_key_info (objs[i], userDataSelection)
        _set_bl_grouping_key_info (objs[i], group_user_data_selection)

        if chosenData[i] == None or chosenData[i] == VALUE_ERROR:
            #print ("HdM BIM Light: Problem")
            rs.SelectObject(objs[i])
            rs.ObjectColor(objs[i], NOT_DEFINED_COLOR)
            chosen_color = NOT_DEFINED_COLOR
        else:
            saved_color = _apply_bl_grouping_color(objs[i], group_user_data_selection)
            if not saved_color:
                rs.ObjectColor(objs[i], color)
                chosen_color = color
            else:
                chosen_color = saved_color

    groupName = BL_PREFIX + DELIMITER + str(currentGroupCount + i + 1)
    rs.AddGroup(groupName)
    rs.AddObjectsToGroup(objs, groupName)
    # value calc
    bl_sum = 0
    flag = 0
    flag_concat = 0
    concat_list = []
    for obj in objs:
        value = rs.GetUserText(obj, userDataSelection)
        value = parse_user_text_function_value(value, obj)
        if not value:
            flag_concat = 1
            if VALUE_ERROR in concat_list:
                continue
            else:
                concat_list.append(VALUE_ERROR)
            continue
        else:
            if is_float(value):
                if str(value) not in concat_list:
                    concat_list.append(str(value))
            else:
                if value not in concat_list:
                    concat_list.append(value)
                flag_concat = 1
                continue
            flag = 1
            bl_sum += float(value)
    if flag == 0:
        print ("BL: No numbers to sum up")
    if flag_concat == 1:
        bl_sum = ""
        for t in range(len(concat_list)):
            if t == 0:
                bl_sum = concat_list[t]
            else:
                bl_sum += (STR_DELIMITER + concat_list[t])
    else:
        bl_text = _unit_value_text(userDataSelection, bl_sum)
        if bl_text:
            bl_sum = bl_text

    ### get grouping value
    grouping_value = _get_bl_grouping_key_value(objs[0])
    bl_sum = grouping_value + ": " + str(bl_sum)

    bbox = rs.BoundingBox(objs)
    point = Rhino.Geometry.Line(bbox[0], bbox[6]).PointAt(0.5)
    textDot = rs.AddTextDot(bl_sum, point)
    rs.TextDotFont(textDot, BL_FONT)
    rs.TextDotHeight(textDot, BL_TEXTDOT_HEIGHT)
    rs.SetUserText(textDot, BL_TEMP,True)
    rs.AddObjectToGroup(textDot, groupName)

    create_bl_layer(BL_LAYER)

    #rs.ObjectColor(textDot, BL_GROUP_DOT_COLOR)
    rs.ObjectColor(textDot, chosen_color)
    rs.ObjectLayer(textDot,BL_LAYER)

    print ("HdM-BL: BIM Light sum calculated")
    return

def _visualize_user_data_by_object(objs):
    """
    Creates a Text or TextDot to visualize the information value of the chosen object
    """

    if not objs:
        return

    groupDict = {}

    flag = 0
    gr_table = create_bl_group_table()
    for obj in objs:
        relGroup = get_bl_group(obj)
        if relGroup:
            allObjs = objects_by_bl_group(relGroup, gr_table)
            notTemp = []
            for groupObj in allObjs:
                if not rs.GetUserText(obj, BL_TEMP):
                    notTemp.append(groupObj)
            if len(notTemp) == 1:
                groupDict[relGroup] = groupObj
            else:
                print ("BL: No relevant item found")
                continue
            flag = 1
        else:
            continue

    if flag == 0:
        rs.MessageBox("No information to visualize.", 0, "HdM BIM LIGHT")
        return
    rs.EnableRedraw(False)
    for groupName in groupDict:


        key = get_bl_key_info(groupDict[groupName])
        value = _get_bl_key_value(groupDict[groupName])
        if value == None:
            value = VALUE_ERROR

        bl_text = _unit_value_text(key, value)
        if bl_text:
            value = bl_text

        #define position

        bbox = rs.BoundingBox(groupDict[groupName])
        point = Rhino.Geometry.Line(bbox[0], bbox[6]).PointAt(0.5)
        textDot = rs.AddTextDot(value, point)
        rs.TextDotFont(textDot, BL_FONT)
        rs.TextDotHeight(textDot, BL_TEXTDOT_HEIGHT)
        rs.SetUserText(textDot, BL_TEMP,True)
        rs.AddObjectToGroup(textDot, groupName)
        layer = rs.AddLayer(BL_LAYER, BL_LAYER_COLOR, True)
        rs.ObjectColor(textDot, rs.ObjectColor(groupDict[groupName]))
        rs.ObjectLayer(textDot,layer)
        block_bbx = _block_bbx_color(groupDict[groupName], rs.ObjectColor(groupDict[groupName]), groupName)
    rs.EnableRedraw(True)
    return

def _reset_visualization(objs, all=False):
    """
    reset bim light groups of selected objects
    """
    flag = 0
    objsDone = []
    gr_table = create_bl_group_table()
    for obj in objs:
        if obj in objsDone:
            continue
        relGroup = get_bl_group(obj)
        if relGroup:
            allObjs = objects_by_bl_group(relGroup, gr_table)
            flag = 1
            objsDone += allObjs
        else:
            continue
        nonTempObjs = []
        for blObj in allObjs:
            if rs.GetUserText(blObj, BL_TEMP) == "True":
                rs.DeleteObject(blObj)
            else:
                nonTempObjs.append(blObj)
        for nonTempObj in nonTempObjs:
            rs.RemoveObjectFromGroup(nonTempObj, relGroup)
            _reset_bl_info_original_color(nonTempObj)
            _remove_bl_key_info(nonTempObj)
            _remove_bl_grouping_key_info(nonTempObj)
        delete = rs.DeleteGroup(relGroup)
        if delete == False:
            for nonTempObj in nonTempObjs:
                groups = rs.ObjectGroups(nonTempObj)
                if len(groups) > 1:
                    rs.MessageBox("ERROR: Please check for «bl» groups in «SelGroups» and «Ungroup» them.", 0, "HdM BIM LIGHT")
                else:
                    rs.RemoveObjectFromAllGroups(nonTempObj)
    if all == True:
        _clear_bl_groups()
        wipe_layer(BL_LAYER)
        print ("HdM-BL: Groups cleaned")
    # wipe BL_TEMP
    wipe_layer(BL_LAYER_GEO)
    print ("HdM-BL: Layers wiped")
    if not flag == 1:
        print ("HdM-BL: No BL Groups to reset")
    else:
        print ("HdM-BL: Vizualization reset")
    return True

def _clear_bl_groups():
    """
    deletes all bl groups from table
    """
    group_names = get_bl_groups()
    for group in group_names:
        rs.DeleteGroup(group)
    return True

def _remove_bl_key_info(obj):

    """

    sets the bl_info user text to identify the data that is shown

    """

    rs.SetUserText(obj, KEY_KEY)

    return True

def _set_bl_grouping_key_info(obj, value):
    """
    sets the bl_info user text to identify the data that is shown
    """
    rs.SetUserText(obj, KEY_GROUP_KEY, value)
    return True

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

def _apply_bl_grouping_color(obj, grouping_key):

    """

    applies the bl grouping color to an object

    """



    color_tuple = _get_bl_grouping_color(obj, grouping_key)



    if color_tuple:

        rs.ObjectColor(obj, color_tuple)

        return color_tuple

    else:

        return None

def _remove_bl_grouping_key_info(obj):

    """

    sets the bl_info user text to identify the data that is shown

    """

    rs.SetUserText(obj, KEY_GROUP_KEY)

    return True

def _get_bl_key_value(obj):
    """
    gets BIM LIGHT visualization value
    """
    key = get_bl_key_info(obj)
    if not key:
        print ("BL: Error: Object does not have the requested key")
        return "NoKey"
    else:
        uT = rs.GetUserText(obj, key)
        uT = parse_user_text_function_value(uT, obj)
    if uT == None:
        return None
    else:
        return uT

def _get_bl_grouping_key_value(obj):
    """
    gets BIM LIGHT visualization value
    """
    key = get_bl_grouping_key_info(obj)
    if not key:
        print ("BL: Error: Object does not have the requested key")
        return "NoKey"
    else:
        uT = rs.GetUserText(obj, key)
        uT = parse_user_text_function_value(uT, obj)
    if uT == None:
        return None
    else:
        return uT

def _get_bl_group_count():
    """
    gets the number of existing BIM LIGHT groups
    """

    allGroups = rs.GroupNames()
    blGroupCount = 0
    if allGroups:
        for gr in allGroups:
            split_gr = gr.split(DELIMITER)
            if split_gr[0] == BL_PREFIX:
                if int(split_gr[1]) > blGroupCount:
                    blGroupCount = int(split_gr[1])

    blGroupCount += 1
    return blGroupCount

def _value_color_range(values, color1 = STANDARD_COLOR_1, color2 = STANDARD_COLOR_2):
    colorDict = {}

    if len(values) == 0:
        return colorDict
    if len(values) == 1:
        colorDict[values[0]] = color1
        return colorDict

    valFloats = []
    for val in values:
        try:
            valFloat = float(val)
            valFloats.append(valFloat)
        except:
            valFloats = None

    colorLine = Rhino.Geometry.Line(
                            Rhino.Geometry.Point3d(color1[0], color1[1], color1[2]),
                            Rhino.Geometry.Point3d(color2[0], color2[1], color2[2])).ToNurbsCurve()

    #Rhino 7 fix
    final_param_list = []

    if valFloats:
        #sort values with floats
        valFloatsSorted, valuesSorted = zip(*sorted(zip(valFloats, values)))
        differenceFloat = valFloatsSorted [-1] - valFloatsSorted[0]
        final_param_list = []
        for val in valFloatsSorted:
            if differenceFloat == 0:
                final_param_list.append(0)
                continue
            param = 1 / differenceFloat * (val - valFloatsSorted[0])
            final_param_list.append(param)

    else:

        #Rhino 7 fix
        final_param_list = []
        valuesSorted = sorted(values)
        paramsOnLine = colorLine.DivideByCount(len(valuesSorted)-1, True)
        for param in paramsOnLine:
            final_param_list.append(param/paramsOnLine[-1])


    for i in range(len(final_param_list)):
        relPoint = colorLine.PointAtNormalizedLength(final_param_list[i])
        colorDict[valuesSorted[i]] = (
                                int(round(relPoint[0])),
                                int(round(relPoint[1])),
                                int(round(relPoint[2]))
                                )

    return colorDict

def _set_bl_info_original_color(obj):
    """
    sets UserText for BIM LIGHT usage only - saves the initial color of the object
    """

    colorSource = str(rs.ObjectColorSource(obj))
    colorValue = rs.ObjectColor(obj)
    colorValue = str(colorValue.R) + DELIMITER + str(colorValue.G) + DELIMITER + str(colorValue.B)
    rs.SetUserText(obj, KEY_SOURCE, colorSource)
    rs.SetUserText(obj, KEY_COLOR, colorValue)
    #HdM-BL: Original color saved

    return

def _reset_bl_info_original_color(obj):
    """
    resets the original color of a BIM LIGHT object
    """
    valueSource = rs.GetUserText(obj, KEY_SOURCE)
    valueColor = rs.GetUserText(obj, KEY_COLOR)
    if valueColor:
        try:
            rs.ObjectColor(obj, color_str_to_tuple(valueColor))
        except:
            print ("HdM-BL: Color value probably has wrong format")
    if valueSource:
        rs.ObjectColorSource (obj, int(valueSource))
    rs.SetUserText(obj, KEY_SOURCE)
    rs.SetUserText(obj, KEY_COLOR)
    #HdM-BL: Color reset

    return

def _block_bbx_color(possible_block_id, color, group=False):
    """
    creates a bounding box around the block in direction of its plane
    colors the bbx
    sets temp status
    """

    if rs.ObjectType(possible_block_id) == 4096:
        block_id = possible_block_id
        trans = rs.BlockInstanceXform(block_id)
        rel_plane = rs.PlaneTransform(rs.WorldXYPlane(), trans)
        bbx = rs.BoundingBox(block_id, rel_plane)
        bbx_std = []
        if abs((bbx[0] - bbx[4]).Length) <= rs.UnitAbsoluteTolerance():
            for t in range(8):
                if t > 3:
                    bbx_std.append(Rhino.Geometry.Point3d(bbx[t].X, bbx[t].Y, bbx[t-4].Z + BBX_STD_HEIGHT))
                else:
                    bbx_std.append(bbx[t])
            bbx = bbx_std

        if abs((bbx[0] - bbx[1]).Length) <= rs.UnitAbsoluteTolerance() or abs((bbx[0] - bbx[3]).Length) <= rs.UnitAbsoluteTolerance():
            print (MSG_PREFIX + "Block has no footprint")
            return None
        bbx_id = rs.AddBox(bbx)

        #scale by BBX_SCALE_FACTOR
        mid_point = Rhino.Geometry.Line(bbx[0], bbx[6]).PointAt(0.5)
        rs.ScaleObject(bbx_id, mid_point, BBX_SCALE_FACTOR)

        rs.ObjectColor(bbx_id, color)
        rs.SetUserText(bbx_id, BL_TEMP,True)

        layer = rs.AddLayer(BL_LAYER, BL_LAYER_COLOR, True)
        rs.ObjectLayer(bbx_id,layer)
        if group:
            rs.AddObjectToGroup(bbx_id, group)

        return bbx_id
    else:
        return None

def _unit_value_text(user_param, value_to_show):
    """add unit for value when known"""
    if is_float(value_to_show) == True:
        value_to_show = float(value_to_show)
    else:
        return False
    if user_param[-3:] == BL_SUFFIX:
        # get display unit from document text
        unit_word = rs.GetDocumentUserText(DOC_KEY_DISPLAY_UNIT)
        # get abbreviation from dict
        unit = DISPLAY_LOOKUP_TABLE.get(unit_word)
        if not type(unit) == str:
            unit_word = rs.UnitSystemName(capitalize = True, singular = False)
            unit = " " + rs.UnitSystemName(abbreviate = True)

    else:
        return False

    round_dig = ROUNDING_LOOKUP_TABLE.get(unit_word)

    #check for round digit overwrite
    round_dig_overwrite = get_round_dig_overwrite()
    if round_dig_overwrite != None:
        round_dig = round_dig_overwrite

    if unit == "":
        rel_unit = ""
    for param in BL_MASSES:
        if user_param == param[0]:
            if param[1] == 1:
                rel_unit = unit
            if param[1] == 2:
                rel_unit = unit + "²"
            if param[1] == 3:
                rel_unit = unit + "³"


    if round_dig == 0:
        final_text = str(int(round(value_to_show))) + rel_unit
    else:
        final_text = str(format(value_to_show, '.%sf' %round_dig)) + rel_unit

    return final_text