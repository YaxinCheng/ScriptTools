#!/Users/Yaxin.Cheng@iCloud.com/Developer/venv/bin/python
import re
import requests
import argparse
import webbrowser
import sys
__FALL__, __WINTER__, __SUMMER__ = 201810, 201820, 201830

baseURL = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={term}&s_crn=&s_subj={faculty}&s_numb=&n={page}&s_district=100'
parser = argparse.ArgumentParser(description='Search for the existence of courses')
parser.add_argument('-o', '--open', action='store_true', help='Open the url in the browser')
parser.add_argument('-t', '--term', nargs='*', default='w', help='Term (Available input: winter/fall/w/f; winter by default)')
parser.add_argument('-d', '--digit', help='Course Digit (Precise search only; Cannot search with name at the same time)')
parser.add_argument('-n', '--name', help='Name (Partial search is available; Mobile Computing by default; Cannot search with digit at the same time)')
parser.add_argument('-p', '--page', type=int, help='Page (One specific page needs to be search; All pages by default)')
parser.add_argument('-f', '--faculty', help='Faculty (Shorthand of faculty name; CSCI by default)')
args = parser.parse_args()

def openURL(baseURL, term, faculty, page):
    page = page[0] if isinstance(page, list) else (page - 1) * 20 + 1
    webbrowser.open(baseURL.format(term=term, faculty=faculty, page=page))
    sys.exit(0)

encodePage = lambda number: int((number - 1) * 20 + 1)
decodePage = lambda number: int((number - 1) / 20 + 1)

Page = [encodePage(args.page)] if args.page else [ encodePage(i) for i in range(1, 8) ]
reverseTermMapping = {__FALL__: 'fall', __WINTER__: 'winter', __SUMMER__: 'summer'}
termMapping = {**{value: key for key, value in reverseTermMapping.items()}, 'w': __WINTER__, 'f': __FALL__, 's': __SUMMER__}
Term = [termMapping[args.term.lower()]] if not isinstance(args.term, list) else [termMapping[term.lower()] for term in args.term]
Facu = (args.faculty or 'CSCI').upper()
if args.open:
    openURL(baseURL, Term[0], Facu, Page)
Name = args.name or 'Mobile Computing'
Digit = args.digit
if Digit: Name = '.+?'
else: Digit = '[0-9]*?'

nameRegex = '<b>{faculty}\s{digit}\s.*?{name}.*?<\/b>'.format(faculty=Facu, name=Name, digit=Digit)
emptyRegex = '<b>{faculty}\s[0-9]*?\s.+?<\/b>'.format(faculty=Facu)
for term in Term:
    print('Searching {name} in {term} term for {faculty}'.format(name=Facu+' '+Digit if Name == '.+?' else Name, term=reverseTermMapping[term], faculty=Facu))
    for index, page in enumerate(Page):
        searchURL = baseURL.format(term=term, faculty=Facu, page=page)
        source = requests.get(searchURL).text
        if not re.search(emptyRegex, source): break
        print('Searching on page', index + 1 if len(Page) > 1 else decodePage(page), ':')
        for course in re.findall(nameRegex, source, flags=re.I):
            print(course.strip('<b></b>'))
