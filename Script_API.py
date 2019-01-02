#################################################

def isTesterDefDeclare(lineofcode) -> bool:
    if (('INITIALISE' not in lineofcode) and ('_entity' in lineofcode) and ('=' not in lineofcode) and ('[' not in lineofcode)
        and (isNotComment(lineofcode))): return True
    else: return False

def isTesterDefInit(lineofcode) -> bool:
    if (('INITIALISE' in lineofcode) and (('_entity') in lineofcode) and (isNotComment(lineofcode))): return True
    else: return False

def isTestScriptWarning(lineofcode)-> bool:
    if (('TEST_SCRIPT_WARNING' in lineofcode) and (isNotComment(lineofcode))): return True
    else: return False

def isBeginDeclareTestCases(lineofcode)-> bool:
    if (('void run_tests()' in lineofcode) and (';' not in lineofcode)): return True
    else: return False

def isEndDeclareTestCases(lineofcode)-> bool:
    if ('EXPORT_COVERAGE' in lineofcode): return True
    else: return False

def isUsedTestCase(lineofcode)-> bool:
    if (('(1)' in lineofcode) and (isNotComment(lineofcode))): return True
    else: return False

def isBeginTestCase(lineofcode)-> bool:
    if (('void' in lineofcode) and ('int doIt' in lineofcode)): return True
    else: return False

def isCalledSeq(lineofcode)-> bool:
    if ((lineofcode.count('"') == 2) and ('#' in lineofcode)): return True
    else: return False

def isVCmapped(lineofcode)-> bool:
    if ((('{' in lineofcode) and ('}' in lineofcode)) or ('Not Applicable' in lineofcode)): return True
    else: return False

def isEndTestCase(lineofcode)-> bool:
    if ('END_TEST();') in lineofcode: return True
    else: return False

def isEndAllTestCases(lineofcode)-> bool:
    if ('Call Interface Control') in lineofcode: return True
    else: return False

def isBeginStubFunc(lineofcode)-> bool:
    if (('Stub for function' in lineofcode) or ('Isolate for function' in lineofcode)): return True
    else: return False

def isRegisterCall(lineofcode)-> bool:
    if ('REGISTER_CALL' in lineofcode): return True
    else:  return False

def isBeginInstance(lineofcode)-> bool:
    if ('IF_INSTANCE' in lineofcode): return True
    else: return False

def isEndInstance(lineofcode)-> bool:
    if ('return' in lineofcode): return True
    else: return False

def isEndStubFunction(lineofcode)-> bool:
    if ('LOG_SCRIPT_ERROR' in lineofcode): return True
    else: return False

def isEndFile(lineofcode)-> bool:
    if ('End of test script' in lineofcode): return True
    else: return False

def isNotComment(lineofcode)-> bool:
    if (('//' not in lineofcode) and ('/*' not in lineofcode) and ('*/' not in lineofcode)): return True
    else: return False

        
#################################################