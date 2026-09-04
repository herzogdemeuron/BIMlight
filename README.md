# BIMlight
*Simple BIM tools for Rhino*

## Installation Guide

On HdM machines BIMlight is installed and kept up to date by **DT Update**. The steps below are only needed for a manual install.

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

The `rhyton` core library now lives in this repository under `lib\rhyton\` and is no longer installed separately. `install.py` removes the old `C:\HdM-DT\RhinoToolbarExtensions\rhyton` folder automatically on the next update.

If you installed manually, delete that folder yourself. Leaving it in place means Rhino may load the old library instead of the bundled one; BIMlight raises a clear error on startup when that happens. A leftover search path entry pointing at the deleted folder is harmless.

### Update
- To update, pull the latest changes from this repository into  
  `C:\HdM-DT\RhinoToolbarExtensions\BIMlight`.

### Behaviour changes

- **User text values are stored verbatim.** Earlier versions silently converted values to Title Case and replaced underscores with spaces on write. Existing values are not rewritten.
- **Layer names are exported exactly as they are in Rhino.** Nothing is reformatted, and layer names are never interpreted as numbers, so `01` stays `01`. Other user text that looks like a number is still read as one so it can be summed, but values with a leading zero (`007`) keep their spelling.
- **Export can run a quality check.** Before exporting, BIMlight offers to recalculate areas and volumes and compare them against the stored values. Objects whose values differ are selected so you can inspect them, and you can always export anyway. Controlled by the `Ask QC before export` setting (`Yes` by default).
- **Blocks can be included.** Block instances are treated as regular objects for visualisation, export and PowerBI. Controlled by the `Include blocks` setting (`No` by default). Area and volume calculations always skip blocks, because those values cannot be derived from a block instance.
- **Skipped objects are reported.** Selecting objects that a command cannot handle no longer fails silently; BIMlight says how many were skipped and why.

## Structure

| Path | Contents |
| --- | --- |
| `lib\bimlight\` | The BIM specific commands: calculations, quality check, logging. |
| `lib\rhyton\` | The core library: object user text, document storage, colours, visualisation, export. |
| `toolbar\` | The Rhino toolbars and the script each button runs. |

## History

BIMlight began as part of the internal HdM Rhino toolbar. It was extracted into this repository and open sourced on GitHub in 2023, so **the commit history of this repository starts there** — everything before that was developed internally and is recorded below.

| Year | Milestone | Contributors |
| --- | --- | --- |
| 2020 | Concept and first release | [@julianKD](https://github.com/julianKD) |
| 2021–2022 | Feature development and refinement | [@yschindel](https://github.com/yschindel), [@julianKD](https://github.com/julianKD) |
| 2023 | Rewritten on a new reusable core library, `rhyton`, and open sourced on GitHub | [@yschindel](https://github.com/yschindel) |

