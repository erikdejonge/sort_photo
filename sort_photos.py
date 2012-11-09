# -*- coding: utf-8 -*-

"""
    Sorts photos found in sourcedir and moves them to a new datebased directory structure
"""

import time
import os
import sys
#noinspection PyCompatibility,PyCompatibility
import hashlib
import Image
from dateutil.parser import parse

SIZEALL = 1
MINWIDTH = 360
MINHEIGHT = 270

NAME = "djv"

if NAME == "test":
    SOURCEDIR = "./source"
    TARGETDIR = "./target"

def valid_types(filepath):
    """
        extensions which are added to the process list
    """

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
    """
        callback for the recursive file indexer
    """

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
    """
        read the source path and index files
    """

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
    """
        check if the file exists, filter for media files)
    """

    media_files2 = []
    for media_file in media_files:
        filepath = media_files[media_file][1]
        if os.path.exists(filepath):
            media_files2.append(media_files[media_file][1])
    return media_files2


def determine_date_file(filepath):
    """
        get date from file
    """

    stat_file = os.stat(filepath)
    gmtime_data = time.gmtime(int(stat_file.st_mtime))
    year = str(gmtime_data[0])
    month = str(gmtime_data[1])
    day = str(gmtime_data[2])

    return year, month, day


def exif_date_time(filepath, year, month, day):
    """
        get date from exif data in jpg
    """

    image_file = Image.open(filepath)
    try:
        exif = image_file._getexif()

        if exif:
            if 36867 in exif:
                jpgd = str(image_file._getexif()[36867]).split(":")
                if len(jpgd) == 3:
                    year = str(jpgd[0]).strip()
                    month = str(jpgd[1]).strip()
                    day = str(jpgd[2].split(" ")[0]).strip()
    except Exception, ex:
        print ex
    return year, month, day


def determine_date_filename_dropbox(filepath, year, month, day):
    """
        get date from dropbox style files
    """

    filename = os.path.basename(filepath)
    fnamesplit = filename.split(" ")
    if len(fnamesplit) > 0:
        datefilename = fnamesplit[0].strip()
        if len(datefilename.split("-")) == 3:
            try:
                filedate = parse(datefilename)
                year = filedate.year
                month = filedate.month
                day = filedate.day
            except ValueError, exc:
                print exc
    return year, month, day


def fp_is_jpg(filepath):
    """
        test for jpg
    """

    extensions = ["jpg"]
    for ext in extensions:
        if filepath.lower().endswith(ext):
            return True
    return False


def ensure_directory(year, month, day):
    """
        check and make folder
    """
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
    """
        escape os path
    """

    return astring.replace("(", "\\(").replace(")", "\\)").replace(" ", "\\ ").replace("'", "\\'")


def main():
    """
        check all files, determine date and move to new folder
    """

    pics_moved = 0

    media_files = check_for_existence(read_path())
    data = 0
    print len(media_files)

    for filepath in media_files:
        data += 1

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
                os.system('mv ' + shell_escape(filepath) + ' ' + shell_escape(day_path) + "/")
                pics_moved += 1

    print
    print pics_moved, "pics moved"
    return pics_moved

if __name__ == "__main__":
    while main() != 0:
        pass
