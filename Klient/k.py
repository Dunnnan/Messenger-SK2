import socket
import threading
import struct

server_address = "127.0.0.1"
server_port = 1100

class Message:
    def __init__(self,flag):
        self.flag = flag

    def to_bytes(self):
        return struct.pack("i",self.flag)

def action(action):
    if action == "signup":
        # 1 Tworzenie konta
        action = 100
    elif action == "login":
        # 2 Logowanie
        action = 200
    elif action == "main":
        # 3 Strona Główna
        action = 300
    elif action == "chat":
        # 4 Chat
        action = 400
    elif action == "friends":
        # 5 Wyświetlanie znajomych
        action = 500
    elif action == "search":
        # 6 Wyszukiwanie znajomych
        action = 600
    elif action == "invite":
        # 7 Dodawanie znajomych
        action = 700
    elif action == "group":
        # 8 Grupowa konwersacja
        action = 800

    elif action == "message":
        # 0 Debug
        action = 0

    else:
        # -1 Exit
        return(-1)

    return(action)

def receive_friends(client_socket,nazwyZnajomi,statusZnajomi):
    client_socket.settimeout(1)

    # Wyczyść listy znajomych
    nazwyZnajomi.clear()
    statusZnajomi.clear()

    while True:
        try:
            mess = client_socket.recv(1024).decode("utf-8",errors='replace')
            if mess:
                print(f"friend: {mess}")
                nazwyZnajomi.append(mess)
            else:
                print("Server disconnected")
                break

            if mess:
                mess = client_socket.recv(1024).decode("utf-8",errors='replace')
                print(f"status: {mess}")
            else:
                print("Server disconnected")
                break

        except socket.timeout:
            if not nazwyZnajomi:
                print("\033[31mUżytkownik nie posiada żadnych znajomych !\033[0m")
            print("Server timed out")
            break
        except Exception as e:
            print(f"An error occurred while receiving friends: {e}")
            break

def receive_history(client_socket,nazwyChaty,idChaty):
    client_socket.settimeout(1)

    # Wyczyść listy chatów
    nazwyChaty.clear()
    idChaty.clear()

    while True:
        try:
            # Odbierz nazwy chatów
            mess = client_socket.recv(1024).decode("utf-8",errors='replace')
            if mess:
                print(f"chat: {mess}")
                nazwyChaty.append(mess)
            else:
                print("Server disconnected")
                break

            # Odbierz identyfikatory chatów
            mess = client_socket.recv(1024).decode("utf-8",errors='replace')
            if mess:
                print(f"chat: {mess}")
                idChaty.append(mess)
            else:
                print("Server disconnected")
                break

        except socket.timeout:
            if not nazwyChaty:
                print("\033[31mUżytkownik nie posiada żadnych chatów !\033[0m")
            print("Receiving history timed out")
            break
        except Exception as e:
            print(f"An error occured while receiving history: {e}")
            break

def receive_message(client_socket):
    client_socket.settimeout(1)
    while True:
        try:
            mess = client_socket.recv(1024).decode('utf-8',errors='replace') #char
            if mess:
                print(f"Server: {mess}")
            else:
                print("Server disconnected")
                break
        except socket.timeout:
            print("Receiving message timed out")
            break
        except Exception as e:
            print(f"An error occured while receiving message: {e}")
            break

