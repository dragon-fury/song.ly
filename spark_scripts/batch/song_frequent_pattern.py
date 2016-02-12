import pyspark_cassandra, time, config
from pyspark import SparkConf
from pyspark_cassandra import CassandraSparkContext
from collections import Counter
from itertools import combinations
from datetime import datetime, timedelta

"""
This script provides frequency for pairs of songs frequently listened together
in a given time period.

	1. Find all the song requests within a given period of time (5 weeks here)
	2. Group the requests by users' id to obtain a list of "transaction" of songs
	3. For each "transaction" of songs find all the combinations of songs
	4. Filter out song pairs occuring together less than a given frequency threshold
	5. Format and store the data into frequent_song_pairs cassandra table
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

def produce_song_pairs(song_list):
	song_pairs = combinations(song_list, 2)
	song_pairs_list = map(lambda song_pair: (song_pair, 1), song_pairs)
	return song_pairs_list

def cassandra_row_format(song_pair):
	songs = song_pair[0]
	frequency = song_pair[1]
	return [{"song_id": int(songs[0]), "freq_song_id": int(songs[1]), "frequency": frequency}, {"song_id": int(songs[1]), "freq_song_id": int(songs[0]), "frequency": frequency}]


if __name__ == "__main__":
	conf = SparkConf().setAppName("FrequentPatternsSongs").setMaster(config.SPARK_MASTER).set("spark.cassandra.connection.host", config.CASSANDRA_SEED_NODE_IP)
	sc = CassandraSparkContext(conf=conf)
	frequency_threshold = 3

	filename = datetime.now().strftime("%Y-%m-%d")+"-usersonglog.txt"

	sc.textFile(config.HDFS_URL+":"+config.HDFS_PORT+config.LOG_FOLDER+filename) \
		.filter(time_range_filter) \
		.map(parse_log_entry) \
		.reduceByKey(lambda song1, song2: song1+song2) \
		.map(lambda x: sorted(set(x[1]))) \
		.flatMap(produce_song_pairs) \
		.reduceByKey(lambda a,b: a+b) \
		.filter(lambda song_pair: song_pair[1] > frequency_threshold) \
		.flatMap(cassandra_row_format) \
		.saveToCassandra(config.CASSANDRA_KEYSPACE, "frequent_song_pairs")

	sc.close()
