from flask import Blueprint, render_template, abort, request, jsonify, make_response, Response, redirect
from jinja2 import TemplateNotFound
from main.dbaccess import DBAccess
import json

users = Blueprint('users', __name__)

@users.route('/users/<user_id>')
def user(user_id):
	db = DBAccess()
	user_detail = db.get_user_detail(user_id)

	return render_template("users/user_page.html", detail=user_detail)

@users.route('/user_name/<user_name>')
def username(user_name):
	db = DBAccess()
	return db.get_user_detail_from_name(user_name)
