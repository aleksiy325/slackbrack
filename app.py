from flask import Flask, url_for, render_template, request, redirect
from werkzeug.routing import BaseConverter
from models.models import User, Tournament, db
from keys import DATABASE_URI, SLACK_OAUTH_URL, FLASK_SECRET_KEY, CHALLONGE_USERNAME, CHALLONGE_API_KEY, SLACK_VERIFICATION_TOKEN
import requests
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import challonge
from slackclient import SlackClient
import uuid

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)
challonge.set_credentials(CHALLONGE_USERNAME, CHALLONGE_API_KEY)
sc = SlackClient(SLACK_VERIFICATION_TOKEN)

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

@app.route("/newtourney", methods=['GET', 'POST'])
def new_tourney():
    #TODO ADD SLACK
    uid = str(uuid.uuid4()).replace('-', '')
    data = challonge.tournaments.create(uid, uid)
    tournament = Tournament(data['id'])
    db.session.add(tournament)
    db.session.commit()
    return

@app.route("/jointourney", methods=['GET', 'POST'])
def join_tourney():
    #TODO ADD SLACK
    uid = str(uuid.uuid4()).replace('-', '')
    tournament = Tournament.query.all()[0]
    data = challonge.participants.create(tournament.challonge_id, uid)
    return

@app.route("/starttourney", methods=['GET', 'POST'])
def start_tourney():


    #TODO get tourney and start matches
    tournament = Tournament.query.all()[0]
    data = challonge.tournaments.start(tournament.challonge_id)
    matches = challonge.matches.index(tournament.challonge_id)
    return

@app.route("/score", methods=['GET', 'POST'])
def report_match
    #TODO slack
    score = "1-3"
    match_id = "someid"
    match_winner = "someid"
    data = challognge.matches.update(match_id = match_id, scores_csv=score, match_winner=match_winner)
    

if __name__ == "__main__":
    app.run()