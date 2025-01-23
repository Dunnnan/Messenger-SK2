#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<unistd.h>
#include<stdbool.h>

#include<sys/socket.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<sys/select.h>
#include<pthread.h>
#include<fcntl.h>
#include<ctype.h>
#include<signal.h>

// Zmienne globalne
#define PORT 1100
#define BUFFER_SIZE 1024
#define BUFFER_2_SIZE 2148
#define LOGIN_FILE "users.txt"

#define GROUP_NUMBER 3

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
int username_index = 0;
int invitation_index = 1;
int f_columns = 2;

// Mutexy
pthread_mutex_t file_mutex;
pthread_mutex_t login_mutex;

// Funkcje pomocnicze
// Wielobarwne printf
void color(const char *color) {
    if (strcmp(color,"red") == 0) {
        printf("\033[0;31m");
    } else if (strcmp(color,"green") == 0) {
        printf("\033[0;32m");
    } else if (strcmp(color,"yellow") == 0) {
        printf("\033[0;33m");
    } else if (strcmp(color,"blue") == 0) {
        printf("\033[0;34m");
    } else {
        printf("\033[0m");
    }
}

// Min()
int min(int a, int b, int c) {
    if (a < b && a < c) return a;
    if (b < c) return b;
    return c;
}

// Wyszukiwarka użytkowników
int simpleComparator(const char b1[BUFFER_SIZE], const char b2[BUFFER_SIZE]) {
    int diff = 0;
    int i = 0;
    while (b1[i] != '\0' && b2[i] != '\0') {
        if (tolower(b1[i]) == tolower(b2[i])) {
            diff += 1;
        }
        i++;
    }
    return diff;
}

// Kopiuje tempfilepath do filepath
void overwrite(char *filepath, char *tempfilepath) {
    FILE *file = fopen(filepath,"w");
    FILE *tempfile = fopen(tempfilepath,"a+");
    char line[BUFFER_SIZE * f_columns]; bzero(line,sizeof(line));
    while (fgets(line, sizeof(line), tempfile)) {
        fprintf(file, "%s", line);
    }
    fclose(file);
    fclose(tempfile);
}


// Czy *buffer* istnieje w *filepath*, w kolumnie *column_index*
bool existsInColumn(char *filepath, char buffer[BUFFER_SIZE], int column_index) {
    char line[BUFFER_SIZE];
    bool found = false;
    
    pthread_mutex_lock(&file_mutex);
    FILE *file = fopen(filepath, "r");

    if (file != NULL){
        while (fgets(line, sizeof(line), file)) {
            char *token;
            int current_column = 0;

            token = strtok(line, ",");
            while (token != NULL) {
                if (current_column == column_index) {
                    token[strcspn(token, "\r\n")] = '\0';

                    if (strcmp(token, buffer) == 0) {
                        found = true;
                    }
                    break;
                }
                token = strtok(NULL, ",");
                current_column++;
            }

            if (found) {
                break;
            }
        }
    }
    fclose(file);
    pthread_mutex_unlock(&file_mutex);
    return found;
}

