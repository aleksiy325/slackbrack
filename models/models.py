from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    access_token = db.Column(db.String(120), unique=True)
    slack_name = db.Column(db.String(80))
    slack_id = db.Column(db.String(80), unique=True)
    team_id = db.Column(db.String(80))


    def __init__(self, access_token, slack_name, slack_id, team_id):
        self.access_token = access_token
        self.slack_name = slack_name
        self.slack_id = slack_id
        self.team_id = team_id

    def __repr__(self):
        return '<User %r>' % self.username