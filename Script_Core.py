import os
from Common_Def import *
from Common_API import *
from Script_Report_Def import *
from Script_API import *

#################################################

# Name: Script_MainFunction
# Param: inputdir_st: directory to Component name
#        reportname_st: .txt report name
# Return: None
# Desciption: #1: Initialize list to store report content
#             #2: Concatenates string to get directory to 02_TestScript folder
#             #3: Call GetScriptList to get all directories to test script file (.c)
#             #4: For each test script, start Review process
#             #5: Push all report contents to .txt file

#################################################


def Script_MainFunction(inputdir_st, reportname_st):
    global ReportContent_lst        #1 
    ReportContent_lst = InitList(1)

    ScriptDir_st = inputdir_st + TEST_SCRIPT_DIR    #2
    ScriptDir_lst = GetScriptList(ScriptDir_st)     #3

    for scriptdir in ScriptDir_lst:     #4
        ScanTestScript(scriptdir)

    Export_Report(reportname_st, ReportContent_lst)     #5

#################################################

# Name: GetScriptList
# Param: ScriptDir_st: directory to 02_TestScript folder
# Return: Cfile_lst: list to store all directories of .c files
# Description: #1: Initialize return list
#              #2: For given directory, browse all .c files in all sub-dirs and store their directories in Cfile_lst
#              #3: If no .c file found, throw WARNING to report

#################################################

def GetScriptList(ScriptDir_st):
    Cfile_lst = InitList(1)     #1

    for path, subdirs, files in os.walk(ScriptDir_st):      #2
        for filename in files:
            if filename.endswith('.c'):
                filepath = os.path.join(path, filename)
                Cfile_lst.append(filepath)
    if not (Cfile_lst):     #3
        ReportContent_lst.append(NO_SCRIPT_FOUND)

    return Cfile_lst


#################################################

# Name: ScanTestScript
# Param: scriptdir: directory to each test script
# Return: None
# Description: Beginning review process
#              #1: Notify in report the beginning of each test script
#              #2: Open .c file, store all lines of code in allcodes_lst, then close it.
#              #3: Throw WARNING if unable to open file (nearly impossible to occur)
#              #4: Scan every line of code until the end of test case declaration, the LineCounter stopped here
#              #5: Start Review test case from the LineCounter line

#################################################

def ScanTestScript(scriptdir):
    ReportContent_lst.append(START_C_FILE + scriptdir + PROCESSING)     #1
    try:        #2
        Cfile_temp = open(scriptdir, 'r')
        allcodes_lst = Cfile_temp.readlines()
        Cfile_temp.close()
        del Cfile_temp
    except:     #3
        ReportContent_lst.append(UNABLE_OPEN_SCRIPT)
        ReportContent_lst.append(END_C_FILE)
        return

    for LineCounter, LineofCode in enumerate(allcodes_lst, start = 1):      #4
        #Use enumerare to get both line content and line number
        if (isEndDeclareTestCases(LineofCode)):
            break

    ReviewTestCases(allcodes_lst, LineCounter)      #5

#################################################

# Name: ReviewTestCases
# Param: allcodes_lst: store all lines of code
#        begin_counter: specifies the beginning (index) of test case execution in allcodes_lst
# Return: None
# Description: Review all test cases in test script
#             #1: Initialize state for each lineofcode
#             #2: Initialize some lists to store specified contents
#             #3: This lineofcode is the first line of test case
#             #4: This lineofcode is in TO_CHECK_LIST
#             #5,6,7: Store contents of Tester Define, Expected Calls, GUID
#             #8: This lineofcode is the end of each test case
#             #9: This lineofcode is the end of test case execution part
#             #10: Begin review process of Stub and Isolate functions

#################################################

