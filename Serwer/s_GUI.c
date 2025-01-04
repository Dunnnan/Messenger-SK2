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


// Zmienne globalne
#define PORT 1100
#define BUFFER_SIZE 1024
#define HISTORY_FILE "chat_history.txt"
#define LOGIN_FILE "users.txt"

// Zmienne do przetwarzania "users.txt"
int name_index = 0;
int surname_index = 1;
int nick_index = 2;
int password_index = 3;
int columns = 4;

// Zmienne do przetwarzania "nick_chats.txt"
int chatname_index = 0;
int chathistory_index = 1;
int p_columns = 2;

// Zmienne do przetwarzania "nick_friends.txt"
int invitation_index = 0;
int username_index = 0;
int f_columns = 2;

// Zmienne do przetwarzania "chat_history.txt"


pthread_mutex_t file_mutex;

// Funkcje pomocnicze
void gs(int client_socket, char *buffer, char *buffer2, size_t size) {
    // Zerowanie buforów
    bzero(buffer, size);
    bzero(buffer2, size);

    // Odbieranie danych
    ssize_t received_bytes = recv(client_socket, buffer, size, 0);
    if (received_bytes > 0) {
        // Kopiowanie danych do drugiego bufora
        strncpy(buffer2, buffer, size - 1); // Dodaj -1 dla miejsca na null-terminator
    } else {
        // Obsługa błędu lub zakończenia połączenia
        perror("recv failed or connection closed");
    }
}

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
        int n;
        n=read_size = recv(client_socket,&action,sizeof(action),0);
        printf("Liczba bajtow: %d\n", n);
        // Czyszczenie bufora
        bzero(buffer,BUFFER_SIZE);
        // Debug
        printf("action: %d \n",action);

        // Obsługa żądań klienta
        if (action == -1){
            color("blue"); printf("Exit \n"); color("reset");
            break;
        }

        else if (action == 100){
            color("blue"); printf("signup \n"); color("reset");

            // Inicjalizacja buforów
            char name[BUFFER_SIZE];     bzero(name,sizeof(name));
            char surname[BUFFER_SIZE];  bzero(surname,sizeof(surname));
            char nick[BUFFER_SIZE];     bzero(nick,sizeof(nick));
            char password[BUFFER_SIZE]; bzero(password,sizeof(password));

            // Odebranie danych
            recv(client_socket,name,sizeof(name),0);
            recv(client_socket,surname,sizeof(surname),0);
            recv(client_socket,nick,sizeof(nick),0);
            recv(client_socket,password,sizeof(password),0);

            int flag = 0;
            char line[BUFFER_SIZE * columns];
            char column[BUFFER_SIZE];
            int column_index = nick_index;

            // Test unikalności nicku
            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(LOGIN_FILE, "r");
            while(fgets(line,sizeof(line),file)){
                char *token = strtok(line,",");
                int current_index = 0;

                while(token){
                    if (current_index == column_index){
                        strncpy(column, token, BUFFER_SIZE-1);
                        column[BUFFER_SIZE-1] = '\0';

                        column[strcspn(column,"\r\n")] = '\0';
                        if(strcmp(column, nick) == 0){
                            flag = 110;
                            break;
                        }
                    }
                    token = strtok(NULL,",");
                    current_index += 1;
                }
                if (flag == 110){
                    break;
                }
            }
            if (flag == 110){
                send(client_socket, &flag, sizeof(flag), 0);
                color("red"); printf("Konto o tym nicku już istnieje.\n"); color("reset");
                fclose(file);
                pthread_mutex_unlock(&file_mutex);
            }
            else{
                flag = 120;
                send(client_socket, &flag, sizeof(flag), 0);
                color("green"); printf("Stworzono nowe konto.\n"); color("reset");
                fclose(file);
                FILE *file = fopen(LOGIN_FILE,"a");
                    if (file != NULL){
                        fprintf(file, "%s,%s,%s,%s\n", name, surname, nick, password);
                        fclose(file);
                    }
                pthread_mutex_unlock(&file_mutex);
            }
        }

        else if (action == 200){
            color("blue"); printf("login \n"); color("reset");

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];     bzero(nick,sizeof(nick));
            char password[BUFFER_SIZE]; bzero(password,sizeof(password));

            // Odebranie danych
            int n1, n2;
            char a='a';
            n1=recv(client_socket,nick,sizeof(nick),0);
            printf("DLugosc pierwszej wiadomosci: %d\n", n1);
            printf("Wiadomosc: %s\n", nick);
            n2=recv(client_socket,password,sizeof(password),0);
            printf("DLugosc drugiej wiadomosci: %d\n", n2);
            printf("Wiadomosc: %s\n", password);

            if (n1==0 || n2 ==0) {
                nick[BUFFER_SIZE]="asdasda";
                password[BUFFER_SIZE]="asdssadasdadsasd";
            }


            int flag = 210;
            char line[BUFFER_SIZE * columns];
            char column[BUFFER_SIZE];
            int column_index1 = nick_index;
            int column_index2 = password_index;

            // Test unikalności nicku
            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(LOGIN_FILE, "r");
            while(fgets(line,sizeof(line),file)){
                char *token = strtok(line,",");
                int current_index = 0;

                while(token){
                    if (current_index == column_index1){
                        strncpy(column, token, BUFFER_SIZE-1);
                        column[BUFFER_SIZE-1] = '\0';

                        column[strcspn(column,"\r\n")] = '\0';


                        if(strcmp(column, nick) == 0){
                            token = strtok(NULL,",");
                            strncpy(column, token, BUFFER_SIZE-1);
                            current_index += 1;

                            column[BUFFER_SIZE-1] = '\0';
                            column[strcspn(column,"\r\n")] = '\0';
                            printf("%s,%s\n", column,password);
                            if(strcmp(column, password) == 0){
                                flag = 230;
                                break;
                            }
                            else{
                                flag = 220;
                                break;
                            }
                        }
                    }
                    token = strtok(NULL,",");
                    current_index += 1;
                }
                if (flag == 220 || flag == 230){
                    break;
                }
            }
            fclose(file);
            pthread_mutex_unlock(&file_mutex);

            if (flag == 210){
                send(client_socket, &flag, sizeof(flag), 0);
                color("red"); printf("Nick nie istnieje.\n"); color("reset");
            }
            else if (flag == 220){
                send(client_socket, &flag, sizeof(flag), 0);
                color("red"); printf("Niepoprawne hasło.\n"); color("reset");
            }
            else if (flag == 230){
                send(client_socket, &flag, sizeof(flag), 0);
                color("green"); printf("Zalogowano.\n"); color("reset");
            }
        }

        else if (action == 300){
            color("blue"); printf("main \n"); color("reset");
            char nick[1048]; bzero(nick,sizeof(nick));
            char filepath[2200]; bzero(filepath,sizeof(filepath)); strcpy(filepath,"users/");
            char buffer[BUFFER_SIZE]; bzero(buffer,sizeof(buffer));

            recv(client_socket,nick,sizeof(nick),0);

            int flag = 320;
            char line[BUFFER_SIZE * p_columns];
            char column[BUFFER_SIZE];


            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(strcat(filepath,strcat(nick,".txt")),"a+");
            printf("tutaj\n");
            if (file != NULL){
                while(fgets(line,sizeof(line), file)){

                    char *token = strtok(line,",");

                    strncpy(column, token, BUFFER_SIZE-1);
                    column[BUFFER_SIZE-1] = '\0';
                    column[strcspn(column, "\r\n")] = '\0';

                    send(client_socket,column,sizeof(column),0);

                    token = strtok(NULL,",");

                    strncpy(column,token, BUFFER_SIZE-1);
                    column[BUFFER_SIZE-1] = '\n';
                    column[strcspn(column, "\r\n")] = '\0';

                    int n=send(client_socket,column,sizeof(column),0);
                    printf("%d\n", n);
                    flag = 310;
                }
            }

            fclose(file);
            pthread_mutex_unlock(&file_mutex);

            if (flag == 310){
                color("green"); printf("Przesłano chaty użytkownika.\n"); color("reset");
            }
            else if (flag == 320){
                color("red"); printf("Użytkownik nie posiada żadnych chatów.\n"); color("reset");
            }

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

            char nick[1048]; bzero(nick,sizeof(nick));
            char filepath[2200]; bzero(filepath,sizeof(filepath)); strcpy(filepath,"friends/");
            char buffer[BUFFER_SIZE]; bzero(buffer,sizeof(buffer));

            recv(client_socket,nick,sizeof(nick),0);

            int flag = 520;

            char line[BUFFER_SIZE * f_columns];
            char column[BUFFER_SIZE];

            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(strcat(filepath,strcat(nick,".txt")),"a+");
            if (file != NULL){
                while(fgets(line,sizeof(line), file)){

                    char *token = strtok(line,",");

                    printf("TOKEN: \n");

                    strncpy(column, token, BUFFER_SIZE-1);
                    printf("column: %s \n",column);
                    column[BUFFER_SIZE-1] = '\0';
                    column[strcspn(column, "\r\n")] = '\0';

                    send(client_socket,column,sizeof(column),0);

                    token = strtok(NULL,",");

                    strncpy(column,token, BUFFER_SIZE-1);
                    printf("column: %s \n",column);
                    column[BUFFER_SIZE-1] = '\0';
                    column[strcspn(column, "\r\n")] = '\0';

                    send(client_socket,column,sizeof(column),0);

                    flag = 510;
                }
            }

            fclose(file);
            pthread_mutex_unlock(&file_mutex);

            if (flag == 510){
                color("green"); printf("Przesłano znajomych użytkownika.\n"); color("reset");
            }
            else if (flag == 520){
                color("red"); printf("Użytkownik nie posiada żadnych znajomych.\n"); color("reset");
            }

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

