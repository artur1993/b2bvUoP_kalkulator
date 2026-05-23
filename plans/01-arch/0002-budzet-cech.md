# 0002 — Budżet cech

> Każda cecha jest pozycją w bilansie: koszt utrzymania vs wartość dla użytkownika. Tabela jest sztywna — zmiana wymaga update tego pliku (i PR).

## Decyzje

| Cecha | Decyzja | Faza | Uzasadnienie |
|-------|---------|------|--------------|
| Eksport PDF (podstawowy + zaawansowany) | **TNIJMY** | A01 | Endpoint nie istnieje; deklaracja w README/UI = kłamstwo. Excel wystarczy. |
| Sensitivity chart (tornado) | **TNIJMY** | A02 | 3 sztywnie zakodowane parametry. Wartość marginalna; programista podejmuje decyzję raz. |
| Equalize pension + `pension_calculator.py` | **TNIJMY** | A03 | UI nie pokazuje `pension_details`; model sztywny (30 lat, stała stopa zwrotu). Lepszy link „rozważ IKE/IKZE". |
| Insurance configurator | **TNIJMY** | A04 | Polskie teksty w `insuranceOptions.js`, broken i18n, side-effect na `monthly_business_costs`. `monthly_business_costs` zostaje jako ręczne pole. |
| Opcja `life_insurance` w UoP | **TNIJMY** | A05 | Brak w configu → martwy kod, nie wpływa na wynik. |
| Pole `customBenefits` B2B | ZOSTAJE | — | Realna potrzeba: programista wpisuje swoje benefity. |
| Pole `companyBenefits` B2B (medical, sport, training, equipment) | ZOSTAJE | — | Porównanie z UoP benefitami. |
| Pole `monthly_business_costs` (B2B) | ZOSTAJE | — | Edytowalne ręcznie po A04. |
| Dark mode | ZOSTAJE | D07 (dopasuje sekcje formularza) | Niski koszt, użytkownicy lubią. |
| Share URL (parametry) | ZOSTAJE | D04 (walidacja URL) | „Spójrz na moje liczby." |
| Break-even **liczba** + chart | ZOSTAJE | — | Centralna wartość kalkulatora. |
| Waterfall chart | ZOSTAJE | — | Pokazuje, gdzie znika pensja. |
| Comparison chart (B2B vs UoP) | ZOSTAJE | — | Centralny element wyniku. |
| framer-motion | ZOSTAJE | — | UX, kosmetyka, koszt niski. |
| Eksport Excel | ZOSTAJE, ROZSZERZAMY | F03 + osobny task w fazie F | Dziś tylko 2 liczby; ma być pełen breakdown analogiczny do PDF z poprzedniej iteracji. |
| 4 formy podatku B2B | WSZYSTKIE 4 | B08 | IP Box z polem „udział kwalifikowanego dochodu" + wybór base_form. |
| 3 typy ZUS B2B (`start_relief`, `preferential`, `full`) | ZOSTAJĄ | B09 | `start_relief` dodajemy do UI (był w configu, nie w UI). |
| `small_business` ZUS | USUWAMY z walidatora | B09 | Mały ZUS Plus → [03-backlog/maly-zus-plus.md](../03-backlog/maly-zus-plus.md). |
| Danina solidarnościowa 4% > 1M PLN | DODAJEMY (prosty model) | B12 | Z disclaimerem „wymaga osobnego rozliczenia z PIT-DS". |
| VAT | OUT OF SCOPE | — | Programista IT zwykle nie kombinuje; complikacja > wartość. |
| Koszty pracodawcy UoP | OUT OF SCOPE | — | Programista patrzy z perspektywy własnej kieszeni. |
| Symulacja emerytalna | OUT OF SCOPE (zastępujemy linkiem IKE/IKZE) | A03 | Sztywne założenia bardziej szkodzą niż pomagają. |
| Mały ZUS Plus | BACKLOG | [03-backlog/maly-zus-plus.md](../03-backlog/maly-zus-plus.md) | Złożona logika (dochód z poprzedniego roku, limity czasowe). |
| Tryb side-by-side (2 warianty B2B na raz) | OUT OF SCOPE (na razie) | — | Możliwe rozszerzenie, ale nie w MVP remontu. |
| Auto-detekcja ulgi dla młodych przez wiek | TYLKO UoP | B04 | Frontend pokazuje checkbox tylko dla UoP, włącza automatycznie gdy `age < 26`. |

## Co dodajemy nowego

| Cecha | Powód | Faza |
|-------|-------|------|
| Pole `ip_box_qualified_share` (0-100%) | IP Box wymaga wyodrębnienia kwalifikowanego dochodu | B08 |
| Pole `ip_box_base_form` (flat_tax/tax_scale) | Część niekwalifikowana musi być gdzieś opodatkowana | B08 |
| Disclaimer dla daniny solidarnościowej | Prosty model, pełne rozliczenie wymaga PIT-DS | B12 |
| Metadane w configu (source_url, source_checked_at, valid_from, valid_to) | Audytowalność | B11 |
| Disclaimer dla IP Box („wymaga ewidencji i konsultacji") | IP Box ma rygor formalny | B08 |
| Info-box „rozważ IKE/IKZE" (zamiast pension calculator) | Wartość edukacyjna bez sztywnego modelu | A03 |

## Reguły zmiany budżetu

1. Każda nowa cecha = update tego pliku + nowy task w `02-tasks/`.
2. Każde wycięcie cechy = update tego pliku + task `usun-<slug>` w fazie A.
3. Decyzje „WYMAGA KONSULTACJI" z [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) **nie mogą być zmienione** bez konsultacji księgowej (jawne ograniczenie z konstytucji).
