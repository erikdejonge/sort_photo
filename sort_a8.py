import sort_photos

sort_photos.SOURCEDIR = "/Users/rabshakeh/Dropbox (Personal)/Camera Uploads2"
sort_photos.TARGETDIR = "/Users/rabshakeh/dropboxa8/photos"
import os


if __name__ == "__main__":
    while sort_photos.main() != 0:
        pass
