import re
import sys
import urllib
import threading

class myThread(threading.Thread):
	def __init__(self, ccn, data):
		self.ccn = ccn
		self.data = data
		threading.Thread.__init__(self)

	def run(self):
		section_url = "https://telebears.berkeley.edu/enrollment-osoc/osc?_InField1=RESTRIC&_InField2="+str(self.ccn)+"&_InField3=13B4"
		content = urllib.urlopen(section_url).read()
		numbers = []
		for line in content.split('\n'):
			if 'limit' in line:
				match = re.findall(r'([0-9]+)', line)
				if match:
					numbers += match

		(enrolled, limit, wait_list, wait_limit) = (0, 0, 0, 0)

		match = re.search(r"faced size1 bolded'>([^:]+):</div>", content)
		if not match:
			return

		info = " ".join(match.group(1).split()[-2:])
		enrolled = numbers[0]
		limit = numbers[1]

		if (len(numbers) == 4):
			wait_list = numbers[2]
			wait_limit = numbers[3]
			
		self.data.append((info, self.ccn, enrolled, limit, wait_list, wait_limit))


def main():
	dept = sys.argv[1]
	num = sys.argv[2]
	class_url = 'https://osoc.berkeley.edu/OSOC/osoc?y=0&p_term=SP&p_deptname=--+Choose+a+Department+Name+--&p_classif=--+Choose+a+Course+Classification+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&p_course=' + num + '&p_dept=' + dept + '&x=0'
	contents = urllib.urlopen(class_url).read()

	data = []
	threads = []

	match = re.findall(r'input type="hidden" name="_InField2" value="([0-9]*)"', contents)
	for ccn in match:
		t = myThread(ccn, data)
		t.start()
		threads.append(t)

	for t in threads:
		t.join()

	data = sorted(data, key=lambda x: x[0])
	four_columns = '{0:<9} {1:<7} {2:<9} {3:<9}'
	print four_columns.format('Name', 'CCN', 'Enrolled', 'Waitlist')
	
	for info, ccn, enrolled, limit, wait_list, wait_limit in data:
		enrolled = str(enrolled) + '/' + str(limit)
		wait_list = str(wait_list) + '/' + str(wait_limit)
		print four_columns.format(info, ccn, enrolled, wait_list)


if __name__=="__main__":
	main()

