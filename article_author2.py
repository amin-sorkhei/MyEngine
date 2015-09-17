import numpy as np


class article:
    def __init__(self, _id, _title, _author_ids, _abstract,
                 _venue, _url):
        self.id = _id
        self.title = _title
        self.author_ids = _author_ids
        self.abstract = _abstract
        self.venue = _venue
        self.url = _url



class author:
    def __init__(self, _id, _name, _paper_ids, _matrix):
        self.id = _id
        self.name = _name
        self.paper_ids = _paper_ids
        # self.paper_matrix = _matrix
        # self.research_area = self.find_research_area()
        # self.number_of_papers = len(_paper_ids)
    '''
    def find_research_area(self):
        sum_vector = np.sum(self.paper_matrix, 0)
        research_fields = np.argsort(sum_vector)[::-1]
        return research_fields

    def find_relevant_papers_based_on_topic(self, _topic_number):
        sorted_paper_ids = np.argsort(self.paper_matrix[:, _topic_number])[::-1]
        paper_ids = [self.paper_ids[_id] for _id in sorted_paper_ids]
        return paper_ids

for item in result:
    author_str = item.author.contents[0]
    tmp_str = author_str.replace(';', '')
    auth = [item.strip() for item in tmp_str.split(',')]
    auth = filter(lambda x: x != '' and x != ' ', auth)
    final_author += auth
'''

'''
for item in result:
    article_id = int(item.id.contents[0])-1
    title = unicode(item.title.contents[0])
    abstract = unicode(item.abstract.contents[0])
    venue = unicode(item.venue.contents[0])
    url = unicode(item.url.contents[0])
    abstract_obj = article(article_id, title, abstract, venue, url)
    #---------------------------------
    author_str = item.author.contents[0].split(',')
    authors = [item.strip() for item in author_str]
    authors = filter(lambda author: author != '' and author != ' ', authors)
    for author in authors:
        author_id = dic_tmp_auhtors_id[author]
        abstract_obj.add_author(author_id)
    id_abstract_dic[article_id] = abstract_obj
'''
'''
import re
p = re.compile(ur'\s*(?:Dr|Prof|Mr|Mrs|Ms).\s*([\w|\W]*)')
test_str = u"Dr. Vinay Kumar Pathak\n"
re.search(p, test_str)
'''
'''
for article in id_abstract_dic.values():
    article_id = article.id
    authors = article.author_ids
    if len(authors) == 1:
        author_id_articles[authors[0]].append((article_id, 100))
    else:
        author_id_articles[authors[0]].append((article_id, 40))
        author_id_articles[authors[-1]].append((article_id, 40))
        middle_authors = authors[1:-1]
        if len(middle_authors) != 0:
            score = 20.0/len(middle_authors)
            for author_id in middle_authors:
                author_id_articles[author_id].append((article_id, score))
'''