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
		numbers += ['0']*4
		enrolled = numbers[0] + '/' + numbers[1]
		waitlist = numbers[2] + '/' + numbers[3]
		self.stats[self.ccn] = (enrolled, waitlist)


def main():
	dept = '+'.join(sys.argv[1:-1])
	num = sys.argv[-1]
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
		print columns.format(name, section[5], enrolled, waitlist, time, place)


if __name__=="__main__":
	main()

