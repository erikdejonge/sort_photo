#!/usr/local/bin/python3
# coding=utf-8
"""
    Sorts photos found in sourcedir and moves them to a new datebased directory structure xxx
"""

from __future__ import division, print_function, absolute_import, unicode_literals
from builtins import int
from builtins import open
from builtins import str
from future import standard_library

import os
import sys
print(sys.version_info)
import time
import hashlib

from PIL import Image
from appinstance import AppInstanceRunning
from consoleprinter import console
from dateutil.parser import parse

SOURCEDIR = "/Users/rabshakeh/Dropbox (Personal)/Camera Uploads"
#SOURCEDIR= "/Users/rabshakeh/camera_uploads_aug_2015"
#TARGETDIR = "/Users/rabshakeh/Dropbox (Active8)/photos"
TARGETDIR = "/Users/rabshakeh/fulldropbox/photos"

MINWIDTH = 360
MINHEIGHT = 20

SIZEALL = 1


def callback(arg, directory, files):
    """
    @type arg: list
    @type directory: unicode
    @type files: list
    @return: None
    """
    for filen in files:
        the_pic = os.path.join(directory, filen)

        if valid_types(the_pic):
            if os.path.isfile(the_pic):
                data = open(the_pic, "rb").read(2000)
                md5_data = (len(arg), the_pic, hashlib.md5(data).hexdigest())
                arg.append(md5_data)

                # noinspection PyTypeChecker
                sys.stdout.write(".")

                if len(arg) % 100 == 0:
                    sys.stdout.write("\n" + str(len(arg)))

                sys.stdout.flush()


def check_for_existence(media_files):
    """
    @type media_files: dict
    @return: None
    """
    media_files2 = []

    for media_file in media_files:
        filepath = media_files[media_file][1]

        if os.path.exists(filepath):
            media_files2.append(media_files[media_file][1])

    return media_files2


def determine_date_file(filepath):
    """
    @type filepath: unicode
    @return: None
    """
    stat_file = os.stat(filepath)
    gmtime_data = time.gmtime(int(stat_file.st_mtime))
    year = str(gmtime_data[0])
    month = str(gmtime_data[1])
    day = str(gmtime_data[2])
    return year, month, day


def determine_date_filename_dropbox(filepath, year, month, day):
    """
    @type filepath: str
    @type year: str
    @type month: str
    @type day: str
    @return: None
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
            except ValueError as exc:
                print(exc)

    return year, month, day


def ensure_directory(year, month, day):
    """
    @type year: unicode
    @type month: unicode
    @type day: unicode
    @return: None
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


def exif_date_time(filepath, year, month, day):
    """
    @type filepath: unicode
    @type year: str
    @type month: str
    @type day: str
    @return: None
    """
    image_file = Image.open(filepath)
    try:

        # noinspection PyProtectedMember
        exif = image_file._getexif()

        if exif:
            if 36867 in exif:
                # noinspection PyProtectedMember
                jpgd = str(image_file._getexif()[36867]).split(":")

                if len(jpgd) == 3:
                    year = str(jpgd[0]).strip()
                    month = str(jpgd[1]).strip()
                    day = str(jpgd[2].split(" ")[0]).strip()

    except Exception as ex:
        print(filepath)
        print(ex)


    return year, month, day


def fp_is_jpg(filepath):
    """
    @type filepath: unicode
    @return: None
    """
    extensions = ["jpg"]

    for ext in extensions:
        if filepath.lower().endswith(ext):
            return True

    return False


def read_path():
    """
    read_path
    """
    media_files = {}
    file_list = []
    print(SOURCEDIR)
    try:
        walk = os.path.walk
        walk(SOURCEDIR, callback, file_list)
    except AttributeError:
        walk = os.walk
        for dirName, _, fileList in walk(SOURCEDIR):
            callback(file_list, dirName, fileList)
    print(len(file_list))

    for i in file_list:
        if "Aperture" not in str(i):
            media_files[i[2]] = i

    print(len(media_files))
    return media_files


def shell_escape(astring):
    """
    @type astring: unicode
    @return: None
    """

    return astring.replace("(", "\\(").replace(")", "\\)").replace(" ", "\\ ").replace("'", "\\'")


def valid_types(filepath):
    """
    @type filepath: unicode
    @return: None
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
        "m4v",
        "cr2",
        "bmp",
    ]

    for ext in extensions:
        if filepath.lower().endswith(ext):
            return True

    return False


def main():
    """
    main
    """
    if os.path.exists(".DS_Store"):
        os.remove(".DS_Store")
    try:
        pics_moved = 0
        media_files = check_for_existence(read_path())

        print(len(media_files))

        for filepath in media_files:
            if not valid_types(filepath):
                print("not valid type", filepath)
            else:
                (year, month, day) = determine_date_file(filepath)
                is_image = fp_is_jpg(filepath)

                # noinspection PyBroadException
                try:
                    if is_image:
                        (year, month, day) = exif_date_time(filepath, year, month, day)
                except:
                    raise

                (year, month, day) = determine_date_filename_dropbox(filepath, year, month, day)
                day_path = ensure_directory(year, month, day)
                #print(day_path + "/" + os.path.basename(filepath), os.path.exists(day_path + "/" + os.path.basename(filepath)))
                if not os.path.exists(day_path + "/" + os.path.basename(filepath)):
                    print(filepath)
                    os.system('mv ' + shell_escape(filepath) + ' ' + shell_escape(day_path) + "/")
                    pics_moved += 1

        print()
        print(pics_moved, "pics moved")
        return pics_moved
    except AppInstanceRunning:
        console(color="red", msg="instance runs already")

standard_library.install_aliases()


if __name__ == "__main__":
    while main() != 0:
        pass
