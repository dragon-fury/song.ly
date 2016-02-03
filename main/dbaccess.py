from main import cassandra_session, redis_session
from cassandra import ReadTimeout
from datetime import datetime, timedelta
import json, config

class DBAccess(object):
	def __init__(self):
		self.cassandra_session = cassandra_session
		self.a_day_ago = (datetime.today() + timedelta(weeks=-15)).strftime('%s')
		self.now = datetime.today().strftime('%s')
		self.redis_session = redis_session

	def get_recommended_songs(self, user_id):
		results = self.cassandra_session.execute("select follows_id, relevance_score from usrusr where user_id="+user_id)
		most_relevant_friend = sorted(results, key=lambda row: row[1])[0][0]
		results = self.cassandra_session.execute("select song_id from usrsng where user_id="+str(most_relevant_friend)+" and req_time > "+self.a_day_ago+" and req_time < "+self.now)
		return list(set(map(lambda x: x[0], results)))

	def get_recommended_friends(self, user_id):
		suggestions = self.redis_session.hget("friend_suggest", str(usr))
		if not suggestions:
			results = self.cassandra_session.execute("select any_user_id, relevance_score from usrrelevance where user_id="+user_id+" and time >"+self.a_day_ago+" and time < "+self.now)
			most_relevant_friends = sorted(results, key=lambda row: row[1])[0]
			friend_suggestion_list = list(set(map(lambda friend_id: str(friend_id), most_relevant_friends)))
			self.redis_session.hset("friend_suggest", str(usr), ",".join(friend_suggestion_list))
		else:
			friend_suggestion_list = suggestions.split(",")

		self.group = "users"
		return map(self._make_json, friend_suggestion_list)

	def get_local_artists(self, area):
		self.group = "location"
		artist_ids = (self.redis_session.hget(self.group, area)).split(",")
		return map(self._make_json, artist_ids)

	def get_user_detail(self, user_id):
		self.group = "users"
		return self._make_json(user_id)

	def get_song_detail(self, song_id):
		self.group = "songs"
		return self._make_json(song_id)

	def get_trending_songs(self):
		top_10_songs = self.redis_session.zrevrange("trends", 0, 10, withscores=True, score_cast_func=int)
		songs_json = []
		self.group = "songs"
		for song in top_10_songs:
			song_name = self._make_json(song[0])["name"]
			songs_json.append({"name": song_name, "count": song[1]}) 
		return songs_json

	def _make_json(self, key):
		result = self.redis_session.hget(self.group, str(key))
		if not result:
			result = "{}"
		return json.loads(result)