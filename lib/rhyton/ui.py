"""
Module for interacting with the user.
Provides ready-made functions that can be used by buttons in any extension.
"""
# python standard imports
import os
from datetime import datetime

# rhino imports
import rhinoscriptsyntax as rs

# rhyton imports
from rhyton.main import Rhyton
from rhyton.export import CsvExporter, JsonExporter
from rhyton.document import GetBreps, ElementUserText, Group, TextDot, GetFilePath
from rhyton.document import DocumentConfigStorage, ElementOverrides, Layer
from rhyton.utils import Format, groupGuidsBy

class Visualize:
    """
    Class for visualizing user text on Rhino objects.
    """
    @classmethod
    def byGroup(cls):
        """
        Visualizes a set of Rhino objects and their user text:
        The user input 'Parameter to Group By' is used for coloring
        and grouping objects, as well as for building sub-totals of the
        user-selected 'Parameter to Summarize'.
        Places text dots with the value for each group.
        """
        from rhyton.color import ColorScheme

        breps = GetBreps()
        if not breps:
            return
        
        with Layer.hierarchyInformation(breps):
            keys = ElementUserText.getKeys(breps)
            if not keys:
                SelectionWindow.showWarning('No user text found on selected objects.')
                return
            
            selectedKey = SelectionWindow.show(
                    keys, message='Select Parameter to Group By:')
            if not selectedKey:
                return
            
            selectedValue = SelectionWindow.show(
                    keys, message='Select Parameter to Summarize')
            if not selectedValue:
                return
            
            cls.reset()
            rs.EnableRedraw(False)
            try:
                objectData = ColorScheme.apply(breps, selectedKey)
                if not objectData:
                    return

                objectData = groupGuidsBy(objectData, [selectedKey, Rhyton.COLOR])
                objectData = TextDot.add(
                        objectData, selectedValue, prefixKey=selectedKey)
                for item in objectData:
                    Group.create(item[Rhyton.GUID], item[selectedKey])

                rs.UnselectAllObjects()
            finally:
                rs.EnableRedraw(True)

    @classmethod
    def sumTotal(cls):
        """
        Visualizes the total for selected parameter.
        Groups selected objects and places a text dot to display the total.
        Non-number parameter values will result in a simple object count.
        """
        from rhyton.color import ColorScheme

        breps = GetBreps()
        if not breps:
            return
        
        keys = ElementUserText.getKeys(breps)
        if not keys:
            SelectionWindow.showWarning('No user text found on selected objects.')
            return
        
        selectedKey = SelectionWindow.show(
                keys, message='Select Parameter to Calculate Total:')
        if not selectedKey:
            return
        
        colors = ColorScheme().getColors(1)
        if not colors:
            return

        cls.reset()
        rs.EnableRedraw(False)
        try:
            objectData = {}
            objectData[Rhyton.GUID] = breps
            objectData[Rhyton.COLOR] = colors[0]
            ElementOverrides.apply(objectData)
            objectData = TextDot.add(objectData, selectedKey)
            for item in objectData:
                Group.create(item[Rhyton.GUID])

            rs.UnselectAllObjects()
        finally:
            rs.EnableRedraw(True)

    @classmethod
    def byValue(cls):
        """
        Visualizes the value of selected parameter for each object individually.
        Applies a user-defined color gradient to the values.
        """
        from rhyton.color import ColorScheme

        breps = GetBreps()
        if not breps:
            return

        keys = ElementUserText.getKeys(breps)
        if not keys:
            SelectionWindow.showWarning('No user text found on selected objects.')
            return
        
        selectedKey = SelectionWindow.show(
                options=keys, message='Select Parameter to visualize:')
        if not selectedKey:
            return
        
        color = rs.GetColor(Rhyton.STANDARD_COLOR_1)
        if not color:
            return
        
        colorStart = [color[0], color[1], color[2]]
        
        color = rs.GetColor(Rhyton.STANDARD_COLOR_2)
        if not color:
            return    
        
        colorEnd = [color[0], color[1], color[2]]

        cls.reset()
        rs.EnableRedraw(False)
        try:
            objectData = ColorScheme.applyGradient(
                    breps, selectedKey, [colorStart, colorEnd])
            objectData = TextDot.add(
                    objectData, selectedKey, aggregate=False)
            for item in objectData:
                Group.create(item[Rhyton.GUID])

            rs.UnselectAllObjects()
        finally:
            rs.EnableRedraw(True)
    
    @staticmethod
    def reset(clearSource=False):
        """
        Resets the visualization for 'all' or 'selected' objects.
        Ungroups visualized objects.
        """
        preSelection = rs.SelectedObjects()
        resetAll = 'select'
        if not preSelection:
            choices = {
                    "Yes, reset all.": 'reset',
                    "No wait, let me select!": 'select'}
            resetAll = SelectionWindow.show(
                    choices, message='Reset all visualizations?')

        if resetAll == 'select':
            breps = GetBreps(filterByTypes=[8, 16, 8192, 1073741824, 65536])
            if not breps:
                return
            
            rs.EnableRedraw(False)
            ElementOverrides.clear(breps, clearSource=clearSource)
            Group.dissolve(breps)
        elif resetAll == 'reset':
            rs.EnableRedraw(False)
            data = DocumentConfigStorage().get(
                    Rhyton().extensionOriginalColors, dict())
            if not data:
                rs.EnableRedraw(True)
                SelectionWindow.showWarning(
                        "No information about original colors available."
                        " Select the elements and try again.")
                return

            guids = data.keys()
            # check if guids are still valid
            guids = [guid for guid in guids if rs.IsObject(guid)]
            Group.dissolve(guids)
            ElementOverrides.clear(guids, clearSource=clearSource)
            textDots = DocumentConfigStorage().get(
                    Rhyton().extensionTextdots, dict()).keys()
            rs.DeleteObjects(textDots)
            DocumentConfigStorage().save(Rhyton().extensionTextdots, None)

        rs.EnableRedraw(True)
    

