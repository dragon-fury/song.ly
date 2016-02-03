from flask import Blueprint, render_template, request, jsonify, redirect
from jinja2 import TemplateNotFound
from main.dbaccess import DBAccess
import json

general = Blueprint('general', __name__)

@general.route('/', methods=['GET', 'POST'])
def index_login():
	if request.method == 'POST':
		user_id = request.form["userid"]
		return redirect("/user/"+user_id)
	return render_template("general/index.html")

