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

Klient:
1)	Klasa signup - odpowiada za stworzenie interfejsu graficznego formularza rejestracji użytkownika oraz obsługę całego procesu rejestracji, w tym walidację danych, przesyłanie ich na serwer oraz odbiór odpowiedzi zwrotnej. W przypadku udanej rejestracji automatycznie przełącza użytkownika na ekran logowania.
2)	Klasa signin - obsługuje proces logowania użytkownika umożliwiając wprowadzenie nazwy użytkownika i hasła, ich weryfikację oraz przesłanie do serwera. W przypadku poprawnych danych użytkownik zostaje zalogowany i przekierowany do głównego menu aplikacji, a w razie błędu wyświetlany jest odpowiedni komunikat.
3)	Klasa main_menu - obsługuje główne okno aplikacji czatu, umożliwiając użytkownikowi wybór chatu, wysyłanie wiadomości, wyświetlanie historii rozmów oraz przełączanie się do listy znajomych. Dzięki cyklicznemu odświeżaniu danych i komunikacji z serwerem w tle zapewnia aktualizowanie czatów i historii wiadomości.
4)	Klasa znajomi - reprezentuje główne okno aplikacji do zarządzania znajomymi, umożliwiając użytkownikowi przeglądanie znajomych, zaproszeń oraz zarządzanie grupami. Obsługuje interakcje, takie jak akceptowanie i odrzucanie zaproszeń, dodawanie znajomych oraz tworzenie grup.
5)	Klasa worker - umożliwia wykonywanie żądań w osobnym wątku, zapewniając współbieżność w aplikacji PyQt6. Obsługuje sygnały do przekazywania wyników, błędów, aktualizacji czatu i zakończenia pracy, co pozwala na płynne przetwarzanie operacji bez blokowania interfejsu użytkownika.
6)	Klasa Message umożliwia serializację flagi do postaci bajtów, co jest przydatne przy przesyłaniu danych w protokołach komunikacyjnych.




## Struktura plików
##

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
##

``` Tworzenie konta : 100 ```

***Wejście serwera*** <br>
```name``` - imię użytkownika tworzącego konto.<br>
```surname``` - nazwisko użytkownika tworzącego konto.<br>
```nick``` - nick użytkownika tworzącego konto ***(unikalny w systemie)***.<br>
```password``` - hasło użytkownika tworzącego konto.<br>

***Działanie serwera***<br>
Sprawdza unikalność przesłanego nicku w systemie i tworzy konto użytkownika, wpisując wejście jako pojedynczą linię w pliku ***users.txt***.

***Wyjście serwera***<br>
Flaga mówiąca o powodzeniu stworzenia konta:
```
flag = 110 // Konto o tym nicku już istnieje
flag = 120 // Konto zostało utworzone.
```

##
``` Logowanie : 200 ```

***Wejście serwera***<br>
```nick``` - nick użytkownika logującego się ***(unikalny w systemie)***.<br>
```password``` - hasło użytkownika logującego sie.<br>

***Działanie serwera***<br>
Sprawdza poprawność przesłanych danych i umożliwia uczestnikowi korzystanie z aplikacji.

***Wyjście serwera***<br>
Flaga mówiąca o powodzeniu logowania:
```
flag = 210 // Konto o tym nicku nie istnieje.
flag = 220 // Niepoprawne hasło.
flag = 230 // Zalogowano.
```

##
``` Strona główna : 300 ```

***Wejście serwera***<br>
```nick``` - nick użytkownika.

***Działanie serwera***<br>
Otwiera plik użytkownika, w którym znajduje się chaty, których jest uczestnikiem i przesyła mu jego nazwy (zarówno tą do wyświetlenia jak i nazwę pliku tego chatu na serwerze).

***Wyjście serwera***<br>
Pary nazw chatów użytkownika - nieparzyste to nazwy do wyświetlenia, a parzyste to nazwy plików na serwerze (dalej będziemy posługiwać się terminem identyfikator chatu).

##
``` Wyświetlenie chatu : 400 ```

***Wejście serwera***<br>
```chatName``` - identyfikator chatu, który użytkownik chce wyświetlić.

***Działanie serwera***<br>
Otwiera plik o przesłanym identyfikatorze i odsyła użytkownikowi jego zawartość linia po linii.

***Wyjście serwera***<br>
Zawartość chatu, którego identyfikator przesłał użytkownik.


##
``` Znajomi : 500 ```

***Wejście serwera***<br>
```nick``` - nick użytkownika.