class ColorSchemeEditor:
    def __init__(self):
        """
        Inits a new ColorSchemeEditor Instance. Asks the user to select
        a color scheme and opens a dialog to edit the colors.
        """
        from rhyton.color import ColorScheme

        schemeName = self.showSchemes()
        if not schemeName:
            return
        
        keyValues = self.showColors(schemeName)
        if not keyValues:
            return
        
        ColorScheme().save(schemeName, keyValues)
    
    @staticmethod
    def showSchemes():
        """
        Ask the user to select a color scheme.

        Returns:
            str: The name of the selected color scheme.
        """
        from rhyton.color import ColorScheme

        schemes = ColorScheme().schemes.keys()
        if not schemes:
            SelectionWindow.showWarning("No color schemes available, Use 'Visualize Data by Grouping' first.")
            return
        
        return SelectionWindow.show(
                ColorScheme().schemes.keys(), message="Select Color Scheme:")

    @staticmethod
    def showColors(schemeName):
        """
        Presents the user a dialog to edit the colors of a color scheme.

        Args:
            schemeName (str): The name of the color scheme to edit.
        """
        from rhyton.color import ColorScheme

        scheme = ColorScheme().schemes.get(schemeName)
        return SelectionWindow.dictBox(scheme, message=schemeName)
    
    @staticmethod
    def importScheme():
        pass

    @staticmethod
    def exportScheme():
        pass


