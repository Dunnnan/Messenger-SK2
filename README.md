# Messenger-SK2

## TODO
0. System flag. (Klient wysyła flagę, aby serwer wiedział jakie operacje wykonać)
1. Tworzenie Konta. (Nick|Login Hasło Imię Nazwisko adresObrazka)
2. Logowanie.
3. Strona główna
4. Chat.
5. Wyświetlanie znajomych.
6. Wyszukiwywanie znajomych.
7. Dodawanie znajomych.
8. Grupowa konwersacja.

### Czy możemy napisać klienta w pythonie.
### Jak ma wyglądać konwersacja z wieloma użytkownikami naraz.

### Odpowiedź Prowadzącego
1. Można napisaćw pythonie
2. tutaj zostawiam inwencję państwu, ale podam przykład: Mają Panstwo zaimplemntowany system znajomych,
 wybieramy 2 z tych znajomych i tworzymy konwersacje grupową w której serwer, po odebraniu wiadomości przesyła ją do innych uszestników, sami uszestnicy nasłuchują na wiadomosci od serwera 


# Protokół

## Struktura plików
```
├── chats
│   ├── Gwiazdka-Rudolf.txt
│   ├── Błyskawica-Gwiazdka.txt
│   └── Błyskawica-Gwiazdka-Rudolf.txt
├── friends
│   ├── Błyskawica.txt
│   ├── Gwiazdka.txt
│   └── Rudolf.txt
├── users
│   ├── Błyskawica.txt
│   ├── Gwiazdka.txt
│   └── Rudolf.txt
├── klient.py
├── serwer.c
└── users.txt
```

```chats``` to folder z plikami będącymi zapisami chatów. Ich nazwa to konkatenacja nicków użytkowników, których dotyczy ten chat, posortowanych rosnąco wg. ASCII.
***Format:***
```
Użytkownik1: wiadomość
Użytkownik2: wiadomość
...
```

```friends``` to folder z plikami przechowującymi nicki znajomych danego użytkownika i zaproszenia do grona znajomych. Ich nazwa to nick użytkownika. Litera ***f*** w drugiej kolumnie danej linii oznacza, iż użytkownik o tym nicku jest znajomym uzytkownika, którego dotyczy plik, a litera ***n*** w tej kolumnie oznacza, iż zapisany użytkownik wysłał zaproszenie do grona znajomych.
***Format:***
```
nickUżytkownika1,f
nickUżytkownika2,n
...
```

```users``` to folder z plikami przechowującymi nazwy chatów danego użytkownika. Ich nazwa to nick użytkownika. Pierwsza kolumna to wyświetlana w menu wyboru nazwa chatu, a druga kolumna to nazwa pliku chatu w folderze ```/chats```.
***Format:***
```
nickUżytkownika1,nickUżytkownika0-nickUżytkownika1
nickUżytkownika2,nickUżytkownika0-nickUżytkownika2
...
```

## Żądania

``` Tworzenie konta : 100 ```

***Wejście serwera***
```name``` - imię użytkownika tworzącego konto.
```surname``` - nazwisko użytkownika tworzącego konto.
```nick``` - nick użytkownika tworzącego konto ***(unikalny w systemie)***.
```password``` - hasło użytkownika tworzącego konto.

***Działanie serwera***
Sprawdza unikalność przesłanego nicku w systemie i tworzy konto użytkownika, wpisując wejście jako pojedynczą linię w pliku ***users.txt***.

***Wyjście serwera***
Flaga mówiąca o powodzeniu stworzenia konta:
```
flag = 110 // Konto o tym nicku już istnieje
flag = 120 // Konto zostało utworzone.
```


``` Logowanie : 200 ```

***Wejście serwera***
```nick``` - nick użytkownika logującego się ***(unikalny w systemie)***.
```password``` - hasło użytkownika logującego sie.

***Działanie serwera***
Sprawdza poprawność przesłanych danych i umożliwia uczestnikowi korzystanie z aplikacji.

***Wyjście serwera***
Flaga mówiąca o powodzeniu logowania:
```
flag = 210 // Konto o tym nicku nie istnieje.
flag = 220 // Niepoprawne hasło.
flag = 230 // Zalogowano.
```


``` Strona główna : 300 ```

***Wejście serwera***
```nick``` - nick użytkownika.

***Działanie serwera***
Serwer otwiera plik użytkownika, w którym znajduje się chaty, których jest uczestnikiem i przesyła mu jego nazwy (zarówno tą do wyświetlenia jak i nazwę pliku tego chatu na serwerze).

***Wyjście serwera***
Pary nazw chatów użytkownika - nieparzyste to nazwy do wyświetlenia, a parzyste to nazwy plików na serwerze (dalej będziemy posługiwać się terminem identyfikator chatu).


``` Wyświetlenie chatu : 400 ```

***Wejście serwera***
```chatName``` - identyfikator chatu, który użytkownik chce wyświetlić.

***Działanie serwera***
Serwer otwiera plik o przesłanym identyfikatorze i odsyła użytkownikowi jego zawartość linia po linii.

***Wyjście serwera***
Zawartość chatu, którego identyfikator przesłał użytkownik.



``` Znajomi : 500 ```

***Wejście serwera***
```nick``` - nick użytkownika.

***Działanie serwera***
Serwer otwiera plik użytkownika, w którym znajdują się nicki jego znajomych oraz zaproszenia do znajomych. 

***Wyjście serwera***
Pary nick i identyfikator f/n informujący o tym czy dany nick to znajomy, czy użytkownik wysyłający zaproszenie do znajomych.



``` Wyszukiwanie użytkowników : 600 ```



***Wejście serwera***

***Działanie serwera***

***Wyjście serwera***

``` Zaproszenie użytkowników : 700 ```



***Wejście serwera***

***Działanie serwera***

***Wyjście serwera***

``` Akceptacja zaproszenia : 710 ```



***Wejście serwera***

***Działanie serwera***

***Wyjście serwera***

``` Odrzucenie zaproszenia : 720 ```



***Wejście serwera***

***Działanie serwera***

***Wyjście serwera***



``` Stworzenie grupowego chatu : 800 ```



***Wejście serwera***

***Działanie serwera***

***Wyjście serwera***

``` Wysłanie wiadomości : 0 ```



***Wejście serwera***

***Działanie serwera***

***Wyjście serwera***



``` Wyjście : -1 ```





