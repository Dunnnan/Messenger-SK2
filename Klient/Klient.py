from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import traceback
import socket
import threading
import struct
import time

server_address = "127.0.0.2"
server_port = 1100

class Message:
    def __init__(self,flag):
        self.flag = flag

    def to_bytes(self):
        return struct.pack("i",self.flag)

def receive_message(client_socket):
    client_socket.settimeout(1)
    while True:
        try:
            mess = client_socket.recv(1024).decode('utf-8',errors='replace') #char
            if mess:
                print(f"Server: {mess}")
                return mess
            else:
                print("Server disconnected")
                break
        except socket.timeout:
            print("Receiving message timed out")
            break
        except Exception as e:
            print(f"An error occured while receiving message: {e}")
            break

def send_to_server(client_socket,data):
    for i in data:
        client_socket.sendall(i.encode('utf-8'))



# Klasy Worker i WorkerSignals
class WorkerSignals(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()


class signin(object):
    
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(266, 393)
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(70, 30, 131, 91))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setScaledContents(False)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")

        self.lineEdit = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit.setGeometry(QtCore.QRect(60, 130, 131, 31))
        self.lineEdit.setText("")
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit.setClearButtonEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.returnPressed.connect(self.login)  # Reakcja na Enter

        self.lineEdit_2 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(60, 180, 131, 31))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_2.setObjectName("haslo")
        self.lineEdit_2.returnPressed.connect(self.login)  # Reakcja na Enter

        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(80, 230, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.login)

        self.lineEdit_3 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_3.setGeometry(QtCore.QRect(80, 310, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setAutoFillBackground(False)
        self.lineEdit_3.setStyleSheet("background-color:rgba(255, 255, 255, 0)")
        self.lineEdit_3.setFrame(False)
        self.lineEdit_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")

        self.pushButton_2 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_2.setGeometry(QtCore.QRect(80, 340, 81, 24))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.signup)

        self.lineEdit_4 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(71, 280, 90, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setAutoFillBackground(False)
        self.lineEdit_4.setStyleSheet("background-color:rgba(255, 255, 255, 0);\n"
"color:rgba(255, 0, 0, 255)")
        self.lineEdit_4.setFrame(False)
        self.lineEdit_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.threadpool = QThreadPool()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Messenger", "Messenger"))
        self.label.setText(_translate("Form", "Zaloguj się"))
        self.lineEdit.setPlaceholderText(_translate("Form", "Nick"))
        self.lineEdit_2.setPlaceholderText(_translate("Form", "Hasło"))
        self.pushButton.setText(_translate("Form", "Zaloguj się"))
        self.lineEdit_3.setText(_translate("Form", "Nie masz konta?"))
        self.pushButton_2.setText(_translate("Form", "Utwórz konto"))
        self.lineEdit_4.setText(_translate("Form", ""))
    
    def login(self):
        self.nick = self.lineEdit.text()
        password = self.lineEdit_2.text()
        print(f"Nick: {self.nick}, Hasło: {password}")

        data = (self.nick, password)
        self.run_thread(self.send_to_server, data)
        self.run_thread(self.receive_message)

    def signup(self):
        # Zamykamy obecne okno
        open_windows=QApplication.topLevelWidgets()
        for i in open_windows:
            i.close()
        # Tworzymy nowe okno i je wyświetlamy
        self.window = QtWidgets.QWidget()  # Stwórz nowe okno
        self.ui = signup(Form)  # Utwórz obiekt klasy signup
        self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
        self.window.show()  # Pokaż nowe okno

        open_windows=QApplication.topLevelWidgets()
        for i in open_windows:
            print(i)

    def send_to_server(self, data):
        try:
            flag=200
            client_socket.send(struct.pack("i",flag))
            print(data)
            client_socket.send(data[0].encode('utf-8'))
            time.sleep(1)
            client_socket.send(data[1].encode('utf-8'))
                
            return "Message sent."
        except Exception as e:
            return f"Error send: {str(e)}"

    def receive_message(self):
        try:
            response = client_socket.recv(4)
            response=struct.unpack('<i', response)[0]
            return response
        except Exception as e:
            return f"Error recv: {str(e)}, {response}\n"
        
    def run_thread(self, function, *args):
        worker = Worker(function, *args)
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def handle_result(self, result):
        if result!=230:
            _translate = QtCore.QCoreApplication.translate
            self.lineEdit_4.setText(_translate("Form", "Niepoprawne dane!"))
        else:
            open_windows=QApplication.topLevelWidgets()
            for i in open_windows:
                i.close()
            flag=500
            client_socket.send(struct.pack("i",flag))
            client_socket.send(self.nick.encode('utf-8'))
            rec=client_socket.recv(1024)
            print(rec.decode())

    def handle_error(self, error):
        print(f"Error: {error[1]}")


class signup(object):
    def __init__(self, Form):
        self.Form = Form  # Zapisujemy Form, aby móc zamknąć okno

    def setupUi(self, Form):
        Form.setObjectName("Sign up")
        Form.resize(266, 393)
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(50, 0, 161, 91))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setScaledContents(False)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")

        self.lineEdit = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit.setGeometry(QtCore.QRect(60, 100, 131, 31))
        self.lineEdit.setText("")
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit.setClearButtonEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.returnPressed.connect(self.signup_action)  # Reakcja na Enter

        self.lineEdit_2 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(60, 150, 131, 31))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit_2.setClearButtonEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.returnPressed.connect(self.signup_action)  # Reakcja na Enter

        self.lineEdit_3 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_3.setGeometry(QtCore.QRect(60, 200, 131, 31))
        self.lineEdit_3.setText("")
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit_3.setClearButtonEnabled(False)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.returnPressed.connect(self.signup_action)  # Reakcja na Enter

        self.lineEdit_4 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(60, 250, 131, 31))
        self.lineEdit_4.setText("")
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_4.setClearButtonEnabled(False)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_4.returnPressed.connect(self.signup_action)  # Reakcja na Enter

        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(80, 320, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.signup_action)

        self.lineEdit_5 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_5.setGeometry(QtCore.QRect(60, 285, 150, 31))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        self.lineEdit_5.setFont(font)
        self.lineEdit_5.setAutoFillBackground(False)
        self.lineEdit_5.setStyleSheet("background-color:rgba(255, 255, 255, 0);\n"
"color:rgba(255, 0, 0, 255)")
        self.lineEdit_5.setFrame(False)
        self.lineEdit_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName("lineEdit_5")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.threadpool = QThreadPool()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "App"))
        self.label.setText(_translate("Form", "Utwórz konto"))
        self.lineEdit.setPlaceholderText(_translate("Form", "Imię"))
        self.lineEdit_2.setPlaceholderText(_translate("Form", "Nazwisko"))
        self.lineEdit_3.setPlaceholderText(_translate("Form", "Nazwa użytkownika"))
        self.lineEdit_4.setPlaceholderText(_translate("Form", "Hasło"))
        self.pushButton.setText(_translate("Form", "Utwórz konto"))
        self.lineEdit_5.setText(_translate("Form", ""))

    def signup_action(self):
        print("Zarejestrowano")
        imie = self.lineEdit.text()
        nazwisko = self.lineEdit_2.text()
        username = self.lineEdit_3.text()
        password = self.lineEdit_4.text()
        print(f"Imię: {imie}, Nazwisko: {nazwisko}, Nazwa użytkownika: {username}, Hasło: {password}")

        data = (imie, nazwisko,username,password)
        self.run_thread(self.send_to_server, data)
        self.run_thread(self.receive_message)

    def send_to_server(self, data):
        try:
            flag=100
            client_socket.send(struct.pack("i",flag))
            print(data)
            client_socket.send(data[0].encode('utf-8'))
            time.sleep(1)
            client_socket.send(data[1].encode('utf-8'))
            time.sleep(1)
            client_socket.send(data[2].encode('utf-8'))
            time.sleep(1)
            client_socket.send(data[3].encode('utf-8'))
                
            return "Message sent."
        except Exception as e:
            return f"Error send: {str(e)}"

    def receive_message(self):
        try:
            response = client_socket.recv(4)
            response=struct.unpack('<i', response)[0]
            return response
        except Exception as e:
            return f"Error recv: {str(e)}, {response}\n"
        
    def run_thread(self, function, *args):
        worker = Worker(function, *args)
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def handle_result(self, result):

        if result==120:
            open_windows=QApplication.topLevelWidgets()
            for i in open_windows:
                i.close()
            # Tworzymy nowe okno i je wyświetlamy
            self.window = QtWidgets.QWidget()  # Stwórz nowe okno
            self.ui = signin()  # Utwórz obiekt klasy signup
            self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
            self.window.show()  # Pokaż nowe okno
        else:
            _translate = QtCore.QCoreApplication.translate
            self.lineEdit_5.setText(_translate("Form", "Podany użytkownik już istnieje!"))
        

    def handle_error(self, error):
        print(f"Error: {error[1]}")

import sys

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    client_socket.connect((server_address,server_port))
    print("Connected!")
except Exception as e:
    print("Could not connect to the server", e)
    socket.close(client_socket)
    exit()



app = QtWidgets.QApplication(sys.argv)
Form = QtWidgets.QWidget()
ui = signin()
ui.setupUi(Form)
Form.show()
app.exec()
