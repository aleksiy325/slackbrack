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
    if request.method == 'POST':
        print "slack"
    else:
        #webapp
        if not current_user.is_authenticated:
            return redirect('/', code=302)

        t = Tournament(current_user.team_id)

    return redirect('/tournament/' + str(t.challonge_id), code=302)

@app.route("/tournament/<challonge_id>",  methods=['GET'])
def tournament(challonge_id):
    tournament = Tournament.query.filter_by(challonge_id=challonge_id).first()
    data = None
    if tournament is not None:
        data = tournament.get_data()
    return render_template('pages/tournament.html', title='user', tournament=tournament, data=data)


@app.route("/jointourney", methods=['GET', 'POST'])
def join_tourney():
    if request.method == 'POST':
        #slack
        print "test"
    else:
        #webapp
        if not current_user.is_authenticated:
            return redirect('/', code=302)

        tournament = Tournament.query.filter_by(team_id=current_user.team_id).first()
        tournament.join(current_user.slack_id)

    return redirect('/tournament/' + str(tournament.challonge_id), code=302)


@app.route("/starttourney", methods=['GET', 'POST'])
def start_tourney():
    if request.method == 'POST':
        #slack
        print "test"
    else:
        #webapp
        if not current_user.is_authenticated:
            return redirect('/', code=302)
        tournament = Tournament.query.filter_by(team_id=current_user.team_id).first()
        tournament.start()

    return redirect('/tournament/' + str(tournament.challonge_id), code=302)

@app.route("/score", methods=['GET', 'POST'])
def report_match():
    if request.method == 'POST':
        #slack
        print "test"
    else:
        #webapp
        if not current_user.is_authenticated:
            return redirect('/', code=302)


    #TODO slack
    score = "1-3"
    match_id = "someid"
    match_winner = "someid"
    data = challonge.matches.update(match_id = match_id, scores_csv=score, match_winner=match_winner)


if __name__ == "__main__":
    app.run(debug=True)