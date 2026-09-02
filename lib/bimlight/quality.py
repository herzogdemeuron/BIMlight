"""
Module for checking stored quantities against the geometry they came from.
"""

import rhinoscriptsyntax as rs
import rhyton

import calculate


def storedKey(key):
    """
    Builds the user text key that rhyton writes for a given calculation.

    Args:
        key (str): A key from ``calculate.CALCULATIONS``.

    Returns:
        str: The user text key on the object.
    """
    return rhyton.Format.key(
            rhyton.Rhyton().extensionName + rhyton.Rhyton.DELIMITER + key)


def findMismatches(guids):
    """
    Recalculates every stored quantity and collects the objects whose stored
    value no longer matches their geometry.
    Objects that do not carry a given key are skipped.

    Args:
        guids (list(str)): A list of Rhino object ids.

    Returns:
        dict: Calculation key mapped to the guids that no longer match.
    """
    checks = [(storedKey(key), key, calculation)
            for key, calculation in calculate.CALCULATIONS.items()]
    decimals = rhyton.Rhyton.ROUNDING_DECIMALS
    mismatches = dict()

    with rhyton.ProgressBar(len(guids), label="Quality Check...") as bar:
        for guid in guids:
            for userTextKey, key, calculation in checks:
                stored = rhyton.ElementUserText.getValue(guid, userTextKey)
                if stored is None:
                    continue

                if not _matches(stored, calculation(guid), decimals):
                    mismatches.setdefault(key, []).append(guid)

            bar.update()

    return mismatches


def gate(guids):
    """
    Offers to run the quality check and lets the user decide how to proceed.
    Objects whose stored values no longer match their geometry are selected so
    they can be inspected before the export continues.

    Args:
        guids (list(str)): The objects about to be exported.

    Returns:
        bool: True when the export should continue.
    """
    if not rhyton.Rhyton().qualityCheck:
        return True

    if not rhyton.SelectionWindow.confirm(
            "Run quality check on {0} object(s) before exporting?".format(
                    len(guids))):
        return True

    rs.EnableRedraw(False)
    try:
        mismatches = findMismatches(guids)
    finally:
        rs.EnableRedraw(True)

    if not mismatches:
        print("Quality check passed for {0} object(s).".format(len(guids)))
        return True

    affected = set()
    for flagged in mismatches.values():
        affected.update(flagged)

    rs.UnselectAllObjects()
    rs.SelectObjects(list(affected))

    lines = ["{0} object(s) have values that differ from their geometry.".format(
            len(affected)), ""]
    for key in sorted(mismatches):
        lines.append("- {0}: {1}".format(key, len(mismatches[key])))

    lines.append("")
    lines.append("These objects are now selected."
            " Values may have been entered manually.")
    lines.append("")
    lines.append("Export anyway?")

    return rhyton.SelectionWindow.confirm("\n".join(lines))


def _matches(stored, current, decimals):
    """
    Compares a stored quantity to a freshly calculated one at the rounding
    precision configured for the extension.

    Args:
        stored (mixed): The value read from the object user text.
        current (float): The recalculated value, or None.
        decimals (int): The number of decimals to compare at.

    Returns:
        bool: True when both values agree.
    """
    if current is None:
        return False

    try:
        return round(float(stored), decimals) == round(float(current), decimals)
    except (TypeError, ValueError):
        return False
