from __future__ import division, print_function
import os
import sys
import dropboximport

class DropboxRenamer(object):
    """Main window for the application"""

    def __init__(self):
        super(DropboxRenamer, self).__init__()
        self.filelist = [x for x in os.listdir(sys.argv[1]) if x.lower().endswith('jpg') or x.lower().endswith('png') and not x.lower().startswith("201")]
        self.dirname = sys.argv[1:]
    def init_gui_values(self):

        self.shifttime.setRange(-24 * 60, 24 * 60)
        self.shifttime.setValue(0)
        self.shifttime.setSuffix(" min")


    def removeFiles(self):
        for item in self.filelist:
            self.filelist.remove(self.filelist.row(item))

    def renameFiles(self):
        for index in range(len(self.filelist) - 1, -1, -1):
            filename = self.filelist[index]

            targetdir = self.dirname

            status = dropboximport.import_file(os.path.join(targetdir[0], filename), targetdir[0],
                                               shift_seconds=0,
                                               shift_img=False,
                                               shift_vid=False,
                                               sort_in_dir=False,
                                               rename=True)

            #print("status", status, os.path.join(targetdir[0], filename))
            #os.remove(os.path.join(targetdir[0], filename))

def main():
  dr = DropboxRenamer()
  dr.renameFiles()

if __name__=="__main__":
  main()