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
			bold.append(str(i))
		if ((re.findall("enrolled, with a limit of", str(i)) != [])):
			numbers = re.findall(r"([1-9][0-9]*)", str(i))

	className = ""
	enrolled = numbers[0]
	limit = numbers[1]
	waitList = numbers[2]
	waitListLimit = numbers[3]
	remaining = int(limit) - int(enrolled)
	for i in range(43, len(bold[1]) - 7):
		className += bold[1][i]
	
	print '\n' + className
	print 'Enrolled: ' + (enrolled) + ' Limit: ' + (limit) + ' Remaining: ' + remaining
	print 'Waiting List: ' + (waitList) + ' Limit: ' + aitListLimit + '\n'






def main():
	ccn = sys.argv[1]
	get_live_info(ccn)


if __name__=="__main__":
	main()