class Export:

    def __init__(self, guids=None):
        """
        Inits a new export Instance. Asks the user to select the export format,
        gets memorized checkbox values for available keys. Presents those 
        to the user to select the keys for export. Stores checkbox states 
        and exports keys to selected output format.

        Args:
            guids (list(str), optional): The objects to export. Asks the user when omitted.
        """
        breps = guids if guids else GetBreps()
        if not breps:
            return
        
        exportMethod = SelectionWindow.show(
                [Rhyton.CSV, Rhyton.JSON],
                message='Select export format:')
        if not exportMethod:
            return
        
        with Layer.hierarchyInformation(breps):
            flag = '.'.join([Rhyton().extensionName, Rhyton.EXPORT_CHECKBOXES])
            selectedKeys = self.getExportKeys(flag, breps)
            if not selectedKeys:
                return

            if exportMethod == Rhyton.CSV:
                self.toCSV(breps, selectedKeys)
            elif exportMethod == Rhyton.JSON:
                self.toJSON(breps, selectedKeys)

    def toCSV(self, guids, keys):
        """
        Exports the values for provided keys to CSV.
        Opens the new file.

        Args:
            guids (list(str)): A list of Rhino object ids.
            keys (list(str)): A list of document user text keys to export.
        """
        data = ElementUserText.get(guids, keys)
        file = CsvExporter.write(data)
        os.startfile(file)

    def toJSON(self, guids, keys):
        """
        Exports the values for provided keys to JSON.
        Opens the new file.

        Args:
            guids (list(str)): A list of Rhino object ids.
            keys (list(str)): A list of document user text keys to export.
        """
        data = ElementUserText.get(guids, keys)
        file = JsonExporter.write(data)
        os.startfile(file)

    @classmethod
    def getExportKeys(cls, flag, guids):
        """
        Presents a checkbox to the user to pick the user text keys for export.
        The checkbox states are stored in the document config storage and
        are used a the default values for the next time the dialog is shown.

        Args:
            flag (str): The identifier for the default values in the document config storage.
            guids (str): A list of Rhino object ids.

        Returns:
            list(str): A list of user text keys.
        """
        keys = sorted(list(ElementUserText.getKeys(guids)))
        options = cls.getCheckboxDefaults(flag, keys=keys)
        selectedOptions = SelectionWindow.showBoxes(options)
        if not selectedOptions:
            return
        
        cls.setCheckboxDefaults(flag, selectedOptions)
        selectedKeys = [key[0] for key in selectedOptions if key[1] == True]
        return selectedKeys

    @staticmethod
    def getCheckboxDefaults(flag, keys=[]):
        """
        Loads export checkbox defaults from the document config storage for given keys.
        If no default is available in the document config storage, <True> will
        be used.

        Args:
            flag (str): The identifier for the default values in the document config storage.
            keys (list(str)): A list of keys to get default values for.

        Returns:
            tuple: A list of tuples indicating the defaults for given values.
        """
        defaults = DocumentConfigStorage().get(flag, dict())
        if keys:
            for key in keys:
                if not key in defaults:
                    defaults[key] = True

            defaults = [(k, v) for k, v in defaults.items() if k in keys]
        else:
            defaults = [(k, v) for k, v in defaults.items()]

        return defaults

    @staticmethod
    def setCheckboxDefaults(flag, newDefaults):
        """
        Updates the document config storage with new export checkbox defaults
        for the current extension.

        Args:
            flag (str): The identifier for the default values in the document config storage.
            defaults (tuple): A list of tuples indicating the default per value.
        """
        defaults = DocumentConfigStorage().get(flag, dict())
        newDefaults = dict((k, v) for k, v in newDefaults)
        defaults.update(newDefaults)
        DocumentConfigStorage().save(flag, defaults)


class Settings(Rhyton):
    """
    Class for handling extension settings.
    """
    def __init__(self, extensionName):
        super(Settings, self).__init__(extensionName)
        """
        Inits a new Settings instance.
        Presents a UI to the user that shows the current settings and
        allows to change them.
        """
        while True:
            res = SelectionWindow.dictBox(
                    options=self.settings, message=self.extensionSettings)
            if not res:
                return

            problem = self.validate(res)
            if not problem:
                break

            SelectionWindow.showWarning(problem)

        self.saveSettings(res)

    @classmethod
    def validate(cls, settings):
        """
        Checks the values the user entered in the settings dialog.

        Args:
            settings (dict): The settings to check.

        Returns:
            str: A message describing the problem, or None when valid.
        """
        try:
            int(settings[cls.ROUNDING_DECIMALS_NAME])
        except (KeyError, TypeError, ValueError):
            return "'{0}' must be a whole number.".format(
                    cls.ROUNDING_DECIMALS_NAME)

        allowed = [cls.QUALITY_CHECK_ASK, cls.QUALITY_CHECK_OFF]
        value = str(settings.get(cls.QUALITY_CHECK_NAME, '')).strip().lower()
        if value not in allowed:
            return "'{0}' must be one of: {1}".format(
                    cls.QUALITY_CHECK_NAME, ', '.join(allowed))

        settings[cls.QUALITY_CHECK_NAME] = value


