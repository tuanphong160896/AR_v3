import os
from AR_common import *
from AR_Script_report import *
from AR_Script_lib import *


#################################################


def main_Script(input_dir, report_name):
    global report_content
    report_content = Init_List(1)

    script_dir = input_dir + TEST_SCRIPT_DIR
    list_dir_script = findScriptdir(script_dir)

    for dir_script in list_dir_script:
        ScanTestScript(dir_script)

    Export_Report(report_name, report_content)


#################################################


def findScriptdir(script_dir):
    Cfile_lst = Init_List(1)

    for path, subdirs, files in os.walk(script_dir):
        for filename in files:
            if filename.endswith('.c'):
                filepath = os.path.join(path, filename)
                Cfile_lst.append(filepath)
    if not (Cfile_lst):
        report_content.append(NO_SCRIPT_FOUND)

    return Cfile_lst


#################################################


def ScanTestScript(dir_script):
    report_content.append(START_C_FILE + dir_script + PROCESSING)
    try:
        C_file = open(dir_script, 'r')
        all_codes = C_file.readlines()
        C_file.close()
        del C_file
    except:
        report_content.append(UNABLE_OPEN_SCRIPT)
        report_content.append(END_C_FILE)
        return

    for LineCounter, LineofCode in enumerate(all_codes, start = 1):
        if (isEndDeclareTestCases(LineofCode)):
            break
    ReviewTestScript(all_codes, LineCounter)

#################################################


def ReviewTestScript(all_codes, begin_counter):
    state = UNDEFINED_STATE
    TesterDef_lst, ExptCalls_lst, Checked_lst, CalledSeq_lst, VerfCrit_lst = Init_List(5)
    
    for LineCounter, LineofCode in enumerate(all_codes[begin_counter:], start = begin_counter+1):
        pre_state = state
        state = state_machine(LineofCode, Checked_lst, pre_state)
        if ((state == BEGIN_TEST_CASE) and (pre_state != state)):
            BeginTestCase(LineofCode, LineCounter)
        elif (state == TESTERDEFINE_STR):
            TesterDef_lst.append(LineofCode)
        elif (state == EXPTCALL):
            ExptCalls_lst.append(LineofCode)
        elif (state == VC):
            VerfCrit_lst.append(LineofCode)
        elif ((state == END_TEST_CASE) and (pre_state != state)):
            checkTesterDef(TesterDef_lst)
            getCalledSeq(ExptCalls_lst, CalledSeq_lst)
            check_TO_CHECK_LST(Checked_lst, VerfCrit_lst)
        elif (state == END_ALL_TEST_CASES):
            break

    Review_Call_Interface(all_codes, CalledSeq_lst , LineCounter)


#################################################


def state_machine(LineofCode, Checked_lst, pre_state):
    retval = pre_state

    if (isBeginTestCase(LineofCode)):
        retval = BEGIN_TEST_CASE
    elif (isEndTestCase(LineofCode)):
        retval = END_TEST_CASE
    elif (isEndAllTestCases(LineofCode)):
        retval = END_ALL_TEST_CASES
    else:
        for element_to_check in TO_CHECK_LST:
            if (element_to_check.lower() in LineofCode.lower()):
                Checked_lst.append(element_to_check)
                retval = element_to_check
                break

    return retval


################################################# 


def BeginTestCase(lineofcode, linecounter):
    TestCase_name = (lineofcode.strip())[5:-11]
    report_content.append(START_TESTCASE + TestCase_name + AT_LINE + str(linecounter) + PROCESSING)

    
################################################# 


def getCalledSeq(ExptCalls_lst, CalledSeq_lst):
    for lineofcode in ExptCalls_lst:
        if (isCalledSeq(lineofcode)):
            calledseq = getInsideQuote(lineofcode)
            CalledSeq_lst.append(calledseq)

    Clear_List(ExptCalls_lst)


##################################################
   

def checkTesterDef(TesterDef_lst):
    list_Declare, list_Init = Init_List(2)

    for lineofcode in TesterDef_lst:
        if (isTesterDefDeclare(lineofcode)):
            var_Declare = (lineofcode.split()[1]).replace(SEMICOLON, NO_SPACE)
            list_Declare.append(var_Declare)
        elif (isisTesterInit(lineofcode)):
            var_Init = getInsideBracket(lineofcode)
            list_Init.append(var_Init)

    for elem in list_Declare:
        if elem not in list_Init:
            report_content.append(WARNING + elem + UNITIALIZED)

    Clear_List(TesterDef_lst)


