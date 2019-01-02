import os
from Common_Def import *
from Common_API import *
from Script_Report_Def import *
from Script_API import *


#################################################


def Script_MainFunction(inputdir_st, reportname_st):
    global ReportContent_lst
    ReportContent_lst = InitList(1)

    TargetDir_st = inputdir_st + TEST_SCRIPT_DIR
    ScriptDir_lst = GetScriptList(TargetDir_st)

    for scriptdir in ScriptDir_lst:
        ScanTestScript(scriptdir)

    Export_Report(reportname_st, ReportContent_lst)

#################################################


def GetScriptList(TargetDir_st):
    Cfile_lst = InitList(1)

    for path, subdirs, files in os.walk(TargetDir_st):
        for filename in files:
            if filename.endswith('.c'):
                filepath = os.path.join(path, filename)
                Cfile_lst.append(filepath)
    if not (Cfile_lst):
        ReportContent_lst.append(NO_SCRIPT_FOUND)

    return Cfile_lst


#################################################


def ScanTestScript(scriptdir):
    ReportContent_lst.append(START_C_FILE + scriptdir + PROCESSING)
    try:
        Cfile_temp = open(scriptdir, 'r')
        allcodes_lst = Cfile_temp.readlines()
        Cfile_temp.close()
        del Cfile_temp
    except:
        ReportContent_lst.append(UNABLE_OPEN_SCRIPT)
        ReportContent_lst.append(END_C_FILE)
        return

    for LineCounter, LineofCode in enumerate(allcodes_lst, start = 1):
        if (isEndDeclareTestCases(LineofCode)):
            break

    ReviewTestCase(allcodes_lst, LineCounter)

#################################################


def ReviewTestCase(allcodes_lst, begin_counter):
    state_st = UNDEFINED_STATE
    TesterDef_lst, ExptCalls_lst, Checked_lst, CalledSeq_lst, VerfCrit_lst = InitList(5)
    
    for LineCounter, LineofCode in enumerate(allcodes_lst[begin_counter:], start = begin_counter+1):
        state_st, statechanged_b = StateMachine_TC(LineofCode, state_st)

        if ((state_st == BEGIN_TEST_CASE) and (statechanged_b)):
            BeginTestCase(LineofCode, LineCounter)
        if (state_st in TO_CHECK_LST):
            Checked_lst.append(state_st)
            if (state_st == TESTERDEFINE_STR): 
                TesterDef_lst.append(LineofCode)
            elif (state_st == EXPTCALL): 
                ExptCalls_lst.append(LineofCode)
            elif (state_st == VC): 
                VerfCrit_lst.append(LineofCode)
        elif ((state_st == END_TEST_CASE) and (statechanged_b)):
            CheckTesterDefine(TesterDef_lst)
            GetCalledSeq(ExptCalls_lst, CalledSeq_lst)
            CheckTOCHECKLIST(Checked_lst, VerfCrit_lst)
        elif (state_st == END_ALL_TEST_CASES):
            break

    ReviewCallInterface(allcodes_lst, CalledSeq_lst , LineCounter)


#################################################


def StateMachine_TC(LineofCode, prestate_st):
    retval = prestate_st

    if (isBeginTestCase(LineofCode)):
        retval = BEGIN_TEST_CASE
    elif (isEndTestCase(LineofCode)):
        retval = END_TEST_CASE
    elif (isEndAllTestCases(LineofCode)):
        retval = END_ALL_TEST_CASES
    else:
        for element_to_check in TO_CHECK_LST:
            if (element_to_check.lower() in LineofCode.lower()):
                retval = element_to_check
                break

    return (retval, (retval != prestate_st))


################################################# 


def BeginTestCase(lineofcode, linecounter):
    TestCase_name = (lineofcode.strip())[5:-11]
    ReportContent_lst.append(START_TESTCASE + TestCase_name + AT_LINE + str(linecounter) + PROCESSING)

    
################################################# 


def GetCalledSeq(ExptCalls_lst, CalledSeq_lst):
    for lineofcode in ExptCalls_lst:
        if (isCalledSeq(lineofcode)):
            calledseq_st = getInsideQuote(lineofcode)
            CalledSeq_lst.append(calledseq_st)

    ClearList(ExptCalls_lst)


##################################################
   

