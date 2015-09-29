__author__ = 'sorkhei'
version = '2.01'
"""
New to version 2.01
ability to show more articles and papers
"""
import nltk
import pickle
import numpy as np
import copy
import lemmagen
from lemmagen.lemmatizer import Lemmatizer
from article_author2 import article


class search_object(object):
    def __init__(self, _text, _id, _matrix):
        self.id = _id
        self.matrix = _matrix
        self.text = _text

    def get_vector(self):
        return self.matrix

    def get_id(self):
        return self.id

    def get_text(self):
        return self.text


class author:
    def __init__(self, _id, _name, _papers):
        self.id = _id
        self.name = _name
        # papers is a list of mini article search objects
        self.papers = _papers
        self.displayed_papers_ids = []
        self.info = 'Number of papers published by this author : ' + str(self.number_of_articles())
        self.number_of_papers = len(self.papers)

    def number_of_articles(self):
        return len(self.papers)

    def get_info(self):
        return self.info

    def top_articles(self, caller_paper_id):
        """
        Caller_paper_id is the id of the paper from which the author is being called

        The method that GUI deals with when an author is clicked. This function returns
        a list of mini_search_article objects

        If the author has published only one paper, the an empty list is returned

        If the number of published papers is less than 6, all articles are returned a list of papers

        other wise, some measurements will be taken into account -- that is -- research areas of the author is detected
        and two mostly related papers will be displayed there regarding each topic.
        If the author has published more than 5 papers, a list of 3 tuples will be returned
        where the first element is topic number and the second argument is a list of paper objects
        """
        num_of_top_topics = 3
        selected_papers = []
        if caller_paper_id not in self.displayed_papers_ids:
            self.displayed_papers_ids.append(caller_paper_id)

        if self.num_of_articles() == 1:
            return []

        elif self.num_of_articles() < 6:
            return [paper for paper in self.papers if paper.get_id() != caller_paper_id]
        else:
            paper_matrix = np.array([paper.get_vector() for paper in self.papers])
            sum_matrix = np.sum(paper_matrix, 0)
            top_topics = np.argsort(sum_matrix)[::-1][0:num_of_top_topics]
            for top_topic in top_topics:
                tmp_papers = []
                indices = np.argsort(paper_matrix[:, top_topic])[::-1]
                for index in indices:
                    paper = self.papers[index]
                    tmp_papers.append(paper)

                tmp_papers = [paper for paper in tmp_papers if paper.get_id() != caller_paper_id][0:2]
                self.displayed_papers_ids += [paper.get_id() for paper in tmp_papers]
                selected_papers.append((top_topic, tmp_papers))
        return selected_papers

    def show_more(self):
        """
        This function returns a list of 10 papers, if an empty list is returned, then there is no more paper to show
        """
        available_papers = [paper for paper in self.papers if paper.get_id() not in self.displayed_papers_ids]
        ''' update displayed papers '''
        selected_papers = available_papers[0:10]
        self.displayed_papers_ids += [paper.get_id() for paper in selected_papers]
        return selected_papers


class mini_article_search_object(search_object):
    def __init__(self, _id, _matrix, _title, _abstract):
        super(mini_article_search_object, self).__init__(_abstract, _id, _matrix)
        self.title = _title


class article_search_object(search_object):
    def __init__(self, _id, _matrix, _title, _abstract, _authors, _venue, _link):
        super(article_search_object, self).__init__(_abstract, _id, _matrix)
        self.title = _title
        # authors is a list of authors object
        self.authors = _authors
        self.venue = _venue
        self.url = _link

    # def get_text(self):
        # return self.title + '\n' + ','.join([_author.name for _author in self.authors]) + '\n' + self.text + '\n' + self.venue + '\n' + self.url


