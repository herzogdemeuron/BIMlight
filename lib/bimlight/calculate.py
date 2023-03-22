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

