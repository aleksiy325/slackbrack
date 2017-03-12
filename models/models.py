from flask_sqlalchemy import SQLAlchemy
import uuid
import challonge
from keys import CHALLONGE_API_KEY, CHALLONGE_USERNAME

db = SQLAlchemy()
challonge.set_credentials(CHALLONGE_USERNAME, CHALLONGE_API_KEY)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    access_token = db.Column(db.String(120), unique=True)
    slack_name = db.Column(db.String(80))
    slack_id = db.Column(db.String(80), unique=True)
    team_id = db.Column(db.String(80))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, access_token, slack_name, slack_id, team_id):
        self.access_token = access_token
        self.slack_name = slack_name
        self.slack_id = slack_id
        self.team_id = team_id
        self.authenticated = False

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % self.slack_name


class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True)
    challonge_id = db.Column(db.Integer, unique=True)
    active = db.Column(db.Boolean, default=True)
    team_id = db.Column(db.String(80))
    uid = db.Column(db.String(80))


    def __init__(self, team_id):
        uid = str(uuid.uuid4()).replace('-', '')
        data = challonge.tournaments.create(uid, uid)
        self.challonge_id = data['id'], 
        self.team_id = team_id
        self.uid = uid
        db.session.add(self)
        db.session.commit()

    def get_data(self):
        return challonge.tournaments.show(self.challonge_id)

    def join(self, slack_id):
        return challonge.participants.create(self.challonge_id, slack_id)

    def start(self):
        return challonge.tournaments.start(self.challonge_id)
 
class  Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80))
    challonge_id = db.Column(db.Integer, default=None)

    def __init__(self, team_id):
        self.team_id = team_id
