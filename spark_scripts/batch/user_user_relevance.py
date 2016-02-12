import pyspark_cassandra, time, config
from pyspark import SparkConf
from datetime import datetime, timedelta
from pyspark_cassandra import CassandraSparkContext
from collections import Counter

"""
This script calculates relevance_score between users for a given time period.

relevance_score(A,B) = (number of songs common between users A & B)/ (number of songs listened to by user A)

	1. Find all the song requests by a given user within a given period of time (5 weeks here)
	2. For each song
		2.1. Find the top N (11 here) users who listened to the song in given time period
		2.2. Collect the users
	3. Count the number of times each user occured in the list
	4. Calculate the relevance score for each user with given user and take top 25 users
	5. Format and store the data into user_relevance cassandra table
"""

five_weeks_back = int((datetime.today() + timedelta(weeks=-5)).strftime('%s')) - 1
now = int(datetime.today().strftime('%s'))

def time_range_filter(line):
	val = line.split(",")
	if len(val) < 3:
		return False
	return (int(val[0]) > five_weeks_back and int(val[0]) < (now+1))

def parse_log_entry(line):
	val = line.split(",")
	if len(val) < 3:
		return None
	return (str(val[1]), [str(val[2])])

if __name__ == "__main__":
	conf = SparkConf().setAppName("UserUserRelevance").setMaster(config.SPARK_MASTER).set("spark.cassandra.connection.host", config.CASSANDRA_SEED_NODE_IP)
	sc = CassandraSparkContext(conf=conf)
	
	filename = datetime.now().strftime("%Y-%m-%d")+"-usersonglog.txt"

	users = sc.textFile(config.HDFS_URL+":"+config.HDFS_PORT+config.LOG_FOLDER+filename) \
						.filter(time_range_filter) \
						.map(parse_log_entry) \
						.keys() \
						.collect()

	song_map = {} # store song to user mapping for use in later stages

	usersongdb = sc.cassandraTable(config.CASSANDRA_KEYSPACE, "user_to_song")
	songuserdb = sc.cassandraTable(config.CASSANDRA_KEYSPACE, "song_to_user")

	for user in users:
		user_suggest = []
		song_list = usersongdb.select("song_id") \
				.where("user_id=? and req_time > ? and req_time < ?", int(user), five_weeks_back, now+1) \
				.map(lambda row: row.song_id) \
				.distinct() \
				.collect()
		songs = list(set(song_list))

		for song in songs:
			if song in song_map:
				listeners = song_map[song]
			else:
				listeners = songuserdb.select("user_id") \
						.where("song_id=? and req_time > ? and req_time < ?", int(song), five_weeks_back, now+1) \
						.map(lambda row: (row.user_id, 1)) \
						.reduceByKey(lambda count1, count2: count1+count2) \
						.sortBy(lambda x: x[1], ascending=False) \
						.map(lambda x: x[0]) \
						.take(11)
				song_map[song] = list(listeners)

			if user in listeners:
				listeners.remove(user)
			user_suggest += listeners

		if len(user_suggest) > 0 and len(songs) > 0:

			user_freq = Counter(user_suggest)

			rdd = sc.parallelize([{
				"user_id": user,
				"timestamp": now,
				"suggested_user_id": suggested_user[0],
				"relevance_score": round(float(suggested_user[1])/len(songs) , 3)
			} for suggested_user in user_freq.most_common(25)])

			rdd.saveToCassandra(config.CASSANDRA_KEYSPACE, "user_relevance")

	sc.stop()
