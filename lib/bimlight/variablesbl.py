# -*- coding: utf-8 -*-

"""
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - Variables

    Created on 29.06.2022 by y.schindel
    
"""

import rhinoscriptsyntax as rs

#variables
BIMLIGHT = "bimlight"
BL_PREFIX = "bl_"
BL_SUFFIX = "_bl"
BL_TEMP = "bl_temp"
BL_INFO = "bl_info_"
BL_LEVELS_PREFIX = "bl_levels_"
DELIMITER = "_"
STR_DELIMITER = ";"
STR_LIST_DELIMITER = ","
GRP_DELIMITER = "/"
BL_NONE = "<none>"
VALUE_ERROR = "NOT-DEFINED"
NOT_DEFINED_COLOR = (200,200,200)
SAMPLE_COLOR = (217,183,121)
KEY_SOURCE = BL_INFO + "orginal_color_source"
KEY_COLOR = BL_INFO + "origial_color"
KEY_GROUP_KEY = BL_INFO + "group_key"
KEY_KEY = BL_INFO + "visualized_key"
DOC_KEY_ROUND_DIGIT = BL_INFO + "round_digit_overwrite"
ROUND_DIGIT_STD_STR = "Standard"
DOC_KEY_UNIT_CONVERSION_FACTOR = BL_INFO + "unit_conversion_factor"
DOC_KEY_DISPLAY_UNIT = BL_INFO + "display_unit"
STANDARD_COLOR_1 = (200,200,255)
STANDARD_COLOR_2 = (50,50,255)
BL_EXPORT_ALIAS = "bl_export_alias"
BL_EXPORT_PATH = "bl_export_path"
BL_LAYER = "BL_TEMP"
BL_LAYER_GEO = "BL_TEMP_GEO"
BL_LAYER_COLOR = (255,0,255)
BL_CHECKBOX_DATA = "bl_checkbox_data"
BL_TEXTDOT_HEIGHT = 12.0
BL_FONT = "Arial"
BL_GROUPING_NAME = "_"
BL_COLOR_SUFFIX = "_bl_group_color"
BL_GROUP_DOT_COLOR = (255,255,255)

BL_LOCATION = "Location"
BL_INTERIOR = "Interior"
BL_EXTERIOR = "Exterior"

#TBD PARAMETERS VERTICAL AREAS
FACES_VERTICAL = "facesCalculated_bl"
TILT_FACE_INDEX = "tiltedFaceIndex_bl"
FACE_NORMAL_ANGLE_MAX = 0.01

COLOR_CORRECT = (0,255,0)
COLOR_ERROR = (255,0,0)
COLOR_ERROR_2 = (100,0,0)

#Messages
MSG_PREFIX = "HdM-BL: "
BOX_HEADER = "HdM BIM LIGHT"

#bl mass calculation variables
# numbers are used to raise to the power of x
BL_LENGTH_BREP = ("LENGTH_brep_bl", 1, "Length (brep)") # not in use on 201126
BL_AREA_SRF = ("AREA_srf_bl", 2, "Area (surfaces)")
BL_AREA_LOW_SRF = ("AREA_brep_bl", 2, "Area (brep lowest surface)")
BL_AREA_VOLUME = ("VOLUME_bl", 3, "Volume (solid)")

BL_SET_CONVERSION = ("", 0, "Unit Conversion (no auto recalc)")
BL_OVW_ROUNDING = ("", 0, "Rounding Decimals")

BL_IMPORT_CSV = ("", 0, "import attributes via csv")

#export
# Fixed headers are hardcoded into the Export_Object class, because class def rely on that.
# HEADER_CONTENT_FIXED = ["guid","name","block_name","color","layer","groups","bim_light_group"]
# BLOCK_NAME_HEADER = "block_name"
LAYER_HIER_PREFIX = "Layer Hierarchy "

#block variables
BBX_SCALE_FACTOR = (1.01, 1.01, 1.01)
BBX_STD_HEIGHT = 1.00

