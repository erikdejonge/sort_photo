#!/usr/bin/env python
"""Dropbox CameraUpload renamer

"""
from __future__ import division, print_function
import os
import sys

try:
    from PySide import QtGui
except ImportError:
    print("Fallback to PyQt")
    import sip
    sip.setapi(u'QDate', 2)
    sip.setapi(u'QDateTime', 2)
    sip.setapi(u'QString', 2)
    sip.setapi(u'QTextStream', 2)
    sip.setapi(u'QTime', 2)
    sip.setapi(u'QUrl', 2)
    sip.setapi(u'QVariant', 2)
    from PyQt4 import QtGui

import dropboximport


class FileListWithDrop(QtGui.QListWidget):
    """Extend ListWidget with Drop capability."""
    def __init__(self, parent):
        super(FileListWithDrop, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                self.addItem(url.toLocalFile())
        else:
            event.ignore()


class DropboxRenamerWindow(QtGui.QWidget):
    """Main window for the application"""

    def __init__(self):
        super(DropboxRenamerWindow, self).__init__()
        # Add widgets
        addbtn = QtGui.QPushButton("Add files", self)
        delbtn = QtGui.QPushButton("Remove files", self)

        self.filelist = FileListWithDrop(self)
        self.filelist.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        
        filegroupbox = QtGui.QGroupBox("Import files", self)
        self.makedirscb = QtGui.QCheckBox("Put in folders", filegroupbox)
        self.renfilescb = QtGui.QCheckBox("Rename files", filegroupbox)
        dirlabel = QtGui.QLabel("Import to ...", filegroupbox)
        self.dirname = QtGui.QLineEdit(self)
        dirbtn = QtGui.QPushButton('...', self)
        
        shiftgroupbox = QtGui.QGroupBox("Timeshift", self)
        self.shiftimgcb = QtGui.QCheckBox("for images", shiftgroupbox)
        self.shiftvidcb = QtGui.QCheckBox("for videos", shiftgroupbox)
        shiftlabel = QtGui.QLabel("Shift time by", shiftgroupbox)
        self.shifttime = QtGui.QSpinBox(shiftgroupbox)
        
        importbtn = QtGui.QPushButton("Import", self)

        # Connect signals
        addbtn.clicked.connect(self.addFiles)
        delbtn.clicked.connect(self.removeFiles)
        dirbtn.clicked.connect(self.chooseDir)
        importbtn.clicked.connect(self.renameFiles)

        # Init widgets
        self.init_gui_values()

        # Do layout
        mainbox = QtGui.QVBoxLayout()
        
        filesbox = QtGui.QHBoxLayout()
        filesbox.addWidget(addbtn)
        filesbox.addWidget(delbtn)
        mainbox.addLayout(filesbox)

        mainbox.addWidget(self.filelist)

        filebox = QtGui.QVBoxLayout()
        
        filecbbox = QtGui.QHBoxLayout()        
        filecbbox.addWidget(self.makedirscb)
        filecbbox.addWidget(self.renfilescb)
        filebox.addLayout(filecbbox)
        
        dirbox = QtGui.QHBoxLayout()        
        dirbox.addWidget(dirlabel)
        dirbox.addWidget(self.dirname)
        dirbox.addWidget(dirbtn)

        filebox.addLayout(dirbox)
        filegroupbox.setLayout(filebox)

        mainbox.addWidget(filegroupbox)


        shiftbox = QtGui.QVBoxLayout()
        shiftcbbox = QtGui.QHBoxLayout()
        shiftcbbox.addWidget(self.shiftimgcb)
        shiftcbbox.addWidget(self.shiftvidcb)
        shiftbox.addLayout(shiftcbbox)
        
        timebox = QtGui.QHBoxLayout()
        timebox.addWidget(shiftlabel)
        timebox.addWidget(self.shifttime)
        shiftbox.addLayout(timebox)
        
        shiftgroupbox.setLayout(shiftbox)
        
        mainbox.addWidget(shiftgroupbox)
        mainbox.addWidget(importbtn)

        self.setLayout(mainbox)

        self.setWindowTitle("Dropbox photo import")

    def init_gui_values(self):
        if len(sys.argv) > 1:
            self.filelist.addItems(sys.argv[1:])
        self.dirname.setText(os.path.expanduser("~/Dropbox/Camera Uploads"))
        self.shifttime.setRange(-24 * 60, 24 * 60)
        self.shifttime.setValue(0)
        self.shifttime.setSuffix(" min")
        self.shiftvidcb.setChecked(True)
        self.shiftimgcb.setChecked(False)
        self.makedirscb.setChecked(False)
        self.renfilescb.setChecked(True)

    def addFiles(self):
        dlg = QtGui.QFileDialog(self)
        dlg.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        dlg.setFileMode(QtGui.QFileDialog.ExistingFiles)
#        dlg.setDirectory(os.path.abspath())
        if dlg.exec_():
            self.filelist.addItems(dlg.selectedFiles())

    def removeFiles(self):
        for item in self.filelist.selectedItems():
            self.filelist.takeItem(self.filelist.row(item))

    def chooseDir(self):
        dlg = QtGui.QFileDialog(self)
        dlg.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        dlg.setFileMode(QtGui.QFileDialog.Directory)
        dlg.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        dlg.setDirectory(os.path.abspath(self.dirname.text()))
        if dlg.exec_():
            self.dirname.setText(dlg.selectedFiles()[0])

    def renameFiles(self):
        for index in range(self.filelist.count() - 1, -1, -1):
            filename = self.filelist.item(index).text()
            targetdir = self.dirname.text()
            shift = 60 * self.shifttime.value()
            shift_img = self.shiftimgcb.isChecked()
            shift_vid = self.shiftvidcb.isChecked()
            sort_in_dir = self.makedirscb.isChecked()
            rename = self.renfilescb.isChecked()
            status = dropboximport.import_file(filename, targetdir,
                                               shift_seconds=shift,
                                               shift_img=shift_img,
                                               shift_vid=shift_vid,
                                               sort_in_dir=sort_in_dir,
                                               rename=rename)
            if not status:
                self.filelist.takeItem(index)
        if self.filelist.count() > 0:
            icon = QtGui.QMessageBox.Warning
            title = "Warning"
            text = 'Could not rename some files!'
            infotext = 'Check files remained in the list'
        else:
            icon = QtGui.QMessageBox.Information
            title = "Note"
            text = 'Processing complete.'
            infotext = 'No errors occured.'
        mesg = QtGui.QMessageBox(icon, title, text)
        mesg.setInformativeText(infotext)
        mesg.exec_()

app = QtGui.QApplication(sys.argv)
window = DropboxRenamerWindow()
window.show()
sys.exit(app.exec_())
