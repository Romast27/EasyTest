import sys
import sqlite3
import datetime


from PyQt5 import uic, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QTableWidgetItem, QComboBox, QTableWidget, QRadioButton, QSpacerItem, QSpinBox, QAbstractItemView
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt


def set_style_combobox(item):
    item.setStyleSheet("""QComboBox{
        background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #4287ff, stop: 1 #356ccc);
        color: #fff;
        border-style: solid;
        font: 12pt "Arial";
        font-weight: bold;
        border: 1px solid #3873d9;
        selection-background-color: #ccdfff;}
     QComboBox::drop-down{
        border: none;
        selection-background-color: #4287ff;
        color: #000;
        font: 12pt "Arial";
        font-weight: bold;
        padding: 0px;}
     QComboBox::down-arrow {
        border : 4px black;
        image: url(arrow(4));}""")


class CreatingQuestions(QMainWindow):
    def __init__(self, client):
        super().__init__()
        uic.loadUi('.\\Ui\\CreatingQuestions.ui', self)
        self.client = client
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        sql = "SELECT DISTINCT theme FROM Questions"
        self.themes = self.client.listen(sql, 1)
        for item in self.themes:
            self.combobox.addItem(item[0])
        sql = "SELECT MAX(id_question) FROM Questions"
        self.id_question = self.client.listen(sql, 1)[0][0]
        if self.id_question is None:
            self.id_question = 1
        else:
            self.id_question += 1
        self.id_answer = 1
        self.rows = 1
        self.table_answers.setRowCount(self.rows)
        self.item = QComboBox(self.table_answers)
        set_style_combobox(self.item)
        self.item.addItem('Да')
        self.item.addItem('Нет')
        self.table_answers.setCellWidget(self.rows-1, 1, self.item)
        self.sp_1 = QSpacerItem(20, 100)
        self.sp_2 = QSpacerItem(20, 110)
        self.radio_variants.setChecked(True)
        self.table_answers.setHorizontalHeaderLabels(['Ответ', 'Правильность (да или нет)'])
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.showMaximized()
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;}
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
            color: #333;}""")
        self.btn_add_answer.clicked.connect(self.add_answer)
        self.btn_delete_answer.clicked.connect(self.delete_answer)
        self.btn_save.clicked.connect(self.save_result)
        self.btn_next.clicked.connect(self.next_window)
        self.btn_end.clicked.connect(self.end_variant)
        self.radio_variants.toggled.connect(self.change)
    
    def change(self):
        if self.radio_variants.isChecked():
            self.layout.removeItem(self.sp_1)
            self.table_answers.show()
            self.btn_delete_answer.show()
            self.btn_add_answer.show()
            self.layout.addItem(self.sp_2, 9, 2)
        else:
            self.table_answers.hide()
            self.btn_delete_answer.hide()
            self.btn_add_answer.hide()
            self.layout.addItem(self.sp_1, 9, 2)
    
    def add_answer(self):
        self.rows += 1
        self.table_answers.setRowCount(self.rows)
        self.item = QComboBox(self.table_answers)
        set_style_combobox(self.item)
        self.item.addItem('Да')
        self.item.addItem('Нет')
        self.table_answers.setCellWidget(self.rows-1, 1, self.item)
    
    def delete_answer(self):
        if self.rows > 1:
            index = self.table_answers.selectedItems()[0].row()
            self.rows -= 1
            self.table_answers.removeRow(index)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка\nНельзя удалить все ответы из таблицы")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

    def save_result(self):
        if self.radio_variants.isChecked():
            if self.edit_question.toPlainText() == '' or self.combobox.currentText() == '':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка\nВведите вопрос")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            else:
                sql = "INSERT INTO Questions(id_question, question, manual_check, theme) VALUES({0}, '{1}', {2}, '{3}')".format(self.id_question, self.edit_question.toPlainText(), False, self.combobox.currentText())
                self.client.listen(sql, 2)
            rows = self.table_answers.rowCount()
            for row in range(rows):
                if not self.table_answers.itemAt(row, 0).text() in ('', None):
                    answer = self.table_answers.item(row, 0).text()
                    correctness = self.table_answers.cellWidget(row, 1).currentText()
                    if correctness == 'Да':
                        correctness = True
                    else:
                        correctness = False
                    sql = "INSERT INTO Answers(id_question, id_answer, answer, correctness) VALUES({0}, {1}, '{2}', {3})".format(self.id_question, row + 1, answer, correctness)
                    self.client.listen(sql, 2)
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка\nНеправильный ввод ответа")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    return
        else:
            question = self.edit_question.toPlainText()
            sql = "INSERT INTO Questions(id_question, question, manual_check, theme) VALUES({0}, '{1}', {2}, '{3}')".format(self.id_question, question, True, self.combobox.currentText())
            self.client.listen(sql, 2)
        
    def next_window(self):
        self.close()
        self.creating_question = CreatingQuestions(self.client)
        self.creating_question.show()
    
    def end_variant(self):
        self.close()


