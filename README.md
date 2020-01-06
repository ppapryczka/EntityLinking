# Entity Linking
Opis zadania (.ang) - [Entity Linking](http://2019.poleval.pl/index.php/tasks/task3?fbclid=IwAR32WO2Yg3Dmt-CpWbYADOPjjFOiR8yJormzwOfdfHccwP0mJ4u2aAbcYG4)

### Środowisko

Do stworzenia środowiska potrzebne są: 
- `pyenv`(https://github.com/pyenv/pyenv-installer) 
- `poetry`(https://poetry.eustace.io/docs/#introduction).

##### Tworzenie środowiska
1. Zainstaluj `pyenv` i `poetry`.
2. Wywołaj `poetry config settings.virtualenvs.in-project true` - zmusi to  `poetry` do stworzenia `venv'a` w repo.
3. Zainstaluj Python'a 3.7 lokalnie w katalogu projektu:
` shell`
`pyenv install 3.7`
`pyenv local 3.7`
4. Uruchom polecenie `poetry install`.

#### Praca ze środowiskiem
Po poprawnym wykonaniu `poetry install` uruchom `poetry shell`. Poetry utworzy środowisko wirtualne, które można aktywować w konsoli wywołując `source .venc/bin/activate`. Można też wybrać z wcześniej wymienionego miejsca interpreter np. dla PyCharm co pozwoli wykonywać skrypty z poziomu tego IDE.

### Biblioteki
#### Aktualizacja
Biblioteki można zaktualizować lub dodać te, które dodali inni poprzez `poetry install`.

#### Dodawanie
Aby dodać nową bibliotekę będąc w wirtualnym wydajemy wywołujemy polecenie `poetry add [--dev] <nazwa biblioteki>`. Flaga `--dev` jest użyta tylko, jeśli dana biblioteka służy jedynie tworzeniu aplikacji, a nie jest użyta w samej aplikacji. 
