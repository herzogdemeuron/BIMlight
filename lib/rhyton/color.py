"""
Module for color operations.
"""
# python standard imports
import os
import json
import random
import colorsys
from collections import defaultdict

# rhyton imports
from rhyton.main import Rhyton
from rhyton.document import DocumentConfigStorage, ElementUserText, ElementOverrides

class Color:
    """
    Class for basic color operations.
    """
    @staticmethod
    def HSVtoRGB(hsv):
        """
        Convert a color from hsv to rgb.

        Args:
            hsv (tuple): A color in hsv format.

        Returns:
            tuple: A color in rgb format
        """
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]))

    @staticmethod
    def RGBtoHEX(rgb):
        """
        Convert an RGB color to HEX.

        Args:
            rgb (tuple): The RGB color.

        Returns:
            str: The HEX color
        """
        return '%02x%02x%02x' % rgb

    @staticmethod
    def HEXtoRGB(hexColor):
        """
        Converts a hex color string to rgb.

        Args:
            hexColor (sting): The hex color

        Returns:
            tuple: The rgb color
        """
        hexColor = hexColor.lstrip('#')
        return tuple(int(hexColor[i:i+2], 16) for i in (0, 2, 4))


class ColorScheme:
    """
    Class for handling relationships between labels and colors.
    """
    def __init__(self):
        """
        Inits a new ColorScheme instance.
        """
        self.flag = Rhyton().extensionColorSchemes
        self.schemes = DocumentConfigStorage().get(
            self.flag, defaultdict())
        self.defaultColors = [
                            '#F44336', '#E91E63', '#9C27B0', '#673AB7',
                            '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4',
                            '#009688', '#4CAF50', '#8BC34A', '#CDDC39',
                            '#FFEB3B', '#FFC107', '#FF9800', '#FF5722',
                            '#795548', '#607D8B'
                            ]
        self.additionalColors = [
                            '#D32F2F', '#C2185B', '#7B1FA2', '#512DA8',
                            '#303F9F', '#1976D2', '#0288D1', '#0097A7',
                            '#00796B', '#388E3C', '#689F38', '#AFB42B',
                            '#FBC02D', '#FFA000', '#F57C00', '#E64A19',
                            '#5D4037', '#616161', '#455A64'
                            ]
        self.extendedColors = self.defaultColors + self.additionalColors

    @staticmethod
    def toJSON(data, path):
        """
        Write color scheme to json

        Args:
            data (dict): The data to export
            path (str): The output file path.

        Returns:
            string: The json filepath
        """
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, 'w') as f:
            json.dump(data, f)

        return path

    @staticmethod
    def fromJSON(path):
        """
        Reads a color scheme from json.

        Args:
            path (string): The json file

        Returns:
            dict: The color scheme
        """
        with open(path, 'r') as f:
            scheme = json.load(f)

        return scheme

    @staticmethod
    def apply(guids, schemeName):
        """
        Applies a rhyton color scheme to given objects.
        Updates the color scheme with new keys and colors.

        Args:
            guids (str): A list of Rhino objects ids
            schemeName (string): The name of the color scheme

        Returns:
            dict: Same return as :func:`rhyton.document.ElementUserText.getValues` but with key "color" added.
        """
        keys = ElementUserText.getValues(guids, keys=schemeName)
        colorScheme = ColorScheme()
        keyColors = colorScheme.schemes.get(schemeName)
        if not keyColors:
            keyColors = colorScheme.generate(keys)
            if not keyColors:
                return None
            colorScheme.save(schemeName, keyColors)
        else:
            colorScheme.update(schemeName, keys)
            keyColors = colorScheme.schemes.get(schemeName)

        objectData = ElementUserText.get(guids, keys=schemeName)
        for entry in objectData:
            value = entry.get(schemeName)
            if value:
                entry[Rhyton.COLOR] = keyColors[value]
            else:
                entry[Rhyton.COLOR] = Rhyton.HEX_WHITE
                entry[schemeName] = Rhyton.NOT_AVAILABLE

        ElementOverrides.apply(objectData)
        return objectData

    @staticmethod
    def applyGradient(guids, schemeName, gradient):
        """
        Applies a rhyton color gradient to given objects.

        Args:
            guids (str): A list of guids.
            schemeName (str): The name of the color scheme.
            gradient (list): Two RGB colors: [start, end]
        """
        rawValues = ElementUserText.getValues(guids, keys=schemeName)
        values = sorted(v for v in rawValues
                if v is not None and v != Rhyton.WHITESPACE)
        keyColors = ColorScheme.gradientColors(values, gradient)
        objectData = ElementUserText.get(guids, keys=schemeName)
        for entry in objectData:
            value = entry.get(schemeName)
            if value in keyColors:
                entry[Rhyton.COLOR] = keyColors[value]

        ElementOverrides.apply(objectData)
        return objectData

    @staticmethod
    def gradientColors(values, gradient):
        """
        Maps given values onto a color gradient.
        Numeric values are placed proportionally to their magnitude, so the
        color distance between two values reflects their numeric distance.
        Any other set of values is spaced evenly along the gradient.

        Args:
            values (list): The sorted values to map.
            gradient (list): Two RGB colors: [start, end]

        Returns:
            dict: The values and their hex colors.
        """
        numbers = []
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                numbers = None
                break

            numbers.append(float(value))

        keyColors = dict()
        if numbers:
            low = min(numbers)
            span = max(numbers) - low
            for value, number in zip(values, numbers):
                parameter = 0.0 if span == 0 else (number - low) / span
                keyColors[value] = Color.RGBtoHEX(
                        Gradient.atParameter(parameter, gradient[0], gradient[1]))
        else:
            colors = Gradient.betweenRgbColors(
                    len(values), gradient[0], gradient[1])
            for value, rgb in zip(values, colors):
                keyColors[value] = Color.RGBtoHEX(rgb)

        return keyColors

    def generate(self, keys, excludeColors=None):
        """
        Generates a new color scheme.

        A color scheme has the following layout::

            {
                <schemeName>: {"key1": <hexcolor>}
            }

        Args:
            schemeName (string): The name of the color scheme
            keys (string): A set of keys
            excludeColors (string, optional): A list of colors to exclude

        Returns:
            dict: A color scheme
        """
        colors = ColorScheme().getColors(len(keys), excludeColors)
        if not colors:
            return None

        keyColors = dict()
        for value, color in zip(sorted(keys), colors):
            keyColors[value] = color

        return keyColors

    def update(self, schemeName, keys):
        """
        Updates a given color scheme with new keys and default colors
        and saves the changes to the DocumentConfigStorage.

        Args:
            scheme (dict): The color scheme to update
            keys (set): The keys to add

        Returns:
            dict: The updated color scheme
        """
        oldKeys = set(self.schemes[schemeName].keys())
        newKeys = list(set(keys).difference(oldKeys))
        if newKeys:
            excludeColors = self.schemes[schemeName].values()
            tempKeyColors = ColorScheme().generate(
                    newKeys, excludeColors=excludeColors)
            if not tempKeyColors:
                return None
            
            self.schemes[schemeName].update(tempKeyColors)

        DocumentConfigStorage().save(self.flag, self.schemes)

    def save(self, schemeName, keyValues):
        """
        Saves a single color scheme to the rhyton DocumentConfigStorage.

        Color schemes are stored as follows::

            {
                <extensionName>.colorSchemes: {
                    <schemeName1>: {"key1": "value1"},
                    <schemeName2>: {"key1": "value1"}
                }
            }

        Args:
            schemeName (str): The name of the color scheme
            keyValues (dict): The keys and colors associated with the name
        """
        scheme = dict()
        scheme[schemeName] = keyValues
        self.schemes.update(scheme)
        DocumentConfigStorage().save(self.flag, self.schemes)

    def delete(self, schemeName):
        """
        Deletes a color scheme from the rhyton DocumenConfigStorage.

        Args:
            scheme (dict): A color scheme
        """
        if schemeName in self.schemes:
            del self.schemes[schemeName]
        
        DocumentConfigStorage().save(self.flag, self.schemes)

    def getColors(self, count, excludeColors=[]):
        """
        Gets a given amount of colors.

        Args:
            count (int): The number of colors to get
            excludeColors (string, optional): List of colors to exclude. Defaults to None.

        Returns:
            string: A list of colors, or None when there are too many keys.
        """
        from rhyton.ui import SelectionWindow

        defaultColors = self._filterColors(excludeColors, self.defaultColors)
        extendedColors = self._filterColors(excludeColors, self.extendedColors)

        if count <= len(defaultColors):
            availableColors = defaultColors
        elif count <= len(extendedColors):
            availableColors = extendedColors
        elif count >= len(extendedColors) and count < 100:
            hsvColors = ColorRange(count).getHSV()
            availableColors = []
            for hsvColor in hsvColors:
                rgbColor = Color.HSVtoRGB(hsvColor)
                hexColor = Color.RGBtoHEX(rgbColor)
                availableColors.append(hexColor)
        else:
            SelectionWindow.showWarning(
                    "{0} different values are too many to color distinctly."
                    " Pick a parameter with fewer values.".format(count))
            return None

        colors = random.sample(availableColors, count)
        return colors
    
    def _filterColors(self, excludeColors, colors):
        """
        Filters a list of colors.

        Args:
            excludeColors (list): A list of colors to exclude.
            colors (list): A list of colors to filter.

        Returns:
            lsit: A filtered list of colors.
        """
        if excludeColors:
            return [color for color in colors if color not in excludeColors]
        else:
            return colors


