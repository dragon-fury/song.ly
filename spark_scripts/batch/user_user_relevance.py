# For this implementation: Think of a day when new album was released and heavy traffic was on that one album
import pyspark_cassandra, time
from pyspark import SparkConf, SparkContext
from datetime import datetime, timedelta
from pyspark_cassandra import CassandraSparkContext
from collections import Counter


five_weeks_back = int((datetime.today() + timedelta(weeks=-6)).strftime('%s')) - 1
now = int((datetime.today() + timedelta(weeks=-1)).strftime('%s')) - 1
# now = int(datetime.today().strftime('%s'))

def filterem(line):
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
	conf = SparkConf().setAppName("UserUserRelevance").setMaster("spark://ip-172-31-2-132:7077")
	sc = SparkContext(conf=conf)
	
	# filename = datetime.now().strftime("%Y-%m-%d")+"-usersonglog.txt"
	filename = "2016-01-27-usersonglog.txt"
	users = sc.textFile("hdfs://ec2-52-35-204-86.us-west-2.compute.amazonaws.com:9000/sesha/hadoop/logs/"+filename) \
						.filter(filterem) \
						.map(parse_log_entry) \
						.keys() \
						.collect()

	sc.stop()

	time.sleep(5)

	five_weeks_back = int((datetime.today() + timedelta(weeks=-6)).strftime('%s')) - 1
	now = int((datetime.today() + timedelta(weeks=-1)).strftime('%s')) - 1
	# now = int(datetime.today().strftime('%s'))

	conf = SparkConf().setAppName("UserUserRelevance").setMaster("spark://ip-172-31-2-132:7077").set("spark.cassandra.connection.host", "52.89.0.21")
	sc = CassandraSparkContext(conf=conf)

	song_map = {}
	usersongdb = sc.cassandraTable("usersong", "usrsng")
	songuserdb = sc.cassandraTable("usersong", "sngusr")

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

			# relevance_score = # common songs (user, any_user)/ #songs for user
			rdd = sc.parallelize([{
				"user_id": user,
				"timestamp": now,
				"suggested_user_id": any_user[0],
				"relevance_score": round(float(any_user[1])/len(songs) , 3)
			} for any_user in user_freq.most_common(25)])

			rdd.saveToCassandra("usersong", "user_relevance")

	sc.stop()
