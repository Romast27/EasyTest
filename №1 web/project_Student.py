import sqlite3
import datetime

from PyQt5 import uic, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QMainWindow, QCheckBox, QLineEdit, QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QListWidgetItem
from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QButtonGroup, QFrame, QScrollArea, QSizePolicy
from PyQt5.QtWidgets import QMessageBox


class DoingTest(QMainWindow):
    def __init__(self, id_test, id_student, client):
        super().__init__()
        uic.loadUi('.\\Ui\\DoingTest.ui', self)
        self.showMaximized()
        self.id_test = id_test
        self.date_now = datetime.datetime.now()
        self.id_student = id_student
        self.client = client
        self.mark = 0
        self.k = 0
        self.flag_manual = False
        self.label_2.setText(f"Тест №{self.id_test}")
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;
           font-weight: bold;}
        QPushButton {
           padding:4px;
           color: #fff;
           border-radius: 6px;
           border: 1px solid #3873d9;
           background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);}
        QPushButton:pressed {
           color: #111;
           border: 1px solid #3873d9;
           background: #fff;}
        QHeaderView {
           background-color: #fff;
           }
        QHeaderView::section:horizontal {
            color: #fff;
            border-style: solid;
            background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);
                                                }
        QTableView {
            border-grid: 3px;
            border-top-color: #4287ff;
            border-radius: 4px;
            background-color: #fff;
            gridline-color: #ccc;
            selection-background-color: #ccdfff;
            color: #333;}
        QScrollBar:vertical {
            background: #e4e4e4;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            width: 12px;
            margin: 0px;}
        QScrollBar::handle:vertical {
            background-color: qlineargradient( x1: 0, y1: 0, x2: 1, y2: 0,
                                        stop: 0 #4287ff, stop: 1 #356ccc);
            border-radius: 4px;
            min-height: 20px;
            margin: 0px 2px 0px 2px;}
         QScrollBar::add-line:vertical {
            background: none;
            height: 0px;
            subcontrol-position: right;
            subcontrol-origin: margin;}
         QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
            subcontrol-position: left;
            subcontrol-origin: margin;}""")
        sql = "SELECT num_questions FROM Test_info WHERE id_test={0}"
        self.num_questions = self.client.listen(sql.format(self.id_test), 1)
        self.num_questions = list(map(lambda x: x[0], self.num_questions))
        self.num_questions = sum(self.num_questions)
        sql = "SELECT id_question FROM Students_answers WHERE id_test={0} AND id_student={1}"
        self.ids_question = self.client.listen(sql.format(self.id_test, self.id_student), 1)
        sql = """SELECT Questions.question, Questions.manual_check FROM Questions 
INNER JOIN 
Students_answers ON Students_answers.id_question = Questions.id_question AND id_student = {0} AND id_test = {1}"""
        self.info = self.client.listen(sql.format(self.id_student, int(self.id_test)), 1)        
        self.make_question()
    
    def make_question(self):
        if self.k == self.num_questions:
            sql = "UPDATE Test_for_student SET done=1 WHERE id_test={0} AND id_student={1}"
            self.client.listen(sql.format(self.id_test, self.id_student), 2)
            if not self.flag_manual:
                sql = "UPDATE Test_for_student SET mark={0} WHERE id_test={1} AND id_student={2}"
                self.client.listen(sql.format(self.mark, self.id_test, self.id_student), 2)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Вы прошли тест")
            msg.setWindowTitle("Завершение")
            msg.exec_()
            self.close()
        else:
            self.flag_answered = False
            self.id_question = self.ids_question[self.k][0]
            self.label_3.setText(f"Вопрос №{self.k + 1}")
            self.question, self.manual_check = self.info[self.k]
            self.text_question.setText(str(self.question))
            self.text_question.setFont(QFont('Arial', 12))
            self.text_question.setReadOnly(True)
            if self.manual_check == 1:
                self.layout = QVBoxLayout()
                self.edit_ans = QLineEdit()
                self.layout.addWidget(self.edit_ans)
                w = QWidget()
                w.setLayout(self.layout)
                self.scroll.setWidget(w)
                self.scroll.show()
                self.btn_save.clicked.connect(self.save_manual_result)
            else:
                sql = "SELECT COUNT(id_answer) FROM Answers WHERE id_question={0}"
                self.num_answers = self.client.listen(sql.format(self.id_question), 1)[0][0]
                self.num_ans = 0
                self.dict_ans = dict()
                self.layout = QVBoxLayout()
                self.group = QButtonGroup()
                self.group.setExclusive(False)
                for j in range(1, self.num_answers + 1):
                    self.num_ans += 1
                    sql = "SELECT answer, correctness FROM Answers " \
                          "WHERE id_question={0} AND id_answer={1}"
                    info = self.client.listen(sql.format(self.id_question, j), 1)
                    print(info)
                    self.answer, self.cor = info[0][0], info[0][1]
                    self.check_btn = QCheckBox()
                    self.check_btn.setFont(QFont('Arial', 12))
                    self.check_btn.setText(str(self.answer))
                    if self.cor == 1:
                        self.check_btn.setObjectName(f'+{self.num_ans}')
                    else:
                        self.check_btn.setObjectName(f'-{self.num_ans}')
                    self.group.addButton(self.check_btn)
                    self.layout.addWidget(self.check_btn)
                w = QWidget()
                w.setLayout(self.layout)
                self.scroll.setWidget(w)
                self.scroll.show()
                self.group.buttonToggled.connect(self.checking_btn)
                self.btn_save.clicked.connect(self.save_result)
        self.k += 1
        
    def checking_btn(self, button):
        self.name = button.objectName()
        if button.checkState() == 2:
            if self.name[0] == '+':
                self.ans_cor = True
                self.mark += 1
            else:
                self.ans_cor = False
            self.dict_ans[self.name[1:]] = self.ans_cor
        else:
            self.dict_ans.pop(self.name[1:])
    
    def save_result(self):
        self.flag_answered = True
        for num, answer in enumerate(self.dict_ans):
            if num == 0:
                sql = "UPDATE Students_answers SET id_answer = {0}, correctness = {1}, checked = 1 WHERE id_test = {2} AND id_student = {3} AND id_question = {4}"
            else:
                sql = "INSERT INTO Students_answers(id_answer, correctness, checked, id_test, id_student, id_question, manual_check) VALUES({0}, {1}, 1, {2}, {3}, {4}, 1)"
            self.client.listen(sql.format(answer, self.dict_ans[answer], self.id_test, self.id_student, self.id_question), 2)
        self.dict_ans = dict()
        self.btn_save.clicked.disconnect()
        self.make_question()

    def save_manual_result(self):
        self.flag_manual = True
        sql = "UPDATE Students_answers SET answer = '{0}' WHERE id_test = {1} AND id_student = {2} AND id_question = {3}"
        self.client.listen(sql.format(self.edit_ans.text(), self.id_test, self.id_student, self.id_question), 2)
        self.btn_save.clicked.disconnect()
        self.make_question()


class MainWindowStudent(QMainWindow):
    def __init__(self, username, id_student, client):
        super().__init__()
        self.username = username
        self.id_student = id_student
        self.client = client
        uic.loadUi('.\\Ui\\MainWindowStudent.ui', self)
        self.showMaximized()
        self.label.setText(self.username)
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;}
        QPushButton {
           padding:4px;
           color: #fff;
           padding: 20px 55px;
           border-radius: 6px;
           border: 1px solid #3873d9;
           background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);}
        QPushButton:pressed {
           color: #111;
           border: 1px solid #3873d9;
           background: #fff;}
        QHeaderView {
           background-color: #fff;
           }
        QHeaderView::section:horizontal {
            color: #fff;
            border-style: solid;
            background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);
                                                }
        QTableView {
            border-grid: 3px;
            border-top-color: #4287ff;
            border-radius: 4px;
            background-color: #fff;
            gridline-color: #ccc;
            selection-background-color: #ccdfff;
            color: #333;}
        QScrollBar:vertical {
            background: #e4e4e4;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            width: 12px;
            margin: 0px;}
        QScrollBar::handle:vertical {
            background-color: qlineargradient( x1: 0, y1: 0, x2: 1, y2: 0,
                                        stop: 0 #4287ff, stop: 1 #356ccc);
            border-radius: 4px;
            min-height: 20px;
            margin: 0px 2px 0px 2px;}
         QScrollBar::add-line:vertical {
            background: none;
            height: 0px;
            subcontrol-position: right;
            subcontrol-origin: margin;}
         QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
            subcontrol-position: left;
            subcontrol-origin: margin;}
         QComboBox{
            background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);
            color: #fff;
            border-style: solid;
            border: 1px solid #3873d9;
            selection-background-color: #ccdfff;}
         QComboBox::drop-down{
            border: none;
            background-color: #fff;
            selection-background-color: #4287ff;
            color: #000;
            font-weight: bold;
            padding: 0px;}""")
        self.create_table(self.id_student)
        
    def create_table(self, id_student):
        self.id_student = id_student
        sql = "SELECT id_test FROM Test_for_student WHERE id_student={0}"
        self.res = self.client.listen(sql.format(id_student), 1)
        self.group = QButtonGroup()
        self.line = QFrame(self.centralwidget)
        self.line.setGeometry(QRect(320, 150, 118, 3))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        for i in range(len(self.res)):
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            sql = "SELECT starting_date, ending_date, limit_time FROM Tests WHERE id_test={0}"
            self.start_date, self.end_date, self.limit = self.client.listen(sql.format(self.res[i][0]), 1)[0]
            self.date_now = datetime.datetime.now()
            with open('sql/Part 6.sql', mode='r', encoding='utf-8') as f:
                sql = f.read()
            self.name = self.client.listen(sql.format(self.res[i][0]), 1)[0]
            self.name = list(map(str, self.name))
            self.name = '  '.join(self.name)
            custom_font = QFont('Arial', 14)
            self.label = QLabel()
            self.label_2 = QLabel()
            self.label.setFont(custom_font)
            self.label_2.setFont(custom_font)
            self.label_2.setAlignment(Qt.AlignRight)
            self.label_2.setAlignment(Qt.AlignVCenter)
            self.label.setMargin(40)
            self.label.setIndent(20)
            self.label_2.setIndent(170)
            item_layout.addWidget(self.label)
            item_layout.addWidget(self.label_2)
            sql = "SELECT done FROM Test_for_student WHERE id_test={0} AND id_student={1}"
            self.done = self.client.listen(sql.format(self.res[i][0], self.id_student), 1)[0][0]
            if self.done == 0 and (self.limit == 0 or (datetime.datetime.strptime(self.end_date, '%Y-%m-%d %H:%M') > self.date_now > datetime.datetime.strptime(self.start_date, '%Y-%m-%d %H:%M'))):
                self.btn = QPushButton()
                self.btn.setFont(QFont('Arial', 14))
                self.btn.setObjectName(f'{self.res[i][0]}')
                self.btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
                self.group.addButton(self.btn)
                self.btn.setText('Начать тест')
                item_layout.addWidget(self.btn)
            else:
                sql = "SELECT checked FROM Students_answers WHERE id_test={0} AND id_student={1} AND checked = 0"
                self.all_done = self.client.listen(sql.format(self.res[i][0], self.id_student), 1)
                print(self.res[i][0], self.all_done)
                if not self.all_done:
                    sql = "SELECT mark FROM Test_for_student WHERE id_test={0} and id_student={1}"
                    self.mark = self.client.listen(sql.format(self.res[i][0], self.id_student), 1)[0][0]
                    self.label_2.setText(f'Ваш балл: {self.mark}')
                elif not self.done or self.done == 0:
                    self.label_2.setText('Вы не успели написать данный тест')
                else:
                    self.label_2.setText('Ваша работа проверяется')
            self.label.setText(self.name)
            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, item_widget)
        self.group.buttonClicked.connect(self.begin_test)
        self.btn_update.clicked.connect(self.update_page)
    
    def begin_test(self, button):
        name = button.objectName()
        self.doing_test_win = DoingTest(name, self.id_student, self.client)
        self.doing_test_win.show()
    
    def update_page(self):
        self.list.clear()
        self.create_table(self.id_student)
