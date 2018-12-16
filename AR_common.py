SPACE = ' '
NO_SPACE = ''
LINE_BREAK = '\n'
COMMA = ','
SEMICOLON = ';'
DOUBLE_QUOTE = '"'
OPEN_PAREN = '('
CLOSE_PAREN = ')'
HASH = '#'

#################################################

def Export_Report(report_name, report_content):
    txt_file = open(report_name, 'w')
    for content in report_content:
        print(content)
        txt_file.write(content)
    txt_file.close()
    del txt_file
        
#################################################


def Init_List(numberoflists) -> list:
    if (numberoflists > 1):
        return ([] for _ in range(numberoflists))
    else: return []


#################################################


def Clear_List(*all_list) -> list:
    for lst in all_list:
        lst.clear()


#################################################
