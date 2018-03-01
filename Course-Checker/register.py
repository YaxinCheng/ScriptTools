import requests, sys, time, argparse
from datetime import datetime
from getpass import getpass

LOGIN_URL = 'https://dalonline.dal.ca/PROD/twbkwbis.P_ValLogin'
REGISTER_URL = 'https://dalonline.dal.ca/PROD/bwckcoms.P_Regs'
FAILED_TEXT = 'Registration changes are not allowed. Status rules not defined for part of term'
COURSE_NUMS = list(range(16, 66, 5))
parser = argparse.ArgumentParser(description='Course register')
parser.add_argument('year', type=int, help='Year of the timetable (Must be in format yyyy; Historical data may be unaccessible)') 
parser.add_argument('term', help='Term (Available input: winter/fall/summer/w/f/s; fall and winter by default)')
parser.add_argument('crn', type=int, nargs='+', help='Course CRN (You can only register at most 10 courses at once')
args = parser.parse_args()
term = args.term
PACK = [['term_in', term], ['RSTS_IN', 'DUMMY'], ['assoc_term_in', 'DUMMY'], ['CRN_IN', 'DUMMY'], ['start_date_in', 'DUMMY'], ['end_date_in', 'DUMMY'], ['SUBJ', 'DUMMY'], ['CRSE', 'DUMMY'], ['SEC', 'DUMMY'], ['LEVL', 'DUMMY'], ['CRED', 'DUMMY'], ['GMOD', 'DUMMY'], ['TITLE', 'DUMMY'], ['MESG', 'DUMMY'], ['REG_BTN', 'DUMMY'], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['RSTS_IN', 'RW'], ['CRN_IN', ''], ['assoc_term_in', ''], ['start_date_in', ''], ['end_date_in', ''], ['regs_row', '0'], ['wait_row', '0'], ['add_row', '10'], ['REG_BTN', 'Submit Changes']]
for index, crn in zip(COURSE_NUMS, args.crn):
    PACK[index][1] = str(crn)

NetID = input("NetID: ")
Password = getpass("Password: ")

def register():
    session = requests.session()
    session.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6', 'Accept-Language': 'en-ca', 'Accept-Encoding': 'br, gzip, deflate', 'Connection': 'keep-alive'}
    going = True
    while going:
        session.get(LOGIN_URL)# Get cookies
        loginResponse = session.post(LOGIN_URL, {'sid': NetID, 'PIN': Password})
        if loginResponse.status_code != 200:
            print('LOGIN ERROR')
            continue
        counter = 0
        while counter < 50:
            registerResponse = session.post(REGISTER_URL, PACK)
            if registerResponse.status_code == 200:
                if FAILED_TEXT not in registerResponse.text:# success register
                    print('SUCCESS')
                    going = False
                    break
                else:# failed register
                    print('FAILED TO REGISTER, RETRYING...', counter)
                    time.sleep(5)
            else: #if code is not 200, I do everything again
                print('FAILED WITH WRONG CODE, RETRYING FROM BEGINNING')
                break
            counter += 1
register()
