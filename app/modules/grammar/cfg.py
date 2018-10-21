from collections import OrderedDict, defaultdict
import re, random
import numpy.random as nr
import numpy as np


class CFG_Informasi():
    """
        Implementation Context-free Grammar
    """
    def __init__(self):
        self.NP = ['_NN', '_NNG', '_NNP']
        self.VP = ['_VBT _NN', '_VBT _NN _NN', '_VBT _NN _CC _NN', '_VBT _PP', '_VBT _NN _PP', '_VBT _NN _SC _JJ',
                   '_VBI _PP', '_VBI _JJ', '_SC _JJ _VBI _NN',
                   '_PP _NN', '_PP', '_SC _JJ']

    def create_sentences_from_data(self, dict_data):
        """Create dictionary with key: topic and value: list of sentences
        Args:
            dict_data(dict): dictionary data with 'key': 'topic' and 'value': 'list of words'
        Returns:
            dictionary data with 'key': 'topic' and 'value': 'list of sentences'
        """
        result = {}
        np.random.seed(10)
        for topic, words in dict_data.items():
            sentence = []
            grammar, dict_pwz_by_tag = self.create_grammar(words)
            for s in range(10):
                sentence.append(' '.join(self.generate_sentence(grammar, dict_pwz_by_tag)))
            result = self.merge_two_dicts(result, {topic: sentence})
        return result

    def is_terminal(self, token):
        """Check whether token is terminal
        Args:
            token(str): token from production rules grammar
        Returns:
            True if token is a terminal, and False otherwise
        """
        return token[0] != "_"

    def expand(self, grammar, tokens, dict_pwz_by_tag):
        """Recursive to replace tokens with random words
        Args:
            grammar(dict): dictionary of grammar production rules
            tokens(str): token in grammar production rules
            dict_pwz_by_tag(dict): dictionary of pwz by tag
        Returns:
            token with random word
        """
        for i, token in enumerate(tokens):

            # skip over terminals
            if self.is_terminal(token): continue

            # if we get here, we found a non-terminal token
            # so we need to choose a replacement at random
            replacement = nr.choice(grammar[token])

            if replacement == '_NN':
                dict_pwz_by_tag['_NN'] = [float(i) for i in dict_pwz_by_tag['_NN']]
                weight = [x/sum(dict_pwz_by_tag['_NN']) for x in dict_pwz_by_tag['_NN']]
                replacement = nr.choice(grammar['_NN'], p=weight)

            if self.is_terminal(replacement):
                tokens[i] = replacement
            else:
                tokens = tokens[:i] + replacement.split() + tokens[(i+1):]

            # now call expand on the new list of tokens
            return self.expand(grammar, tokens, dict_pwz_by_tag)

        # if we get here we had all terminals and are done
        return tokens

    def generate_sentence(self, grammar, dict_pwz_by_tag):
        """Generate sentence randomly from token '_S'
        Args:
            grammar(dict): dictionary of grammar production rules
            dict_pwz_by_tag(dict): dictionary of pwz by tag
        Returns:
            sentence(list): list of words randomly
        """
        return self.expand(grammar, ["_S"], dict_pwz_by_tag)

    def merge_two_dicts(self, x, y):
        """Merge two dictionaries into a new dictionary as a shallow copy
        Args:
            x(dict): dictionary 1
            y(dict): dictionary 2
        Returns:
            z(dict): merge of x and y
        """
        z = x.copy()
        z.update(y)
        return z

    def create_grammar(self, dict_words_by_topic):
        """Create grammar production rules
        Args:
            dict_words_by_topic(dict): dictionary of topic that contains words
        Returns:
            grammar(dict): grammar production rules
        """
        grammar = {}

        dict_words_pwz_by_tag = self.organize_words_by_tag(dict_words_by_topic)
        list_tag = self.get_list_tag(dict_words_pwz_by_tag)
        base_grammar = self.generate_base_grammar(list_tag)
        dict_word_by_tag, dict_pwz_by_tag = self.split_word_pwz(dict_words_pwz_by_tag)
        words_grammar = self.generate_words_grammar(dict_word_by_tag)

        for r in [base_grammar, words_grammar]:
            grammar.update(r)
        return grammar, dict_pwz_by_tag

    def organize_words_by_tag(self, list_words):
        """Create dictionary of 'key': 'tag' and 'value': 'a list of words'
        Args:
            list_words(dict): a list words with tag
        Returns:
            dict_words_by_tag(dict): dictionary of 'key': 'tag' and 'value': 'a list of words'
        """
        result = defaultdict(list)

        for s in list_words:
            word, pwz = s[0], s[1]

            wrd = word.split('/')[0]
            tag = word.split('/')[1]
            result['_'+tag].append([wrd, pwz])
        return dict(result)

    def split_word_pwz(self, dict_words_pwz_by_tag):
        """Split word and pwz.
        Args:
            dict_words_pwz_by_tag(dict): dictionary word and pwz by tag
        Returns:
            dict_word_by_tag: dictionary word by tag
            dict_pwz_by_tag: dictionary pwz by tag
        """
        dict_word_by_tag = defaultdict(list)
        dict_pwz_by_tag = defaultdict(list)

        for key, values in dict_words_pwz_by_tag.items():
            for data in values:
                word, pwz = data[0], data[1]
                dict_word_by_tag[key].append(word)
                dict_pwz_by_tag[key].append(pwz)
        return dict(dict_word_by_tag), dict(dict_pwz_by_tag)

    def get_list_tag(self, dict_words_by_tag):
        """Get tags in dictionary of 'key': 'tag' and 'value': 'a list of words'
        Args:
            dict_words_by_tag(dict): dictionary of 'key': 'tag and 'value': 'a list of words'
        Returns:
            list_tag(list): a list of tags
        """
        result = []
        for key in dict_words_by_tag:
            result.append(key)
        return result

    def generate_base_grammar(self, list_tag):
        """Generate base grammar (only terminal)
        Args:
            list_tag(list): a list of tags
        Returns:
            base_grammar(dict): base grammar production rules
        """
        result = {}

        if '_VBT' not in list_tag:
            list_tag.append('_VBT')

        if '_VBI' not in list_tag:
            list_tag.append('_VBI')

        S = {"_S": ["_NP _VP"]}
        PP = {"_PP": ["_IN _NN"]}

        if '_JJ' in list_tag:
            NP_RULES = self.generate_NP(list_tag)
            NP = {"_NP": NP_RULES}

            VP_RULES = self.generate_VP(list_tag)
            VP = {"_VP": VP_RULES}

            for r in [S, NP, VP, PP]:
                result.update(r)
            return result
        else:
            NP_RULES = self.remove_JJ(self.generate_NP(list_tag))
            NP = {"_NP": NP_RULES}

            VP_RULES = self.remove_JJ(self.generate_VP(list_tag))
            VP = {"_VP": VP_RULES}

            for r in [S, NP, VP, PP]:
                result.update(r)
            return result

    def check_VP(self, list_tag):
        """Return True if there is tag '_VBI' or '_VBT'
        Args:
            list_tag(list): a list of tags
        Returns:
            True if there is tag '_VBI' or '_VBT', False otherwise
        """
        for tag in list_tag:
            if '_V' in tag:
                return True
        return False

    def remove_JJ(self, list_tag):
        """Remove element in a list of tags that contains '_JJP'
        Args:
            list_tag(list): a list of tags
        Returns:
            modified list_tag without '_JJP'
        """
        result = []
        for tag in list_tag:
            if '_JJ' in tag:
                continue
            else:
                result.append(tag)
        return result

    def generate_NP(self, list_tag):
        """Generate tags for '_NP'
        Args:
            list_tag(list): a list of tags
        Returns:
            modified list_tag for '_NP'
        """
        result = []
        for tag in list_tag:
            for words in self.NP:
                if re.search(r'\b' + tag + r'\b', words):
                    result.append(words)
        return list(OrderedDict.fromkeys(result))

    def generate_VP(self, list_tag):
        """Generate tags for '_VP'
        Args:
            list_tag(list): a list of tags
        Returns:
            modified list_tag for '_VP'
        """
        result = []
        for tag in list_tag:
            for words in self.VP:
                if re.search(r'\b' + tag + r'\b', words):
                    result.append(words)
        return list(OrderedDict.fromkeys(result))

    def generate_words_grammar(self, dict_words_by_tag):
        """Generate words grammar production rules
        Args:
            dict_words_by_tag(dict): dictionary of 'key': 'tag' and 'value': 'a list of words'
        Returns:
            words_grammar(dict): words grammar production rules
        """
        result = {}
        IN = {"_IN": ['di']}
        CC = {"_CC": ['dan']}
        SC = {"_SC": ['yang']}
        ADD_VBI = {"_VBI": ['ada']}
        ADD_VBT = {"_VBT": ['memiliki', 'adalah', 'merupakan', 'mempunyai']}

        WORDS = dict_words_by_tag
        if '_VBT' in WORDS:
            for word in ADD_VBT["_VBT"]:
                if word not in WORDS['_VBT']:
                    WORDS['_VBT'].append(word)
        else:
            WORDS.update(ADD_VBT)

        if '_VBI' in WORDS:
            for word in ADD_VBI["_VBI"]:
                if word not in WORDS['_VBI']:
                    WORDS['_VBI'].append(word)
        else:
            WORDS.update(ADD_VBI)
            WORDS = dict_words_by_tag

        for r in [IN, CC, SC, WORDS]:
            result.update(r)
        return result


