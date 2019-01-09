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


############################################################################



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Auto Review Tool'
        self.setWindowIcon(QtGui.QIcon('github.ico'))
        self.initUI()


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
        self.button_browse.clicked.connect(self.browse_root_dir)

        # Create Review Script button
        self.button_script = QPushButton('Review Test Script', self)
        self.button_script.setGeometry(QRect(25, 190, 110, 35))
        self.button_script.clicked.connect(self.Review_Test_Script)

        # Create Review Spec button
        self.button_spec = QPushButton('Review Test Spec', self)
        self.button_spec.setGeometry(QRect(155, 190, 110, 35))
        self.button_spec.clicked.connect(self.Review_Test_Spec)

        #Create open newest .txt file
        self.button_open = QPushButton('Open Report', self)
        self.button_open.setGeometry(QRect(285, 190, 90, 35))
        self.button_open.setEnabled(False)
        self.button_open.clicked.connect(Open_latest_report)

        self.move(500, 200)
        self.show() 


#################################################


    def browse_root_dir(self):
        try:
            self.input_directory = QFileDialog.getExistingDirectory(None, 'Select folder:')
            self.textbox.setText(self.input_directory)

        except Exception as e:
            messagebox.showinfo('Auto Review Tool', e)

           
#################################################


    def Review_Test_Script(self):
        root_dir = self.textbox.text()
        if (len(root_dir) == 0):
            QMessageBox.warning(self, 'Auto Review Tool', 'Plese input a directory')
        else:
            report_name = getReportName(root_dir, 'Script')
            Script_Core.Script_MainFunction(root_dir, report_name)
            self.button_open.setEnabled(True)
            QMessageBox.warning(self, 'Auto Review Tool', 'Review Test Script done !')
           

#################################################


    def Review_Test_Spec(self):
        root_dir = self.textbox.text()
        if (len(root_dir) == 0):
            QMessageBox.warning(self, 'Auto Review Tool', 'Plese input a directory')
        else:
            report_name = getReportName(root_dir, 'Spec')
            Spec_Core.Spec_MainFunction(root_dir, report_name)
            self.button_open.setEnabled(True)
            QMessageBox.warning(self, 'Auto Review Tool', 'Review Test Spec done !')


#################################################


def getReportName(root_dir, report_type):
    root_dir = root_dir.replace(BACKSLASH, SLASH)
    compname_idx = root_dir.rfind(SLASH)
    comp_name = root_dir[compname_idx+1:]
    git_dir = root_dir.split(GITLOCATION, 1)[0]

    if (GITFOLDER in os.listdir(git_dir)):
        try:
            repo = Repo(os.path.join(git_dir, GITFOLDER))
            info = str(repo.active_branch)
            if (info == BRANCHMASTER): 
                info = info + '_' + comp_name
        except:
            info = comp_name
    else:
        info = comp_name

    #get datetime
    time = str(datetime.now().strftime('%H%M%S'))

    #Report name
    report_name = REPORT_PREFIX + report_type + '_' + info + '_' + time + TXTFILETYPE
    return report_name


#################################################


def Open_latest_report():
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