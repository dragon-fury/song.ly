import os, redis
from flask import Flask, render_template, send_from_directory
from cassandra.cluster import Cluster

app = Flask(__name__)

app.debug = True 

cluster = Cluster(['52.89.0.21'])
keyspace = 'usersong'
cassandra_session = cluster.connect(keyspace)

redis_session = redis.StrictRedis(host='52.35.176.202', port=6379, db=0)

from views.general import general
from views.users import users
from views.songs import songs
from views.recommendation import recommendations

app.register_blueprint(general)
app.register_blueprint(users)
app.register_blueprint(songs)
app.register_blueprint(recommendations)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'images/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



