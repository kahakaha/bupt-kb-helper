from bs4 import BeautifulSoup as BS
import re
import sys
import os
import argparse

# regular expression for extracting subject information
SUBJECT_REGEX = re.compile(r'\[(\w+)\](.+)｛(\d+-\d+)周\[教师:(\w+),地点:(.+)\]｝')
# argument parser
PARSER = argparse.ArgumentParser(
    prog='bupt-kb-helper',
    description="This script helps graduate students from BUPT import their subject into WakeUp App"
)
PARSER.add_argument('-i', '--input', default='', help='html file path,  declare it or let script find itself')
PARSER.add_argument('-t', '--type', choices=['csv', 'ics'], default='csv', help='output file type, default is csv')
PARSER.add_argument('-o', '--output', default='kb', help='output file name, default is kb')

# subject information
class Subject(object):
    def __init__(self, str, weekday, start, rowspan) -> None:
        tmp_m = SUBJECT_REGEX.findall(str)[0]
        self.name = tmp_m[1]
        self.weekday = weekday
        self.start = start
        self.end = start + rowspan - 1
        self.week_number = tmp_m[2]
        self.teacher = tmp_m[3]
        self.dst = f'{tmp_m[0]}{tmp_m[4]}'

    # this method return a csv row which stands for this subject
    def to_csv(self) -> str:
        return f'{self.name},{self.weekday},{self.start},{self.end},{self.teacher},{self.dst},{self.week_number}'


if __name__ == "__main__":
    # parse arguments
    args=PARSER.parse_args()
    html_path = args.input
    output_type = args.type
    output_name = args.output

    # read html file
    if html_path == '':
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
    # record the skipped weekday in a table row
    td_void = [0,0,0,0,0,0,0]
    for section in range(1,16):
        tds = trs[section].find_all('td')
        # remove the first td, because it is the section number
        tds.pop(0)
        weekday = 0
        for td in tds:
            # because of the merged cells, some row have <td> less than 7. 
            # to make weekday correct, these "missing" <td> should be taken into account.
            weekday += 1 if td_void[weekday] != 0 else 0
            td_attrs = td.attrs
            if 'rowspan' in td_attrs and int(td_attrs['rowspan']) > 1:
                rowspan = int(td_attrs['rowspan'])
                sub = Subject(td.text.strip(), weekday+1, section, rowspan)
                subject_tables.append(sub)
                td_void[weekday] = rowspan
            weekday += 1
        # maintain td_void, every non-zero element should minus 1
        for i in range(0,7):
            if td_void[i] != 0:
                td_void[i] -= 1
    
    # export csv file
    if output_type == 'csv':
        csv = "课程名称,星期,开始节数,结束节数,老师,地点,周数\n"
        for subject in subject_tables:
            csv = csv + subject.to_csv() + '\n'
        try: 
            with open(f'./{output_name}.csv', 'w+', encoding='utf8') as f:
                f.write(csv)
        except Exception as e:
            print(e)
            print("can't write csv file")
    
    print(f'{len(subject_tables)} subjects have been exported')
