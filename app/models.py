from app import db
from flask import current_app


class Crawler(db.Model):
    __tablename__ = 'crawler'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True)
    tweets = db.relationship('Tweet', backref='crawler', lazy='dynamic')
    preprocess = db.relationship('Preprocess', backref='crawler', lazy='dynamic')
    postag = db.relationship('PosTag', backref='crawler', lazy='dynamic')
    penentuan_kelas = db.relationship('PenentuanKelas', backref='crawler', lazy='dynamic')
    ldapwz = db.relationship('LdaPWZ', backref='crawler', lazy='dynamic')
    grammar_story = db.relationship('GrammarStory', backref='crawler', lazy='dynamic')
    attractions = db.relationship('Attractions', backref='crawler', lazy='dynamic')

    def __repr__(self):
        return '<Crawler {}>'.format(self.timestamp)


class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    username = db.Column(db.String(50))
    created = db.Column(db.DateTime)
    text = db.Column(db.String(200))
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)
    preprocess = db.relationship('Preprocess', backref='tweet', uselist=False)
    postag = db.relationship('PosTag', backref='tweet', uselist=False)
    penentuan_kelas = db.relationship('PenentuanKelas', backref='tweet', uselist=False)

    def __repr__(self):
        return '<Tweet {}>'.format(self.username)


class Preprocess(db.Model):
    __tablename__ = 'preprocess'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<Preprocess {}>'.format(self.text)


class PosTag(db.Model):
    __tablename__ = 'postag'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<PosTag {}>'.format(self.text)


class PenentuanKelas(db.Model):
    __tablename__ = 'penentuan_kelas'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    function = db.Column(db.String(200))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<PenentuanKelas {} {}>'.format(self.content, self.function)


class LdaPWZ(db.Model):
    __tablename__ = 'ldapwz'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(200))
    topic = db.Column(db.Integer)
    pwz = db.Column(db.String(200))
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<LdaPWZ {} {} {}>'.format(self.word, self.topic, self.pwz)


class GrammarStory(db.Model):
    __tablename__ = 'grammar_story'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.Integer)
    rules = db.Column(db.String(25))
    story = db.Column(db.String(10000))
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<GrammarStory {} {}>'.format(self.topic, self.story)


class Attractions(db.Model):
    __tablename__ = 'attractions'
    id = db.Column(db.Integer, primary_key=True)
    attractions = db.Column(db.String(1000))
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'), nullable=False)

    def __repr__(self):
        return '<Attractions {}>'.format(self.attractions)
