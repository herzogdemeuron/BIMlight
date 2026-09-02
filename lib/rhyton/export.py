"""
Module for exporting data to various formats.
"""
# python standard imports
import os
import csv
import json
from datetime import datetime

# rhyton imports
from rhyton.main import Rhyton


class ExportBase:
    """
    Base class for all exporters.
    """
    @staticmethod
    def prepFile(file, extension):
        """
        Prepares the file path for writing.

        Args:
            file (str): The file path.
            extension (str): The file extension.

        Returns:
            str: The file path.
        """
        if not file:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file = '{}/{}.{}'.format(Rhyton.HDM_DT_DIR, now, extension.lower())

        directory = os.path.dirname(file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        return file
    
class CsvExporter(ExportBase):
    """
    Exports data to a csv file.
    """
    @classmethod
    def write(cls, data, file=None):
        """
        Writes data to a csv file.

        Args:
            data (dict): The data to write.
            file (str, optional): The file path. Defaults to None.

        Returns:
            str: The file path.
        """
        import itertools
        file = cls.prepFile(file, 'csv')
        keys = [d.keys() for d in data]
        headers = sorted(list(set(itertools.chain.from_iterable(keys))))

        with open(file, 'wb') as f:
            writer = csv.DictWriter(
                    f,
                    fieldnames=headers,
                    extrasaction='ignore',
                    dialect='excel',
                    delimiter=cls.getListseperator())
            writer.writeheader()
            writer.writerows(data)
        
        return file

    @staticmethod
    def getListseperator():
        """
        Returns the list seperator for the current locale.
        """
        import _winreg
        key = _winreg.OpenKey(
                _winreg.HKEY_CURRENT_USER,
                r"Control Panel\International")
        return _winreg.QueryValueEx(key, "sList")[0]


class JsonExporter(ExportBase):
    """
    Exports data to a json file.
    """
    @classmethod
    def write(cls, data, file=None):
        """
        Writes data to a json file.

        Args:
            data (dict): The data to write.
            file (str, optional): The file path. Defaults to None.

        Returns:
            str: The file path.
        """
        file = cls.prepFile(file, 'json')
        with open(file, 'w') as f:
            f.write(json.dumps(data, encoding="utf-8", ensure_ascii=False))

        return file

    @staticmethod
    def append(data, file):
        """
        Appends data to a json file.

        Args:
            data (dict): The data to append.
            file (str): The file path.

        Returns:
            str: The file path.
        """
        with open(file, 'r') as f:
            existingData = json.load(f)
        if existingData:
            existingData = existingData + data
            with open(file, 'w') as f:
                f.write(json.dumps(
                        existingData, encoding="utf-8", ensure_ascii=False))

        return file
    