class SelectionWindow:
    """
    Wrapper class for Rhino user interfaces.
    """
    @staticmethod
    def show(options, message=None):
        """
        Shows a list box to the user that allows to select from a
        list of options.

        Args:
            options (mixed): A list of strings or dict 
                    (shows keys to user, returns value).
            message (str, optional): The message to the user. Defaults to None.

        Returns:
            mixed: The value of the selected key from the input dictionary or the selected item from the input list.
        """
        if not type(options) == dict:
            options = dict((i, i) for i in options)

        res = rs.ListBox(
                sorted(options.keys()),
                message,
                title=Rhyton().extensionName.title(),
                default=options.keys()[0])
        if res:
            return options[res]
        
    @staticmethod
    def showBoxes(options, message=None):
        """
        Shows a checkbox list to the user that allows to select from
        multiple items.

        Example input/output::

            [("option1", True), ("option2", False)]

        The returns are formatted as shown above.

        Args:
            options (list(tuple)): A list of tuples with pre-defined checkbox states
            message (str, optional): The message to the user. Defaults to None.

        Returns:
            list(tuple): A list of tuples indicating the name and state of each checkbox.
        """ 
        return rs.CheckListBox(
                sorted(options),
                message,
                title=Rhyton().extensionName.title())
    
    @staticmethod
    def dictBox(options, message=None):
        """
        Show a dictionary-style list box to the user.

        Args:
            options (dict): The key, value pairs.
            message (str, optional): The message to the user. Defaults to None.
        """
        res = rs.PropertyListBox(
                [Format.value(k) for k in options.keys()],
                options.values(),
                message,
                title=Rhyton().extensionName.title())
        if res:
            return dict((k, v) for k, v in zip(options.keys(), res))
        
    @staticmethod
    def showWarning(message):
        """
        Shows a warning to the user.

        Args:
            message (str): The message to the user.
        """
        rs.MessageBox(message, 48, Rhyton().extensionName.title())

    @staticmethod
    def confirm(message):
        """
        Asks the user to confirm or cancel.

        Args:
            message (str): The message to the user.

        Returns:
            bool: True when the user confirmed.
        """
        return rs.MessageBox(
                message, 4 | 48, Rhyton().extensionName.title()) == 6


