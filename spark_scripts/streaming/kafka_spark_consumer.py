import pyspark_cassandra, redis, sys, config
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark_cassandra import streaming


def track_trends(rdditer):
	redis_session = redis.Redis(host=config.REDIS_CLUSTER_IP, port=config.REDIS_CLUSTER_PORT, db=config.DBCOUNT)
	with redis_session.pipeline() as pipe:
		for data in rdditer:
			pipe.zincrby("trends", str(data[2]), 1)
		pipe.execute()


if __name__ == "__main__":
	conf = SparkConf().setAppName("StreamingLayer").setMaster(SPARK_MASTER).set("spark.cassandra.connection.host", config.CASSANDRA_SEED_NODE_IP)
	sc = SparkContext(conf=conf)
	ssc = StreamingContext(sc, 1)

	brokers, topic = sys.argv[1:]
	kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
	lines = kvs.map(lambda x: x[1].split(","))
	song_req_by_time = lines.map(lambda x: {"timestamp" : x[0], "user_id": x[1], "song_id": x[2]})
	user_to_song = lines.map(lambda x: {"user_id": x[1], "req_time": x[0], "song_id": x[2]})
	song_to_user = lines.map(lambda x: {"song_id": x[2], "req_time": x[0], "user_id": x[1]})

	lines.foreachRDD(lambda rdd: rdd.foreachPartition(track_trends))

	song_req_by_time.saveToCassandra(config.CASSANDRA_KEYSPACE, "user_song_log")
	user_to_song.saveToCassandra(config.CASSANDRA_KEYSPACE, "user_to_song")
	song_to_user.saveToCassandra(config.CASSANDRA_KEYSPACE, "song_to_user")


	ssc.start()
	ssc.awaitTermination()
