from Sign_in import signin
from PyQt6 import QtWidgets
from PyQt6 import QtCore

import socket
import struct
import sys

server_address = "127.0.0.1"
server_port = 1100

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    client_socket.connect((server_address,server_port))
except Exception as e:
    print("Could not connect to the server", e)
    socket.close(client_socket)
    exit()

def disconnect():
    try:
        flag = -1
        if client_socket:
            client_socket.send(struct.pack("i", flag))
            client_socket.close()
        print("Disconnected from the server.")
    except Exception:
        pass


thread_pool = QtCore.QThreadPool.globalInstance()
thread_pool.setMaxThreadCount(1)

app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(lambda: disconnect())
Form = QtWidgets.QWidget()
ui = signin(Form,client_socket)
ui.setupUi(Form)
Form.show()
app.exec()
