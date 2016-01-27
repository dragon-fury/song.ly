# Source: http://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
import random
import time

def strTimeProp(start, end, format, prop):
	stime = time.mktime(time.strptime(start, format))
	etime = time.mktime(time.strptime(end, format))

	ptime = stime + prop * (etime - stime)

	return time.strftime("%s", time.localtime(ptime))


def randomDate(start, end, prop):
	return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', prop)

# print randomDate("1/1/2015 12:00 AM", "1/20/2016 12:00 AM", random.random())