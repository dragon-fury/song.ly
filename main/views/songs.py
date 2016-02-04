from flask import Blueprint, request, jsonify
from jinja2 import TemplateNotFound
from main.dbaccess import DBAccess
import json

songs = Blueprint('songs', __name__)

@songs.route('/songs/<song_id>')
def song(song_id):
	db = DBAccess()
	song_detail = db.get_song_detail(song_id)
	return jsonify(detail=song_detail)

@songs.route('/songs/trending')
def trending_songs():
	db = DBAccess()
	trending_songs = db.get_trending_songs()
	return jsonify(trending=trending_songs)

@songs.route('/artists/<location>')
def local_artists(location):
	db = DBAccess()
	artists = db.get_local_artists(location)
	return jsonify(detail=artists)