***Działanie serwera***<br>
Otwiera plik użytkownika, w którym znajdują się nicki jego znajomych oraz zaproszenia do znajomych. Odsyła użytkownikowi jego zawartość linia po linii

***Wyjście serwera***<br>
Pary nick i identyfikator (f/n) informujący o tym czy dany nick to znajomy, czy użytkownik wysyłający zaproszenie do znajomych.


##
``` Wyszukiwanie użytkowników : 600 ```


***Wejście serwera***<br>
```selfnick``` - nick użytkownika.<br>
```nick``` - nick, którego użytkownik szuka w wyszukiwarce.<br>

***Działanie serwera***<br>
Przeszukuje przestrzeń użytkowników, licząc stopień podobieństwa do szukanego nicku oraz określając czy dany użytkownik jest znajomym wyszukiwającego.

***Wyjście serwera***<br>
Trójki nick, identyfikator (f/n), stopień pokrewieństwa (im wyższy tym większe pokrewieństwo).


##
``` Zaproszenie użytkowników : 700 ```


***Wejście serwera***<br>
```selfnick``` - nick użytkownika wysyłającego zaproszenie.<br>
```friendnick``` - nick użytkownika, do którego skierowane jest zaproszenie.<br>

***Działanie serwera***<br>
Zapisuje w plikach ```/friends``` użytkowników linie ```nick,n``` oznaczającą nierozpatrzone jeszcze zaproszenie do znajomych.

***Wyjście serwera***<br>
Brak.
##
``` Akceptacja zaproszenia : 710 ```


***Wejście serwera***<br>
```selfnick``` - nick użytkownika akceptującego zaproszenie.<br>
```friendnick``` - nick użytkownika, którego zaproszenie jest akceptowane.<br>

***Działanie serwera***<br>
Zamienia status nierozpatrzonego zaproszeia na znajomość (zmiana ***n*** na ***f*** w plikach ```/friends```), tworzy nowy chat w ```/chats``` oraz dopisuje użytkownikom ten chat do ich własnych list chatów.

***Wyjście serwera***<br>
Brak.

##
``` Odrzucenie zaproszenia : 720 ```


***Wejście serwera***<br>
```selfnick``` - nick użytkownika odrzucającego zaproszenie.<br>
```friendnick``` - nick użytkownika, którego zaproszenie jest odrzucane.<br>

***Działanie serwera***<br>
Usuwa zaproszenie do znajomych z plików ```/friends``` obu użytkowników.

***Wyjście serwera***<br>
Brak.

##
``` Stworzenie grupowego chatu : 800 ```


***Wejście serwera***<br>
```selfnick``` - nick użytkownika tworzącego grupowy chat.<br>
```friendnick1``` - nick użytkownika, który będzie członkiem grupowego chatu.<br>
```friendnick2``` - nick użytkownika, który będzie członkiem grupowego chatu.<br>


***Działanie serwera***<br>
Tworzy nowy chat w ```/chats``` oraz dopisuje użytkownikom ten chat do ich własnych list chatów.

***Wyjście serwera***<br>
Brak.

##

``` Wysłanie wiadomości : 0 ```


***Wejście serwera***<br>
```nick``` - nick użytkownika wysyłającego wiadomość.<br>
```chatName``` - identyfikator chatu, na który jest wysyłana wiadomość.<br>
```message``` - treść wysyłanej wiadomości.<br>

***Działanie serwera***<br>
Zapisuje wiadomość w chacie wskazanym przez użytkownika.

***Wyjście serwera***<br>
Brak.

##
``` Wyjście : -1 ```
Kończy obsługę żądań.

##
## Szkielet klienta
##

## Ważne ogólne rzeczy, które trzeba uwzględnić
***Odświeżanie cykliczne - Niektóre bloki powinny być wywoływane cyklicznie i samoistnie - 300, 400, 500, aby zapewnić aktualność danych po stronie użytkownika. (Te bloki też powinny być wykonane od razu po zalogowaniu)*** <br><br>
***Odświeżanie po zmianach - Dodatkowo po każdej operacji zmiany danych - 700, 710, 720, 800, 0, również powinno mieć miejsce odświeżenie, chyba że cykl odświeżenia jest na tyle krótki, iż brak tego aspektu będzie niezauważalny dla użytkownika*** <br><br>
***Menu rozwijane - Wybór chatu z menu rozwijanego powinien umożliwić przypisanie id tego chatu do jakiejś zmiennej currentChat albo currentChatIndex dla łatwości wysyłania tego id do serwera (tak samo nick użytkownika)*** <br><br>
***Wyszukiwarka - Przyjąłem, że wyszukujemy użytkowników, którzy jeszcze nie są naszymi znajomymi, albo nie wysłali nam zaproszenia (lub vice versa), stąd 3 listy zwracane przez serwer*** <br><br>
***Przypisywanie zmiennych - zmienne, które są aktualnie podawane z klawiatury w celu przesłania serwerowi (jak np. w 700, 710, 720 nicki użytkowników, których dotyczą zaproszenia) powinny być przypisywane w momencie klikięcia konkretnego guzika w aplikacji (feeedback pls czy możliwe)***