def ReviewTestCases(allcodes_lst, begin_counter):
    state_st = UNDEFINED_STATE      #1
    TesterDef_lst, ExptCalls_lst, Checked_lst, CalledSeq_lst, VerfCrit_lst = InitList(5)        #2
    
    for LineCounter, LineofCode in enumerate(allcodes_lst[begin_counter:], start = begin_counter+1):
        state_st, statechanged_b = StateMachine_TC(LineofCode, state_st)

        if ((state_st == BEGIN_TEST_CASE) and (statechanged_b)):        #3
            BeginTestCase(LineofCode, LineCounter)
        if (state_st in TO_CHECK_LST):      #4
            Checked_lst.append(state_st)
            if (state_st == TESTERDEFINE_STR):      #5
                TesterDef_lst.append(LineofCode)
            elif (state_st == EXPTCALL):        #6
                ExptCalls_lst.append(LineofCode)
            elif (state_st == VC):      #7
                VerfCrit_lst.append(LineofCode)
        elif ((state_st == END_TEST_CASE) and (statechanged_b)):        #8
            CheckTesterDefine(TesterDef_lst)
            GetCalledSeq(ExptCalls_lst, CalledSeq_lst)
            CheckTOCHECKLIST(Checked_lst, VerfCrit_lst)
        elif (state_st == END_ALL_TEST_CASES):      #9
            break

    ReviewCallInterface(allcodes_lst, CalledSeq_lst , LineCounter)      #10

#################################################

# Name: StateMachine_TC
# Param: LineofCode: each line of code
#        prestate_st: the previous state
# Return: retval: current state
#         retval != prestate_st: boolean variable to indicate state changed or not          
# Description: Detect state for each line of code (only for test cases part)
#              #1: Assign previous state to return value
#              #2: Compare in lower case because tester may use different commments
            
#################################################

def StateMachine_TC(LineofCode, prestate_st):
    retval = prestate_st        #1

    if (isBeginTestCase(LineofCode)):
        retval = BEGIN_TEST_CASE
    elif (isEndTestCase(LineofCode)):
        retval = END_TEST_CASE
    elif (isEndAllTestCases(LineofCode)):
        retval = END_ALL_TEST_CASES
    else:
        for element_to_check in TO_CHECK_LST:
            if (element_to_check.lower() in LineofCode.lower()):        #2
                retval = element_to_check
                break

    return (retval, (retval != prestate_st))


################################################# 

# Name: BeginTestCase
# Param: lineofcode: line of code
#        linecounter: line number
# Return: None
# Description: #1: Get Test case name from the first line of each test case
#                  The test case name is the element between "void" and "(int doIt)" in this string
#                  Ex: "void Fls_Read_Cfg01_InvalidLength(int doIt){" ==> "Fls_Read_Cfg01_InvalidLength"
#              #2: Notify in report the beginning of each test case

#################################################

def BeginTestCase(lineofcode, linecounter):
    tcname_st = (lineofcode.strip())[5:-11]     #1
    ReportContent_lst.append(START_TESTCASE + tcname_st + AT_LINE + str(linecounter) + PROCESSING)      #2
    
################################################# 

# Name: GetCalledSeq
# Param: ExptCalls_lst: stores the contents in EXPECTED_CALLS of each test case
#        CalledSeq_lst: store the called sequences of all test cases in each test script
# Return: None
# Description: This function is invoked at the end of each test case
#              #1: Check whether this line of code is a valid sequence (function with instance name)
#                  The called sequence is obtained between the double quote
#                  Store the called sequence in CalledSeq_lst
#              #2: ClearExptCalls_lst (after each test case)

################################################# 

def GetCalledSeq(ExptCalls_lst, CalledSeq_lst):
    for lineofcode in ExptCalls_lst:
        if (isCalledSeq(lineofcode)):       #1
            calledseq_st = getInsideQuote(lineofcode)       
            if (calledseq_st not in CalledSeq_lst):  
                CalledSeq_lst.append(calledseq_st)      

    ClearList(ExptCalls_lst)        #2

##################################################
   