class CreatingTest(QMainWindow):
    def __init__(self, client):
        super().__init__()
        uic.loadUi('.\\Ui\\CreatingTest.ui', self)
        self.creating_questions = None
        self.client = client
        self.id_test = self.client.listen("SELECT MAX(id_test) FROM Tests", 1)[0][0]
        if self.id_test is None:
            self.id_test = 1
        else:
            self.id_test += 1
        self.themes = self.client.listen("SELECT DISTINCT theme FROM Questions", 1)
        for item in self.themes:
            self.combobox_theme.addItem(item[0])
        self.classes = self.client.listen("SELECT name_class FROM Classes", 1)
        for item in self.classes:
            self.combobox_class.addItem(item[0])
        self.label.setText(f'Тест №{self.id_test}')
        self.sp_1 = QSpacerItem(20, 110)
        self.sp_2 = QSpacerItem(20, 110)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;}
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
        QComboBox{
            background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);
            color: #fff;
            border-style: solid;
            border: 1px solid #3873d9;
            selection-background-color: #ccdfff;}
         QComboBox::drop-down{
            border: none;
            selection-background-color: #4287ff;
            color: #000;
            font-weight: bold;
            padding: 0px;}
         QComboBox::down-arrow{
            border : 4px black;
            image: url(arrow(1));}""")
        self.showMaximized()
        self.btn_next.clicked.connect(self.next_window)
        self.cb_limit_datetime.toggled.connect(self.change)

    def change(self):
        if self.cb_limit_datetime.checkState() == 0:
            self.label_3.hide()
            self.label_4.hide()
            self.layout.addItem(self.sp_1, 8, 2)
            self.layout.addItem(self.sp_2, 9, 2)
            self.edit_start_datetime.hide()
            self.edit_end_datetime.hide()
        else:
            self.layout.removeItem(self.sp_1)
            self.layout.removeItem(self.sp_2)
            self.label_3.show()
            self.label_4.show()
            self.edit_start_datetime.show()
            self.edit_end_datetime.show()

    def next_window(self):
        theme_test = self.combobox_theme.currentText()
        class_ = self.combobox_class.currentText()
        class_ = self.client.listen("SELECT id_class FROM Classes WHERE name_class='{0}'".format(class_), 1)[0][0]
        num_questions = self.spinbox.value()
        if num_questions >= self.client.listen("SELECT COUNT(*) FROM Questions WHERE theme='{0}'".format(theme_test), 1)[0][0]:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка\nКоличество выбранных вопросов больше чем количество составленных вопросов")
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open('sql/Part 1.sql', mode='r', encoding='utf-8') as f:
            script = f.read()
            script = script.format(str(class_), f"'{theme_test}'")
            self.client.listen(script, 2)
        if self.cb_limit_datetime.checkState() == 0:
            num_work = self.client.listen("SELECT COUNT(*) FROM Tests WHERE type_work=1", 1)[0][0] + 1
            sql = "INSERT INTO Tests(id_test, date_of_creature, id_class, type_work, num_work) VALUES({0}, '{1}', {2}, 1, {3})".format(self.id_test, date_now, class_, num_work)
            self.client.listen(sql, 2)
            sql = "INSERT INTO Test_info(id_test, theme, num_questions) VALUES({0}, '{1}', {2})".format(self.id_test, theme_test, num_questions)
            self.client.listen(sql, 2)
        else:
            start_datetime = self.edit_start_datetime.dateTime().toString('yyyy-MM-dd hh:mm')
            end_datetime = self.edit_end_datetime.dateTime().toString('yyyy-MM-dd hh:mm')
            st_date = self.edit_start_datetime.dateTime()
            st_date = datetime.datetime(st_date.date().year(), st_date.date().month(), st_date.date().day(), st_date.time().hour(), st_date.time().minute())
            end_date = self.edit_end_datetime.dateTime()
            end_date = datetime.datetime(end_date.date().year(), end_date.date().month(), end_date.date().day(), end_date.time().hour(), end_date.time().minute())
            if not end_date > st_date:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка\nНеправильный ввод время")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            num_work = self.client.listen("SELECT COUNT(*) FROM Tests WHERE type_work=1", 1)[0][0] + 1
            sql = "INSERT INTO Tests(id_test, date_of_creature, limit_time, starting_date, ending_date, id_class, type_work, num_work) VALUES({0}, '{1}', 1, '{2}', '{3}', {4}, 1, {5})".format(self.id_test, date_now, start_datetime, end_datetime, class_, num_work)
            self.client.listen(sql, 2)
            sql = "INSERT INTO Test_info(id_test, theme, num_questions) VALUES({0}, '{1}', {2})".format(self.id_test, theme_test, num_questions)
            self.client.listen(sql, 2)
        students = self.client.listen("SELECT DISTINCT id_student FROM Students_class WHERE id_class={0}".format(class_), 1)
        with open('sql/Part 21.sql', mode='r', encoding='utf-8') as f:
            script = f.read()
            iteration = 1
            for student in students:
                self.client.listen("INSERT INTO Test_for_student(id_test, id_student) VALUES({0}, {1})".format(self.id_test, student[0]), 2)
                self.client.listen(script.format(num_questions, student[0], iteration, self.id_test), 2)
                delta = self.client.listen("""SELECT count(*) FROM temp_result_table 
