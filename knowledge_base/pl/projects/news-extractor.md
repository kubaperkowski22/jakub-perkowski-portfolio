---
id: project.news-extractor
language: pl
title: News Extractor
source_type: project
source_slug: news-extractor
source_path: /projekty/news-extractor
visibility: public
---

# News Extractor

## Kontekst i cel projektu

News Extractor to samodzielnie wykonany przeze mnie projekt akademicki z przedmiotu „Przetwarzanie języka naturalnego”. Projekt dotyczył przetwarzania polskich tekstów, klasyfikacji wiadomości oraz ekstrakcji informacji z treści.

Celem było praktyczne poznanie klasycznych metod NLP i machine learningu oraz porównanie kilku algorytmów klasyfikacji na tym samym zbiorze testowym. Projekt ma mniejszy zakres niż moje prace dyplomowe i AI Portfolio Assistant, ale pokazuje doświadczenie w przygotowaniu danych tekstowych, trenowaniu modeli oraz analizie ich wyników.

## Dane i przygotowanie tekstu

Dane treningowe przygotowałem samodzielnie. Zbiór był wykorzystywany do trenowania i porównywania modeli klasyfikujących polskie teksty.

W projekcie wykorzystywałem narzędzia do przetwarzania języka polskiego, w tym spaCy, oraz reprezentację tekstu TF-IDF. TF-IDF przekształca dokumenty w numeryczne wektory cech na podstawie występowania słów i ich znaczenia w całym korpusie. Takie wektory mogą następnie stanowić wejście dla klasycznych klasyfikatorów.

Nie mam obecnie potwierdzonej pełnej specyfikacji zbioru, liczby klas, dokładnego podziału treningowego i walidacyjnego ani wszystkich etapów preprocessingu. Nie przypisuję więc projektowi niezweryfikowanych procedur ani liczebności. Dane przygotowane z pomocą modelu generatywnego nie są też równoważne niezależnie zebranym i ręcznie oznaczonym danym rzeczywistym.

## Modele klasyfikacyjne

Porównałem trzy klasyczne algorytmy machine learningu:

- **Support Vector Machine (SVM)** — klasyfikator wyznaczający granicę decyzyjną między klasami na podstawie wektorowej reprezentacji tekstu.
- **Naive Bayes** — probabilistyczny klasyfikator oparty na twierdzeniu Bayesa i założeniu warunkowej niezależności cech.
- **Random Forest** — model zespołowy łączący wiele drzew decyzyjnych.

Modele zostały wykorzystane do porównania skuteczności klasyfikacji. Nie był to projekt polegający na trenowaniu modelu językowego typu LLM ani na fine-tuningu transformera.

## Ekstrakcja informacji

Projekt obejmował również część związaną z ekstrakcją informacji z tekstu. Do analizy języka polskiego wykorzystywałem spaCy, m.in. do pracy z tokenami i strukturą językową.

Szczegółowa rola poszczególnych komponentów ekstrakcji, reguł i reprezentacji wymaga ponownej weryfikacji w kodzie. Nie deklaruję obecnie konkretnych wyników jakości ekstrakcji ani nie utożsamiam jej automatycznie z klasyfikacją wiadomości.

## Ewaluacja klasyfikacji

Wyniki oceniałem na podstawie macierzy pomyłek utworzonych dla każdego modelu. Na zbiorze testowym obejmującym 302 rekordy uzyskałem następującą liczbę błędnych klasyfikacji:

| Model | Błędne klasyfikacje | Poprawne klasyfikacje | Accuracy |
|---|---:|---:|---:|
| SVM | 29 | 273 | 90,40% |
| Naive Bayes | 24 | 278 | 92,05% |
| Random Forest | 46 | 256 | 84,77% |

Accuracy obliczono jako liczbę poprawnych klasyfikacji podzieloną przez 302. W tym konkretnym porównaniu najmniej błędów popełnił Naive Bayes, następnie SVM, a najwięcej Random Forest.

Wyniki dotyczą jednego opisanego zbioru testowego. Nie stanowią dowodu, że Naive Bayes jest uniwersalnie najlepszym modelem do klasyfikacji tekstu. Nie mam obecnie potwierdzonych wyników precision, recall, F1-score, przedziałów ufności ani eksperymentów powtarzanych z różnymi podziałami danych, dlatego nie podaję takich wartości.

## Mój wkład i zdobyte umiejętności

Samodzielnie realizowałem projekt akademicki, przygotowałem dane treningowe, wykorzystałem klasyczne modele klasyfikacyjne oraz porównałem ich wyniki za pomocą macierzy pomyłek.

Projekt pozwolił mi przećwiczyć podstawy NLP, reprezentacji tekstu, klasyfikacji nadzorowanej i interpretowania wyników modeli. Stanowi uzupełnienie moich bardziej rozbudowanych projektów deep learningowych i aplikacyjnych.

## Ograniczenia i dalszy rozwój

Najważniejszym ograniczeniem jest niewielki, akademicki charakter projektu oraz wykorzystanie niewielkiej ilości danych. Nie przeprowadziłem obecnie dodatkowej weryfikacji jakości etykiet, reprezentatywności danych ani odporności modeli na teksty pochodzące z innych źródeł.

Przy ewentualnej rozbudowie warto byłoby odtworzyć pełny pipeline, udokumentować klasy i pochodzenie danych, przeprowadzić dodatkową walidację oraz porównać wyniki z nowoczesnymi reprezentacjami tekstu. Nie są to jednak funkcjonalności, które przedstawiam jako już zrealizowane.

## Źródła i zakres dokumentu

Repozytorium projektu: https://github.com/kubaperkowski22/News-extractor---NLP

Opis samodzielnego wykonania projektu oraz liczby błędów poszczególnych modeli pochodzi z informacji potwierdzonych przeze mnie. Dokument jest krótkim opisem portfolio, a nie pełną dokumentacją eksperymentalną. Szczegóły implementacyjne, których obecnie nie pamiętam lub nie zostały ponownie zweryfikowane, nie są przedstawiane jako potwierdzone fakty.
