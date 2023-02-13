# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Export

    Created on 29. June 2022 by j.hoell, y.schindel

'''

##------------------ IMPORTS
import rhinoscriptsyntax as rs
from datetime import datetime
import time
import os
import json
import utilsbl
from variablesbl import *
from utilsbl import *
from hdmrhino import CSV # Change this
##------------------ CLASSES




class Export_Object:
    # this class is used to hold and maipulate export data.

    # these headers will always appear in the given order
    HEADER_CONTENT_FIXED = ["guid", "date_time", "name", 
                            "block_name", "color", "groups", 
                            "bim_light_group", "layer", "unified_area"]
    BLOCK_NAME_HEADER = HEADER_CONTENT_FIXED[2]


    def __init__(self, guid, date_time, hierarchies):
        # attribute names must match with header content above
        self.guid = guid
        self.date_time = str(date_time)
        self.name = ""
        self.block_name = ""
        self.color = ""
        self.layer = ""
        self.groups = ""
        self.bim_light_group = ""
        self.unified_area = ""
        # since we don't know how many sublayers we have to deal with 
        # we need to iterate over a previously created list of leayer hierarchies
        # that is passes into the class upon instance creation
        for hier in hierarchies:
            self.__dict__[hier] = ""

    # ---------------------------------------------------------------------
    # the following functions will be called when creating the output line, if demanded by user

    def _get_name(self):
        self.name = rs.ObjectName(self.guid)
        if not self.name:
            self.name = ""

    def _get_block_name(self):
        if rs.ObjectType(self.guid) == 4096:
            self.block_name = rs.BlockInstanceName(self.guid)
        else:
            self.block_name = ""

    def _get_color(self):
        self.color = str(rs.ObjectColor(self.guid))

    def _get_layer(self):
        self.layer = rs.ObjectLayer(self.guid)

    def _get_group(self):
        # groups (/ delimited)
        self.group = _get_groups_str(self.guid)

    def _get_group_bl(self):
        self.bim_light_group = get_bl_group(self.guid)
        if not self.bim_light_group:
            self.bim_light_group = ""

    def _split_layer(self, user_selection):
        # splits the layer string of the current object into parts representing nested layers
        # and enumerate by hierachy level
        self._get_layer()
        layer_split = self.layer.split("::")
        for param_name in user_selection:
            if LAYER_HIER_PREFIX in param_name:
                t = 0
                for letter in param_name.split():
                    try:
                        t = int(letter)
                    except ValueError:
                        pass
                if len(layer_split) < t:
                    pass
                else:
                    print('name, layersplit', param_name, layer_split[t-1])
                    setattr(self, param_name, layer_split[t-1])

    def _unify_areas(self, user_selection):
        # if multiple area parameters are found for one object, 
        # an error message is written into the csv field
        area_params = 0
        for param_name in user_selection:
            if "AREA" in param_name:
                value = getattr(self, param_name, "")
                if len(value) > 1:
                    area_params += 1
                    if area_params == 1:
                        self.unified_area = value
                    else:
                        self.unified_area = "Multiple Area Parameters found"
        if area_params == 0:
            self.unified_area = "No data"
        if area_params > 1:
            rs.SelectObject(self.guid)
            print("{}: Multiple AREA parameters found.".format(self.guid))
            self.unified_area = "Multiple area values"
            return self.guid
        else:
            return None

    # ---------------------------------------------------------------------

    def _output_data(self, user_input, user_selection):
        # this function returns an output line containing the user specified data fields
        if user_input.get("name") == True:
            self._get_name()
        if user_input.get("block_name") == True:
            self._get_block_name()
        if user_input.get("color") == True:
            self._get_color()
        if user_input.get("layer") == True:
            self._get_layer()
        if user_input.get("groups") == True:
            self._get_group()
        if user_input.get("bim_light_group") == True:
            self._get_group_bl()
        output = []
        for selection in user_selection:
            output.append(getattr(self, selection, ""))
        data_line = STR_DELIMITER.join(output)
        return data_line

    def _to_dict(self, user_input, user_selection):

        if user_input.get("name") == True:
            self._get_name()
        if user_input.get("block_name") == True:
            self._get_block_name()
        if user_input.get("color") == True:
            self._get_color()
        if user_input.get("layer") == True:
            self._get_layer()
        if user_input.get("groups") == True:
            self._get_group()
        if user_input.get("bim_light_group") == True:
            self._get_group_bl()
        
        output = {}
        for selection in user_selection:
            output[selection] = getattr(self, selection, "")

        return output

##------------------ PUBLIC FUNCITONS


def ExportUserData(file_name=None, 
                    qs = False, 
                    file_path = None, 
                    append_existing_file = False, 
                    open_export_file = True,
                    get_user_input = True,
                    no_hierarchy = False,
                    max_hierarchy = False,
                    power_bi = False):
    """
    Exports userdata from selected elements to CSV.

    Args:
        file_name (bool, optional): The file name.
        qs (bool, optional): Run quality check. Defaults to False.
        file_path (string, optional): The full file path for the export CSV. Defaults to False.
        append_existing_file (bool, optional): Append to existing file (True) or override existing file (False). Defaults to False.
        open_export_file (bool, optional): Open the exported file. Defaults to True.
        get_user_input (bool, optional): Prompt user with checkbox to select parameters for the export. Defaults to True.
        no_hierarchy (bool, optional): Exclude layer hierarchy from export. Defaults to False.
        max_hierarchy (bool, optional): Override user selection to include all hierarchy. Defaults to False.
        power_bi (bool, optional): Error handling for missing or duplicate area parameters. Defaults to False.

    Returns:
        bool: Use for error handling.
    """
    if not file_name:
        file_name = FILE_NAME

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = time.time()

    if not file_path:
        file_path = os.path.join(EXPORT_PATH, (now_file + '_' + file_name + '.csv'))

    objs = utilsbl.user_object_selection(True)
    if not objs:
        return False
    if qs == True:
        if _quality_check(objs) == False:
            return

    if not max_hierarchy:
    # get layer header names from document
        layer_headers = _get_layer_hierarchy_headers()
        
    if max_hierarchy:
    # get layer header names from selection
        layer_headers = _get_layer_hierarchy_headers(objs)
        if len(layer_headers) < 2:
            rs.MessageBox("The chosen template requires at least a parent layer and one sub-layer per option.")
            return False
        else:
            out_of_range_layers = []
            for layer in layer_headers:
                # remove layer hierarchy if it is bigger than max_hierarchy
                hierachy_num = [int(s) for s in layer.split() if s.isdigit()][0]
                if hierachy_num > max_hierarchy:
                    out_of_range_layers.append(layer)
            # remove out of range layers from layer_headers set.
            # this needs to be a seperate loop because afaik you cannot change a while iterating over it
            for layer in out_of_range_layers:
                layer_headers.remove(layer)
    
    layer_headers_list = sorted(list(layer_headers), key=lambda s: s.lower())

    # create class objects "Export_Object" as data_objs
    Data_Objs = []
    for obj in objs:
        Data_Object = Export_Object(str(obj), now, layer_headers)
        Data_Objs.append(Data_Object)

    # set usertext and get key headers
    key_headers = _set_usertext_for_export_object(Data_Objs)

    if len(Data_Objs) != len(objs):
        print ("HdM-BL: Data does not match. Contact DT.")

    #filter bl_info and bl_temp from keys
    valid_keys = set()
    for key in key_headers:
        if BL_TEMP not in key and BL_INFO not in key:
            valid_keys.add(key)
    if len(valid_keys) > 0:
        #sorting single keys
        valid_keys = sorted(list(valid_keys), key=lambda s: s.lower())
    else:
        valid_keys = []

    # final list of attributes
    if no_hierarchy == True:
        # eliminate all layer hierarchy from the process
        all_keys = Export_Object.HEADER_CONTENT_FIXED + valid_keys
    if no_hierarchy == False:
        # use layer hierarchy
        all_keys = Export_Object.HEADER_CONTENT_FIXED + layer_headers_list + valid_keys

    default_bools = []
    for key in all_keys:
        default_bools.append(True)

    # get time measurment before interface
    total_time_before_UI = time.time() - start_time

    pre_selection = False
    # try to load the pre selection dictionary from document text
    try:
        pre_selection = json.loads(rs.GetDocumentUserText(BL_CHECKBOX_DATA))
    except:
        pass

    checkbox_data = zip(all_keys, default_bools)

    # if pre selection was loaded use true false values as default for CheckListBox
    if pre_selection:
        for count, sub_list in enumerate(checkbox_data):
            if sub_list[0] in pre_selection:
                sub_list = (sub_list[0], pre_selection.get(sub_list[0]))
                checkbox_data[count] = sub_list

    # convert pre selection dictionary to list and prepare alias dictionary
    export_alias = {}
    for sub_list in checkbox_data:
        key = sub_list[0]
        export_alias[key] = key

    # try to load export alias dictionary from document user text
    alias_dict = False
    try:
        alias_dict = json.loads(rs.GetDocumentUserText(BL_EXPORT_ALIAS))
    except:
        pass

    # if aliases where loaded append potential new parameter to alias dictionary
    if alias_dict:
        for key, value in export_alias.items():
            if not key in alias_dict:
                alias_dict[key] = key
        export_alias = alias_dict

    rs.SetDocumentUserText(BL_EXPORT_ALIAS, json.dumps(export_alias, ensure_ascii=False))

    if get_user_input:
        # promt user to select export parameters from checkbox
        user_input = rs.CheckListBox(checkbox_data, title = "Select export data")
        if not user_input:
            return False
        else:
            result =_correct_export_parameters(user_input, no_hierarchy=no_hierarchy, max_hierarchy=max_hierarchy)
            user_input = result[0]
            user_selection = result[1]
            rs.SetDocumentUserText(BL_CHECKBOX_DATA, json.dumps(user_input, ensure_ascii=False))
    else:
        # do not prompt user
        result =_correct_export_parameters(checkbox_data, no_hierarchy=no_hierarchy, max_hierarchy=max_hierarchy)
        user_input = result[0]
        user_selection = result[1]

    # join the list of user selected parameters into one delimited sting
    colum_names = user_selection
    # get time measurment after interface
    start_time_after_UI = time.time()

    if power_bi == True and not any('AREA' in name for name in colum_names):
        rs.MessageBox("No Area parameters found, cannot start PowerBI.", 0, BOX_HEADER)
        return False

    if not append_existing_file:
        # override if file existst or creat new file
        multi_area_guids = []

        #redraw for error selection _unify_areas
        rs.EnableRedraw(False)

        for obj in Data_Objs:
            if "unified_area" in colum_names:
                multi_area_guid = obj._unify_areas(user_selection)
                if multi_area_guid:
                    multi_area_guids.append(multi_area_guid)

        #redraw for error selection in _unify_areas
        rs.EnableRedraw(True)
        if len(multi_area_guids) > 0:
            print ("HdM-BL: Multiple area parameter values found. Affected objects selected.")
        if len(multi_area_guids) > 0 and power_bi == True:
            rs.MessageBox("Cannot start PowerBI, Multiple area parameters found on selected objects. Delete one of the Parameters and try again.", 0, BOX_HEADER)
            return False
        else:
            data = []
            for obj in Data_Objs:
                obj._split_layer(user_selection)
                data.append(obj._to_dict(user_input, user_selection))
            file_path = CSV.export(
                            data=data,
                            file_path=file_path,
                            headers=colum_names,
                            append=False
                            )
            print("Data written to: {}".format(file_path))

    elif append_existing_file:
        multi_area_guids = []
        #redraw for error selection _unify_areas
        rs.EnableRedraw(False)
        for obj in Data_Objs:
            if "unified_area" in colum_names:
                multi_area_guid = obj._unify_areas(user_selection)
                if multi_area_guid:
                    multi_area_guids.append(multi_area_guid)

        #redraw for error selection in _unify_areas
        rs.EnableRedraw(True)

        if len(multi_area_guids) > 0:
            rs.MessageBox("Cannot start PowerBI. Multiple area parameters found on selected objects. Delete one of the Parameters and try again.", 0, BOX_HEADER)
            return False
        else:
            data = []
            for obj in Data_Objs:
                if LAYER_HIER_PREFIX in colum_names:
                    obj._split_layer(user_selection)
                data.append(obj._to_dict(user_input, user_selection))

            file_path = CSV.export(
                            data=data,
                            file_path=file_path,
                            headers=colum_names,
                            append=True
                            )
            print ("Data written to: {}".format(file_path))

    else:
        # catch invalid input
        rs.MessageBox(("No valid csv file creation method found, contact DT"), 0, BOX_HEADER)
        return

    # time measurment
    total_time_after_UI = time.time() - start_time_after_UI
    total_time =total_time_before_UI + total_time_after_UI
    print("Exported {amount} objects in {x} seconds."\
    .format(amount = len(objs), x = total_time))

    
    if open_export_file == True:
        rs.MessageBox(("Data written to: {}".format(file_path)), 0, BOX_HEADER)
        os.startfile(file_path)
    elif open_export_file == False:
        pass
    else:
        return

    return


##------------------ PRIVATE FUNCITONS

def _correct_export_parameters(user_input, no_hierarchy = False, max_hierarchy = False):
    # run multiple corrections on the parameters which should be exported
    user_selection = []

    for t in range(len(user_input)):
        # override user selection to always export these parameters
        if user_input[t][0] == 'guid':
            user_input[t] = ("guid", True)
        if user_input[t][0] == 'date_time':
            user_input[t] = ("date_time", True)
        if user_input[t][0] == 'unified_area':
            user_input[t] = ("unified_area", True)
        if no_hierarchy:
            # override user selection to include layer
            if user_input[t][0] == 'layer':
                user_input[t] = ("layer", True)
        if max_hierarchy:
            # override user selection to include all hierarchy
            if 'hierarchy' in user_input[t][0].lower():
                user_input[t] = (user_input[t][0], True)
        # for the rest of the selection use the actual user input
        if user_input[t][1] == True:
            user_selection.append(user_input[t][0])

    user_input = dict(user_input)

    return user_input, user_selection

def _get_layer_hierarchy_headers(objs=False):
    """gets all keys for the objects and returns a class with all information"""

    # create list of layer hierarchies
    if not objs:
        layers = rs.LayerNames()
    if objs:
        layers = set()
        for obj in objs:
            layers.add(rs.ObjectLayer(obj))

    layer_hier_count = 0
    layers_hierarchies = set()
    for layer in layers:
        count = len(layer.split("::"))
        if count > layer_hier_count:
            layer_hier_count = count
            for i in range(layer_hier_count):
                layers_hierarchies.add(LAYER_HIER_PREFIX + str(i+1))

    return layers_hierarchies

def _set_usertext_for_export_object(export_objects):
    '''
    sets the keys for objects and returns the list
    returns set of keys
    '''
    key_headers = set()

    for obj in export_objects:
        keys = rs.GetUserText(obj.guid)

        for key in keys:
            value = rs.GetUserText(obj.guid, key)
            value = parse_user_text_function_value(value, obj.guid)
            key_headers.add(key)
            setattr(obj, key, value)

    return key_headers

def _quality_check(objs):
    """checks the quality of the model and mass parameters"""

    import time
    start_time = time.time()

    err_msg = ""
    #dup check
    err_flag = 0
    for i in range(len(objs)):
        for t in range(len(objs)):
            if i != t:
                check = rs.CompareGeometry(objs[i], objs[t])
                if check == True:
                    err_flag = 1
    if err_flag == 1:
        err_msg1 = "BIM Light Error: Duplicates found. Please check."
        print (err_msg1)
    BL_MASSES = [BL_AREA_SRF, BL_AREA_LOW_SRF, BL_AREA_VOLUME]
    #param check

    err_calc_flag = [0, 0, 0]
    err_msg2 = "BIM Light Error in srf area, please recalculate."
    err_msg3 = "BIM Light Error in brep area, please recalculate."
    err_msg4 = "BIM Light Error brep volume, please recalculate."

    rs.EnableRedraw(False)

    for obj in objs:
        testValue1 = None
        testValue2 = None
        testValue3 = None
        if BL_MASSES[0][0] in rs.GetUserText(obj):
            testValue1 = str(_calculate_area_srf(obj))
            if testValue1 == "None":
                testValue1 = VALUE_ERROR
            if testValue1 != rs.GetUserText(obj, BL_MASSES[0][0]):
                print (err_msg2)
                rs.SelectObject(obj)
                err_calc_flag[0] = 1
        if BL_MASSES[1][0] in rs.GetUserText(obj):
            testValue2 = str(_calculate_area_brep(obj))
            if testValue2 == "None":
                testValue2 = VALUE_ERROR
            if testValue2 != rs.GetUserText(obj, BL_MASSES[1][0]):
                print (testValue2)
                print (rs.GetUserText(obj, BL_MASSES[1][0]))
                rs.SelectObject(obj)
                err_calc_flag[1] = 1
        if BL_MASSES[2][0] in rs.GetUserText(obj):
            testValue3 = str(_calculate_volume_brep(obj))
            if testValue3 == "None":
                testValue3 = VALUE_ERROR
            if testValue3 !=  rs.GetUserText(obj, BL_MASSES[2][0]):
                print (err_msg4)
                rs.SelectObject(obj)
                err_calc_flag[2] = 1

    rs.EnableRedraw(True)

    if err_flag == 1:
        err_msg += err_msg1 + "\n"
    if err_calc_flag[0] == 1:
        err_msg += err_msg2 + "\n"
    if err_calc_flag[1] == 1:
        err_msg += err_msg3 + "\n"
    if err_calc_flag[2] == 1:
        err_msg += err_msg4 + "\n"

    check_amount = len(objs)
    check_time = time.time() - start_time
    ratio = check_time / check_amount
    print("{objs} objects checked in {x} seconds. Time per Objects was {y}"\
        .format(objs = check_amount, x = check_time, y = ratio))

    if err_msg == "":
        rs.MessageBox("Mass calculations OK. (Converted data not checked)", 0, "HdM BIM Light")
        return True

    else:
        err_msg += "Do you want to export anyway?"
        answer = rs.MessageBox(err_msg,4,"HdM BIM Light")
    if answer == 6:
        return True
    else:
        return False

def _get_groups_str(obj):
    """gets the group of an object"""
    groups = rs.ObjectGroups(obj)
    group_str = ""
    if len(groups) > 1:
        for i in range(len(groups)):
            if i == 0:
                group_str += groups[i]
            else:
                group_str += (GRP_DELIMITER + groups[i])
        return group_str
    elif len(groups) == 0:
        return group_str
    else:
        return groups[0]