void *handle_client(void *socket_desc){
    int client_socket = *(int *)socket_desc;
    free(socket_desc);
    int read_size = -2;
    int action = 1;

    // Pętla główna
    while (1){
        read_size = recv(client_socket,&action,sizeof(action),0);
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
            if (
                recv(client_socket,name,sizeof(name),0)         == -1  ||
                recv(client_socket,surname,sizeof(surname),0)   == -1  ||
                recv(client_socket,nick,sizeof(nick),0)         == -1  ||
                recv(client_socket,password,sizeof(password),0) == -1
                ) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 0;
            char line[BUFFER_SIZE * columns];
            char column[BUFFER_SIZE];

            // Test unikalności nicku
            pthread_mutex_lock(&login_mutex);
            FILE *file = fopen(LOGIN_FILE, "r");
            
            // Iteruj linie
            while(fgets(line,sizeof(line),file)){
                char *token = strtok(line,",");
                int current_index = 0;

                // Iteruj kolumny
                while(token){
                    if (current_index == nick_index){
                        strncpy(column, token, BUFFER_SIZE-1);
                        column[BUFFER_SIZE-1] = '\0';
                        column[strcspn(column,"\r\n")] = '\0';
                        if(strcmp(column, nick) == 0){
                            // Nick nieunikalny
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
                pthread_mutex_unlock(&login_mutex);
            }
            else{
                flag = 120;
                send(client_socket, &flag, sizeof(flag), 0);
                color("green"); printf("Stworzono nowe konto.\n"); color("reset");
                fclose(file);

                // Dodaj użytkownika do systemu
                FILE *file = fopen(LOGIN_FILE,"a");
                    if (file != NULL){
                        fprintf(file, "%s,%s,%s,%s\n", name, surname, nick, password);
                        fclose(file);
                    }
                pthread_mutex_unlock(&login_mutex);
            }
        }

        else if (action == 200){
            color("blue"); printf("login \n"); color("reset");

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];     bzero(nick,sizeof(nick));
            char password[BUFFER_SIZE]; bzero(password,sizeof(password));

            // Odebranie danych
            if (
                recv(client_socket,nick,sizeof(nick),0)           == -1  ||
                recv(client_socket,password,sizeof(password),0)   == -1 
                ) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 210;
            char line[BUFFER_SIZE * columns];
            char column[BUFFER_SIZE];

            // Test istnienia danych
            pthread_mutex_lock(&login_mutex);
            FILE *file = fopen(LOGIN_FILE, "r");

            // Iteruj linie
            while(fgets(line,sizeof(line),file)){
                char *token = strtok(line,",");
                int current_index = 0;

                // Iteruj kolumny
                while(token){
                    if (current_index == nick_index){
                        strncpy(column, token, BUFFER_SIZE-1);
                        column[BUFFER_SIZE-1] = '\0';
                        column[strcspn(column,"\r\n")] = '\0';

                        if(strcmp(column, nick) == 0){
                            token = strtok(NULL,",");
                            strncpy(column, token, BUFFER_SIZE-1);
                            column[BUFFER_SIZE-1] = '\0';
                            column[strcspn(column,"\r\n")] = '\0';
                            current_index += 1;

                            if(strcmp(column, password) == 0){
                                // Zalogowanie
                                flag = 230;
                                break;
                            }
                            else{
                                // Nieprawidłowe hasło
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
            pthread_mutex_unlock(&login_mutex);

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

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];         bzero(nick,sizeof(nick));
            char filepath[BUFFER_2_SIZE];   bzero(filepath,sizeof(filepath)); strcpy(filepath,"users/");
            char buffer[BUFFER_SIZE];       bzero(buffer,sizeof(buffer));

            // Odebranie danych
            if (recv(client_socket,nick,sizeof(nick),0) == -1) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 320;
            char line[BUFFER_SIZE * p_columns];
            char column[BUFFER_SIZE];

            // Przesłanie listy chatów użytkownika
            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(strcat(filepath,strcat(nick,".txt")),"a+");
            if (file != NULL){
                while(fgets(line,sizeof(line), file)){

                    // Prześlij nazwę chatu
                    char *token = strtok(line,",");
                    strncpy(column, token, BUFFER_SIZE-1);
                    column[BUFFER_SIZE-1] = '\0';
                    column[strcspn(column, "\r\n")] = '\0';
                    send(client_socket,column,sizeof(column),0);

                    // Prześlij identyfikator chatu
                    token = strtok(NULL,",");
                    strncpy(column, token, BUFFER_SIZE-1);
                    column[BUFFER_SIZE-1] = '\0';
                    column[strcspn(column, "\r\n")] = '\0';
                    send(client_socket,column,sizeof(column),0);

                }
                    // Wysłano wszystko
                    flag = 310;
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

            // Inicjalizacja buforów
            char chatName[GROUP_NUMBER * BUFFER_SIZE];     bzero(chatName,sizeof(chatName));
            char filepath[(GROUP_NUMBER+1) * BUFFER_SIZE]; bzero(filepath,sizeof(filepath));
            char buffer[BUFFER_SIZE];                      bzero(buffer,sizeof(buffer));

            // Odebranie danych
            if (recv(client_socket,chatName,sizeof(chatName),0) == -1) {
                break;
            }

            // Stworzenie ścieżki do chatu
            snprintf(filepath, sizeof(filepath), "%s%s.txt", "chats/", chatName);

            // Przesłanie historii chatu
            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(filepath, "r");
            if (file != NULL){
                while (fgets(buffer, BUFFER_SIZE, file) != NULL){
                    send(client_socket, buffer, strlen(buffer), 0);
                    bzero(buffer,sizeof(buffer));
                }
            }
            fclose(file);
            pthread_mutex_unlock(&file_mutex);
        }

        else if (action == 500){
            color("blue"); printf("friends \n"); color("reset");

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];       bzero(nick,sizeof(nick));
            char filepath[BUFFER_2_SIZE]; bzero(filepath,sizeof(filepath)); strcpy(filepath,"friends/");
            char buffer[BUFFER_SIZE];     bzero(buffer,sizeof(buffer));

            // Odebranie danych
            if (recv(client_socket,nick,sizeof(nick),0) == -1) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 520;
            char line[BUFFER_SIZE * f_columns];
            char column[BUFFER_SIZE];

            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(strcat(filepath,strcat(nick,".txt")),"a+");
            if (file != NULL){
                while(fgets(line,sizeof(line), file)){

                    char *token = strtok(line,",");
                    strncpy(column, token, BUFFER_SIZE-1);
                    column[BUFFER_SIZE-1] = '\0';
                    column[strcspn(column, "\r\n")] = '\0';
                    send(client_socket,column,sizeof(column),0);

                    token = strtok(NULL,",");
                    strncpy(column, token, BUFFER_SIZE-1);
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

            // Inicjalizacja buforów
            char selfnick[BUFFER_SIZE];   bzero(selfnick,sizeof(selfnick));
            char nick[BUFFER_SIZE];       bzero(nick,sizeof(nick));
            char buffer[BUFFER_SIZE];     bzero(buffer,sizeof(buffer));
            char filepath[BUFFER_2_SIZE]; bzero(filepath,sizeof(filepath)); strcpy(filepath,"friends/");

            // Odebranie danych
            if (
                recv(client_socket,selfnick,sizeof(selfnick),0) == -1  ||
                recv(client_socket,nick,sizeof(nick),0)         == -1 
                ) {
                break;
            }

            // Stworzenie ścieżki do pliku
            strcat(filepath,strcat(selfnick,".txt"));

            // Zmienne do przetwarzania pliku
            int flag = 610;
            char line[BUFFER_SIZE * columns];
            char column[BUFFER_SIZE];

            // Wyszukanie użytkownika
            pthread_mutex_lock(&login_mutex);
            FILE *file = fopen(LOGIN_FILE, "r");
            if (file != NULL){
                while(fgets(line,sizeof(line),file)){
                    char *token = strtok(line,",");
                    int current_index = 0;
                    int sim = 0;

                    bzero(buffer,sizeof(buffer));
                    while(token){
                        if (current_index == nick_index){
                            strncpy(column, token, BUFFER_SIZE);
                            strncpy(buffer, column, sizeof(column));

                            // oblicz stopień podobieństwa
                            sim = simpleComparator(column,nick);

                            // Prześlij nick
                            send(client_socket,buffer,sizeof(buffer),0);

                            // Prześlij stopień podobieństwa
                            send(client_socket,&sim,sizeof(sim),0);

                            if ( !(existsInColumn(filepath, buffer, username_index)) ){
                                // Nieznajomy || Niezaproszony użytkownik
                                send(client_socket,"n",1,0);
                            }
                            else{
                                // Znajomy || Zaproszony użytkownik
                                send(client_socket,"f",1,0);
                            }
                        }
                        token = strtok(NULL,",");
                        current_index += 1;
                    }
                }
            }
            fclose(file);
            pthread_mutex_unlock(&login_mutex);

            if (flag == 610){
                color("green"); printf("Przesłano nazwy użytkowników.\n"); color("reset");
            }
        }

        else if (action == 700){
            color("blue"); printf("invite \n"); color("reset");

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];       bzero(nick,sizeof(nick));
            char selfnick[BUFFER_SIZE];   bzero(selfnick,sizeof(selfnick));
            char friendnick[BUFFER_SIZE]; bzero(friendnick,sizeof(friendnick));
            char filepath[BUFFER_2_SIZE]; bzero(filepath,sizeof(filepath));

            // Odebranie danych
            if (
                recv(client_socket,selfnick,sizeof(selfnick),0)     == -1  ||
                recv(client_socket,friendnick,sizeof(friendnick),0) == -1 
                ) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 702;

            FILE *file = NULL;
            for (int i = 0; i < 2; i++){
                // Zapisanie zaproszenia u siebie i u znajomego
                // ( Sekwencyjnie, aby uniknąć deadlocków )
                if (i == 0){
                    bzero(nick,sizeof(nick));
                    strcpy(nick,friendnick);

                    pthread_mutex_lock(&file_mutex);
                    snprintf(filepath, sizeof(filepath), "%s%s.txt", "friends/", selfnick);
                    file = fopen(filepath,"a+");
                }
                else{
                    bzero(nick,sizeof(nick));
                    strcpy(nick,selfnick);

                    pthread_mutex_lock(&file_mutex);
                    snprintf(filepath, sizeof(filepath), "%s%s.txt", "friends/", friendnick);
                    file = fopen(filepath,"a+");
                }
                if (file != NULL){
                    flag = 701;
                    if (i == 0){
                        // Zaproszenie wysłane przez użytkownika
                        fprintf(file, "%s,m\n",nick);
                    }
                    else{
                        // Zaproszenie wysłane przez innego użytkownika
                        fprintf(file, "%s,n\n",nick);
                    }
                }

                fclose(file);
                pthread_mutex_unlock(&file_mutex);
            }
            if (flag == 701){
                color("green"); printf("Zaproszono użytkownika.\n"); color("reset");
            }
            else if (flag == 702){
                color("red"); printf("Nie udało się zaprosić użytkownika.\n"); color("reset");
            }
        }

        else if (action == 710){
            color("blue"); printf("accept \n"); color("reset");

            // PART 1 - Stworzenie znajomości
            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];             bzero(nick,sizeof(nick));
            char selfnick[BUFFER_SIZE];         bzero(selfnick,sizeof(selfnick));
            char friendnick[BUFFER_SIZE];       bzero(friendnick,sizeof(friendnick));
            char filepath[BUFFER_2_SIZE + 10];       bzero(filepath,sizeof(filepath));
            char tempfilepath[BUFFER_2_SIZE];   bzero(tempfilepath,sizeof(tempfilepath));

            // Odebranie danych
            if (
                recv(client_socket,selfnick,sizeof(selfnick),0)     == -1  ||
                recv(client_socket,friendnick,sizeof(friendnick),0) == -1 
                ) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 712;
            char line[BUFFER_SIZE * f_columns];
            char linecopy[BUFFER_SIZE * f_columns];

            FILE *file = NULL;
            FILE *tempfile = NULL;

            // Akceptacja zaproszenia u siebie i u znajomego
            // ( Sekwencyjnie, aby uniknąć deadlocków )
            for (int i = 0; i < 2; i++){
                if (i == 0){
                    bzero(nick,sizeof(nick));
                    strcpy(nick,friendnick);

                    pthread_mutex_lock(&file_mutex);
                    snprintf(filepath, sizeof(filepath), "%s%s.txt", "friends/", selfnick);
                    file = fopen(filepath,"a+");

                    snprintf(tempfilepath, sizeof(tempfilepath), "%s%s_temp.txt", "friends/", selfnick);
                    tempfile = fopen(tempfilepath,"w");

                }
                else{
                    bzero(nick,sizeof(nick));
                    strcpy(nick,selfnick);

                    pthread_mutex_lock(&file_mutex);
                    snprintf(filepath, sizeof(filepath), "%s%s.txt", "friends/", friendnick);
                    file = fopen(filepath,"a+");

                    snprintf(tempfilepath, sizeof(tempfilepath), "%s%s_temp.txt", "friends/", friendnick);
                    tempfile = fopen(tempfilepath,"w");

                }

                // Przekopiuj listę znajomych użytkownika do pliku tymczasowego
                if (file != NULL){
                    flag = 711;
                    while(fgets(line,sizeof(line), file)){
                        bzero(linecopy,sizeof(linecopy));
                        strcpy(linecopy,line);

                        char *token = strtok(line,",");
                        // Zmień zaproszenie na znajomość, jeżeli właściwy nick
                        if (strcmp(token, nick) == 0){
                            fprintf(tempfile, "%s,f\n",nick);
                        }
                        // Inaczej przekopiuj linię
                        else{
                            fprintf(tempfile, "%s", linecopy);
                        }
                    }
                }
                fclose(file);
                fclose(tempfile);

                // Nadpisz plik główny i usuń tymczasowy
                overwrite(filepath,tempfilepath);
                remove(tempfilepath);

                pthread_mutex_unlock(&file_mutex);
            }

            // PART 2 - Stworzenie chatu
            // Inicjalizacja buforów
            bzero(nick,sizeof(nick));
            bzero(filepath,sizeof(filepath));
            char temp[BUFFER_SIZE];         bzero(temp,sizeof(temp));
            char nicknames[2][BUFFER_SIZE]; bzero(nicknames,sizeof(nicknames));
            char chatName[BUFFER_2_SIZE];   bzero(chatName,sizeof(chatName));

            // Stwórz tablicę nicków
            strcpy(nicknames[0], selfnick);
            strcpy(nicknames[1], friendnick);

            // Posortuj tablicę nicków
            for (int i = 0; i < 2 - 1; i++) {
                for (int j = i + 1; j < 2; j++) {
                    if (strcmp(nicknames[i], nicknames[j]) > 0) {
                        strcpy(temp, nicknames[i]);
                        strcpy(nicknames[i], nicknames[j]);
                        strcpy(nicknames[j], temp);
                    }
                }
            }

            // Stwórz nazwę chatu
            for (int i = 0; i < 2; i++) {
                strcat(chatName, nicknames[i]);
                if (i < 2 - 1) {
                    strcat(chatName, "-");
                }
            }

            // Stwórz ścieżkę do chatu
            snprintf(filepath, sizeof(filepath), "%s%s.txt", "chats/", chatName);

            // Jeżeli taki chat już istniał to nie dopisuj go użytkownikom (jest już dopisany)
            if (access(filepath, F_OK) == 0) {
                continue;
            }

            file = fopen(filepath,"a+");
            fclose(file);

            // Zapisz chat użytkownikom
            for (int i = 0; i < 2; i++){
                bzero(nick,sizeof(nick));
                bzero(filepath,sizeof(filepath));
                if (i == 0){
                    strcpy(nick,selfnick);
                }
                else{
                    strcpy(nick,friendnick);
                }

                pthread_mutex_lock(&file_mutex);
                snprintf(filepath, sizeof(filepath), "%s%s.txt", "users/", nick);
                FILE *file = fopen(filepath,"a+");
                if (file != NULL){
                    if (i == 0){
                        fprintf(file, "%s,%s\n",friendnick,chatName);
                    }
                    else{
                        fprintf(file, "%s,%s\n",selfnick,chatName);
                    }
                }
                fclose(file);
                pthread_mutex_unlock(&file_mutex);
            }
            if (flag == 711){
                color("green"); printf("Zaakceptowano zaproszenie.\n"); color("reset");
            }
            else if (flag == 712){
                color("red"); printf("Nie zaakceptowano zaproszenia.\n"); color("reset");
            }
        }

        else if (action == 720){
            color("blue"); printf("remove \n"); color("reset");

            // Inicjalizacja danych
            char nick[BUFFER_SIZE];           bzero(nick,sizeof(nick));
            char selfnick[BUFFER_SIZE];       bzero(selfnick,sizeof(selfnick));
            char friendnick[BUFFER_SIZE];     bzero(friendnick,sizeof(friendnick));
            char filepath[BUFFER_2_SIZE];     bzero(filepath,sizeof(filepath));
            char tempfilepath[BUFFER_2_SIZE]; bzero(tempfilepath,sizeof(tempfilepath));

            // Odebranie danych
            if (
                recv(client_socket,selfnick,sizeof(selfnick),0)     == -1  ||
                recv(client_socket,friendnick,sizeof(friendnick),0) == -1 
                ) {
                break;
            }

            // Zmienne do przetwarzania pliku
            int flag = 722;
            char line[BUFFER_SIZE * f_columns];
            char linecopy[BUFFER_SIZE * f_columns];

            FILE *file = NULL;
            FILE *tempfile = NULL;

            // Odrzucenie zaproszenia u siebie i u znajomego
            // ( Sekwencyjnie, aby uniknąć deadlocków )
            for (int i = 0; i < 2; i++){
                if (i == 0){
                    bzero(nick,sizeof(nick));
                    strcpy(nick,friendnick);

                    pthread_mutex_lock(&file_mutex);
                    snprintf(filepath, sizeof(filepath), "%s%s.txt", "friends/", selfnick);
                    file = fopen(filepath,"a+");

                    snprintf(tempfilepath, sizeof(tempfilepath), "%s%s_temp.txt", "friends/", selfnick);
                    tempfile = fopen(tempfilepath,"w");

                }
                else{
                    bzero(nick,sizeof(nick));
                    strcpy(nick,selfnick);

                    pthread_mutex_lock(&file_mutex);
                    snprintf(filepath, sizeof(filepath), "%s%s.txt", "friends/", friendnick);
                    file = fopen(filepath,"a+");

                    snprintf(tempfilepath, sizeof(tempfilepath), "%s%s_temp.txt", "friends/", friendnick);
                    tempfile = fopen(tempfilepath,"w");

                }
                
                // Przekopiuj listę znajomych użytkownika do pliku tymczasowego
                if (file != NULL){
                    flag = 721;
                    while(fgets(line,sizeof(line), file)){
                        bzero(linecopy,sizeof(linecopy)); strcpy(linecopy,line);

                        char *token = strtok(line,",");
                        if (strcmp(token, nick) == 0){
                            // Nie zapisuj zaproszenia jeśli właściwy nick                                                
                            continue;
                        }
                        else{
                            // Inaczej przekopiuj linię
                            fprintf(tempfile, "%s", linecopy);
                        }
                    }
                }
                fclose(file);
                fclose(tempfile);

                // Nadpisz plik główny i usuń tymczasowy
                overwrite(filepath,tempfilepath);
                remove(tempfilepath);

                pthread_mutex_unlock(&file_mutex);
            }
            if (flag == 721){
                color("green"); printf("Odrzucono zaproszenia.\n"); color("reset");
            }
            else if (flag == 722){
                color("red"); printf("Użytkownik nie posiada żadnych zaproszeń do odrzucenia.\n"); color("reset");
            }
        }

        else if (action == 800){
            color("blue"); printf("group \n"); color("reset");

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];                        bzero(nick,sizeof(nick));
            char selfnick[BUFFER_SIZE];                    bzero(selfnick,sizeof(selfnick));
            char friendnick1[BUFFER_SIZE];                 bzero(friendnick1,sizeof(friendnick1));
            char friendnick2[BUFFER_SIZE];                 bzero(friendnick2,sizeof(friendnick2));
            char nicknames[GROUP_NUMBER][BUFFER_SIZE];     bzero(nicknames,sizeof(nicknames));
            char temp[BUFFER_SIZE];                        bzero(temp,sizeof(temp));
            char chatName[GROUP_NUMBER * BUFFER_SIZE];     bzero(chatName,sizeof(chatName));
            char filepath[(GROUP_NUMBER+1) * BUFFER_SIZE]; bzero(filepath,sizeof(filepath));
            int flag = 820;

            // Odebranie danych
            if (
                recv(client_socket,selfnick,sizeof(selfnick),0)        == -1  ||
                recv(client_socket,friendnick1,sizeof(friendnick1),0)  == -1  ||
                recv(client_socket,friendnick2,sizeof(friendnick2),0)  == -1  
                ) {
                break;
            }

            // Stwórz tablicę nicków
            strcpy(nicknames[0], selfnick);
            strcpy(nicknames[1], friendnick1);
            strcpy(nicknames[2], friendnick2);

            // Posortuj tablicę nicków
            for (int i = 0; i < GROUP_NUMBER - 1; i++) {
                for (int j = i + 1; j < GROUP_NUMBER; j++) {
                    if (strcmp(nicknames[i], nicknames[j]) > 0) {
                        strcpy(temp, nicknames[i]);
                        strcpy(nicknames[i], nicknames[j]);
                        strcpy(nicknames[j], temp);
                    }
                }
            }

            // Stwórz nazwę chatu
            for (int i = 0; i < GROUP_NUMBER; i++) {
                strcat(chatName, nicknames[i]);
                if (i < GROUP_NUMBER - 1) {
                    strcat(chatName, "-");
                }
            }

            // Stwórz ścieżkę do chatu
            snprintf(filepath, sizeof(filepath), "%s%s.txt", "chats/", chatName);

            // Jeżeli taki chat już istniał to nie dopisuj go użytkownikom (jest już dopisany)
            if (access(filepath, F_OK) == 0) {
                continue;
            }

            FILE *file = fopen(filepath,"a+");
            fclose(file);

            // Zapisz chat użytkownikom
            for (int i = 0; i < GROUP_NUMBER; i++){
                bzero(nick,sizeof(nick));
                bzero(filepath,sizeof(filepath));
                strcpy(nick,nicknames[i]);

                pthread_mutex_lock(&file_mutex);
                snprintf(filepath, sizeof(filepath), "%s%s.txt", "users/", nick);
                FILE *file = fopen(filepath,"a+");

                // Zapisz nazwę chatu i identyfikator chatu
                if (file != NULL){
                    flag = 810;
                    fprintf(file, "%s,%s\n",chatName,chatName);
                }

                fclose(file);
                pthread_mutex_unlock(&file_mutex);
            }
            if (flag == 810){
                color("green"); printf("Stworzono chat grupowy.\n"); color("reset");
            }
            else if (flag == 820){
                color("red"); printf("Nie udało się stworzyć chatu grupowego.\n"); color("reset");
            }
        }

        else if (action == 0){
            color("blue"); printf("Saving messages to chat \n"); color("reset");

            // Inicjalizacja buforów
            char nick[BUFFER_SIZE];                        bzero(nick,sizeof(nick));
            char chatName[GROUP_NUMBER * BUFFER_SIZE];     bzero(chatName,sizeof(chatName));
            char filepath[(GROUP_NUMBER+1) * BUFFER_SIZE]; bzero(filepath,sizeof(filepath));
            char buffer[BUFFER_SIZE];                      bzero(buffer,sizeof(buffer));

            // Odebranie danych
            if (
                recv(client_socket,nick,sizeof(nick),0)          == -1  ||
                recv(client_socket,chatName,sizeof(chatName),0)  == -1  ||
                recv(client_socket,buffer,sizeof(buffer),0)      == -1  
                ) {
                break;
            }

            // Stwórz ścieżkę do chatu
            snprintf(filepath, sizeof(filepath), "%s%s.txt", "chats/", chatName);

            // Zapisz wiadomość do chatu
            pthread_mutex_lock(&file_mutex);
            FILE *file = fopen(filepath, "a");
            if (file != NULL){
                fprintf(file, "%s: ", nick);
                fprintf(file, "%s\n", buffer);
            }
            fclose(file);
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

int serverSocket, client_socket, *new_socket;
pthread_t client_thread;
void close_server(int sig){
    if (sig == SIGINT){
        printf("Closing server... (SIGINT)\n");
        pthread_mutex_destroy(&login_mutex);
        pthread_mutex_destroy(&file_mutex);
        close(client_socket);
        close(serverSocket);
        pthread_cancel(client_thread);
        printf("Resources freed. Ending program.\n");
        exit(0);
    }
}


int main(){
    signal(SIGINT, close_server);
    int serverSocket, client_socket, *new_socket;
    struct sockaddr_in serverAddr, clientAddr;
    socklen_t client_len = sizeof(struct sockaddr_in);

    // Inicjalizacja mutexu
    pthread_mutex_init(&login_mutex,NULL);
    pthread_mutex_init(&file_mutex,NULL);

    serverSocket = socket(AF_INET, SOCK_STREAM, 0);

    memset(&serverAddr,0,sizeof serverAddr);
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(1100);
    serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);

    bind(serverSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr));

    listen(serverSocket,50);

    color("blue"); printf("Server starting work.\n"); color("reset");
    // Nasłuchiwanie na gnieździe serwera
    while ((client_socket = accept(serverSocket, (struct sockaddr *)&clientAddr, &client_len))){
        color("green"); printf("New client connected\n"); color("reset");

        new_socket = malloc(sizeof(int));
        *new_socket = client_socket;

        // Tworzenie wątku
        pthread_create(&client_thread, NULL, handle_client, (void *)new_socket);
        pthread_detach(client_thread);
    }

    // Wyjście
    pthread_mutex_destroy(&login_mutex);
    pthread_mutex_destroy(&file_mutex);

    close(serverSocket);
    return 0;
}
