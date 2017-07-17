#!/Users/Yaxin.Cheng@iCloud.com/Developer/venv/bin/python
import re
import requests
import argparse
import webbrowser
import sys
from datetime import datetime

baseURL = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={term}&s_crn=&s_subj={faculty}&s_numb=&n={page}&s_district=All'
parser = argparse.ArgumentParser(description='Search for the existence of courses')
parser.add_argument('-o', '--open', action='store_true', help='Open the url in the browser')
parser.add_argument('-t', '--term', nargs='*', default=['f', 'w'], help='Term (Available input: winter/fall/w/f; winter by default)')
parser.add_argument('-d', '--digit', nargs='*', help='Course Digit (Fuzzy search available (regex); Cannot search with name at the same time)')
parser.add_argument('-n', '--name', nargs='*', help='Name (Partial search is available; Mobile Computing by default; Cannot search with digit at the same time)')
parser.add_argument('-p', '--page', type=int, help='Page (One specific page needs to be search; All pages by default)')
parser.add_argument('-f', '--faculty', help='Faculty (Shorthand of faculty name; CSCI by default)')
parser.add_argument('-s', '--show', action='store_true', help='Show course dates')
parser.add_argument('-y', '--year', type=int, help='Year of the timetable (Historical data may be unaccessible)')
args = parser.parse_args()

def openURL(baseURL, term, faculty, page):
    page = page[0] if isinstance(page, list) else (page - 1) * 20 + 1
    webbrowser.open(baseURL.format(term=term, faculty=faculty, page=page))
    sys.exit(0)

encodePage = lambda number: int((number - 1) * 20 + 1)
decodePage = lambda number: int((number - 1) / 20 + 1)
encodeYear = lambda year: (year + 1) * 100
decodeYear = lambda year: int(year / 100) - 1

year = encodeYear(args.year or datetime.now().year)
__FALL__, __WINTER__, __SUMMER__ = year + 10, year + 20, year + 30

Page = [encodePage(args.page)] if args.page else [ encodePage(i) for i in range(1, 8) ]
reverseTermMapping = {__FALL__: 'fall', __WINTER__: 'winter', __SUMMER__: 'summer'}
termMapping = {**{value: key for key, value in reverseTermMapping.items()}, 'w': __WINTER__, 'f': __FALL__, 's': __SUMMER__}
Term = [termMapping[args.term.lower()]] if not isinstance(args.term, list) else [termMapping[term.lower()] for term in args.term]
Facu = (args.faculty or 'CSCI').upper()
if args.open:
    openURL(baseURL, Term[0], Facu, Page)
Name = args.name or ['Mobile Computing']
Digit = args.digit
if Digit: 
    Name = '.+?'
    Digit = '(' + '|'.join(args.digit) + ')'
else: 
    Digit = '[0-9]*?'
    Name = '(' + '|'.join(Name) + ')'

crnRegex  = re.compile('<b>\d{5}<\/b>')
coreRegex = re.compile('^<TD.*?COLSPAN="15" CLASS="detthdr">(.|\s)*?<tr.*valign=', re.M)
nameRegex = re.compile('<b>{faculty}\s{digit}\s.*?{name}.*?<\/b>'.format(faculty=Facu, name=Name, digit=Digit), re.I|re.M)
typeRegex = re.compile('(Lec|Lab|Tut|WkT|Ths)')
timeRegex = re.compile('[0-9]{4}\-[0-9]{4}')
weekRegex = re.compile('<p class="centeraligntext">[MTWRF]<\/p>')
dateRegex = re.compile('\d{2}\-\w{3}\-\d{4}\s\-\s\d{2}\-\w{3}\-\d{4}')
percRegex = re.compile('(\d{1,2}\.\d{1,2}\%)|(WLIST)|(FULL)')
emptyRegex = re.compile('<b>{faculty}\s[0-9]*?\s.+?<\/b>'.format(faculty=Facu))
clearRegex = re.compile('(<b>)|(<\/b>)')
splitRegex = re.compile('<\/tr>\s*?<tr>')

for term in Term:
    print('Searching {name} in {term} term for {faculty} (Year {year})\n'.format(name=Facu+' '+str(Digit) if Name == '.+?' else Name, term=reverseTermMapping[term], faculty=Facu, year=decodeYear(year)))
    print('=' * 50)
    for index, page in enumerate(Page):
        searchURL = baseURL.format(term=term, faculty=Facu, page=page)
        source = requests.get(searchURL).text
        if not emptyRegex.search(source): break
        for course in coreRegex.finditer(source):
            components = splitRegex.split(course.group())
            try:
                name = nameRegex.search(components[0]).group()
                summary = "Name: " + clearRegex.sub('', name) + '\n'
            except:
                continue
            if args.show: summary += dateRegex.search(components[0]) + '\n'
            print(summary)
            print('\t'.join(['CRN', 'Type', 'Weeks', 'Time', 'Percentage']))
            for detail in components[1:]:
                try:
                    crn = crnRegex.search(detail).group().strip('<b></b>')
                except: continue
                ctype = typeRegex.search(detail).group()
                weeks = '|'.join(map(lambda week: week.strip('<p class="centeraligntext"></p>'), weekRegex.findall(detail)))
                time = timeRegex.search(detail).group()
                percent = percRegex.search(detail).group()
                print('\t'.join([crn, ctype, weeks, time, percent]))
            print('=' * 50)
    print()
