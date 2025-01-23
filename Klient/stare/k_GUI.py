from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import traceback
import socket
import threading
import struct
import time
import os

server_address = "127.0.0.1"
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
    update_chat = pyqtSignal(list)  # Nowy sygnał do aktualizacji historii chatu

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

class main_menu(object):

    def __init__(self, nick=None):
        self.nick = nick
        self.signals = WorkerSignals()  # Używamy WorkerSignals zdefiniowanego dla Worker
        self.signals.update_chat.connect(self.update_chat_history)
        self.message_to_send = False
        self.znajomi_flag = False

    nazwyChaty = []
    idChaty = []

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

        # Timer do odświeżania zawartości
        self.threadpool = QThreadPool()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_receive_history_thread)
        self.timer.start(2000)  # Co 2 sekundy

        self.current_option = ""

        self.mutex = QMutex()

        self.run_thread(self.sequential_receive)

    def run_thread(self, function, *args):
        worker = Worker(function, *args)
        worker.signals.update_chat.connect(self.update_chat_history)
        self.threadpool.start(worker)
        self.threadpool.setMaxThreadCount(1)

    def run_receive_history_thread(self):
        self.run_thread(self.sequential_receive)

    def sequential_receive(self):
        self.current_option = self.comboBox.currentText()
        parts = self.current_option.split('-')
        if len(parts) == 2:
            parts.append(self.nick)
        parts.sort()
        merged_option = '-'.join(parts)
        self.current_option = merged_option

        if not self.znajomi_flag:
            with QMutexLocker(self.mutex):
                self.receive_history()
                nick_option= "-"+self.nick
                if self.current_option != "" and not self.message_to_send and self.current_option != nick_option:
                    self.send_to_server(400, self.current_option)
                    self.receive_chat()

                if self.message_to_send:
                    self.send_message_to_server()  # Wyślij wiadomość
                    self.message_to_send = False  # Resetuj flagę

    def update_text_based_on_selection(self):
        self.current_option = self.comboBox.currentText()
        parts = self.current_option.split('-')
        if len(parts) == 2:
            parts.append(self.nick)
        parts.sort()
        merged_option = '-'.join(parts)
        self.current_option = merged_option
        print(merged_option)
        
        
    def send_message(self):
        self.message_to_send = True  # Ustaw flagę na True, aby wysłać wiadomość

    def znajomi(self):
        self.znajomi_flag = True
        self.timer.stop()
        time.sleep(2)
        open_windows=QApplication.topLevelWidgets()
        for i in open_windows:
             if i.isVisible():
                position = i.geometry().topLeft()  # Pobranie pozycji okna
                print(position)
                i.close()
        # Tworzymy nowe okno i je wyświetlamy
        self.window = QtWidgets.QWidget()  # Stwórz nowe okno
        self.ui = znajomi(self.nick,position.x(),position.y())  # Utwórz obiekt klasy signup
        self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
        self.window.show()  # Pokaż nowe okno

    def send_message_to_server(self):

        self.current_option = self.comboBox.currentText()
        parts = self.current_option.split('-')
        if len(parts) == 2:
            parts.append(self.nick)
        parts.sort()
        merged_option = '-'.join(parts)
        self.current_option = merged_option

        message = self.lineEdit_2.text().strip()
        nick = self.nick
        chatName=self.current_option

        flag = 0
        client_socket.send(struct.pack("i", flag))
        time.sleep(0.5)
        client_socket.send(nick.encode('utf-8'))
        time.sleep(0.5)
        client_socket.send(chatName.encode('utf-8'))
        time.sleep(0.5)
        client_socket.send(message.encode('utf-8'))

    def send_to_server(self, flag, data):
        try:
            print(data)
            client_socket.send(struct.pack("i",flag))
            client_socket.send(data.encode('utf-8'))
            time.sleep(1)
                
            return "Message sent."
        except Exception as e:
            return f"Error send: {str(e)}"

    def receive_history(self):
        flag = 300
        client_socket.send(struct.pack("i", flag))
        client_socket.send(self.nick.encode('utf-8'))

        client_socket.settimeout(1)

        new_nazwyChaty = []
        new_idChaty = []

        while True:
            try:
                mess = client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
                if mess:
                    new_nazwyChaty.append(mess)
                else:
                    print("Server disconnected")
                    break

                mess = client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
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
                print(f"An error occurred while receiving history: {e}")
                break

        if new_nazwyChaty != self.nazwyChaty:
            self.nazwyChaty = new_nazwyChaty
            self.idChaty = new_idChaty
            self.update_combobox()
    
    def receive_chat(self):
        history_received = False
        chat_history = []  # Lista do przechowywania historii chatu

        # Najpierw odbieramy historię chatu
        while not history_received:
            try:
                # Odbieranie historii (w formacie danych z serwera)
                mess = client_socket.recv(1024).decode('utf-8', errors='replace')
                if mess:
                    chat_history.append(mess)  # Dodaj wiadomość do historii
                else:
                    print("Server disconnected")
                    break
            except socket.timeout:
                break
            except Exception as e:
                print(f"An error occurred while receiving message: {e}")
                break
            else:
                # Jeśli wiadomość została odebrana pomyślnie
                history_received = True

        self.signals.update_chat.emit(chat_history)

    def update_chat_history(self, chat_history):
    # Uaktualnij textEdit w głównym wątku
        if chat_history:
            self.textEdit.setText("".join(chat_history))  # Ustaw tekst na wszystkie wiadomości w historii
        else:
            self.textEdit.setText("Brak wiadomości w historii.")
        self.textEdit.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    # Przypisz metodę do sygnału
    
    def update_combobox(self):
        self.comboBox.blockSignals(True)  # Zablokowanie sygnałów podczas aktualizacji
        self.comboBox.clear()
        for nazwa in self.nazwyChaty:
            self.comboBox.addItem(nazwa)
        self.comboBox.blockSignals(False)  # Odblokowanie sygnałów
        self.update_text_based_on_selection()

    def handle_result(self, result):
        pass

    def handle_error(self, error):
        print(f"Error: {error[1]}")

