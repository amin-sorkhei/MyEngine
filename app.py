from flask import Flask, request, send_from_directory, render_template, jsonify
from engine_core import search_core
import json

app = Flask(__name__)
app.debug = True

search_service = search_core()
iteration_data = {}
author_mapping = {}
id_iterator = 0

def search_objects_to_topics(search_objects, desired_number_topics=10, desired_number_top_words=10):
    search_service.set_query(search_objects)
    search_service.set_desired_number_topics(desired_number_topics)
    search_service.set_desired_number_top_words(desired_number_top_words)
    top_words_results, top_articles_result = search_service.search()

    global iteration_data, id_iterator, author_mapping

    topics = []
    iteration_data = {}
    author_mapping = {}
    id_iterator = 0
    author_iterator = 0

    for topic in top_words_results:
        topic_name = topic[0]
        t = { 'topic': topic_name }
        t['keywords'] = []

        for keyword in topic[1]:
            t['keywords'].append({ 'label': keyword.get_text(), 'id': id_iterator })
            iteration_data[str(id_iterator)] = keyword
            id_iterator = id_iterator + 1

        topics.append(t)

    for topic in top_articles_result:
        topic_name = topic[0]

        t = filter(lambda target: target['topic'] == topic_name, topics)[0]

        t['articles'] = []

        for article in topic[1]:
            article_authors = [];

            for author in article.authors:
                authors_top_articles = []
                number_of_articles = author.num_of_articles()
                core_top_articles = author.top_articles(article.id)

                if number_of_articles < 6:
                    for top_article in core_top_articles:
                        authors_top_articles.append({ 'title': top_article.title, 'id': id_iterator, 'abstract': top_article.abstract, 'realId': top_article.id })
                        iteration_data[str(id_iterator)] = top_article
                        id_iterator = id_iterator + 1
                else:
                    for top_topic in core_top_articles:
                        articles_in_topic = []

                        for top_article in top_topic[1]:
                            articles_in_topic.append({ 'title': top_article.title, 'id': id_iterator, 'abstract': top_article.abstract, 'realId': top_article.id })
                            iteration_data[str(id_iterator)] = top_article
                            id_iterator = id_iterator + 1

                        authors_top_articles.append({ 'topic': top_topic[0], 'articles': articles_in_topic })

                article_authors.append({ 'name': author.name, 'id': author.id, 'articles': authors_top_articles, 'numArticles': number_of_articles, 'index': author_iterator })

                author_mapping[str(author_iterator)] = author
                author_iterator = author_iterator + 1

            t['articles'].append({ 'abstract': article.get_text(), 'title': article.title, 'id': id_iterator, 'authors': article_authors, 'venue': article.venue, 'url': article.url, 'realId': article.id })

            iteration_data[str(id_iterator)] = article
            id_iterator = id_iterator + 1

    return topics

@app.route('/dist/<path:path>')
def send_static_file(path):
    return send_from_directory('dist', path)

@app.route('/node_modules/<path:path>')
def send_module(path):
    return send_from_directory('node_modules', path)

@app.route('/src/app/views/<path:path>')
def send_template(path):
    return send_from_directory('src/app/views', path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/next', methods=['POST'])
def next():
    selections = json.loads(request.data)
    search_objects = []

    for selection in selections:
        if str(selection) in iteration_data:
            search_objects.append(iteration_data[str(selection)])

    topics = search_objects_to_topics(search_objects, 10, 10)

    return json.dumps(topics)

@app.route('/api/search', methods=['GET'])
def search():
    topic_count = int(request.args.get('topic_count'))
    keyword_count = int(request.args.get('keyword_count'))
    keywords = request.args.get('keywords').split()
    search_objects = search_service.create_word_search_object(keywords)

    topics = search_objects_to_topics(search_objects, topic_count, keyword_count)

    return json.dumps(topics)

@app.route('/api/more_articles_from_author/<author_index>', methods=['GET'])
def more_topics(author_index):
    global id_iterator, author_mapping, iteration_data

    author = author_mapping[str(author_index)]
    articles = author.show_more()
    response_articles = []

    for article in articles:
        response_articles.append({ 'title': article.title, 'id': id_iterator, 'abstract': article.abstract, 'realId': article.id })
        iteration_data[str(id_iterator)] = article
        id_iterator = id_iterator + 1

    return json.dumps(response_articles)

if __name__ == '__main__':
    app.run()
