
TEST_SCRIPT_DIR: str = "/02_TestScript"



############################################################################

START_C_FILE: str = "Checking file: "
END_C_FILE: str = "\n\n*********************************************************\n\n"
NO_SCRIPT_FOUND: str = "\nCannot find any Test Script file.\nThe tool stopped here.\n"
UNABLE_OPEN_SCRIPT: str = "\nCannot open Test Script file. The tool stopped here.\n"
START_TESTCASE: str = "\n\nChecking Test Case: "
START_STUBFNC: str = "\n\nChecking Call Interface Control"
PARAMETER_CHECK: str = "parameters check in INSTANCE "
OF_FUNCTION: str = " of Function "
AT_LINE: str = " at line "
WARNING: str = "\n- WARNING: "
UNITIALIZED: str = " was not INITIALISED"
LACKOF: str = "Lack of "
NOVCMAPPED: str = "No VC was mapped"
PROCESSING: str = "..."

############################################################################

TESTMETHOD_STR: str = "Test Method"
TESTERDEFINE_STR: str = "Tester Define"
TESTCASEDECLARE_STR: str = "Test case data declarations"
SETGLOBALDATA_STR: str = "Set global data"
INITGLOBAL: str = "initialise_global_data()"
SETEXPTGLOBAL_STR: str = "Set expected values for global data checks"
INITEXPTGLOBAL: str = "initialise_expected_global_data()"
EXPTCALL_STR: str = "Expected call sequence"
EXPTCALL: str = "EXPECTED_CALLS"
CALLSUT_STR: str = "Call SUT"
TESTCASECHECK: str = "Test case checks"
EXPTRESULT: str = "Expected Result"
CHECKGLOBAL_STR: str = "Checks on global data"
CHECKGLOBAL: str = "check_global_data"
VC: str = "GUID"
TO_CHECK_LST: str = [ TESTMETHOD_STR, TESTERDEFINE_STR, TESTCASEDECLARE_STR, SETGLOBALDATA_STR,
                INITGLOBAL, SETEXPTGLOBAL_STR, INITEXPTGLOBAL,
                EXPTCALL_STR, EXPTCALL, CALLSUT_STR, TESTCASECHECK, EXPTRESULT,
                CHECKGLOBAL_STR, CHECKGLOBAL, VC]

BEGIN_TEST_CASE: str = "Begin Test Case"
END_TEST_CASE: str = "End Test Case"
END_ALL_TEST_CASES: str = "End of Checking Test Cases"
UNDEFINED_STATE: str = "Undefined"

############################################################################

BEGINFUNC: str = "Begin Stub Function"
DECLAREFNC: str = "Stub Function Declaration"
REGISTERCALL: str = "REGISTER CALL"
BEGININTSTANCE: str = "Begin INSTANCE"
CHECK_PARAM: str = "CHECK_"
ENDINSTANCE: str = "End INSTANCE"
ENDFILE: str = "End Test Script file"
ENDFUNC: str = "End Stub Function"

############################################################################

