from app import db
from flask import current_app
from flask import render_template, url_for, session, redirect, make_response, jsonify, request
from flask_googlemaps import Map
from flask_babel import _
from googleplaces import GooglePlaces
from collections import defaultdict
import pandas as pd
import time
import os
import math
from datetime import datetime
import pytz
from io import BytesIO
from app.main import bp
from app.main.forms import SearchPlaceForm, SearchTweetsForm, ChoiceObj
from app.models import Crawler, Tweet, Preprocess, PosTag, PenentuanKelas, LdaPWZ, GrammarStory, Attractions
from ..modules.crawler import TwitterCrawler
from ..modules.preprocess import Normalize, Tokenize, SymSpell
from ..modules.hmmtagger import MainTagger, Tokenization
from ..modules.lda import LdaModel
from ..modules.grammar import CFG_Informasi, CFG_Cerita
from app._helpers import flash_errors


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm()

    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets)


@bp.route('/attractions', methods=['GET', 'POST'])
def attractions():
    selectedChoices = ChoiceObj('multi_attractions', session.get('selected'))
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm(obj=selectedChoices)

    attractions, attractions_next_page, attractions_next_page2 = None, None, None
    list_attractions = ()
    GOOGLEMAPS_KEY = "AIzaSyCc3VpBAxqVIwkCvQC1ibFGFnqJbXDmxwE"
    google_places = GooglePlaces(GOOGLEMAPS_KEY)
    if form_splace.validate_on_submit():
        place_name = form_splace.place_name.data
        attractions = google_places.text_search(query=place_name+' tourist attractions',
                                                language='id')
        # if have more than 20
        if attractions.has_next_page_token:
            time.sleep(2)
            attractions_next_page = google_places.text_search(pagetoken=attractions.next_page_token)

            # if have more than 40
            if attractions_next_page.has_next_page_token:
                time.sleep(2)
                attractions_next_page2 = google_places.text_search(pagetoken=attractions_next_page.next_page_token)

        if attractions:
            la = list(list_attractions)
            for place in attractions.places:
                la.append(place.name)
            if attractions_next_page:
                for place in attractions_next_page.places:
                    la.append(place.name)
            if attractions_next_page2:
                for place in attractions_next_page2.places:
                    la.append(place.name)
            list_attractions = tuple(la)

        form_stweets.multi_attractions.choices =  [(att, att) for att in list_attractions]
        form_stweets.latitude.data = form_splace.lat.data
        form_stweets.longitude.data = form_splace.lng.data
        form_stweets.place.data = place_name
    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets)