class search_core():
    def __init__(self):
        print 'This is version ' + version
        self.word_id_dic = pickle.load(open('word_id_dic.pkl', 'r'))
        self.id_word_dic = pickle.load(open('id_word_dic.pkl', 'r'))
        self.word_topic_matrix = pickle.load(open('word_topic_weight_matrix.pkl', 'r'))
        self.doc_topic_matrix = pickle.load(open('doc_topic_matrix.pkl'))

        self.id_author_dic = pickle.load(open('id_author_dic.pkl'))
        self.id_author_articles = pickle.load(open('id_author_article_dic.pkl'))
        self.id_article_dic = pickle.load(open('id_article_dic.pkl'))

        self.stemmer = nltk.PorterStemmer()
        #self.stemmer = Lemmatizer(dictionary=lemmagen.DICTIONARY_ENGLISH)
        self.query = ''
        self.desired_top_topics = 0
        self.desired_top_words = 0
        self.desired_top_articles = 2
        self.total_number_of_selected_articles = 50
        self.total_number_of_selected_words = 50

    def reset(self):
        self.query = []
        self.desired_top_topics = 0
        self.desired_top_words = 0
        self.total_number_of_selected_articles = 50
        self.total_number_of_selected_words = 50

    def word_valideator(self, word):
        return self.stem(word.lower()) in self.word_id_dic.keys()

    def stem(self, word):
        return self.stemmer.stem(word)
        # return self.stemmer.lemmatize(word)

    def create_word_search_object(self, raw_query):
        """ Creates search objects from raw input """
        tmp = [self.stem(item.lower()) for item in raw_query]
        result = []
        for item in tmp:
            _text = item
            _id = self.word_id_dic[_text]
            _matrix = self.word_topic_matrix[_id, :]
            result.append(search_object(_text, _id, _matrix))
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
            top_topics = self.probabilistic_multi_word_search()

        return self.topic_article_finder(top_topics)

    def score_multi_word_search(self):
        print ('score multi word search entered')
        voting_matrix = np.array(
            [np.argsort(search_object_instance.get_vector())[::-1] for search_object_instance in self.query])

        for item in self.query:
            print str(item.get_id()) + ' ' + str(item.get_text()) + '\n' + str(
                np.argsort(item.get_vector())[::-1][0:20])

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

    def probabilistic_multi_word_search(self):
        print ('Probabilistic multi word search entered')
        voting_matrix = np.array(
            [search_object_instance.get_vector() for search_object_instance in self.query])
        '''for item in self.query:
            print str(item.get_id()) + ' ' + str(item.get_text().encode('utf8')) + '\n' + str(
                np.argsort(item.get_vector())[::-1][0:20])'''

        multiplication_result = np.ones(voting_matrix.shape[1])
        for row in xrange(voting_matrix.shape[0]):
            multiplication_result = np.multiply(multiplication_result, voting_matrix[row])
        print 'result'
        print np.sort(multiplication_result)[::-1][0:self.desired_top_topics]
        return np.argsort(multiplication_result)[::-1][0:self.desired_top_topics]

    def single_word_search(self):
        print('single word search entered')
        self.query = self.query[0]
        print self.query
        top_topics = np.argsort(self.query.get_vector())[::-1][0:self.desired_top_topics]
        return top_topics

    def topic_article_finder(self, top_topics):
        """
        total_number_of_articles and total_number_of_words have been selected and returned as tuples
        where the first element of the tuple is the topic number and the second element is the list of  either
        keywords or articles
        """

        topic_search_words_tuples = []
        topic_search_articles_tuples = []
        search_articles_list = []
        search_words_list = []
        for topic in top_topics:
            words_id = np.argsort(self.word_topic_matrix[:, topic])[::-1][0:self.total_number_of_selected_words]
            articles_id = np.argsort(self.doc_topic_matrix[:, topic])[::-1][0:self.total_number_of_selected_articles]
            for word_id in words_id:
                _id = word_id
                _text = self.id_word_dic[_id]
                _matrix = self.word_topic_matrix[_id, :]
                search_words_list.append(search_object(_text, _id, _matrix))
            topic_search_words_tuples.append((topic, search_words_list))
            search_words_list = []

            for article_id in articles_id:
                '''
                add 1 to the idea, since in dataset, ids starts from 1 but mallet starts ids from 0
                '''
                _id = article_id + 1
                _title = self.id_article_dic[_id].title
                _abstract = self.id_article_dic[_id].abstract
                _matrix = self.doc_topic_matrix[_id, :]
                author_ids = self.id_article_dic[_id].author_ids
                _authors = []
                for author_id in author_ids:
                    _name = self.id_author_dic[author_id]
                    _papers = []
                    for paper_id in self.id_author_articles[author_id]:
                        _papers.append(mini_article_search_object(paper_id, self.doc_topic_matrix[paper_id, :],
                                                                  _title=self.id_article_dic[paper_id].title,
                                                                  _abstract=self.id_article_dic[paper_id].abstract))
                    _authors.append(author(author_id, _name, _papers))

                # authors is a list of author objects
                _venue = self.id_article_dic[_id].venue
                _url = self.id_article_dic[_id].url
                tmp_article_search_object = article_search_object(
                    _id, _matrix, _title, _abstract, _authors, _venue, _url)
                search_articles_list.append(tmp_article_search_object)
            topic_search_articles_tuples.append((topic, search_articles_list))
            search_articles_list = []
        # print 'Top words ' + str(topic_search_words_tuples)
        # print 'Top articles ' + str(topic_search_articles_tuples)
        return topic_search_words_tuples, topic_search_articles_tuples
