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
    # Get total selection count before filtering
    allSelected = rs.GetObjects(preselect=True, select=True)
    if not allSelected:
        return
    totalSelected = len(allSelected)
    
    breps = rhyton.GetBreps([8, 16, 1073741824])  # Only surfaces, polysurfaces, extrusions
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    failedObjectList = []

    with rhyton.ProgressBar(len(breps)) as bar:
        for brep in breps:
            if not rs.ObjectType(brep) == 8:
                #explode brep to get singel surfaces
                surfaces = rs.ExplodePolysurfaces(brep)
                if len(surfaces)==0:
                    print ("%s can not be calculated" %(brep)) 
                    failedObjectList.append(brep)
                    rs.DeleteObjects(surfaces)
                    continue
                #create list of minimal Z centroid of each surface and select lowest
                minimaZ = []
                for srf in surfaces:
                    srfAreaCentroid = rs.SurfaceAreaCentroid(srf)
                    if srfAreaCentroid == None:
                        print ("%s can not be calculated" %(brep)) 
                        failedObjectList.append(brep)
                        rs.DeleteObjects(surfaces)
                        minimaZ = []
                        area = None
                        break
                    else:
                        minimaZ.append(srfAreaCentroid[0][2])
                if len(minimaZ) > 0:
                    surface = surfaces[minimaZ.index(min(minimaZ))]
                    #calculate area of bottom surface
                    area = rs.SurfaceArea(surface)[0]
                    rs.DeleteObjects(surfaces)
            else:
                area = rs.SurfaceArea(brep)[0]

            if area != None:
                info = dict()
                info['guid'] = brep
                info['bottom face area'] = area
                data.append(info)
                bar.update()
    
        rhyton.ElementUserText.apply(data)

    rs.UnselectAllObjects()
    rs.EnableRedraw(True)
    
    _errorOutput(failedObjectList)
    
    # Check if some objects were not processed
    if len(data) + len(failedObjectList) < totalSelected:
        print("Note: Bottom Face Area calculation only includes Surfaces, Polysurfaces and Extrusions.")
    
    return

def _surfaceArea():
    """
    Calculates the surface area of a Brep or Hatch.
    Uses Rhyton to write the results to the user text of the objects.
    """
    # Get total selection count before filtering
    allSelected = rs.GetObjects(preselect=True, select=True)
    if not allSelected:
        return
    totalSelected = len(allSelected)
    
    breps = rhyton.GetBreps([8, 16, 1073741824, 65536])  # Surfaces, polysurfaces, extrusions, hatches
    if not breps:
        return
    
    failedObjectList = []
    failedHatchList = []  # Separate list for failed hatches

    rs.EnableRedraw(False)
    data = []

    with rhyton.ProgressBar(len(breps)) as bar:
        for brep in breps:
            info = dict()
            info['guid'] = brep
            area = None
            
            objectType = rs.ObjectType(brep)
            
            if objectType == 65536:  # Hatch
                area = rs.Area(brep)
                if area is None:
                    print("%s hatch area could not be calculated" % brep)
                    failedHatchList.append(brep)
                    bar.update()
                    continue
            else:
                # Existing BREP area calculation
                brepSurface = rs.SurfaceArea(brep)
                if brepSurface == None:
                    print("%s can not be calculated" % brep) 
                    failedObjectList.append(brep)
                    bar.update()
                    continue
                area = brepSurface[0]
            
            info['surface area'] = area
            data.append(info)
            bar.update()

        rhyton.ElementUserText.apply(data)

    rs.UnselectAllObjects()
    rs.EnableRedraw(True)
    
    # Handle all failed objects with combined feedback
    _combinedErrorOutput(failedObjectList, failedHatchList)
    
    # Check if some objects were not processed
    if len(data) + len(failedObjectList) + len(failedHatchList) < totalSelected:
        print("Note: Surface Area calculation only includes Surfaces, Polysurfaces, Extrusions and Hatches.")
    
    return

def _volume():
    """
    Calculates the volume of a Brep.
    Uses Rhyton to write the results to the user text of the objects.
    """
    # Get total selection count before filtering
    allSelected = rs.GetObjects(preselect=True, select=True)
    if not allSelected:
        return
    totalSelected = len(allSelected)
    
    breps = rhyton.GetBreps([16, 1073741824])  # Only closed polysurfaces and extrusions
    if not breps:
        return
    
    rs.EnableRedraw(False)
    data = []

    failedObjectList = []

    with rhyton.ProgressBar(len(breps)) as bar:
        for brep in breps:
            #check type and if brep is closed
            objectType = rs.ObjectType(brep)
            if objectType == 16 or objectType == 1073741824:
                isPolySrfClosed = rs.IsPolysurfaceClosed(brep)
            else:
                print ("%s is type %s and can not be calculated" %(brep, objectType))
                failedObjectList.append(brep)
                continue
            
            if isPolySrfClosed:
                brepVolume = rs.SurfaceVolume(brep)
                if brepVolume == None: 
                    print ("%s can not be calculated" %(brep)) 
                    failedObjectList.append(brep)
                    continue
            else:
                print ("%s is not closed and can not be calculated" %(brep))
                failedObjectList.append(brep)
                continue

            info = dict()
            info['guid'] = brep
            info['volume'] = brepVolume[0]
            data.append(info)
            bar.update()
        
        rhyton.ElementUserText.apply(data)
    
    rs.UnselectAllObjects()
    rs.EnableRedraw(True)
    
    _errorOutput(failedObjectList)
    
    # Check if some objects were not processed
    if len(data) + len(failedObjectList) < totalSelected:
        print("Note: Volume calculation only includes closed Polysurfaces and Extrusions.")

    return

def _errorOutput(list):
    """
    Creates warning message and prints for list of object that failed to calculate
    """

    if len(list) > 0:
        rs.SelectObjects(list)
        rhyton.SelectionWindow.showWarning(
            'Partial volume calculation failure.'
            + ' Selected items affected. See Command window for details.'
            )
        print ("Calculation partially successful")
    else:
        print ("Calculation successful")

    return

def _combinedErrorOutput(objectList, hatchList):
    """
    Creates combined warning message for all objects that failed surface area calculation
    """
    allFailedObjects = objectList + hatchList
    
    if len(allFailedObjects) > 0:
        message = (
            'Surface area calculation failed for {0} object(s):\n'
            '- {1} surface/polysurface objects\n'
            '- {2} hatch objects\n\n'
            'This may be due to invalid geometry, open boundaries, '
            'or unsupported object types.\n\n'
            'Affected objects will be selected after clicking OK.'
        ).format(len(allFailedObjects), len(objectList), len(hatchList))
        
        rhyton.SelectionWindow.showWarning(message)
        rs.SelectObjects(allFailedObjects)
        print("Surface area calculation failed for {0} objects".format(len(allFailedObjects)))
    else:
        print("Surface area calculation successful")
    
    return
