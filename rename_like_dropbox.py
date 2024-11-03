# coding=utf-8
from __future__ import division, print_function
import os
import sys
import consoleprinter

import shutil

from PIL import Image
from PIL import ExifTags
import enzyme
import datetime

DATEEXIFKEY = [key for (key, value) in ExifTags.TAGS.items()
               if value == 'DateTimeOriginal'][0]
FILEFMT = "%Y-%m-%d %H.%M.%S"
DIRFMT = "%Y-%m-%d"

VIDEOFILES = ['.mp4', '.3gp', '.mov', '.mkv', '.webm', '.avi', '.ogm', '.ogv']
IMAGEFILES = ['.jpg', '.jpeg', 'cr2']


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
    
def import_file(filename, targetdir='',
                filefmt=FILEFMT, dirfmt=DIRFMT,
                shift_seconds=0, shift_img=False, shift_vid=True,
                sort_in_dir=False, rename=True):
    """Rename file according to metadata date/time.

    Puts files into target dir, creating optional subdirs.
    Formats for both filename and subdirs are the same used by ``strftime``.

    """

    dir, name = os.path.split(filename)
    print(dir, name)
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
        if os.path.exists(newfilename):
            for i in range(0, 10):
                ext = newfilename.split(".")[-1]
                tempfilename = newfilename.strip(ext).rstrip(".") + "-" + str(i) + "." + ext
                if not os.path.exists(tempfilename):
                    newfilename = tempfilename
                    break
        print(newfilename)
        if os.path.exists(newfilename):
            return filename+" skipped"
        try:
            #print(filename, newfilename.replace('JPG', 'jpg').replace('PNG', 'png').replace('MOV', 'mov'))

            os.rename(filename, newfilename.replace('JPG', 'jpg').replace('PNG', 'png').replace('MOV', 'mov'))
        except IOError as err:
            return filename+" error "+str(err)
        else:
            return filename+" ok"
    else:
        return filename

class DropboxRenamer(object):
    """Main window for the application"""
    def __init__(self):
        """
        __init__
        """
        super(DropboxRenamer, self).__init__()
        print("hello")

        #filelist = [x for x in os.listdir(sys.argv[1])]
        #print(filelist)



        filelist = []
        for root, dirs, files in os.walk(sys.argv[1]):
            for file in files:
                filelist.append(os.path.join(root, file))



        #return
        print(len(filelist))
        filelist = [x for x in filelist if x.lower().endswith('mp4') or x.lower().endswith('cr2') or x.lower().endswith('mov') or x.lower().endswith('jpg') or x.lower().endswith('png') or x.lower().endswith('jpeg') or x.lower().endswith('heic') ]

        self.filelist = filelist
        self.dirname = sys.argv[1:]
        print(len(filelist))


    def init_gui_values(self):
        """
        init_gui_values
        """
        self.shifttime.setRange(-24 * 60, 24 * 60)
        self.shifttime.setValue(0)
        self.shifttime.setSuffix(" min")

    def removeFiles(self):
        """
        removeFiles
        """
        for item in self.filelist:
            self.filelist.remove(self.filelist.row(item))

    def renameFiles(self):
        """
        renameFiles
        """
        #for index in range(len(self.filelist) - 1, -1, -1):
        for filename in self.filelist:
            #filename = self.filelist[index]


            targetdir = self.dirname
            try:
                status = import_file(filename, targetdir[0],
                                               shift_seconds=0,
                                               shift_img=False,
                                               shift_vid=False,
                                               sort_in_dir=False,
                                               rename=True)

                #print("status", status)
            except OSError as e:
                consoleprinter.warning("renameFiles", str(e))
            # os.remove(os.path.join(targetdir[0], filename))


def main():
    """
    main
    """
    if len(sys.argv) <= 1:
        consoleprinter.warning("Main", "Which path? (rename_like_dropbox.py <path>)")
        return

    dr = DropboxRenamer()

    dr.renameFiles()


if __name__ == "__main__":
    main()
