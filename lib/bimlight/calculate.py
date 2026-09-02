"""
module for calculating object information.
"""

import rhinoscriptsyntax as rs
import rhyton

SURFACE = 8
POLYSURFACE = 16
HATCH = 65536
EXTRUSION = 1073741824

BOTTOM_FACE_AREA = 'bottom face area'
SURFACE_AREA = 'surface area'
VOLUME = 'volume'


def bottomFaceArea(guid):
    """
    Calculates the area of the lowest face of a Brep.
    Single surfaces are measured directly.

    Args:
        guid (str): A Rhino object id.

    Returns:
        float: The area, or None if it cannot be calculated.
    """
    if rs.ObjectType(guid) == SURFACE:
        area = rs.SurfaceArea(guid)
        return area[0] if area else None

    surfaces = rs.ExplodePolysurfaces(guid)
    if not surfaces:
        return None

    try:
        elevations = []
        for surface in surfaces:
            centroid = rs.SurfaceAreaCentroid(surface)
            if not centroid:
                return None

            elevations.append(centroid[0][2])

        area = rs.SurfaceArea(surfaces[elevations.index(min(elevations))])
        return area[0] if area else None
    finally:
        rs.DeleteObjects(surfaces)


def surfaceArea(guid):
    """
    Calculates the surface area of a Brep or the area of a hatch.

    Args:
        guid (str): A Rhino object id.

    Returns:
        float: The area, or None if it cannot be calculated.
    """
    if rs.ObjectType(guid) == HATCH:
        return rs.Area(guid)

    area = rs.SurfaceArea(guid)
    return area[0] if area else None


def volume(guid):
    """
    Calculates the volume of a closed Brep.

    Args:
        guid (str): A Rhino object id.

    Returns:
        float: The volume, or None for open Breps and anything that cannot be calculated.
    """
    if not rs.IsPolysurfaceClosed(guid):
        return None

    result = rs.SurfaceVolume(guid)
    return result[0] if result else None


CALCULATIONS = {
        BOTTOM_FACE_AREA: bottomFaceArea,
        SURFACE_AREA: surfaceArea,
        VOLUME: volume,
        }


def createObjectInformation():
    """
    Creates object information.
    Asks for the information to create and executes the corresponding function.
    """
    bottomLabel = 'Bottom Face Area'
    surfaceLabel = 'Surface Area'
    volumeLabel = 'Volume'
    res = rhyton.SelectionWindow.show(
            [bottomLabel, surfaceLabel, volumeLabel],
            "Choose Calculation:")
    if not res:
        return

    if res == bottomLabel:
        _bottomFaceArea()
    elif res == surfaceLabel:
        _surfaceArea()
    elif res == volumeLabel:
        _volume()


def _bottomFaceArea():
    """
    Calculates the bottom face area of the selected Breps and writes the
    results to their user text.
    """
    _applyCalculation(
            BOTTOM_FACE_AREA,
            [SURFACE, POLYSURFACE, EXTRUSION],
            "Only Surfaces, Polysurfaces and Extrusions are supported.")


def _surfaceArea():
    """
    Calculates the surface area of the selected Breps and hatches and writes
    the results to their user text.
    """
    _applyCalculation(
            SURFACE_AREA,
            [SURFACE, POLYSURFACE, EXTRUSION, HATCH],
            "Only Surfaces, Polysurfaces, Extrusions and Hatches are supported.")


def _volume():
    """
    Calculates the volume of the selected closed Breps and writes the results
    to their user text.
    """
    _applyCalculation(
            VOLUME,
            [POLYSURFACE, EXTRUSION],
            "Only closed Polysurfaces and Extrusions are supported.")


def _applyCalculation(key, objectTypes, requirement):
    """
    Runs the calculation registered for given key over the current selection
    and writes the results to the user text of the objects it could handle.
    Objects that could not be calculated are selected afterwards.

    Args:
        key (str): The user text key to write.
        objectTypes (list(int)): The Rhino object types to keep from the selection.
        requirement (str): Describes which objects the calculation supports.
    """
    selection = rs.GetObjects(preselect=True, select=True)
    if not selection:
        return

    guids = [str(g) for g in selection if rs.ObjectType(g) in objectTypes]
    if not guids:
        rhyton.SelectionWindow.showWarning("Nothing to calculate. " + requirement)
        return

    calculate = CALCULATIONS[key]
    data = []
    failed = []

    rs.EnableRedraw(False)
    try:
        with rhyton.ProgressBar(len(guids)) as bar:
            for guid in guids:
                value = calculate(guid)
                if value is None:
                    failed.append(guid)
                else:
                    data.append({rhyton.Rhyton.GUID: guid, key: value})

                bar.update()

        rhyton.ElementUserText.apply(data)
        rs.UnselectAllObjects()
    finally:
        rs.EnableRedraw(True)

    skipped = len(selection) - len(guids)
    if skipped:
        print("{0} object(s) skipped. {1}".format(skipped, requirement))

    if failed:
        rs.SelectObjects(failed)
        rhyton.SelectionWindow.showWarning(
                "{0} object(s) could not be calculated and are now selected.\n"
                "This is usually caused by invalid or open geometry.".format(
                        len(failed)))
    else:
        print("Calculated '{0}' for {1} object(s).".format(key, len(data)))
