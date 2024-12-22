# Description

This is an application that comapres two directory images and lists what files and directories were deleted or added in an easily navigatable fashion. 
A directory image is a snapshots of the directory or drive which stores the tree structure of the filenames into a single .json file.

# To use
To use the application, download the latest release/zip, unzip it.
Execute the `.exe` to run it

1. Click "create new image" to create snapshot of a directory then save the output `.json` file in any directory.

![image](https://github.com/user-attachments/assets/1b6f313f-ab6c-414c-a46f-c0c552af13e9)

2. At a later date, open the application and click `Load Old Image` -> `Select File` -> select the `.json` file

![image](https://github.com/user-attachments/assets/8627bb16-aa0f-4d57-bdee-3e4ce9a29397)

3. Select `Load New Image` -> `Select Folder` -> pick the folder to compare against the `.json`

Finally, you will see all the differences (and similarities) between the old snapshot in the `.json` file and the live contents of the directory. (Or you can compare past two `.json` files if you want, or for some reason two live directories if you want)

![image](https://github.com/user-attachments/assets/eef76619-f50b-4ced-b0b9-f93d2f6276b8)


Additionally, settings can be changed to compare or ignore Size and Modification Time:

![image](https://github.com/user-attachments/assets/de960c6e-93b7-4853-936c-5b4223b6e63d)


# Build

To build the exe:

First create a conda env: `conda create --name myenv python=3.11`
If already created env: `conda activate myenv`
Then:
`pyinstaller    --onefile --noconsole --windowed --icon=clocks.ico --name directory_compare compare_gui.py`
