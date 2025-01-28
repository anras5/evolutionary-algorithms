# lab 7

```
./run.sh
./run-update.sh <numer_pokolenia_do_wczytania>
```

# Opracowanie

1. Celem ewolucji w eksperymencie symulacyjnym jest wykształcenie osobników, które będą poruszać się jak najdalej od miejsca narodzin oraz skakać jak najwyżej. W związku z tym w badaniu wykorzystałem podejście wielokryterialne. Pierwszym kryterium, które określiłem jako "distance", jest różnica pomiędzy lokalizacją początkową, a końcową danego osobnika. Drugim kryterium, które określiłem jako "height", jest różnica pomiędzy najwyższą pozycją w jakiej znajdował się podczas swojego życia, a pozycją najniższą. Kryteria miały taką samą wagę.

Do symulacji użyłem standardowego świata i lokalizacji - płaski teren. Osobniki będą mogły być wyposażone w zmysły, które umożliwią im poruszanie się.

Moje oczekiwania przed rozpoczęciem eksperymentu: ewolucja wykształci 3 różne "typy" osobników. Pierwszym z nich będą "skoczkowie" - osobniki, które będą wysoko skakać, ale nie będą to skoki dalekie - osobniki raczej małe (aby nie musiały podnosić wielkiego ciała), ale "silne" aby wysoko się wybić. Drugim typem będą osobniki poruszające się w stylu samochodów "lowrider car bouncing" albo w stylu żaby - kompromis pomiędzy dwoma kryteriami. Trzecim typem będą osobniki podobne do węży - poruszające się szybko (i dzięki temu daleko), ale utrzymujące nisko swój środek ciężkości. 



2. Użyta sekwencja plików: eval-allcriteria-mini.sim;deterministic.sim;sample-period-longest.sim;recording-body-coords.sim



3. Zmian dokonałem głównie w skrypcie. Do wyznaczania frontów niezdominowanych oraz crowding distance użyłem wbudowanej w deap funkcji selNSGA2. Jednak zamiast standardowego eaSimple dostępnego w deap, napisałem główną pętlę algorytmu samodzielnie. Zrobiłem to z dwóch powodów: po pierwsze, eaSimple nie gwarantuje elitaryzmu, przez co wyniki były bardzo niezadowalające, a po drugie łatwiej było mi zapisywać populację do pliku, co było potrzebne przy tworzeniu wykresów. 


Krzyżowanie: Jedno krzyżowanie rozpoczyna się poprzez rozegranie turnieju o wielkości 2 dwa razy. Z pierwszego turnieju powstaje rodzic 1, a z drugiego turnieju powstaje rodzic 2. Zbiór osobników, z którego dokonujemy losowania do turnieju nr 2 to populacja pomniejszona o rodzica 1 (Aby nie zdarzyło się, że rodzic będzie krzyżował się sam ze sobą). Podczas turnieju wygrywa ten rodzic, który ma lepszy front i lepszy crowding distance. Następnie dwóch zwycięzców (z dwóch rozegranych turniejów) krzyżujemy i powstaje jedno dziecko. Krzyżowanie ma miejsce N razy (gdzie N to liczba osobników w populacji), więc powstaje N dzieci.

Mutacja na utworzonych przez krzyżowanie dzieciach następuje z domyślnym prawdopodobieństwem. 

Wybór kolejnego pokolenia odbywa się przez selNSGA2, z populacji 2N (N rodziców i N dzieci) wybieranych jest N najlepszych osobników. Dzięki temu dobre rozwiązania wypracowane przez ewolucję nie przepadają.

Przy implementacji wzorowałem się na opisie:  https://www.geeksforgeeks.org/non-dominated-sorting-genetic-algorithm-2-nsga-ii/

Jako kryterium stopu wybrałem liczbę pokoleń - 1500. Wyboru dokonałem na podstawie wykresu [1-przebiegi]. Większość przebiegów nie zwiększa już znacząco swojej wartości fitness. Przez znacząco mam na myśli szybkość wzrostu jak dla pokoleń 1-400.



4. W ramach zadania porównałem 4 różne reprezentacje - f0, f1, f4 i fH. Liczbę osobników w populacji ustaliłem na 60.



5. Dla dwóch kryteriów można wyobrazić sobie krajobraz przystosowania jak koncepcję hollow earth albo upside down. Mamy więc dwa krajobrazy - jeden u góry, a drugi na dole. Krajobrazy różnią się w zależności od wybranej reprezentacji - patrząc na ogólnie uzyskiwane wyniki najtrudniejszy krajobraz występuje dla reprezentacji fH (w szczególności kryterium height). Początkowe trudności wykazuje reprezentacja f4, która do około 100 pokolenia osiąga najgorsze wartości, ale później (pokolenia 200-600) wzrost wartości funkcji celu jest lepszy niż dla innych reprezentacji. Może to oznaczać, że krajobraz w miejscu startu nie jest przyjazny, ale wraz ze wzrostem wartości funkcji celu, krajobraz jest łatwiejszy do optymalizacji niż dla pozostałych reprezentacji. Natomiast dla reprezentacji f0 krajobraz w miejscu startu może być przyjazny (szczególnie kryterium height), ponieważ dla wielu przebiegów udało się szybko osiągnąć bardzo dobre (okolice wartości 4.0) rezultaty, na które inne reprezentacje musiały długo (ponad 200 pokoleń) pracować, a fH nigdy nie udało się ich osiągnąć.