##
``` Strona główna : 300 ```

***Odbiera od serwera***<br>
```nazwyChaty``` - nazwy chatów użytkownika - do wyświetlenia w rozwijanym menu.<br>
```idChaty``` - id chatów użytkownika - do przesłania serwerowi kiedy będziemy chcieli otworzyć konkretny chat (zażądać przesłania zawartości).<br>

***Funkcjonalność***<br>
Zapisuje chaty użytkownika po stronie klienta - ten blok powinien być wykonywany co jakiś czas (odświeżanie), aby zapewnić aktualność danych użytkownika.


##
``` Wyświetlenie chatu : 400 ```

***Odbiera od serwera***<br>
```mess``` - pojedyncza linia chatu.<br>

***Funkcjonalność***<br>
Klient odbiera pojedyncze linie od serwera reprezentujące pojedynczą wiadomość danego użytkownika na chacie.


##
``` Znajomi : 500 ```

***Odbiera od serwera***<br>
```nazwyZnajomi``` - nicki znajomych użytkownika.<br>
```statusZnajomi``` - f - znajomy | n - zaproszenie do znajomych.<br>

***Funkcjonalność***<br>
Zapisuje znajomych użytkownika po stronie klienta - ten blok powinien być wykonywany co jakiś czas (odświeżanie), aby zapewnić aktualność danych użytkownika. 



##
``` Wyszukiwanie użytkowników : 600 ```


***Odbiera od serwera***<br>
```nickiUzytkownicy``` - nicki użytkowników w systemie.<br>
```strcmpUzytkownicy``` - stopień podobieństwa do wyszukiwanej frazy (im wyższy tym lepszy)<br>
```znajomiUzytkownicy``` - f - znajomy lub zaproszenie do znajomych | n - nie widnieje.<br><br>

***Funkcjonalność***<br>
Odbiera i zapisuje w listach wyniki wyszukiwania po stronie serwera. Dodatkowo sortuje listy malejąco po stopniu podobieństwa do szukanej frazy. Ostatnia lista ```znajomiUzytkownicy``` służy do pomijania użytkowników już wpisanych w pliku ```/friends``` osoby zgłaszającej wyszukiwanie. 


##
``` Zaproszenie użytkowników : 700 ```


***Odbiera od serwera***<br>
Brak.

***Funkcjonalność***<br>
Planowo funkcjonalność pod guzikiem Zaproś, czyli przesłanie własnego nicku i nicku osoby zapraszanej.

##
``` Akceptacja zaproszenia : 710 ```


***Odbiera od serwera***<br>
Brak.

***Funkcjonalność***<br>
Planowo funkcjonalność pod guzikiem Zaakceptuj, czyli przesłanie własnego nicku i nicku osoby, od której zaproszenie do znajomych akceptujemy.


##
``` Odrzucenie zaproszenia : 720 ```


***Odbiera od serwera***<br>
Brak.

***Funkcjonalność***<br>
Planowo funkcjonalność pod guzikiem Odrzuć, czyli przesłanie własnego nicku i nicku osoby, od której zaproszenie do znajomych odrzucamy.


##
``` Stworzenie grupowego chatu : 800 ```


***Odbiera od serwera***<br>
Brak.

***Funkcjonalność***<br>
Planowo funkcjonalność pod guzikiem Group, finalizującego stworzenie grupy, czyli przesłanie ***! własnego nicku i nicków dwóch osób z którymi tworzymy chat grupowy. !***
Ewentualnie można później rozszerzyć o możliwość nazwania grupy.

##

``` Wysłanie wiadomości : 0 ```


***Odbiera od serwera***<br>
Brak.

***Funkcjonalność***<br>
Planowo funkcjonalność pod guzikiem Wyślij, finalizującego wysłanie wiadomości na dany chat, czyli przesłanie własnego nicku, id chatu, na który wysyłamy wiadomość ***(np. zapisane w currentChat ze wstępu)*** oraz treści wiadomości.

##
``` Wyjście : -1 ```
Kończy obsługę żądań.


