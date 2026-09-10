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

AI Portfolio Assistant to rozwijany przeze mnie projekt flagowy, którego celem jest przekształcenie portfolio i CV online w interaktywną aplikację AI. Asystent ma umożliwiać rekruterom i osobom technicznym zadawanie pytań o moje doświadczenie zawodowe, wykształcenie, projekty i umiejętności.

Projekt powstaje jako praktyczne środowisko do nauki i zastosowania AI engineeringu. Chcę samodzielnie przejść przez projektowanie architektury, przygotowanie danych, integrację modelu językowego, retrieval, ewaluację, testy i wdrożenie. Poszczególne technologie będę dodawał wtedy, gdy będą potrzebne do rozwiązania konkretnego problemu.

## Problem i użytkownicy

Klasyczne portfolio wymaga samodzielnego przeglądania sekcji strony i dokumentu PDF. Celem asystenta jest ułatwienie dotarcia do konkretnych informacji za pomocą pytań w języku naturalnym, np. o moje doświadczenie z deep learningiem, szczegóły pracy magisterskiej lub technologie wykorzystane w projektach.

Głównymi użytkownikami są rekruterzy oraz osoby oceniające moje kompetencje techniczne. Asystent ma pomagać w poznaniu mojego profilu zawodowego, ale nie ma udawać, że jest mną, ani podejmować decyzji rekrutacyjnych.

## Aktualny stan implementacji

Na obecnym etapie działa lokalna aplikacja portfolio z backendem Python i FastAPI. Frontend wykorzystuje HTML, CSS, Jinja2 i JavaScript. Strona obsługuje język polski i angielski, zawiera sekcje „O mnie”, „Projekty” i „Kontakt” oraz umożliwia pobranie CV w formacie PDF.

Zaimplementowałem wspólny layout Jinja2, routing podstron, responsywną nawigację oraz osobne pliki JavaScript dla zachowań wspólnych i specyficznych dla podstron. Strona Projects jest generowana z uporządkowanych danych JSON. Każdy projekt posiada własny adres oparty na stabilnym slug-u oraz sekcje szczegółowe, do których można odsyłać za pomocą kotwic URL.

Kod portfolio znajduje się w publicznym repozytorium GitHub. Projekt ma opis zależności Pythona, plik `.gitignore`, przykładową konfigurację środowiskową i dokumentację uruchomienia. Przygotowywana jest również osobna, dwujęzyczna baza wiedzy w formacie Markdown.

Część konwersacyjna AI, embeddings, wyszukiwanie wektorowe, testy automatyczne i deployment nie są jeszcze ukończone. Nie przedstawiam ich jako gotowych funkcjonalności.

## Planowana architektura AI

Docelowy przepływ zapytania ma wyglądać następująco:

1. Użytkownik wpisuje pytanie na dedykowanej podstronie asystenta.
2. Frontend wysyła zapytanie do backendu FastAPI.
3. Backend przygotowuje kontekst rozmowy i wyszukuje odpowiednie fragmenty zatwierdzonej knowledge base.
4. Model językowy otrzymuje pytanie, instrukcje oraz wybrane fragmenty źródłowe.
5. Odpowiedź jest zwracana wraz z odnośnikami do odpowiednich stron i sekcji portfolio.

Planowane jest zastosowanie Retrieval-Augmented Generation (RAG), czyli połączenia wyszukiwania informacji z generowaniem odpowiedzi przez LLM. Dokumenty Markdown będą źródłem wiedzy, a indeks wektorowy ich odtwarzalną reprezentacją.

## Knowledge base i źródła

Knowledge base będzie zawierała wyłącznie informacje, które świadomie zatwierdzę do publicznego udostępnienia. Obejmie profil zawodowy, doświadczenie, wykształcenie, umiejętności i szczegółowe opisy projektów.

Dokumenty będą miały stabilne identyfikatory, wersje językowe oraz metadane pozwalające powiązać je z publicznymi adresami portfolio. Asystent nie będzie automatycznie przeszukiwał mojego prywatnego dysku, prywatnych repozytoriów ani niepublicznych danych osobowych.

Nie chcę, aby bot odpowiadał na podstawie informacji prywatnych lub niezatwierdzonych. Jeśli wiedza nie wystarcza do udzielenia odpowiedzi, system powinien jasno komunikować brak podstaw zamiast zgadywać.

## Planowany stack i decyzje techniczne