6. Wnioski ilościowe

W ramach zadania przygotowałem wykresy przebiegu i boxploty osobno dla dwóch kryteriów. W opisie stosuję oznaczenie: [1] - 1-przebiegi.png, [2] - 2-przebiegi-agregacja.png, [3] - 3-boxplot.png. Odchylenia standardowe na wykresie [2] pomnożone zostały przez 0.3. 

Wykres [1] dla kryterium distance pokazuje że sporo przebiegów dla różnego rodzaju reprezentacji osiąga podobne wartości w okolicach 150-300 jednostek wartości fitness. Wyróżniają się 3 przebiegi, które uzyskały wynik lepszy niż 400 - dwa dla reprezentacji f4 i jeden dla f1 (najlepsza wartość). Dla kryterium height widać od razu, że najgorzej poradziła sobie reprezentacja fH (brak przebiegu z fitness lepszym niż 3.0), a najlepiej f1 (przebieg z fitness lepszym niż aż 7.0).

Wykres [2] pokazuje jak zmienia się średnia najlepszych osobników dla danego kryterium. Dla "distance" można wyróżnić 2 fazy algorytmu - największy wzrost wartości w pokoleniach 0-400 i spowolnienie od 400 pokolenia. Na 400 pokoleniu średnio najlepsze wartości miała reprezentacja f0, ale w 1500 pokoleniu przegoniły ją aż dwie inne - f1 i f4. Widać to też na wykresie [1], że od 400 pokolenia f0 nie podnosiła się znacząco, podczas gdy f1 i f4 nadal znajdowały lepsze rozwiązania. Reprezentacja f4 mimo swojego słabego startu (w 100 pokoleniu była ostatnia), ostatecznie średnio wypada najlepiej ze wszystkich. Ma jednak również spore odchylenie standardowe - na wykresie [1] widać, że znalazła rozwiązanie z fitness lepszym niż 500, ale najsłabszy przebieg znalazł jedynie rozwiązanie na poziomie reprezentacji fH. fH pomimo dobrego startu (drugie miejsce w 200 pokoleniu), została wyprzedzona w okolicach 500 pokolenia i ostatecznie skończyła na ostatnim miejscu. Co trochę mnie zaskoczyło, to że wykres [2] dla kryterium "height" wygląda całkiem podobnie jak ten dla "distance" - f0 również daje najlepsze wyniki na początku (chociaż tutaj to jeszcze bardziej widoczne), f4 radzi sobie najgorzej na początku, a potem goni resztę i ostatecznie znajduje się na drugim miejscu. fH też radzi sobie nieźle na początku, ale w okolicach od około 200 tempo wzrostu zaczyna spadać, a od 400 już praktycznie się nie zmienia (wynosi nieco ponad 2). To podobieństwo może sugerować, że pomimo tego że kryteria dotyczą innych ruchów (jeden w poziomie, a drugi w pionie), to nadal potrzebne są podobne zestawy cech, które są łatwiejsze albo trudniejsze do wykształcenia w zależności od reprezentacji.

Wykres [3] pokazuje mniej więcej to co wykres [2] - fH jest na ostatnim miejscu na obu kryteriach, f4 ma największe IQR dla "distance". Widać również outliery dla "distance" dla reprezentacji f1 i f4. Czasy wykonywania są dość podobne dla f0, f1 i f4, ale sporo mniejsze (wykonywanie szybsze o około 50 minut) dla fH. Może to być związane z tym, że więcej rozwiązań niż dla tej reprezentacji było infeasible. 

Wykresy [1], [2] i [3] pokazują jedynie najlepsze osobniki na danym kryterium dla przebiegów, jednak nie mają wglądu w to co dzieje się "w środku" - czyli dla osobników, które nie są najlepsze na którymś z kryteriów, a znalazły kompromis pomiędzy "height" i "distance". Aby to zaprezentować przygotowałem dwa wykresy - [4] - 4-pareto-all.png i [5] - 5-pareto-all-colored.png. Na [4] zaprezentowałem wszystkie rozwiązania jakie udało się znaleźć w przeciągu działania algorytmu dla wszystkich przebiegów. Na [5] tak samo jak [4], ale z podziałem na różne przebiegi - dzięki temu widać, który przebieg odpowiada za którą część przestrzeni na wykresie [4].

