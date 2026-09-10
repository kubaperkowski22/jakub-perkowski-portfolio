---
id: project.diagnose-me
language: pl
title: DiagnoseMe
source_type: project
source_slug: diagnose-me
source_path: /projekty/diagnose-me
visibility: public
---

# DiagnoseMe

## Kontekst i cel projektu

DiagnoseMe powstał w ramach mojej pracy inżynierskiej na Politechnice Białostockiej, zatytułowanej „Aplikacja wspomagająca wstępną diagnozę medyczną i rekomendację dalszego postępowania z wykorzystaniem elementów sztucznej inteligencji”.

Celem było stworzenie aplikacji desktopowej dla systemu Windows, która umożliwia przeprowadzenie uporządkowanego wywiadu dotyczącego objawów i przedstawienie wstępnej oceny oraz sugestii dalszego postępowania. Projekt łączył klasyczną inżynierię oprogramowania, relacyjną bazę danych i zewnętrzny model językowy. Nie polegał na trenowaniu własnego modelu medycznego.

Był to prototyp akademicki. Nie został poddany klinicznej walidacji i nie stanowi certyfikowanego wyrobu medycznego. Generowane informacje nie zastępują konsultacji z lekarzem ani profesjonalnej diagnozy.

## Architektura i technologie

Aplikację zaimplementowałem w C# jako aplikację WPF z interfejsem opisanym w XAML. Projekt wykorzystywał platformę .NET, wzorzec MVVM oraz podział na warstwę prezentacji, logiki aplikacyjnej i danych.

Najważniejsze wykorzystane technologie i narzędzia:

- **WPF, XAML i C#** — interfejs desktopowy oraz logika aplikacji.
- **CommunityToolkit.Mvvm** — wsparcie dla wzorca MVVM i powiadamiania o zmianach właściwości.
- **MahApps.Metro i MahApps.Metro.IconPacks** — kontrolki, style i ikony interfejsu.
- **Entity Framework Core** — mapowanie encji, operacje na relacyjnej bazie danych i migracje.
- **Azure SQL / SQL Server** — chmurowa baza danych używana podczas działania projektu.
- **Microsoft.Extensions.DependencyInjection** — rejestracja i zarządzanie zależnościami.
- **OpenAI API** — zewnętrzny model językowy wykorzystywany do generowania odpowiedzi.
- **Inno Setup Compiler** — przygotowanie instalatora aplikacji.

Wzorzec MVVM pozwalał oddzielić widoki od ViewModeli i logiki. Asynchroniczne operacje, w szczególności komunikacja z API i bazą danych, pomagały zachować responsywność interfejsu podczas oczekiwania na odpowiedź.

## Proces wstępnej oceny objawów

Główną funkcjonalnością był wieloetapowy wywiad. Użytkownik rozpoczynał od formularza zawierającego podstawowe informacje, takie jak rok urodzenia, płeć, wzrost i waga. Następnie mógł wybrać objawy z listy obejmującej 31 pozycji.

Kolejny ekran przedstawiał dodatkowe pytania zależne od wybranych objawów. Dzięki temu aplikacja nie musiała zadawać wszystkich pytań każdemu użytkownikowi. Zebrane odpowiedzi wraz z podstawowymi danymi stanowiły kontekst dla zapytania do modelu językowego.

Przepływ można przedstawić następująco:

```text
Podstawowe dane użytkownika
          ↓
Wybór objawów z listy
          ↓
Dodatkowe pytania zależne od objawów
          ↓
Zbudowanie prompta
          ↓
Asynchroniczne żądanie HTTP do OpenAI API
          ↓
Odbiór i przetworzenie odpowiedzi
          ↓
Wstępna ocena, opis i zalecenia
          ↓
Opcjonalny zapis wyniku dla zalogowanego użytkownika
```

## Integracja z modelem językowym

Moduł AI wykorzystywał gotowy model GPT udostępniany przez OpenAI API. Dane z wywiadu były przekształcane w prompt, który określał zadanie modelu oraz oczekiwaną strukturę odpowiedzi. Zapytanie było wysyłane za pomocą klienta HTTP, a odpowiedź przetwarzana w aplikacji.

Wynik był dzielony na nazwę rozpoznawanej choroby lub problemu, opis oraz rekomendacje dalszego postępowania. Taki podział umożliwiał prezentowanie informacji w oddzielnych częściach interfejsu i zapisywanie ich w odpowiednich polach bazy danych.

W promptcie zastosowano również instrukcje dotyczące ignorowania odpowiedzi pustych lub niezwiązanych z wywiadem. Była to próba ograniczenia niepożądanego użycia funkcji, a nie gwarancja odporności na prompt injection lub inne manipulacje. Projekt nie wykorzystywał RAG, embeddings ani własnego treningu lub fine-tuningu modelu.

## Warstwa danych i pozostałe funkcjonalności

Baza Azure SQL przechowywała dane kont użytkowników, wyniki diagnoz i informacje o wizytach. W pracy przedstawiono encje Users, Appointments i DiagnosisResults oraz tabelę historii migracji Entity Framework. Relacje pozwalały powiązać zapisane wyniki i wizyty z konkretnym użytkownikiem.

