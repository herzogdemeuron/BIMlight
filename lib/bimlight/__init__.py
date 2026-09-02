import os


def _assertVendoredRhyton():
    """
    Fails loudly when an old standalone rhyton search path shadows the copy
    that ships inside this repository.
    """
    import rhyton

    libDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    expected = os.path.normcase(os.path.join(libDir, 'rhyton'))
    loaded = os.path.normcase(os.path.dirname(os.path.abspath(rhyton.__file__)))
    if loaded != expected:
        raise ImportError(
                "BIMlight loaded rhyton from '{0}' instead of '{1}'.\n"
                "Remove the old rhyton entry from the Rhino Python search paths "
                "(EditPythonScript > Tools > Options) and restart Rhino.".format(
                        loaded, expected))


# runs before the submodules so a shadowed rhyton is reported, not stumbled over
_assertVendoredRhyton()

import calculate
import quality
import variablesbl
from variablesbl import *


def exportUserData():
    """
    Exports object user text, offering the quality check first.
    The full selection is exported even when only part of it was flagged.
    """
    import rhyton

    guids = rhyton.GetBreps()
    if not guids:
        return

    if not quality.gate(guids):
        return

    rhyton.Export(guids=guids)


_logger = None


def _getLogger():
    """
    Returns the shared logger, attaching its file handler only once per session.
    """
    global _logger
    if _logger is not None:
        return _logger

    import logging
    from datetime import datetime

    now = datetime.now()
    filePath = os.path.join(
            'C:\\HdM-DT',
            '_'.join([str(now.year), str(now.month), 'HdMRhino_toolbar.log']))

    handler = logging.FileHandler(filePath)
    handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    logger = logging.getLogger('HdMRhinoToolbar')
    logger.setLevel(logging.DEBUG)
    logger.handlers = [handler]
    _logger = logger
    return _logger


def Log(message, extension=variablesbl.BIMLIGHT):
    """
    Logs toolbar usage. Never interrupts the command that called it.

    Args:
        message (str): The message to log.
        extension (str, optional): The extension the message belongs to.
    """
    import re
    import Rhino

    try:
        documentPath = str(Rhino.RhinoDoc.ActiveDoc.Path).replace(" ", '_')
        documentPath = documentPath.replace('\\', '/')
        # try to take out usernames
        documentPath = re.sub(
                r'/[a-z][._][a-z]*/', '/xxx/', documentPath, flags=re.IGNORECASE)
        documentPath = re.sub(
                r'/[a-z]*[._][a-z]/', '/xxx/', documentPath, flags=re.IGNORECASE)

        _getLogger().info(' '.join([
                message.replace(" ", '_'),
                extension.replace(" ", '_').lower().title(),
                documentPath]))
    except Exception:
        pass
