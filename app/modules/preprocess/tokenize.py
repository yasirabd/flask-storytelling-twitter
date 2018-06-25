import re
import string
from nltk.tokenize import RegexpTokenizer


class Tokenize():
    def WordTokenize(self, sentence, removepunct=False, splitby='space'):
        """Tokenize sentence into words.
        Args:
            sentence (str): text of string
            stopword (list of str): list of unnecessary words
            removepunct (bool): True if want to remove punctuation
            splitby: split sentence based on
        Returns:
            list of words
        """
        if splitby.strip().lower() == 'space':
            words = re.split(r'\s', sentence)
        elif splitby.strip().lower() == 'word':
            words = re.split('(\w+)?', sentence)
        else:
            raise NotImplementedError

        if removepunct:
            remove = string.punctuation
            remove = remove.replace("-", "")
            transtab = str.maketrans('', '', remove)
            words = [w.translate(transtab).strip() for w in words]
            # remove empty char in list
            words = [w.strip().lower() for w in words if w.strip()]

        return words

    def CharTokenize(self, word):
        """Tokenize word into characters.
        Args:
            word (str): word
        Returns:
            list of characters
        """
        return list(word)
