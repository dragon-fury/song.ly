from flask import Blueprint, render_template, request, jsonify, redirect
from jinja2 import TemplateNotFound
from main.dbaccess import DBAccess
import json

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/recommended_friends/<user_id>')
def friends(user_id):
	db = DBAccess()
	friend_list = db.get_recommended_friends(user_id)
	return jsonify(friends=friend_list)

@recommendations.route('/recommended_songs/<user_id>')
def songs(user_id):
	db = DBAccess()
	recommended_songs = db.get_recommended_songs(user_id)
	return jsonify(songs=recommended_songs)