@bp.route('/result', methods=['GET', 'POST'])
def result():
    selectedChoices = ChoiceObj('attractions', session.get('selected'))
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm(obj=selectedChoices)

    if form_stweets.validate_on_submit():
        session['selected'] = form_stweets.multi_attractions.data
        place_name = form_stweets.place.data
        latitude = form_stweets.latitude.data
        longitude = form_stweets.longitude.data
        attractions = session.get('selected')
        range_dist = form_stweets.range_dist.data
        days_before = form_stweets.days_before.data

        # CRAWLING
        twitter_crawler = TwitterCrawler(current_app)
        df_attractions = twitter_crawler.fetch_tweets_from_attractions(attractions, int(days_before), float(latitude),
                                                                       float(longitude), int(range_dist), place_name)

        # if data from crawling less than 20, return notification
        if len(df_attractions) < 20:
            return render_template('notification.html')

        # insert into crawler table
        crawler = Crawler()
        crawler.timestamp = datetime.now(pytz.timezone('Asia/Jakarta'))
        db.session.add(crawler)
        db.session.commit()

        # insert into attractions table
        attractions_lower = [x.lower() for x in attractions]
        att = Attractions()
        att.attractions = ','.join(attractions_lower)
        att.crawler_id = crawler.id
        db.session.add(att)
        db.session.commit()

        # insert into tweet table
        for _, row in df_attractions.iterrows():
            tweet = Tweet()
            tweet.user_id = row['user_id']
            tweet.username = row['username']
            tweet.created = row['created_at']
            tweet.text = row['text']
            tweet.latitude = row['latitude']
            tweet.longitude = row['longitude']
            tweet.crawler_id = crawler.id
            db.session.add(tweet)
            db.session.commit()

        # PREPROCESSING
        tweets = Tweet.query.filter_by(crawler_id=crawler.id)
        attractions = Attractions.query.filter_by(crawler_id=crawler.id)

        # change attractions into list
        list_attractions = []
        for a in attractions:
            list_attractions.append(a.attractions)

        list_attractions = ''.join(list_attractions).split(',')

        # separate text into list
        list_tweets = []
        for t in tweets:
            id_tweet = [t.id, t.text]
            list_tweets.append(id_tweet)

        # define
        normalizer = Normalize()
        tokenizer = Tokenize()
        symspell = SymSpell(max_dictionary_edit_distance=3)
        SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "..\data", "corpus_complete_model.json")
        symspell.load_complete_model_from_json(json_url, encoding="ISO-8859-1")

        # do preprocess
        result = []
        for tweet in list_tweets:
            id, text = tweet[0], tweet[1]

            # normalize
            tweet_norm = normalizer.remove_ascii_unicode(text)
            tweet_norm = normalizer.remove_rt_fav(tweet_norm)
            tweet_norm = normalizer.lower_text(tweet_norm)
            tweet_norm = normalizer.remove_newline(tweet_norm)
            tweet_norm = normalizer.remove_url(tweet_norm)
            tweet_norm = normalizer.remove_emoticon(tweet_norm)
            tweet_norm = normalizer.remove_hashtag_mention(tweet_norm)
            tweet_norm = normalizer.remove_punctuation(tweet_norm)

            # tokenize
            tweet_tok = tokenizer.WordTokenize(tweet_norm, removepunct=True)

            # spell correction
            temp = []
            for token in tweet_tok:
                suggestion = symspell.lookup(phrase=token, verbosity=1, max_edit_distance=3)

                # option if there is no suggestion
                if len(suggestion) > 0:
                    get_suggestion = str(suggestion[0]).split(':')[0]
                    temp.append(get_suggestion)
                else:
                    temp.append(token)
            tweet_prepared = ' '.join(temp)

            # join attraction with strip
            tweet_prepared = normalizer.join_attraction(tweet_prepared, list_attractions)

            id_tweet_prepared = [id, tweet_prepared]
            result.append(id_tweet_prepared)

        # insert into table preprocess
        for res in result:
            id, text = res[0], res[1]

            tb_preprocess = Preprocess()
            tb_preprocess.text = text
            tb_preprocess.tweet_id = id
            tb_preprocess.crawler_id = crawler.id
            db.session.add(tb_preprocess)
            db.session.commit()

        # POS TAGGING
        tweets_preprocessed = Preprocess.query.filter_by(crawler_id=crawler.id)

        # get text from table Preprocess
        list_tweets = []
        for t in tweets_preprocessed:
            tid_tweet = [t.tweet_id, t.text]
            list_tweets.append(tid_tweet)

        # path
        SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
        lexicon_url = os.path.join(SITE_ROOT, "..\data", "Lexicon.trn")
        ngram_url = os.path.join(SITE_ROOT, "..\data", "Ngram.trn")

        # initialize
        tagger = MainTagger(lexicon_url, ngram_url, 0, 3, 3, 0, 0, False, 0.2, 0, 500.0, 1)
        tokenize = Tokenization()

        # do pos tagging
        result = []
        for tweet in list_tweets:
            tweet_id, text = tweet[0], tweet[1]

            if len(text) == 0:
                tid_text = [tweet_id, text]
                result.append(tid_text)
            else:
                out = tokenize.sentence_extraction(tokenize.cleaning(text))
                join_word = []
                for o in out:
                    strtag = " ".join(tokenize.tokenisasi_kalimat(o)).strip()
                    join_word += [" ".join(tagger.taggingStr(strtag))]
                tid_text = [tweet_id, join_word]
                result.append(tid_text)

        # insert into table preprocess
        for tweet in result:
            tweet_id, text = tweet[0], tweet[1]
            tweet_str = ''.join(text)

            tb_postag = PosTag()
            tb_postag.text = tweet_str
            tb_postag.tweet_id = tweet_id
            tb_postag.crawler_id = crawler.id
            db.session.add(tb_postag)
            db.session.commit()

        # PENENTUAN KELAS
        Ccon = ['JJ', 'NN','NNP', 'NNG', 'VBI', 'VBT']
        Cfunc = ['OP', 'CP', 'GM', ';', ':', '"', '.',
                 ',', '-', '...', 'RB', 'IN', 'MD', 'CC',
                 'SC', 'DT', 'UH', 'CDO', 'CDC', 'CDP', 'CDI',
                 'PRP', 'WP', 'PRN', 'PRL', 'NEG', 'SYM', 'RP', 'FW']
        tweets_tagged = PosTag.query.filter_by(crawler_id=crawler.id)

        # get text from table PostTag
        list_tweets = []
        for t in tweets_tagged:
            tid_tweet = [t.tweet_id, t.text]
            list_tweets.append(tid_tweet)

        # do penentuan kelas
        result = []
        for tweet in list_tweets:
            tweet_id, text = tweet[0], tweet[1]

            if len(text) > 0:
                text_split = text.split(' ')

                doc_complete = {"con": [], "func": []}
                con = []
                func = []

                for word in text_split:
                    w = word.split('/', 1)[0]
                    tag = word.split('/', 1)[1]
                    if tag in Ccon:
                        con.append(word)
                    elif tag in Cfunc:
                        func.append(word)
                doc_complete["con"].append(' '.join(con))
                doc_complete["func"].append(' '.join(func))
            else:
                doc_complete["con"].append(text)
                doc_complete["func"].append(text)

            result.append([tweet_id, doc_complete])

        # insert into table penentuan kelas
        for tweet in result:
            tweet_id, text = tweet[0], tweet[1]
            content, function = ''.join(text["con"]), ''.join(text["func"])

            tb_penentuan_kelas = PenentuanKelas()
            tb_penentuan_kelas.content = content
            tb_penentuan_kelas.function = function
            tb_penentuan_kelas.tweet_id = tweet_id
            tb_penentuan_kelas.crawler_id = crawler.id
            db.session.add(tb_penentuan_kelas)
            db.session.commit()

        # LDA
        tweets_penentuan_kelas = PenentuanKelas.query.filter_by(crawler_id=crawler.id)

        # get tweets content
        tweets_content_tagged = []
        for tweet in tweets_penentuan_kelas:
            tweets_content_tagged.append(tweet.content)

        # separate word and tag
        documents = []
        for tweet in tweets_content_tagged:
            tweet_split = tweet.split(' ')
            temp = []
            for word in tweet_split:
                w = word.split("/", 1)[0]
                temp.append(w)
            documents.append(temp)

        # do process lda
        lda = LdaModel(documents, int(4), float(0.001), float(0.001), int(1000))
        result = lda.get_topic_word_pwz(tweets_content_tagged)

        # insert into table ldapwz
        for r in result:
            topic, word, pwz = r[0], r[1], r[2]

            tb_ldapwz = LdaPWZ()
            tb_ldapwz.topic = topic
            tb_ldapwz.word = word
            tb_ldapwz.pwz = pwz
            tb_ldapwz.crawler_id = crawler.id
            db.session.add(tb_ldapwz)
            db.session.commit()

        # GRAMMAR STORY
        ldapwz = LdaPWZ.query.filter_by(crawler_id=crawler.id)

        # get topic with words in dictionary
        dict_ldapwz = defaultdict(list)
        for data in ldapwz:
            dict_ldapwz[data.topic].append([data.word, data.pwz])

        # initialize
        cfg_informasi = CFG_Informasi()
        cfg_cerita = CFG_Cerita()

        # create sentence for story
        dict_story_informasi = cfg_informasi.create_sentences_from_data(dict(dict_ldapwz))
        dict_story_cerita = cfg_cerita.create_sentences_from_data(dict(dict_ldapwz))

        # join into dict_story
        dict_story = defaultdict(list)
        for d in (dict_story_informasi, dict_story_cerita):
            for key, value in d.items():
                dict_story[key].append('. '.join(i.capitalize() for i in value))

        # insert into table GrammarStory
        for topic, stories in dict_story.items():
            # insert informasi
            tb_grammar_story = GrammarStory()
            tb_grammar_story.topic = topic
            tb_grammar_story.rules = 'informasi'
            tb_grammar_story.story = stories[0]
            tb_grammar_story.crawler_id = crawler.id
            db.session.add(tb_grammar_story)
            db.session.commit()

            # insert cerita
            tb_grammar_story = GrammarStory()
            tb_grammar_story.topic = topic
            tb_grammar_story.rules = 'cerita'
            tb_grammar_story.story = stories[1]
            tb_grammar_story.crawler_id = crawler.id
            db.session.add(tb_grammar_story)
            db.session.commit()

    c = Crawler.query.order_by(Crawler.id.desc()).all()

    return render_template("stories.html", crawler=c, form_stweets=form_stweets)


