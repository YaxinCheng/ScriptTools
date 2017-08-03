#!/Users/Yaxin.Cheng@iCloud.com/Developer/venv/bin/python
import re, argparse, webbrowser, sys
import requests
from datetime import datetime 

baseURL = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={term}&s_crn=&s_subj={faculty}&s_numb=&n={page}&s_district=All'
parser = argparse.ArgumentParser(description='Search for the existence of courses')
parser.add_argument('-o', '--open', action='store_true', help='Open the url in the browser')
parser.add_argument('-s', '--show', action='store_true', help='Show course dates')
parser.add_argument('-t', '--term', nargs='*', default=['f', 'w'], help='Term (Available input: winter/fall/summer/w/f/s; fall and winter by default)')
parser.add_argument('-d', '--digit', nargs='*', help='Course Digit (Fuzzy search available (regex))')
parser.add_argument('-n', '--name', nargs='*', help='Name (Partial search is available)')
parser.add_argument('-f', '--faculty', help='Faculty (Shorthand of faculty name)')
parser.add_argument('-r', '--range', metavar='TIME', default='0:2400', help='''Time range the courses are available. Example: ":1605"=before 16:05, "1605:"=after 16:05, "1505:1605"=between 15:05 and 16:05''')
parser.add_argument('-w', '--week', default='MTRWF', help='Week days which courses are available; Example: MWF(Mon, Wed, Fri)')
parser.add_argument('-y', '--year', type=int, help='Year of the timetable (Historical data may be unaccessible)')
args = parser.parse_args() 
if not (args.faculty and (args.name or args.digit or args.range)): 
    parser.print_help()
    sys.exit(0)

def openURL(baseURL, term, faculty, page):
    webbrowser.open(baseURL.format(term=term, faculty=faculty, page=1))
    sys.exit(0)

encodePage = lambda number: int((number - 1) * 20 + 1)
encodeYear = lambda year: (year + 1) * 100
decodeYear = lambda year: int(year / 100) - 1
encodeTime = lambda time: int(time)

year = encodeYear(args.year or datetime.now().year)
__FALL__, __WINTER__, __SUMMER__ = year + 10, year + 20, year + 30

Page = [ encodePage(i) for i in range(1, 8) ]
reverseTermMapping = {__FALL__: 'fall', __WINTER__: 'winter', __SUMMER__: 'summer'}
termMapping = {**{value: key for key, value in reverseTermMapping.items()}, 'w': __WINTER__, 'f': __FALL__, 's': __SUMMER__}
Term = [termMapping[args.term.lower()]] if not isinstance(args.term, list) else [termMapping[term.lower()] for term in args.term]
Facu = args.faculty.upper()
Week = args.week.upper()
if args.range.startswith(':'): Time = list(map(encodeTime, ('0'+args.range).split(':')))
elif args.range.endswith(':'): Time = list(map(encodeTime, (args.range+'2400').split(':')))
else: Time = list(map(encodeTime, args.range.split(':')))
if args.open: openURL(baseURL, Term[0], Facu, Page)
Name = '({})'.format('|'.join(args.name)) if args.name else '.+?'
Digit = '({})'.format('|'.join(args.digit)) if args.digit else '\d*?'

crnRegex  = re.compile('<b>\d{5}<\/b>')
coreRegex = re.compile('^<TD.*?COLSPAN="15" CLASS="detthdr">(.|\s)*?<tr.*valign=', re.M)
nameRegex = re.compile('<b>{faculty}\s{digit}\s.*?{name}.*?<\/b>'.format(faculty=Facu, name=Name, digit=Digit), re.I|re.M)
typeRegex = re.compile('(Lec|Lab|Tut|WkT|Ths)')
timeRegex = re.compile('[0-9]{4}\-[0-9]{4}')
weekRegex = re.compile('<p class="centeraligntext">[{week}]<\/p>'.format(week=Week))
dateRegex = re.compile('\d{2}\-\w{3}\-\d{4}\s\-\s\d{2}\-\w{3}\-\d{4}')
percRegex = re.compile('(\d{1,2}\.\d{1,2}\%)|(WLIST)|(FULL)')
emptyRegex = re.compile('<b>{faculty}\s[0-9]*?\s.+?<\/b>'.format(faculty=Facu))
clearRegex = re.compile('(<b>)|(<\/b>)')
splitRegex = re.compile('<\/tr>\s*?<tr>')

if Name == '.+?' and Digit == '\d*?': searchingName = '{faculty} between {From} and {End}'.format(faculty=Facu, From=Time[0], End=Time[1])
elif Name != '.+?': searchingName = '{name} between {From} and {End}'.format(name=Name, From=Time[0], End=Time[1])
else: searchingName = '{faculty} {digit} between {From} and {End}'.format(faculty=Facu, digit=Digit, From=Time[0], End=Time[1])

for term in Term:
    print('Searching {name} in {term} term for {faculty} (Year {year})\n'.format(name=searchingName, term=reverseTermMapping[term], faculty=Facu, year=decodeYear(year)))
    print('=' * 50)
    for index, page in enumerate(Page):
        searchURL = baseURL.format(term=term, faculty=Facu, page=page)
        source = requests.get(searchURL).text
        if not emptyRegex.search(source): break
        for course in coreRegex.finditer(source):
            printable = True
            components = splitRegex.split(course.group())
            try:
                name = nameRegex.search(components[0]).group()
                header = "Name: " + clearRegex.sub('', name) + '\n'
            except: continue
            if args.show: header += dateRegex.search(components[0]).group() + '\n'
            content = ''
            for detail in components[1:]:
                try: crn = crnRegex.search(detail).group().strip('<b></b>')
                except: continue
                ctype = typeRegex.search(detail).group()
                if ctype == 'Lec':
                    weeks = '|'.join(map(lambda week: week.strip('<p class="centeraligntext"></p>'), weekRegex.findall(detail)))
                    printable = len(weeks)
                    if not printable: break
                else: weeks = '|'.join(map(lambda week: week.strip('<p class="centeraligntext"></p>'), re.findall('<p class="centeraligntext">[MTWRF]<\/p>', detail))) 
                try: time = timeRegex.search(detail).group()
                except: time = 'N.A.\t'
                if ctype == 'Lec': 
                    pre, post = [int(each) for each in time.split('-')]
                    printable = Time[0] <= pre and post <= Time[1]
                    if not printable: break
                percent = percRegex.search(detail).group()
                content += '\t'.join([crn, ctype, weeks, time, percent]) + '\n'
            if printable:
                print(header)
                print('\t'.join(['CRN', 'Type', 'Weeks', 'Time', '\tPercentage']))
                print(content)
                print('=' * 50, '\n')