def CheckTesterDefine(TesterDef_lst):
    declared_lst, initialised_lst = InitList(2)

    for lineofcode in TesterDef_lst:
        if (isTesterDefDeclare(lineofcode)):
            varname_st = (lineofcode.split()[1]).replace(SEMICOLON, NO_SPACE)
            declared_lst.append(varname_st)
        elif (isTesterDefInit(lineofcode)):
            varname_st = getInsideBracket(lineofcode)
            initialised_lst.append(varname_st)

    for declaredvar in declared_lst:
        if declaredvar not in initialised_lst:
            ReportContent_lst.append(WARNING + declaredvar + UNITIALIZED)

    ClearList(TesterDef_lst)


##################################################  


def CheckTOCHECKLIST(Checked_lst, VerfCrit_lst):
    for tocheck in TO_CHECK_LST:
        if ((tocheck not in Checked_lst) and (tocheck != TESTERDEFINE_STR)):
            ReportContent_lst.append(WARNING + LACKOF + tocheck)
    
    if (VC in Checked_lst):
        VCmapped_b = False
        for lineofcode in VerfCrit_lst:
            if isVCmapped(lineofcode):
                VCmapped_b = True
                break 
        if not (VCmapped_b):
            ReportContent_lst.append(WARNING + NOVCMAPPED)

    ClearList(Checked_lst, VerfCrit_lst)
    

##################################################  


def ReviewCallInterface(allcodes_lst, CalledSeq_lst, begin_counter):
    ReportContent_lst.append(START_STUBFNC + PROCESSING)
    state_st = UNDEFINED_STATE
    fncinused_b = False
    for LineCounter, LineofCode in enumerate(allcodes_lst[begin_counter:], start = begin_counter+1 ):
        state_st, statechanged_b = StateMachine_StubFnc(LineofCode, state_st, fncinused_b)

        if ((state_st == BEGINFUNC) and (statechanged_b)):
            fncname_st = (LineofCode.split())[4]
            fncinused_b = CheckUsedFnc(fncname_st, CalledSeq_lst)
        elif (state_st == DECLAREFNC):
            if (statechanged_b):
                FuncDeclare_lst, InstanceContent_lst = InitList(2)
            FuncDeclare_lst.append(LineofCode)
        elif ((state_st == REGISTERCALL) and (statechanged_b)):
            paramcnt_int = CountParam(FuncDeclare_lst)
        elif (state_st == BEGININTSTANCE):
            InstanceContent_lst.append(LineofCode)
        elif ((state_st == ENDINSTANCE) and (statechanged_b)):
            checkInstance(fncname_st, paramcnt_int, InstanceContent_lst, CalledSeq_lst)
        elif (state_st == ENDFUNC):
            fncinused_b = False
        elif (state_st == ENDFILE):
            ReportContent_lst.append(END_C_FILE)
            break

        
#################################################


def StateMachine_StubFnc(LineofCode, prestate_st, fncinused_b):
    retval = prestate_st

    if (isBeginStubFunc(LineofCode)):
        retval = BEGINFUNC
    elif ((prestate_st == BEGINFUNC) and (isNotComment(LineofCode)) and (fncinused_b)):
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
    Checkcnt_int = 0
    for lineofcode in InstanceContent_lst:
        if (isBeginInstance(lineofcode)):
            instancename_st = getInsideBracket(lineofcode)
        Checkcnt_int += lineofcode.count(CHECK_PARAM)

    seqname_st = fncname_st + HASH + instancename_st
    if (seqname_st not in CalledSeq_lst):
        return
    elif (Checkcnt_int < paramcnt_int):
        ReportContent_lst.append(WARNING + LACKOF + PARAMETER_CHECK + instancename_st + OF_FUNCTION + fncname_st)

    ClearList(InstanceContent_lst)


#################################################


def CountParam(FuncDeclare_lst):
    FuncDeclare_st = NO_SPACE.join(FuncDeclare_lst)
    FuncDeclare_st  = FuncDeclare_st.replace(SPACE, NO_SPACE).replace(LINE_BREAK, NO_SPACE)
    inputparam_st = getInsideBracket(FuncDeclare_st)
    comma_cnt_int = FuncDeclare_st.count(COMMA)

    if (comma_cnt_int > 0): 
        paramcnt_int = comma_cnt_int + 1
    else:
        if not (inputparam_st): paramcnt_int = 0
        else: paramcnt_int = 1

    ClearList(FuncDeclare_lst)
    return paramcnt_int


#################################################