class znajomi(object):

    def __init__(self, nick=None, x=1000,y=100):
        self.nick = nick
        self.back_flag=False
        self.nazwyZnajomi=[]
        self.statusZnajomi=[]
        self.window_x=x
        self.window_y=y
        self.nickiUzytkownicy = []
        self.strcmpUzytkownicy = []
        self.znajomiUzytkownicy = []
        self.nazwyChaty = []
        self.idChaty = []

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.move(self.window_x, self.window_y)
        print(100,self.window_y)
        Form.resize(533, 397)


        # Tworzenie grupy - lewy dolny róg
        self.groupLabel = QtWidgets.QLabel(parent=Form)
        self.groupLabel.setGeometry(QtCore.QRect(15, 220, 271, 20))
        self.groupLabel.setObjectName("groupLabel")
        self.groupLabel.setText("Tworzenie grupy")

        self.nick1Input = QtWidgets.QComboBox(parent=Form)
        self.nick1Input.setGeometry(QtCore.QRect(15, 250, 271, 30))
        self.nick1Input.setObjectName("nick1Input")

        self.nick2Input = QtWidgets.QComboBox(parent=Form)
        self.nick2Input.setGeometry(QtCore.QRect(15, 290, 271, 30))
        self.nick2Input.setObjectName("nick2Input")

        self.createGroupButton = QtWidgets.QPushButton(parent=Form)
        self.createGroupButton.setGeometry(QtCore.QRect(15, 330, 271, 30))
        self.createGroupButton.setObjectName("createGroupButton")
        self.createGroupButton.setText("Utwórz grupę")
        self.createGroupButton.clicked.connect(self.create_group)

        # Inne 
        self.labelNick = QtWidgets.QLabel(parent=Form)
        self.labelNick.setGeometry(QtCore.QRect(255, 10, 200, 24))
        self.labelNick.setObjectName("labelNick")
        self.labelNick.setText(f"Nick: {self.nick}")

        self.listView = QtWidgets.QListWidget(parent=Form)
        self.listView.setGeometry(QtCore.QRect(15, 30, 271, 180))
        self.listView.setObjectName("listView")

        self.comboBox = QtWidgets.QComboBox(parent=Form)
        self.comboBox.setGeometry(QtCore.QRect(310, 80, 201, 51))
        self.comboBox.setObjectName("comboBox")

        self.comboBox_2 = QtWidgets.QComboBox(parent=Form)
        self.comboBox_2.setGeometry(QtCore.QRect(340, 310, 131, 31))
        self.comboBox_2.setObjectName("comboBox_2")

        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(320, 160, 75, 24))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.accept_friend)

        self.pushButton_2 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_2.setGeometry(QtCore.QRect(410, 160, 75, 24))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.decline_friend)

        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setGeometry(QtCore.QRect(340, 350, 130, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.send_invitation)

        self.pushButton_4 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_4.setGeometry(QtCore.QRect(370, 260, 75, 24))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.search_users)

        self.pushButtonBack = QtWidgets.QPushButton(parent=Form)
        self.pushButtonBack.setGeometry(QtCore.QRect(450, 10, 75, 24))
        self.pushButtonBack.setObjectName("pushButtonBack")
        self.pushButtonBack.setText("Powrót")
        self.pushButtonBack.clicked.connect(self.back_to_main)

        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=Form)
        self.plainTextEdit.setGeometry(QtCore.QRect(340, 220, 131, 31))
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(360, 30, 101, 16))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(parent=Form)
        self.label_2.setGeometry(QtCore.QRect(400, 50, 16, 16))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(parent=Form)
        self.label_3.setGeometry(QtCore.QRect(20, 10, 49, 16))
        self.label_3.setObjectName("label_3")
        
        self.label_4 = QtWidgets.QLabel(parent=Form)
        self.label_4.setGeometry(QtCore.QRect(340, 200, 161, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        
        self.label_5 = QtWidgets.QLabel(parent=Form)
        self.label_5.setGeometry(QtCore.QRect(400, 280, 49, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        
        
        

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.threadpool = QThreadPool()


        self.run_thread(self.sequential_receive)

        self.mutex = QMutex()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Znajomi"))
        self.pushButton.setText(_translate("Form", "Zaakceptuj"))
        self.pushButton_2.setText(_translate("Form", "Odrzuć"))
        self.label.setText(_translate("Form", "Liczba zaproszeń:"))
        self.label_2.setText(_translate("Form", "0"))
        self.label_3.setText(_translate("Form", "Znajomi"))
        self.pushButton_3.setText(_translate("Form", "Dodaj użytkownika"))
        self.label_4.setText(_translate("Form", "Wyszukaj użytkownika"))
        self.pushButton_4.setText(_translate("Form", "Szukaj"))
        self.label_5.setText(_translate("Form", "↓"))
    
    # Funkcja uruchamiajaca watki
    def run_thread(self, function, *args):
        worker = Worker(function, *args)
        self.threadpool.start(worker)
        self.threadpool.setMaxThreadCount(1)

    # Po kliknieciu guzika --> Powrot do menu glownego
    def back_to_main(self):
        self.back_flag = True
        open_windows=QApplication.topLevelWidgets()
        for i in open_windows:
            i.close()
        # Tworzymy nowe okno i je wyświetlamy
        self.window = QtWidgets.QWidget()  # Stwórz nowe okno
        self.ui = main_menu(self.nick)  # Utwórz obiekt klasy signup
        self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
        self.window.show()  # Pokaż nowe okno

    # Po kliknieciu guzika --> obsluga akceptacji i odswiezenie okna
    def accept_friend(self):
        with QMutexLocker(self.mutex):
            self.run_thread(self.accept_friend_send)
            time.sleep(0.5)
            self.refresh()

    # Funkcja do obslugi przyjecia zaproszenia do znajomych
    def accept_friend_send(self):
        flag = 710
        client_socket.send(struct.pack("i", flag))
        client_socket.send(self.nick.encode('utf-8'))

        time.sleep(0.5)

        friend = self.comboBox.currentText()
        client_socket.send(friend.encode('utf-8'))

    # Po kliknieciu guzika --> obsluga odrzucenia i odswiezenie okna
    def decline_friend(self):
        with QMutexLocker(self.mutex):
            self.run_thread(self.decline_friend_send)
            time.sleep(0.5)
            self.refresh()

    # Funkcja do obslugi odrzucenia zaproszenia do znajomych
    def decline_friend_send(self):
        flag = 720
        client_socket.send(struct.pack("i", flag))
        client_socket.send(self.nick.encode('utf-8'))

        time.sleep(0.5)
        friend = self.comboBox.currentText()
        client_socket.send(friend.encode('utf-8'))

    def search_users(self):
        self.run_thread(self.receive_search)

    def receive_search(self):

        flag = 600
        client_socket.send(struct.pack("i", flag))

        time.sleep(0.5)
        print("\033[33mPodaj swój nick: \033[0m")
        nick = self.nick
        client_socket.send(nick.encode('utf-8'))
        
        time.sleep(0.5)
        print("\033[33mWprowadź nick szukanego użytkownika: \033[0m")
        searchedNick = self.plainTextEdit.toPlainText()
        client_socket.send(searchedNick.encode('utf-8'))

        nickiUzytkownicy = []
        strcmpUzytkownicy = []
        znajomiUzytkownicy = []

        client_socket.settimeout(1)

        nickiUzytkownicy.clear()
        strcmpUzytkownicy.clear()
        znajomiUzytkownicy.clear()

        while True:
            try:
                # Odbierz efekty wyszukiwania (nicki)
                mess = client_socket.recv(1024).decode("utf-8",errors='replace')
                mess = mess.replace('\x00', '')
                if mess:
                    #print(f"search (nick): {mess}")
                    nickiUzytkownicy.append(mess)
                else:
                    print("Server disconnected")
                    break

                # Odbierz efekty wyszukiwania (int podobieństwa)
                data = client_socket.recv(4)
                mess = struct.unpack('<i', data)[0]
                #print(f"search (podobieństwo): {mess}")
                strcmpUzytkownicy.append(mess)

                # Odbierz efekty wyszukiwania (czy znajomi)
                mess = client_socket.recv(1).decode("utf-8",errors='replace')
                mess = mess.replace('\x00', '')
                if mess:
                    #print(f"search (friend): {mess}")
                    znajomiUzytkownicy.append(mess)
                else:
                    #print("Server disconnected")
                    break

            except socket.timeout:
                if not nickiUzytkownicy:
                    print("\033[31mW systemie nie istnieje żaden użytkownik!\033[0m")
                #print("Server timed out")

                #print("Nick: ", nickiUzytkownicy)
                #print("Podobieństwo: ", strcmpUzytkownicy)
                #print("Znajomi: ", znajomiUzytkownicy)

                listy = list(zip(nickiUzytkownicy,strcmpUzytkownicy,znajomiUzytkownicy))
                listy_sorted = sorted(listy, key=lambda x: x[1], reverse=True)
                nickiUzytkownicy_sorted, strcmpUzytkownicy_sorted, znajomiUzytkownicy_sorted = zip(*listy_sorted)

                print("Nick: ", nickiUzytkownicy_sorted)
                print("Podobieństwo: ", strcmpUzytkownicy_sorted)
                print("Znajomi: ", znajomiUzytkownicy_sorted)

                self.nickiUzytkownicy = nickiUzytkownicy
                self.strcmpUzytkownicy = strcmpUzytkownicy
                self.znajomiUzytkownicy = znajomiUzytkownicy

                # Wyczyść comboBox_2 z istniejących elementów
                self.comboBox_2.clear()

                # Dodaj do comboBox_2 nicki użytkowników, którzy:
                # - Nie są znajomymi ('n' w znajomiUzytkownicy)
                # - Mają wartość podobieństwa > 0
                for nick, podobienstwo, czyZnajomy in zip(self.nickiUzytkownicy, self.strcmpUzytkownicy, self.znajomiUzytkownicy):
                    if czyZnajomy == 'n' and podobienstwo > 0 and nick != self.nick:
                        self.comboBox_2.addItem(nick)

                break
            except Exception as e:
                print(f"An error occurred while receiving search: {e}")
                break

    def send_invitation(self):
        try: 
            flag = 700
            client_socket.send(struct.pack("i", flag))

            time.sleep(0.5)
            print("\033[33mPodaj swój nick: \033[0m")
            mess2 = self.nick
            client_socket.send(mess2.encode('utf-8'))

            time.sleep(0.5)
            print("\033[33mPodaj nick osoby, którą zapraszasz: \033[0m")
            mess1 = self.comboBox_2.currentText()
            client_socket.send(mess1.encode('utf-8'))
        except Exception as e:
            print(f"An error occured while inviting {e}")

    def create_group(self):
        self.run_thread(self.create_group_send)
    
    def create_group_send(self):

        self.receive_history()

        mess2 = self.nick
        mess1 = self.nick1Input.currentText()
        mess0 = self.nick2Input.currentText()

        nick_list = [self.nick, self.nick1Input.currentText(), self.nick2Input.currentText()]

        nick_list.sort()

        result = '-'.join(nick_list)

        if result not in self.idChaty:


            flag = 800
            client_socket.send(struct.pack("i", flag))

            time.sleep(0.5)
            print(mess2)
            client_socket.send(mess2.encode('utf-8'))

            time.sleep(0.5)
            print(mess1)
            client_socket.send(mess1.encode('utf-8'))

            time.sleep(0.5)
            print(mess0)
            client_socket.send(mess0.encode('utf-8'))

        else:
            print("Chat juz istnieje!\n")
    
    def receive_history(self):
        flag = 300
        client_socket.send(struct.pack("i", flag))
        client_socket.send(self.nick.encode('utf-8'))

        client_socket.settimeout(1)

        new_nazwyChaty = []
        new_idChaty = []

        while True:
            try:
                mess = client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
                if mess:
                    new_nazwyChaty.append(mess)
                else:
                    print("Server disconnected")
                    break

                mess = client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
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
                print(f"An error occurred while receiving history: {e}")
                break

        if new_nazwyChaty != self.nazwyChaty:
            self.nazwyChaty = new_nazwyChaty
            self.idChaty = new_idChaty

    
    # Funkcja rozpoczynajaca watek obslugujacy calosciowe odswiezenie ekranu (odbior znaj i wypisanie)
    def refresh(self):
        self.run_thread(self.sequential_receive)

    # Sekwencyjny odbior listy znajomych od serwera oraz ich wczytanie
    def sequential_receive(self):
        with QMutexLocker(self.mutex):
            self.receive_friends()
            self.load_friends()

    # Funkcja obslugujaca odbior znajomych od serwera
    def receive_friends(self):

        if not self.back_flag:
            flag = 500
            client_socket.send(struct.pack("i", flag))
            client_socket.send(self.nick.encode('utf-8'))
            client_socket.settimeout(1)

            # Wyczyść listy znajomych
            self.nazwyZnajomi.clear()
            self.statusZnajomi.clear()

            while True:
                try:
                    mess = client_socket.recv(1024).decode("utf-8",errors='replace')
                    cleaned_mess = mess.replace('\x00', '').strip()
                    if cleaned_mess:
                        #print(f"friend: {mess}")
                        self.nazwyZnajomi.append(cleaned_mess)
                    else:
                        #print("Server disconnected")
                        break

                    if mess:
                        mess = client_socket.recv(1024).decode("utf-8",errors='replace')
                        cleaned_mess = mess.replace('\x00', '').strip()
                        self.statusZnajomi.append(cleaned_mess)
                    else:
                        print("Server disconnected")
                        break

                except socket.timeout:
                    if not self.nazwyZnajomi:
                        print("\033[31mUżytkownik nie posiada żadnych znajomych !\033[0m")
                    print(self.statusZnajomi)
                    print("Server timed out")
                    break
                except Exception as e:
                    print(f"An error occurred while receiving friends: {e}")
                    break

    # Funkcja obslugujaca odswiezenie okna
    def load_friends(self):
        friend_requests = 0
        self.comboBox.clear()
        self.listView.clear()
        self.nick1Input.clear()  # Czyszczenie nick1Input
        self.nick2Input.clear()  # Czyszczenie nick2Input

        for i in range(len(self.statusZnajomi)):
            print(self.statusZnajomi[i])
            if self.statusZnajomi[i] == 'f':
                # Dodaj do listy znajomych
                self.listView.addItem(self.nazwyZnajomi[i])
                # Dodaj do nick1Input i nick2Input, jeżeli status to 'f'
                self.nick1Input.addItem(self.nazwyZnajomi[i])
                self.nick2Input.addItem(self.nazwyZnajomi[i])
            elif self.statusZnajomi[i] == 'n':
                self.comboBox.addItem(self.nazwyZnajomi[i])
                friend_requests += 1
            else:
                pass

        self.label_2.setText(str(friend_requests))

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


    def send_to_server(self, data):
        try:
            flag=200
            client_socket.send(struct.pack("i",flag))
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

            # Tworzymy nowe okno i je wyświetlamy
            self.window = QtWidgets.QWidget()  # Stwórz nowe okno
            self.ui = main_menu(self.nick)  # Utwórz obiekt klasy signup
            self.ui.setupUi(self.window)  # Ustaw UI dla tego okna
            self.window.show()  # Pokaż nowe okno

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


def disconnect():
    flag=-1
    client_socket.send(struct.pack("i",flag))
    client_socket.close()
    exit()


app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(lambda: disconnect())
Form = QtWidgets.QWidget()
ui = signin()
ui.setupUi(Form)
Form.show()
app.exec()
