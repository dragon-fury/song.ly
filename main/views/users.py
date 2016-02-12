from flask import Blueprint, render_template, abort, request, jsonify, make_response, Response, redirect
from jinja2 import TemplateNotFound
from main.dbaccess import DBAccess
# from kafka import KafkaProducer
import json, time

users = Blueprint('users', __name__)

@users.route('/users/<user_id>')
def user(user_id):
	db = DBAccess()
	user_detail = db.get_user_detail(user_id)

	return render_template("users/user_page.html", detail=user_detail)

@users.route('/user_name/<user_name>')
def username(user_name):
	db = DBAccess()
	user_id = db.get_user_detail_from_name(user_name)
	return str(user_id)

@users.route('/users/<user_id>/songs/<song_id>')
def user_song_request(user_id, song_id):
	# timestamp = int(time()) 
	# topic = "songreq"
	# producer = KafkaProducer(bootstrap_servers=['52.89.194.130:9092'])
	# data = str(timestamp)+","+str(user_id)+","+str(song_id)
	# producer.send(topic, data)

	db = DBAccess()
	songs = db.get_frequent_songs(song_id)
	return jsonify(frequent_songs=songs)

@users.route('/users/<user_id>/recentsongs')
def user_recent_songs(user_id):
	db = DBAccess()
	songs = db.get_recent_songs(user_id)
	return jsonify(songs=songs)
