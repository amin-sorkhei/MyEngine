__author__ = 'sorkhei'

import nltk
import pickle
import numpy as np
import matplotlib.pyplot as plt
import collections


class search_object():
    def __init__(self, _text, _id, _matrix, _type):
        self.type = _type
        self.id = _id
        self.matrix = _matrix
        self.text = _text

    def get_matrix(self):
        return self.matrix

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_text(self):
        return self.text


class search_core():
    def __init__(self):
        self.word_id_dic = pickle.load(open('word_id_dic.pkl', 'r'))
        self.id_word_dic = pickle.load(open('id_word_dic.pkl', 'r'))
        self.word_topic_matrix = pickle.load(open('word_topic_weight_matrix.pkl', 'r'))
        self.id_abstracts_dic = pickle.load(open('id_abstracts_dic.pkl'))
        self.doc_topic_matrix = pickle.load(open('doc_topic_matrix.pkl'))
        self.stemmer = nltk.PorterStemmer()
        self.query = ''
        self.desired_top_topics = 0
        self.desired_top_words = 0
        self.desired_top_articles = 2

    def reset(self):
        self.query = []
        self.desired_top_topics = 0
        self.desired_top_words = 0

    def word_valideator(self, word):
        return self.stem(word.lower()) in self.word_id_dic.keys()

    def stem(self, word):
        return self.stemmer.stem(word)

    def create_word_search_object(self, raw_query):
        """ Creates search objects from raw input """
        tmp = [self.stem(item.lower()) for item in raw_query]
        result = []
        for item in tmp:
            _text = item
            _id = self.word_id_dic[_text]
            _matrix = self.word_topic_matrix[_id, :]
            _type = 'word'
            result.append(search_object(_text, _id, _matrix, _type))
        return result

    def set_query(self, query):
        self.query = query

    def set_desired_number_topics(self, number_topics):
        self.desired_top_topics = number_topics

    def set_desired_number_top_words(self, number_words):
        self.desired_top_words = number_words

    def search(self):
        if len(self.query) == 1:
            top_topics = self.single_word_search()
        else:
            top_topics = self.multi_word_search()

        return self.topic_article_finder(top_topics)

    def multi_word_search(self):
        print ('multi word search entered')
        voting_matrix = np.array([np.argsort(search_object_instance.get_matrix())[::-1] for search_object_instance in self.query])

        for item in self.query:
            print str(item.get_id()) + ' ' + str(item.get_text()) + '\n' + str(np.argsort(item.get_matrix())[::-1][0:20])

        num_of_candidate_topics = len(voting_matrix[0])
        counter_dictionary = dict([(k, [0, 0]) for k in set(voting_matrix.flatten())])
        for i, j in enumerate(voting_matrix.flatten()):
            counter_dictionary[j][0] += 1
            counter_dictionary[j][1] += i % num_of_candidate_topics

        # (topic, count, position)
        list_of_topic_count_score_tuples = map(lambda x: (x[0], x[1][0], x[1][1]), counter_dictionary.items())
        # items with counter greater than one is of interest
        list_of_topic_count_score_tuples = filter(lambda x: x[1] > 1, list_of_topic_count_score_tuples)
        list_of_topic_count_score_tuples = sorted(list_of_topic_count_score_tuples, key=lambda x: (x[1], -x[2]))[::-1]
        selected_topics = [topic_count_score[0] for topic_count_score in list_of_topic_count_score_tuples]
        print selected_topics[0:self.desired_top_topics]
        print '\n\n'
        return selected_topics[0:self.desired_top_topics]

    def single_word_search(self):
        print('single word search entered')
        self.query = self.query[0]
        print self.query
        top_topics = np.argsort(self.query.get_matrix())[::-1][0:self.desired_top_topics]
        return top_topics

    def topic_article_finder(self, top_topics):
        topic_search_words_tuples = []
        topic_search_articles_tuples = []
        search_articles_list = []
        search_words_list = []
        for topic in top_topics:
            words_id = np.argsort(self.word_topic_matrix[:, topic])[::-1][0:self.desired_top_words]
            articles_id = np.argsort(self.doc_topic_matrix[:, topic])[::-1][0:self.desired_top_articles]
            for word_id in words_id:
                _id = word_id
                _text = self.id_word_dic[_id]
                _matrix = self.word_topic_matrix[_id, :]
                _type = 'word'
                search_words_list.append(search_object(_text, _id, _matrix, _type))
            topic_search_words_tuples.append((topic, search_words_list))
            search_words_list = []

            for article_id in articles_id:
                _id = article_id
                _text = self.id_abstracts_dic[_id]
                _matrix = self.doc_topic_matrix[_id, :]
                _type = 'doc'
                search_articles_list.append(search_object(_text, _id, _matrix, _type))
            topic_search_articles_tuples.append((topic, search_articles_list))
            search_articles_list = []
        # print 'Top words ' + str(topic_search_words_tuples)
        # print 'Top articles ' + str(topic_search_articles_tuples)
        return topic_search_words_tuples, topic_search_articles_tuples
