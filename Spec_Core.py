import os
import xlrd
from Common_Def import *
from Common_API import *
from Spec_Report_Def import *

#################################################

# Name: Spec_MainFunction
# Param: inputdir_st: directory to Component name
#        reportname_st: .txt report name
# Return: None
# Desciption: #1: Initialize list to store report content
#             #2: Concatenates string to get directory to 01_TestSpecification folder
#             #3: Call GetSpecList to get all directories to test spec file (.xlsm)
#             #4: For each test spec, start Review process
#             #5: Push all report contents to .txt file

#################################################


def Spec_MainFunction(specdir_st, reportname_st):
    global ReportContent_lst        #1
    ReportContent_lst = InitList(1)

    SpecDir_st = specdir_st + TEST_SPEC_DIR       #2
    SpecFile_lst = GetSpecList(SpecDir_st)      #3

    for specfile in SpecFile_lst:       #4
        OpenWorkbook(specfile)
    
    Export_Report(reportname_st, ReportContent_lst)     #5


#################################################

# Name: GetSpecList
# Param: SpecDir_st: directory to 01_TestSpecification folder
# Return: allfiles_lst: list to store all directories of .xlsm files
# Description: #1: Initialize return list
#              #2: For given directory, browse all .xlsm files in all sub-dirs and store their directories in allfiles_lst
#              #3: If no .xlsm file found, throw WARNING to report

#################################################


def GetSpecList(SpecDir_st):
    allfiles_lst = InitList(1)      #1

    for path, dirs, files in os.walk(SpecDir_st):       #2
        for filename in files:
            if not (filename.startswith('~$')):     #check for temporary if file is opening
                filepath = os.path.join(path, filename)
                allfiles_lst.append(filepath)
    if not (allfiles_lst):     #3 
        ReportContent_lst.append(NO_SPEC_FOUND)

    return allfiles_lst


#################################################


def OpenWorkbook(specfile):
    ReportContent_lst.append(START_SPEC_FILE + specfile + PROCESSING)
    try:
        spec_workbook = xlrd.open_workbook(specfile)
        allsheets_lst = spec_workbook.sheet_names()
    except Exception as e:
        ReportContent_lst.append(UNABLE_OPEN_SPEC)
        ReportContent_lst.append(END_SPEC_FILE)
        return

    check_Stream(spec_workbook)
    tcunit_lst = GetTCSheets(allsheets_lst)
    CheckTCSheet(tcunit_lst, spec_workbook)

    spec_workbook.release_resources()
    del spec_workbook
    ReportContent_lst.append(END_SPEC_FILE)


#################################################


def check_Stream(spec_workbook):
    ReportContent_lst.append(CHECKING + TEST_RESULT_SUMMARY_SHEET + PROCESSING)
    try:
        current_sheet = spec_workbook.sheet_by_name(TEST_RESULT_SUMMARY_SHEET)
    except:
        ReportContent_lst.append(WARNING + UNABLE_OPEN_SHEET + TEST_RESULT_SUMMARY_SHEET)
        return

    try:
        stream_st = current_sheet.cell(STREAM_POSITION[0], STREAM_POSITION[1]).value
    except:
        ReportContent_lst.append(WARNING + UNABLE_READ_STREAM)
        return

    if (CUBAS not in stream_st):
        ReportContent_lst.append(WARNING + CUBAS + CONTENT_EMPTY)


#################################################


def GetTCSheets(allsheets_lst):
    TCsheet_lst = InitList(1)
    for sheet in allsheets_lst:
        if (TCUNIT_SHEET in sheet):
            TCsheet_lst.append(sheet)

    if not (TCsheet_lst):
        ReportContent_lst.append(WARNING + TCUNIT_NOT_FOUND)
        return
    else:
        return TCsheet_lst

#################################################


def CheckTCSheet(tcunit_lst, spec_workbook):
    for tcsheet in tcunit_lst:
        ReportContent_lst.append(CHECKING + tcsheet + PROCESSING)
        current_sheet = spec_workbook.sheet_by_name(tcsheet)

        for index, pos_to_check in enumerate(LIST_TO_CHECK_POS):
            try:
                cellcontent_st = current_sheet.cell(pos_to_check[0], pos_to_check[1]).value
            except: 
                ReportContent_lst.append(WARNING + UNABLE_TO_READ + LIST_TO_CHECK[index])
                continue

            ReviewContent(cellcontent_st.strip(), LIST_TO_CHECK[index])
            

#################################################


def ReviewContent(cellcontent_st, reference_st):
    if not (cellcontent_st):
        ReportContent_lst.append(WARNING + reference_st + CONTENT_EMPTY)

    if (reference_st in (SET_GLOBAL_VARIABLES, SET_PARAMETERS, SET_STUB_FUNCTIONS)):
        for to_check in LIST_REMAINING_TO_CHECK:
            if (to_check in cellcontent_st):
                redundant_int = cellcontent_st.count(to_check)
                ReportContent_lst.append(WARNING + str(redundant_int) + SPACE + to_check + REMAINING + IN + SPACE + reference_st)


#################################################
