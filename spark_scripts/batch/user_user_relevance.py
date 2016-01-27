import sys

from pyspark import SparkConf
import pyspark_cassandra
from pyspark_cassandra import CassandraSparkContext

if __name__ == "__main__":
	sc = SparkContext(conf=conf)



	ssc.start()
	ssc.awaitTermination()

