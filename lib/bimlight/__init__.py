import calculate
import export
import powerbi
import settings
import utilsbl
import variablesbl
import visualize
import grouping


class Log():
    def __init__(self, message):
        import logging
        import os
        import Rhino
        from datetime import datetime

        currentFile = os.path.abspath(__file__)
        baseDir = os.path.dirname(currentFile)
    
        month = str(datetime.now().month)
        year = str(datetime.now().year)
        filePath = os.path.join(baseDir, '_'.join([year, month, 'BIMlight_toolbar.log']))

        doc_path = str(Rhino.RhinoDoc.ActiveDoc.Path).replace(" ", '_')
        message = message.replace(" ", '_')

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler = logging.FileHandler(filePath)        
        handler.setFormatter(formatter)

        logger = logging.getLogger('BIMlight')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        logger.info(' '.join([message, doc_path]))
