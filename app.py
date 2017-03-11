from flask import Flask, url_for, render_template, request, redirect
from werkzeug.routing import BaseConverter
from models.models import User, db
from keys import DATABASE_URI, SLACK_OAUTH_URL, FLASK_SECRET_KEY
import requests
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import challonge

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)
challonge.set_credentials(CHALLONGE_USERNAME, CHALLONGE_API_KEY)

@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@app.route("/")
def hello():
    return render_template('pages/home.html', title='home')

@app.route("/slack_auth",  methods=['GET', 'POST'])
def slack_login():
    #TODO error handling and rewrite func

    code  = request.args.get('code') 
    r = requests.get(SLACK_OAUTH_URL + code)
    data = json.loads(r.text)

    if current_user.is_authenticated:
        return redirect('/user', code=302)

    slack_id = data['user']['id']
    user = User.query.filter_by(slack_id=slack_id).first()

    if user is None:
        user = User(access_token=data['access_token'], slack_id=slack_id, slack_name=data['user']['name'], team_id=data['team']['id'])

    user.authenticated = True
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect('/user', code=302)

@app.route("/logout")
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect('/', code=302)

@app.route("/user")
@login_required
def user_page():
    return render_template('pages/user.html', title='user')






if __name__ == "__main__":
    app.run()