INNER JOIN 
[temp]._Variables AS _Variables ON temp_result_table.id_student = _Variables.IdUser;""", 1)[0][0]
                print(delta)
                delta = num_questions - delta
                if delta > 0:
                    iteration += 1
                    self.client.listen(script.format(delta, student[0], iteration, self.id_test), 2)
        with open('sql/Part 3.sql', mode='r', encoding='utf-8') as f:
            script = f.read()
            script = script.format(self.id_test)
            self.client.listen(script, 2)
        self.combobox_theme.clear()
        self.close()


class CreatingControl(QMainWindow):
    def __init__(self, client):
        super().__init__()
        uic.loadUi('.\\Ui\\CreatingControl.ui', self)
        self.font = QFont('Arial', 12)
        self.font.setBold(True)
        self.creating_questions = None
        self.client = client
        self.rows = 1
        self.id_test = self.client.listen("SELECT MAX(id_test) FROM Tests", 1)[0][0]
        if self.id_test is None:
            self.id_test = 1
        else:
            self.id_test += 1
        self.table.setHorizontalHeaderLabels(["Тема", "Количество вопросов"])
        self.table.horizontalHeader().setFont(self.font)
        self.table.setColumnWidth(0, 460)
        self.table.setColumnWidth(1, 208)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.themes = self.client.listen("SELECT DISTINCT theme FROM Questions", 1)
        self.combobox_theme = QComboBox(self.table)
        self.combobox_theme.setFont(self.font)
        self.spinbox = QSpinBox(self.table)
        self.spinbox.setFont(self.font)
        self.table.setCellWidget(self.rows - 1, 0, self.combobox_theme)
        self.table.setCellWidget(self.rows - 1, 1, self.spinbox)
        for item in self.themes:
            self.combobox_theme.addItem(item[0])
        self.classes = self.client.listen("SELECT name_class FROM Classes", 1)
        for item in self.classes:
            self.combobox_class.addItem(item[0])
        self.label.setText(f'Контрольная работа №{self.id_test}')
        self.sp_1 = QSpacerItem(20, 110)
        self.sp_2 = QSpacerItem(20, 110)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;}
        QPushButton {
           padding:4px;
           color: #fff;
           font-weight: bold;
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
           font-weight: bold;}
        QHeaderView::section:horizontal {
            color: #fff;
            border-style: solid;
            font-weight: bold;
            background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);}
        QTableView {
            border-grid: 3px;
            border-top-color: #4287ff;
            border-radius: 4px;
            font-weight: bold;
            background-color: #fff;
            gridline-color: #ccc;
            selection-background-color: #ccdfff;
            color: #333;}
        QComboBox{
            background-color: qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4287ff, stop: 1 #356ccc);
            color: #fff;
            font-weight: bold;
            border-style: solid;
            border: 1px solid #3873d9;
            selection-background-color: #ccdfff;}
         QComboBox::drop-down{
            border: none;
            selection-background-color: #4287ff;
            color: #000;
            font-weight: bold;
            padding: 0px;}
         QComboBox::down-arrow{
            border : 4px black;
            image: url(arrow(1));}""")
        self.showMaximized()
        self.btn_next.clicked.connect(self.next_window)
        self.cb_limit_datetime.toggled.connect(self.change)
        self.btn_delete_row.clicked.connect(self.delete_row)
        self.btn_add_row.clicked.connect(self.add_row)

    def delete_row(self):
        if self.rows > 1:
            index = self.table.currentRow()
            self.rows -= 1
            self.table.removeRow(index)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка\nНельзя удалить все ответы из таблицы")
            msg.setWindowTitle("Error")
            msg.exec_()
            return
    
    def add_row(self):
        self.rows += 1
        self.table.setRowCount(self.rows)
        self.combobox_theme = QComboBox(self.table)
        self.combobox_theme.setFont(self.font)
        self.spinbox = QSpinBox(self.table)
        self.spinbox.setFont(self.font)
        self.table.setCellWidget(self.rows - 1, 0, self.combobox_theme)
        self.table.setCellWidget(self.rows - 1, 1, self.spinbox)
        for item in self.themes:
            self.combobox_theme.addItem(item[0])

    def change(self):
        if self.cb_limit_datetime.checkState() == 0:
            self.label_3.hide()
            self.label_4.hide()
            self.layout.addItem(self.sp_1, 8, 2)
            self.layout.addItem(self.sp_2, 9, 2)
            self.edit_start_datetime.hide()
            self.edit_end_datetime.hide()
        else:
            self.layout.removeItem(self.sp_1)
            self.layout.removeItem(self.sp_2)
            self.label_3.show()
            self.label_4.show()
            self.edit_start_datetime.show()
            self.edit_end_datetime.show()

    def next_window(self):
        class_ = self.combobox_class.currentText()
        class_ = self.client.listen("SELECT id_class FROM Classes WHERE name_class='{0}'".format(class_), 1)[0][0]
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        students = self.client.listen("SELECT DISTINCT id_student FROM Students_class WHERE id_class={0}".format(class_), 1)
        if self.cb_limit_datetime.checkState() == 0:
            num_work = self.client.listen("SELECT COUNT(*) FROM Tests WHERE type_work=2", 1)[0][0] + 1
            sql = "INSERT INTO Tests(id_test, date_of_creature, id_class, type_work, num_work) VALUES({0}, '{1}', {2}, 2, {3})".format(self.id_test, date_now, class_, num_work)
            self.client.listen(sql, 2)
        else:
            start_datetime = self.edit_start_datetime.dateTime().toString('yyyy-MM-dd hh:mm')
            end_datetime = self.edit_end_datetime.dateTime().toString('yyyy-MM-dd hh:mm')
            st_date = self.edit_start_datetime.dateTime()
            st_date = datetime.datetime(st_date.date().year(), st_date.date().month(), st_date.date().day(), st_date.time().hour(), st_date.time().minute())
            end_date = self.edit_end_datetime.dateTime()
            end_date = datetime.datetime(end_date.date().year(), end_date.date().month(), end_date.date().day(), end_date.time().hour(), end_date.time().minute())
            if not end_date > st_date:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка\nНеправильный ввод время")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            num_work = self.client.listen("SELECT COUNT(*) FROM Tests WHERE type_work=2", 1)[0][0] + 1
            sql = "INSERT INTO Tests(id_test, date_of_creature, limit_time, starting_date, ending_date, id_class, type_work, num_work) VALUES({0}, '{1}', 1, '{2}', '{3}', {4}, 2, {5})".format(self.id_test, date_now, start_datetime, end_datetime, class_, num_work)
            self.client.listen(sql, 2)
        with open('sql/Part 1.sql', mode='r', encoding='utf-8') as f:
            script_1 = f.read()
        with open('sql/Part 2.sql', mode='r', encoding='utf-8') as f:
            script_2 = f.read()
        with open('sql/Part 3.sql', mode='r', encoding='utf-8') as f:
            script_3 = f.read()
            script_3 = script_3.format(self.id_test)
        for row in range(self.rows):
            iteration = 1
            num_questions = self.table.cellWidget(row, 1).value()
            theme = self.table.cellWidget(row, 0).currentText()
            sql = "INSERT INTO Test_info(id_test, theme, num_questions) VALUES({0}, '{1}', {2})".format(self.id_test, theme, num_questions)
            self.client.listen(sql, 2)
            script = script_1.format(str(class_), f"'{theme}'")
            self.client.listen(script, 2)
            if num_questions >= self.client.listen("SELECT COUNT(*) FROM Questions WHERE theme='{0}'".format(theme), 1)[0][0]:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка\nКоличество выбранных вопросов больше чем количество составленных вопросов")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            for student in students:
                if row == 0:
                    self.client.listen("INSERT INTO Test_for_student(id_test, id_student) VALUES({0}, {1})".format(self.id_test, student[0]), 2)
                self.client.listen(script_2.format(num_questions, student[0], iteration, self.id_test), 2)
                delta = self.client.listen("""SELECT count(*) FROM temp_result_table 
INNER JOIN 
[temp]._Variables AS _Variables ON temp_result_table.id_student = _Variables.IdUser;""", 1)[0][0]
                delta = num_questions - delta
                if delta > 0:
                    iteration += 1
                    self.client.listen(script_2.format(delta, student[0], iteration, self.id_test), 2)
            self.client.listen(script_3, 2)
        self.combobox_theme.clear()
        self.close()


