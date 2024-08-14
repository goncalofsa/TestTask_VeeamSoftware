To run the script that synchronizes two folders, source and replica, and maintain a full, identical copy of source folder at replica folder, navigate on the terminal to the path inside the folder that contains the script and both folders and execute the following command line:


"""
python sync_folders.py source_folder replica_folder 1 logfile.log
"""

This way, all the files inside the source folder will be automatically updated with creation, copying and removal operations to the replica folder with 1 second of interval and all the steps will be written in the logfile file.