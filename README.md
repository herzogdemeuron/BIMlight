# BIMlight
*Simple BIM tools for Rhino*

## Installation Guide

### Prerequisites
- Rhino installed
- Git for cloning repositories

### Installation Steps

1. **Clone Repositories**
   Clone this repo and [Rhyton](https://github.com/herzogdemeuron/rhyton) into `C:\HdM-DT\RhinoToolbarExtensions\`. This specific path is required for the toolbar buttons to function correctly.

2. **Configure Python Paths**
   - Open Rhino
   - Run the command: `EditPythonScript`
   - In the Rhino Python Editor, go to `Tools > Options...`
   - Add the following paths:
     - `C:\HdM-DT\RhinoToolbarExtensions\BIMlight\lib\`
     - `C:\HdM-DT\RhinoToolbarExtensions\rhyton\lib\`

3. **Install Toolbar**
   - Run the command: `Toolbar`
   - Open the BIMlight toolbar file:
     `C:\HdM-DT\RhinoToolbarExtensions\BIMlight\toolbar\BIMlight.rui`

### Ready to Use!

### Update
- To update, pull the latest changes from the **BIMlight** and **rhyton** repositories into their respective paths under  
  `C:\HdM-DT\RhinoToolbarExtensions\BIMlight` and  
  `C:\HdM-DT\RhinoToolbarExtensions\rhyton`.
