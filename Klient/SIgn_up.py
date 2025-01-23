from Worker import Worker
from Sign_in import signin

from PyQt6 import QtCore, QtGui, QtWidgets

import struct
import time

class signup(object):

    # Inicjalizacja klasy
    def __init__(self,Form,client_socket):
        self.Form = Form
        self.client_socket = client_socket
        self.block=False

    # Inicjalizacja GUI
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

        self.lineEdit_2 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(60, 150, 131, 31))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit_2.setClearButtonEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.lineEdit_3 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_3.setGeometry(QtCore.QRect(60, 200, 131, 31))
        self.lineEdit_3.setText("")
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit_3.setClearButtonEnabled(False)
        self.lineEdit_3.setObjectName("lineEdit_3")

        self.lineEdit_4 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(60, 250, 131, 31))
        self.lineEdit_4.setText("")
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_4.setClearButtonEnabled(False)
        self.lineEdit_4.setObjectName("lineEdit_4")

        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(80, 320, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.signup_action)

        self.lineEdit_5 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_5.setGeometry(QtCore.QRect(0, 285, 266, 31))
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

        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)

    # Ustawienie początkowych wartości komórek
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

    # Obsługa rejestracji - przy poprawności danych --> rozpoczęcie tworzenia konta (serwer)
    def signup_action(self):

        imie = self.lineEdit.text()
        nazwisko = self.lineEdit_2.text()
        username = self.lineEdit_3.text()
        password = self.lineEdit_4.text()

        # Sprawdzenie czy nie ma pustych komórek
        if imie == "" or nazwisko == "" or username == "" or password == "":
            self.lineEdit_5.setText("Wszystkie pola muszą być wypełnione!")
            return
        else:
            self.lineEdit_5.setText("")

        max_length = 1024
        if len(imie) > max_length or len(nazwisko) > max_length or len(username) > max_length or len(password) > max_length:
            self.lineEdit_5.setText("Dane przekraczają dozwolony rozmiar!")
            return
        else:
            self.lineEdit_5.setText("")           

        data = (imie, nazwisko,username,password)

        self.run_thread1(self.send_to_server, data)
        self.run_thread2(self.receive_message)

    # Wysłanie danych na serwer (rejestrowanie)
    def send_to_server(self, data):
        try:
            flag=100
            self.client_socket.send(struct.pack("i",flag))
            self.client_socket.send(data[0].encode('utf-8'))
            time.sleep(1)
            self.client_socket.send(data[1].encode('utf-8'))
            time.sleep(1)
            self.client_socket.send(data[2].encode('utf-8'))
            time.sleep(1)
            self.client_socket.send(data[3].encode('utf-8'))
            
                
            return "Message sent."
        except Exception as e:
            return f"Error send: {str(e)}"

    # Odbiór od serwera zwrotki na temat rejestracji -> czy uzytkownik istnieje czy nie 
    def receive_message(self):
        try:
            response = self.client_socket.recv(4)
            response=struct.unpack('<i', response)[0]
            return response
        except Exception as e:
            return f"Error recv: {str(e)}, {response}\n"
    
    # Funkcja pomocnicza do zarządzania wątkamiem do wysyłu
    def run_thread1(self, function, *args):
        worker = Worker(function, *args)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    # Funkcja pomocnicza do zarządzania wątkamiem do odbioru
    def run_thread2(self, function, *args):
        worker = Worker(function, *args)
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    # Sprawdzenie rezultatu rejestracji -> poprawna - przejście do logowania | niepoprawna -> wyświetlenie komunikatu
    def handle_result(self, result):

        if result==120:
            self.block=True
            self.lineEdit_5.setText("")
            open_windows=QtWidgets.QApplication.topLevelWidgets()
            for i in open_windows:
                i.close()
            self.window = QtWidgets.QWidget() 
            self.ui = signin(self.Form, self.client_socket) 
            self.ui.setupUi(self.window) 
            self.window.show()
        else:
            print(self.block)
            if not self.block:
                _translate = QtCore.QCoreApplication.translate
                self.lineEdit_5.setText(_translate("Form", "Podany użytkownik już istnieje!"))
        
    def handle_error(self, error):
        print(f"Error: {error[1]}")
