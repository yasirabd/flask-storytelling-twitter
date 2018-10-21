import string
import tweepy
import time
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

PLACES = ['Klenteng', 'Kawasan']
SEPARATOR = [',', '-', '|']

class TwitterCrawler:
    '''module for twitter crawling'''

    def __init__(self, app):
        self.__ACCESS_TOKEN = app.config['TWITTER_ACCESS_TOKEN']
        self.__ACCESS_SECRET = app.config['TWITTER_ACCESS_SECRET']
        self.__CONSUMER_KEY = app.config['TWITTER_CONSUMER_KEY']
        self.__CONSUMER_SECRET = app.config['TWITTER_CONSUMER_SECRET']
        self.__auth = tweepy.OAuthHandler(self.__CONSUMER_KEY, self.__CONSUMER_SECRET)
        self.__auth.set_access_token(self.__ACCESS_TOKEN, self.__ACCESS_SECRET)
        self.__api = tweepy.API(self.__auth, wait_on_rate_limit=True)


    def fetch_tweets_from_attractions(self, attractions, days_before, latitude, longitude, range_dist, place_name):
        df_attractions = pd.DataFrame({'user_id': [], 'username': [], 'created_at': [], 'latitude': [], 'longitude': [], 'text': []})
        for att in attractions:
            query = self.generate_query(att, place_name)
            df_tweet = self.fetch_tweets(query, days_before, latitude, longitude, range_dist)
            df_attractions = df_attractions.append(df_tweet, ignore_index=True)

        return df_attractions


    def fetch_tweets(self, query, days_before, latitude, longitude, range_dist):
        now = datetime.today()
        date_before = now - timedelta(days=days_before)
        df_tweet = pd.DataFrame({'user_id': [], 'username': [], 'created_at': [], 'latitude': [], 'longitude': [], 'text': []})

        c = tweepy.Cursor(self.__api.search, q=query, tweet_mode='extended',
                          geocode = "%f,%f,%dkm" % (latitude, longitude, range_dist)).items()
        while True:
            try:
                tweet = c.next()
                if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
                    user_id = tweet.user.id
                    username = tweet.user.screen_name
                    created = tweet.created_at
                    text = tweet.full_text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')

                    # get tweets maximum before x days
                    if tweet.created_at < date_before:
                        break
                    if tweet.geo:
                        latitude = tweet.geo['coordinates'][0]
                        longitude = tweet.geo['coordinates'][1]
                        df_tweet = df_tweet.append({'user_id': user_id, 'username': username, 'created_at': created,
                                                    'latitude': latitude, 'longitude': longitude, 'text': text}, ignore_index=True)
                    else:
                        df_tweet = df_tweet.append({'user_id': user_id, 'username': username, 'created_at': created,
                                                    'latitude': '', 'longitude': '', 'text': text}, ignore_index=True)
            except tweepy.TweepError as e:
                print(e.reason)
                time.sleep(15 * 60)
                continue
            except StopIteration:
                break
        return df_tweet


    def generate_query(self, text, place_name):
        query = []

        text = string.capwords(text) # capitalize the first letter of each word

        # if word contains SEPARATOR then remove after it
        for sep in SEPARATOR:
            if sep in text:
                text = text.split(sep, 1)[0]
        query.append(text)

        # split text into words list
        text = text.split(' ')
        query.append(self.change_into_hashtags(text))

        # if word contains in PLACES, remove it
        for word in text:
            if word in PLACES:
                text.remove(word)
                query.append(' '.join(text))
                query.append(self.change_into_hashtags(text))

        # if word contains place name, remove it
        for word in text:
            if word.lower() == place_name.lower():
                text.remove(word)
                query.append(' '.join(text))
                query.append(self.change_into_hashtags(text))

        return self.makes_twitter_query(query)


    def makes_twitter_query(self, query):
        for _ in query:
            query[query.index(_)] = '"'+ _ + '"'
        return ' OR '.join(query) + ' -filter:retweet'


    def change_into_hashtags(self, text):
        return '#'+''.join(text).lower()
