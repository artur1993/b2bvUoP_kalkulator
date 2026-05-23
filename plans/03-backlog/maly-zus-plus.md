# Backlog: Mały ZUS Plus

## Status
**ODŁOŻONE NA PÓŹNIEJ** (decyzja 2026-05-23).

W fazie B usuwamy `small_business` z walidatora (task B09). Mały ZUS Plus jako pełna funkcjonalność wraca jako osobny projekt po zakończeniu remontu.

## Czym jest Mały ZUS Plus

Preferencja dla mikroprzedsiębiorców z rocznym przychodem do ~120 000 PLN. Pozwala płacić mniejszy ZUS przez **36 miesięcy** po wykorzystaniu preferencyjnego ZUS-u.

- Podstawa składek społecznych = średni miesięczny dochód z poprzedniego roku × 30% × 60%
- Wymaga: prowadzenia działalności ≥60 dni w poprzednim roku
- Wyklucza: PKD pewnych branż (m.in. doradztwo)
- Ograniczenie czasowe: 36 mies. w ciągu ostatnich 60 mies.

Źródła:
- ZUS: https://www.zus.pl/-/maly-zus-plus
- Ustawa: art. 18c ustawy z 13 października 1998 r. o systemie ubezpieczeń społecznych

## Zakres przyszłego projektu (gdy ruszymy)

### Backend
- Nowa gałąź `zus_2026.small_business_plus` w configu:
  - Pole wejściowe: `average_monthly_income_previous_year` w `B2BDataModel`
  - Walidator: pole wymagane gdy `zus_type='small_business_plus'`, `le=120000/12`
  - Logika: `base = average_monthly_income * 0.3 * 0.6`, składki = `base × stawki%`
- Limit czasowy: pole `months_used_so_far` (0–35), walidacja
- Walidator: pattern `^(start_relief|preferential|small_business_plus|full)$`

### Frontend
- Dropdown ZUS rozszerzony o „Mały ZUS Plus"
- Conditional rendering: gdy wybrany Mały ZUS Plus → pojawia się pole „Średni miesięczny dochód z poprzedniego roku"
- Tooltip: warunki kwalifikacji + link do ZUS
- Alert: „Mały ZUS Plus dostępny przez 36 miesięcy. Po tym okresie konieczne przejście na pełny ZUS."

### Tests
- Test akceptacji: dochód 5000/mies. (60k roczne) → składki Mały ZUS Plus < pełny ZUS, > preferencyjny
- Test krawędziowy: dochód > 120k/rok → walidator odrzuca
- Test krawędziowy: `months_used_so_far = 36` → walidator odrzuca

### Dokumentacja
- Aktualizacja [00-spec/0001-zakres.md](../00-spec/0001-zakres.md): przenieść Mały ZUS Plus z OUT OF SCOPE do IN SCOPE
- Nowy task `<faza>NN-maly-zus-plus.md` w `02-tasks/`

## Kiedy ruszyć

Po zakończeniu pełnego remontu (wszystkie fazy A-G zielone) i przynajmniej miesiącu stabilizacji.

## Decyzja o realizacji
Człowiek (artur@) decyduje na podstawie liczby pytań/feedbacku użytkowników.
