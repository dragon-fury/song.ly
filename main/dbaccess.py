from main import cassandra_session, redis_session
from cassandra import ReadTimeout
from datetime import datetime, timedelta
import json, pdb

class DBAccess(object):
	def __init__(self):
		self.cassandra_session = cassandra_session
		self.fifteen_weeks_ago = (datetime.today() + timedelta(weeks=-15)).strftime('%s')
		self.now = datetime.today().strftime('%s')
		self.redis_session = redis_session

	def get_recommended_songs(self, user_id):
		results = self.cassandra_session.execute("select follows_id, relevance_score from usrusr where user_id="+user_id)
		friends = sorted(results, key=lambda row: row[1], reverse=True)
		send_songs = []
		if len(friends) > 0:
			most_relevant_friend = friends[0][0]
			results = self.cassandra_session.execute("select song_id from usrsng where user_id="+str(most_relevant_friend)+" and req_time > "+self.fifteen_weeks_ago+" and req_time < "+self.now)
			played = self.cassandra_session.execute("select song_id from usrsng where user_id="+str(user_id)+" and req_time > "+self.fifteen_weeks_ago+" and req_time < "+self.now)
			recommended_songs = list(set(map(lambda x: x[0], played)).difference(set(map(lambda x: x[0], results))))
			
			for song in recommended_songs[0:10]:
				send_songs.append(json.loads(self.redis_session.hget("songs", str(song))))
		return send_songs

	def get_recommended_friends(self, user_id):
		suggestions = self.redis_session.hget("friend_suggest", str(user_id))
		if not suggestions:
			results = self.cassandra_session.execute("select any_user_id, relevance_score from usrrelevance where user_id="+user_id+" and time >"+self.fifteen_weeks_ago+" and time < "+self.now)
			friends_list_tuple = map(lambda row: (str(row[0]), row[1]), results)
			friends_by_relevance = sorted(friends_list_tuple, key=lambda row: row[1], reverse=True)
			
			seen = set()
			friend_suggestion_list = []
			for idx in xrange(len(friends_by_relevance)):
				if len(seen) == 10:
					break
				friend_id = friends_by_relevance[idx][0]
				if friend_id not in seen:
					friend_suggestion_list.append(friend_id)
					seen.add(friend_id)

			self.redis_session.hset("friend_suggest", str(user_id), ",".join(friend_suggestion_list))
		else:
			friend_suggestion_list = suggestions.split(",")

		self.group = "usersid"
		return map(self._make_json, friend_suggestion_list)

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
			songs_json.append({"title": song_title, "artist": song_artist, "count": int(song[0])}) 
		return songs_json

	def get_recent_songs(self, user_id):
		one_week_ago = (datetime.today() + timedelta(weeks=-7)).strftime('%s')
		now = (datetime.today() + timedelta(weeks=-6)).strftime('%s')
		# now = datetime.today().strftime('%s')

		results = self.cassandra_session.execute("select req_time, song_id from usrsng where user_id="+str(user_id)+" and req_time > "+one_week_ago+" and req_time < "+now)
		sort_results = sorted(results, key=lambda x: x[0], reverse=True)

		send_songs = []
		for song in sort_results[0:10]:
			send_songs.append(json.loads(self.redis_session.hget("songs", str(song[1]))))
		return send_songs

	def _make_json(self, key):
		result = self.redis_session.hget(self.group, str(key))
		if not result:
			result = "{}"
		return json.loads(result)