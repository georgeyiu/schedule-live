html_doc = " " 
import urllib
import re
import sys

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc)

def get_live_info(ccn):
	openPage = urllib.urlopen("https://telebears.berkeley.edu/enrollment-osoc/osc?_InField1=RESTRIC&_InField2=" + str(ccn) + "&_InField3=13B4")
	soup = BeautifulSoup(openPage.read())
	bold = []
	for i in soup.find_all(["div"]):
 		if ((re.findall("faced size1 bolded", str(i)) != [])):
			bold.append(i)
		if ((re.findall("enrolled, with a limit of", str(i)) != [])):
			numbers = re.findall(r"([1-9][0-9]*)", str(i))

	className = bold[1].get_text()
	className = className[:len(className) -1]
	enrolled = numbers[0]
	limit = numbers[1]
	waitList = numbers[2]
	waitListLimit = numbers[3]
	remaining = str(int(limit) - int(enrolled))
	return (enrolled, limit, waitList, waitListLimit)

def main():
	dept = sys.argv[1]
	num = sys.argv[2]
	search_url = 'https://osoc.berkeley.edu/OSOC/osoc?y=0&p_term=SP&p_deptname=--+Choose+a+Department+Name+--&p_classif=--+Choose+a+Course+Classification+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&p_course=' + num + '&p_dept=' + dept + '&x=0'
	openPage = urllib.urlopen(search_url)
	contents = openPage.read()
	match = re.findall(r'input type=\"hidden\" name=\"_InField2\" value=\"([0-9]*)\"', contents)
	print '{0:<8} {1:<8} {2:<8} {3:<8} {4:<8}'.format('CCN', 'Enrolled', 'Limit', 'Waitlist', 'Limit')
	for ccn in match:
		enrolled, limit, waitList, waitListLimit = get_live_info(ccn)
		print '{0:<8} {1:<8} {2:<8} {3:<8} {4:<8}'.format(ccn, enrolled, limit, waitList, waitListLimit)


if __name__=="__main__":
	main()