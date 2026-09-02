# BIMlight
*Simple BIM tools for Rhino*

## Installation Guide

### Prerequisites
- Rhino installed
- Git for cloning repositories

### Installation Steps

1. **Clone Repository**
   Clone this repo into `C:\HdM-DT\RhinoToolbarExtensions\`. This specific path is required for the toolbar buttons to function correctly.

2. **Configure Python Path**
   - Open Rhino
   - Run the command: `EditPythonScript`
   - In the Rhino Python Editor, go to `Tools > Options...`
   - Add the following path:
     - `C:\HdM-DT\RhinoToolbarExtensions\BIMlight\lib\`

3. **Install Toolbar**
   - Run the command: `Toolbar`
   - Open the toolbar file for your Rhino version:
     - Rhino 8: `C:\HdM-DT\RhinoToolbarExtensions\BIMlight\toolbar\BIMlight-R8.rui`
     - Rhino 7: `C:\HdM-DT\RhinoToolbarExtensions\BIMlight\toolbar\BIMlight.rui`

### Ready to Use!

### Upgrading from a previous install

[Rhyton](https://github.com/herzogdemeuron/rhyton) now ships inside this repository under `lib\rhyton\`. If you installed BIMlight before this change:

- **Remove** the old `C:\HdM-DT\RhinoToolbarExtensions\rhyton\lib\` entry from the Rhino Python search paths. If it is left in place it may shadow the bundled copy. BIMlight raises a clear error on startup when this happens.
- The separate `rhyton` clone is no longer needed.

### Update
- To update, pull the latest changes from this repository into  
  `C:\HdM-DT\RhinoToolbarExtensions\BIMlight`.

### Behaviour changes

- **User text values are stored verbatim.** Earlier versions silently converted values to Title Case and replaced underscores with spaces on write. Existing values are not rewritten.
- **Export can run a quality check.** Before exporting, BIMlight offers to recalculate areas and volumes and compare them against the stored values. Objects whose values differ are selected so you can inspect them, and you can always export anyway. Controlled by the `Ask QC before export` setting (`Yes` by default).
- **Blocks can be included.** Block instances are treated as regular objects for visualisation, export and PowerBI. Controlled by the `Include blocks` setting (`No` by default). Area and volume calculations always skip blocks, because those values cannot be derived from a block instance.
- **Skipped objects are reported.** Selecting objects that a command cannot handle no longer fails silently; BIMlight says how many were skipped and why.

## Bundled dependencies

`lib\rhyton\` is vendored from [herzogdemeuron/rhyton](https://github.com/herzogdemeuron/rhyton) at commit `ee02e56`.