Wykresy [4] wyglądają podobnie dla wszystkich reprezentacji (tylko z różną skalą) i przypominają mi proporzec, tylko z obniżonym rogiem o najmniejszym kącie. Oznacza to, że istnieją rozwiązania które skaczą wysoko, ale praktycznie w miejscu, a ewolucji nie udało się znaleźć dla żadnej reprezentacji "węża" - osobnika, który porusza się szybko, ale nie zmienia swojej wartości "z" - najwidoczniej do szybkiego biegu potrzebny jest również chociaż niewielki ruch w osi "z". Oczywiście im dalej w prawo i do góry na wykresie, tym mniej jest punktów-osobników. Wykres [5] jest według mnie nieco ciekawszy niż [4], ponieważ dostarcza tych samych informacji co [4], a jeszcze dzieli zebrane próbki na przebiegi. Dzięki temu widać, że różne przebiegi trafiły w różne miejsca w przestrzeni - przykładowo przebieg 2 i 8 dla f0 zbadały różne miejsca. Widać też przykładowo, że niektóre przebiegi były zaskakująco udane (przebieg 9 dla f1) podczas gdy inne (przebieg 10 dla f1) niekoniecznie (są zdominowane przez inne przebiegi). Poleganie więc na jednokrotnym uruchomieniu algorytmu i wyciąganie z tego wniosków mogłoby być złudne. Dla f4 ciekawym przebiegiem jest nr 2, ponieważ nie osiąga on najlepszych wartości na wykresie [1], ale znalazł sporo rozwiązań, które są na froncie pareto i są dobrym kompromisem pomiędzy kryteriami. 

Na wykresach [4] i [5] straciliśmy jednak informację o procesie ewolucji, a widzimy jedynie końcowy wynik. Wiadomo, że skoro wykorzystany został algorytm, który zachowuje najlepsze rozwiązania to proces przebiegał od lewego dolnego rogu do górnego prawego, ale nie wiadomo z jakim "tempem". Z tego powodu przygotowałem dwa filmiki: [6] https://www.youtube.com/watch?v=4UErh6UrD0c  i [7] https://www.youtube.com/watch?v=HFc5y9aAQHI, które pokazują zmiany w czasie. Podobnie jak poprzednio [6] jest dla wszystkich przebiegów, a [7] z podziałem na przebiegi (dla [7] musiałem jednak niestety ograniczyć wyświetlanie tylko do niektórych pokoleń, ponieważ generowanie tego filmiku przez matplotlib trwało bardzo długo (jedna "klatka" mniej więcej tyle co 20 klatek dla [6]). Użyte kolory na wykresie [7] są takie same jak na [5]. Dzięki tym filmikom widać, że f4 słabo radziło sobie na początku i kiedy f0 (okolice 50 pokolenia) miało już sensowne rozwiązania (distance ponad 150 i height ponad 4), to f4 dopiero dało radę wyjść z zera. Na filmiku [7] warto zwrócić uwagę na okolice pokolenia 1200 i reprezentację f4 - przebieg, o którym pisałem przy omawianiu wykresu [5] zanotował w tym czasie spory wzrost, czego nie moglibyśmy wiedzieć tylko na podstawie [5]. Widać jednak ten wzrost na [1].

Wnioski z analizy: Jeżeli zależy nam na szybkim uzyskaniu dobrych wyników to należy użyć reprezentacji f0. Natomiast jeżeli mamy do dyspozycji więcej czasu to można wykorzystać reprezentację f1 lub f4. 

7. Wnioski jakościowe

W ramach tego podpunktu zdecydowałem się zobaczyć jak wyglądają osobniki najlepsze dla reprezentacji na obu kryteriach oraz jeden przykład który reprezentuje kompromis pomiędzy kryteriami. Poniżej opiszę tylko te osobniki, które są dla mnie ciekawe albo ich wygląd mnie zaskoczył. Filmik dostępny pod linkiem: https://www.youtube.com/watch?v=-MkTojoG4N4

f0-distance: Styl poruszania się przypomina mi nieco samochody, o których pisałem w punkcie 1. (albo może trochę żabę - pokonuje odległość skokami)

Wszystkie z f1: są bardzo podobne, przypominają właśnie węża, o którym mówiłem, ale który jednak nie czołga się po ziemi (być może trudno coś takiego zrobić w wykorzystywanym symulatorze), ale trochę się unosi. Najbardziej ze wszystkich zaskoczył mnie f1-height, który składa się w harmonijkę i potem naraz prostuje wszystkie części, dzięki czemu osiąga dużą wysokość.

Spodobał mi się też f4-distance, ponieważ ten kształt nie jest skomplikowany, a osiąga bardzo dobre rezultaty w porównaniu do innych. Swoim zachowaniem przypomina on zwierzęta typu królik.