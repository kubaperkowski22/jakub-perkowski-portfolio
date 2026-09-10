---
id: project.survival-analysis
language: pl
title: Głębokie sieci neuronowe w analizie przeżycia
source_type: project
source_slug: survival-analysis
source_path: /projekty/survival-analysis
visibility: public
---

# Głębokie sieci neuronowe w analizie przeżycia

## Kontekst i cel projektu

Projekt powstał w ramach pracy magisterskiej poświęconej zastosowaniu głębokich sieci neuronowych w analizie przeżycia na danych onkologicznych. Analiza przeżycia dotyczy modelowania czasu do określonego zdarzenia, np. zgonu pacjenta, z uwzględnieniem obserwacji cenzurowanych, dla których nie znamy dokładnego czasu wystąpienia zdarzenia.

Głównym celem pracy było zaprojektowanie, zaimplementowanie i zbadanie mechanizmu zwiększającego możliwość analizy działania modeli DeepSurv i DeepHit. Chciałem uzyskać informację, które cechy wejściowe były silniej ważone przez sieć, a następnie sprawdzić, czy dodanie tego mechanizmu wpływa na jakość predykcji. Interpretowalność była główną motywacją; poprawa metryk nie była jedynym celem.

Praca miała charakter badawczo-implementacyjny. Nie była kliniczną walidacją systemu diagnostycznego ani wdrożeniem narzędzia do podejmowania decyzji medycznych.

## Modele bazowe

Porównano dwa podejścia do głębokiego uczenia w analizie przeżycia:

- **DeepSurv** — model oparty na sieci neuronowej i modelu proporcjonalnych hazardów Coxa. Sieć uczy się nieliniowej reprezentacji cech i zwraca skalarny predyktor ryzyka. Trenowanie wykorzystuje funkcję straty opartą na częściowej wiarygodności Coxa. Model służy m.in. do porządkowania pacjentów według ryzyka oraz wyznaczania krzywych przeżycia.
- **DeepHit** — podejście dyskretne, w którym czas jest dzielony na przedziały, a sieć przewiduje rozkład prawdopodobieństwa zdarzenia w czasie. W implementacji wykorzystano DeepHitSingle, czyli wariant dla jednego rodzaju zdarzenia. Funkcja straty łączy składnik związany z prawdopodobieństwem zdarzenia ze składnikiem rankingowym.

Modele bazowe stanowiły punkt odniesienia dla dwóch własnych wariantów z modułem attention. W eksperymentach analizowano łącznie cztery architektury: DeepSurv, DeepHit, AttentionDeepSurv i AttentionDeepHit.

## Własne modyfikacje

### Moduł FeatureAttention

Zaimplementowałem w PyTorch moduł FeatureAttention umieszczony przed główną siecią neuronową. Dla wektora cech pacjenta moduł oblicza wektor wag, a następnie skaluje nim dane wejściowe.

Mechanizm składa się z trzech etapów:

1. Warstwa liniowa przekształca wektor wejściowy w wartości oceniające poszczególne cechy.
2. Funkcja softmax normalizuje wartości do dodatnich wag, których suma dla danego pacjenta wynosi 1.
3. Oryginalny wektor cech jest mnożony element po elemencie przez obliczone wagi, a wynik trafia do dalszej części sieci.

W zapisie matematycznym:

a(x) = softmax(Wx + b)

x_attended = x ⊙ a(x)

Wagi zależą od wejścia, więc mogą być inne dla różnych pacjentów. Ich wartości pokazują, jak moduł względnie waży cechy w danym przypadku. Nie oznacza to jednak automatycznie, że największa waga jest dowodem przyczynowego wpływu danej cechy na wynik.

### AttentionDeepSurv i AttentionDeepHit

Moduł został zintegrowany z dwiema architekturami bazowymi. Po przeskalowaniu cech dane przechodzą przez wielowarstwową sieć MLP. W wariancie DeepSurv wyjściem jest skalarny predyktor ryzyka, a w wariancie DeepHit wektor prawdopodobieństw dla przedziałów czasu.

