"""
module for calculating object information.
"""

import rhinoscriptsyntax as rs
import rhyton


def createObjectInformation():
    """
    Creates object information.
    Asks for the information to create and executes the corresponding function.
    """
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
    """
    Calculates the bottom face area of a Brep.
    If the Brep is a polysurface, the bottom face area is the area of the
    surface with the lowest centroid.
    If the Brep is a surface, the bottom face area is the area of the surface.
    Uses Rhyton to write the results to the user text of the objects.
    """
    breps = rhyton.GetBreps()
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    with rhyton.ProgressBar(len(breps)) as bar:
        for brep in breps:
            if not rs.ObjectType(brep) == 8:
                surfaces = rs.ExplodePolysurfaces(brep)
                minimaZ = [rs.SurfaceAreaCentroid(srf)[0][2] for srf in surfaces]
                surface = surfaces[minimaZ.index(min(minimaZ))]
                area = rs.SurfaceArea(surface)[0]
                rs.DeleteObjects(surfaces)
            else:
                area = rs.SurfaceArea(brep)[0]

            info = dict()
            info['guid'] = brep
            info['bottom face area'] = area
            data.append(info)
            bar.update()
    
        rhyton.ElementUserText.apply(data)

    rs.EnableRedraw(True)

def _surfaceArea():
    """
    Calculates the surface area of a Brep.
    Uses Rhyton to write the results to the user text of the objects.
    """
    breps = rhyton.GetBreps()
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    with rhyton.ProgressBar(len(breps)) as bar:
        for brep in breps:
            info = dict()
            info['guid'] = brep
            info['surface area'] = rs.SurfaceArea(brep)[0]
            data.append(info)
            bar.update()

        rhyton.ElementUserText.apply(data)

    rs.EnableRedraw(True)

def _volume():
    """
    Calculates the volume of a Brep.
    Uses Rhyton to write the results to the user text of the objects.
    """
    breps = rhyton.GetBreps()
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    with rhyton.ProgressBar(len(breps)) as bar:
        for brep in breps:
            info = dict()
            info['guid'] = brep
            info['volume'] = rs.SurfaceVolume(brep)[0]
            data.append(info)
            bar.update()
        
        rhyton.ElementUserText.apply(data)
        
    rs.EnableRedraw(True)