@bp.route('/dump', methods=['GET', 'POST'])
def dump():
    return render_template('dump.html')


# @bp.route('/process', methods=['GET', 'POST'])
# def process():
#     selectedChoices = ChoiceObj('attractions', session.get('selected'))
#     form_splace = SearchPlaceForm()
#     form_stweets = SearchTweetsForm(obj=selectedChoices)
#     input_crawling = {}
#
#     if form_stweets.validate_on_submit():
#         session['selected'] = form_stweets.multi_attractions.data
#         place_name = form_stweets.place.data
#         latitude = form_stweets.latitude.data
#         longitude = form_stweets.longitude.data
#         attractions = session.get('selected')
#         range_dist = form_stweets.range_dist.data
#         days_before = form_stweets.days_before.data
#
#         input_crawling = {'place_name': place_name,
#                           'latitude': latitude,
#                           'longitude': longitude,
#                           'attractions': attractions,
#                           'range_dist': range_dist,
#                           'days_before': days_before}
#
#     return render_template('process.html', form_stweets=form_stweets, input_crawling=input_crawling)


# @bp.route('/process/crawl', methods=['GET', 'POST'])
# def crawl():
#     place_name = request.form.get('place_name')
#     latitude = request.form.get('latitude')
#     longitude = request.form.get('longitude')
#     attractions = request.form.getlist('attractions[]')
#     range_dist = request.form.get('range_dist')
#     days_before = request.form.get('days_before')
#
#     twitter_crawler = TwitterCrawler(current_app)
#     df_attractions = twitter_crawler.fetch_tweets_from_attractions(attractions, int(days_before), float(latitude),
#                                                                    float(longitude), int(range_dist), place_name)
#
#     # insert into crawler table
#     crawler = Crawler()
#     crawler.timestamp = datetime.utcnow()
#     db.session.add(crawler)
#     db.session.commit()
#
#     # insert into attractions table
#     attractions_lower = [x.lower() for x in attractions]
#     att = Attractions()
#     att.attractions = ','.join(attractions_lower)
#     att.crawler_id = crawler.id
#     db.session.add(att)
#     db.session.commit()
#
#     # insert into tweet table
#     for _, row in df_attractions.iterrows():
#         tweet = Tweet()
#         tweet.user_id = row['user_id']
#         tweet.username = row['username']
#         tweet.created = row['created_at']
#         tweet.text = row['text']
#         tweet.latitude = row['latitude']
#         tweet.longitude = row['longitude']
#         tweet.crawler_id = crawler.id
#         db.session.add(tweet)
#         db.session.commit()
#
#     return jsonify(status_crawling="success")
#
#
# @bp.route('/process/preprocess', methods=['GET', 'POST'])
# def preprocess():
#     latest_crawler_id = (Crawler.query.order_by(Crawler.id.desc()).first()).id
#     tweets = Tweet.query.filter_by(crawler_id=latest_crawler_id)
#     attractions = Attractions.query.filter_by(crawler_id=latest_crawler_id)
#
#     # change attractions into list
#     list_attractions = []
#     for a in attractions:
#         list_attractions.append(a.attractions)
#
#     list_attractions = ''.join(list_attractions).split(',')
#
#     # separate text into list
#     list_tweets = []
#     for t in tweets:
#         id_tweet = [t.id, t.text]
#         list_tweets.append(id_tweet)
#
#     # define
#     normalizer = Normalize()
#     tokenizer = Tokenize()
#     symspell = SymSpell(max_dictionary_edit_distance=3)
#     SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
#     json_url = os.path.join(SITE_ROOT, "..\data", "corpus_complete_model.json")
#     symspell.load_complete_model_from_json(json_url, encoding="ISO-8859-1")
#
#     # do preprocess
#     result = []
#     for tweet in list_tweets:
#         id, text = tweet[0], tweet[1]
#
#         # normalize
#         tweet_norm = normalizer.remove_ascii_unicode(text)
#         tweet_norm = normalizer.remove_rt_fav(tweet_norm)
#         tweet_norm = normalizer.lower_text(tweet_norm)
#         tweet_norm = normalizer.remove_newline(tweet_norm)
#         tweet_norm = normalizer.remove_url(tweet_norm)
#         tweet_norm = normalizer.remove_emoticon(tweet_norm)
#         tweet_norm = normalizer.remove_hashtag_mention(tweet_norm)
#         tweet_norm = normalizer.remove_punctuation(tweet_norm)
#
#         # tokenize
#         tweet_tok = tokenizer.WordTokenize(tweet_norm, removepunct=True)
#
#         # spell correction
#         temp = []
#         for token in tweet_tok:
#             suggestion = symspell.lookup(phrase=token, verbosity=1, max_edit_distance=3)
#
#             # option if there is no suggestion
#             if len(suggestion) > 0:
#                 get_suggestion = str(suggestion[0]).split(':')[0]
#                 temp.append(get_suggestion)
#             else:
#                 temp.append(token)
#         tweet_prepared = ' '.join(temp)
#
#         # join attraction with strip
#         tweet_prepared = normalizer.join_attraction(tweet_prepared, list_attractions)
#
#         id_tweet_prepared = [id, tweet_prepared]
#         result.append(id_tweet_prepared)
#
#     # insert into table preprocess
#     for res in result:
#         id, text = res[0], res[1]
#
#         tb_preprocess = Preprocess()
#         tb_preprocess.text = text
#         tb_preprocess.tweet_id = id
#         tb_preprocess.crawler_id = latest_crawler_id
#         db.session.add(tb_preprocess)
#         db.session.commit()
#
#     return jsonify(status_preprocessing="success")
#
#
# @bp.route('/process/pos_tagging', methods=['GET', 'POST'])
# def pos_tagging():
#     latest_crawler_id = (Crawler.query.order_by(Crawler.id.desc()).first()).id
#     tweets_preprocessed = Preprocess.query.filter_by(crawler_id=latest_crawler_id)
#
#     # get text from table Preprocess
#     list_tweets = []
#     for t in tweets_preprocessed:
#         tid_tweet = [t.tweet_id, t.text]
#         list_tweets.append(tid_tweet)
#
#     # path
#     SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
#     lexicon_url = os.path.join(SITE_ROOT, "..\data", "Lexicon.trn")
#     ngram_url = os.path.join(SITE_ROOT, "..\data", "Ngram.trn")
#
#     # initialize
#     tagger = MainTagger(lexicon_url, ngram_url, 0, 3, 3, 0, 0, False, 0.2, 0, 500.0, 1)
#     tokenize = Tokenization()
#
#     # do pos tagging
#     result = []
#     for tweet in list_tweets:
#         tweet_id, text = tweet[0], tweet[1]
#
#         if len(text) == 0:
#             tid_text = [tweet_id, text]
#             result.append(tid_text)
#         else:
#             out = tokenize.sentence_extraction(tokenize.cleaning(text))
#             join_word = []
#             for o in out:
#                 strtag = " ".join(tokenize.tokenisasi_kalimat(o)).strip()
#                 join_word += [" ".join(tagger.taggingStr(strtag))]
#             tid_text = [tweet_id, join_word]
#             result.append(tid_text)
#
#     # insert into table preprocess
#     for tweet in result:
#         tweet_id, text = tweet[0], tweet[1]
#         tweet_str = ''.join(text)
#
#         tb_postag = PosTag()
#         tb_postag.text = tweet_str
#         tb_postag.tweet_id = tweet_id
#         tb_postag.crawler_id = latest_crawler_id
#         db.session.add(tb_postag)
#         db.session.commit()
#
#     return jsonify(status_pos_tagging="success")
#
#
# @bp.route('/process/penentuan_kelas', methods=['GET', 'POST'])
# def penentuan_kelas():
#     Ccon = ['JJ', 'NN','NNP', 'NNG', 'VBI', 'VBT']
#     Cfunc = ['OP', 'CP', 'GM', ';', ':', '"', '.',
#              ',', '-', '...', 'RB', 'IN', 'MD', 'CC',
#              'SC', 'DT', 'UH', 'CDO', 'CDC', 'CDP', 'CDI',
#              'PRP', 'WP', 'PRN', 'PRL', 'NEG', 'SYM', 'RP', 'FW']
#
#     latest_crawler_id = (Crawler.query.order_by(Crawler.id.desc()).first()).id
#     tweets_tagged = PosTag.query.filter_by(crawler_id=latest_crawler_id)
#
#     # get text from table PostTag
#     list_tweets = []
#     for t in tweets_tagged:
#         tid_tweet = [t.tweet_id, t.text]
#         list_tweets.append(tid_tweet)
#
#     # do penentuan kelas
#     result = []
#     for tweet in list_tweets:
#         tweet_id, text = tweet[0], tweet[1]
#
#         if len(text) > 0:
#             text_split = text.split(' ')
#
#             doc_complete = {"con": [], "func": []}
#             con = []
#             func = []
#
#             for word in text_split:
#                 w = word.split('/', 1)[0]
#                 tag = word.split('/', 1)[1]
#                 if tag in Ccon:
#                     con.append(word)
#                 elif tag in Cfunc:
#                     func.append(word)
#             doc_complete["con"].append(' '.join(con))
#             doc_complete["func"].append(' '.join(func))
#         else:
#             doc_complete["con"].append(text)
#             doc_complete["func"].append(text)
#
#         result.append([tweet_id, doc_complete])
#
#     # insert into table penentuan kelas
#     for tweet in result:
#         tweet_id, text = tweet[0], tweet[1]
#         content, function = ''.join(text["con"]), ''.join(text["func"])
#
#         tb_penentuan_kelas = PenentuanKelas()
#         tb_penentuan_kelas.content = content
#         tb_penentuan_kelas.function = function
#         tb_penentuan_kelas.tweet_id = tweet_id
#         tb_penentuan_kelas.crawler_id = latest_crawler_id
#         db.session.add(tb_penentuan_kelas)
#         db.session.commit()
#
#     return jsonify(status_penentuan_kelas="success")
#
#
# @bp.route('/process/lda/generate_topik', methods=['GET', 'POST'])
# def generate_topik():
#     latest_crawler_id = (Crawler.query.order_by(Crawler.id.desc()).first()).id
#     tweets_penentuan_kelas = PenentuanKelas.query.filter_by(crawler_id=latest_crawler_id)
#
#     # get tweets content
#     list_tweets = []
#     for tweet in tweets_penentuan_kelas:
#         list_tweets.append(tweet.content)
#
#     # only get text not tag
#     documents = []
#     for tweet in list_tweets:
#         tweet_split = tweet.split(' ')
#
#         temp = []
#         for word in tweet_split:
#             w = word.split("/", 1)[0]
#             temp.append(w)
#         documents.append(temp)
#
#     # calculate distinct words
#     distinct_words = set(word for document in documents for word in document)
#     W = len(distinct_words)
#
#     # calculate number of topic
#     jumlah_topik = math.ceil(1 + 3.222 * math.log10(W))
#
#     return jsonify(num_topics=jumlah_topik)
#
#
# @bp.route('/process/lda', methods=['GET', 'POST'])
# def lda():
#     latest_crawler_id = (Crawler.query.order_by(Crawler.id.desc()).first()).id
#     tweets_penentuan_kelas = PenentuanKelas.query.filter_by(crawler_id=latest_crawler_id)
#
#     # get tweets content
#     tweets_content_tagged = []
#     for tweet in tweets_penentuan_kelas:
#         tweets_content_tagged.append(tweet.content)
#
#     # separate word and tag
#     documents = []
#     for tweet in tweets_content_tagged:
#         tweet_split = tweet.split(' ')
#         temp = []
#         for word in tweet_split:
#             w = word.split("/", 1)[0]
#             temp.append(w)
#         documents.append(temp)
#
#     num_topics = request.form['num_topics']
#     alpha = request.form['alpha']
#     beta = request.form['beta']
#     iterations = request.form['iterations']
#
#     if num_topics and alpha and beta and iterations:
#         lda = LdaModel(documents, int(num_topics), float(alpha), float(beta), int(iterations))
#         result = lda.get_topic_word_pwz(tweets_content_tagged)
#
#         # insert into table ldapwz
#         for r in result:
#             topic, word, pwz = r[0], r[1], r[2]
#
#             tb_ldapwz = LdaPWZ()
#             tb_ldapwz.topic = topic
#             tb_ldapwz.word = word
#             tb_ldapwz.pwz = pwz
#             tb_ldapwz.crawler_id = latest_crawler_id
#             db.session.add(tb_ldapwz)
#             db.session.commit()
#
#         return jsonify(status_lda="success")
#     else:
#         return jsonify(status_lda="failed")
#
#
# @bp.route('/process/grammar', methods=['GET', 'POST'])
# def grammar():
#     latest_crawler_id = (Crawler.query.order_by(Crawler.id.desc()).first()).id
#     ldapwz = LdaPWZ.query.filter_by(crawler_id=latest_crawler_id)
#
#     # get topic with words in dictionary
#     dict_ldapwz = defaultdict(list)
#     for data in ldapwz:
#         dict_ldapwz[data.topic].append([data.word, data.pwz])
#
#     # initialize
#     cfg_informasi = CFG_Informasi()
#     cfg_cerita = CFG_Cerita()
#
#     # create sentence for story
#     dict_story_informasi = cfg_informasi.create_sentences_from_data(dict(dict_ldapwz))
#     dict_story_cerita = cfg_cerita.create_sentences_from_data(dict(dict_ldapwz))
#
#     # join into dict_story
#     dict_story = defaultdict(list)
#     for d in (dict_story_informasi, dict_story_cerita):
#         for key, value in d.items():
#             dict_story[key].append('. '.join(i.capitalize() for i in value))
#
#     # insert into table GrammarStory
#     for topic, stories in dict_story.items():
#         # insert informasi
#         tb_grammar_story = GrammarStory()
#         tb_grammar_story.topic = topic
#         tb_grammar_story.rules = 'informasi'
#         tb_grammar_story.story = stories[0]
#         tb_grammar_story.crawler_id = latest_crawler_id
#         db.session.add(tb_grammar_story)
#         db.session.commit()
#
#         # insert cerita
#         tb_grammar_story = GrammarStory()
#         tb_grammar_story.topic = topic
#         tb_grammar_story.rules = 'cerita'
#         tb_grammar_story.story = stories[1]
#         tb_grammar_story.crawler_id = latest_crawler_id
#         db.session.add(tb_grammar_story)
#         db.session.commit()
#
#     return jsonify(status_grammar="success")


