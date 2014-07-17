#!/usr/bin/python

import argparse
import re
import sys
import urllib
import urllib2

from multiprocessing import Pool

TERM = ["FL", "SP", "SU"][0]
SEMESTER_CODE = "14D2"

class colors:
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    @staticmethod
    def header(msg):
        return colors.HEADER + msg + colors.ENDC

    @staticmethod
    def fail(msg):
        return colors.FAIL + msg + colors.ENDC

def scrape_enrollment(ccn):
    url = "https://telebears.berkeley.edu/enrollment-osoc/osc"
    data = urllib.urlencode({"_InField1":"RESTRIC",
                             "_InField2":str(ccn),
                             "_InField3":SEMESTER_CODE})
    content = urllib2.urlopen(urllib2.Request(url, data)).read()
    numbers = []
    for line in filter(lambda l: 'limit' in l, content.split('\n')):
        numbers += re.findall(r'([0-9]+)', line)
    numbers += ['0']*4
    enrolled = numbers[0] + '/' + numbers[1]
    waitlist = numbers[2] + '/' + numbers[3]
    return (ccn, (enrolled, waitlist))

def course_search(dept, num):
    url = 'https://osoc.berkeley.edu/OSOC/osoc?y=0&p_term={}&p_deptname=--+Ch' \
          'oose+a+Department+Name+--&p_classif=--+Choose+a+Course+Classificat' \
          'ion+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&p_course={}&' \
          'p_dept={}&x=0'.format(TERM, num, dept)
    contents = urllib.urlopen(url).read()

    stats = {}
    def save(res):
        if res: stats[res[0]] = res[1]

    pool = Pool(30)
    ccns = re.findall(r'input type="hidden" name="_InField2" value="([0-9]*)"',
                      contents)
    for ccn in ccns:
        pool.apply_async(scrape_enrollment, (ccn,), callback=save)
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
    dept = args['class'][:-1]
    num = args['class'][-1]
    dept = '+'.join(dept) if dept else 'cs'
    course_search(dept, num)
