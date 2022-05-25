# Thunder Delivery
Projekt aplikacji zarządzania paczkami kurierskimi. Stworzony w ramach przedmiotu Programowanie aplikacji webowych i mobilnych.

KM1
Obrazek na stronie głównej i czcionka zostały wybrane z opensource'owych bibliotek (https://undraw.co/ i https://fonts.google.com/)

KM2
Aplikacja main_app pełni funkcję renderowania wizualnej części, zarządzania rejestrowaniem oraz logowaniem, a co za tym idzie również przyznawaniem session id oraz żetonów JWT.
Aplikacja db_app pełni funkcję aplikacji zarządzającej elementami bazy danych po zalogowaniu. Została skonfigurowana w ten sposób, aby szukała żetonu JWT w pliku cookie. 
W związku z problemami z metoda fetch, używaną przeze mnie w javascript'cie, musiałem zaimplementować prosty CORS dla tej aplikacji.

Aby uruchomić aplikację należy jako administrator użyć skryptu shellowego.
Do użycia skryptu wymagane jest posiadanie programów:
1. Docker
2. Docker-compose
3. Openssl
Kiedy chcemy zbudować obrazy dockerowe używamy polecenia "sudo sh start.sh --build", będąc w korzeniu repozytorium.
Kiedy nie chcemy przebudowywać obrazów używamy polecenia "sudo sh start.sh", będąc w korzeniu repozytorium.

KM3
Aplikacja główna - https://localhost:8080
Aplikacja bazy danych  - https://localhost:8081
Aplikacja kuriera - https://localhost:8082
Aplikacja paczkomatu - https://localhost:8083

W każdej aplikacji:
"/" -> swagger
"/home/" -> strona domowa

Po użyciu skryptu włączającego aplikacje i wykonaniu dowolnego zapytania do dowolnej aplikacji do bazy zostaje zapisane:
    - 2 kurierzy
    - 2 paczkomaty
Kurierzy mają dane:
    - pierwszy:
        - username: kurier
        - password: zaq1@WSX
    - drugi:
        - username: drugiKurier
        - password: zaq1@WSX

Paczkomaty mają identyfikatory:
- locker_1
- locker_2

Przy włączniu aplikacji paczkomatu musimy podać identyfikator paczkomatu. Jeżeli dobrze go podamy to zostanie zapisane cookie z identyfikatorem.
W tym momencie jesteśmy "zalogowani" do paczkomatu (korzystamy z aplikacji jakby była w urządzeniu, stąd przy pobieraniu paczek nie podajemy id paczkomatu).
Aby zmienić paczkomat należy wyczyścić cookie "locker_id" i powtórzyć "logowanie"

Do aplikacji kuriera należy użyć przeglądarki z wyłączoną funkcjonalności walidacji certyfikatu (https://bitbucket.org/zespoll/notes_from_classes_pamiw_2020z/src/master/Lab_10_example/Readme.md).

KM4
Aplikacja zarządzająca websocketami - https://localhost:8084
Należy ją uruchomić i zaakceptować certyfikat (endpoint "/"). W innym przypadku wszystkie aplikacje nie będą działały poprawnie