# Name: CheckTesterDefine
# Param: TesterDef_lst: stores the contents in Tester define of each test case
# Return: None
# Description: This function is invoked at the end of each test case
#              #1: If this line of code is an entity declaration
#                  Remove the semicolon in line of code and get the second element (variable name)
#                  Ex: "uint8 ptr_entity;" ==> "ptr_entity"
#                  Store the variable name in declared list
#              #2: If this line of code is the INITIALIZATION of entity
#                  The variable name is inside brackets "()"
#                  Store varaible name in initialized list
#              #3: For each declared variable, check whether it has been initialized
#                  If not, throw WARNING to report
#              #4: Clear TesterDef_lst (after each test case)

################################################# 

def CheckTesterDefine(TesterDef_lst):
    declared_lst, initialised_lst = InitList(2)

    for lineofcode in TesterDef_lst:
        if (isTesterDefDeclare(lineofcode)):        #1
            varname_st = (lineofcode.split()[1]).replace(SEMICOLON, NO_SPACE)    
            declared_lst.append(varname_st)     
        elif (isTesterDefInit(lineofcode)):     #2
            varname_st = getInsideBracket(lineofcode)       
            initialised_lst.append(varname_st)      

    for declaredvar in declared_lst:    #3
        if declaredvar not in initialised_lst:
            ReportContent_lst.append(WARNING + declaredvar + UNITIALIZED)

    ClearList(TesterDef_lst)        #4

##################################################  

# Name: CheckTOCHECKLIST
# Param: Checked_lst: stores element that has been found
#        VerfCrit_lst: stores the contents of GUID
# Return: None
# Description: This function is invoked at the end of each test case
#              #1: If TO_CHECK_LIST has element that has not been found, throw WARNING to report
#              #2: If GUID exists but has not been mapped, throw WARNING to report
#              #3: Clear Checked_lst, VerfCrit_lst after each test case

##################################################  

def CheckTOCHECKLIST(Checked_lst, VerfCrit_lst):
    for tocheck in TO_CHECK_LST:
        if ((tocheck not in Checked_lst) and (tocheck != TESTERDEFINE_STR)):    #1
            ReportContent_lst.append(WARNING + LACKOF + tocheck)
    
    if (VC in Checked_lst):     #2
        VCmapped_b = False
        for lineofcode in VerfCrit_lst:
            if isVCmapped(lineofcode):
                VCmapped_b = True
                break 
        if not (VCmapped_b):
            ReportContent_lst.append(WARNING + NOVCMAPPED)

    ClearList(Checked_lst, VerfCrit_lst)        #3
    
################################################## 

# Name: ReviewCallInterface
# Param: allcodes_lst: store all lines of code
#        CalledSeq_lst: stores called sequence of all test cases
#        begin_counter: specifies the beginning (index) of Stub/Iso Functions Execution (Call Interface Control)
# Return: None
# Description: Review all test cases in test script
#             #1: Initialize state for each lineofcode
#             #2: This lineofcode is the first line of each function (comment)
#                 Get function name by the 5th element of the string
#                 Ex: "/* Stub for function rba_BswSrv_MemCopy */" ==> "rba_BswSrv_MemCopy"
#                 Boolean fncinused_b indicates whether this function is used
#             #3: Store function declaration
#             #4: Count number of input params
              #5: Process for each instance
#             #6: Notify to report the end of test script file              

#################################################