class Powerbi:
    """
    Class for opening and updating PowerBI.
    """
    CUSTOM_TEMPLATE = "Load Custom Template"
    POWERBI_TEMPLATE = '.template'
    POWERBI_DATAFILE = Rhyton.HDM_DT_DIR + '/RhinoToolbarExtensions/powerbi.json'
    POWERBI_TEMPLATES_DIR = Rhyton.HDM_DT_DIR + '/RhinoToolbarExtensions/powerbi-templates'
    POWERBI_TEMPLATES_EXTENSION = '.pbit'
    TIMESTAMP = "timestamp"
    # fixed keys are necessary to ensure the powerbi visuals do not break
    VIZ_KEY = "visualization_parameter"

    @classmethod
    def show(cls):
        """
        This method is used to start PowerBI.

        It checks if PowerBI is already running and if not, it opens it.
        The user can select a pre-defined template or load a custom template.
        When a pre-defined template is selected, certain parameters are fixed
        to ensure that the query and visuals in powerbi do not break. 
        The user is asked to select a parameter to visualize which is then 
        renamend to meet the PowerBI template requirements.

        The data is then written to a json file and PowerBI is opened.
        """
        pbiRunning = cls._processExists('PBIDesktop.exe')
        if pbiRunning:
            print("powerbi already running")
            return
        
        template = cls._pickTemplate()
        if not template:
            return
        
        config = dict()
        config[cls.POWERBI_TEMPLATE] = template
        if template == cls.CUSTOM_TEMPLATE:
            template = GetFilePath(cls.POWERBI_TEMPLATES_EXTENSION)
            breps = GetBreps()
            if not breps:
                return
        
            data = cls._getData(breps)
            if not data:
                return
        else:
            breps = GetBreps()
            if not breps:
                return
        
            allKeys = ElementUserText.getKeys(breps)
            if not allKeys:
                SelectionWindow.showWarning('No user text found on selected objects.')
                return
        
            vizKey = SelectionWindow.show(
                    allKeys, message="Select Parameter to Visualize:")
            config[cls.VIZ_KEY] = vizKey
            fixedKeys = cls.fixedKeys()
            fixedKeys.append(vizKey)
            data = cls._getData(breps, fixedKeys=fixedKeys, vizKey=vizKey)
            if not data:
                return

        templateFlag = ''.join([
                Rhyton().extensionName,
                Rhyton.POWERBI,
                cls.POWERBI_TEMPLATE])
        DocumentConfigStorage().save(templateFlag, config)

        JsonExporter.write(data, file=cls.POWERBI_DATAFILE)
        os.startfile(template)
        
    @classmethod
    def update(cls):
        """
        This method is used to update PowerBI.
        It gets the current PowerBI template and chooses the correct method for
        updating the data.
        
        The data is then written to a json file and PowerBI is opened.
        """
        templateFlag = ''.join([
                Rhyton().extensionName,
                Rhyton.POWERBI,
                cls.POWERBI_TEMPLATE])
        config = DocumentConfigStorage().get(templateFlag)
        if config[cls.POWERBI_TEMPLATE] == cls.CUSTOM_TEMPLATE:
            breps = GetBreps()
            if not breps:
                return
        
            data = cls._getData(breps)
            if not data:
                return
        else:
            breps = GetBreps()
            if not breps:
                return
        
            vizKey = config.get(cls.VIZ_KEY)
            fixedKeys = cls.fixedKeys()
            fixedKeys.append(vizKey)
            data = cls._getData(breps, fixedKeys=fixedKeys, vizKey=vizKey)
            if not data:
                return
            
        JsonExporter.append(data, cls.POWERBI_DATAFILE)

    @classmethod
    def _pickTemplate(cls):
        """
        This method is used to pick a PowerBI template.
        It checks if the PowerBI template directory exists. If not, it is created.
        It then searches for all files with the extension ``.pbit`` and adds them
        to a list of templates. The user is then asked to select a template.
        The seleceted templates is returned.
        """   
        if not os.path.exists(cls.POWERBI_TEMPLATES_DIR):
            os.makedirs(cls.POWERBI_TEMPLATES_DIR)

        files = cls.absoluteFilePaths(cls.POWERBI_TEMPLATES_DIR)
        templates = [os.path.abspath(f) for f in files if f.endswith(cls.POWERBI_TEMPLATES_EXTENSION)]
        templateNames = [os.path.basename(t).replace(cls.POWERBI_TEMPLATES_EXTENSION, '') for t in templates]
        options = dict((k, v) for k, v in zip(templateNames, templates))
        options[cls.CUSTOM_TEMPLATE] = cls.CUSTOM_TEMPLATE
        return SelectionWindow.show(options, message="Pick PowerBI Template:")

    @classmethod
    def _getData(cls, guids, fixedKeys=[], vizKey=None):
        """
        This method is used to get the data for PowerBI.
        It temporarily adds layer information to the object user text.
        If no fixed keys are provided, the user is asked to select the keys
        for export. It then gets the data for the selected keys.
        The data for the visualization parameter is renamed to meet the PowerBI
        template requirements. All extension prefixes are removed from the keys.

        Args:
            guids (list(str)): A list of Rhino objects ids.
            fixedKeys (list, optional): A list of keys that need to be exported. 
            Defaults to [].
            vizKey (str, optional): The key of the data used for visualization. 
            Defaults to None.

        Returns:
            dict: The data for PowerBI.
        """
        with Layer.hierarchyInformation(guids):
            flag = '.'.join([Rhyton().extensionPowerbi, Rhyton.EXPORT_CHECKBOXES])
            if fixedKeys:
                selectedKeys = fixedKeys
            else:
                selectedKeys = Export.getExportKeys(flag, guids)
                if not selectedKeys:
                    return

            data = ElementUserText.get(guids, selectedKeys)

        timeStamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        prefix = Rhyton().extensionName + Rhyton.DELIMITER
        for d in data:
            if vizKey and vizKey in d:
                d[cls.VIZ_KEY] = d.pop(vizKey)

            for key in d.keys():
                if Rhyton().extensionName in key:
                    keyNew = key.replace(prefix, '')
                    d[keyNew] = d.pop(key)
            d[cls.TIMESTAMP] = timeStamp

        return data
    
    @staticmethod
    def _processExists(processName):
        """
        This method is used to check if a process is running or not.

        Args:
            processName (str): The name of the process.

        Returns:
            bool: True if the process is running, False otherwise.
        """
        import subprocess
        # checks if a process is running or not
        call = 'TASKLIST', '/FI', 'imagename eq %s' % processName
        # use buildin check_output right away
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(call).decode()
        # check in last line for process name
        lastLine = output.strip().split('\r\n')[-1]
        # because Fail message could be translated
        return lastLine.lower().startswith(processName.lower())
    
    @staticmethod
    def absoluteFilePaths(directory):
        """
        This method is used to get all absolute file paths in a directory.

        Args:
            directory (str): The directory to search.

        Yields:
            list(str): The absolute file paths.
        """
        for dirpath,_,filenames in os.walk(directory):
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))

    @staticmethod
    def fixedKeys():
        """
        Generates fixed keys when needed. This cannot be done as a
        class variable because the extension name might change.

        Yields:
            list(str): The fixed keys.
        """
        name = Rhyton().extensionName
        return [
            Rhyton.DELIMITER.join([name, Rhyton.LAYER_HIERARCHY, Rhyton.NAME]),
            Rhyton.DELIMITER.join([name, Rhyton.LAYER_HIERARCHY, "1"]),
            Rhyton.DELIMITER.join([name, Rhyton.LAYER_HIERARCHY, "2"]),
            Rhyton.DELIMITER.join([name, Rhyton.LAYER_HIERARCHY, "3"])]
    

