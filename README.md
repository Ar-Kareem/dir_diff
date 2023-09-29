# Description

This is an application that comapres two directory images and lists what files and directories were deleted or added in an easily navigatable fashion. 
A directory image is a snapshots of the directory or drive which stores the tree structure of the filenames into a single .json file.

# Build

To build:

To create a conda env: `conda create --name myenv python=3.11`
Already created env: `conda activate myenv`
Then:
`pyinstaller    --onefile --noconsole --windowed --icon=clocks.ico --name directory_compare compare_gui.py`

# To use
To use the application, download the latest release/zip, unzip it, and edit the settings.json to do what you want (e.g. click on specific pictures and/or automate mouse keyboard with specific macros).
Execute the `.exe` to run it. A black window will appear with current program info (the same info is dumped into the `main.log` file)
