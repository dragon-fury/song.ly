import sys

"""
The purpose of this script is to produce comma separated
user-song and song-user request pairs and persist them.

"""



filed = open(sys.argv[1], "r")
write_users = open("user_list.csv", "w+")
write_songs = open("song_list.csv", "w+")
write_counts = open("user_song_count.csv", "w+")

users = songs = {}
counter = user_counter = song_counter = 0
user_list = song_list = counts_list = ""

for line in filed:
	user, song, count = line.split("\t")
	if user not in users:
		user_counter+=1
		users[user] = user_counter
		user_list += str(users[user]) +","+ user+"\n"

	if song not in songs:
		song_counter+=1
		songs[song] = song_counter
		song_list += str(songs[song]) +","+ song+"\n"

	counts_list += str(users[user]) +","+ str(songs[song]) +","+ count
	counter += 1

	# write to files after every 10000 rows read
	if counter > 10000:
		write_users.write(user_list)
		write_songs.write(song_list)
		write_counts.write(counts_list)

		counter = 0
		user_list = song_list = counts_list = ""

if counter > 0:
	write_users.write(user_list)
	write_songs.write(song_list)
	write_counts.write(counts_list)


write_counts.close()
write_songs.close()
write_users.close()
filed.close()
