# Description

This is an application that comapres two directory images and lists what files and directories were deleted or added in an easily navigatable fashion. 
A directory image is a snapshots of the directory or drive which stores the tree structure of the filenames into a single .json file.

# Example

![image](https://github.com/user-attachments/assets/ea58c18c-7aca-4df9-8cc7-e97ad29c3371)

The first example shows a comparison to the directory of a game before and after an update. We can see that no top-level files were edited but there are two directories that contain differences (one where 7 files were replaced with 2 files and another where 16 files were replaced with 17 files).

![image](https://github.com/user-attachments/assets/fca27bc0-ee9b-47a4-9d98-b855a1f8bd35)

The second example shows the comparison inside one of the directory's. We can see that all of the subdirectory contants are the same and only in the current directory files do we have a difference where 7 files were deleted and 2 new files were added during the update. (we are ignoring "size" and "modification time" in the settings menu for this example).

This application was particularly useful when having a very nested and duplicate directory on two different harddrives and I needed to quickly compare which files were added to the new version.

# To use

## Install

### Windows

To use the application on windows with no programming knowledge, simply download the latest release/zip, unzip it.
Execute the `.exe` to run it. The `.exe` is not signed so your antivirus might block it.

### Other platforms

If you want to run the application on other platforms (or want to avoid running `.exe`s on windows) then simply clone this project and execute `python compare_gui.py` after installing the conda environment (go to [build section](https://github.com/Ar-Kareem/dir_diff?tab=readme-ov-file#build))

## Steps

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

First create a local conda env: `conda create -p ./env python=3.11`

If already created env: `conda activate ./env`

Then:
`pyinstaller    --onefile --noconsole --windowed --icon=clocks.ico --name directory_compare compare_gui.py`
