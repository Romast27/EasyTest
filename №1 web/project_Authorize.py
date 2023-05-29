import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QDialog


class Authorize(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('.\\Ui\\Authorize.ui', self)
        self.authorized = None
        self.radio_student.setChecked(True)
        self.edit_password.setPlaceholderText('Не менее 8 символов')
        self.pushButton_enter.clicked.connect(self.enter_account)
        #self.pushButton_create.clicked.connect(self.create_account)
        self.con = sqlite3.connect("project_db.sqlite")
        self.cur = self.con.cursor()
        self.name = str()
        self.password = str()
        self.id = int()
        self.setStyleSheet("""
        QDialog {
           background-color: qlineargradient( x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 #ffe0c9, stop: 1 #b1ebff);}}
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
           background: #fff;}""")        

    def create_account(self):
        self.name = self.edit_login.text()
        self.password = self.edit_password.text()
        if len(self.password) < 8:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка\nНе правильный пароль")
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        if self.radio_student.isChecked():
            sql = "INSERT INTO Students(login_student, password) VALUES(?, ?)"
            self.cur.execute(sql, (self.name, self.password))
            self.authorized = 'student'
            sql = "SELECT id_student FROM Students WHERE login_student=?"
            self.id = self.cur.execute(sql, (self.name, )).fetchone()[0]
        else:
            sql = "INSERT INTO Teachers(name_teacher, password) VALUES(?, ?)"
            self.cur.execute(sql, (self.name, self.password))
            self.authorized = 'teacher'
        self.con.commit()
        self.con.close()
        self.close()

    def enter_account(self):
        self.name = self.edit_login.text()
        self.password = self.edit_password.text()
        if self.radio_student.isChecked():
            sql = "SELECT id_student FROM Students WHERE login_student=? AND password=?"
            info = self.cur.execute(sql, (self.name, self.password)).fetchall()
            if info:
                sql = "SELECT id_student FROM Students WHERE login_student=@log"
                self.id = self.cur.execute(sql, (self.name, )).fetchone()[0]
                self.authorized = 'student'
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка\nНеправильный логин или пароль")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
        else:
            sql = "SELECT id_teacher FROM Teachers WHERE name_teacher=? AND password=?"
            info = self.cur.execute(sql, (self.name, self.password)).fetchall()
            if info:
                self.authorized = 'teacher'
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка\nНеправильный логин или пароль")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
        self.close()
        self.con.close()
