#################################################

#packing to exe command: pyinstaller -F  AutoReview_main.py

#################################################

import os
import sys
import glob
from PyQt5.QtCore import Qt, QRect
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QToolButton, QPushButton, QLineEdit, QMessageBox, QLabel, QFileDialog
from datetime import datetime
from git import Repo
from Common_Def import *
import Script_Core, Spec_Core

#################################################

# Class: App
# Description: Init GUI anf some linkage functions

#################################################

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Auto Review Tool'
        self.setWindowIcon(QtGui.QIcon('github.ico'))
        self.initUI()

#################################################

# Name: initUI
# Description: Create GUI, textboxes, buttons,..

#################################################

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(10, 10, 550, 260)

        #create Menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        # Create label
        instruction_text = '1. Click on the Browse directory button.\n\n' + \
                           '2. Choose the COMPONENT directory.\n\n' + \
                           '3. Click on Review button then Open Report (default in Notepad++)'
 
        self.label = QLabel(instruction_text, self)
        self.label.setFont(QtGui.QFont('MS San Serif', 8))
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setGeometry(QRect(25, 40, 0, 0))
        self.label.adjustSize()

        # insert PYTHON logo
        self.github = QLabel(self)
        self.github.pic = QtGui.QPixmap('Octocat.png')
        self.github.setPixmap(self.github.pic)
        self.github.setGeometry(QRect(365, 20, 0, 0))
        self.github.adjustSize()
        self.github.show()

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.setGeometry(QRect(25, 130, 295, 32))
        self.textbox.setText('C:/Users/tuanp/Desktop/Dem/Com_Section3_4/rba/TEST/ComServices/Com')
        
        #Create Browse directory button
        self.button_browse = QToolButton(self)
        self.button_browse.setText('...')
        self.button_browse.setGeometry(QRect(340, 130, 32, 32))
        self.button_browse.clicked.connect(self.BrowseDirectory)

        # Create Review Script button
        self.button_script = QPushButton('Review Test Script', self)
        self.button_script.setGeometry(QRect(25, 190, 110, 35))
        self.button_script.clicked.connect(self.ReviewScript)

        # Create Review Spec button
        self.button_spec = QPushButton('Review Test Spec', self)
        self.button_spec.setGeometry(QRect(155, 190, 110, 35))
        self.button_spec.clicked.connect(self.ReviewSpec)

        #Create open newest .txt file
        self.button_open = QPushButton('Open Report', self)
        self.button_open.setGeometry(QRect(285, 190, 90, 35))
        self.button_open.setEnabled(False)
        self.button_open.clicked.connect(OpenReport)

        self.move(500, 200)
        self.show() 

#################################################

    def BrowseDirectory(self):
        try:
            self.input_directory = QFileDialog.getExistingDirectory(None, 'Select folder:')
            self.textbox.setText(self.input_directory)

        except Exception as e:
            messagebox.showinfo_st('Auto Review Tool', e)
           
#################################################

    def ReviewScript(self):
        rootdir_st = self.textbox.text()
        if not (len(rootdir_st)):
            QMessageBox.warning(self, 'Auto Review Tool', 'Plese input a directory')
        else:
            reportname_st = GetReportName(rootdir_st, 'Script')
            Script_Core.Script_MainFunction(rootdir_st, reportname_st)
            self.button_open.setEnabled(True)
            QMessageBox.warning(self, 'Auto Review Tool', 'Review Test Script done !')

#################################################

    def ReviewSpec(self):
        rootdir_st = self.textbox.text()
        if not (len(rootdir_st)):
            QMessageBox.warning(self, 'Auto Review Tool', 'Plese input a directory')
        else:
            reportname_st = GetReportName(rootdir_st, 'Spec')
            Spec_Core.Spec_MainFunction(rootdir_st, reportname_st)
            self.button_open.setEnabled(True)
            QMessageBox.warning(self, 'Auto Review Tool', 'Review Test Spec done !')


#################################################

# Name: GetReportName
# Param: rootdir_st: input directory by user
#        reporttype_st: type of object to review: Script/Spec
# Return: reportname_st: String of report name
# Description: Collect some information to generate report name
#              #1: Found name of comoponent under test
#              #2: Found Git folder in parent directories
#                  If found, get the current active branch (tester's branch)
#              #3: Get current time to make sure no report name is duplicated

#################################################


def GetReportName(rootdir_st, reporttype_st) -> str:
    rootdir_st = rootdir_st.replace(BACKSLASH, SLASH)
    compname_idx = rootdir_st.rfind(SLASH)      #2
    compname_st = rootdir_st[compname_idx+1:]
    gitdir_st = rootdir_st.split(GITLOCATION, 1)[0]

    if (GITFOLDER in os.listdir(gitdir_st)):        #2
        try:
            repo = Repo(os.path.join(gitdir_st, GITFOLDER))
            info_st = str(repo.active_branch)
            if (info_st == BRANCHMASTER): 
                info_st = info_st + '_' + compname_st
        except:
            info_st = compname_st
    else:
        info_st = compname_st

    #get datetime
    time_st = str(datetime.now().strftime('%H%M%S'))        #3

    #Report name
    reportname_st = REPORT_PREFIX + reporttype_st + '_' + info_st + '_' + time_st + TXTFILETYPE
    return reportname_st


#################################################

# Name: OpenReport
# Param: None
# Return: None
# Description: Get the latest .txt file in current folder.
#              If no Notepad++ installed, open by Notepad Windows

#################################################


def OpenReport():
    latest_file = max(glob.glob('*.txt'), key=os.path.getctime)
    try:
        os.system('start notepad++.exe ' + latest_file)
    except:
        os.system('start notepad.exe ' + latest_file)
           

#################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle('fusion')
    ex = App()
    sys.exit(app.exec_())


#################################################