Własne klasy zostały dostosowane do wrapperów biblioteki pycox. AttentionDeepSurv współpracuje z CoxPH, a AttentionDeepHit z DeepHitSingle. W przypadku modelu dyskretnego zastosowano 100 przedziałów czasowych. W konfiguracji DeepHitSingle wykorzystano parametry alpha = 0,2 oraz sigma = 0,1.

Dodałem również możliwość pobierania wag attention dla danych wejściowych bez śledzenia gradientów, aby można je było analizować po treningu i porównywać rankingi cech między modelami.

## Dane i preprocessing

### Pochodzenie i charakterystyka danych

Wykorzystano siedem zbiorów danych onkologicznych pochodzących z programu SEER (Surveillance, Epidemiology, and End Results) prowadzonego przez National Cancer Institute. Dane obejmowały różne grupy nowotworów, co umożliwiało porównanie modeli na zbiorach o odmiennej liczebności i poziomie cenzurowania.

| Grupa nowotworowa | Liczba pacjentów | Odsetek zdarzeń | Odsetek cenzurowanych |
|---|---:|---:|---:|
| Rak mózgu | 65 719 | 80% | 20% |
| Rak piersi | 741 107 | 51% | 49% |
| Białaczka | 145 407 | 69% | 31% |
| Rak płuc | 474 994 | 97% | 3% |
| Chłoniak | 229 218 | 62% | 38% |
| Rak prostaty | 664 874 | 57% | 43% |
| Rak jelita cienkiego | 21 026 | 63% | 37% |

Liczebności i odsetki pochodzą z tabeli 5.1 pracy. Największy zbiór w tym zestawieniu to rak piersi. Najmniejszy zbiór dotyczy raka jelita cienkiego.

### Przygotowanie cech

W pracy opisano przygotowanie danych za pomocą potoków preprocessingowych dostosowanych do poszczególnych zbiorów. Główne etapy obejmowały:

- usunięcie rekordów bez ustalonego czasu przeżycia (wartość null), zdefiniowanie zmiennej czasu oraz statusu zdarzenia i usunięcie identyfikatorów, które nie niosły wartości predykcyjnej;
- ujednolicenie formatów i typów danych, w tym konwersję wybranych wartości tekstowych na liczbowe;
- usunięcie kolumn, w których brakowało ponad 50% obserwacji;
- kodowanie zmiennych kategorycznych metodą one-hot encoding;
- podział danych na zbiór treningowy (60%), walidacyjny (20%) i testowy (20%), z zachowaniem powtarzalności podziału przez `random_state=42`;
- uzupełnianie braków wartościami mediany oraz standaryzację cech, z parametrami wyznaczanymi wyłącznie na zbiorze treningowym.

Rozdzielenie danych przed dopasowaniem imputera i skalera jest istotne, ponieważ ogranicza ryzyko przecieku informacji ze zbioru testowego do treningu. W szczegółowej analizie interpretowalności zwrócono też uwagę, że one-hot encoding utrudnia bezpośrednie przełożenie indeksów cech na czytelne nazwy kliniczne.

## Metodologia eksperymentów

### Główny eksperyment

Każdy z czterech modeli trenowano dziesięć razy na każdym z siedmiu zbiorów. Daje to 280 uruchomień treningowych w głównym porównaniu, bez wliczania dodatkowych eksperymentów wrażliwości i analizy przypadku.

Powtórzenia miały ograniczać wpływ losowej inicjalizacji wag. W opisie metodologii zaznaczono, że dla każdego zbioru zachowywano ten sam podział treningowy, walidacyjny i testowy, natomiast poszczególne treningi rozpoczynały się od nowych losowych wag. Wyniki agregowano, analizując średnie, zmienność oraz najlepsze uzyskane wartości.

### Parametry treningu

