# -*- coding: utf-8 -*-

"""
Module for general utily functions.
"""
# rhyton imports
from rhyton.main import Rhyton


class Format:
    """
    Class for formatting keys and values to meet sql-standards
    """
    @staticmethod
    def key(key):
        """
        Sanitize given key to meet rhyton standards.

        Args:
            key (str): The key to clean.

        Returns:
            str: The sanitized key.
        """
        return key.replace(Rhyton.WHITESPACE, Rhyton.DELIMITER).lower()

    @staticmethod
    def value(value):
        """
        Sanitize given value to meet rhyton standards.

        Args:
            value (str): The value to clean.

        Returns:
            str: The sanitized value.
        """
        return str(value).replace(Rhyton.DELIMITER, Rhyton.WHITESPACE).title()

    @staticmethod
    def formatNumber(number, key, unitSuffix):
        """
        Formats a number.

        Args:
            number (float): The number to format.

        Returns:
            float: The formatted number.
        """
        key = key.lower()

        if 'area' in key:
            unitSuffix += '²'
        elif 'volume' in key:
            unitSuffix += '³'

        return str(round(number, Rhyton.ROUNDING_DECIMALS)) + " " + unitSuffix
    

def displayKey(key, rmPrefix=None):
    """
    Formats an SQL-style key ('snake_case') for display.
    Optionally removes a prefix.

    Example::

        displayKey("xyz_some_area", prefix="xyz_")
        >>> "Some Area"

    Args:
        key (str): The text to format.
        rmPrefix (str, optional): A prefix to remove. Defaults to None.

    Returns:
        _type_: _description_
    """
    if rmPrefix:
        if key.startswith(rmPrefix):
            key = key[len(rmPrefix):]
    
    return str(key).replace('_', " ").title()


def toList(data):
    """
    Ensures that the input data is a list.

    Args:
        data (mixed): The object to check

    Returns:
        list: The original object or the object wrapped in a list.
    """
    if isinstance(data, list):
        return data
    else:
        return [data]
    

def groupGuidsBy(data, keys):
    """
    Re-organizes a list of dictionaies by given key.
    All dicts in the list that share the same values for given keys will be
    merged into one dict.
    All the "guid"s of the source dicts get stored as a list under the 
    "guid" key in the merged dict and the source dicts are removed from the list.
    All keys other than the input keys will be removed in the process to
    prevent ambiguity.

    Args:
        data (dict): The Dictionary to re-organize.
        keys (list[str]): The list of keys to group by.
    """
    mergedDict = dict()
    keys = toList(keys)
    
    for d in data:
        values = tuple(d[key] for key in keys)
        
        if values not in mergedDict:
            mergedDict[values] = {Rhyton.GUID: []}
        
        mergedDict[values][Rhyton.GUID].append(d[Rhyton.GUID])
        
    result = []
    for k, v in mergedDict.items():
        newDict = dict(zip(keys, k))
        newDict[Rhyton.GUID] = v[Rhyton.GUID]
        result.append(newDict)

    return result


def removePrefix(string, prefix):
    """
    Removes a prefix from a string.
    Python 2.7 substitute for 'string.removeprefix(str)'

    Args:
        string (str): The text to remove the prefix from.
        prefix (str): The prefix to remove from the string.

    Returns:
        str: The resulting string.
    """
    if string.startswith(prefix):
        string = string[len(prefix):]
    
    return string


def detectType(value):
    """
    Tries to convert a given string to an integer, number or boolean.
    If no conversion is possible, the original string is returned.

    Args:
        value (str): The string to convert.
    """
    if value == None:
        return None
    
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if value.lower() in ['true', 'yes', '1']:
        return True
    elif value.lower() in ['false', 'no', '0']:
        return False

    return value