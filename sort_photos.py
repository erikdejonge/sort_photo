# pylint: disable-msg=C0103
# pylint: enable-msg=C0103
# tempfile regex format
#
# pylint: disable-msg=C0111
# missing docstring
#
# pylint: disable-msg=W0232
# no __init__ method
#
# pylint: disable-msg=R0903
# to few public methods
#
# DISABLED_ylint: disable-msg=R0201
# method could be a function
#
#!/usr/bin/python
# -*- coding: utf-8 -*-

# time.gmtime(s.st_mtime)

import time
import os
import sys
import hashlib
import Image
from dateutil.parser import parse

SIZEALL = 1
MINWIDTH = 360
MINHEIGHT = 270

NAME = "test"

if NAME == "test":
    SOURCEDIR = "./source"
    TARGETDIR = "./target"

def valid_types(filepath):
    extensions = [
        "jpg",
        "mpg",
        "png",
        "mov",
        "avi",
        "gif",
        "3gp",
        "mp4",
        "mpg",
        "cr2",
        "bmp",
        ]
    for ext in extensions:
        if filepath.lower().endswith(ext):
            return True
    return False


def callback(arg, directory, files):
    for filen in files:
        the_pic = os.path.join(directory, filen)
        if valid_types(the_pic):
            if os.path.isfile(the_pic):
                data = open(the_pic, "r").read(2000)
                md5_data = (len(arg), the_pic, hashlib.md5(data).hexdigest())
                arg.append(md5_data)
                sys.stdout.write(".")
                if len(arg) % 100 == 0:
                    sys.stdout.write("\n" + str(len(arg)))
                sys.stdout.flush()


def read_path():
    media_files = {}
    file_list = []
    print SOURCEDIR
    os.path.walk(SOURCEDIR, callback, file_list)
    print len(file_list)
    for i in file_list:
        if "Aperture" not in str(i):
            media_files[i[2]] = i
    print len(media_files)
    return media_files


def check_for_existence(media_files):
    media_files2 = []
    for media_file in media_files:
        filepath = media_files[media_file][1]
        if os.path.exists(filepath):
            media_files2.append(media_files[media_file][1])
    return media_files2


def determine_date_file(filepath):
    stat_file = os.stat(filepath)
    gmtime_data = time.gmtime(int(stat_file.st_mtime))
    year = str(gmtime_data[0])
    month = str(gmtime_data[1])
    day = str(gmtime_data[2])

    return (year, month, day)


def exif_date_time(filepath, year, month, day):
    image_file = Image.open(filepath)

    # protected member
    # pylint: disable-msg=W0212

    exif = image_file._getexif()

    if exif:
        if 36867 in exif:
            jpgd = str(image_file._getexif()[36867]).split(":")
            if len(jpgd) == 3:
                year = str(jpgd[0]).strip()
                month = str(jpgd[1]).strip()
                day = str(jpgd[2].split(" ")[0]).strip()

    # pylint: enable-msg=W0212

    return (year, month, day)


def determine_date_filename_dropbox(filepath, year, month, day):
    filename = os.path.basename(filepath)
    fnamesplit = filename.split(" ")
    if len(fnamesplit)>0:
        datefilename = fnamesplit[0].strip()
        if len(datefilename.split("-")) == 3:
            try:
                filedate = parse(datefilename)
                year = filedate.year
                month = filedate.month
                day = filedate.day
            except ValueError, exc:
                print exc
    return (year, month, day)


def fp_is_jpg(filepath):
    extensions = ["jpg"]
    for ext in extensions:
        if filepath.lower().endswith(ext):
            return True
    return False


def ensure_directory(year, month, day):
    year = str(year)
    month = str(month)
    day = str(day)

    if len(str(year).strip()) == 0:
        year = "1900"
    imonth = int(month)
    iday = int(day)

    if imonth < 10:
        month = "0"
    else:
        month = ""
    month += str(imonth)
    if iday < 10:
        day = "0"
    else:
        day = ""
    day += str(iday)
    year_path = TARGETDIR + "/" + year
    month_path = year_path + "/" + month
    day_path = month_path + "/" + day
    if not os.path.exists(year_path):
        os.mkdir(year_path)
    if not os.path.exists(month_path):
        os.mkdir(month_path)
    if not os.path.exists(day_path):
        os.mkdir(day_path)
    return day_path


def shell_escape(astring):
    return astring.replace("(","\\(").replace(")","\\)").replace(" ","\\ ").replace("'","\\'")


def main():
    pics_moved = 0

    media_files = check_for_existence(read_path())
    data = 0
    print len(media_files)

    for filepath in media_files:

        data = data + 1

        if not valid_types(filepath):
            print "not valid type", filepath
        else:
            (year, month, day) = determine_date_file(filepath)
            is_image = fp_is_jpg(filepath)

            if is_image:
                (year, month, day) = exif_date_time(filepath, year, month, day)

            (year, month, day) = determine_date_filename_dropbox(filepath, year, month, day)

            day_path = ensure_directory(year, month, day)
            if not os.path.exists(day_path + "/" + os.path.basename(filepath)):
                print filepath
                #print "moved:", day_path + "/" + os.path.basename(filepath)
                #print ('mv "' + shell_escape(filepath) + '" ' + shell_escape(day_path) + "/")
                os.system('mv ' + shell_escape(filepath) + ' ' + shell_escape(day_path) + "/")
                pics_moved += 1

    print
    print pics_moved, "pics moved"
    return pics_moved

if __name__ == "__main__":
    while main() != 0:
        pass
