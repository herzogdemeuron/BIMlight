import calculate
import variablesbl
from variablesbl import *


class Log():
    def __init__(self, message, extension=variablesbl.BIMLIGHT):
        """
        Logs a message to a file.

        Args:
            message (str): The message to log.
        """
        import os
        import re
        import logging
        import Rhino
        from datetime import datetime

        month = str(datetime.now().month)
        year = str(datetime.now().year)
        filePath = os.path.join('C:\\HdM-DT', '_'.join([year, month, 'HdMRhino_toolbar.log']))

        doc_path = str(Rhino.RhinoDoc.ActiveDoc.Path).replace(" ", '_')
        doc_path = doc_path.replace('\\', '/')
        # try to take out usernames
        doc_path = re.sub(r'/[a-z][._][a-z]*/', '/xxx/', doc_path, flags=re.IGNORECASE)
        doc_path = re.sub(r'/[a-z]*[._][a-z]/', '/xxx/', doc_path, flags=re.IGNORECASE)
        message = message.replace(" ", '_')
        extension = extension.replace(" ", '_')

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler = logging.FileHandler(filePath)        
        handler.setFormatter(formatter)

        logger = logging.getLogger('HdMRhinoToolbar')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        logger.info(' '.join([message, extension, doc_path]))
