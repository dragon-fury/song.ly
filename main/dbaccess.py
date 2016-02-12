from main import cassandra_session, redis_session
from cassandra import ReadTimeout
from datetime import datetime, timedelta
import json, config
"""
	Perform all the database access for the application
"""
class DBAccess(object):
	def __init__(self):
		self.five_weeks_ago = (datetime.today() + timedelta(weeks=-5)).strftime('%s')
		self.now = datetime.today().strftime('%s')
		self.cassandra_session = cassandra_session
		self.redis_session = redis_session

	"""
		Get songs listened to by the top 5 most relevant connections for a given user_id 
		(in the past 1 hour) and suggest top 10 songs that the user_id has not listened to.
	"""
	def get_recommended_songs(self, user_id):
		an_hour_ago = (datetime.today() + timedelta(hours=-1)).strftime('%s')

		results = self.cassandra_session.execute("select follows_id, relevance_score from user_connections where user_id="+user_id)
		friends = sorted(results, key=lambda row: row[1], reverse=True)
		recommended_songs = []
		friends_song_list = []

		if len(friends) > 0:
			# Get top 5 relevant connections for the user_id
			most_relevant_friends = friends[0][0:5]
			for friend_id in most_relevant_friends:
				friends_song_list += self.cassandra_session.execute("select song_id from user_to_song where user_id="+str(friend_id)+" and req_time > "+self.an_hour_ago+" and req_time < "+self.now)

			# Get songs played by the user_id in last 5 weeks
			played = self.cassandra_session.execute("select song_id from user_to_song where user_id="+str(user_id)+" and req_time > "+self.five_weeks_ago+" and req_time < "+self.now)

			# Find songs that the user_id has not listened to
			recommended_songs = list(set(map(lambda x: x[0], played)).difference(set(map(lambda x: x[0], results))))
			
			for song in recommended_songs[0:10]:
				song_json = json.loads(self.redis_session.hget("songs", str(song)))
				song_json["song_id"] = song		
				recommended_songs.append(song_json)

		friend = json.loads(self.redis_session.hget("usersid", most_relevant_friend))
		return {"friend": friend["name"], "songs": recommended_songs}

	"""
		Find the suggested user list with their relevance score calculated in last 5 weeks.
		Sort them by their recent relevance score and get recent, unique tuples of (user, relevance_score)
		Sort the tuples from highest relevance_score to lowest relevance_score.
		Suggest the top 10 user_ids as recommended connections.
	"""
	def get_recommended_friends(self, user_id):
		suggestions = self.redis_session.hget("friend_suggest", str(user_id))

		if not suggestions:
			results = self.cassandra_session.execute("select timestamp, suggested_user_id, relevance_score from user_relevance where user_id="+user_id+" and timestamp >"+self.five_weeks_ago+" and timestamp < "+self.now)
			friends_list_tuple = map(lambda row: (timestamp, str(row[0]), row[1]), results)
			sorted_by_recency = sorted(friends_list_tuple, key=lambda row: row[0], reverse=True)

			seen = set()
			friends_by_relevance = []
			# Get unique users by the most recent relevance_score
			for idx in xrange(len(sorted_by_recency)):
				friend_id = sorted_by_recency[idx][1]
				if friend_id not in seen:
					friends_by_relevance.append((sorted_by_recency[idx][1], sorted_by_recency[idx][2]))
					seen.add(friend_id)

			friends_by_relevance = sorted(friends_by_relevance, key=lambda row: row[1], reverse=True)

			# Suggest top 10 users by relevance_score
			friend_suggestion_list = map(lambda x: x[0], friends_by_relevance[0:10])
			self.redis_session.hset("friend_suggest", str(user_id), ",".join(friend_suggestion_list))
		else:
			friend_suggestion_list = suggestions.split(",")

		self.group = "usersid"
		return map(self._make_json, friend_suggestion_list)


	"""
		Get the songs that are frequently played together with the current song
		selected by the user. This way we can handle cold-start problem to some
		extent.
	"""
	def get_frequent_songs(self, song_id):
		results = self.cassandra_session.execute("select freq_song_id from frequent_song_pairs where song_id="+song_id+"limit 10")
		recommend_songs = []
		for song in results:
			song_json = json.loads(self.redis_session.hget("songs", str(song.freq_song_id)))
			song_json["song_id"] = song
			recommend_songs.append(song_json)

		return {"songs": recommend_songs}


	def get_local_artists(self, area):
		artist_ids = (self.redis_session.hget("location", area)).split(",")
		return map(lambda x: self.redis_session.hget("artists", x), artist_ids[0:10])

	def get_user_detail(self, user_id):
		self.group = "usersid"
		return self._make_json(user_id)

	def get_user_detail_from_name(self, user_name):
		self.group = "users"
		return self._make_json(user_name)

	def get_song_detail(self, song_id):
		self.group = "songs"
		return self._make_json(song_id)

	def get_trending_songs(self):
		top_10_songs = self.redis_session.zrevrange("trends", 0, 10, withscores=True, score_cast_func=int)
		songs_json = []
		self.group = "songs"
		for song in top_10_songs:
			song_detail = self._make_json(song[1])
			song_title = song_detail["title"]
			song_artist = song_detail["artist_name"]
			songs_json.append({"title": song_title, "artist": song_artist, "count": int(song[1])}) 
		return songs_json

	def get_recent_songs(self, user_id):
		now = datetime.today().strftime('%s')

		results = self.cassandra_session.execute("select req_time, song_id from user_to_song where user_id="+str(user_id)+" and req_time < "+now+" limit "+config.TREND_SONGS_COUNT)
		sort_results = sorted(results, key=lambda x: x[0], reverse=True)

		send_songs = []
		for song in sort_results:
			send_songs.append(json.loads(self.redis_session.hget("songs", str(song[1]))))
		return send_songs

	# Augment data using information from Redis datastore
	def _make_json(self, key):
		result = self.redis_session.hget(self.group, str(key))
		if not result:
			result = "{}"
		return json.loads(result)