import sys
import project_Authorize
import project_Teacher
import project_Student

from PyQt5.QtWidgets import QApplication

from socket import *
import json


class Client:
    def __init__(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect((ip, port))
        self.connect()

    def connect(self):
        try:
            msg = self.client.recv(1024).decode('utf-8')
        except Exception as e:
            print(f'ERROR: {e}')
            exit()

        if msg == 'YOU ARE CONNECTED!':
            return
        else:
            exit()

    def sender(self, text):
        self.client.send(text.encode('utf-8'))
        while self.client.recv(1024).decode('utf-8') != 'getted':
            self.client.send(text.encode('utf-8'))

    def listen(self, req, type_req):
        req = req.replace('\n', '')
        msg = json.dumps({'req': req, 'type_req': type_req})
        self.sender(msg)
        ans = self.client.recv(1000000)
        if ans == 'No answer':
            return
        data = json.loads(ans.decode('utf-8'))
        if data["error"] == "":
            res = data["answer"]
            return res


if __name__ == '__main__':
    app = QApplication(sys.argv)
    authorizing = project_Authorize.Authorize()
    authorizing.show()
    if not authorizing.exec_() and authorizing.authorized == 'teacher':
        client = Client(input('Type server IP: '), 8000)
        window_teacher = project_Teacher.MainWindowTeacher(authorizing.name, authorizing.id, client)
        #window_teacher = project_Teacher.MainWindowTeacher('ФИ Учителя', 1, client)
        window_teacher.show()
        authorizing.close()
    elif authorizing.authorized == 'student':
    #else:
        client = Client(input('Type server IP: '), 8000)
        window_student = project_Student.MainWindowStudent(authorizing.name, authorizing.id, client)
        #window_student = project_Student.MainWindowStudent('Ученик', 2, client)
        window_student.show()
        authorizing.close()
    sys.exit(app.exec_())