def ReviewCallInterface(allcodes_lst, CalledSeq_lst, begin_counter):
    ReportContent_lst.append(START_STUBFNC + PROCESSING)

    state_st = UNDEFINED_STATE      #1
    fncinused_b = False
    for LineCounter, LineofCode in enumerate(allcodes_lst[begin_counter:], start = begin_counter+1 ):
        state_st, statechanged_b = StateMachine_StubFnc(LineofCode, state_st, fncinused_b)      

        if ((state_st == BEGINFUNC) and (statechanged_b)):      #2
            fncname_st = (LineofCode.split())[4]
            fncinused_b = CheckUsedFnc(fncname_st, CalledSeq_lst)
        elif (state_st == DECLAREFNC):      #3
            if (statechanged_b):
                FuncDeclare_lst, InstanceContent_lst = InitList(2)
            FuncDeclare_lst.append(LineofCode)
        elif ((state_st == REGISTERCALL) and (statechanged_b)):     #4
            paramcnt_int = CountParam(FuncDeclare_lst)
        elif (state_st == BEGININTSTANCE):
            InstanceContent_lst.append(LineofCode)
        elif ((state_st == ENDINSTANCE) and (statechanged_b)):      #5
            checkInstance(fncname_st, paramcnt_int, InstanceContent_lst, CalledSeq_lst)
        elif (state_st == ENDFUNC):
            fncinused_b = False
        elif (state_st == ENDFILE):     #6
            ReportContent_lst.append(END_C_FILE)        
            break

#################################################

# Name: StateMachine_StubFnc
# Param: LineofCode: each line of code
#        prestate_st: the previous state
#        fncinused_b: indicates function has been used
# Return: retval: current state
#         retval != prestate_st: boolean variable to indicate state changed or not          
# Description: Detect state for each line of code (only for test cases part)
#              #1: Assign previous state to return value
#              #2: Only if this function was used, return DECLAREFNC

################################################

def StateMachine_StubFnc(LineofCode, prestate_st, fncinused_b):
    retval = prestate_st        #1

    if (isBeginStubFunc(LineofCode)):
        retval = BEGINFUNC
    elif ((prestate_st == BEGINFUNC) and (isNotComment(LineofCode)) and (fncinused_b)):     #2
        retval = DECLAREFNC
    elif (isRegisterCall(LineofCode) and (fncinused_b)):
        retval = REGISTERCALL
    elif (isBeginInstance(LineofCode) and (fncinused_b)):
        retval = BEGININTSTANCE
    elif ((prestate_st == BEGININTSTANCE)) and (isEndInstance(LineofCode)):
        retval = ENDINSTANCE
    elif (isEndStubFunction(LineofCode)):
        retval = ENDFUNC
    elif (isEndFile(LineofCode)):
        retval = ENDFILE
    
    return (retval, (retval != prestate_st))


#################################################


def CheckUsedFnc(fncname_st, CalledSeq_lst) -> bool:
    for sequence in CalledSeq_lst:
        if (fncname_st in sequence):
            return True
    return False


#################################################


def checkInstance(fncname_st, paramcnt_int, InstanceContent_lst, CalledSeq_lst):
    checkcnt_int = 0
    for lineofcode in InstanceContent_lst:
        if (isBeginInstance(lineofcode)):
            instancename_st = getInsideBracket(lineofcode)
        checkcnt_int += lineofcode.count(CHECK_PARAM)

    seqname_st = fncname_st + HASH + instancename_st
    if (seqname_st not in CalledSeq_lst):
        return
    elif (checkcnt_int < paramcnt_int):
        ReportContent_lst.append(WARNING + LACKOF + PARAMETER_CHECK + instancename_st + OF_FUNCTION + fncname_st)

    ClearList(InstanceContent_lst)


#################################################


def CountParam(FuncDeclare_lst) -> int:
    fncdeclare_st = NO_SPACE.join(FuncDeclare_lst)
    fncdeclare_st  = fncdeclare_st.replace(SPACE, NO_SPACE).replace(LINE_BREAK, NO_SPACE)
    inputparam_st = getInsideBracket(fncdeclare_st)
    commacnt_int = fncdeclare_st.count(COMMA)

    if (commacnt_int > 0): 
        paramcnt_int = commacnt_int + 1
    else:
        if not (inputparam_st): paramcnt_int = 0
        else: paramcnt_int = 1

    ClearList(FuncDeclare_lst)
    return paramcnt_int


#################################################
