---
id: project.ai-portfolio-assistant
language: pl
title: AI Portfolio Assistant
source_type: project
source_slug: ai-portfolio-assistant
source_path: /projekty/ai-portfolio-assistant
visibility: public
---

# AI Portfolio Assistant

## Kontekst i cel projektu

AI Portfolio Assistant to chatbot osadzony w portfolio Jakuba, którego zadaniem jest odpowiadanie na pytania dotyczące jego doświadczenia zawodowego, projektów, wykształcenia i umiejętności.

Projekt powstał jako praktyczne rozwinięcie kompetencji związanych z budową aplikacji wykorzystujących modele językowe. Głównym celem było stworzenie systemu RAG działającego na kontrolowanym zbiorze publicznych informacji, z naciskiem na poprawność odpowiedzi, cytowanie źródeł, ograniczanie halucynacji, bezpieczeństwo oraz możliwość ewaluacji działania systemu.

Asystent mówi o Jakubie w trzeciej osobie i nie podszywa się pod niego.

## Architektura aplikacji

Backend aplikacji został zbudowany w Pythonie z wykorzystaniem FastAPI. Warstwa frontendowa wykorzystuje Jinja2, HTML, CSS i JavaScript bez dodatkowego frameworka frontendowego.

Wiedza wykorzystywana przez chatbota jest utrzymywana w dwujęzycznej bazie wiedzy w plikach Markdown. Dokumenty są traktowane jako źródło prawdy, natomiast PostgreSQL z rozszerzeniem pgvector pełni rolę odtwarzalnego indeksu wyszukiwania.

Proces RAG składa się z dwóch głównych części:

1. procesu offline:
   - wczytanie i walidacja dokumentów,
   - podział dokumentów na fragmenty na podstawie struktury Markdown,
   - wygenerowanie embeddings,
   - zapis fragmentów i wektorów do PostgreSQL z pgvector;

2. procesu online:
   - przygotowanie zapytania użytkownika,
   - wygenerowanie embeddingu zapytania,
   - semantyczne wyszukiwanie najbardziej pasujących fragmentów,
   - przekazanie odzyskanego kontekstu do modelu językowego,
   - wygenerowanie odpowiedzi opartej na źródłach,
   - walidacja cytowań i zwrócenie odpowiedzi wraz ze źródłami.

## Retrieval i embeddings

Do wyszukiwania semantycznego wykorzystywane są embeddings oraz PostgreSQL z rozszerzeniem pgvector.

Tekst wykorzystywany do generowania embeddingu fragmentu zawiera tytuł dokumentu, nazwę sekcji, opcjonalną podsekcję oraz treść fragmentu. Oryginalna treść pozostaje zachowana oddzielnie i jest wykorzystywana jako materiał źródłowy do generowania odpowiedzi i cytowania.

Retriever filtruje wyniki według języka, dzięki czemu polskie pytania korzystają z polskich źródeł, a angielskie z angielskich.

Dla obecnego niewielkiego zbioru wiedzy wykorzystywane jest dokładne wyszukiwanie wektorowe bez indeksu HNSW. Jest to świadoma decyzja wynikająca z małej liczby fragmentów.

## Generowanie odpowiedzi i cytowania

Model językowy otrzymuje wyłącznie fragmenty odnalezione przez warstwę retrieval oraz kontrolowane instrukcje systemowe.

Odpowiedź ma ustrukturyzowaną postać zawierającą:

- informację, czy pytanie może zostać odpowiedziane na podstawie dostępnych źródeł;
- treść odpowiedzi;
- listę numerów wykorzystanych źródeł.

Odpowiedzi zawierają cytowania w formacie `[1]`, `[2]` itd. Backend weryfikuje, czy wszystkie numery cytowań rzeczywiście odnoszą się do fragmentów zwróconych przez retriever oraz czy cytowania w tekście są zgodne z ustrukturyzowaną listą źródeł.

Do użytkownika zwracane są tylko źródła rzeczywiście wykorzystane w odpowiedzi.

Kliknięcie cytowania lub źródła prowadzi do odpowiedniej strony portfolio. Dla wybranych sekcji strony „O mnie” obsługiwane są również deep linki, które otwierają właściwą sekcję, np. wykształcenie lub doświadczenie.

## Abstention i ograniczanie halucynacji

Jeżeli dostępne źródła nie zawierają wystarczających informacji, chatbot powinien odmówić udzielenia konkretnej odpowiedzi zamiast uzupełniać ją na podstawie domysłów.

Brak informacji w bazie wiedzy nie jest interpretowany jako dowód, że dana rzecz nie istnieje.

Podczas eksperymentów analizowano również możliwość zastosowania progu odległości wektorowej jako automatycznego mechanizmu abstention. Na małym zestawie testowym zakresy wyników dla pytań odpowiedzialnych i nieodpowiedzialnych nakładały się na siebie, dlatego nie wprowadzono arbitralnego progu similarity.

## Kontekst rozmowy

Chatbot obsługuje krótki kontekst rozmowy.

Do retrievalu wykorzystywane są bieżące pytanie oraz ostatnie pytania użytkownika, dzięki czemu możliwe są follow-upy takie jak:

