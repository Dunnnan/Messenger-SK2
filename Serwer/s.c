#include<stdio.h>
#include<stdlib.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<string.h>
#include <arpa/inet.h>
#include<sys/select.h>

#include <fcntl.h>

void color(const char *color) {
    if (color == "red") {
        printf("\033[0;31m");
    } else if (color == "green") {
        printf("\033[0;32m");
    } else if (color == "yellow") {
        printf("\033[0;33m");
    } else if (color == "blue") {
        printf("\033[0;34m");
    } else {
        printf("\033[0m");
    }
}

void setnonblock(int socket) {
    int flag = fcntl(socket, F_GETFL, 0);

    if (fcntl(socket, F_SETFL, flag | O_NONBLOCK) == -1){
        perror("Failure setting nonblock");
        exit(EXIT_FAILURE);
    }
}

int main(){
    int serverSocket;
    char buffer[1024];
    struct sockaddr_in serverAddr;

    serverSocket = socket(AF_INET, SOCK_STREAM, 0);

    memset(&serverAddr,0,sizeof serverAddr);
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(1100);
    serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);


    setnonblock(serverSocket);
    bind(serverSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));

    listen(serverSocket,5);

    fd_set current_sockets, read_sockets, write_sockets;
    FD_ZERO(&current_sockets);
    FD_SET(serverSocket, &current_sockets);

    //set fd_sets !!!

    int client_socket;

    printf("Waiting for clients !\n");
    for(;;){
	    read_sockets = current_sockets;
        write_sockets = current_sockets;

        select(FD_SETSIZE,&read_sockets, &write_sockets, NULL, NULL);

        for (int i = 0; i < FD_SETSIZE; i++){
            if (FD_ISSET(i, &read_sockets)){
                if (i == serverSocket){
                    client_socket=accept(serverSocket,NULL,NULL);

                    setnonblock(client_socket);

                    FD_SET(client_socket,&current_sockets);

                    color("green"); printf("New client connected\n"); color("reset");

                    printf("Sending handshake \n");
                    send(client_socket,"hello world",12,0);

                }
                else {
                    // Odczytanie wiadomości od klienta
                    int message = recv(i, buffer, sizeof(buffer), 0);

                    if (message <= 0) {
                        close(i);
                        FD_CLR(i, &current_sockets);
                        printf("Client disconnected\n");
                    } else {
                        // Wyswietlenie odebranej wiadomości
                        color("yellow"); printf("Received from client: %s\n", buffer); color("reset");
                        // Odpowiedź do klienta
                        send(i, "Message received", 17, 0);
                        memset(&buffer,0,sizeof(buffer));
                    }
                }
            }
        }
    }
    close(serverSocket);
    return 0;
}

