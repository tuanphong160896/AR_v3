from Common_Def import *

#################################################

def Export_Report(reportname_st, reportcontent_lst):
    txt_file = open(reportname_st, 'w')
    for eachline in reportcontent_lst:
        print(eachline)
        txt_file.write(eachline)
    txt_file.close()
    del txt_file
        
#################################################


def InitList(listnum_int) -> list:
    if (listnum_int > 1):
        return ([] for _ in range(listnum_int))
    else: return []


#################################################


def ClearList(*all_list) -> list:
    for lst in all_list:
        lst.clear()


#################################################

def getInsideQuote(lineofcode) -> str:
    if (lineofcode.count(DOUBLE_QUOTE) == 2):
        beginidx_int: int = lineofcode.find(DOUBLE_QUOTE) + 1
        endidx_int: int = lineofcode.rfind(DOUBLE_QUOTE)
        inside_st: str = lineofcode[beginidx_int:endidx_int]
        inside_st = inside_st.replace(SEMICOLON, NO_SPACE)
        return inside_st
    return None


#################################################


def getInsideBracket(lineofcode) -> str:
    if ((OPEN_PAREN and CLOSE_PAREN) in lineofcode):
        beginidx_int: int = lineofcode.find(OPEN_PAREN) + 1
        endidx_int: int = lineofcode.rfind(CLOSE_PAREN)
        inside_st: str = lineofcode[beginidx_int:endidx_int]
        inside_st = inside_st.replace(DOUBLE_QUOTE, NO_SPACE)
        return inside_st
    return None


#################################################