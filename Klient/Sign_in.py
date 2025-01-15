from Worker import Worker
from Main_Window import main_menu

from PyQt6 import QtCore, QtGui, QtWidgets

import struct
import time

class signin(object):

    def __init__(self,Form,client_socket=None):
        self.client_socket = client_socket
        self.Form = Form

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

        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)

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

        data = (self.nick, password)
        #self.run_thread(self.send_to_server, data)
        self.run_thread(self.login_thread,data)


    def signup(self):
        # Zamykamy obecne okno
        open_windows=QtWidgets.QApplication.topLevelWidgets()
        for i in open_windows:
            i.close()
        # Tworzymy nowe okno i je wyświetlamy
        self.window = QtWidgets.QWidget()  # Stwórz nowe okno
        
        from SIgn_up import signup
        self.ui = signup(self.Form,self.client_socket)  # Utwórz obiekt klasy signup

        self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
        self.window.show()  # Pokaż nowe okno

        open_windows=QtWidgets.QApplication.topLevelWidgets()


    def login_thread(self,data):

        # Jeśli dane są niepoprawne, ustawiamy komunikat o błędzie
        if data[0] == "" or data[1] == "":
            self.lineEdit_4.setText("Niepoprawne dane!")
            self.lineEdit_4.setStyleSheet("color: red;")  # Ustawiamy tekst na czerwony
            return
        # Wysyłanie danych do serwera
        flag = 200
        self.client_socket.send(struct.pack("i", flag))
        self.client_socket.send(data[0].encode('utf-8'))
        time.sleep(1)  # Chwileczkę czekamy, żeby dane mogły zostać wysłane
        self.client_socket.send(data[1].encode('utf-8'))
        
        # Po udanym wysłaniu komunikatu
        self.lineEdit_4.setText("")  # Czyszczenie pola tekstowego
        try:
            response = self.client_socket.recv(4)
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
            open_windows=QtWidgets.QApplication.topLevelWidgets()
            for i in open_windows:
                i.close()
            # Tworzymy nowe okno i je wyświetlamy
            self.window = QtWidgets.QWidget()  # Stwórz nowe okno
            self.ui = main_menu(self.Form,self.nick,self.client_socket)  # Utwórz obiekt klasy signup
            self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
            self.window.show()  # Pokaż nowe okno

    def handle_error(self, error):
        print(f"Error: {error[1]}")
