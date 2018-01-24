#!/usr/local/bin/python3
import re, argparse, webbrowser, sys, os, json, requests
from datetime import datetime 

baseURL = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={term}&s_crn=&s_subj={faculty}&s_numb=&n={page}&s_district=All'
parser = argparse.ArgumentParser(description='Search for the existence of courses')
parser.add_argument('-o', '--open', action='store_true', help='Open the url in the browser')
parser.add_argument('-t', '--term', nargs='*', default=['f', 'w'], help='Term (Available input: winter/fall/summer/w/f/s; fall and winter by default)')
parser.add_argument('-d', '--digit', nargs='*', help='Course Digit (Fuzzy search available (regex))')
parser.add_argument('-n', '--name', nargs='*', help='Name (Partial search is available)')
parser.add_argument('-f', '--faculty', help='Faculty (Shorthand of faculty name)')
parser.add_argument('-r', '--range', metavar='TIME', default='MTWRF, 0:2400', help='''Time range the courses are available. Example: "MR, :1605"=Monday& Thursday, before 16:05, "M, 1605:"=Monday after 16:05, "1505:1605"=Any day between 15:05 and 16:05''')
parser.add_argument('-y', '--year', type=int, help='Year of the timetable (Must be in format yyyy; Historical data may be unaccessible)')
parser.add_argument('--date', metavar='DATE', default=None, help='Date range for filter. "17092018:"=Begin after 2018-Sep-17, ":17092018"=End before 2018-Sep-17')
args = parser.parse_args() 
if not (args.faculty and (args.name or args.digit or args.range)): 
    parser.print_help()
    sys.exit(0)

def openURL(baseURL, term, faculty, page):
    webbrowser.open(baseURL.format(term=term, faculty=faculty, page=1))
    sys.exit(0)

def searchByTime(timeRange):
    upperTime = timeRange.upper()
    week = ''.join(re.findall('[MTWRF]', upperTime)) or 'MWTRF'
    try: Time = (int(re.search('(\d*):', upperTime).groups()[0] or 0), int(re.search(':(\d*)', upperTime).groups()[0] or 2400),)
    except: Time = (0, 2400)
    return week, Time

def filterByDate(dateStandard, dateRange, compareMode):
    begin, end = [datetime.strptime(each, '%d-%b-%Y') for each in dateRange.split(' - ')]
    if compareMode == True: return end <= dateStandard
    elif compareMode == False: return begin >= dateStandard

encodePage = lambda number: int((number - 1) * 20 + 1)
decodeYear = lambda year: int(year / 100) - 1
weekProcessor = lambda chunk: ''.join(map(lambda week: week.groups()[1], chunk))
year = ((args.year or datetime.now().year) + 1) * 100
__FALL__, __WINTER__, __SUMMER__ = year + 10, year + 20, year + 30
Export = os.fstat(0) != os.fstat(1)# Check if stdin == stdout
Page = [ encodePage(i) for i in range(1, 8) ]
reverseTermMapping = {__FALL__: 'fall', __WINTER__: 'winter', __SUMMER__: 'summer'}
termMapping = {**{value: key for key, value in reverseTermMapping.items()}, 'w': __WINTER__, 'f': __FALL__, 's': __SUMMER__}
Term = [termMapping[args.term.lower()]] if not isinstance(args.term, list) else [termMapping[term.lower()] for term in args.term]
Facu = args.faculty.upper()
if args.open: openURL(baseURL, Term[0], Facu, Page)
Name = '({})'.format('|'.join(args.name)) if args.name else '.+?'
Digit = '({})'.format('|'.join(args.digit)) if args.digit else '\d*?'
Week, Time = searchByTime(args.range)
if args.date:
    DateBefore, DateStd = ':' == args.date[0], datetime.strptime(args.date.strip(':'), '%d%m%Y')

