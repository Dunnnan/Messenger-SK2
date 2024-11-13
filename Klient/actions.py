def action(action):
    # 1 Tworzenie konta
    if action == 'signup':
        return(100)

    # 2 Logowanie
    if action == 'login':
        return(200)
    
    # 3 Stronga Główna
    if action == 'main':
        return(300)
    
    # 4 Wyświetlanie znajomych
    if action == 'friends':
        return(400)
    
    # 5 Wyszukiwanie znajomych
    if action == 'search':
        return(500)

    # 6 Dodawanie znajomych
    if action == 'invite':
        return(600)
    
    # 7 Grupowa konwersacja
    if action == 'group':
        return(700)

def result(flag):
    # 1 Tworzenie konta
    if flag == 110:
        flag = 100
        print('Użytkownik o podanym nicku już istnieje !')
    
    if flag == 120:
        print('Konto klienta zostało utworzone !')

    #2 Logowanie
    if flag == 210:
        flag = 200
        print('Konto o podanym nicku nie istnieje !')

    if flag == 220:
        flag = 200
        print('Wprowadzono niepoprawne hasło')

    if flag == 230:
        print('Pomyślnie zalogowano')
