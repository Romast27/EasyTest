from socket import *
import sqlite3
import json


class Server:
    def __init__(self, ip, port):
        print(f'SERVER IP: {ip}\nSERVER PORT: {port}')
        self.db_name = 'project_db.sqlite'
        self.con = sqlite3.connect(self.db_name)
        self.cursors = {}
        self.ser = socket(AF_INET, SOCK_STREAM)
        self.ser.bind((ip, port))
        self.ser.listen(30)
        self.start_server()

    def sender(self, user, text):
        user.send(text.encode('utf-8'))

    def start_server(self):
        while True:
            user, addr = self.ser.accept()
            print(f'CLIENT CONNECTED: {user}\nIP: {addr[0]}\nPORT: {addr[1]}')
            self.listen(user)

    def listen(self, user):
        if self.cursors.get(user, None) is not None:
            cur = self.cursors.get(user)
        else:
            cur = self.con.cursor()
            self.cursors[user] = cur
        self.sender(user, 'YOU ARE CONNECTED!')
        is_work = True

        while is_work:
            try:
                data = user.recv(8192)
                self.sender(user, 'getted')
            except Exception as e:
                data = ''
                is_work = False

            if len(data) > 0:
                msg = json.loads(data.decode('utf-8'))
                type_req = msg["type_req"]
                msg = msg["req"]

                try:
                    print(msg)
                    if type_req == 1:
                        answer = [x for x in cur.execute(msg)]
                    elif type_req == 2:
                        answer = cur.executescript(msg)
                        answer = 'No answer'
                    error = ''
                except Exception as e:
                    error = e
                    print(e)
                    answer = ''

                self.con.commit()
                ans = json.dumps({'answer': answer, 'error': error})
                self.sender(user, ans)
            data = ''
            msg = ''


Server(input('Type server IP: '), 8000)
