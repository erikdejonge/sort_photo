import sort_photos

sort_photos.SOURCEDIR = "/Users/rabshakeh/Dropbox (Personal)/Camera Uploads"


sort_photos.TARGETDIR = "/Users/rabshakeh/dropboxpers/photos"


if __name__ == "__main__":
    while sort_photos.main() != 0:
        pass
