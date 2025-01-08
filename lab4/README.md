Run:

```
./run.sh
./run-mutations.sh
./run-cross.sh
./run-walk.sh
```

## Zadanie 1

W ramach laboratorium zdecydowałem się na optymalizację "vertpos". Użyłem pomocniczej funkcji celu do opuszczenia plateau podczas ewolucji. Wielkość populacji ustaliłem na 50, a liczbę pokoleń na 130. 

Wyniki są analogiczne do tych otrzymanych w  laboratorium nr 2. Najlepsze wyniki osiąga genotyp f4, później podobne wartości f1 i f0, a na końcu genotyp f9. Najlepiej widać to na wykresie 1-przebiegi-agregacja oraz 1-boxplot (wykres lewy z jakością osobników). Na wykresach (w szczególności 1-przebiegi-agregacja) widać, że dla genotypu:

- f0 udało zebrać się osobniki z fitness w przedziale 0-1.85

- f1 udało zebrać się osobniki z fitness w przedziale 0-1.68

- f4 udało zebrać się osobniki z fitness w przedziale 0-2.09

- f9 udało zebrać się osobniki z fitness w przedziale 0-1.14

Podczas działania algorytmu zapisywałem osobniki z każdego pokolenia, aby zgromadzić ich jak najwięcej. Następnie dla każdego genotypu wyszczególniłem 500 genotypów z zebranych, w taki sposób aby były one równo rozłożone i nie było dużych przerw pomiędzy fitnessami.

Na wykresie 1-mutacje przedstawiłem badanie wpływu mutacji na osobniki dla poszczególnych genotypów. Ogólny trend na wszystkich czterech wykresach jest taki sam - mutacje w większości przypadków pogarszają fitness osobnika, ponieważ większość punktów znajduje się pod prostą y=x. Co można również zauważyć to, że im lepsze wartości fitness osobników, tym rzadziej mutacje pomagają, a mogą dużo popsuć. Dla każdego genotypu obliczyłem ile procent osobników po mutacji ma lepszy fitness niż osobnik oryginalny. Dodatkowo, obliczyłem też taką samą wartość ale z podziałem - dolna i górna połowa zakresu oryginalnego fitness. Określa to więc ile procent mutacji poprawiło wynik osobnika oryginalnego dla fitness mniejszego/większego niż max(fitness)/2 dla danego genotypu. Pozwoli to na liczbową reprezentację tego, że lepsze wartości fitness osobników oryginalnych powodują że mniej mutacji skutkuje polepszeniem wartości.

- f0 - poprawa w 11.15% przypadków, 15.05% dla dolnej połowy i 7.25% dla górnej połowy. Na wykresie f0 widoczne jest, że mając dobrą (powyżej 1.25) wartość fitness możemy bardzo łatwo "spaść" i pogorszyć wynik ponad dwukrotnie (poniżej 0.5). Widać również, że ulepszenia występują przede wszystkim dla osobników z niskim fitness oraz nie są duże.

- f1 - poprawa w 14.93% przypadków, 22.05% dla dolnej połowy i 7.81% dla górnej połowy. Wykres f1 ukazuje, że popraw jest więcej niż w przypadku f0, ale również o wiele łatwiej "spaść". Pogorszenia wyników nie są jednak tak znaczące dla największych wartości fitness. Ciekawe jest zgrupowanie wielu osobników w przedziale x (0.25, 0.5) i y (1.5, 1.75), co może sugerować, że w krajobrazie istnieje tam kotlina/dolina ograniczona wysokimi wartościami fitness.

- f4 - poprawa w 16.13% przypadków, 21.45% dla dolnej połowy i 10.74% dla górnej połowy. Dla f4 udało się uzyskać najwyższe wartości fitness (większe od 2) i może to być rezultat między innymi tego, że dla dolnej połowy oryginalnego fitness widzimy, że sporo mutacji ulepsza rodzica o sporą wartość (np zdarzają się mutacje, które pozwalają na przeskoczenie z wartości mniejszej niż 0.5 od razu do 2.0). Natomiast podobnie jak dla f0, ale nie tak wyraźnie, widać że utworzyła się "linia", do której wpada dużo osobników. Widoczna jest ona tuż poniżej fitnessu równego 0.5. 

- f9 - poprawa w 22.55% przypadków, 37.57% dla dolnej połowy i 7.60% dla górnej połowy. Dla tego genotypu najłatwiej jest dokonać poprawy dla słabych (poniżej max(fitness)/2) wartości fitness. Pamiętać jednak trzeba, że w tym przypadku max(fitness) to jedynie 1.14. Widać również że reprezentacja nie pozwala w łatwy sposób na konstrukcję osobników, które mają wysokie i niskie wartości (objawia się to widocznymi pionowymi "liniami"). Tak jak dla pozostałych reprezentacji im wyższa wartość fitness rodzica, tym trudniej poprawić fitness. Dla najlepszych osobników oryginalnych łatwo popsuć rozwiązanie o dużą (ponad dwukrotnie) wartość - z fitness w okolicach 1 wystarczy jeden ruch (jedna mutacja) aby znaleźć się w fitness równym około 0.2-0.4.

