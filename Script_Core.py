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


def Script_MainFunction(inputdir_st, reportname_st) -> None:
    global ReportContent_lst        #1 
    ReportContent_lst = InitList(1)

    ScriptDir_st = inputdir_st + TEST_SCRIPT_DIR    #2
    ScriptFile_lst = GetScriptList(ScriptDir_st)     #3

    for scriptdir in ScriptFile_lst:     #4
        OpenTestScript(scriptdir)

    Export_Report(reportname_st, ReportContent_lst)     #5


#################################################

# Name: GetScriptList
# Param: ScriptDir_st: directory to 02_TestScript folder
# Return: allfiles_lst: list to store all directories of .c files
# Description: #1: Initialize return list
#              #2: For given directory, browse all .c files in all sub-dirs and store their directories in allfiles_lst
#              #3: If no .c file found, throw WARNING to report

#################################################


def GetScriptList(ScriptDir_st) -> list:
    allfiles_lst = InitList(1)     #1

    for path, subdirs, files in os.walk(ScriptDir_st):      #2
        for filename in files:
            if filename.endswith('.c'):
                filepath = os.path.join(path, filename)
                allfiles_lst.append(filepath)
    if not (allfiles_lst):     #3
        ReportContent_lst.append(NO_SCRIPT_FOUND)

    return allfiles_lst


#################################################

# Name: OpenTestScript
# Param: scriptdir: directory to each test script
# Return: None
# Description: Beginning review process
#              #1: Notify in report the beginning of each test script
#              #2: Open .c file, store all lines of code in allcodes_lst, then close it.
#              #3: Throw WARNING if unable to open file (nearly impossible to occur)
#              #4: Scan every line of code until the end of test case declaration, the LineCounter stopped here
#              #5: Start Review test case from the LineCounter line

#################################################


def OpenTestScript(scriptdir) -> None:
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


def ReviewTestCases(allcodes_lst, begin_counter) -> None:
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


def GetCalledSeq(ExptCalls_lst, CalledSeq_lst) -> None:
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


def CheckTesterDefine(TesterDef_lst) -> None:
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


def CheckTOCHECKLIST(Checked_lst, VerfCrit_lst) -> None:
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
#                 Boolean fncinused_b indicates whether this stub/isolate function is used
#             #3: Store function declaration
#             #4: Count number of input params
#              #5: Process for each instance
#             #6: Notify to report the end of test script file              

#################################################


def ReviewCallInterface(allcodes_lst, CalledSeq_lst, begin_counter) -> None:
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
            CheckFncInstance(fncname_st, paramcnt_int, InstanceContent_lst, CalledSeq_lst)
        elif (state_st == ENDFUNC):
            fncinused_b = False
        elif (state_st == ENDFILE):     #6
            ReportContent_lst.append(END_C_FILE)        
            break


#################################################

# Name: StateMachine_StubFnc
# Param: LineofCode: each line of code
#        prestate_st: the previous state
#        fncinused_b: indicates function has been used or not
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

# Name: CheckUsedFnc
# Param: fncname_st: stub/isolate function name
#        CalledSeq_lst: store the called sequences of all test cases in each test script
# Return: True: stub/isolate function has been used in test cases
#         False: stub/isolate function has never been used  
# Description: Get each stub/isolate function name and compare with list of used functions in test cases

################################################


def CheckUsedFnc(fncname_st, CalledSeq_lst) -> bool:
    for sequence in CalledSeq_lst:
        if (fncname_st in sequence):
            return True
    return False


#################################################

# Name: CheckFncInstance
# Param: fncname_st: stub/isolate function name
#        paramcnt_int: number of input params of stub/isolate function
#        InstanceContent_lst: store contents of each INSTANCE in stub/isolate function
#        CalledSeq_lst: store the called sequences of all test cases in each test script
# Return: None
# Description: Check if this INSTANCE has CHECKED enough input params or not
#              #1: count number of keywords 'CHECK' in this INSTANCE
#              #2: get sequence name = Function name + # + Instance name (Expected call)
#              #3: check if this sequence is in CalledSeq_lst (used in Test cases)
#                  If used and this instance did not have enough CHECK, notify in report

################################################


def CheckFncInstance(fncname_st, paramcnt_int, InstanceContent_lst, CalledSeq_lst) -> None:
    checkcnt_int = 0
    for lineofcode in InstanceContent_lst:      #1
        if (isBeginInstance(lineofcode)):
            instancename_st = getInsideBracket(lineofcode)
        checkcnt_int += lineofcode.count(CHECK_PARAM)

    seqname_st = fncname_st + HASH + instancename_st        #2

    if (seqname_st not in CalledSeq_lst):       #3
        return
    elif (checkcnt_int < paramcnt_int):
        ReportContent_lst.append(WARNING + LACKOF + PARAMETER_CHECK + instancename_st + OF_FUNCTION + fncname_st)

    ClearList(InstanceContent_lst)


#################################################

# Name: CountParam
# Param: FuncDeclare_lst: store contents of stub/isolate functions declaration
# Return: paramcnt_int: number of input of input params of this function
# Description: #1: convert from list to string
#              #2: get contents inside brackets, which are input params declaration
#              #3: count number of commmas in param declaration
#              #4: If inputparam_st is empty, function has no input param
#                  Else, and no comma found, function has one input param

#################################################


def CountParam(FuncDeclare_lst) -> int:
    fncdeclare_st = NO_SPACE.join(FuncDeclare_lst)      #1
    fncdeclare_st  = fncdeclare_st.replace(SPACE, NO_SPACE).replace(LINE_BREAK, NO_SPACE)
    inputparam_st = getInsideBracket(fncdeclare_st)     #2
    commacnt_int = fncdeclare_st.count(COMMA)       #3

    if (commacnt_int > 0):
        paramcnt_int = commacnt_int + 1
    else:       #4
        if not (inputparam_st): paramcnt_int = 0
        else: paramcnt_int = 1

    ClearList(FuncDeclare_lst)
    return paramcnt_int


#################################################