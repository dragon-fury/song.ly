song.ly - connected by songs
=================================

song\.ly (song + friendly) is a song recommendation application built during my time at Insight Data Engineering program.  

Motivation
=============
- many talented local artists get lesser visibility and reach in music streaming applications - increase their reach
- everybody likes to listen to songs but there is no community of people with similar musical tastes - connect
- personalized recommendations often tie users down to their history and fail to provide reasons for why something is recommened to the user

song.ly presents an alternative approach to address the above concerns.
    
Introduction
================
song.ly is a song recommendation application with the following features:  
> - Suggest songs to a user based on the songs listened to by the most relevant friends of the user
> - Suggest artists to listen to based on the current location of the user
> - Suggest friends based on a relevance score which mimics a naive, logical implementation of collaborative filtering defined as:

>> <a href="http://tinypic.com?ref=w2hc1g" target="_blank"><img src="http://i66.tinypic.com/w2hc1g.jpg" border="0" alt="Image and video hosting by TinyPic"></a>

Datasets
=============
I used the "Million Song Dataset" [1] which is "a freely-available collection of audio features and metadata for a million contemporary popular music tracks" according to [Labrosa](http://labrosa.ee.columbia.edu/millionsong) website. Along with the metadata for songs a list of more than 150 M user-song request pairs was obtained from [Echonest](http://labrosa.ee.columbia.edu/millionsong/tasteprofile) [2] and [Last.fm](http://www.last.fm/). Also a list of unique artists with their location information was obtained from Echonest. More details can be found [here](goo.gl/NcaIeP).

Data Pipeline
================
<a href="http://tinypic.com?ref=w1dwm8" target="_blank"><img src="http://i64.tinypic.com/w1dwm8.png" border="0" alt="Image and video hosting by TinyPic"></a>

####Ingestion Layer
[Kafka](http://kafka.apache.org/): The user taste profile is used to synthesize more user-song requests as a stream of request data. A synthesized stream of user's current location and the user-song requests are ingested into Kafka.

####Streaming Layer
[Spark Streaming](http://spark.apache.org/streaming): The ingested data gets processed by Spark streaming to extract data in the required formats. The information of user-song request with timestamp is stored into [Cassandra](http://cassandra.apache.org/) - a NoSQL data store. The counts for requested songs and the users' current locations are stored in [Redis](http://redis.io) - a caching datastore - for faster access. The data is periodically flushed into [HDFS](http://hortonworks.com/hadoop/hdfs/).

####Batch Layer
[Spark](http://spark.apache.org): Apache Spark reads data from HDFS to find friend suggestions and songs frequently played together. The recommendations are explained [here](https://goo.gl/Nggqt9).

Cassandra Tables
===============
user_song_log: (streaming) stores user-song requests partitioned by time  
user_to_song: (streaming) stores user-song requests partitioned by user  
song_to_user: (streaming) stores user-song requests partitioned by song  
user_connections: stores user's connections (follows) partitioned by user  
user_relevance: (batch) stores suggested users with relevance score  
frequent_song_pairs: (batch) stores song-song frequencies  

Demo
===========
The application can be accessed at [song.ly](http://song-ly.herokuapp.com)
To login username: adam, password: 123


References
===============
[1] Thierry Bertin-Mahieux, Daniel P.W. Ellis, Brian Whitman, and Paul Lamere. 
	The Million Song Dataset. In Proceedings of the 12th International Society
	for Music Information Retrieval Conference (ISMIR 2011), 2011.

[2] The Echo Nest Taste profile subset, the official user data collection for the Million Song
	Dataset, available at: http://labrosa.ee.columbia.edu/millionsong/tasteprofile