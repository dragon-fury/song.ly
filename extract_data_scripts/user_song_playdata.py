import sys, time, random

def strTimeProp(start, end, format, prop):
	stime = time.mktime(time.strptime(start, format))
	etime = time.mktime(time.strptime(end, format))

	ptime = stime + prop * (etime - stime)

	return time.strftime("%s", time.localtime(ptime))

def randomDate():
	return strTimeProp("1/1/2015 12:01 AM", "1/30/2016 11:59 PM", '%m/%d/%Y %I:%M %p', random.random())

filed = open(sys.argv[1], "r")
write_user_song = open("user_to_song.csv", "w+")
write_song_user = open("song_to_user.csv", "w+")

counter = 0
total_counter = 0
user_song_list = ""
song_user_list = ""

for line in filed:
	user, song, count = line.split(",")
	for t in xrange(int(count)):
		timed = randomDate()
		user_song_list += user+","+timed+","+song+"\n"
		song_user_list += song+","+timed+","+user+"\n"
		counter += 1
		total_counter += 1

	if counter > 100000:
		write_user_song.write(user_song_list)
		write_song_user.write(song_user_list)

		counter = 0
		user_song_list = ""
		song_user_list = ""

if counter > 0:
	write_user_song.write(user_song_list)
	write_song_user.write(song_user_list)


write_user_song.close()		
write_song_user.close()		
filed.close()	
