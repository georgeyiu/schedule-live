import re
import sys
import urllib
import threading

class myThread(threading.Thread):
	def __init__(self, ccn, stats):
		self.ccn = ccn
		self.stats = stats
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

		if (len(numbers) >= 2):
			enrolled = numbers[0]
			limit = numbers[1]
		if (len(numbers) == 4):
			wait_list = numbers[2]
			wait_limit = numbers[3]

		e = str(enrolled) + '/' + str(limit)
		w = str(wait_list) + '/' + str(wait_limit)

		self.stats[self.ccn] = (e, w)


def main():

	dept = ""
	numIndex = len(sys.argv) - 1
	for i in range(1, numIndex):
		if (i < numIndex - 1):
			dept += sys.argv[i] + " " 
		else:
			dept += sys.argv[i]
		
	num = sys.argv[numIndex]
	class_url = 'https://osoc.berkeley.edu/OSOC/osoc?y=0&p_term=SP&p_deptname=--+Choose+a+Department+Name+--&p_classif=--+Choose+a+Course+Classification+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&p_course=' + num + '&p_dept=' + dept + '&x=0'
	contents = urllib.urlopen(class_url).read()

	stats = {}
	threads = []
	ccns = re.findall(r'input type="hidden" name="_InField2" value="([0-9]*)"', contents)
	for ccn in ccns:
		t = myThread(ccn, stats)
		t.start()
		threads.append(t)

	for t in threads:
		t.join()

	data = []
	for line in contents.split('\n'):
		if ':&#160;' in line:
			raw = re.findall(r'>([^:<]+)', line)
			if len(raw) == 1:
				raw.append('')
			data.append(raw[1].strip())

	columns = '{0:<10}{1:<8}{2:<11}{3:<11}{4:<14}{5:<20}'
	print columns.format('Section', 'CCN', 'Enrolled', 'Waitlist', 'Time', 'Place')
	print '-------   -----   --------   --------   -----------   --------------'

	sections = zip(*[iter(data)] * 11)
	# sections contains a list per section:
	# [course, coursetitle, location, instructor, status, ccn, units, 
	#  finalgroup, restrictions, note]

	for i, g in enumerate(sections):
		enrolled, wait_list = stats[ccns[i]]
		name = ' '.join(g[0].split()[-2:])
		time_place = map(lambda x: x.strip(), g[2].split(','))
		if len(time_place) == 2:
			time = time_place[0]
			place = time_place[1]
		else:
			time = time_place[0]
			place = time_place[0]
		print columns.format(name, g[5], enrolled, wait_list, time, place)


if __name__=="__main__":
	main()