W głównym porównaniu zastosowano architekturę MLP z dwiema warstwami ukrytymi po 32 neurony, dropout 0,3 oraz learning rate 0,0001. Rozmiar batcha wynosił 256. Do optymalizacji wykorzystano Adam, a w module attention zastosowano również regularyzację L2.

Zastosowano early stopping monitorujący stratę walidacyjną, z patience równym 10 epok. Miało to ograniczać przeuczenie i skracać trening, gdy model przestawał poprawiać wynik na zbiorze walidacyjnym.

### Eksperymenty wrażliwości

Przed główną ewaluacją porównano różne konfiguracje na trzech reprezentatywnych zbiorach: raku płuc, raku prostaty i raku jelita cienkiego. Analizowano m.in. zwiększenie architektury z (32, 32) do (64, 64) oraz podniesienie dropout z 0,3 do 0,5.

Wyniki nie wskazywały na uniwersalną korzyść ze zwiększenia pojemności sieci. Silniejszy dropout mógł pogarszać wyniki, szczególnie na mniejszym zbiorze raka jelita cienkiego. Do głównego porównania wybrano konfigurację (32, 32), dropout 0,3 i learning rate 0,0001 jako kompromis między skutecznością, stabilnością i kosztem obliczeniowym.

## Ewaluacja

Do oceny wykorzystano dwie główne metryki:

- **C-index (concordance index)** — mierzy zdolność modelu do prawidłowego porządkowania porównywalnych obserwacji według ryzyka. Wyższa wartość oznacza lepszą dyskryminację.
- **Integrated Brier Score (IBS)** — zagregowana w czasie miara błędu prognozowanego prawdopodobieństwa przeżycia. Uwzględnia dokładność prognoz probabilistycznych w czasie; niższa wartość jest korzystniejsza.

Metryki odpowiadają na różne pytania. Model może dobrze porządkować pacjentów według ryzyka, a jednocześnie gorzej szacować prawdopodobieństwa przeżycia. Z tego powodu oceniano obie miary, zamiast opierać wnioski wyłącznie na C-index.

W eksperymentach wykorzystano m.in. PyTorch, torchtuples i pycox do budowy, treningu i ewaluacji modeli, a także pandas, NumPy, scikit-learn i lifelines do przetwarzania danych oraz analiz pomocniczych.

## Wyniki głównego porównania

Poniższe wartości pochodzą z tabel 6.4–6.10 pracy. Są to średnie IBS, średnie C-index i najlepsze C-index dla danej konfiguracji. Nie należy mylić najlepszego pojedynczego wyniku ze średnią z dziesięciu treningów. Wszystkie wartości podano z dokładnością zachowaną w pracy.

