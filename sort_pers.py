import sort_photos

sort_photos.SOURCEDIR = "/Volumes/2tb/Dropbox/Dropbox (Personal)/Camerauploads"
sort_photos.TARGETDIR = "/Volumes/2tb/Dropbox/Dropbox (Active8)/photos"


if __name__ == "__main__":
    while sort_photos.main() != 0:
        pass
