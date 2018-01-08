#!/usr/local/bin/python3
import re, argparse, webbrowser, sys, os, json, requests
from datetime import datetime 

baseURL = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={term}&s_crn=&s_subj={faculty}&s_numb=&n={page}&s_district=All'
parser = argparse.ArgumentParser(description='Search for the existence of courses')
parser.add_argument('-t', '--term', help='Term (Available input: winter/fall/summer/w/f/s')
parser.add_argument('-l', '--level', type=int, nargs='*', help='Keep courses from certain levels')
parser.add_argument('-r', '--range', metavar='TIME', default='MTWRF, 0:2400', help='''Time range the courses are available. Example: "MR, :1605"=Monday& Thursday, before 16:05, "M, 1605:"=Monday after 16:05, "1505:1605"=Any day between 15:05 and 16:05''')
parser.add_argument('-y', '--year', type=int, help='Year of the timetable (Must be in format yyyy; Historical data may be unaccessible)')
parser.add_argument('--date', metavar='DATE', default=None, help='Date range for filter. "17092018:"=Begin after 2018-Sep-17, ":17092018"=End before 2018-Sep-17')
args = parser.parse_args() 

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
Term = termMapping[args.term]
resourcePage = requests.get(baseURL.format(term=Term, faculty="CSCI", page=1)).text
fList = re.findall('\<OPTION VALUE="([A-Z]{4})"', resourcePage)
Week, Time = searchByTime(args.range)
Level = str(args.level or range(1, 9))
if args.date:
    DateBefore, DateStd = ':' == args.date[0], datetime.strptime(args.date.strip(':'), '%d%m%Y')

crnRegex  = re.compile('<b>(\d{5})<\/b>')
coreRegex = re.compile('^<TD.*?COLSPAN="15" CLASS="detthdr">(.|\s)*?<tr.*valign=', re.M)
nameTemplate = '<b>({faculty}\s{level}[0-9]{{2,3}}\s.+?)<\/b>'
typeRegex = re.compile('(Lec|Lab|Tut|WkT|Ths|Int|WkS|Aud)')
timeRegex = re.compile('[0-9]{4}\-[0-9]{4}')
dateRegex = re.compile('\d{2}\-\w{3}\-\d{4}\s\-\s\d{2}\-\w{3}\-\d{4}')
percRegex = re.compile('(\d{1,2}\.\d{1,2}\%)|(WLIST)|(FULL)')
weekRegex = re.compile('<p class="centeraligntext">(<br>|<br \/>|&nbsp;)*?([MTWRF])')
weekFRegex = re.compile('<p class="centeraligntext">(<br>|<br \/>|&nbsp;)*?([{week}])'.format(week=Week))
splitRegex = re.compile('<\/tr>\s*?<tr>')
locatRegex = re.compile('<td CLASS="dett[lbtws]" ?NOWRAP(="")?>(.|\s)*?((Studley|Carleton|Consult|Sexton|DISTANCE|Agricultural|King|Other).*?)<\/td>', re.I)

try:
    for faculty in fList:
        nameRegex = re.compile(nameTemplate.format(faculty=faculty, level=Level), re.M)
        for index, page in enumerate(Page):
            searchURL = baseURL.format(term=Term, faculty=faculty, page=page)
            source = requests.get(searchURL).text
            if not nameRegex.search(source): break
            for course in coreRegex.finditer(source):
                printable = True
                components = splitRegex.split(course.group())
                try: header = nameRegex.search(components[0]).groups()[0]
                except AttributeError: continue
                if Export or (Term - 30) % 100 == 0: 
                    courseDate = dateRegex.search(components[0]).group()
                    if args.date: 
                        if not filterByDate(DateStd, courseDate, DateBefore): continue
                    header += '\n' + courseDate + '\n' # Show dates only in summers
                content = ''
                for detail in components[1:]:
                    try: crn = crnRegex.search(detail).groups()[0]
                    except AttributeError: continue
                    #try: location = locatRegex.search(detail).groups()[2].strip()
                    #except AttributeError: location = ''
                    #if '<br />' in location: location = location.split('<br />')[0]
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
                    content += '\t'.join([crn, ctype+'\t', weeks, time, percent, '\t' ]) + '\n'
                if printable: print(header + '\n' + '\t'.join(['CRN', '\tType', 'Weeks', 'Time', '\tPercentage']) + '\n' + content + '\n' + '=' * 80, '\n')
except KeyboardInterrupt: pass
