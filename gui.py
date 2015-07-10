__author__ = 'sorkhei'

from PyQt4 import QtGui, QtCore
import sys
import random
from engine_core import search_core


class search_object_checkbox(QtGui.QStandardItem):
    def __init__(self, search_object):
        super(search_object_checkbox, self).__init__(search_object.get_text())
        self.search_object = search_object

    def get_search_object_data(self):
        return self.search_object



class mainWindow(QtGui.QWidget):
    def __init__(self):
        self.core = search_core()
        self.new_query_list = []
        super(mainWindow, self).__init__()
        self.setWindowTitle('Search Engine')
        self.setWindowIcon(QtGui.QIcon('hiit.jpg'))
        self.showMaximized()

        # --------- Layouts ----------
        self.main_layout = QtGui.QVBoxLayout()
        self.configuration_section = QtGui.QGridLayout()
        self.top_topics_section = QtGui.QHBoxLayout()
        self.top_topics_section_content = QtGui.QHBoxLayout()
        self.top_topics_section_configurations = QtGui.QVBoxLayout()
        self.top_articles_section = QtGui.QHBoxLayout()

        # ----------- Button and Objects Declaration -----------
        self.label_query = QtGui.QLabel('Enter the query:')
        self.label_number_of_topwords = QtGui.QLabel('# Top words: ')
        self.label_number_of_toptopics = QtGui.QLabel('# Top topics: ')
        self.edit_number_of_topwords = QtGui.QLineEdit()
        self.edit_number_of_topwords.setMaximumWidth(50)
        self.edit_number_of_toptopics = QtGui.QLineEdit()
        self.edit_number_of_toptopics.setMaximumWidth(50)
        self.edit_query = QtGui.QLineEdit()

        self.edit_reset_template = QtGui.QTextEdit()
        self.btn_go = QtGui.QPushButton('Go')
        self.btn_reset = QtGui.QPushButton('Reset')
        self.btn_reset.setDisabled(True)
        self.btn_hierarchical_model = QtGui.QPushButton('Hierarchical Mode')
        self.btn_hierarchical_model.setDisabled(True)
        self.btn_next_round = QtGui.QPushButton('Next Round')
        self.btn_next_round.setDisabled(True)

        #self.example_text_area = QtGui.QTextEdit()

        # ------------- validator --------------
        self.edit_number_of_toptopics.setValidator(QtGui.QIntValidator(1, 15))
        self.edit_number_of_topwords.setValidator(QtGui.QIntValidator(1, 30))

        self.initUI()
        self.show()


    def initUI(self):
        # ------------- Inserting Layouts --------------

        self.setLayout(self.main_layout)
        self.main_layout.addLayout(self.configuration_section)
        self.main_layout.addLayout(self.top_topics_section)
        self.main_layout.addLayout(self.top_articles_section)

        self.top_topics_section.addLayout(self.top_topics_section_content)
        self.top_topics_section.addLayout(self.top_topics_section_configurations)

        # ------------ Configuration Section Buttons ----------
        self.configuration_section.addWidget(self.label_number_of_toptopics, 2, 0)
        self.configuration_section.addWidget(self.edit_number_of_toptopics, 2, 1)
        self.configuration_section.addWidget(self.label_number_of_topwords, 3, 0)
        self.configuration_section.addWidget(self.edit_number_of_topwords, 3, 1)
        self.configuration_section.addWidget(self.label_query, 1, 0)
        self.configuration_section.addWidget(self.edit_query, 1, 1)
        self.configuration_section.addWidget(self.btn_go, 1, 2)
        self.configuration_section.addWidget(self.btn_reset, 2, 2)
        self.configuration_section.addWidget(self.btn_hierarchical_model, 3, 2)

        # ----------- Top topics section -----------------
        self.btn_next_round.setFixedSize(self.btn_next_round.sizeHint())
        self.top_topics_section_configurations.addWidget(self.btn_next_round)


        self.edit_reset_template.setDisabled(True)
        self.edit_reset_template.setText('Waiting for Query')
        self.top_topics_section_content.addWidget(self.edit_reset_template)
        self.top_articles_section.addWidget(self.edit_reset_template)

        # -----------Button signals-----------
        self.btn_go.clicked.connect(self.listener_btn_go)
        self.btn_next_round.clicked.connect(self.listener_btn_next_round)
        self.btn_reset.clicked.connect(self.listener_btn_reset)
        self.btn_hierarchical_model.clicked.connect(self.listener_btn_hierarchical_model)




    def empty_layout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    # ---------------- Listeners -----------------
    def listener_btn_go(self):
        entered_query = self.edit_query.text()
        entered_words = str(entered_query).split(' ')
        number_top_words = self.edit_number_of_topwords.text()
        number_top_topics = self.edit_number_of_toptopics.text()

        for word in entered_words:
            if not self.core.word_valideator(word):
                QtGui.QMessageBox.critical(None, 'Hir', word + ' could not be matched')
                self.edit_query.setText('')
                return 0
        if entered_query == '' or number_top_words == '' or number_top_topics == '':
            QtGui.QMessageBox.critical(None, 'Hir', 'Fill in the necessary fields please!')
            return 0

        # ----------- Initialize the Core ---------
        search_objects = self.core.create_word_search_object(entered_words)
        self.core.set_query(search_objects)
        self.core.set_desired_number_topics(int(number_top_topics))
        self.core.set_desired_number_top_words(int(number_top_words))

        # ----------- Change the status of keys and text areas -----
        self.btn_go.setDisabled(True)
        self.btn_reset.setDisabled(False)
        self.btn_next_round.setDisabled(False)
        self.edit_query.setDisabled(True)

        # ---------- run the core -----------
        top_words_results, top_articles_result = self.core.search()
        self.fill_top_topic_section(top_words_results)
        self.fill_top_articles_section(top_articles_result)

    def listener_btn_next_round(self):

        # ---------- ReInitialize the core -------
        number_top_words = self.edit_number_of_topwords.text()
        number_top_topics = self.edit_number_of_toptopics.text()
        self.core.set_desired_number_topics(int(number_top_topics))
        self.core.set_desired_number_top_words(int(number_top_words))
        self.core.set_query(self.new_query_list)
        top_words_results, top_articles_result = self.core.search()
        self.fill_top_topic_section(top_words_results)
        self.fill_top_articles_section(top_articles_result)
        self.new_query_list = []

    def listener_btn_hierarchical_model(self):
        return 0

    def listener_btn_reset(self):
        self.core.reset()
        self.edit_query.setText('')
        self.edit_query.setDisabled(False)
        self.edit_number_of_toptopics.setText('')
        self.edit_number_of_topwords.setText('')
        self.btn_go.setDisabled(False)
        self.btn_next_round.setDisabled(False)
        self.empty_layout(self.top_topics_section_content)
        self.empty_layout(self.top_articles_section)
        self.edit_reset_template.setDisabled(True)
        self.edit_reset_template.setText('Waiting for Query')
        self.top_topics_section_content.addWidget(self.edit_reset_template)
        self.top_articles_section.addWidget(self.edit_reset_template)
    def listener_check_box(self, item):
        if item.checkState():
            self.new_query_list.append(item.get_search_object_data())
        else:
            self.new_query_list.remove(item.get_search_object_data())

        # print self.new_query_list






    def test(self, topic_search_words_tuple):
        list = QtGui.QListView()
        model = QtGui.QStandardItemModel(list)
        model.itemChanged.connect(self.listener_check_box)
        item = QtGui.QStandardItem('Topic :' + str(topic_search_words_tuple[0]))
        model.appendRow(item)
        for search_word in topic_search_words_tuple[1]:
            item = search_object_checkbox(search_word)
            item.setCheckable(True)
            model.appendRow(item)

        list.setModel(model)
        list.setMaximumHeight(150)
        return list

    def fill_top_topic_section(self, topic_search_object_word_tuple):
        self.empty_layout(self.top_topics_section_content)
        for topic_word_tuple in topic_search_object_word_tuple:
            self.top_topics_section_content.addWidget(self.test(topic_word_tuple))

    def fill_top_articles_section(self, topic_search_object_articles_tuples):
        self.empty_layout(self.top_articles_section)
        list = QtGui.QListView()
        list.setWordWrap(True)
        model = QtGui.QStandardItemModel(list)
        model.itemChanged.connect(self.listener_check_box)
        for tuple in topic_search_object_articles_tuples:
            item = QtGui.QStandardItem('Topic :' + str(tuple[0]))
            model.appendRow(item)
            for search_article in tuple[1]:
                item = search_object_checkbox(search_article)
                item.setCheckable(True)
                model.appendRow(item)
                model.appendRow(QtGui.QStandardItem('\n'))
        list.setModel(model)
        self.top_articles_section.addWidget(list)




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = mainWindow()
    sys.exit(app.exec_())
