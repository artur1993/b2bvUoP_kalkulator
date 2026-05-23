# 0001 — Zakres produktu (Specify)

## Persona

**Programista IT, 3–10 lat doświadczenia.** Pracuje na etacie (UoP) lub rozważa przejście na B2B. Pracuje w Polsce, zna podstawy podatków, ale nie księgowy. Chce porównać liczby, nie czytać ustawy.

## Job to be done

Trzy główne zadania, w kolejności ważności:

1. **„Chcę wiedzieć, ile dostanę na rękę na B2B vs UoP dla mojej stawki, na 2026 rok."**
   - Wprowadza pensję UoP i fakturę B2B, wybiera formę podatku/ZUS, klika Oblicz, widzi netto.
2. **„Chcę zobaczyć, ile musiałbym fakturować, żeby zarobić tyle samo netto, co na etacie."**
   - Tryb break-even: wpisuje UoP, dostaje minimalną fakturę B2B.
3. **„Chcę porównać dwa warianty B2B (np. ryczałt vs liniowy) dla tej samej stawki."**
   - Tryb side-by-side: dwa zestawy parametrów B2B → dwa wyniki.

## Sukces

- Użytkownik kończy ścieżkę 1 w **<2 minutach** od wejścia.
- Widzi **konkretną liczbę netto** rocznego/miesięcznego.
- Widzi **break-even invoice** (jeśli wybrał taki tryb).
- Widzi **breakdown**: ile z faktury idzie na ZUS, podatek, składkę zdrowotną, ile zostaje.

## In scope

- 4 formy podatku B2B: ryczałt 12% IT, liniowy 19%, skala 12%/32%, IP Box 5%.
- 3 typy ZUS B2B: start_relief, preferential, full (Mały ZUS Plus — backlog).
- UoP: standardowe i podwyższone KUP, koszty autorskie 50%, ulga dla młodych (do 26 r.ż.).
- 2026 rok podatkowy.
- Język: polski + angielski.
- Eksport: Excel (pełny breakdown).
- Wykres: comparison (B2B vs UoP), waterfall (jak znika pensja), break-even chart.

## Out of scope (jawnie)

| Co | Dlaczego |
|----|----------|
| VAT (faktury netto/brutto, VAT należny/naliczony) | Mały programista B2B w IT zwykle nie kombinuje z VAT-em. Zakres = porównanie netto „do kieszeni". |
| Koszty pracodawcy w UoP | Programista patrzy z perspektywy własnej kieszeni, nie firmy. |
| Symulacja emerytalna | Sztywne założenia (30 lat, stała stopa) bardziej szkodzą niż pomagają. Zamiast tego: krótka informacja „rozważ IKE/IKZE" z linkiem do ZUS. |
| Pełne porównanie pakietów ubezpieczeń | Insurance configurator z poprzedniej iteracji był martwym kodem z polskimi tekstami. Zamiast tego: prosta kwota „dodatkowe koszty firmowe (PLN/mies.)". |
| Sensitivity / what-if analysis | Programista podejmuje decyzję raz na lata. Break-even już mu to mówi. |
| Mały ZUS Plus | Złożona logika (podstawa z dochodu z poprzedniego roku, limity czasowe). Backlog. |
| Eksport PDF | Niedokończona migracja. Excel wystarczy. |
| Tax optimization advisor | Nie udajemy księgowego. „Zobacz wyniki, porozmawiaj z księgowym." |
| Przejścia w trakcie roku (np. B2B od września) | Niska wartość, duża komplikacja. |

## User journey (happy path)

```
1. Wejście na stronę → widzi formularz z 2 kolumnami (B2B | UoP)
2. (Opcjonalnie) Wybiera tryb porównania (UoP → B2B lub odwrotnie)
3. Wpisuje wiek (jedno pole, używane do PIT-0 dla UoP)
4. Wpisuje pensję UoP brutto + wybiera KUP
5. Wpisuje fakturę B2B + wybiera formę podatku + ZUS
6. (Opcjonalnie) Dodaje koszty firmowe, dni urlopu, benefity
7. Klika „Oblicz"
8. Widzi 3 sekcje:
   a) Porównanie netto (B2B vs UoP, rocznie/miesięcznie)
   b) Break-even (ile musiałby fakturować = pensji)
   c) Wykresy (comparison, waterfall, break-even chart)
9. (Opcjonalnie) Eksportuje Excel albo dzieli URL-em
```

Dark mode jako opcja w nagłówku. Share URL przez parametry w pasku adresu.

## Sukces mierzalny (dla testów akceptacyjnych)

Każdy z 3 przypadków użycia ([0002-przypadki-uzycia.md](0002-przypadki-uzycia.md)) ma zdefiniowane oczekiwane netto z tolerancją ±50 PLN/rok. Testy integracyjne w `tests/integration/test_real_scenarios.py` muszą przechodzić.