| Zbiór | Model | Średni IBS ↓ | Średni C-index ↑ | Najlepszy C-index ↑ |
|---|---|---:|---:|---:|
| Rak mózgu | DeepSurv | 0,0729 | 0,793 | 0,7938 |
| Rak mózgu | DeepHit | 0,1539 | 0,7944 | 0,7964 |
| Rak mózgu | AttentionDeepSurv | 0,0733 | 0,7935 | 0,7944 |
| Rak mózgu | AttentionDeepHit | 0,1464 | 0,7998 | 0,8018 |
| Rak piersi | DeepSurv | 0,1241 | 0,7727 | 0,7732 |
| Rak piersi | DeepHit | 0,1582 | 0,7782 | 0,7796 |
| Rak piersi | AttentionDeepSurv | 0,1247 | 0,773 | 0,7739 |
| Rak piersi | AttentionDeepHit | 0,1563 | 0,7767 | 0,7779 |
| Białaczka | DeepSurv | 0,1172 | 0,7028 | 0,7032 |
| Białaczka | DeepHit | 0,178 | 0,7105 | 0,7112 |
| Białaczka | AttentionDeepSurv | 0,105 | 0,7881 | 0,7891 |
| Białaczka | AttentionDeepHit | 0,17 | 0,7985 | 0,799 |
| Rak płuc | DeepSurv | 0,0319 | 0,7047 | 0,7052 |
| Rak płuc | DeepHit | 0,057 | 0,7078 | 0,7085 |
| Rak płuc | AttentionDeepSurv | 0,0319 | 0,7038 | 0,7046 |
| Rak płuc | AttentionDeepHit | 0,0572 | 0,7062 | 0,7065 |
| Chłoniak | DeepSurv | 0,1231 | 0,7488 | 0,7503 |
| Chłoniak | DeepHit | 0,1739 | 0,7654 | 0,7658 |
| Chłoniak | AttentionDeepSurv | 0,1247 | 0,7473 | 0,7489 |
| Chłoniak | AttentionDeepHit | 0,1751 | 0,7626 | 0,7641 |
| Rak prostaty | DeepSurv | 0,0952 | 0,769 | 0,7693 |
| Rak prostaty | DeepHit | 0,1447 | 0,7695 | 0,7701 |
| Rak prostaty | AttentionDeepSurv | 0,0952 | 0,7692 | 0,7698 |
| Rak prostaty | AttentionDeepHit | 0,1397 | 0,7699 | 0,7705 |
| Rak jelita cienkiego | DeepSurv | 0,1141 | 0,7714 | 0,7752 |
| Rak jelita cienkiego | DeepHit | 0,2084 | 0,7499 | 0,7746 |
| Rak jelita cienkiego | AttentionDeepSurv | 0,1146 | 0,7566 | 0,7823 |
| Rak jelita cienkiego | AttentionDeepHit | 0,1836 | 0,7756 | 0,7845 |

### Interpretacja wyników

Największą poprawę wskaźnika C-index odnotowano w przypadku białaczki. Średnia wartość C-index dla modelu DeepSurv wzrosła z 0,7028 do 0,7881 po zastosowaniu mechanizmu uwagi (attention), natomiast dla modelu DeepHit wzrost wyniósł z 0,7105 do 0,7985. Jednocześnie średnia wartość IBS spadła odpowiednio z 0,1172 do 0,105 oraz z 0,178 do 0,17.

W przypadku zbioru danych dotyczącego nowotworów mózgu model AttentionDeepHit osiągnął średni wskaźnik C-index na poziomie 0,7998 (w porównaniu do 0,7944 dla bazowego modelu DeepHit), przy jednoczesnym uzyskaniu niższej średniej wartości IBS (0,1464 wobec 0,1539). Dla nowotworu prostaty średnie wartości C-index wszystkich czterech modeli mieściły się w wąskim przedziale od 0,769 do 0,7699.

Nie wszystkie zmiany były korzystne. W przypadku zbioru danych dotyczącego nowotworów jelita cienkiego średni wskaźnik C-index modelu DeepSurv spadł z 0,7714 do 0,7566 po zastosowaniu mechanizmu uwagi, mimo że najlepszy indywidualny wynik C-index dla wariantu z uwagą był wyższy. W przypadku niektórych innych zbiorów danych zmiany były niewielkie lub prowadziły do ​​pogorszenia jednej z metryk.

Wniosek zależy zatem od danych i architektury: mechanizm uwagi może pozwolić na utrzymanie zbliżonej skuteczności predykcyjnej, a w niektórych przypadkach ją poprawić, jednak nie gwarantuje poprawy dla każdego zbioru danych. Wyniki nie potwierdzają tezy, jakoby zmodyfikowane warianty były uniwersalnie lepsze od swoich wersji bazowych.

## Interpretowalność i analiza wag attention

Po zakończeniu procesu uczenia wyznaczono rankingi pięciu cech o największych wagach dla każdego z siedmiu zbiorów danych. Porównano rankingi uzyskane dla modeli AttentionDeepSurv oraz AttentionDeepHit.

### Sposób tworzenia rankingów