def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_address, server_port))
        print("Connected to the server")
    except Exception as e:
        print(f"Could not connect to the server {e}")

    while True:

        # Choose action
        try:
            #print("\033[33mChoose action:\033[0m\n(1) signup\n(2) login\n(3) main\n(4) chat\n(5) friends\n(6) search\n(7) invite\n(8) group\n(9) message\n(-1) exit\n")
            print("\033[33mChoose action:\033[0m (1) signup, (2) login, (3) main, (4) chat, (5) friends, (6) search, (7) invite, (8) group, (9) message, (-1) exit")
            act = input()
            flag = action(act)
        except Exception as e:
            print(f"An error occured while sending action: {e}")
            break

        try:
            client_socket.send(struct.pack("i",flag))
        except Exception as e:
            print(f"An error occured while sending action: {e}")
            break



        # Act on action
        if act == "signup":
            # 1. Tworzenie konta
            name = input("Podaj imię:")
            client_socket.send(name.encode('utf-8'))

            surname = input("Podaj Nazwisko: ")
            client_socket.send(surname.encode('utf-8'))

            nick = input("Podaj nazwę użytkownika:")
            client_socket.send(nick.encode('utf-8'))

            password = input("Podaj hasło:")
            client_socket.send(password.encode('utf-8'))

            data = client_socket.recv(4)
            if data:
                mess = struct.unpack('<i', data)[0]
            if mess == 110:
                print("\033[33mKonto o podanym nicku już istnieje!\033[0m")
            elif mess == 120:
                print("\033[33mPomyślnie utworzono konto użytkownika!\033[0m")



        elif act == "login":
            # 2. Logowanie
            nick = input("Podaj nazwę użytkownika:")
            client_socket.send(nick.encode('utf-8'))

            password = input("Podaj hasło:")
            client_socket.send(password.encode('utf-8'))

            data = client_socket.recv(4)
            if data:
                mess = struct.unpack('<i', data)[0]
            if mess == 210:
                print("Konto o podanym nicku nie istnieje !")
            elif mess == 220:
                print("Wprowadzono niepoprawne hasło !")
            elif mess == 230:
                print("Pomyślnie zalogowano !")



        elif act == "main":
            # 3. Strona Główna
            try:
                print("\033[33mPodaj swój nick: \033[0m")
                # W przyszłości nick będzie przypisywany na etapie tworzenia konta / logowania
                nick = input()
                client_socket.send(nick.encode('utf-8'))

                # Zainicjuj listy na chaty użytkownika
                nazwyChaty = []
                idChaty = []

                # Otwórz wątek do odbierania chatów użytkownika
                receive_thread = threading.Thread(target=receive_history, args=(client_socket,nazwyChaty,idChaty,))
                receive_thread.start()
                receive_thread.join()

            except Exception as e:
                print(f"An error occured while opening the history thread: {e}")
                break



        elif act == "chat":
            # 4. Chat
            try:
                print("\033[33mWaiting for chat history receiving \033[0m")
                # Oczekiwanie na wiadomość
                receive_thread = threading.Thread(target=receive_message, args=(client_socket,))
                receive_thread.start()
                receive_thread.join()
            except Exception as e:
                print(f"An error occurred while chatting: {e}")
                break

        elif act == "friends":
            # 5. Wyświetlanie znajomych
            try:
                print("\033[33mPodaj swój nick: \033[0m")
                # W przyszłości nick będzie przypisywany na etapie tworzenia konta / logowania
                nick = input()
                client_socket.send(nick.encode('utf-8'))

                nazwyZnajomi = []
                statusZnajomi = []

                receive_thread = threading.Thread(target=receive_friends, args=(client_socket,nazwyZnajomi,statusZnajomi,))
                receive_thread.start()
                receive_thread.join()
            except Exception as e:
                print(f"An error occured while receiving friends: {e}")
                break

        elif act == "search":
            # 6. Wyszukiwanie znajomych
            print("\033[33mImplement friend search here: \033[0m")

        elif act == "invite":
            # 7. Dodawanie znajomych
            print("\033[33mImplement friend invite here: \033[0m")

        elif act == "group":
            # 8. Grupowa konwersacja
            print("\033[33mImplement group chat here: \033[0m")

        elif act == "message":
            # 0. Debug
            print("\033[33mWaiting for message: \033[0m")
            message = input()
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred while sending message: {e}")
                break

        elif act == "exit":
            print("\033[34mExiting the program \033[0m")
            break

    client_socket.close()
    print("Disconnected")

if __name__ == "__main__":
    main()