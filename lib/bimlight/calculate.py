# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Calculate

    Created on 29. June 2022 by j.hoell, y.schindel

'''

##------------------ IMPORTS
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import rhyton
from variablesbl import *
from utilsbl import *


def createObjectInformation():
    bottom, surface, volume = 'Bottom Face Area', 'Surface Area', 'Volume'
    res = rhyton.SelectionWindow.show(
            [bottom, surface, volume],
            "Choose Calculation:")
    if not res:
        return

    if res == bottom:
        _bottomFaceArea()
    elif res == surface:
        _surfaceArea()
    elif res == volume:
        _volume()


def _bottomFaceArea():
    breps = rhyton.GetBreps()
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    for brep in breps:
        if not rs.ObjectType(brep) == 8:
            surfaces = rs.ExplodePolysurfaces(brep)
            minimaZ = [rs.SurfaceAreaCentroid(srf)[1][2] for srf in surfaces]
            surface = surfaces[minimaZ.index(min(minimaZ))]
            area = rs.SurfaceArea(surface)[0]
            rs.DeleteObjects(surfaces)
        else:
            area = rs.SurfaceArea(brep)[0]

        info = dict()
        info['guid'] = brep
        info['bottom face area'] = area
        data.append(info)
    
    rhyton.ElementUserText.apply(data)
    rs.EnableRedraw(True)

def _surfaceArea():
    breps = rhyton.GetBreps()
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    for brep in breps:
        info = dict()
        info['guid'] = brep
        info['surface area'] = rs.SurfaceArea(brep)[0]
        data.append(info)

    rhyton.ElementUserText.apply(data)
    rs.EnableRedraw(True)

def _volume():
    breps = rhyton.GetBreps()
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    for brep in breps:
        info = dict()
        info['guid'] = brep
        info['volume'] = rs.SurfaceVolume(brep)[0]
        data.append(info)

    rhyton.ElementUserText.apply(data)
    rs.EnableRedraw(True)


















































##-------------------- PUBLIC FUNCTIONS

# def CreateObjectInformation(geometry = False):
#     """
#     Creates Parameters from geometery
#     """

#     wipe_layer(BL_LAYER_GEO)

#     mass_calc_methods = []
#     unit_factors = []
#     for entry in BL_MASSES:
#         mass_calc_methods.append(entry[2])
#         unit_factors.append(entry[1])

#     mass_calc_vars = BL_MASSES#bl mass calculation variables


#     user_method_selection = rs.ListBox(mass_calc_methods,
#     "Which information do you want to create?", "HdM BIM LIGHT")
#     if user_method_selection == None:
#         return

#     #wipe creat bl layer srf for temp info

#     create_bl_layer(BL_LAYER_GEO)
#     t = None
#     if user_method_selection == mass_calc_methods[0]:
#         t = 0
#     if user_method_selection == mass_calc_methods[1]:
#         t = 1
#     if user_method_selection == mass_calc_methods[2]:
#         t = 2
#     if t == None:
#         return

#     objs = user_object_selection()

#     if not objs:
#         return

#     # get conversion unit_factor
#     conversion_factor = get_unit_conversion_factor()

#     rs.EnableRedraw(False)
#     for count, obj in enumerate(objs):
#         if (scriptcontext.escape_test(False)):
#             print ("BIM Light: Task cancelled.")
#             return
#         print ("BIM Light: Calculating %d / %d (ESC to cancel)" %(count + 1, len(objs)))

#         if t == 0:
#             calc_mass = _calculate_area_srf(obj, geometry)
#         if t == 1:
#             calc_mass = _calculate_area_brep(obj, geometry)
#         if t == 2:
#             calc_mass = _calculate_volume_brep(obj, geometry)

#         if calc_mass:
#             # this can always calculate, since "no conversion" is
#             # CONVERSION_LOOKUP_TABLE.key("None") which is 1.
#             # 1^x is always 1 so this is safe.
#             calc_mass = calc_mass * (conversion_factor ** unit_factors[t])
#             rs.SetUserText(obj, mass_calc_vars[t][0], calc_mass)
#         else: rs.SetUserText(obj, mass_calc_vars[t][0], VALUE_ERROR)

#     rs.EnableRedraw(True)
#     return

##-------------------- PUBLIC LEVEL FUNCTIONS

class Level_Data:
    # this is class for all csv level information

    ABOVE_GROUND_ENG = "Level"
    ABOVE_GROUND_GER = "OG"
    GROUND_FLOOR_GER = "EG"
    BELOW_GROUND_ENG = "Basement"
    BELOW_GROUND_GER = "UG"

    def __init__(self, guid, elevation):
        self.guid = guid
        self.elevation = elevation


def LevelsFromCsv():

    level_names = []
    level_heights = []

    filepath = rs.OpenFileName("BIMlight - Level csv import")
    level_file = open(filepath, "r")
    for line in level_file:
        line_split = line.strip().split(";")
        level_names.append(line_split[0])
        if line_split[0] == "":
            print ("BIMlight - Not all Levels have names")
        if not is_float(line_split[1]):
            print ("BIMlight ERROR - csv is not in the right number format")
            return
        else:
            level_heights.append(line_split[1])
    level_file.close()

    _save_levels(level_names, level_heights)
    return True

   
def SplitBrepByLevels():
    """
    select volumes and area calculation method to split level
    """
    levels_name = _chose_level_list()
    if levels_name == False:
        return
    if  levels_name == LVL_FROM_SURFACE:
        level_system = _get_level_system_from_user()
        if not level_system:
            return
        levels = _get_lvl_from_srf(level_system)
    else:
        levels = _get_levels(levels_name)
    if not levels:
        rs.MessageBox("Levels not loaded", 0, BOX_HEADER)
        return

    string = ""
    level_names = []
    for i in range(len(levels[0])):
        #apply elevation data and names to srfs
        if len(levels) > 3:
            level_elevation = levels[1][i]
            rs.SetUserText(levels[3][i], BL_LEVEL_ELEVATION[0], str(level_elevation))
        
            #check level name
            level_value = rs.GetUserText(levels[3][i], BL_LEVEL_NAME)
            if level_value:
                level_names.append(level_value)
            else:
                level_value = levels[0][i]
                level_names.append(level_value)
            rs.SetUserText(levels[3][i], BL_LEVEL_NAME, level_value)
        else:
            level_value = levels[0][i]
            level_names.append(level_value)
        #create user feedback
        string += (level_value + ": " + "\t" + str(levels[1][i]) + " " + rs.UnitSystemName(abbreviate = True)
                    + "\n")
        


    rs.MessageBox(string, 0, BOX_HEADER)
    

    prefix = "BIMlight::" + levels_name + "::"
    rs.EnableRedraw(False)
    rs.AddLayer(prefix + BL_LAYER_LEVEL_TEMP)
    rs.EnableRedraw(True)

    layer = prefix + BL_LAYER_LEVEL_TEMP

    volumes = rs.GetObjects("Select volumes to cut", 16)
    if not volumes: 
        rs.MessageBox("No volumes selected, select volume to cut.")
        volumes = rs.GetObjects("Select volumes to cut", 16)
    if not volumes:
        return


    if not levels:
        rs.MessageBox("BIMlight - No levels found")
        return
    planes = []
    for i in range(len(levels[1])):
        plane_point = Rhino.Geometry.Point3d(0,0,levels[1][i])
        planes.append(Rhino.Geometry.Plane(plane_point,
                            Rhino.Geometry.Plane.WorldXY.XAxis,
                            Rhino.Geometry.Plane.WorldXY.YAxis))
    rs.EnableRedraw(False)
    for i in range(len(planes)):
        #get level name
        level_number = levels[2]
        #level_elevation = levels[1]
        #LEVEL_HEIGHT
        for brep in volumes:
            brep_obj = scriptcontext.doc.Objects.Find(brep).Geometry
            brep_ids = _cut_and_create(brep_obj, planes[i])
            for id in brep_ids:
                rs.SetUserText(id, BL_LEVEL_NAME, level_names[i])
                #rs.SetUserText(id, BL_LEVEL_ELEVATION[0], str(level_elevation[i]))
                rs.SetUserText(id, BL_LEVEL, str(level_number[i]))
                rs.SetUserText(id, BL_AREA_SRF[0], _calculate_area_srf(id, False))
                rs.SelectObject(id)
                rs.ObjectLayer(id, layer)
    rs.EnableRedraw(True)


def AssignLevelsFromSrf():
    # Assigns levels to objects from level surfaces

    # INPUTS ----------------------------------

    # ask user to select level surfaces
    srfs = user_object_selection(True, display_message="Select level surfaces")
    if srfs == None:
        return

    level_system = _get_level_system_from_user()
    if not level_system:
        return
    
    # ask user to specify ground floor elevation
    elevation_gf = rs.GetReal("Specify ground floor elevation", number=0)
    if elevation_gf == None:
        return

    # ask user to specify average floor thickness
    floor_thickness = rs.GetReal("Specify average floor thickness", number=0)
    # if existing, get floor thickness
    try:
        floor_thickness = float(rs.GetDocumentUserText(BL_FLOOR_THICKNESS))
    except:
        pass
    if floor_thickness == None:
        return

    # CALCULATION -------------------------
    
    levels = _level_objects(srfs, level_system, elevation_gf)

    # Add level information to levels
    string = ""
    for t in range(len(levels)):
        rs.SetUserText(levels[t].guid, BL_LEVEL_ELEVATION[0], str(levels[t].elevation))
        rs.SetUserText(levels[t].guid, BL_LEVEL_NAME, str(levels[t].full_name))
        string += (levels[t].full_name + ": " + "\t" + str(levels[t].elevation) + " " + rs.UnitSystemName(abbreviate = True)
                    + "\n")
    rs.MessageBox(string, 0, BOX_HEADER)

    # ask user to select objects to classify
    objs = user_object_selection(True, display_message="Select objects to classify")
    if objs == None:
        return
    # assign level to objects
    for count, obj in enumerate(objs):
        if (scriptcontext.escape_test(False)):
            print ("BIM Light: Task cancelled.")
            return
        print ("BIM Light: Calculating %d / %d (ESC to cancel)" %(count + 1, len(objs)))
        bbox = rs.BoundingBox(obj)
        sum_z = 0
        for point in bbox:
            sum_z += point[2]
        center_z = round(sum_z / 8, 2)
        for lvl in levels:
            if (lvl.level_above_elev - floor_thickness) > center_z >= (lvl.elevation - floor_thickness):
                rs.SetUserText(obj, BL_LEVEL, str(lvl.number))  
                rs.SetUserText(obj, BL_GEOM_LOCATION, str(center_z))  
                rs.SetUserText(obj, BL_LEVEL_NAME, str(lvl.full_name))
    return
    

##-------------------- PRIVATE FUNCTIONS

def _calculate_area_brep(obj_id, surface = False):
    """
    calculates the area of the lowest surface of a polysurface or extrusion
    """
    obj_type = rs.ObjectType(obj_id)

    if obj_type == 16 or obj_type == 1073741824:
        srf_ids = rs.ExplodePolysurfaces(obj_id)

    else:
        print ("%s is type %s and not consided" %(obj_id, obj_type))
        return None

    rel_srf_id_check = []
    lowest_centroid = None
    rel_srf_id = None
    for srf_id in srf_ids:
        srf_centroid = rs.SurfaceAreaCentroid(srf_id)
        if srf_centroid:
            if lowest_centroid == None:
                lowest_centroid = srf_centroid[0][2]
                rel_srf_id = srf_id
                rel_srf_id_check.append(rel_srf_id)
            else:
                test_val = lowest_centroid - srf_centroid[0][2]
                if test_val > (0-rs.UnitAbsoluteTolerance()):
                    if abs(test_val) <= rs.UnitAbsoluteTolerance():
                        rel_srf_id_check.append(rel_srf_id)
                    else:
                        rel_srf_id_check = [rel_srf_id]
                    lowest_centroid = srf_centroid[0][2]
                    rel_srf_id = srf_id
        else:
            continue

    if len(rel_srf_id_check) > 1:
        print ("BIM Light: More than one surface.")
        rs.DeleteObjects(srf_ids)
        return
    
    if rel_srf_id == None:
        print('{} has no SrfAreaCentroid, object not considered'.format(obj_id))
        return None

    #check if in xy plane
    rel_point = rs.SurfaceAreaCentroid(rel_srf_id)[0]
    rel_uv = rs.SurfaceClosestPoint(rel_srf_id, rel_point)
    normal_vector = rs.SurfaceNormal(rel_srf_id, rel_uv)

    dot_product = abs(normal_vector * Rhino.Geometry.Plane.WorldXY.ZAxis)
    if dot_product > 1.01 or dot_product < 0.99:
        print("BIM Light: SURFACE NOT IN XY PLANE. NOT CALCULATED.")
        rs.DeleteObjects(srf_ids)
        return None

    if rel_srf_id:
        area = rs.Area(rel_srf_id)
        if surface == True:
            rel_srf_id_copy = rs.CopyObject(rel_srf_id)
            rs.ObjectLayer(rel_srf_id_copy, BL_LAYER_GEO)
            rs.SetUserText(rel_srf_id_copy, BL_TEMP, "True")
            rs.ObjectColorSource([rel_srf_id_copy], 0)
            rs.SelectObject(rel_srf_id_copy)
        rs.DeleteObjects(srf_ids)
        return area
    else:
        rs.DeleteObjects(srf_ids)
        return None

def _calculate_volume_brep(obj_id, geometry = False):
    """
    calculates the volume of brep
    """
    obj_type = rs.ObjectType(obj_id)

    if obj_type == 16 or obj_type == 1073741824:
        psrf_closed = rs.IsPolysurfaceClosed(obj_id)

    else:
        print ("%s is type %s and not consided" %(obj_id, obj_type))
        return None

    if psrf_closed:
        if geometry == True:
            rel_srf_id_copy = rs.CopyObject(obj_id)
            rs.ObjectLayer(rel_srf_id_copy, BL_LAYER_GEO)
            rs.SetUserText(rel_srf_id_copy, BL_TEMP, "True")
            rs.ObjectColorSource([rel_srf_id_copy], 0)
            rs.SelectObject(rel_srf_id_copy)
        volume = rs.SurfaceVolume(obj_id)[0]
        return volume

    else:
        print ("BIM Light ERROR: Polysurface %s is not closed" %obj_id)
        return None

def _calculate_area_srf(obj_id, geometry = False):
    """
    calculates the area of srf
    """
    obj_type = rs.ObjectType(obj_id)

    if obj_type in [8, 16, 1073741824]:
        area = rs.SurfaceArea(obj_id)[0]
    else:
        print ("%s is type %s and not consided" %(obj_id, obj_type))
        return None

    if geometry == True:
        rel_srf_id_copy = rs.CopyObject(obj_id)
        rs.ObjectLayer(rel_srf_id_copy, BL_LAYER_GEO)
        rs.SetUserText(rel_srf_id_copy, BL_TEMP, "True")
        rs.ObjectColorSource([rel_srf_id_copy], 0)
        rs.SelectObject(rel_srf_id_copy)

    return area

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

##-------------------- PRIVATE LEVEL FUNCTIONS

def _get_level_system_from_user():

        # ask user to specify level system and write it to document text
        # if existing, get level system
        try:
            level_system = rs.GetDocumentUserText(BL_LEVEL_SYSTEM)
        except:
            pass
        
        if not level_system:
            user_level_system = rs.GetString("Ground floor is on level: (german = 0, english = 1)", 
                                            BL_LEVEL_SYSTEMS[0], 
                                            list(BL_LEVEL_SYSTEMS))
            if user_level_system:
                if BL_LEVEL_SYSTEMS[0] in user_level_system.lower():
                    level_system = 'german'
                    rs.SetDocumentUserText(BL_LEVEL_SYSTEM, level_system)
                elif BL_LEVEL_SYSTEMS[1] in user_level_system.lower():
                    level_system = 'english'
                    rs.SetDocumentUserText(BL_LEVEL_SYSTEM, level_system)
                else:
                    rs.MessageBox("That did not work, please click on an option when asked for a level system",
                                0, MSG_PREFIX)
                    return None
            else:
                rs.MessageBox("No level system specified, please try again",
                                0, MSG_PREFIX)
                return None
        return level_system

def _level_objects(surfaces, level_system, elevation_gf):
      # create level class instances
    levels = []
    level_names = []
    basement = 0
    for srf in surfaces:
        elev = round(rs.SurfaceAreaCentroid(srf)[0][2], 2)
        levels.append(Level_Data(str(srf), elev))
        if elev < elevation_gf:
            basement -= 1
                #check for surface names
        lvl_name = rs.GetUserText(srf, BL_LEVEL_NAME)
        if lvl_name:
            level_names.append(lvl_name)
        else: level_names.append("")


    # sort by elevation low to high
    levels.sort(key=lambda level: level.elevation, reverse=False)

    # set level names (a number) according to the prject level system
    for num, level in enumerate(levels, start=basement):
        if level_system == BL_LEVEL_SYSTEMS[0]:
            level.name = level.ABOVE_GROUND_GER
            level.number = num
            if level.number == 0:
                level.name = level.GROUND_FLOOR_GER
            elif level.number < 0:
                level.name = level.BELOW_GROUND_GER
            else:
                pass
        elif level_system == BL_LEVEL_SYSTEMS[1]:
            level.name = level.ABOVE_GROUND_ENG
            if num < 0:
                level.number = num
            else:
                level.number = num + 1
            if level.number < 1:
                level.name = level.BELOW_GROUND_ENG
            else:
                pass
        
    # get elevation from level above and add attribute to current level
    for count, level in enumerate(levels):
        if count < len(levels) - 1:
            lvl_next_elev = float(levels[count + 1].elevation)
            next_elev = lvl_next_elev
        else:
            next_elev = 1000000
        level.level_above_elev = next_elev
        if level_names[count] != "":
            level.full_name = level_names[count]
        else:
            level.full_name = level.name + str(abs(level.number)).zfill(2)
    return levels

def _save_levels(level_names, level_heights):
    """
    """
    value_names = ""
    value_heights = ""

    levels_name = rs.StringBox("BIMlight levels name")
    if not levels_name:
        rs.MessageBox("BIMlight - No Name defined")
        return

    key_text = BL_LEVELS_PREFIX + levels_name
    if rs.GetDocumentUserText(key_text):
        rs.MessageBox("BIMlight - Levels name exists already")
        return

    for i in range(len(level_names)):
        if level_names[i] == "":
            level_names[i] = "None"
        value_names += level_names[i]
        value_heights += level_heights[i]

        if i < len(level_names) - 1:
            value_names += STR_LIST_DELIMITER
            value_heights += STR_LIST_DELIMITER

    value_text = value_names + STR_DELIMITER + value_heights

    rs.SetDocumentUserText(key_text, value_text)
    return True

def _get_lvl_from_srf(lvl_system):
    """
    gets a nested list
    [[lvl-names], [lvl-elevation]]
    """

    output_lvls = [[],[],[],[]]

    # ask user to select level surfaces
    srfs = user_object_selection(True, display_message="Select level surfaces")
    levels = _level_objects(srfs, lvl_system, 0.0)
    
    for lvl in levels:
        output_lvls[0].append(lvl.full_name)
        output_lvls[1].append(lvl.elevation)
        output_lvls[2].append(lvl.number)
        output_lvls[3].append(lvl.guid)
    return output_lvls
 
def _create_layer_for_categories():
    """
    """
    return

def _cut_and_create(brep, plane):
    """
    cuts brep and gets surface
    """
    brep_ids = []
    brep_test = _to_brep(brep)
    if brep_test == True:
        brep = brep.ToBrep()
    int_result = Rhino.Geometry.Intersect.Intersection.BrepPlane(brep, plane, rs.UnitAbsoluteTolerance())

    if int_result[0] and len(int_result[1]) > 0:  
        crv_ids_temp = []
        for crv in int_result[1]:
            
            if crv.IsClosed:
                crv_id = scriptcontext.doc.Objects.AddCurve(crv)
                crv_ids_temp.append(crv_id)
            else:
                print ("BIMlight Warning - Plane did not cut volume")
                crv_id = None
                continue
        srf_id = rs.AddPlanarSrf(crv_ids_temp)
        brep_ids.append(srf_id)
        rs.DeleteObjects(crv_ids_temp)
    else:
        print ("BIMlight Warning - Plane did not cut volume")
    return brep_ids

def _to_brep(obj):
    """
    trys to get Brep geometry
    """
    try:
        obj.ToBrep()
        return True
    except:
        return False

def _chose_level_list():

    levels_options = []
    doc_keys = rs.GetDocumentUserText()
    if doc_keys:
        for key in doc_keys:
            if BL_LEVELS_PREFIX in key:
                levels_options.append(key)
    levels_options.append(LVL_FROM_SURFACE)
    if len(levels_options) == 0:
        rs.MessageBox("No levels found", 0, "BIMlight")
    levels = rs.ListBox(levels_options, "Choose your levels", MSG_PREFIX)
    if not levels:
        return False
    else:
        return levels

def _get_levels(level_list_name):

    levels_chosen = rs.GetDocumentUserText(level_list_name)
    names_levels = _decrypt_levels(levels_chosen)

    #height_values = rs.PropertyListBox(names_levels[0], names_levels[1],
    #                                "Level Heights - Changes will not be saved",
    #                               "BIMlight")
    
    string = ""

    height_values = names_levels[1]
    #workaround for level number
    count_levels = []
    height_values_float = []
    for i in range(len(height_values)):
        if not is_float(height_values[i]):
            rs.MessageBox("Not all levels are numbers", 0, "BIMlight")
            return
        else:
            height_values_float.append(float(height_values[i]))
            count_levels.append(i)

    return[names_levels[0], height_values_float, count_levels]

def _decrypt_levels(levels_text_value):
    """
    decrypts levels in the format name,name,name;height,height,height of unlimited end
    """

    names_levels = levels_text_value.split(STR_DELIMITER)
    names = names_levels[0].split(STR_LIST_DELIMITER)
    levels = names_levels[1].split(STR_LIST_DELIMITER)

    return [names, levels]
