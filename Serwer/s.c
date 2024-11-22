#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<unistd.h>

#include<sys/socket.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<sys/select.h>
#include<pthread.h>
#include<fcntl.h>

#define PORT 1100
#define BUFFER_SIZE 1024
#define HISTORY_FILE "chat_history.txt"

pthread_mutex_t file_mutex;

typedef struct message{
    int flag;
} order;

void *handle_client(void *socket_desc){
    int client_socket = *(int *)socket_desc;
    free(socket_desc);
    char buffer[BUFFER_SIZE];
    int read_size = -2;
    int action = 1;
    int a = 10;


    while (1){
        // Przyjęcie żądania
        read_size = recv(client_socket,&action,sizeof(action),0);
        // Czyszczenie bufora
        bzero(buffer,BUFFER_SIZE);
        // Debug
        printf("action: %d \n",action);

        // Obsługa żądań klienta
        if (action == -1){
            color("blue"); ("Exit \n"); color("reset");
            break;
        }

        else if (action == 100){
            color("blue"); printf("signup \n"); color("reset");
        }

        else if (action == 200){
            color("blue"); printf("login \n"); color("reset");
        }

        else if (action == 300){
            color("blue"); printf("main \n"); color("reset");
        }

        else if (action == 400){
            color("blue"); printf("chat \n"); color("reset");
            // Wysłanie historii chatu do klienta
            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(HISTORY_FILE, "r");
            if (file != NULL){
                while (fgets(buffer, BUFFER_SIZE, file) != NULL){
                    send(client_socket, buffer, strlen(buffer), 0);
                }
                fclose(file);
            }
            pthread_mutex_unlock(&file_mutex);
        }

        else if (action == 500){
            color("blue"); printf("friends \n"); color("reset");
        }

        else if (action == 600){
            color("blue"); printf("search \n"); color("reset");
        }

        else if (action == 700){
            color("blue"); printf("invite \n"); color("reset");
        }

        else if (action == 800){
            color("blue"); printf("group \n"); color("reset");
        }

        else if (action == 0){
            color("blue"); printf("Saving messages to file: 'chat.txt' \n"); color("reset");
            // Odbieranie wiadomości od klienta i zapisywanie do pliku (chatu)
            read_size = recv(client_socket,buffer,BUFFER_SIZE,0);
                 buffer[read_size] = '\0';

                 printf("Zapisuję wiadomość: %d %s\n",a,buffer);
                 a += 10;

                pthread_mutex_lock(&file_mutex);
                FILE *file = fopen(HISTORY_FILE, "a");
                if (file != NULL){
                    fprintf(file, "%s\n", buffer);
                    fclose(file);
                }
                pthread_mutex_unlock(&file_mutex);
        }

        // Obsługa przesłanych wiadomości (errors)
        if (read_size == 0){
            printf("Client disconnected \n");
        }
        else if (read_size == -1){
            color("red"); perror("recv failed"); color("reset");
        }
        else if (read_size == -2){
            printf("read_size not changed");
        }
    }
    // Zamykanie gniazda
    printf("Closing client socket ! \n");
    close(client_socket);
    return 0;
}

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
/*
void setnonblock(int socket) {
    int flag = fcntl(socket, F_GETFL, 0);

    if (fcntl(socket, F_SETFL, flag | O_NONBLOCK) == -1){
        perror("Failure setting nonblock");
        exit(EXIT_FAILURE);
    }
}
*/
int main(){
    int serverSocket, client_socket, *new_socket;
    char buffer[1024];
    struct sockaddr_in serverAddr, clientAddr;
    socklen_t client_len = sizeof(struct sockaddr_in);

    // Inicjalizacja mutexu
    pthread_mutex_init(&file_mutex,NULL);

    serverSocket = socket(AF_INET, SOCK_STREAM, 0);

    memset(&serverAddr,0,sizeof serverAddr);
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(1100);
    serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);

    bind(serverSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr));

    listen(serverSocket,5);

    color("blue"); printf("Server starting work.\n"); color("reset");
    // Nasłuchiwanie na gnieździe serwera
    while ((client_socket = accept(serverSocket, (struct sockaddr *)&clientAddr, &client_len))){
        color("green"); printf("New client connected\n"); color("reset");

        pthread_t client_thread;
        new_socket = malloc(sizeof(int));
        *new_socket = client_socket;

        // Tworzenie wątku
        pthread_create(&client_thread, NULL, handle_client, (void *)new_socket);
        pthread_detach(client_thread);
    }

    // Wyjście
    pthread_mutex_destroy(&file_mutex);
    close(serverSocket);
    return 0;
}