class CheckingAnswers(QMainWindow):
    def __init__(self, client):
        super().__init__()
        uic.loadUi('.\\Ui\\CheckingAnswers.ui', self)
        self.showMaximized()
        self.client = client
        self.i = 0
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;}
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
                                               stop: 0 #4287ff, stop: 1 #356ccc);}
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
            selection-background-color: #4287ff;
            color: #000;
            font-weight: bold;
            padding: 0px;}
         QComboBox::down-arrow{
            border : 4px black;
            image: url(arrow);}""")        
        sql = "SELECT id_test, id_question, answer, id_student FROM Students_answers " \
                   "WHERE manual_check = 1 AND checked = 0 AND answer IS NOT NULL"
        self.answers = self.client.listen(sql, 1)
        self.btn_save.clicked.connect(self.save_result)
        self.btn_end.clicked.connect(self.ending_test)
        self.creating_question()
        
    def creating_question(self):
        if self.answers is not None and self.i < len(self.answers):
            self.label.setText(f'Тест №{self.answers[self.i][0]}')
            sql = "SELECT question FROM Questions WHERE id_question={0}".format(self.answers[self.i][1])
            self.question = self.client.listen(sql, 1)[0][0]
            self.answer = self.answers[self.i][2]
            self.line_question.setText(self.question)
            self.line_answer.setText(self.answer)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Вы проверили все ответы")
            msg.setWindowTitle("Завершение")
            msg.exec_()
            self.close()
        
    def save_result(self):
        id_student = self.answers[self.i][3]
        id_test = self.answers[self.i][0]
        id_question = self.answers[self.i][1]
        sql = "UPDATE Students_answers SET checked=1, correctness={0} " \
              "WHERE id_student={1} AND id_test={2} AND id_question={3}".format(str(self.radio_true.isChecked()), id_student, id_test, id_question)        
        self.client.listen(sql, 2)
        sql = "SELECT checked FROM Students_answers WHERE id_test={0} AND id_student={1} AND checked=0".format(id_test, id_student)
        if not self.client.listen(sql, 1):
            sql = "SELECT COUNT(*) FROM Students_answers WHERE id_test={0} AND id_student={1} AND correctness=1".format(id_test, id_student)
            mark = self.client.listen(sql, 1)
            sql = "UPDATE Test_for_student SET mark={0} WHERE id_student={1} AND id_test={2}".format(mark[0][0], id_student, id_test)
            self.client.listen(sql, 2)
        self.i += 1
        self.creating_question()
    
    def ending_test(self):
        self.close()


class MainWindowTeacher(QMainWindow):
    def __init__(self, username, id, client):
        super().__init__()
        self.username = username
        self.client = client
        uic.loadUi('.\\Ui\\MainWindowTeacher.ui', self)
        self.label.setText(self.username)
        self.showMaximized()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)    
        self.setStyleSheet("""
        QMainWindow {
           background-image: url(background);
           background-size: cover;}
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
            selection-background-color: #4287ff;
            color: #000;
            font-weight: bold;
            padding: 0px;}
         QComboBox::down-arrow{
            border : 4px black;
            image: url(arrow);}""")

# Test table

        self.table_test.setColumnCount(4)
        self.table_test.setHorizontalHeaderLabels(["Тема", "Дата создания", "Начало работы", "Конец работы"])
        if self.client.listen("SELECT COUNT(*) FROM Tests", 1):
            with open('sql/Part 4.sql', mode='r', encoding='utf-8') as f:
                sql = f.read()
            info = self.client.listen(sql, 1)
            for i in info:
                rows = self.table_test.rowCount()
                self.table_test.setRowCount(rows + 1)
                self.table_test.setItem(rows, 0, QTableWidgetItem(i[4]))
                self.table_test.setItem(rows, 1, QTableWidgetItem(i[1]))
                if i[2] is None:
                    self.table_test.setItem(rows, 2, QTableWidgetItem('Не указано'))
                    self.table_test.setItem(rows, 3, QTableWidgetItem('Не указано'))
                else:
                    self.table_test.setItem(rows, 2, QTableWidgetItem(i[2]))
                    self.table_test.setItem(rows, 3, QTableWidgetItem(i[3]))
        self.table_test.setColumnWidth(0, 430)
        self.table_test.setColumnWidth(1, 150)
        self.table_test.setColumnWidth(2, 150)
        self.table_test.setColumnWidth(3, 150)
        self.table_test.verticalHeader().setVisible(False)
        self.table_question.resizeRowsToContents()

# Result table

        self.table_result.setColumnCount(3)
        self.table_result.setHorizontalHeaderLabels(["Тема", "Ученик", "Оценка"])
        if self.client.listen("SELECT COUNT(*) FROM Tests", 1):
            with open('sql/Part 5.sql', mode='r', encoding='utf-8') as f:
                sql = f.read()
            info = self.client.listen(sql, 1)
            for item in info:
                rows = self.table_result.rowCount()
                self.table_result.setRowCount(rows + 1)
                self.table_result.setItem(rows, 0, QTableWidgetItem(item[1]))
                self.table_result.setItem(rows, 1, QTableWidgetItem(item[2]))
                self.table_result.setItem(rows, 2, QTableWidgetItem(str(item[3])))
        self.table_result.setColumnWidth(0, 430)
        self.table_result.setColumnWidth(1, 300)
        self.table_result.setColumnWidth(2, 150)
        self.table_result.verticalHeader().setVisible(False)
        self.table_question.resizeRowsToContents()

# Question table

        self.table_question.setColumnCount(3)
        self.table_question.setHorizontalHeaderLabels(["Номер", "Тема", "Вопрос"])
        sql = "SELECT id_question, theme, question FROM Questions"
        info = self.client.listen(sql, 1)
        for item in info:
            rows = self.table_question.rowCount()
            self.table_question.setRowCount(rows + 1)
            self.table_question.setItem(rows, 0, QTableWidgetItem(str(item[0])))
            self.table_question.setItem(rows, 1, QTableWidgetItem(item[1]))
            self.table_question.setItem(rows, 2, QTableWidgetItem(item[2]))
        self.table_question.setColumnWidth(0, 60)
        self.table_question.setColumnWidth(1, 200)
        self.table_question.setColumnWidth(2, 630)
        self.table_question.verticalHeader().setVisible(False)
        self.themes = self.client.listen("SELECT DISTINCT theme FROM Questions", 1)
        for item in self.themes:
            self.combobox_filter.addItem(item[0])
        self.table_question.resizeRowsToContents()

# Connect buttons

        self.btn_search.clicked.connect(self.find_theme)
        self.btn_delete_filter.clicked.connect(self.delete_filter)
        self.btn_create_test.clicked.connect(self.creating_test)
        self.btn_create_control.clicked.connect(self.creating_control)
        self.btn_check.clicked.connect(self.checking_test)
        self.btn_create_question.clicked.connect(self.creating_question)

    def find_theme(self):
        theme = self.combobox_filter.currentText()
        sql = "SELECT id_question, theme, question FROM Questions WHERE theme='{0}'".format(theme)
        self.table_question.setRowCount(0)
        info = self.client.listen(sql, 1)
        for i in info:
            rows = self.table_question.rowCount()
            self.table_question.setRowCount(rows + 1)
            self.table_question.setItem(rows, 0, QTableWidgetItem(str(i[0])))
            self.table_question.setItem(rows, 1, QTableWidgetItem(i[1]))
            self.table_question.setItem(rows, 2, QTableWidgetItem(i[2]))
    
    def delete_filter(self):
        self.table_question.setRowCount(0)
        sql = "SELECT id_question, theme, question FROM Questions"
        info = self.client.listen(sql, 1)
        for i in info:
            rows = self.table_question.rowCount()
            self.table_question.setRowCount(rows + 1)
            self.table_question.setItem(rows, 0, QTableWidgetItem(str(i[0])))
            self.table_question.setItem(rows, 1, QTableWidgetItem(i[1]))
            self.table_question.setItem(rows, 2, QTableWidgetItem(i[2]))
    
    def creating_test(self):
        self.creating_test = CreatingTest(self.client)
        self.creating_test.show()

    def creating_control(self):
        self.creating_control = CreatingControl(self.client)
        self.creating_control.show()

    def checking_test(self):
        self.checking_answers_win = CheckingAnswers(self.client)
        self.checking_answers_win.show()

    def creating_question(self):
        self.creating_questions = CreatingQuestions(self.client)
        self.creating_questions.show()
