import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '127.0.0.1'
server_port = 1100

try:
    # Łączenie z serwerem
    client_socket.connect((server_address, server_port))
    print("Successfully connected to server.")

    # Odbieranie wiadomości od serwera
    buffer = client_socket.recv(1024).decode()
    print("Message from server: ",buffer)

    while True:
        message = input("\nEnter message to send to server: (or 'exit' to quit): ")

        # Obsługa 'exit'
        if message.lower() == 'exit':
            print("Closing connection...")
            break

        # Wysyłanie wiadomości do serwera
        client_socket.send(message.encode())

        # Odbieranie wiadomości od serwera
        buffer = client_socket.recv(1024).decode()
        print("Message from client: ",buffer)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Zamknięcie połączenia
    client_socket.close()