Z analizy notatników wynika, że ​​wagi uwagi obliczano dla pacjentów ze zbioru testowego po zakończeniu uczenia. W przypadku pojedynczego wytrenowanego modelu wagi uśredniano wzdłuż wymiaru pacjentów, uzyskując jeden wektor średnich wag cech. Następnie cechy sortowano według ich średnich wag. Wizualizacja dla poszczególnych modeli prezentowała 15 najważniejszych cech. W głównych eksperymentach każda z dziesięciu serii treningowych skutkowała wyznaczeniem własnego wektora średnich wag cech. Następnie wektory te uśredniono, a wynikowy wektor posłużył do stworzenia ostatecznego rankingu 15 najważniejszych cech. W dalszej części pracy porównano pięć najważniejszych cech wyłonionych przez obie architektury oparte na mechanizmie uwagi (ang. *attention-based architectures*).

Zatem ranking uzyskany w głównym eksperymencie stanowi średnią uwzględniającą zarówno pacjentów ze zbioru testowego, jak i wyniki dziesięciu serii treningowych. Nie jest to ranking dotyczący pojedynczego pacjenta ani zestawienie oparte wyłącznie na wynikach najlepszej serii treningowej.

Wagi te odzwierciedlają relatywne znaczenie przypisywane cechom przez moduł uwagi. Nie należy ich interpretować jako pełnej miary wpływu danej cechy na ostateczną predykcję, wyjaśnienia przyczynowego ani klinicznego potwierdzenia istotności danej cechy.

### Porównanie rankingów cech

W przypadku niektórych zbiorów danych odnotowano bardzo wysoki stopień zgodności. Dla raka płuca i raka prostaty oba modele wskazały te same zestawy pięciu najważniejszych cech, choć nie zawsze w tej samej kolejności. W innych grupach zgodność była częściowa: najważniejsze cechy często się pokrywały, jednak ich kolejność oraz pozycje na dalszych miejscach rankingu mogły się różnić.

Analiza sugeruje, że różnice te mogą wynikać z odmiennych celów uczenia przyjętych w obu modelach: DeepSurv wykorzystuje funkcję straty powiązaną z modelem Coxa, podczas gdy DeepHit stosuje podejście oparte na czasie dyskretnym z dodatkowym składnikiem uwzględniającym ranking. Wagi mechanizmu uwagi zależą zatem od wyuczonej architektury oraz celu optymalizacji.

### Ograniczenia interpretacyjne

Mechanizm ten pozwala na analizę relatywnego znaczenia cech, jednak sam w sobie nie dowodzi, że dany parametr jest przyczyną zdarzenia medycznego. Nie dostarcza również pełnego, niezależnego od modelu wyjaśnienia każdej predykcji.

Istotnym ograniczeniem było wykorzystanie cech poddanych kodowaniu typu *one-hot*. Wagi odnoszą się do kolumn wejściowych, które mogą reprezentować poszczególne kategorie zmiennych klinicznych. Aby uzyskać czytelny ranking medyczny, konieczne jest zachowanie odwzorowania między przekształconymi kolumnami a oryginalnymi nazwami i kategoriami zmiennych.

W pracy wskazano również na możliwość dalszej weryfikacji interpretowalności modelu przy użyciu innych metod oraz konsultacji z ekspertami medycznymi. Zgodności między rankingami nie należy przedstawiać jako klinicznego potwierdzenia istotności poszczególnych biomarkerów.

## Szczegółowa analiza raka prostaty

Jako dodatkowe studium przypadku wybrano zbiór raka prostaty. W pracy uzasadniono ten wybór dużą liczebnością, stosunkowo zrównoważonym poziomem cenzurowania i stabilnością wyników predykcyjnych.

Zbiór obejmował 664 874 pacjentów, w tym 380 431 obserwacji zdarzenia (57,2%) i 284 443 obserwacje cenzurowane (42,8%).

