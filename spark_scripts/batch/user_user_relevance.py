import pyspark_cassandra, time, config
from pyspark import SparkConf
from datetime import datetime, timedelta
from pyspark_cassandra import CassandraSparkContext
from collections import Counter

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

# Make userid parameterized

if __name__ == "__main__":
	conf = SparkConf().setAppName("UserUserRelevance").setMaster(config.SPARK_MASTER).set("spark.cassandra.connection.host", config.CASSANDRA_SEED_NODE_IP)
	sc = CassandraSparkContext(conf=conf)
	
	filename = datetime.now().strftime("%Y-%m-%d")+"-usersonglog.txt"

	users = sc.textFile(config.HDFS_URL+":"+config.HDFS_PORT+config.LOG_FOLDER+filename) \
						.filter(time_range_filter) \
						.map(parse_log_entry) \
						.keys() \
						.collect()

	song_map = {}
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
				song_map[song] = list(set(listeners))

			if user in listeners:
				listeners.remove(user)
			user_suggest += listeners

		if len(user_suggest) > 0 and len(songs) > 0:

			user_freq = Counter(user_suggest)

			# relevance_score = # common songs (user, suggested_user)/ #songs for user
			rdd = sc.parallelize([{
				"user_id": user,
				"timestamp": now,
				"suggested_user_id": suggested_user[0],
				"relevance_score": round(float(suggested_user[1])/len(songs) , 3)
			} for suggested_user in user_freq.most_common(25)])

			rdd.saveToCassandra(config.CASSANDRA_KEYSPACE, "user_relevance")

	sc.stop()
