"""
Post-install step, run by the DT standard tools installer after every pull.

Removes the standalone rhyton install that BIMlight used to depend on. Both
copies would otherwise compete for the 'rhyton' name on the Rhino python
search path, and which one wins is not predictable.
"""
import os
import shutil

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_RHYTON = os.path.join(REPO_DIR, 'lib', 'rhyton')
OBSOLETE_RHYTON = os.path.join(os.path.dirname(REPO_DIR), 'rhyton')


def removeObsoleteRhyton():
    """
    Deletes the old standalone rhyton folder, but only once the bundled copy
    is confirmed present, so a failed BIMlight update cannot leave a machine
    without a core library at all.
    """
    if not os.path.isdir(BUNDLED_RHYTON):
        print("BIMlight: bundled rhyton not found, leaving '{0}' alone.".format(
                OBSOLETE_RHYTON))
        return

    if not os.path.isdir(OBSOLETE_RHYTON):
        return

    try:
        shutil.rmtree(OBSOLETE_RHYTON)
        print("BIMlight: removed obsolete rhyton install '{0}'.".format(
                OBSOLETE_RHYTON))
    except Exception as error:
        # a locked folder is retried on the next update, so this is not fatal
        print("BIMlight: could not remove '{0}': {1}".format(
                OBSOLETE_RHYTON, error))


if __name__ == '__main__':
    removeObsoleteRhyton()
