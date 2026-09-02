"""
Base module for the rthyton package.
"""

class Rhyton(object):
    """
    Base class to provide a shared data environment between sub-classes.
    This is particularly useful share extension specific settings across all 
    of self's classes while maintaining a single point of entry for developers
    using self as a base of their extension.

    Instead of having a variables.py, this class 
    contains all module-wide variables.

    The init of this class is typically called when instanciating a sub-class.
    The classes in the 'ui' module are a good example of this.

    Example::

        self.Visualize('<name_of_extension>').byGroup()

    This will trigger Rhyton to load the settings for the specified extension
    and provide them as a class variable.

    .. note::

        Create a Rhyton instance and provide you extension name 
        before using any other self functionality.
    """

    RHYTON_CONFIG = 'RHYTON_CONFIG'
    EXTENSION_NAME = 'rhyton'
    GROUP = '.group'
    TEXTDOTS = '.textDots'
    ORIGINAL_COLORS = '.originalColors'
    COLOR_SCHEMES = '.colorSchemes'
    SETTINGS = '.settings'
    POWERBI = '.powerbi'
    DELIMITER = "_"
    WHITESPACE = " "
    GUID = "guid"
    COLOR = 'color'
    COLOR_SOURCE = 'colorSource'
    EMPTY = "<empty>"
    NOT_AVAILABLE = "n/a"
    STANDARD_COLOR_1 = (200,200,255)
    STANDARD_COLOR_2 = (50,50,255)
    HEX_WHITE = '#FFFFFF'
    CSV = "CSV"
    JSON = "JSON"
    FONT = 'Arial'
    NAME = 'name'
    LAYER_HIERARCHY = 'layer_hierarchy'
    EXPORT_CHECKBOXES = 'exportCheckboxes'
    HDM_DT_DIR = 'C:/HdM-DT'

    # Extension settings
    KEY_PREFIX_NAME = 'key_prefix'
    UNIT_SUFFIX_NAME = 'unit_suffix'
    ROUNDING_DECIMALS_NAME = 'rounding_decimals'
    ROUNDING_DECIMALS = 2
    QUALITY_CHECK_NAME = 'quality_check'
    INCLUDE_BLOCKS_NAME = 'include_blocks'
    YES = 'Yes'
    NO = 'No'

    # shown instead of the raw key in the settings dialog
    SETTINGS_LABELS = {
            ROUNDING_DECIMALS_NAME: "Decimals in displayed numbers (number)",
            QUALITY_CHECK_NAME: "Ask QC before export (Yes/No)",
            INCLUDE_BLOCKS_NAME: "Include blocks (Yes/No)",
            }

    @staticmethod
    def isYes(value):
        """
        Interprets a Yes/No setting.

        Args:
            value (mixed): The stored setting value.

        Returns:
            bool: True if the setting is set to Yes.
        """
        return str(value).strip().lower() in ('yes', 'true', '1')

    @property
    def qualityCheck(self):
        """
        Whether the user is offered the quality check before an export.

        Returns:
            bool: True if the export should ask.
        """
        return self.isYes(self.settings.get(self.QUALITY_CHECK_NAME, self.YES))

    @property
    def includeBlocks(self):
        """
        Whether block instances count as objects rhyton operates on.

        Returns:
            bool: True if blocks should be included.
        """
        return self.isYes(
                self.settings.get(self.INCLUDE_BLOCKS_NAME, self.NO))


    def __init__(self, extensionName=None):
        """
        Inits a new Rhyton instance and loads the settings for given extension.
        Adds some shorthands to the settings as class variables.

        Args:
            extensionName (str): The name of the extension that is calling Rhyton.
        """
        if extensionName:
            Rhyton.EXTENSION_NAME = extensionName

        self.settings = self.getSettings()
        Rhyton.ROUNDING_DECIMALS = int(self.settings[self.ROUNDING_DECIMALS_NAME])

    def saveSettings(self, settings):
        """
        Saves a configuration to the document text.

        Args:
            settings (dict): The configuration to save.
        """
        from rhyton.document import DocumentConfigStorage

        DocumentConfigStorage().save(
                self.extensionSettings, settings)
    
    def getSettings(self):
        """
        Gets a settings configuration from the document text.
        Missing entries fall back to their generated default, so settings
        added in a later version do not break existing documents.

        Returns:
            dict: The configuration.
        """
        from rhyton.document import DocumentConfigStorage

        settings = self.generateSettings()
        config = DocumentConfigStorage().get(
                self.extensionSettings, None)
        if config:
            settings.update(config)

        return settings

    def generateSettings(self):
        """
        Generates a settings configuration.

        Returns:
            dict: The resulting configuration.
        """
        config = dict()
        config[self.ROUNDING_DECIMALS_NAME] = self.ROUNDING_DECIMALS
        config[self.QUALITY_CHECK_NAME] = self.YES
        config[self.INCLUDE_BLOCKS_NAME] = self.NO
        return config
    
    @property
    def extensionName(self):
        """
        The current extension name.

        Returns:
            string: The name of the currently active extension
        """
        return Rhyton.EXTENSION_NAME
    
    @property
    def extensionGroup(self):
        """
        The global group identifier prefixied with the current extension.

        Returns:
            string: The group identifier
        """
        return self.extensionName + self.GROUP
    
    @property
    def extensionTextdots(self):
        """
        The global text dot identifier prefixied with the current extension.

        Returns:
            string: The text dot identifier
        """
        return self.extensionName + self.TEXTDOTS
    
    @property
    def extensionOriginalColors(self):
        """
        The global original colors identifier prefixied with the current extension.

        Returns:
            string: The original colors identifier
        """
        return self.extensionName + self.ORIGINAL_COLORS
    
    @property
    def extensionColorSchemes(self):
        """
        The global color scheme identifier prefixied with the current extension.

        Returns:
            string: The color scheme identifier
        """
        return self.extensionName + self.COLOR_SCHEMES
    
    @property
    def extensionSettings(self):
        """
        The global settings identifier prefixied with the current extension.

        Returns:
            string: The settings identifier
        """
        return self.extensionName + self.SETTINGS
    
    @property
    def extensionPowerbi(self):
        """
        The global powerbi identifier prefixied with the current extension.

        Returns:
            string: The powerbi identifier
        """
        return self.extensionName + self.POWERBI

    