@bp.route('/stories', methods=['GET', 'POST'])
def stories():
    crawler = Crawler.query.order_by(Crawler.id.desc()).all()
    return render_template("stories.html", crawler=crawler)


@bp.route('/stories/<int:id>', methods=['GET', 'POST'])
def story(id):
    grammar_story = GrammarStory.query.filter_by(crawler_id=id)

    # store data in dictionary
    dict_story = defaultdict(list)
    for data in grammar_story:
        dict_story[data.topic].append([data.rules, data.story])

    return render_template("story.html", crawler_id=id, dict_story=dict(dict_story))


# @bp.route('/stories/<int:id>/get_story', methods=['GET', 'POST'])
# def get_story(id):
#     jsonData = request.get_json()
#     selected_topic = jsonData['selected_topic']
#     grammar_story = GrammarStory.query.filter_by(crawler_id=id, topic=selected_topic)
#
#     result = []
#     for data in grammar_story:
#         result.append(data.sentence)
#
#     return jsonify(grammar_story='. '.join(i.capitalize() for i in result))


@bp.route('/stories/<int:id>/details/crawling', methods=['GET', 'POST'])
def get_crawling(id):
    tweets = Tweet.query.filter_by(crawler_id=id)

    return render_template("details_crawling.html", crawler_id=id, tweets=tweets)