class CFG_Cerita():
    """
        Implementation Context-free Grammar
    """
    def __init__(self):
        self.NP = ['_PRP', '_NN', '_NN _NN', '_NN _DT', '_NNG', '_NNP']
        self.VP = ['_VBT _NN', '_VBT _NN _NN', '_VBT _PP', '_VBT _PP _NN', '_RB _VBT', '_RB _VBT _PP',
                   '_VBI', '_VBI _NN', '_VBI _SC _JJ', '_SC _VBI',
                   '_VBT _PP _SC _VBI', '_SC _JJ', '_PP']

    def create_sentences_from_data(self, dict_data):
        """Create dictionary with key: topic and value: list of sentences
        Args:
            dict_data(dict): dictionary data with 'key': 'topic' and 'value': 'list of words'
        Returns:
            dictionary data with 'key': 'topic' and 'value': 'list of sentences'
        """
        result = {}
        np.random.seed(10)
        for topic, words in dict_data.items():
            sentence = []
            grammar, dict_pwz_by_tag = self.create_grammar(words)
            for s in range(10):
                sentence.append(' '.join(self.generate_sentence(grammar, dict_pwz_by_tag)))
            result = self.merge_two_dicts(result, {topic: sentence})
        return result

    def is_terminal(self, token):
        """Check whether token is terminal
        Args:
            token(str): token from production rules grammar
        Returns:
            True if token is a terminal, and False otherwise
        """
        return token[0] != "_"

    def expand(self, grammar, tokens, dict_pwz_by_tag):
        """Recursive to replace tokens with random words
        Args:
            grammar(dict): dictionary of grammar production rules
            tokens(str): token in grammar production rules
            dict_pwz_by_tag(dict): dictionary of pwz by tag
        Returns:
            token with random word
        """
        for i, token in enumerate(tokens):

            # skip over terminals
            if self.is_terminal(token): continue

            # if we get here, we found a non-terminal token
            # so we need to choose a replacement at random
            replacement = nr.choice(grammar[token])

            if replacement == '_NN':
                dict_pwz_by_tag['_NN'] = [float(i) for i in dict_pwz_by_tag['_NN']]
                weight = [x/sum(dict_pwz_by_tag['_NN']) for x in dict_pwz_by_tag['_NN']]
                replacement = nr.choice(grammar['_NN'], p=weight)

            if self.is_terminal(replacement):
                tokens[i] = replacement
            else:
                tokens = tokens[:i] + replacement.split() + tokens[(i+1):]

            # now call expand on the new list of tokens
            return self.expand(grammar, tokens, dict_pwz_by_tag)

        # if we get here we had all terminals and are done
        return tokens

    def generate_sentence(self, grammar, dict_pwz_by_tag):
        """Generate sentence randomly from token '_S'
        Args:
            grammar(dict): dictionary of grammar production rules
            dict_pwz_by_tag(dict): dictionary of pwz by tag
        Returns:
            sentence(list): list of words randomly
        """
        return self.expand(grammar, ["_S"], dict_pwz_by_tag)

    def merge_two_dicts(self, x, y):
        """Merge two dictionaries into a new dictionary as a shallow copy
        Args:
            x(dict): dictionary 1
            y(dict): dictionary 2
        Returns:
            z(dict): merge of x and y
        """
        z = x.copy()
        z.update(y)
        return z

    def create_grammar(self, dict_words_by_topic):
        """Create grammar production rules
        Args:
            dict_words_by_topic(dict): dictionary of topic that contains words
        Returns:
            grammar(dict): grammar production rules
        """
        grammar = {}

        dict_words_pwz_by_tag = self.organize_words_by_tag(dict_words_by_topic)
        list_tag = self.get_list_tag(dict_words_pwz_by_tag)
        base_grammar = self.generate_base_grammar(list_tag)
        dict_word_by_tag, dict_pwz_by_tag = self.split_word_pwz(dict_words_pwz_by_tag)
        words_grammar = self.generate_words_grammar(dict_word_by_tag)

        for r in [base_grammar, words_grammar]:
            grammar.update(r)
        return grammar, dict_pwz_by_tag

    def organize_words_by_tag(self, list_words):
        """Create dictionary of 'key': 'tag' and 'value': 'a list of words'
        Args:
            list_words(dict): a list words with tag
        Returns:
            dict_words_by_tag(dict): dictionary of 'key': 'tag' and 'value': 'a list of words'
        """
        result = defaultdict(list)

        for s in list_words:
            word, pwz = s[0], s[1]

            wrd = word.split('/')[0]
            tag = word.split('/')[1]
            result['_'+tag].append([wrd, pwz])
        return dict(result)

    def split_word_pwz(self, dict_words_pwz_by_tag):
        """Split word and pwz.
        Args:
            dict_words_pwz_by_tag(dict): dictionary word and pwz by tag
        Returns:
            dict_word_by_tag: dictionary word by tag
            dict_pwz_by_tag: dictionary pwz by tag
        """
        dict_word_by_tag = defaultdict(list)
        dict_pwz_by_tag = defaultdict(list)

        for key, values in dict_words_pwz_by_tag.items():
            for data in values:
                word, pwz = data[0], data[1]
                dict_word_by_tag[key].append(word)
                dict_pwz_by_tag[key].append(pwz)
        return dict(dict_word_by_tag), dict(dict_pwz_by_tag)

    def get_list_tag(self, dict_words_by_tag):
        """Get tags in dictionary of 'key': 'tag' and 'value': 'a list of words'
        Args:
            dict_words_by_tag(dict): dictionary of 'key': 'tag and 'value': 'a list of words'
        Returns:
            list_tag(list): a list of tags
        """
        result = []
        for key in dict_words_by_tag:
            result.append(key)
        return result

    def generate_base_grammar(self, list_tag):
        """Generate base grammar (only terminal)
        Args:
            list_tag(list): a list of tags
        Returns:
            base_grammar(dict): base grammar production rules
        """
        result = {}

        if '_VBT' not in list_tag:
            list_tag.append('_VBT')

        if '_VBI' not in list_tag:
            list_tag.append('_VBI')

        S = {"_S": ["_NP _VP"]}
        PP = {"_PP": ["_IN _NN"]}

        if '_JJ' in list_tag:
            NP_RULES = ['_PRP'] + self.generate_NP(list_tag)
            NP = {"_NP": NP_RULES}

            VP_RULES = ['_SC _JJ', '_PP'] + self.generate_VP(list_tag)
            VP = {"_VP": VP_RULES}

            for r in [S, NP, VP, PP]:
                result.update(r)
            return result
        else:
            NP_RULES = ['_PRP'] + self.remove_JJ(self.generate_NP(list_tag))
            NP = {"_NP": NP_RULES}

            VP_RULES = ['_PP'] + self.remove_JJ(self.generate_VP(list_tag))
            VP = {"_VP": VP_RULES}

            for r in [S, NP, VP, PP]:
                result.update(r)
            return result

    def check_VP(self, list_tag):
        """Return True if there is tag '_VBI' or '_VBT'
        Args:
            list_tag(list): a list of tags
        Returns:
            True if there is tag '_VBI' or '_VBT', False otherwise
        """
        for tag in list_tag:
            if '_V' in tag:
                return True
        return False

    def remove_JJ(self, list_tag):
        """Remove element in a list of tags that contains '_JJP'
        Args:
            list_tag(list): a list of tags
        Returns:
            modified list_tag without '_JJP'
        """
        result = []
        for tag in list_tag:
            if '_JJ' in tag:
                continue
            else:
                result.append(tag)
        return result

    def generate_NP(self, list_tag):
        """Generate tags for '_NP'
        Args:
            list_tag(list): a list of tags
        Returns:
            modified list_tag for '_NP'
        """
        result = []
        for tag in list_tag:
            for words in self.NP:
                if re.search(r'\b' + tag + r'\b', words):
                    result.append(words)
        return list(OrderedDict.fromkeys(result))

    def generate_VP(self, list_tag):
        """Generate tags for '_VP'
        Args:
            list_tag(list): a list of tags
        Returns:
            modified list_tag for '_VP'
        """
        result = []
        for tag in list_tag:
            for words in self.VP:
                if re.search(r'\b' + tag + r'\b', words):
                    result.append(words)
        return list(OrderedDict.fromkeys(result))

    def generate_words_grammar(self, dict_words_by_tag):
        """Generate words grammar production rules
        Args:
            dict_words_by_tag(dict): dictionary of 'key': 'tag' and 'value': 'a list of words'
        Returns:
            words_grammar(dict): words grammar production rules
        """
        result = {}
        PRP = {"_PRP": ['aku']}
        IN = {"_IN": ['di', 'dengan', 'ke']}
        CC = {"_CC": ['dan']}
        SC = {"_SC": ['yang']}
        RB = {"_RB": ['sedang', 'sambil', 'masih', 'lagi']}
        DT = {"_DT": ['itu', 'ini']}
        MD = {"_MD": ['bisa', 'telah', 'sudah']}
        ADD_VBT = {"_VBT": ['ingin']}
        ADD_VBI = {"_VBI": ['ada']}

        WORDS = dict_words_by_tag
        if '_VBT' in WORDS:
            for word in ADD_VBT["_VBT"]:
                if word not in WORDS['_VBT']:
                    WORDS['_VBT'].append(word)
        else:
            WORDS.update(ADD_VBT)

        if '_VBI' in WORDS:
            for word in ADD_VBI["_VBI"]:
                if word not in WORDS['_VBI']:
                    WORDS['_VBI'].append(word)
        else:
            WORDS.update(ADD_VBI)
            WORDS = dict_words_by_tag

        for r in [PRP, IN, CC, SC, RB, DT, MD, WORDS]:
            result.update(r)
        return result
