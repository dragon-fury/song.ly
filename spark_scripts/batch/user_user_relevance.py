import sys

from pyspark import SparkContext, SparkConf
import pyspark_cassandra

if __name__ == "__main__":
	conf = SparkConf().setAppName("UserUserRelevance").setMaster("spark://ip-172-31-2-132:7077").set("spark.cassandra.connection.host", "52.89.0.21")
	sc = SparkContext(conf=conf)

	user_song_rdd = sc.cassandraTable("usersong", "usrsng")
	

	ssc.start()
	ssc.awaitTermination()