Poza głównym wywiadem aplikacja oferowała rejestrację i logowanie, historię zapisanych wyników, kalendarz wizyt, powiadomienia oraz ustawienia konta i motywu. Zalogowany użytkownik mógł przeglądać szczegóły historycznych diagnoz i usuwać je. Kalendarz umożliwiał dodawanie i usuwanie wydarzeń, a powiadomienia informowały o zbliżających się wizytach.

W aplikacji znajdowała się również wyszukiwarka przychodni specjalistycznych. Była to osadzona strona NFZ wyświetlana w kontrolce przeglądarkowej, a nie samodzielnie zaimplementowana integracja z API NFZ.

## Testowanie i wdrożenie historyczne

W ramach pracy przygotowałem instalator z wykorzystaniem Inno Setup Compiler. W rozdziale dotyczącym wdrożenia opisano testy instalacyjne, funkcjonalne i wydajnościowe. Praca raportuje pomyślne testy instalatora na Windows 7, 10 i 11; nie należy jednak traktować tego jako potwierdzenia pełnej kompatybilności aktualnego kodu ze wszystkimi tymi systemami.

Testy funkcjonalne obejmowały sprawdzenie działania aplikacji po instalacji oraz komunikacji z bazą danych i OpenAI API. Do korzystania z usług zewnętrznych wymagane było połączenie z Internetem. W pracy odnotowano również, że pierwsze połączenie z nieużywaną przez dłuższy czas bazą Azure mogło trwać kilkanaście sekund.

W pracy nie przedstawiono klinicznej ewaluacji trafności diagnoz na referencyjnym zbiorze przypadków medycznych ani potwierdzonych metryk takich jak sensitivity, specificity czy accuracy diagnostyczna. Testy aplikacyjne i instalacyjne nie są równoważne walidacji medycznej.

## Ograniczenia i bezpieczeństwo

Na ekranie wyniku znajdował się komunikat informujący, że wygenerowana diagnoza nie jest profesjonalną poradą medyczną i nie należy opierać się wyłącznie na przedstawionych zaleceniach. Wynik powinien zostać zweryfikowany przez lekarza.

W pracy opisano założenia dotyczące ochrony danych, kontroli dostępu i reguł zapory Azure. Nie oznacza to jednak, że przeprowadzono formalny audyt bezpieczeństwa, potwierdzono zgodność z RODO lub wykazano bezpieczeństwo kliniczne systemu.

W pierwotnym repozytorium znajdowały się wpisane w kodzie credentiale. Podczas późniejszego cleanupu usunąłem je z aktualnego kodu i przepisałem publiczną historię Git. Stary klucz OpenAI oraz zasoby Azure zostały wcześniej unieważnione. Aktualny kod odczytuje wymagane wartości ze zmiennych środowiskowych.

Projekt nie jest obecnie utrzymywany jako działająca usługa. Dawna baza i klucz API nie są dostępne, dlatego samo sklonowanie repozytorium nie wystarcza do uruchomienia pełnej funkcjonalności. Dla ewentualnego publicznego wdrożenia należałoby dodatkowo przenieść dostęp do modelu i wrażliwych usług za kontrolowany backend, zamiast dystrybuować wspólny klucz API w aplikacji desktopowej.

## Mój wkład i zdobyte umiejętności

W ramach pracy zaprojektowałem i zaimplementowałem aplikację desktopową, jej interfejs, przepływ wywiadu, integrację z OpenAI API oraz warstwę danych. Przygotowałem również dodatkowe moduły aplikacyjne, instalator i testy opisane w pracy.

Projekt dał mi praktyczne doświadczenie w C#, WPF, MVVM, integracji zewnętrznych API, asynchroniczności, Entity Framework Core, SQL Server i Azure. Pozwolił mi także zrozumieć, jak model językowy może być elementem większego systemu, w którym dane wejściowe są strukturyzowane, odpowiedź przetwarzana, a wynik integrowany z logiką aplikacji.

Z perspektywy dalszego rozwoju AI engineeringu ważnymi wnioskami są konieczność niezależnej ewaluacji jakości LLM, bezpiecznego zarządzania sekretami oraz rozdzielenia prototypu technicznego od systemu przeznaczonego do zastosowań o wysokiej stawce.

## Źródła i zakres dokumentu

Podstawą opracowania jest moja praca inżynierska „Aplikacja wspomagająca wstępną diagnozę medyczną i rekomendację dalszego postępowania z wykorzystaniem elementów sztucznej inteligencji”, w szczególności rozdziały 2–6. Opis aktualnego stanu repozytorium i wyłączenia usług pochodzi z późniejszych, potwierdzonych przeze mnie działań.

Repozytorium projektu: https://github.com/kubaperkowski22/DiagnoseMe

Dokument opisuje historyczny prototyp i jego ograniczenia. Nie zawiera danych pacjentów, rzeczywistych danych logowania, kluczy API ani connection stringów. Nie jest dokumentacją medyczną ani instrukcją korzystania z aplikacji w celu samodzielnego leczenia.
