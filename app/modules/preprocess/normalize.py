import re
import numpy as np

character = ['.',',',';',':','-,','...','?','!','(',')','[',']','{','}','<','>','"','/','\'','#','-','@']


class Normalize():

    def lower_text(self, tweet):
        """Change characters into lower case.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        tweet = tweet.lower()
        return tweet
        
    def remove_ascii_unicode(self, tweet):
        """Remove ASCII and Unicode.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        tweet = tweet.encode('ascii', 'ignore').decode('utf-8')
        tweet = re.sub(r'[^\x00-\x7f]',r'',tweet)
        return tweet

    def remove_repeated_char(self, tweet):
        """Convert repeated character into one character.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        for i in range(len(character)):
            char_long = 5
            while char_long >= 2:
                char = character[i]*char_long
                tweet = tweet.replace(char, character[i])
                char_long -= 1
        return tweet

    def remove_elipsis(self, tweet):
        """Remove elipsis.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        tweet = tweet.replace('...', ' ...')
        tweet = tweet.replace(' ...', '')
        return tweet

    def remove_newline(self, tweet):
        """Remove newline.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        tweet = tweet.replace('\n', ' ')
        return tweet

    def remove_url(self, tweet):
        """Remove URL link.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        tweet = re.sub(r"\s—\s", "", tweet)
        tweet = re.sub(r"http\S+", "", tweet)
        return tweet

    def remove_emoticon(self, tweet):
        """Remove emoticon.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        smileys_pattern = re.compile(r"(?:X|:|;|=)(?:-)?(?:\)|\(|O|D|P|S){1,}", re.IGNORECASE)
        return smileys_pattern.sub(r'', tweet)

    def remove_hashtag_mention(self, tweet):
        """Remove hastag and mention.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        re_hashtag_mention = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ", tweet)
        return ' '.join(re_hashtag_mention.split())

    def remove_rt_fav(self, tweet):
        """Remove RT and FAV.
        Args:
            tweet(str): tweet
        Returns:
            modified tweet
        """
        tweet = re.sub(r'^(RT|FAV)','', tweet)
        return tweet