class ColorRange:
    """
    Class for working with color ranges.
    """
    def __init__(self, count, min=0, max=100):
        """
        Inits a new ColorRange instance.

        Accepted values::

            0 <= min < 100
            1 < max <= 100
            count < max - min

        Raises:
            ValueError: If the arguments are outside the accepted range.
        """
        if not (0 <= min < 100):
            raise ValueError("ColorRange min must be 0 <= min < 100.")

        if not (1 < max <= 100):
            raise ValueError("ColorRange max must be 1 < max <= 100.")

        if not count < max - min:
            raise ValueError("ColorRange count must be smaller than max - min.")

        self.min = min
        self.max = max
        self.count = count
        self.range = max - min

    def getHSV(self):
        """
        Gets a list of colors in hsv format.

        Returns:
            list: A list of hsv colors
        """
        hsv = []
        for i in [
                x * 0.01 for x in range(
                        self.min, 
                        self.max,
                        (self.range / self.count))]:
            hsv.append((i, 0.5, 0.9))
        return hsv


class Gradient:
    """
    Class for working with gradients.
    """
    @classmethod
    def betweenRgbColors(cls, count, start, end):
        """
        Create a range of evenly spaced colors by interpolating the individual
        r, g, b values. The first color is always the start color, the last one
        is always the end color.

        Args:
            count (int): The total amout of colors to return.
            start (tuple): The start color.
            end (tuple): The end color.

        Returns:
            tuple: The interpolated rgb colors.
        """
        if count < 2:
            return tuple([tuple(start)] * max(count, 0))

        return tuple(cls.atParameter(
                float(i) / (count - 1), start, end) for i in range(count))

    @staticmethod
    def atParameter(parameter, start, end):
        """
        Interpolates a single rgb color between the start and end color.

        Args:
            parameter (float): The position on the gradient, from 0.0 to 1.0.
            start (tuple): The start color.
            end (tuple): The end color.

        Returns:
            tuple: The interpolated rgb color.
        """
        parameter = min(max(float(parameter), 0.0), 1.0)
        return tuple(
                min(max(int(round(s + (e - s) * parameter)), 0), 255)
                for s, e in zip(start, end))
    
