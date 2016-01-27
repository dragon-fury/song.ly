import sys

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark_cassandra
from pyspark_cassandra import streaming

if __name__ == "__main__":
    conf = SparkConf().setAppName("PySpark Cassandra Test").setMaster("spark://ip-172-31-2-132:7077").set("spark.cassandra.connection.host", "52.89.0.21")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 1)

    brokers, topic = sys.argv[1:]
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
    lines = kvs.map(lambda x: x[1].split(","))
    #result = lines.map(lambda x: {"time" : x[0], "user_id": x[1], "song_id": x[2], "count": x[3]})
    result = lines.map(lambda x: {"user_id": x[1], "time": x[0], "song_id": x[2]})
    result.count().pprint()
    #result.pprint()
    result.saveToCassandra("usersong", "usrsng")

    ssc.start()
    ssc.awaitTermination()
