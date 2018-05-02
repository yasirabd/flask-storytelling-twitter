from app import db
from flask import current_app
from datetime import datetime


class Crawler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tweets = db.relationship('Tweet', backref='crawler', lazy='dynamic')

    def __repr__(self):
        return '<Crawler {}>'.format(self.timestamp)


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    username = db.Column(db.String(50))
    created = db.Column(db.DateTime)
    text = db.Column(db.String(200))
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<Tweet {}>'.format(self.username)