Mimo tego, że na każdym wykresie widoczne są osobniki które powstały poprzez mutację i różnią się o dużo wartością fitness od swojego rodzica, to warto zwrócić też uwagę na to, że duża część nowych rozwiązań oscyluje w okolicach prostej y=x dla każdej reprezentacji. 


## Zadanie 2

Dla tego zadania z zebranych próbek wybrałem 250 osobników. Jako wizualizację wybrałem heatmapę - jasne punkty oznaczają niski fitness, a ciemne wysoki fitness [2-krzyzowania]. Dodatkowo przygotowałem również dwa wykresy, które pokazują czy potomek jest lepszy od przynajmniej jednego z rodziców [2-krzyzowania-lepszy-or] oraz od obu rodziców [2-krzyzowania-lepszy-and]. Puste przestrzenie w wykresach to niepoprawni potomkowie. Jako statystykę wyliczyłem ile procent wszystkich krzyżowań skutkowało wartością fitness, która jest lepsza od obu rodziców. Statystyka: f0: 0.76%, f1: 1.71%, f4: 2.72%, f9: 6.95%. 

Na głównym wykresie [2-krzyzowania] widać, że im lepsi rodzice, tym lepsze otrzymywane dzieci. Jest to szczególnie widoczne dla f0, trochę mniej dla f1 i f4 (wartości są bardziej rozłożone po całym wykresie), a najmniej dla f9, ale trend zachowany jest dla wszystkich reprezentacji. Trzeba również pamiętać, że dla f9 najlepsi rodzice są prawie 2 razy gorsi niż najlepsi dla np. reprezentacji f4. To, że dla słabych rodziców otrzymujemy słabe dzieci nie powinno jednak prowadzić do wniosku, że nie warto ich krzyżować. Jeżeli spojrzymy na wykresy 2-krzyzowania-lepszy-or i 2-krzyzowania-lepszy-and to widać, że to właśnie głównie dla słabych rodziców uzyskujemy poprawę w wartości fitness. Może być to kluczowe podczas ewolucji. Co ciekawe, dla reprezentacji f0 na [2-krzyzowania-lepszy-and] widać, że ulepszenia następują głównie dla rodziców, którzy mają podobny fitness, a nie jak w przypadku f1, f4 i f9 gdzie pomarańczowe punkty znajdują się na całym wykresie. Najwięcej popraw jest dla f9, później f4, f1 i na końcu dla f0. 


## Zadanie 3

Na wykresach ciemne linie oznaczają najlepsze rozwiązania początkowe, a im jaśniejsze tym słabszy punkt startowy. Ogólny trend na wszystkich wykresach jest taki sam - wartości fitness spadają. Dla reprezentacji f0 i f4 kończą się w zakresie (0, 0.5), dla f1 w zakresie (0, 0.25) z jednym outlierem, a dla f9 od mniej więcej 10 iteracji oscylują w okolicach wartości 0.2. 

Dla f0 można zaobserwować duże skoki w fitnessie. Przykładowo najlepsze rozwiązanie praktycznie od razu spada do wartości bliskich 0. Niektóre rozwiązania utrzymują swój fitness dość długo (rozwiązanie 7 licząc od najlepszego), ale ostatecznie i tak gwałtownie wartość fitnessu spada. Dla f1 spadek jest również nagły (szczególnie dla środkowej grupy rozwiązań), ale od 7 iteracji nie ma już nagłych wzrostów/spadków, a stopniowe zmniejszanie się fitnessu. Dla f4 również następuje gwałtowny spadek, ale niektóre z rozwiązań jeszcze się poprawiają (okolice 20-25 iteracji). Dla f9 widać największy nieporządek w przebiegach. Rozwiązania prawie w każdej iteracji zmniejszają albo zwiększają swój fitness. Może być to nieprzyjazne dla algorytmu ewolucji, ponieważ wskazuje na spore "postrzępienie" krajobrazu, w przeciwieństwie do reprezentacji f0, f1 i f4.


## Zadanie 4

Tak, związki są widoczne. Dla reprezentacji f4 uzyskiwane są najlepsze wartości, ponieważ dzięki mutacji można osiągnąć szybko dobre osobniki, a krzyżowanie pozwala na uzyskiwanie osobników lepszych częściej niż w przypadku f0 i f1. Te reprezentacje dla mutacji mają podobną charakterystykę jak f4, ale słabiej krzyżuje się osobniki. Najgorsze wyniki osiąga f9, w przypadku którego krajobraz jest postrzępiony (widoczne szczególnie w zadaniu nr 3).

Do zbadania globalnej wypukłości krajobrazu należałoby zebrać próbki (rozwiązania). Następnie dla każdej próbki liczymy średnie podobieństwo do rozwiązań nie gorszych (np. odległością edycyjną). W jednym wektorze umieszczamy fitness osobnika, a w drugim otrzymane podobieństwo. W kolejnym kroku liczymy korelację (albo korelację rangową) pomiędzy otrzymanymi wartościami.