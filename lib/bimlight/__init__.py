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
        filePath = os.path.join(baseDir, '_'.join([year, month, 'BIMlight.log']))

        logging.basicConfig(filename=filePath,
                            level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s')
    
        doc_path = str(Rhino.RhinoDoc.ActiveDoc.Path).replace(" ", '_')
        message = message.replace(" ", '_')

        logging.info(' '.join([message, doc_path]))

