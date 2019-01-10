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


def Spec_MainFunction(specdir_st, reportname_st) -> None:
    global ReportContent_lst        #1
    ReportContent_lst = InitList(1)

    SpecDir_st = specdir_st + TEST_SPEC_DIR       #2
    SpecFile_lst = GetSpecList(SpecDir_st)      #3

    for specdir in SpecFile_lst:       #4
        OpenWorkbook(specdir)
    
    Export_Report(reportname_st, ReportContent_lst)     #5


#################################################

# Name: GetSpecList
# Param: SpecDir_st: directory to 01_TestSpecification folder
# Return: allfiles_lst: list to store all directories of .xlsm files
# Description: #1: Initialize return list
#              #2: For given directory, browse all .xlsm files in all sub-dirs and store their directories in allfiles_lst
#              #3: If no .xlsm file found, throw WARNING to report

#################################################


def GetSpecList(SpecDir_st) -> list:
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

# Name: OpenWorkbook
# Param: specdir: directory to each test spec
# Return: None
# Description: Beginning review process
#              #1: Notify in report the beginning of each test spec
#              #2: Open .xlsm file, store all contents in spec_workbook
#              #3: Throw WARNING if unable to open if bypass this file
#              #4: Check content of Stream (Feature under test name)
#              #5: Check contents of TC_Unin sheets
#              #6: Close file and notify in report the end of one file

#################################################


def OpenWorkbook(specdir) -> None:
    ReportContent_lst.append(START_SPEC_FILE + specdir + PROCESSING)        #1
    try:        #2
        spec_workbook = xlrd.open_workbook(specdir)
        allsheets_lst = spec_workbook.sheet_names()
    except:     #3
        ReportContent_lst.append(UNABLE_OPEN_SPEC)
        ReportContent_lst.append(END_SPEC_FILE)
        return

    CheckStream(spec_workbook)      #4
    tcunit_lst = GetTCSheets(allsheets_lst)     #5
    CheckTCSheet(tcunit_lst, spec_workbook)

    spec_workbook.release_resources()       #6
    del spec_workbook
    ReportContent_lst.append(END_SPEC_FILE)


#################################################

# Name: CheckStream
# Param: spec_workbook: all contents of one spec file
# Return: None
# Description: Check if Stream has filled in TestResultSummary sheet
#              #1: Try to open find TestReusltSummary sheet
#              #2: Try to read Feature under test cell
#              #3: If no string 'CUBAS' found in this cell, throw WARNING

#################################################


def CheckStream(spec_workbook) -> None:
    ReportContent_lst.append(CHECKING + TEST_RESULT_SUMMARY_SHEET + PROCESSING)
    try:        #1
        current_sheet = spec_workbook.sheet_by_name(TEST_RESULT_SUMMARY_SHEET)
    except: 
        ReportContent_lst.append(WARNING + UNABLE_OPEN_SHEET + TEST_RESULT_SUMMARY_SHEET)
        return

    try:        #2
        stream_st = current_sheet.cell(STREAM_POSITION[0], STREAM_POSITION[1]).value
    except:
        ReportContent_lst.append(WARNING + UNABLE_READ_STREAM)
        return

    if (CUBAS not in stream_st):        #3
        ReportContent_lst.append(WARNING + CUBAS + CONTENT_EMPTY)


#################################################

# Name: GetTCSheets
# Param: allsheets_lst: list names of all sheets
# Return: TCsheet_lst: list names of TC_Unit_ sheets
# Description: Return list names of all TC_Unit_ sheets
#              #1: Find all sheets with name 'TC_Unit_'
#              #2: If sheets found, throw WARNING to report

#################################################


def GetTCSheets(allsheets_lst) -> list:
    TCsheet_lst = InitList(1)
    for sheet in allsheets_lst:     #1
        if (TCUNIT_SHEET in sheet):
            TCsheet_lst.append(sheet)

    if not (TCsheet_lst):       #2
        ReportContent_lst.append(WARNING + TCUNIT_NOT_FOUND)
        return
    else:
        return TCsheet_lst


#################################################

# Name: CheckTCSheet
# Param: tcunit_lst: list names of TC_Unit_ sheets
#        spec_workbook: all contents of workbook
# Return: None
# Description: Read content of "TO CHECK" cells in every TC_Unit_ sheet
#              #1: Store contents of current sheet in current_sheet
#              #2: Get contents of every "TO_CHECK" cell
#              #3: Review content of this cell

#################################################


def CheckTCSheet(tcunit_lst, spec_workbook) -> None:
    for tcsheet in tcunit_lst:      #1
        ReportContent_lst.append(CHECKING + tcsheet + PROCESSING)
        current_sheet = spec_workbook.sheet_by_name(tcsheet)

        for index, pos_to_check in enumerate(LIST_TO_CHECK_POS):        #2
            try:
                cellcontent_st = current_sheet.cell(pos_to_check[0], pos_to_check[1]).value
            except: 
                ReportContent_lst.append(WARNING + UNABLE_TO_READ + LIST_TO_CHECK[index])
                continue

            ReviewContent(cellcontent_st.strip(), LIST_TO_CHECK[index])     #3
            

#################################################

# Name: ReviewContent
# Param: cellcontent_st: content of "TO_CHECK" cell
#        reference_st: "TO_CHECK" name
# Return: None
# Description: Check some possible mistake in content of "TO_CHECK"
#              #1: Throw WARNING if cell content is empty
#              #2: Check reduntdancies

#################################################


def ReviewContent(cellcontent_st, reference_st) -> None:
    if not (cellcontent_st):        #1
        ReportContent_lst.append(WARNING + reference_st + CONTENT_EMPTY)

    if (reference_st in (SET_GLOBAL_VARIABLES, SET_PARAMETERS, SET_STUB_FUNCTIONS)):
        for to_check in LIST_REMAINING_TO_CHECK:        #2
            if (to_check in cellcontent_st):
                redundant_int = cellcontent_st.count(to_check)
                ReportContent_lst.append(WARNING + str(redundant_int) + SPACE + to_check + REMAINING + IN + SPACE + reference_st)


#################################################