class ProgressBar():
    """
    This class is used to create and update a progress bar.
    """
    def __init__(self, upper, label="Calculating...", lower=1):
        """
        The constructor for the ProgressBar class.

        Args:
            upper (int): The upper limit of the progress bar.
            label (str, optional): The text to display in the progress bar. Defaults to "Calculating...".
            lower (int, optional): the lower limit of the progress bar. Defaults to 1.
        """
        self.upper = upper
        self.label = label
        self.lower = lower
        self.position = 0
        
    def __enter__(self):
        """
        This method is used to show the progress bar.

        Returns:
            object: The progress bar object.
        """
        rs.StatusBarProgressMeterShow(
                self.label, self.lower, self.upper, embed_label=True, show_percent=True)
        return self.__class__(self.upper)
    
    def __exit__(self, exc_type, exc_val, traceback):
        """
        This method is used to hide the progress bar.

        Args:
            exc_type (_type_): _description_
            exc_val (_type_): _description_
            traceback (_type_): _description_
        """
        rs.StatusBarProgressMeterHide()

    def update(self):
        """
        This method is used to update the progress bar.
        The poistions is automatically incremented by 1 
        each time the method is called.
        """
        self.position += 1
        rs.StatusBarProgressMeterUpdate(self.position, absolute=True)
