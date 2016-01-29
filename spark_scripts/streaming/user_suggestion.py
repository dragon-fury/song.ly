from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark_cassandra
from pyspark_cassandra import streaming
from pyspark_cassandra import CassandraSparkContext
from datetime import datetime, timedelta

def parse_line(line):
	data = line.split(",")
	return {"user_id": data[1], "time": data[0], "song_id": data[2]}

def get_key(value):
	value.user_id = value.user_id+value.any_user_id
	return (value.user_id, value)

def get_suggests(value):
	if len(value) != 0:
		return value[1].any_user_id
	return

if __name__ == "__main__":
	conf = SparkConf().setAppName("UserSuggestion").setMaster("spark://ip-172-31-2-132:7077").set("spark.cassandra.connection.host", "52.89.0.21")
	sc = CassandraSparkContext(conf=conf)
	ssc = StreamingContext(sc, 1)

	brokers, topic = sys.argv[1:]
	kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
	result = kvs.map(parse_line)

	five_weeks_back = int((datetime.today() + timedelta(weeks=-5)).strftime('%s')) - 1
	now = int(datetime.today().strftime('%s'))

	users_suggested = sc.cassandraTable("usersong", "usrrelevance").select("user_id", "time", "any_user_id", "relevance_score") \
		.where("user_id=? and time > ? and time < ?", 1, five_weeks_back, now) \
		.map(get_key) \
		.reduceByKey(lambda x, y: x) \
		.sortBy(lambda x: x[1].relevance_score, ascending=False) \
		.map(get_suggests) \
		.take(10)

	ssc.start()
	ssc.awaitTermination()

