#!/Users/Yaxin.Cheng@iCloud.com/Developer/venv/bin/python
import sys, argparse, re
from ics import Calendar, Event

parser = argparse.ArgumentParser(description='Convert file to ics')
parser.add_argument('file', help='File location')
args = parser.parse_args()

nameRegex = re.compile('[A-Z]{4} \d{4} .+')
dateRegex = re.compile('\d{2}\-\w{3}\-\d{4}\s\-\s\d{2}\-\w{3}\-\d{4}')
contRegex = re.compile('\d{5}\s*?(Lec|Lab|Tut|WkT|Ths)\s*?[MTWRF]+\s*?\d{4}-\d{4}')

def makeEvent(name, date, content):
    try: (_, type, weeks, time, _) = content.split('\t')
    except ValueError: return None
    name = name if type == 'Lec' else name + ' ' + type
    weeksMap = {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4}
    weeks = set(map(lambda w: weeksMap(w), weeks))

with open(args.file) as inFile:
    calendar = Calendar()
    for piece in enumerate(inFile.readlines()):
        if nameRegex.match(piece) is not None:
            name = nameRegex.match(piece).group()
        elif dateRegex.match(piece) is not None:
            date = dateRegex.match(piece).group()
        elif contRegex.match(piece) is not None:
            content = contRegex.match(piece).group()
