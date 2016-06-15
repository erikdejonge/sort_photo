#!/usr/bin/env python
"""Rename files like Dropbox Camera Upload feature does.

"""
#TODO: time shift for video files, maybe optional for images too
from __future__ import division, print_function
import datetime
import os
import shutil

from PIL import Image
from PIL import ExifTags
import enzyme

DATEEXIFKEY = [key for (key, value) in ExifTags.TAGS.items()
               if value == 'DateTimeOriginal'][0]
FILEFMT = "%Y-%m-%d %H.%M.%S"
DIRFMT = "%Y-%m-%d"

VIDEOFILES = ['.mp4', '.3gp', '.mov', '.mkv', '.webm', '.avi', '.ogm', '.ogv']
IMAGEFILES = ['.jpg', '.jpeg']


def import_file(filename, targetdir='',
                filefmt=FILEFMT, dirfmt=DIRFMT,
                shift_seconds=0, shift_img=False, shift_vid=True,
                sort_in_dir=False, rename=True):
    """Rename file according to metadata date/time.

    Puts files into target dir, creating optional subdirs.
    Formats for both filename and subdirs are the same used by ``strftime``.

    """
    dir, name = os.path.split(filename)
    basename, fileext = os.path.splitext(name)
    if targetdir == '':
        targetdir = dir
    filetime = get_time(filename, shift_seconds, shift_img, shift_vid)

    if filetime:
        if rename:
            datetimestring = filetime.strftime(filefmt)
            name = datetimestring + fileext
        if sort_in_dir:
            datestring = filetime.strftime(dirfmt)

            targetdir = os.path.join(targetdir, datestring)
            if not os.path.isdir(targetdir):
                try:
                    os.makedirs(targetdir)
                except:
                    print("Could not create dir {0}".format(targetdir))
                    return filename
        newfilename = os.path.join(targetdir, name)
        print(newfilename)
        if os.path.exists(newfilename):
            return filename+" skipped"
        try:
            os.rename(filename, newfilename.replace('JPG', 'jpg').replace('PNG', 'png').replace('MOV', 'mov'))
        except IOError as err:
            return filename+" error "+str(err)
        else:
            return filename+" ok"
    else:
        return filename


def get_time(filename, shift_seconds=0, shift_img=False, shift_vid=False):
    """Get file date, from metadata or file system.

    Time is optionally shifted by given amount of seconds.
    Wether to shift for images or videos is decided separately.

    """
    ext = os.path.splitext(filename)[1]
    if ext.lower() in IMAGEFILES:
        filedt = get_exif_time(filename)
        if shift_img:
            filedt = shift_time(filedt, shift_seconds)
    elif ext.lower() in VIDEOFILES:

        filedt = get_video_time(filename)
        if shift_vid:
            filedt = shift_time(filedt, shift_seconds)
    else:
        filedt = get_file_time(filename)
    return filedt


def shift_time(dt, shift_seconds):
    return dt + datetime.timedelta(seconds=shift_seconds)


def get_exif_time(filename):
    """Get time from EXIF metadata using ``PIL`` or ``Pillow`` package."""
    img = Image.open(filename)
    exf = img._getexif()
    if exf:

        timestr = exf.get(DATEEXIFKEY, None)

        if timestr:

            return datetime.datetime.strptime(timestr, "%Y:%m:%d %H:%M:%S")
        else:
            return get_file_time(filename)
    else:

        return get_file_time(filename)


def get_video_time(filename):
    """Get file data from video metadata using ``enzyme`` package.

    This one is tricky, as
    (at least in the MP4 headers of files shot with cell phones)
    the time is stored as seconds since epoch **in UTC**.
    Thus the information on the timezone where the shot happened is needed.
    For now, it is assumed that it is the same timezone as the system
    currently running this code.
    Also, as I've met cell phones that put
    very erroneous capture file time in the header,
    I have restricted the recognized capture time to *after* the epoch.

    """
    try:

        with open(filename, 'rb') as f:
            mdata = enzyme.MKV(f)

    except:
        return get_file_time(filename)
    tmepoch = mdata.timestamp
    # here is the place where too old (erroneous) date is not supported
    if tmepoch and tmepoch > 0:
        return datetime.datetime.fromtimestamp(tmepoch)
    else:
        return get_file_time(filename)


def get_file_time(filename):
    """Get file last modification name from file system."""
    try:
        mtime = os.path.getmtime(filename)
    except OSError:

        return None

    return datetime.datetime.fromtimestamp(mtime)