W konfiguracji bazowej (32, 32), dropout 0,3, AttentionDeepSurv osiągnął średni C-index 0,7692 i średni IBS 0,0952. AttentionDeepHit uzyskał średni C-index 0,7699 i średni IBS 0,1397. Wyniki były zbliżone do modeli bazowych, a w przypadku AttentionDeepHit odnotowano niższy IBS niż dla DeepHit.

Analiza rankingów attention wykazała zgodność obu wariantów co do zestawu pięciu najważniejszych cech wejściowych. W pracy wymieniono ich indeksy po preprocessingu, jednak nie przedstawiono pełnego, jednoznacznego mapowania tych indeksów na oryginalne nazwy kliniczne. Z tego powodu w tym dokumencie nie przypisuję im nazw medycznych na podstawie domysłów.

## Mój wkład

W ramach pracy zaimplementowałem modele bazowe DeepSurv i DeepHit oraz opracowałem dwa własne warianty rozszerzone o mechanizm FeatureAttention. Zintegrowałem je z narzędziami do analizy przeżycia, przygotowałem potoki przetwarzania danych i przeprowadziłem porównawcze eksperymenty na siedmiu zbiorach onkologicznych.

Projekt obejmował również analizę wpływu konfiguracji sieci i regularyzacji, ocenę wyników za pomocą C-index i IBS, pobieranie oraz porównywanie wag attention, a także szczegółowe studium przypadku raka prostaty.

## Wnioski i zdobyte umiejętności

Projekt pozwolił mi zdobyć doświadczenie w implementacji i modyfikowaniu architektur deep learningowych, pracy z danymi cenzurowanymi, projektowaniu eksperymentów, przygotowaniu dużych zbiorów danych oraz analizie jakości modeli przy użyciu metryk właściwych dla analizy przeżycia.

Najważniejszym wnioskiem było to, że dodanie mechanizmu interpretowalności nie musi oznaczać istotnego pogorszenia jakości predykcji, a w części badanych konfiguracji może przynieść poprawę. Jednocześnie skuteczność zależy od charakterystyki danych, architektury i parametrów treningu, dlatego nie należy wyciągać wniosków o uniwersalnej przewadze jednego wariantu.

Praca pokazała również, że uzyskanie wag cech jest dopiero początkiem procesu interpretacji. Do użytecznego wyjaśnienia predykcji potrzebne są m.in. czytelne mapowanie cech, analiza stabilności oraz odpowiednia walidacja w kontekście dziedzinowym.

## Ograniczenia badania i dalszy rozwój

Badanie opierało się na retrospektywnych danych onkologicznych i nie stanowiło prospektywnej ani klinicznej walidacji systemu. Wyników nie należy interpretować jako dowodu przydatności do podejmowania decyzji terapeutycznych.

W dalszym rozwoju wskazano automatyzację tłumaczenia indeksów cech po preprocessingu na czytelne nazwy medyczne, eksplorację bardziej zaawansowanych mechanizmów attention oraz weryfikację interpretowalności z udziałem ekspertów dziedzinowych. Dalsze badania mogłyby także obejmować bardziej szczegółową analizę stabilności i uogólniania wyników.

## Źródła i zakres opracowania

Podstawą dokumentu jest fragment własnej pracy magisterskiej „Głębokie sieci neuronowe w analizie przeżycia — eksperymenty”, obejmujący rozdziały 5, 6 i 7 (metodologię, wyniki oraz podsumowanie), oraz informacje o własnym wkładzie potwierdzone przez autora.

Repozytorium projektu: https://github.com/kubaperkowski22/DL_SurvivalAnalysis

Liczby w tabelach odtworzono z tabel 5.1 oraz 6.4–6.10 pracy. Opisy implementacji i konfiguracji przedstawiają metodologię udokumentowaną w pracy; nie są deklaracją, że każda z tych informacji została dodatkowo zweryfikowana przez ponowne uruchomienie kodu. Dokument nie zawiera danych identyfikujących pacjentów ani niepublicznych informacji medycznych.
