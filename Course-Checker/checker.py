#!/Users/Yaxin.Cheng@iCloud.com/Developer/venv/bin/python
import re
import requests
import argparse

baseURL = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={term}&s_crn=&s_subj={faculty}&s_numb=&n={page}&s_district=100'
parser = argparse.ArgumentParser(description='Search for the existence of courses')
parser.add_argument('-t', '--term', nargs='*', default='w', help='Term (Available input: winter/fall/w/f; winter by default)')
parser.add_argument('-d', '--digit', help='Course Digit (Precise search only; Cannot search with name at the same time)')
parser.add_argument('-n', '--name', help='Name (Partial search is available; Mobile Computing by default; Cannot search with digit at the same time)')
parser.add_argument('-p', '--page', help='Page (One specific page needs to be search; All pages by default)')
parser.add_argument('-f', '--faculty', help='Faculty (Shorthand of faculty name; CSCI by default)')
args = parser.parse_args()

Page = args.page or [ (i - 1) * 20 + 1 for i in range(1, 8) ]
termMapping = {'winter': 201820, 'fall': 201810, 'w': 201820, 'f': 201810}
reverseTermMapping = {201810: 'Fall', 201820: 'Winter'}
Term = [termMapping[args.term]] if not isinstance(args.term, list) else [termMapping[term] for term in args.term]
Facu = (args.faculty or 'CSCI').upper()
Name = args.name or 'Mobile Computing'
Digit = args.digit
if Digit: Name = '.+?'
else: Digit = '[0-9]*?'

nameRegex = '<b>{faculty}\s{digit}\s.*?{name}.*?<\/b>'.format(faculty=Facu, name=Name, digit=Digit)
emptyRegex = '<b>{faculty}\s[0-9]*?\s.+?<\/b>'.format(faculty=Facu)
for term in Term:
    print('Searching {name} in {term} term for {faculty}'.format(name=Facu+' '+Digit if Name == '.+?' else Name, term=reverseTermMapping[term], faculty=Facu))
    if not isinstance(Page, list) and Page: Page = [(int(Page) - 1) * 20 + 1]
    for index, page in enumerate(Page):
        searchURL = baseURL.format(term=term, faculty=Facu, page=page)
        source = requests.get(searchURL).text
        if not re.search(emptyRegex, source): break
        print('Searching on page', index + 1 if len(Page) > 1 else int((page - 1)/20 + 1), ':')
        for course in re.findall(nameRegex, source, flags=re.I):
            print(course.strip('<b></b>'))
