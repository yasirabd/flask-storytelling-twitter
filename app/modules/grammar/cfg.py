from collections import OrderedDict, defaultdict
import re, random


NP = ['_NN', '_NNP', '_NNG', '_NN _DT', '_NN _JJP', '_NNP _JJP', '_NP _CC _NP']
VP = ['_VBT _NP', '_VBT _NP _PP', '_VBI', '_VBI _PP', '_PP', '_JJP']

class CFG():
    """
        Implementation Context-free Grammar
    """
    def __init__(self):
        pass

    def create_sentences_from_data(self, dict_data):
        """Create dictionary with key: topic and value: list of sentences
        Args:
            dict_data(dict): dictionary data with 'key': 'topic' and 'value': 'list of words'
        Returns:
            dictionary data with 'key': 'topic' and 'value': 'list of sentences'
        """
        result = {}
        for topic, words in dict_data.items():
            sentence = []
            grammar = self.create_grammar(words)
            for s in range(10):
                sentence.append(' '.join(self.generate_sentence(grammar)))
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

    def expand(self, grammar, tokens):
        """Recursive to replace tokens with random words
        Args:
            grammar(dict): dictionary of grammar production rules
            tokens(str): token in grammar production rules
        Returns:
            token with random word
        """
        for i, token in enumerate(tokens):

            # skip over terminals
            if self.is_terminal(token): continue

            # if we get here, we found a non-terminal token
            # so we need to choose a replacement at random
            replacement = random.choice(grammar[token])

            if self.is_terminal(replacement):
                tokens[i] = replacement
            else:
                tokens = tokens[:i] + replacement.split() + tokens[(i+1):]

            # now call expand on the new list of tokens
            return self.expand(grammar, tokens)

        # if we get here we had all terminals and are done
        return tokens

    def generate_sentence(self, grammar):
        """Generate sentence randomly from token '_S'
        Args:
            grammar(dict): dictionary of grammar production rules
        Returns:
            sentence(list): list of words randomly
        """
        return self.expand(grammar, ["_S"])

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
        result = {}
        dict_words_by_tag = self.organize_words_by_tag(dict_words_by_topic)
        list_tag = self.get_list_tag(dict_words_by_tag)

        base_grammar = self.generate_base_grammar(list_tag)
        words_grammar = self.generate_words_grammar(dict_words_by_tag)
        for r in [base_grammar, words_grammar]:
            result.update(r)
        return result

    def organize_words_by_tag(self, list_words):
        """Create dictionary of 'key': 'tag' and 'value': 'a list of words'
        Args:
            list_words(dict): a list words with tag
        Returns:
            dict_words_by_tag(dict): dictionary of 'key': 'tag' and 'value': 'a list of words'
        """
        result = defaultdict(list)
        i = []
        for s in list_words:
            word = s.split('/')[0]
            tag = s.split('/')[1]
            result['_'+tag].append(word)
        return dict(result)

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
        S = {"_S": ["_NP _VP"]}
        PP = {"_PP": ["_IN _NP"]}
        if '_JJ' in list_tag:
            NP_RULES = ['_NP _CC _NP'] + self.generate_NP(list_tag)
            NP = {"_NP": NP_RULES}
            if self.check_VP(list_tag):
                VP_RULES = ['_PP', '_JJP'] + self.generate_VP(list_tag)
                VP = {"_VP": VP_RULES}
            else:
                VP = {"_VP": ['_PP', '_JJP']}
            JJP = {"_JJP": ['_JJ', '_JJ _CC _JJ']}

            for r in [S, NP, VP, PP, JJP]:
                result.update(r)
            return result
        else:
            NP_RULES = ['_NP _CC _NP'] + self.remove_JJP(self.generate_NP(list_tag))
            NP = {"_NP": NP_RULES}
            if self.check_VP(list_tag):
                VP_RULES = ['_PP'] + self.remove_JJP(self.generate_VP(list_tag))
                VP = {"_VP": VP_RULES}
            else:
                VP = {"_VP": ['_PP']}

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

    def remove_JJP(self, list_tag):
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
            for words in NP:
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
            for words in VP:
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
        IN = {"_IN": ['di', 'ke', 'dari']}
        DT = {"_DT": ['ini', 'itu']}
        CC = {"_CC": ['dan', 'atau']}
        WORDS = dict_words_by_tag
        for r in [IN, DT, CC, WORDS]:
            result.update(r)
        return result
