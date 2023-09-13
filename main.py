from bs4 import BeautifulSoup as BS
import re
import sys
import os

# regular expression for extracting subject information
SUBJECT_REGEX = re.compile(r'\[(\w+)\](.+)｛(\d+-\d+)周\[教师:(\w+),地点:(\d+-\d+)\]｝')

# subject information
class Subject(object):
    def __init__(self, str, weekday, start, rowspan) -> None:
        tmp_m = SUBJECT_REGEX.findall(str)[0]
        self.name = tmp_m[1]
        self.weekday = weekday
        self.start = start
        self.end = start + rowspan - 1
        self.weektime = tmp_m[2]
        self.teacher = tmp_m[3]
        self.dst = f'{tmp_m[0]}{tmp_m[4]}'

    # this method return a csv row which stands for this subject
    def to_csv(self) -> str:
        return f'{self.name},{self.weekday},{self.start},{self.end},{self.teacher},{self.dst},{self.weektime}\n'

if __name__ == "__main__":
    # find the html file path
    html_path = ''
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
    else:
        for root, dirs, files in os.walk('.'):
            for name in files:
                if name == 'loging.html':
                    html_path = os.path.join(root,name)
    try :
        with open(html_path, 'r', encoding='utf8') as f:
            soup = BS(f.read(), 'html.parser')
    except Exception as e:
        print(e)
        print("can't get html file")
        sys.exit()
    
    # find the table in html file
    table = soup.find('table',class_='Grid_Line')
    # table row
    trs = table.find_all('tr')
    # subject_tables saves all your subject
    subject_tables = list()
    # record the skiped weekday in a table row
    td_void = [0,0,0,0,0,0,0]
    for section in range(1,16):
        tds = trs[section].find_all('td')
        tds.pop(0)
        weekday = 0
        for td in tds:
            weekday += 1 if td_void[weekday] != 0 else 0
            td_attrs = td.attrs
            if 'rowspan' in td_attrs and int(td_attrs['rowspan']) > 1:
                rowspan = int(td_attrs['rowspan'])
                sub = Subject(td.text.strip(), weekday+1, section, rowspan)
                subject_tables.append(sub.to_csv())
                td_void[weekday] = rowspan
            weekday += 1
        for i in range(0,7):
            if td_void[i] != 0:
                td_void[i] -= 1
    
    # export csv file
    try: 
        with open('./kb.csv', 'w+', encoding='utf8') as f:
            f.write("课程名称,星期,开始节数,结束节数,老师,地点,周数\n")
            f.writelines(subject_tables)
            print(f'{len(subject_tables)} subjects hava been exported')
    except Exception as e:
        print(e)
        print("can't wirte csv file")
