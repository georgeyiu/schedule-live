#!/usr/bin/env python

import argparse
import getpass
import os
import pickle
import re
import requests
import sys
import urllib2

from bs4 import BeautifulSoup as bs
from multiprocessing import Pool

# Semester must be FL, SP, or SU
TERM = 'FL'

class colors:
    HEADER = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    @staticmethod
    def header(msg):
        return colors.HEADER + msg + colors.ENDC

    @staticmethod
    def fail(msg):
        return colors.FAIL + msg + colors.ENDC

def getSession():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cookie_path = os.path.join(dir_path, 'calnet.cookie')
    if os.path.isfile(cookie_path):
        with open(cookie_path, 'r') as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
        session = requests.Session()
        session.cookies = cookies
    else:
        telebears = \
            'https://auth.berkeley.edu/cas/login?service=https%3A%2F%2F' \
            'telebears.berkeley.edu%2Ftelebears%2Fj_spring_cas_security_check'

        session = requests.Session()

        authenticated = False
        while not authenticated:
            soup = bs(requests.get(telebears).text)
            inputs = soup.findAll('input')
            data = dict([(e['name'], e['value']) \
                            for e in inputs if e['type'] == 'hidden'])

            username = raw_input('CalNet Username: ')
            password = getpass.getpass('CalNet Password: ')
            data.update({'username': username, 'password': password})

            posturl = 'https://auth.berkeley.edu{}'.format(soup.form['action'])
            res = session.post(posturl,
                               headers={'User-Agent': 'Mozilla/5.0'},
                               data=data)
            if 'Passphrase you provided are incorrect' not in res.text:
                authenticated = True
            print 'The CalNet ID and/or Passphrase you provided are incorrect. ' \
                  'Please try again.'

        with open(cookie_path, 'w') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), f)

    return session

def scrape_enrollment(ccn, semester, referer, session):

    url = 'https://telebears.berkeley.edu/enrollment-osoc/osc?{}'
    fields = {
        '_InField1': 'RESTRIC',
        '_InField2': ccn,
        '_InField3': semester
    }
    params = '&'.join(['{}={}'.format(x[0],x[1]) for x in fields.iteritems()])
    session.headers.update({'referer': referer})
    content = session.get(url.format(params)).text

    numbers = []
    for line in filter(lambda l: 'limit' in l, content.split('\n')):
        numbers += re.findall(r'([0-9]+)', line)
    numbers += ['0']*4
    enrolled = numbers[0] + '/' + numbers[1]
    waitlist = numbers[2] + '/' + numbers[3]
    return (ccn, (enrolled, waitlist))

def course_search(dept, num):
    url = 'http://osoc.berkeley.edu/OSOC/osoc?p_term={}&x=0&p_classif=--+' \
          'Choose+a+Course+Classification+--&p_deptname=--+Choose+a+Depar' \
          'tment+Name+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&y' \
          '=0&p_course={}&p_dept={}'.format(TERM, num, dept)
    contents = urllib2.urlopen(url).read()

    stats = {}
    def save(res):
        if res: stats[res[0]] = res[1]

    pool = Pool(30)
    ccns = re.findall(r'input type="hidden" name="_InField2" value="([0-9]*)"',
                      contents)
    semester = re.search(r'input type="hidden" name="_InField3" value="(.*)"',
                      contents).group(1)

    session = getSession()

    for ccn in ccns:
        pool.apply_async(scrape_enrollment,
                         args=(ccn, semester, url, session),
                         callback=save)
    pool.close()
    pool.join()

    data = []
    for line in contents.split('\n'):
        if ':&#160;' in line:
            raw = re.findall(r'>([^:<]+)', line)
            if len(raw) == 1:
                raw.append('')
            data.append(raw[1].strip())

    columns = '{0:<10}{1:<9}{2:<11}{3:<11}{4:<14}{5:<20}'
    print columns.format('Section', 'CCN', 'Enrolled', 'Waitlist', 'Time', 'Place')
    print '-------   -----    --------   --------   -----------   --------------'

    sections = zip(*[iter(data)] * 11)
    # sections contains a list per section:
    # [course, coursetitle, location, instructor, status, ccn, units,
    #  finalgroup, restrictions, note]

    for ccn_lookup, section in zip(ccns, sections):
        enrolled, waitlist = stats[ccn_lookup]
        name = ' '.join(section[0].split()[-2:])
        time_place = section[2].split(',')*2
        time = time_place[0].strip()
        place = time_place[1].strip()
        result = columns.format(name, section[5], enrolled, waitlist, time, place)

        # check if a section has space
        students, spaces = map(int, enrolled.split('/'))
        if students < spaces:
            result = result.replace(enrolled, colors.header(enrolled), 1)
        print result

if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'class',
        nargs='*',
        help='<dept abbrev> <coursenum>')
    args = vars(parser.parse_args())
    if not args['class']:
        print 'USAGE: python schedule.py <dept abbrev> <coursenum>'
        sys.exit()
    dept = args['class'][:-1]
    num = args['class'][-1]
    dept = '+'.join(dept) if dept else 'cs'
    course_search(dept, num)
