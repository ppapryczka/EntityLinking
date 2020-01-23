# Entity Linking
Opis zadania (.ang) - [Entity Linking](http://2019.poleval.pl/index.php/tasks/task3?fbclid=IwAR32WO2Yg3Dmt-CpWbYADOPjjFOiR8yJormzwOfdfHccwP0mJ4u2aAbcYG4)

### Środowisko

Do stworzenia środowiska potrzebne są:
- `python3.6`
- `python3-venv` (`sudo apt install python3-venv`)
- `morfeusz2`: (tylko dla Ubuntu)
  - `wget -O - http://download.sgjp.pl/apt/sgjp.gpg.key|sudo apt-key add -`
  - `sudo apt-add-repository http://download.sgjp.pl/apt/ubuntu`
  - `sudo apt update`
  - `sudo apt install morfeusz2`

##### Tworzenie środowiska
1. `python3 -m venv venv` (tworzy środowisko `venv`)
2. `source venv/bin/activate` (aktywacja środowiska)
3. `pip3 install --upgrade pip` (upgrade pip'a)
4. instalacja `morfeusz2`:
   - Ubuntu
     - `wget http://download.sgjp.pl/morfeusz/20191229/Linux/18.04/64/morfeusz2-0.4.0-py3.6-Linux-amd64.egg`
     - `easy_install morfeusz2-0.4.0-py3.6-Linux-amd64.egg`
     - `rm morfeusz2-0.4.0-py3.6-Linux-amd64.egg`
   - macOS
     - `wget http://download.sgjp.pl/morfeusz/20191229/Darwin/64/morfeusz2-0.4.0-py3.6-macosx-10.9-x86_64.egg`
     - `easy install morfeusz2-0.4.0-py3.6-macosx-10.9-x86_64.egg`
     - `rm morfeusz2-0.4.0-py3.6-macosx-10.9-x86_64.egg`
5. `pip3 install -r requirements.txt` (instalacja dodatkowych bibliotek)

#### Testowanie
- wykonaj komendę `pytest` w katalogu projektu

#### Uruchomienie aplikacji
- `python3 app.py test -h`(wyświetlenie komunikatu z pomocą)
- `python3 app.py test -i test_tags.csv -N 10 -db entity_linking/entity_linking.db`(uruchomienie aplikacji ze zbiorem testowym i utworzoną bazą danych)
- `python3 entity_linking/create_db <database name>`(utworzenie bazy danych) 