„A które z nich były związane z bazą danych?”

Poprzednie odpowiedzi modelu mogą być przekazywane do generowania jako kontekst rozmowy, ale nie są traktowane jako źródło faktów i nie są wykorzystywane jako materiał do retrieval.

Historia jest obecnie przechowywana po stronie przeglądarki i nie jest trwale zapisywana w bazie danych.

## Dwujęzyczność

Portfolio i chatbot obsługują język polski i angielski.

Język interfejsu, retrievalu, instrukcji dla modelu oraz odpowiedzi jest kontrolowany przez parametr języka aplikacji. Linki do źródeł zachowują aktualnie wybraną wersję językową.

## API i komunikacja z frontendem

Aplikacja udostępnia zwykły endpoint JSON oraz endpoint oparty na Server-Sent Events.

SSE jest wykorzystywane do przekazywania informacji o stanie przetwarzania i końcowego wyniku. Odpowiedź modelu nie jest obecnie streamowana token po tokenie.

Pozwala to zachować walidację całej ustrukturyzowanej odpowiedzi przed pokazaniem jej użytkownikowi.

## Ewaluacja retrievalu

Dla pierwszego ręcznie przygotowanego zestawu 12 pytań w języku polskim i angielskim uzyskano:

- Document Hit@1: 100%;
- Document Hit@5: 100%;
- Section Hit@1: 83,3%;
- Section Hit@5: 91,7%;
- Section Hit@8: 100%;
- MRR: 0,873.

Na podstawie tych wyników liczba fragmentów przekazywanych do generowania została zwiększona z `top_k=5` do `top_k=8`.

Zestaw 12 pytań jest developerskim zestawem ewaluacyjnym, a nie rozbudowanym benchmarkiem produkcyjnym.

## Testowanie

Projekt posiada automatyczne testy obejmujące między innymi:

- ładowanie i walidację dokumentów Knowledge Base;
- chunking i zachowanie pełnej treści dokumentów;
- kontrakt warstwy RAG;
- obsługę odpowiedzi i abstention;
- walidację cytowań;
- zachowanie historii rozmowy;
- endpointy FastAPI;
- odpowiedzi SSE;
- rate limiting.

Testy wykorzystują fake providery i monkeypatching tam, gdzie nie jest potrzebne rzeczywiste połączenie z modelem językowym lub bazą danych, dzięki czemu podstawowe testy są deterministyczne i nie generują kosztów API.

## Bezpieczeństwo

Klucze API i dane konfiguracyjne są przechowywane po stronie serwera i nie są udostępniane frontendowi.

Aplikacja posiada między innymi:

- ograniczenie długości wiadomości i historii rozmowy;
- rate limiting dla endpointów chatu;
- walidację struktury odpowiedzi modelu;
- walidację numerów cytowań;
- instrukcje ograniczające prompt injection;
- zasadę odpowiadania wyłącznie na podstawie zatwierdzonych źródeł;
- podstawowe nagłówki bezpieczeństwa HTTP;
- brak permissive CORS, ponieważ frontend i API działają w tym samym originie.

Rate limiter jest obecnie implementacją in-memory przeznaczoną dla pojedynczej instancji aplikacji. W środowisku wieloinstancyjnym wymagałby współdzielonego magazynu stanu, np. Redis.

## Technologie

W projekcie wykorzystywane są między innymi:

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- PostgreSQL;
- pgvector;
- OpenAI API;
- embeddings;
- Jinja2;
- HTML;
- CSS;
- JavaScript;
- Server-Sent Events;
- pytest;
- Docker dla PostgreSQL.

Architektura providerów dla embeddings i modelu językowego została oddzielona od głównej logiki RAG, aby ograniczyć zależność aplikacji od jednego dostawcy API.

## Mój wkład i zdobywane umiejętności

Jakub samodzielnie zaprojektował i implementuje architekturę projektu.

Praca nad projektem obejmuje między innymi:

- projektowanie i implementację pipeline'u RAG;
- przygotowanie dwujęzycznej bazy wiedzy;
- chunking dokumentów;
- integrację embeddings i wyszukiwania wektorowego;
- pracę z PostgreSQL i pgvector;
- integrację modelu językowego;
- projektowanie mechanizmu cytowań i abstention;
- przygotowanie ewaluacji retrievalu;
- obsługę kontekstu rozmowy;
- projektowanie API w FastAPI;
- komunikację SSE;
- testy jednostkowe i API;
- podstawowe zabezpieczenia aplikacji LLM;
- projektowanie interfejsu chatu.

## Aktualny stan projektu

Projekt został ukończony i wdrożony publicznie jako działająca wersja v1.

Aplikacja działa na Renderze, korzysta z zarządzanej bazy PostgreSQL z pgvector i udostępnia dwujęzyczny chatbot RAG z cytowaniami, obsługą follow-up questions, abstention oraz Server-Sent Events.

Projekt posiada testy automatyczne i pipeline CI oparty na GitHub Actions.

## Live demo
Aplikacja jest dostępna na tej stronie pod adresem "/chat?lang=pl" lub "/chat?lang=en"