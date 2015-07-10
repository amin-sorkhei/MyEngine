__author__ = 'sorkhei'
# This package reads data
import os
import pickle
import numpy as np
import re
# This function reads a topic-word-weight file and produces an dictionary
# of the vocabulary
# input: address of the topic-word-weight directory
# output: a .pkl dictionary file called vocab_dic
def word_id_dic_generator(address):
    input_file = open(os.path.join(address, 'topic-word-weight.txt'), 'r')
    output_file1 = open('word_id_dic.pkl', 'w')
    output_file2 = open('id_word_dic.pkl', 'w')
    words = [line.split('\t')[1] for line in input_file.readlines() if line.split('\t')[0] == '0']
    word_id_dic = dict(zip(sorted(words), range(len(words))))
    id_word_dic = dict([(value, key) for key, value in word_id_dic.items()])
    pickle.dump(word_id_dic, output_file1)
    pickle.dump(id_word_dic, output_file2)
    output_file1.close()
    output_file2.close()

    return word_id_dic, id_word_dic


# This function creates a matrix where each row is the id of a word and the entry 'i' of the corresponding row
# stands for the normalized weight that the word belongs to topic number 'i'
def normalizer(address, vocab_dic):
    input_file = open(os.path.join(address, 'topic-word-weight.txt'), 'r')
    outputfile = open('word_topic_weight_matrix.pkl', 'w')
    topic_words_weight_dict = dict([(k, []) for k in sorted(vocab_dic)])
    lines = [line.strip() for line in input_file.readlines()]
    for line in lines:
        topic, word, weight = line.split('\t')
        topic = int(topic)
        weight = float(weight)
        topic_words_weight_dict[word].insert(topic, weight)

    topic_words_weight_matrix = np.array([topic_words_weight_dict[k] for k in sorted(topic_words_weight_dict.keys())],
                                         dtype=float)

    for col in range(topic_words_weight_matrix.shape[1]):
        topic_words_weight_matrix[:, col] /= np.sum(topic_words_weight_matrix[:, col])
    pickle.dump(topic_words_weight_matrix, outputfile)
    return topic_words_weight_matrix


# creates a doc-topic matrix where each row is a doc and each column is a topic
# input: address of the doc-topic.txt directory and the number of topics
# a pickle dictionary and a dictionary returned at the end
def doc_topic_dic_generator(num_of_topics, address):
    input_file = open(os.path.join(address, 'doc-topics.txt'), 'r')
    docs = [line.strip() for line in input_file.readlines()]
    # The first line is information regarding the results and can be safely removed
    del docs[0]
    num_of_docs = len(docs)
    doc_topic_dic = dict([(k, [None] * num_of_topics) for k in range(num_of_docs)])
    for doc in docs:
        doc_id = int(doc.split('\t')[0])
        topics_pro = re.findall(u'\d+\t\d*\.\d*E*[-|+]*\d*', doc)
        for topic_pro in topics_pro:
            topic, probability = topic_pro.split('\t')
            topic = int(topic)
            probability = float(probability)
            assert doc_topic_dic[doc_id][topic] is None
            doc_topic_dic[doc_id][topic] = probability

    doc_topic_matrix = np.array([doc_topic_dic[k] for k in sorted(doc_topic_dic.keys())], dtype=np.float64)

    pickle.dump(doc_topic_matrix, open('doc_topic_matrix.pkl', 'w'))
    return doc_topic_matrix


def id_abstract_dic_generator(address):
    input_file = open(os.path.join(address, 'all_abstract.txt'))
    abstracts = [line.strip() for line in input_file.readlines()]
    id_abstract_dic = dict(zip(xrange(len(abstracts)), abstracts))
    pickle.dump(id_abstract_dic, open('id_abstracts_dic.pkl', 'w'))
    return id_abstract_dic


if __name__ == '__main__':
    address = '/Users/sorkhei/Desktop/mallet-2.0.7/200-stemmed-topics'
    word_id_dic, id_word_dic = word_id_dic_generator(address)
    normalizer(address, word_id_dic)
    doc_topic_dic_generator(num_of_topics=200, address=address)
    id_abstract_dic_generator(address=address)