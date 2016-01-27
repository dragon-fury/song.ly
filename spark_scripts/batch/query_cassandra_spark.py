from pyspark import SparkConf
import pyspark_cassandra
from pyspark_cassandra import CassandraSparkContext

conf = SparkConf().setAppName("PySpark Cassandra").setMaster("spark://ip-172-31-2-132:7077").set("spark.cassandra.connection.host", "52.89.0.21")
sc = CassandraSparkContext(conf=conf)
usr = sc.cassandraTable("usersong", "usrsng")
rows = usr.select("user_id", "req_time", "song_id").where("user_id=?", 1)