#bl level variables
BL_LAYER_LEVEL_TEMP = "TEMP"
BL_LEVEL = "Level"
BL_LEVEL_NAME = "LEVEL_NAME_bl"
BL_LEVEL_ELEVATION = ("LEVEL_ELEVATION_bl", 1, "Level Elevation")
BL_LEVEL_SYSTEM = "bl_level_system"
BL_LEVEL_SYSTEMS = ["german", "english"]
BL_FLOOR_THICKNESS = "bl_floor_thickness"
BL_GEOM_LOCATION = "bl_geo_cen_elevation"

#level standard options
LVL_FROM_SURFACE = "From Surface Geometry"

# PowerBI variables
PBI_DATA_NAME = "PowerBISession"
PBI_TEMPLATE_1 = "W:/01 Rhino3D/BIMlight/PBI Templates/BIMlightOptions.pbit"
PBI_TEMPLATE_1_ALIAS = "Compare Options - Layer Hierarchy (max 3)"
PBI_TEMPLATE_2 = "W:/01 Rhino3D/BIMlight/PBI Templates/BIMlightTimelineSimple.pbit"
PBI_TEMPLATE_2_ALIAS = "Timeline - Simple (No Hierarchy)"
PBI_TEMPLATE_3 = "W:/01 Rhino3D/BIMlight/PBI Templates/BIMlightTimelineHierarchy.pbit"
PBI_TEMPLATE_3_ALIAS = "Timeline - Layer Hierarchy (max 3)"
PBI_TEMPLATE_4 = "W:/01 Rhino3D/BIMlight/PBI Templates/BIMlightTimelineHierarchy.pbit"
PBI_TEMPLATE_CUSTOM_ALIAS = "Load Custom Template (Contact DT for setup)"
PBI_TEMPLATE_OPTIONS = [PBI_TEMPLATE_1_ALIAS, PBI_TEMPLATE_2_ALIAS, PBI_TEMPLATE_3_ALIAS, PBI_TEMPLATE_CUSTOM_ALIAS]
PBI_TEMPLATE_LOCAL = "C:/temp/BIM-LIGHT-EXPORT/PowerBI_Template.pbit"
PBI_MODE = "bl_power_bi_mode"
MAX_HIERARCHY = 3

BL_MASSES = [BL_AREA_SRF,
            BL_AREA_LOW_SRF,
            BL_AREA_VOLUME
            #BL_LEVEL_ELEVATION
            ]

BL_SETTINGS =   [BL_SET_CONVERSION,
                BL_OVW_ROUNDING
                ]

CONVERSION_LOOKUP_TABLE = \
   {"None" : 1,
   "Millimeters" : rs.UnitScale(2),
   "Centimeters" : rs.UnitScale(3),
   "Meters" : rs.UnitScale(4),
   "Kilometers" : rs.UnitScale(5),
   "Inches" : rs.UnitScale(8),
   "Feet" : rs.UnitScale(9),
   "Miles" : rs.UnitScale(10),
   "Nautical mile" : rs.UnitScale(22),
   "Lightyears": rs.UnitScale(24),
   "Parsecs": rs.UnitScale(25)
   }

DISPLAY_LOOKUP_TABLE = \
   {"Millimeters" : " mm",
   "Centimeters" : " cm",
   "Meters" : " m",
   "Kilometers" : " km",
   "Inches" : " in",
   "Feet" : " ft",
   "Miles" : " mi",
   "Nautical mile" : " nmi",
   "Lightyears": " wtf",
   "Parsecs": " are you Han Solo?"
   }

ROUNDING_LOOKUP_TABLE = \
   {"Millimeters" : 0,
   "Centimeters" : 0,
   "Meters" : 1,
   "Kilometers" : 2,
   "Inches" : 1,
   "Feet" : 1,
   "Miles" : 2,
   "Nautical mile" : 2,
   "Lightyears": 0,
   "Parsecs": 0
   }

#export variables
EXPORT_PATH = "C:/temp/BIM-LIGHT-EXPORT"
FILE_NAME = "ObjectInformation"
#today = datetime.now().strftime("%Y%m%d_%H%M%S")