from cassandra.cluster import Cluster

# Connect to cassandra cluster
cluster = Cluster([CASSANDRA_SEED_NODE_IP])
session = cluster.connect()

# Create and set cassandra keyspace to work
session.execute("CREATE KEYSPACE usersong WITH replication = {'class':'SimpleStrategy', 'replication_factor':3};")
session.set_keyspace("usersong")

# Create tables to insert data
session.execute("CREATE TABLE usrsnglog (time int, user_id int, song_id int, count int, primary key (time, user_id, song_id));")
session.execute("CREATE TABLE usrconnection (user_id int, follows_id int, relevance_score float, primary key(user_id, follows_id, relevance_score));")
session.execute("CREATE TABLE usrsng (user_id int, req_time int, song_id int,  primary key (user_id, req_time)) WITH CLUSTERING ORDER BY (req_time DESC);")
session.execute("CREATE TABLE sngusr (song_id int, req_time int, user_id int,  primary key (song_id, req_time)) WITH CLUSTERING ORDER BY (req_time DESC);")
session.execute("CREATE TABLE usrrelevance (user_id int, time int, suggest_user_id int, relevance_score int, primary key (user_id, time)) WITH CLUSTERING ORDER BY (time DESC);")

# Close the connection
session.shutdown()
cluster.shutdown()
