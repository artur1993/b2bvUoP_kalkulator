# A06 — Wyczyszczenie README

## Cel
Po A01-A05: zaktualizować README, żeby opisywało aplikację po wycięciu (bez PDF, sensitivity, insurance configurator, equalize pension, life_insurance).

## Źródło
- [AUDYT.md §12.1, §12.2, §12.3](../../../AUDYT.md)
- Naturalny follow-up po fazie A.

## Pliki
- [README.md](../../../README.md) — pełna sekcja „Key Features" + sekcje opisujące funkcje wycięte

## Acceptance
- [ ] Brak wzmianek o: PDF eksporcie, sensitivity/tornado chart, insurance configurator (z modułami minimal/standard/premium), equalize pension, `life_insurance` benefit
- [ ] Sekcja „Key Features" odzwierciedla aktualny zakres ([00-spec/0001-zakres.md](../../00-spec/0001-zakres.md))
- [ ] Tytuł: „B2B vs UoP IT Calculator **2026**" (przygotowanie pod B01)
- [ ] Instrukcja instalacji: `pip install -e ".[dev]"` zamiast `pip install -r requirements.txt` (powiązane z [AUDYT.md §12.2](../../../AUDYT.md))
- [ ] Instrukcja venv: `.venv/` zamiast `venv/` (powiązane z [AUDYT.md §12.3](../../../AUDYT.md))

## Test plan
```bash
git grep -i 'pdf\|sensitivity\|insurance configurator\|equalize\|life_insurance' README.md  # pusto
# Manualne: czy README opisuje to, co aplikacja faktycznie robi po fazie A?
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A01, A02, A03, A04, A05.
- **Blokuje**: B01 (zamiana „2025" → „2026" — A06 robi to tytułowo, B01 reszta).
