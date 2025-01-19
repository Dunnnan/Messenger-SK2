from Worker import Worker
from Main_Window import main_menu

from PyQt6 import QtCore, QtGui, QtWidgets

import socket
import struct
import time

# KLasa opisująca okno znajomych aplikacji
class znajomi(object):

    # Inicjalizacja wartości używanych w kodzie
    def __init__(self, Form,nick=None, x=1000,y=100, client_socket=None):
        self.client_socket = client_socket
        self.Form = Form
        self.nick = nick
        self.nazwyZnajomi=[]
        self.statusZnajomi=[]
        self.window_x=x
        self.window_y=y
        self.nickiUzytkownicy = []
        self.strcmpUzytkownicy = []
        self.znajomiUzytkownicy = []
        self.nazwyChaty = []
        self.idChaty = []

    # Inicjalizacja GUI
    def setupUi(self, Form):

        # Ustawienie okna w jego poprzedniej lokalizacji (po zamknięciu okna)
        Form.setObjectName("Form")
        Form.move(self.window_x, self.window_y)
        print(100,self.window_y)
        Form.resize(533, 397)


        # Tworzenie grupy - lewy dolny róg
        self.groupLabel = QtWidgets.QLabel(parent=Form)
        self.groupLabel.setGeometry(QtCore.QRect(15, 220, 271, 20))
        self.groupLabel.setObjectName("groupLabel")
        self.groupLabel.setText("Tworzenie grupy")

        # Box do wyboru nicku 1 do tworzenia grupy
        self.nick1Input = QtWidgets.QComboBox(parent=Form)
        self.nick1Input.setGeometry(QtCore.QRect(15, 250, 271, 30))
        self.nick1Input.setObjectName("nick1Input")

        # Box do wyboru nicku 2 do tworzenia grupy
        self.nick2Input = QtWidgets.QComboBox(parent=Form)
        self.nick2Input.setGeometry(QtCore.QRect(15, 290, 271, 30))
        self.nick2Input.setObjectName("nick2Input")

        # Guzik do wysłania zapytania o stworzenie grupy
        self.createGroupButton = QtWidgets.QPushButton(parent=Form)
        self.createGroupButton.setGeometry(QtCore.QRect(15, 330, 271, 30))
        self.createGroupButton.setObjectName("createGroupButton")
        self.createGroupButton.setText("Utwórz grupę")
        self.createGroupButton.clicked.connect(self.create_group)

        # Napis znajomi
        self.labelNick = QtWidgets.QLabel(parent=Form)
        self.labelNick.setGeometry(QtCore.QRect(255, 10, 200, 24))
        self.labelNick.setObjectName("labelNick")
        self.labelNick.setText(f"Nick: {self.nick}")

        # Lista znajomych
        self.listView = QtWidgets.QListWidget(parent=Form)
        self.listView.setGeometry(QtCore.QRect(15, 30, 271, 180))
        self.listView.setObjectName("listView")

        # Combobox do wyboru nicku 1 - tworzenie grupy
        self.comboBox = QtWidgets.QComboBox(parent=Form)
        self.comboBox.setGeometry(QtCore.QRect(310, 80, 201, 51))
        self.comboBox.setObjectName("comboBox")

        # Combobox do wyboru nicku 2 - tworzenie grupy
        self.comboBox_2 = QtWidgets.QComboBox(parent=Form)
        self.comboBox_2.setGeometry(QtCore.QRect(340, 310, 131, 31))
        self.comboBox_2.setObjectName("comboBox_2")

        # Guzik do akceptacji zaproszenia
        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(320, 160, 75, 24))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.accept_friend)

        # Guzik do odrzucenia zaproszenia
        self.pushButton_2 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_2.setGeometry(QtCore.QRect(410, 160, 75, 24))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.decline_friend)

        # Guzik do wysłania zaproszenia
        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setGeometry(QtCore.QRect(340, 350, 130, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.send_invitation)

        # Guzik do wyszukania użytkownika
        self.pushButton_4 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_4.setGeometry(QtCore.QRect(370, 260, 75, 24))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.search_users)

        # Guzik pozwalający wrócić do menu głównego
        self.pushButtonBack = QtWidgets.QPushButton(parent=Form)
        self.pushButtonBack.setGeometry(QtCore.QRect(450, 10, 75, 24))
        self.pushButtonBack.setObjectName("pushButtonBack")
        self.pushButtonBack.setText("Powrót")
        self.pushButtonBack.clicked.connect(self.back_to_main)

        # Pole do wpisania szukanego użytkownika
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=Form)
        self.plainTextEdit.setGeometry(QtCore.QRect(340, 220, 131, 31))
        self.plainTextEdit.setObjectName("plainTextEdit")

        # "Liczba zaproszeń"
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(360, 30, 101, 16))
        self.label.setObjectName("label")

        # Wyświetlanie liczby oczekujących zaproszeń
        self.label_2 = QtWidgets.QLabel(parent=Form)
        self.label_2.setGeometry(QtCore.QRect(400, 50, 16, 16))
        self.label_2.setObjectName("label_2")

        # "Znajomi"
        self.label_3 = QtWidgets.QLabel(parent=Form)
        self.label_3.setGeometry(QtCore.QRect(20, 10, 49, 16))
        self.label_3.setObjectName("label_3")
        
        # "Wyszukaj użytkownika"
        self.label_4 = QtWidgets.QLabel(parent=Form)
        self.label_4.setGeometry(QtCore.QRect(340, 200, 161, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        
        # "Strzałka pokazująca przebieg operacji"
        self.label_5 = QtWidgets.QLabel(parent=Form)
        self.label_5.setGeometry(QtCore.QRect(400, 280, 49, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")

        # Label do wyświetlania nieprawidłowości
        self.errorLabel = QtWidgets.QLabel(parent=Form)
        self.errorLabel.setGeometry(QtCore.QRect(15, 360, 271, 30))
        self.errorLabel.setObjectName("errorLabel")
        self.errorLabel.setStyleSheet("color: red;")  # Kolor tekstu na czerwono
        self.errorLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.errorLabel.setText("")  # Początkowy tekst jest pusty


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.run_thread(self.sequential_receive)
        self.mutex = QtCore.QMutex()

    # Inicjalizacja wartości tekstów
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

        self.threadpool.waitForDone()  

        # Zamykamy otwarte okno
        open_windows=QtWidgets.QApplication.topLevelWidgets()
        for i in open_windows:
            i.close()
        
        # Tworzymy nowe okno i je wyświetlamy
        self.window = QtWidgets.QWidget()
        self.ui = main_menu(self.Form,self.nick,self.client_socket)
        self.ui.setupUi(self.window)
        self.window.show()  # Pokaż nowe okno

    # Po kliknieciu guzika --> obsluga akceptacji i odswiezenie okna
    def accept_friend(self):
        with QtCore.QMutexLocker(self.mutex):
            self.run_thread(self.accept_friend_send)
            time.sleep(0.5)
            self.refresh()

    # Funkcja do obslugi przyjecia zaproszenia do znajomych
    def accept_friend_send(self):
        flag = 710
        self.client_socket.send(struct.pack("i", flag))
        self.client_socket.send(self.nick.encode('utf-8'))

        time.sleep(0.5)

        friend = self.comboBox.currentText()
        self.client_socket.send(friend.encode('utf-8'))

    # Po kliknieciu guzika --> obsluga odrzucenia i odswiezenie okna
    def decline_friend(self):
        with QtCore.QMutexLocker(self.mutex):
            self.run_thread(self.decline_friend_send)
            time.sleep(0.5)
            self.refresh()

    # Funkcja do obslugi odrzucenia zaproszenia do znajomych
    def decline_friend_send(self):
        flag = 720
        self.client_socket.send(struct.pack("i", flag))
        self.client_socket.send(self.nick.encode('utf-8'))

        time.sleep(0.5)
        friend = self.comboBox.currentText()
        self.client_socket.send(friend.encode('utf-8'))

    # Funkcja rozpoczynająca wątek do otrzymania rezultatu wyszukiwania użytkownika
    def search_users(self):
        self.run_thread(self.receive_search)

    # Funkcja obsługująca wyszukiwanie użytkownika
    def receive_search(self):

        flag = 600
        self.client_socket.send(struct.pack("i", flag))

        time.sleep(0.5)
        nick = self.nick
        self.client_socket.send(nick.encode('utf-8'))
        
        time.sleep(0.5)
        searchedNick = self.plainTextEdit.toPlainText()
        self.client_socket.send(searchedNick.encode('utf-8'))

        nickiUzytkownicy = []
        strcmpUzytkownicy = []
        znajomiUzytkownicy = []

        self.client_socket.settimeout(1)

        nickiUzytkownicy.clear()
        strcmpUzytkownicy.clear()
        znajomiUzytkownicy.clear()

        while True:
            try:
                # Odbierz efekty wyszukiwania (nicki)
                mess = self.client_socket.recv(1024).decode("utf-8",errors='replace')
                mess = mess.replace('\x00', '')
                if mess:
                    nickiUzytkownicy.append(mess)
                else:
                    print("Server disconnected")
                    break

                # Odbierz efekty wyszukiwania (int podobieństwa)
                data = self.client_socket.recv(4)
                mess = struct.unpack('<i', data)[0]
                strcmpUzytkownicy.append(mess)

                # Odbierz efekty wyszukiwania (czy znajomi)
                mess = self.client_socket.recv(1).decode("utf-8",errors='replace')
                mess = mess.replace('\x00', '')
                if mess:
                    znajomiUzytkownicy.append(mess)
                else:
                    break

            except socket.timeout:
                if not nickiUzytkownicy:
                    print("\033[31mW systemie nie istnieje żaden użytkownik!\033[0m")

                listy = list(zip(nickiUzytkownicy,strcmpUzytkownicy,znajomiUzytkownicy))
                listy_sorted = sorted(listy, key=lambda x: x[1], reverse=True)
                nickiUzytkownicy_sorted, strcmpUzytkownicy_sorted, znajomiUzytkownicy_sorted = zip(*listy_sorted)

                self.nickiUzytkownicy = nickiUzytkownicy_sorted
                self.strcmpUzytkownicy = strcmpUzytkownicy_sorted
                self.znajomiUzytkownicy = znajomiUzytkownicy_sorted

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

    # Funkcja obsługująca wysłanie zaproszenia do znajomych
    def send_invitation(self):
        try: 
            flag = 700
            self.client_socket.send(struct.pack("i", flag))

            time.sleep(0.5)
            print("\033[33mPodaj swój nick: \033[0m")
            mess2 = self.nick
            self.client_socket.send(mess2.encode('utf-8'))

            time.sleep(0.5)
            print("\033[33mPodaj nick osoby, którą zapraszasz: \033[0m")
            mess1 = self.comboBox_2.currentText()
            self.client_socket.send(mess1.encode('utf-8'))
        except Exception as e:
            print(f"An error occured while inviting {e}")

    # Funkcja rozpoczynająca wątek do tworzenia grupy
    def create_group(self):
        self.run_thread(self.create_group_send)
    
    # Funkcja tworząca grupę
    def create_group_send(self):

        # Otrzymanie chatów użytkownika
        self.receive_chats()

        # Sprawdzenie czy dany chat już istnieje lub czy jest nieprawidłowy
        mess2 = self.nick
        mess1 = self.nick1Input.currentText()
        mess0 = self.nick2Input.currentText()
        nick_list = [self.nick, self.nick1Input.currentText(), self.nick2Input.currentText()]
        nick_list.sort()
        result = '-'.join(nick_list)


        # Sprawdzenie czy chat może zostać utworzony
        if mess0 == "" or mess1 == "":
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText("Wszystkie pola muszą być wypełnione!")
            return
        elif mess0 == mess1:
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText("Nie można utworzyć chatu o identycznych użytkownikach!") 
            return
        elif result in self.idChaty:
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText("Chat już istnieje!")
            return

        # Jeśli wszystkie warunki są spełnione, tworzymy chat
        flag = 800
        self.client_socket.send(struct.pack("i", flag))

        time.sleep(0.5)
        print(mess2)
        self.client_socket.send(mess2.encode('utf-8'))

        time.sleep(0.5)
        print(mess1)
        self.client_socket.send(mess1.encode('utf-8'))

        time.sleep(0.5)
        print(mess0)
        self.client_socket.send(mess0.encode('utf-8'))

        self.errorLabel.setStyleSheet("color: green;")
        self.errorLabel.setText("Chat utworzony!")
    
    # Funkcja wspomagająca tworzenie grupy -> odbiera istniejące chaty
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
                    break

                mess = self.client_socket.recv(1024).decode("utf-8", errors='replace').rstrip('\x00')
                if mess:
                    new_idChaty.append(mess)
                else:
                    break

            except socket.timeout:
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
        with QtCore.QMutexLocker(self.mutex):
            self.receive_friends()
            self.load_friends()

    # Funkcja obslugujaca odbior znajomych od serwera
    def receive_friends(self):

        flag = 500
        self.client_socket.send(struct.pack("i", flag))
        self.client_socket.send(self.nick.encode('utf-8'))
        self.client_socket.settimeout(1)

        # Wyczyść listy znajomych
        self.nazwyZnajomi.clear()
        self.statusZnajomi.clear()
        while True:
            try:
                mess = self.client_socket.recv(1024).decode("utf-8",errors='replace')
                cleaned_mess = mess.replace('\x00', '').strip()
                if cleaned_mess:
                    self.nazwyZnajomi.append(cleaned_mess)
                else:
                    break

                if mess:
                    mess = self.client_socket.recv(1024).decode("utf-8",errors='replace')
                    cleaned_mess = mess.replace('\x00', '').strip()
                    self.statusZnajomi.append(cleaned_mess)
                else:
                    print("Server disconnected")
                    break

            except socket.timeout:
                break
            except Exception as e:
                print(f"An error occurred while receiving friends: {e}")
                break

    # Funkcja obslugujaca odswiezenie okna
    def load_friends(self):

        friend_requests = 0
        
        # Czyszczenie wszystkich boxów i listy
        self.comboBox.clear()
        self.listView.clear()
        self.nick1Input.clear()
        self.nick2Input.clear()

        for i in range(len(self.statusZnajomi)):

            if self.statusZnajomi[i] == 'f':
                self.listView.addItem(self.nazwyZnajomi[i])
                self.nick1Input.addItem(self.nazwyZnajomi[i])
                self.nick2Input.addItem(self.nazwyZnajomi[i])

            elif self.statusZnajomi[i] == 'n':
                self.comboBox.addItem(self.nazwyZnajomi[i])
                friend_requests += 1

            else:
                pass

        # Aktualizacja liczby zaproszeń
        self.label_2.setText(str(friend_requests))