crnRegex  = re.compile('(?<=<b>)\d{5}(?=<\/b>)')
coreRegex = re.compile('^<TD.*?COLSPAN="15" CLASS="detthdr">(.|\s)*?<tr.*valign=', re.M)
nameRegex = re.compile('(?<=<b>){faculty}\s{digit}\s.*?{name}.*?(?=<\/b>)'.format(faculty=Facu, name=Name, digit=Digit), re.I|re.M)
typeRegex = re.compile('(Lec|Lab|Tut|WkT|Ths|Int|WkS|Aud)')
timeRegex = re.compile('[0-9]{4}\-[0-9]{4}')
dateRegex = re.compile('\d{2}\-\w{3}\-\d{4}\s\-\s\d{2}\-\w{3}\-\d{4}')
percRegex = re.compile('(\d{1,2}\.\d{1,2}\%)|(WLIST)|(FULL)')
weekRegex = re.compile('<p class="centeraligntext">(<br>|<br \/>|&nbsp;)*?([MTWRF])')
weekFRegex = re.compile('<p class="centeraligntext">(<br>|<br \/>|&nbsp;)*?([{week}])'.format(week=Week))
emptyRegex = re.compile('<b>{faculty}\s[0-9]*?\s.+?<\/b>'.format(faculty=Facu))
splitRegex = re.compile('<\/tr>\s*?<tr>')
locatRegex = re.compile('<td CLASS="dett[lbtws]" ?NOWRAP(="")?>(.|\s)*?((Studley|Carleton|Consult|Sexton|DISTANCE|Agricultural|King|Other).*?)<\/td>', re.I)
if Name == '.+?' and Digit == '\d*?': searchingName = '{faculty} in {Week} between {From} and {End}'.format(faculty=Facu, Week=Week, From=Time[0], End=Time[1])
elif Name != '.+?': searchingName = '{name} in {Week} between {From} and {End}'.format(name=Name, Week=Week, From=Time[0], End=Time[1])
else: searchingName = '{faculty} {digit} in {Week} between {From} and {End}'.format(faculty=Facu, digit=Digit, Week=Week, From=Time[0], End=Time[1])

try:
    for term in Term:
        if not Export: print('\x1b[0;30;47m{name} in {term} term for {faculty} (Year {year})\x1b[0m\n'.format(name=searchingName, term=reverseTermMapping[term], faculty=Facu, year=decodeYear(year)), '\n' + '=' * 80)
        for index, page in enumerate(Page):
            searchURL = baseURL.format(term=term, faculty=Facu, page=page)
            source = requests.get(searchURL).text
            if not emptyRegex.search(source): break# if page is empty, next term
            for course in coreRegex.finditer(source):
                printable = True
                components = splitRegex.split(course.group())
                try: header = nameRegex.search(components[0]).group()
                except AttributeError: continue
                if Export or (term - 30) % 100 == 0: 
                    courseDate = dateRegex.search(components[0]).group()
                    if args.date: 
                        if not filterByDate(DateStd, courseDate, DateBefore): continue
                    header += '\n' + courseDate + '\n' # Show dates only in summers or Export mode
                content = ''# Empty content string
                for detail in components[1:]:
                    try: crn = crnRegex.search(detail).group()
                    except AttributeError: continue
                    try: location = locatRegex.search(detail).groups()[2].strip()
                    except AttributeError: pass
                    if '<br />' in location: location = location.split('<br />')[0]# Keep only one in multiple locations
                    ctype = typeRegex.search(detail).group()
                    if ctype == 'Lec':
                        weeks = weekProcessor(weekFRegex.finditer(detail))
                        printable = len(weeks) or Week == 'MTWRF'
                        if not printable: break
                    weeks = weekProcessor(weekRegex.finditer(detail))
                    try: time = timeRegex.search(detail).group()
                    except AttributeError: time = 'N.A.\t'
                    if ctype == 'Lec': 
                        if time == 'N.A.\t': printable = Time == (0, 2400) and Week == 'MTWRF'
                        else:
                            pre, post = [int(each) for each in time.split('-')]
                            printable = Time[0] <= pre and post <= Time[1]
                        if not printable: break
                    percent = percRegex.search(detail).group()
                    content += '\t'.join([crn, ctype, weeks, time, percent, '\t' + location]) + '\n'
                if printable: print(header + '\n' + '\t'.join(['CRN', 'Type', 'Weeks', 'Time', '\tPercentage', 'Location']) + '\n' + content + '\n' + '=' * 80, '\n')
except KeyboardInterrupt: pass
