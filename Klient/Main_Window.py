from Worker import Worker,WorkerSignals

from PyQt6 import QtCore, QtGui, QtWidgets

import socket
import struct
import time


# Klasa opisujaca glowne okno do komunikacji 
class main_menu(object):

    def __init__(self,Form,nick,client_socket=None):
        self.client_socket = client_socket
        self.Form = Form
        self.nick = nick
        self.signals = WorkerSignals()
        self.signals.update_chat.connect(self.update_chat_history) 
        self.message_to_send = False
        self.znajomi_flag = False
        self.nazwyChaty = []
        self.idChaty = []

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(533, 396)

        self.labelNick = QtWidgets.QLabel(parent=Form)
        self.labelNick.setGeometry(QtCore.QRect(10, 10, 200, 24))
        self.labelNick.setObjectName("labelNick")
        self.labelNick.setText(f"Nick: {self.nick}")

        self.comboBox = QtWidgets.QComboBox(parent=Form)
        self.comboBox.setGeometry(QtCore.QRect(80, 20, 201, 51))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.currentIndexChanged.connect(self.update_text_based_on_selection)

        self.textEdit = QtWidgets.QTextEdit(parent=Form)
        self.textEdit.setGeometry(QtCore.QRect(40, 110, 281, 191))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setReadOnly(True)

        self.lineEdit_2 = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(70, 320, 201, 21))
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(290, 320, 61, 21))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Send")
        self.pushButton.clicked.connect(self.send_message)

        self.pushButtonFriends = QtWidgets.QPushButton(parent=Form)
        self.pushButtonFriends.setGeometry(QtCore.QRect(400, 180, 75, 24))
        self.pushButtonFriends.setObjectName("pushButtonFriends")
        self.pushButtonFriends.setText("Znajomi")
        self.pushButtonFriends.clicked.connect(self.znajomi)

        # Etykieta do wyświetlania komunikatów
        self.label_status = QtWidgets.QLabel(parent=Form)
        self.label_status.setGeometry(QtCore.QRect(70, 350, 281, 21))
        self.label_status.setObjectName("label_status")
        self.label_status.setStyleSheet("color: red;")
        self.label_status.setText("") 

        # Timer do odświeżania zawartości
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_receive_history_thread)
        self.timer.start(2000)

        self.current_option = ""

        self.mutex = QtCore.QMutex()

        self.run_thread(self.sequential_receive)


    # Funkcja pomocnicza do wykonywania watkow oraz odswiezenia czatu
    def run_thread(self, function, *args):
        worker = Worker(function, *args)
        worker.signals.update_chat.connect(self.update_chat_history)
        self.threadpool.start(worker)
        self.threadpool.setMaxThreadCount(1)

    # Wlaczenie watku do cyklicznego odswiezania 
    def run_receive_history_thread(self):
        self.run_thread(self.sequential_receive)

    # CYkliczne odswiezanie chatow/wiadmosci
    def sequential_receive(self):
        self.current_option = self.comboBox.currentText()
        parts = self.current_option.split('-')
        if len(parts) == 1:
            parts.append(self.nick)
        parts.sort()
        merged_option = '-'.join(parts)
        self.current_option = merged_option

        try:
            if not self.znajomi_flag:
                with QtCore.QMutexLocker(self.mutex):
                    self.receive_chats()
                    nick_option= "-"+self.nick
                    if self.current_option != "" and not self.message_to_send and self.current_option != nick_option:
                        self.send_selection_to_server(400, self.current_option)
                        self.receive_history()

                    if self.message_to_send:
                        time.sleep(0.5)
                        self.send_message_to_server()
                        self.message_to_send = False
        except:
            pass

    # Funkcja do odswiezania selekcji czatu
    def update_text_based_on_selection(self):
        self.current_option = self.comboBox.currentText()
        parts = self.current_option.split('-')
        if len(parts) == 1:
            parts.append(self.nick)
        parts.sort()
        merged_option = '-'.join(parts)
        self.current_option = merged_option
        
    # Wyslanie wiadomosci na serwer --> wlaczenie flagi wysylania 
    def send_message(self):
        self.threadpool.waitForDone()
        self.message_to_send = True  # Ustaw flagę na True, aby wysłać wiadomość

    # Funkcja do przejscia okna znajomych
    def znajomi(self):
        self.znajomi_flag = True
        self.timer.stop()
        self.threadpool.waitForDone()
        #time.sleep(2)
        open_windows=QtWidgets.QApplication.topLevelWidgets()
        for i in open_windows:
             if i.isVisible():
                position = i.geometry().topLeft()  # Pobranie pozycji okna
                i.close()
        self.window = QtWidgets.QWidget()  # Stwórz nowe okno

        from Znajomi import znajomi
        self.ui = znajomi(self.Form,self.nick,position.x(),position.y(),self.client_socket) 
        self.ui.setupUi(self.window)
        self.window.show()

    # Jezeli flaga jest aktywna to funkcja przesle wiadomosc na serwer
    def send_message_to_server(self):

        self.current_option = self.comboBox.currentText()
        message = self.lineEdit_2.text().strip()
        nick = self.nick

        if self.current_option == "":
            self.label_status.setText("Nie wybrano chatu!") 
            return
        elif message == "":
            self.label_status.setText("Twoja wiadomość jest pusta!") 
            return
        else:
            self.label_status.setText("") 


        parts = self.current_option.split('-')
        if len(parts) == 1:
            parts.append(self.nick)        
        parts.sort()
        merged_option = '-'.join(parts)
        self.current_option = merged_option
        chatName=self.current_option


        self.lineEdit_2.setText("")

        self.chat_history.append(f'{self.nick}: {message}')
        self.signals.update_chat.emit(self.chat_history)

        flag = 0
        self.client_socket.send(struct.pack("i", flag))
        time.sleep(0.5)
        self.client_socket.send(nick.encode('utf-8'))
        time.sleep(0.5)
        self.client_socket.send(chatName.encode('utf-8'))
        time.sleep(0.5)
        self.client_socket.send(message.encode('utf-8'))



    # Wysyl wyboru chatu na serwer
    def send_selection_to_server(self, flag, data):
        try:
            self.client_socket.send(struct.pack("i",flag))
            self.client_socket.send(data.encode('utf-8'))
            time.sleep(1)
            return "Message sent."
        except Exception as e:
            return f"Error send: {str(e)}"

    # Odbior czatow od serwera
    def receive_chats(self):
        flag = 300
        self.client_socket.send(struct.pack("i", flag))
        self.client_socket.send(self.nick.encode('utf-8'))

        self.client_socket.settimeout(1)

        new_nazwyChaty = []
        new_idChaty = []

        while True:
            try:
                mess = self.client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
                if mess:
                    new_nazwyChaty.append(mess)
                else:
                    print("Server disconnected")
                    break

                mess = self.client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
                if mess:
                    new_idChaty.append(mess)
                else:
                    print("Server disconnected")
                    break

            except socket.timeout:
                if not new_nazwyChaty:
                    print("\033[31mUżytkownik nie posiada żadnych chatów !\033[0m")
                break
            except Exception as e:
                break

        if new_nazwyChaty != self.nazwyChaty:
            self.nazwyChaty = new_nazwyChaty
            self.idChaty = new_idChaty
            self.update_combobox()
    
    # Odbior historii czatu
    def receive_history(self):
        history_received = False
        self.chat_history = []

        while not history_received:
            try:
                mess = self.client_socket.recv(1024).decode('utf-8', errors='replace')
                if mess:
                    self.chat_history.append(mess)
                else:
                    print("Server disconnected")
                    break
            except socket.timeout:
                break
            except Exception as e:
                break
            else:
                history_received = True

        self.signals.update_chat.emit(self.chat_history)

    # Odswiezenie czatu po odbiorze z serwera
    def update_chat_history(self):
        if self.chat_history:
            self.textEdit.setText("".join(self.chat_history))
        else:
            self.textEdit.setText("Brak wiadomości w historii.")
        self.textEdit.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    # Odswiezenie wyboru czatow po odbiorze z serwera
    def update_combobox(self):
        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        for nazwa in self.nazwyChaty:
            self.comboBox.addItem(nazwa)
        self.comboBox.blockSignals(False)
        self.update_text_based_on_selection()
