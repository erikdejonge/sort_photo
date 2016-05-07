Dropbox Importer
================

I like the the way Dropbox renamed images and videos when importing them using Photo Upload feature, i.e. according to the metadata creation date/time.
As Photo Upload is not available in Dropbox for Linux, and I wanted my files to be consistently named whichever system I use to upload files to Dropbox, I wrote this small utility.

Depends on ``PIL`` and ``enzyme`` packages for metadata extraction, and PySide/PyQt4 for GUI.
There is also an older version with wxPython GUI, but it lacks some features.

Features:

* Copy files to specified folder (empty means copy in place)
* Rename files according to date/time in metadata

  - Falls back to file creation timestamp if no or erroneous metadata is present.
  
* When copying put files in folders according to date from metadata
* Shift the time used to name the files.
  
  - As mp4 headers contain UTC timestamps and no time zone info,
    program first automatically applies time conversion to timezone local to
    the PC runniing the file, and then applies the shift if user asked for it.
  - Program does not understand video files with timestamps before epoch.
  
* Drag and Drop files to the files panel, or start the script with files as arguments.
