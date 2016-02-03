from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark_cassandra import streaming
import pyspark_cassandra, redis, sys


def track_trends(rdditer):
	redis_session = redis.Redis(host=REDIS_CLUSTER_IP, port=REDIS_CLUSTER_PORT, db=0)
	with redis_session.pipeline() as pipe:
		for data in rdditer:
			pipe.zincrby("trends", str(data[2]), 1)
			pipe.zincrby("location_trend", str(data[3]), 1)
			# add song counts by regions
		pipe.execute()


if __name__ == "__main__":
	conf = SparkConf().setAppName("StreamingLayer").setMaster(SPARK_MASTER).set("spark.cassandra.connection.host", CASSANDRA_SEED_NODE_IP)
	sc = SparkContext(conf=conf)
	ssc = StreamingContext(sc, 1)

	brokers, topic = sys.argv[1:]
	kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
	lines = kvs.map(lambda x: x[1].split(","))
	song_req_by_time = lines.map(lambda x: {"time" : x[0], "user_id": x[1], "song_id": x[2]})
	user_to_song = lines.map(lambda x: {"user_id": x[1], "time": x[0], "song_id": x[2]})
	song_to_user = lines.map(lambda x: {"song_id": x[2], "time": x[0], "user_id": x[1]})

	lines.foreachRDD(lambda rdd: rdd.foreachPartition(track_trends))

	song_req_by_time.saveToCassandra(CASSANDRA_KEYSPACE, "usrsnglog")
	user_to_song.saveToCassandra(CASSANDRA_KEYSPACE, "usrsng")
	song_to_user.saveToCassandra(CASSANDRA_KEYSPACE, "sngusr")


	ssc.start()
	ssc.awaitTermination()
