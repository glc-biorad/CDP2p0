# CDP2p0
Full repository for the CDP 2.0 units, including FW binaries, instrument API, chassis controller API, and the development GUI

Version Description cdp2p0.X.Y.Z.py:
 - X: Major (significant) changes
 - Y: Minor changes (small feature or set of small features)
 - Z: Patch (bug fixes)

To-Do List:
- continue adding functionality to the image tab
  - continuous imaging 
  - save view
  - load view
  - image model table for led channel numbers, filter locations, base intensities
  - image model table for focal plane for each unit
  - setup bindings for tray a,b,c,d for starting scan of chip
- use the Tip Use table (tip_use_model) to keep track of what tips are in what column of the tip boxes and what tip is currently where (need config tab)
- add the pre-amp thermocycler to the thermocycle portion of the gui
- allow users to start from selected row in action treeview with a yesno messagebox popup on start
