# 1 Tworzenie konta
flag = 100 # Klient tworzy konto # Serwer czeka na przesłanie danych
flag = 110 # Użytkownik o podanym nicku już istnieje !
flag = 120 # Konto klienta zostało utworzone !

# 2 Logowanie
flag = 200 # Klient loguje się # Serwer czeka na przesłanie danych
flag = 210 # Konto o podanym nicku nie istnieje !
flag = 220 # Wprowadzono niepoprawne hasło !
flag = 230 # Pomyślnie zalogowano ! Serwer przekazuje listę chatów klienta

# 3 Strona Główna
flag = 300 # Klient otwiera konkretny chat # Serwer zestawia połączenie pomiędzy użytkownikami chatu, przesyła historię chatu
             #                      | znajomego

# 4 Wyświetlanie znajomych
flag = 400 # Klient klika kafelek "Znajomi" # Serwer przesyła listę znajomych użytkownika, listę zaproszeń do znajomych

# 5 Wyszukiwanie użytkowników 
flag = 500 # Klient klika pasek wyszukiwania # Serwer oczekuje przesłania nazwy szukanego użytkownika
flag = 510 # Klient przesyła nazwę # Serwer odsyła spokrewnione wyniki

# 6 Dodawanie znajomych
flag = 600 # Klient po otrzymaniu wyników wyszukiwania ma możliwość wysłania użytkownikom zaproszenia do znajomych
           # Serwer zapisuje odpowiednim użytkownikom zaproszenia

# 7 Grupowa konwersacja
flag = 700 # Klient w zakładce znajomi wybiera opcję stwórz chat grupowy # Serwer przesyła jego listę znajomych
flag = 710 # Klient przesyła listę wybranych znajomych do chatu grupowego # Serwer zestawia połączenie
             # ! Serwer zestawia połączenie niezależnie czy chat jest nowy czy jest już stworzony !