Obecnie używane technologie to Python, FastAPI, Jinja2, HTML, CSS i JavaScript. Do dalszego rozwoju planuję wykorzystać PostgreSQL z rozszerzeniem pgvector, SQLAlchemy, Pydantic, zewnętrzne API LLM i embeddings, pytest, Docker oraz GitHub Actions.

Wybór konkretnego dostawcy modeli pozostaje otwarty. Chcę porównać dostępne rozwiązania pod kątem jakości odpowiedzi w języku polskim i angielskim, kosztu, opóźnienia oraz warunków przetwarzania danych. Kod aplikacji ma być możliwie niezależny od jednego providera.

Na początku nie planuję używać rozbudowanego frameworka agentowego. Najpierw chcę zrozumieć i samodzielnie zaimplementować podstawowy przepływ RAG, a dopiero później ocenić, czy dodatkowe biblioteki rzeczywiście upraszczają projekt.

## Planowana ewaluacja

Projekt ma posiadać własny zbiór pytań testowych obejmujący doświadczenie, projekty, umiejętności, pytania przekrojowe oraz pytania, na które knowledge base nie zawiera odpowiedzi.

Chcę oddzielnie oceniać jakość retrievalu i jakość generowanej odpowiedzi. W planie są eksperymenty dotyczące podziału dokumentów na chunki, liczby pobieranych fragmentów, sposobu wyszukiwania i doboru modelu. Będę również analizował przypadki, w których system zwraca niewłaściwe źródła, niepoprawne fakty lub odpowiedzi bez wystarczającego uzasadnienia.

Wyniki eksperymentów zostaną udokumentowane dopiero po ich przeprowadzeniu. Nie deklaruję jeszcze żadnych wartości metryk.

## Bezpieczeństwo i prywatność

Klucze API i hasła nie będą umieszczane w publicznym repozytorium ani w kodzie frontendowym. Dostęp do usług zewnętrznych będzie realizowany przez backend z odpowiednią konfiguracją środowiskową.

Planowane są ograniczenia liczby zapytań, obsługa błędów, kontrola kosztów oraz ochrona przed próbami wykorzystania treści źródłowych lub pytań użytkownika do zmiany zasad działania asystenta. Dokumenty pobrane przez RAG będą traktowane jako dane, a nie jako instrukcje o wyższym priorytecie.

W publicznej wersji nie zamierzam gromadzić niepotrzebnych danych osobowych użytkowników. Szczegóły retencji logów i polityki prywatności zostaną ustalone przed wdrożeniem.

## Planowane funkcjonalności dodatkowe

Po ukończeniu podstawowego, działającego RAG rozważam dodanie analizy treści ogłoszenia o pracę. Funkcja miałaby porównywać wymagania stanowiska z udokumentowanymi umiejętnościami i projektami, wskazując zarówno potwierdzone dopasowania, jak i braki w dostępnych informacjach.

W dalszym etapie planuję również wybrane użycie tool callingu, np. do pobierania uporządkowanych danych o projektach. Nie będzie to jednak pełnoprawny autonomiczny agent, jeśli taki poziom złożoności nie będzie potrzebny.

## Mój wkład i zdobywane umiejętności

Samodzielnie rozwijam istniejącą aplikację portfolio i projektuję kolejne warstwy systemu AI. Dotychczas uporządkowałem strukturę aplikacji, nawigację, dane projektów i publiczne repozytorium oraz rozpocząłem przygotowanie dokumentów knowledge base.

Projekt ma pozwolić mi zdobyć praktyczne doświadczenie w projektowaniu i utrzymywaniu aplikacji LLM, wyszukiwaniu semantycznym, pracy z bazą danych, testowaniu, konteneryzacji, ewaluacji i deploymentcie. Ukończone elementy będę dokumentował na bieżąco, tak aby opis projektu odzwierciedlał rzeczywisty stan implementacji.

## Źródła i aktualizacja dokumentu

Repozytorium projektu: https://github.com/kubaperkowski22/jakub-perkowski-portfolio

Dokument opisuje stan projektu oraz planowane kierunki rozwoju. Przed każdym większym etapem i po jego zakończeniu będzie aktualizowany, aby oddzielać funkcjonalności już zaimplementowane od planowanych. Nie zawiera prywatnych informacji, kluczy API ani danych nieprzeznaczonych do publicznego udostępnienia.
