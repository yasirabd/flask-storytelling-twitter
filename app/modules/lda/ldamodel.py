from collections import Counter
from collections import defaultdict
import random

class LdaModel:
    """
    Parameters:
        `documents` is the documents which used to find the topics
        `K` is the number of topics
        `alpha` is the hyperparameter for document topic distribution
        `beta` is the hyperparameter for topic word distribution
    """
    def __init__(self, documents=None, K=3, alpha=0.1, beta=0.1, iterations=1000):
        self.documents = documents
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations

        if documents is not None:
            self.doProcess()

    def doProcess(self):
        """do process"""
        # a list of Counters, one for each document in documents
        self.document_topic_counts = [Counter() for _ in self.documents]

        # a list of Counters, one for each topic
        self.topic_word_counts = [Counter() for _ in range(self.K)]

        # a list of numbers, one for each topic
        self.topic_counts = [0 for _ in range(self.K)]

        # a list of numbers, one for each document
        self.document_lengths = [len(d) for d in self.documents]

        # the number of distinct words
        distinct_words = set(word for document in self.documents for word in document)
        self.W = len(distinct_words)

        # the number of documents
        D = len(self.documents)

        # assigning every word to a random topic, and populating Counter
        random.seed(0)
        self.document_topics = [[random.randrange(self.K) for word in document]
                                for document in self.documents]

        # a list of pwz
        keys = distinct_words
        topics = [k for k in range(self.K)]
        self.pwz_counts = {key: {key: 0 for key in topics} for key in keys}

        for d in range(D):
            for word, topic, in zip(self.documents[d], self.document_topics[d]):
                self.document_topic_counts[d][topic] += 1
                self.topic_word_counts[topic][word] += 1
                self.topic_counts[topic] += 1

        # Gibbs Sampling
        for iter in range(self.iterations):
            for d in range(D):
                for i, (word, topic) in enumerate(zip(self.documents[d],
                                                      self.document_topics[d])):

                    # remove this word / topic from counts
                    # so that it doesn't influence the weights
                    self.document_topic_counts[d][topic] -= 1
                    self.topic_word_counts[topic][word] -= 1
                    self.topic_counts[topic] -= 1
                    self.document_lengths[d] -= 1

                    # choose a new topic based on the weights
                    new_topic = self.choose_new_topic(d, word, self.K)
                    self.document_topics[d][i] = new_topic

                    # and now add it back to the counts
                    self.document_topic_counts[d][new_topic] += 1
                    self.topic_word_counts[new_topic][word] += 1
                    self.topic_counts[new_topic] += 1
                    self.document_lengths[d] += 1

        # get word with pwz
        for d in range(D):
            for i, (word, topic) in enumerate(zip(self.documents[d], self.document_topics[d])):
                pwz = self.p_word_given_topic(word, topic, self.beta)
                self.pwz_counts[word][topic] = pwz

    def p_topic_given_document(self, topic, d, alpha):
        """the fraction of words in document _d_
        that are assigned to _topic_ (plus some smoothing)"""

        return ((self.document_topic_counts[d][topic] + alpha) /
                (self.document_lengths[d] + self.K * alpha))

    def p_word_given_topic(self, word, topic, beta):
        """the fration of words assigned to _topic_
        that equal _word_ (plus some smoothing)"""

        return ((self.topic_word_counts[topic][word] + beta) /
                (self.topic_counts[topic] + self.W * beta))

    def topic_weight(self, d, word, k):
        """given a document and a word in that document,
        return the weight for the k-th topic"""

        return self.p_word_given_topic(word, k, self.beta) * self.p_topic_given_document(k, d, self.alpha)

    def sample_from(self, weights):
        """returns i with probability weights[i] / sum(weights)"""

        total = sum(weights)
        rnd = total * random.random()     # uniform between 0 and total
        for i, w in enumerate(weights):
            rnd -= w                      # return the smallest i such that
            if rnd <= 0: return i         # weights[0] + ... + weights[i] >= rnd

    def choose_new_topic(self, d, word, K):
        """returns the new topics"""

        return self.sample_from([self.topic_weight(d, word, k)
                            for k in range(K)])

    def get_pwz(self, word):
        """return probability word given topic (pwz)"""
        return self.pwz_counts[word]

    def get_topic_word_pwz(self, documents_tagged):
        """return list contains topic, word with tag, and probability word given topic (pwz)"""
        # split the document by space
        documents_tagged_splitted = []
        for t in documents_tagged:
            documents_tagged_splitted.append(t.split(' '))

        distinct_words_tagged = sorted(set(word for document in documents_tagged_splitted for word in document))

        result = []
        for k, word_counts in enumerate(self.topic_word_counts):
            for word, count in word_counts.most_common():
                if count > 0:
                    temp = []
                    for word_tagged in distinct_words_tagged:
                        if word == word_tagged.split('/')[0]:
                            temp.append(word_tagged)

                    if len(temp) > 1:
                        for t in temp:
                            result.append([k, t, self.get_pwz(word)[k]])
                    else:
                        result.append([k, ''.join(temp), self.get_pwz(word)[k]])
        return result
