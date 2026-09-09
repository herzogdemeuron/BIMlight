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

The `rhyton` core library is bundled in this repository under `lib\rhyton\`. If an older standalone `rhyton` folder still sits under `C:\HdM-DT\RhinoToolbarExtensions\`, Rhino may load it instead of the bundled library; BIMlight raises a clear error when that happens, so remove the old folder. **DT Update** does this automatically. Close Rhino before updating so it does not keep the old library loaded in memory. The existing BIMlight Python search path remains valid.

### Export files

Default CSV/JSON exports are written to `C:\temp\BIMlight\`, created when needed. Power BI uses `C:\temp\BIMlight\powerbi.json`. The folder sits outside the repository so reinstalling BIMlight cannot delete it.

**Start Power BI** offers the templates from both locations in one list: the generic template bundled in `powerbi-templates\`, and the HdM internal templates from `C:\HdM-DT\RhinoToolbarExtensions\powerbi-templates\`. Either location is skipped without a warning when it is not installed or holds no templates, so the command works with one, both or neither. All templates read `C:\temp\BIMlight\powerbi.json`.

### Update
- To update, pull the latest changes from this repository into  
  `C:\HdM-DT\RhinoToolbarExtensions\BIMlight`.

## Behaviour

- **User text values are stored verbatim.** No reformatting is applied on write.
- **Layer names are exported exactly as they are in Rhino** and are never interpreted as numbers, so `01` stays `01`. Other user text that looks like a number is read as one so it can be summed, but values with a leading zero (`007`) keep their spelling.
- **Export can run a quality check.** Before exporting, BIMlight offers to recalculate areas and volumes and compare them against the stored values. Objects whose values differ are selected so you can inspect them, and you can always export anyway. Controlled by the `Ask QC before export` setting (`Yes` by default).
- **Blocks can be included.** Block instances are treated as regular objects for visualisation, export and Power BI. Controlled by the `Include blocks` setting (`No` by default). Area and volume calculations always skip blocks, because those values cannot be derived from a block instance.
- **Skipped objects are reported.** Selecting objects that a command cannot handle does not fail silently; BIMlight says how many were skipped and why.

## Structure

| Path | Contents |
| --- | --- |
| `lib\bimlight\` | The BIM specific commands: calculations, quality check, logging. |
| `lib\rhyton\` | The core library: object user text, document storage, colours, visualisation, export. |
| `toolbar\` | The Rhino toolbars and the script each button runs. |
| `powerbi-templates\` | The generic Power BI report template. |

## History

BIMlight began as part of the internal HdM Rhino toolbar, developed in close collaboration between DT and project teams. It was extracted into this repository in 2023, so **the commit history of this repository starts there** — everything before that was developed internally and is recorded below.

| Year | Milestone | Contributors |
| --- | --- | --- |
| 2020 | Initial concept and first release | [@julianKD](https://github.com/julianKD) |
| 2021–2022 | Feature development and refinement | [@yschindel](https://github.com/yschindel) and [@julianKD](https://github.com/julianKD) |
| 2023 | Rewritten on a new reusable core library, `rhyton` | [@yschindel](https://github.com/yschindel) |