##################################################  


def check_TO_CHECK_LST(Checked_lst, VerfCrit_lst):
    for tocheck in TO_CHECK_LST:
        if tocheck not in Checked_lst:
            report_content.append(WARNING + LACKOF + tocheck)
    
    if (VC in Checked_lst):
        VCmapped_check = 0
        for lineofcode in VerfCrit_lst:
            if isVC(lineofcode):
                VCmapped_check = 1
                break 
        if not (VCmapped_check):
            report_content.append(WARNING + NOVCMAPPED)

    Clear_List(Checked_lst, VerfCrit_lst)
    

##################################################  


def Review_Call_Interface(all_codes, CalledSeq_lst, begin_counter):
    report_content.append(START_STUBFNC + PROCESSING)
    state = UNDEFINED_STATE
    fnc_used = 0
    for LineCounter, LineofCode in enumerate(all_codes[begin_counter:], start = begin_counter+1 ):
        pre_state = state
        state = state_machine_stub_functions(LineofCode, pre_state, fnc_used)

        if ((state == BEGINFUNC) and (pre_state != state)):
            fncname = (LineofCode.split())[4]
            fnc_used = checkusedfnc(fncname, CalledSeq_lst)
            FncDec_lst, InstContent_lst = Init_List(2)
        elif (state == DECLAREFNC):
            FncDec_lst.append(LineofCode)
        elif ((state == REGISTERCALL) and (pre_state != state)):
            param_count = CountParam(FncDec_lst)
        elif (state == BEGININTSTANCE):
            InstContent_lst.append(LineofCode)
        elif ((state == ENDINSTANCE) and (pre_state != state)):
            checkInstance(fncname, param_count, InstContent_lst, CalledSeq_lst)
        elif (state == ENDFUNC):
            fnc_used = 0
        elif (state == ENDFILE):
            report_content.append(END_C_FILE)
            break

        
#################################################


def state_machine_stub_functions(LineofCode, pre_state, fnc_used):
    retval = pre_state

    if (isBeginStubFunc(LineofCode)):
        retval = BEGINFUNC
    elif ((pre_state == BEGINFUNC) and (isNotComment(LineofCode)) and (fnc_used)):
        retval = DECLAREFNC
    elif (isRegisterCall(LineofCode) and (fnc_used)):
        retval = REGISTERCALL
    elif (isBeginInstance(LineofCode) and (fnc_used)):
        retval = BEGININTSTANCE
    elif ((pre_state == BEGININTSTANCE)) and (isEndInstance(LineofCode)):
        retval = ENDINSTANCE
    elif (isEndStubFunction(LineofCode)):
        retval = ENDFUNC
    elif (isEndFile(LineofCode)):
        retval = ENDFILE
    
    return retval


#################################################


def checkusedfnc(fncname, CalledSeq_lst) -> bool:
    for elem in CalledSeq_lst:
        if (fncname in elem):
            return True
    return False


#################################################


def checkInstance(fncname, param_count, InstContent_lst, CalledSeq_lst):
    check_count = 0
    for elem in InstContent_lst:
        if (isBeginInstance(elem)):
            inst_name = getInsideBracket(elem)
        check_count += elem.count(CHECK_PARAM)

    seq_name = fncname + HASH + inst_name
    if (seq_name not in CalledSeq_lst):
        return
    elif (check_count < param_count):
        report_content.append(WARNING + LACKOF + PARAMETER_CHECK + inst_name + OF_FUNCTION + fncname)

    Clear_List(InstContent_lst)

#################################################


def CountParam(FncDec_lst) -> int:
    FncDec_str = NO_SPACE.join(FncDec_lst)
    FncDec_str = FncDec_str.replace(SPACE, NO_SPACE).replace(LINE_BREAK, NO_SPACE)
    input_param = getInsideBracket(FncDec_str)
    comma_count = FncDec_str.count(COMMA)

    if (comma_count > 0): 
        param_count = comma_count + 1
    else:
        if not (input_param): param_count = 0
        else: param_count = 1

    Clear_List(FncDec_lst)
    return param_count


#################################################
