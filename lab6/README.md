# lab 6

Porównanie algorytmu ewolucyjnego i programowania genetycznego.

```shell
./run-gp.sh
./run-ea.sh
```

# Opracowanie

W ramach laboratorium zdecydowałem się na optymalizację vertpos przy użyciu reprezentacji f1. Odchylenie standardowe na wykresie 2 pomnożone jest razy 0.5.

Ogólny pomysł dla GP był taki sam dla wszystkich moich podejść.

Jako Primitives wykorzystałem 4 różne funkcje:

- gp_stick, dodającą "X" na początku genotypu

- gp_parenthesis, obejmującą cały dotychczasowy genotyp w nawiasy

- gp_comma, dodającą pomiędzy dwoma genotypami przecinek i łączącą te genotypy, a następnie zamykającą wynikowy genotyp w nawiasie

- gp_modifier, dodającą na początku genotypu modyfikator z dostępnych [R, r, Q, q, C, c, L, l, W, w, F, f]

Jako terminali użyłem "X", "" (pusty string), "(X)". Aby zabezpieczyć się przed niepoprawnymi genotypami użyłem PrimitiveSetTyped. Zdefiniowałem dwie klasy - Bare (reprezentująca genotyp który nie znajduje się w nawiasie) oraz Branch (reprezentująca genotyp który znajduje się w nawiasie). W taki sposób przykładowo funkcja gp_parenthesis mogła przyjąć Bare lub Branch, ale zwracała zawsze Branch. Ustawienia w algorytmie takie jak "expr", "mate" czy "mutate" zastosowałem takie jak w przykładzie z dokumentacji https://deap.readthedocs.io/en/master/examples/gp_symbreg.html. Minimum height of trees ustawiłem na 2, a maximum na 10. W trakcie wykonywania programu zdarzyło się również parę razy, że nastąpił błąd zbyt wielu nawiasów w Pythonie (https://stackoverflow.com/a/78807078/16191733), więc dla rozwiązań które miały taki problem przypisywałem FITNESS_VALUE_INFEASIBLE_SOLUTION. 

Później przetestowałem również wersję algorytmu dla terminali None (Bare) i None (Branch). Funkcje primitives zostały odpowiednio dostosowane.

Pierwsze podejście na wykresach zaczyna się od "gp", a podejście z terminalami None "gb". Liczba oznacza oznacza liczbę osobników w populacji. Algorytm ewolucyjny oznaczyłem jako "ea".

Początkowo uruchomiłem gp200 oraz ea (również z liczbą osobników 200 w populacji). Na wszystkich wykresach widać, że gp200 poradziło sobie gorzej niż ea (najlepszy średni fitness 1.2 vs 1.7). Postanowiłem wówczas sprawdzić czy wyniki dla gp poprawią się jeżeli zwiększę liczbę populacji ponad dwukrotnie, do 500 osobników. Niestety nie stało się tak, co widać na wykresie nr 2. Mimo tego, że podczas przebiegu algorytmu wersja gp500 osiąga średnio nieco lepsze wyniki niż gp200 (chociaż w 150 pokoleniu średnie są do siebie bardzo zbliżone i blisko im wartości 1.2-1.25), to nadal daleko mu do ea. Zdecydowałem się wtedy zmienić nieco algorytm i zastosować inne terminale. Stwierdziłem, że być może wyznaczone początkowo terminale są w jakiś sposób ograniczające, więc może warto aby algorytm zaczął od zera, czyli od None. Jak widać na wykresie 2, gb200 podobnie jak poprzednie "ulepszenie" odnotowuje nieco lepsze wyniki od swoich poprzedników, ale znów w 150 pokoleniu osiąga podobną wartość fitness jak pozostałe wersje gp. Wszystkie średnie dla programowania genetycznego zatrzymują się w okolicach 1.25 w 150 pokoleniu.

Warto też zwrócić uwagę na wykres 3, na którym po prawej stronie umieszczone są czasy wykonywania. Bez wątpienia ea wykonywało się najszybciej, później gp200 i gb200 (taka sama populacja i podobny algorytm). Zwiększenie populacji dla gp z 200 do 500 znacznie wydłużyło czas wykonywania programu, a trafił się też outlier, dla którego na wynik trzeba było poczekać ponad 2 godziny.

Co ciekawe, dla gp500 osobniki z hall of fame mają o wiele mniejszy IQR niż dla gp200.