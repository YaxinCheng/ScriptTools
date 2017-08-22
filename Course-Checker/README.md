# Course Checker
## Functionalities
1. Search courses in different faculties, terms, and years by their name(fuzzy), number(fuzzy), and course time
2. Print the information on the screen or export to a file
3. Load the exported file to generate a ics calendar file (Note: all courses will be in America/Halifax time zone)
## Requirements
* Python3
* See the requirements.txt
## Examples
- Search by names: checker.py -f csci -t winter -n 'mobile computing'
- Search by number:checker.py -f math -t fall -d 3119 2080
- Fuzzy search all 3000+ math courses: checker -f math -t fall winter -d 3.\*
- Fuzzy search all CS courses with "computing": checker.py -f csci -t f w -n computing
- Search by all CS courses after 10AM on Mon, Wed, and Fri: checker.py -f csci -t f w -r MWF,1000:
- Search by all CS courses between 10AM and 2PM on Mon, Wed, and Fri: checker.py -f csci -t f w -r MWF,1000:1400
- Convert exported file to ics: cal.py filename.txt
