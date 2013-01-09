#schedule-live

View live registration information for Berkeley classes. 

Live enrollment for each lecture/section is typically hidden in links, making it very difficult to find open sections in a very full class. This script displays the live enrollment stats on a single page for all sections that come up in a search. For reference, [schedule.berkeley.edu search](http://osoc.berkeley.edu/OSOC/osoc?y=0&p_term=SP&p_deptname=--+Choose+a+Department+Name+--&p_classif=--+Choose+a+Course+Classification+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&p_course=104&p_dept=bio+eng&x=0).

###Basic Usage

	gy:schedule-live georgeyiu$ python schedule.py bio eng 104
	Section   CCN      Enrolled   Waitlist   Time          Place               
	-------   -----    --------   --------   -----------   --------------
	001 LEC   06527    94/141     6/15       MWF 11-12P    277 CORY            
	011 LAB   06530    13/15      1/15       Tu 4-7P       1111 ETCHEVERRY     
	012 LAB   06533    8/15       3/15       W 4-7P        1111 ETCHEVERRY     
	013 LAB   06536    3/30       1/30       Tu 4-7P       1171 ETCHEVERRY     
	014 LAB   06539    7/30       1/30       W 4-7P        1171 ETCHEVERRY     
	015 LAB   06542    13/15      0/15       Tu 1-4P       1111 ETCHEVERRY     
	016 LAB   06545    27/30      0/30       Tu 1-4P       1171 ETCHEVERRY     
	017 LAB   06548    15/15      0/15       Th 4-7P       1111 ETCHEVERRY     
	018 LAB   06551    8/30       0/30       Th 1-4P       1171 ETCHEVERRY 
