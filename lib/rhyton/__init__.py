"""
Rhyton is a core library for Rhino that you can use to develop your data-centric 
Rhino extensions with.

Focus Areas
-----------

Rhyton's code base is focusses around these topics:

1. Object User Text
2. Document User Text
3. Object Color 'Overrides' / Data Visualization
4. Exporting Object User Text

Data Concept
------------

Since rhyton is a data focussed package, it handles Rhino objects internally as
dictionaries::

    {"guid": <guid>,"'key1": <value1>, "key2", <value2>}

To be more efficient, most functions also take a list of guid's that 
share the same keys and values::

    {"guid": [<guid1>, <guid2>],"'key1": <value1>, "key2", <value2>}

Extensions
----------

Rhyton is inteded to be uses as the basis for other topic-specific extensions.
The ``Rhyton`` class is used as a common base class to share information
across the package. This allows you to separate settings and variables for multiple extensions.

Set extension specific settings::

    rhyton.Settings('bimlight')

Use those settings::

    rhyton.Rhyton('bimlight')
    rhyton.Visualize.byValue()


Coding Style Guide
------------------

    1. 'camelCase' function and variable names.
    2. Title 'CamelCase' class names.
    3. Class names and functions are designed for reading flow::

        rhyton.Visualize.byGroup()
        rhyton.Export.toCSV()

    4. " (double quotes) for text that is presented to the user.
    5. ' (single quotes) for internal stings.
    6. Functions in ui.py should not take arguments to keep out clutter.
    7. The Rhyton('extension_name') class instance is meant to be the **only configurable** point of entry.
    8. **All** modules, classes and function must have extensive docstrings
    9. Keep in-line comments to a minimum.
    
"""
# rhyton imports
from rhyton.ui import *
from rhyton.color import *
from rhyton.document import *
from rhyton.export import *
from rhyton.utils import *