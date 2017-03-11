from flask import Flask, url_for, render_template, request, redirect
from werkzeug.routing import BaseConverter
from models.models import User, db
from keys import DATABASE_URI, SLACK_OAUTH_URL
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.app_context().push()
db.init_app(app)


@app.route("/")
def hello():
   	return render_template('pages/home.html', title='home')


@app.route("/slack_auth",  methods=['GET', 'POST'])
def slack_login():
	#TODO error handling and rewrite func
	code  = request.args.get('code') 
	r = requests.get(SLACK_OAUTH_URL + code)
	data = json.loads(r.text)

	user = User(access_token=data['access_token'], slack_id=data['user']['id'], slack_name=data['user']['name'], team_id=data['team']['id'])
	if(db.session.query(User).filter_by(slack_id=data['user']['id']).scalar() is not None):
		db.session.add(user)
		db.session.commit()
		
	return redirect('/user', code=302)


@app.route("/user")
def user_page():
	return render_template('pages/user.html', title='user')


if __name__ == "__main__":
    app.run()