from flask import Flask, request, send_from_directory, render_template, jsonify
from engine_core import search_core
import json

app = Flask(__name__)
app.debug = True

search_service = search_core()
iteration_data = {}

def search_objects_to_topics(search_objects, desired_number_topics=10, desired_number_top_words=10):
    search_service.set_query(search_objects)
    search_service.set_desired_number_topics(desired_number_topics)
    search_service.set_desired_number_top_words(desired_number_top_words)
    top_words_results, top_articles_result = search_service.search()


    global iteration_data

    topics = {}
    iteration_data = {}
    id_iterator = 0

    for topic in top_words_results:
        topic_name = topic[0]
        topics[str(topic_name)] = {}
        topics[str(topic_name)]['keywords'] = []

        for keyword in topic[1]:
            topics[str(topic_name)]['keywords'].append({ 'label': keyword.get_text(), 'id': id_iterator })
            iteration_data[str(id_iterator)] = keyword
            id_iterator = id_iterator + 1

    for topic in top_articles_result:
        topic_name = topic[0]
        topics[str(topic_name)]['articles'] = []

        for article in topic[1]:
            article_authors = [];

            for author in article.authors:
                authors_top_articles = []

                for top_article in author.top_articles():
                    authors_top_articles.append({ 'title': top_article.title, 'id': id_iterator })
                    iteration_data[str(id_iterator)] = top_article
                    id_iterator = id_iterator + 1

                article_authors.append({ 'name': author.name, 'id': author.id, 'articles': authors_top_articles })

            topics[str(topic_name)]['articles'].append({ 'abstract': article.get_text(), 'title': article.title, 'id': id_iterator, 'authors': article_authors, 'venue': article.venue, 'url': article.url })
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
        search_objects.append(iteration_data[str(selection)])

    topics = search_objects_to_topics(search_objects, 10, 10)

    return jsonify(topics)

@app.route('/api/search', methods=['GET'])
def search():
    topic_count = int(request.args.get('topic_count'))
    keyword_count = int(request.args.get('keyword_count'))
    keywords = request.args.get('keywords').split()
    search_objects = search_service.create_word_search_object(keywords)

    topics = search_objects_to_topics(search_objects, topic_count, keyword_count)

    return jsonify(topics)

@app.route('/api/authors/<id>')
def author_by_id(id):
    return jsonify({ 'name': 'Kalle Ilves', 'topics': [{ 'topic': 1, 'articles': [{ 'title': 'Lorem ipsum dolor sit amet', 'id': 1 } for n in range(0, 10)] }] })

if __name__ == '__main__':
    app.run()
