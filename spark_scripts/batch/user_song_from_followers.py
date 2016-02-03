# For this implementation: Think of a day when new album was released and heavy traffic was on that one album
import pyspark_cassandra, time
from pyspark import SparkConf, SparkContext
from datetime import datetime, timedelta
from pyspark_cassandra import CassandraSparkContext
from collections import Counter

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

	filename = datetime.now().strftime("%Y-%m-%d")+"-usersonglog.txt"
	users = sc.textFile("hdfs://ec2-52-35-204-86.us-west-2.compute.amazonaws.com:9000/sesha/hadoop/logs/"+filename) \
						.filter(filterem) \
						.map(parse_log_entry) \
						.filter(lambda pair: pair != None) \
						.keys() \
						.collect()

	sc.stop()

	time.sleep(5)

	five_weeks_back = int((datetime.today() + timedelta(weeks=-5)).strftime('%s')) - 1
	now = int(datetime.today().strftime('%s'))

	conf = SparkConf().setAppName("UserUserRelevance").setMaster("spark://ip-172-31-2-132:7077").set("spark.cassandra.connection.host", "52.89.0.21")
	sc = CassandraSparkContext(conf=conf)

	user_suggest = []
	songuserdb = sc.cassandraTable("usersong", "sngusr")
	useruserdb = sc.cassandraTable("usersong", "usrusr")
	usersongdb = sc.cassandraTable("usersong", "usrsnglog")

	song_map = {}
	for user in users:
		songs = list(users[user])

		for song in songs:
			rows = songuserdb.select("song_id", "req_time", "user_id") \
					.where("song_id=? and req_time > ? and req_time < ?", song, five_weeks_back, now+1) \
					.filter(lambda song: len(song) == 3) \
					.map(lambda row: (row["song_id"], [row["user_id"]])) \
					.reduceByKey(lambda user1, user2: user1+user2) \
					.values() \
					.collect()
			user_suggest += list(set(rows[0]))

		
		user_freq = Counter(user_suggest)

		# relevance_score = # common songs (user, any_user)/ #songs for user
		rdd = sc.parallelize([{
			"user_id": user,
			"time": now,
			"any_user_id": any_user[0],
			"relevance_score": round(float(any_user[1])/ , 3)
		} for any_user in user_freq.most_common(25)])

		rdd.saveToCassandra("usersong", "usrrelevance")

	sc.stop()