@bp.route('/stories/<int:id>/details/preprocessing', methods=['GET', 'POST'])
def get_preprocessing(id):
    preprocess = Preprocess.query.filter_by(crawler_id=id)

    return render_template("details_preprocessing.html", crawler_id=id, preprocess=preprocess)


@bp.route('/stories/<int:id>/details/postag', methods=['GET', 'POST'])
def get_postag(id):
    postag = PosTag.query.filter_by(crawler_id=id)

    return render_template("details_postag.html", crawler_id=id, postag=postag)


@bp.route('/stories/<int:id>/details/kelas', methods=['GET', 'POST'])
def get_kelas(id):
    kelas = PenentuanKelas.query.filter_by(crawler_id=id)

    return render_template("details_kelas.html", crawler_id=id, kelas=kelas)


@bp.route('/stories/<int:id>/details/lda', methods=['GET', 'POST'])
def get_lda(id):
    lda = LdaPWZ.query.filter_by(crawler_id=id)

    return render_template("details_lda.html", crawler_id=id, lda=lda)


@bp.route('/stories/<int:id>/details/story', methods=['GET', 'POST'])
def get_grammar_story(id):
    story = GrammarStory.query.filter_by(crawler_id=id)

    return render_template("details_story.html", crawler_id=id, story=story)
