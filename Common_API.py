from Common_Def import *

#################################################

def Export_Report(report_name, report_content):
    txt_file = open(report_name, 'w')
    for content in report_content:
        print(content)
        txt_file.write(content)
    txt_file.close()
    del txt_file
        
#################################################


def InitList(numberoflists) -> list:
    if (numberoflists > 1):
        return ([] for _ in range(numberoflists))
    else: return []


#################################################


def ClearList(*all_list) -> list:
    for lst in all_list:
        lst.clear()


#################################################

def getInsideQuote(lineofcode_st) -> str:
    if (lineofcode_st.count(DOUBLE_QUOTE) == 2):
        beginidx_int: int = lineofcode_st.find(DOUBLE_QUOTE) + 1
        endidx_int: int = lineofcode_st.rfind(DOUBLE_QUOTE)
        inside_str: str = lineofcode_st[beginidx_int:endidx_int]
        inside_str = inside_str.replace(SEMICOLON, NO_SPACE)
        return inside_str
    return None


#################################################


def getInsideBracket(lineofcode_st) -> str:
    if ((OPEN_PAREN and CLOSE_PAREN) in lineofcode_st):
        beginidx_int: int = lineofcode_st.find(OPEN_PAREN) + 1
        endidx_int: int = lineofcode_st.rfind(CLOSE_PAREN)
        inside_str: str = lineofcode_st[beginidx_int:endidx_int]
        inside_str = inside_str.replace(DOUBLE_QUOTE, NO_SPACE)
        return inside_str
    return None


#################################################