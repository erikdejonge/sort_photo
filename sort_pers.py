import sort_photos

sort_photos.SOURCEDIR = "/home/rabshakeh/Dropbox (Personal)/Camera Uploads"


sort_photos.TARGETDIR = "/home/rabshakeh/dropboxphotos/photos"


if __name__ == "__main__":
    while sort_photos.main() != 0:
        pass
