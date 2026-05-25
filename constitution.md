# Konstytucja projektu — Kalkulator B2B vs UoP 2026

> Zbiór sztywnych reguł, do których stosuje się każdy kontrybutor (człowiek lub AI). Zmiana konstytucji wymaga osobnego PR-u oznaczonego `chore(constitution):`.

## Cel produktu

Prosty, **rzetelny** kalkulator porównujący dochód netto B2B vs UoP dla programisty IT w Polsce, według prawa **2026**. Bez bajerów, z prawdziwą wartością.

Persona: programista IT, 3–10 lat doświadczenia, rozważa B2B lub etat. Sukces: użytkownik kończy ścieżkę w <2 min, widzi liczbę netto i punkt break-even.

## Stack technologiczny (zamknięty)

- **Backend**: Python 3.10+, Flask, Pydantic 2.x
- **Frontend**: React 18, Vite, Tailwind CSS, Chart.js
- **i18n**: i18next (en, pl)
- **Testy**: pytest + pytest-cov (backend), Vitest + React Testing Library (frontend), Playwright (E2E)
- **Linting**: ruff + mypy (backend), ESLint flat config + Prettier (frontend)
- **CI**: GitHub Actions

Zmiana stacku wymaga jawnej zmiany konstytucji.

## Reguły kodu

### Backend
- Każdy endpoint przyjmujący JSON ma walidację Pydantic. Bez wyjątków.
- Funkcje obliczeniowe typują parametry jako modele Pydantic, nie `Dict[str, Any]`.
- Stałe regulacyjne (stawki, progi, limity) **WYŁĄCZNIE** w `data/dane_wejsciowe_kalkulator.json` z metadanymi: `source_url`, `source_checked_at` (ISO date), `valid_from`, `valid_to`.
- Linting: `ruff` (domyślna konfiguracja + isort), `mypy --strict` dla `backend/`.
- **Brak** `app.debug=True` w produkcji. Tryb debug wyłącznie przez ENV `FLASK_ENV=development`.
- Error handlery zwracają **stałą** wiadomość. Szczegóły wyłącznie do `app.logger.exception(...)`.

### Frontend
- Każdy tekst pokazywany użytkownikowi MUSI iść przez `t()`.
- **Brak** `.replace()` na wynikach `t()` w JSX.
- Logika biznesowa w `services/` lub hookach, nie w komponentach.
- Linting: ESLint flat config + Prettier; CI fails on warnings.

### Testy
- Backend: minimum 80% pokrycia dla `backend/calculations.py` i `backend/validation.py`.
- Frontend: jeden render-test per komponent.
- E2E: smoke test całkowitego flow (formularz → wynik) MUSI być zielony.
- Każda zmiana w `calculations.py` = nowy test z **konkretnymi liczbami** (nie samymi kluczami).

### CI
- GitHub Actions: pytest, vitest, npm run lint, ruff check, mypy, playwright smoke.
- PR nie merguje się, jeśli CI red.
- Brak `--no-verify`, brak `--no-gpg-sign`.

## Reguły dla automatyzacji (Codex i inne narzędzia AI)

1. Codex **nie zmienia** stawek/progów w configu bez wpisu w [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) ze statusem `OK` lub `BŁĄD`.
2. Pozycje `WYMAGA KONSULTACJI` w audycie logiki biznesowej są **zablokowane** — wymagają osobnej decyzji człowieka.
3. Każdy task = jeden PR. Bez bundlowania.
4. Commit message: konwencja [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
5. Identyfikatory w kodzie po **angielsku**. Polskie komentarze dozwolone.
6. Każdy pod-plan w `plans/02-tasks/<faza>/<id>-<slug>.md` ma sekcje: Cel, Pliki, Acceptance, Test plan, Rollback.
7. Plan-file jest opisem PR. `progress` aktualizowany w tej samej PR-ce co kod.

## Audyt config

Każda wartość regulacyjna w `data/dane_wejsciowe_kalkulator.json` ma cztery pola metadanych:

```json
{
  "minimum_wage": {
    "value": 4806.00,
    "source_url": "https://www.gov.pl/web/rodzina/minimalne-wynagrodzenie-2026",
    "source_checked_at": "2026-05-23",
    "valid_from": "2026-01-01",
    "valid_to": "2026-12-31"
  }
}
```

Wartości bez metadanych = niezgodność z konstytucją.

## Hierarchia decyzji

1. **Konstytucja** (ten plik) — sztywne reguły
2. **Master plan** ([plans/MASTER.md](plans/MASTER.md)) — kierunek remontu
3. **Specify** ([plans/00-spec/](plans/00-spec/)) — co aplikacja robi
4. **Architecture** ([plans/01-arch/](plans/01-arch/)) — jak jest zbudowana
5. **Tasks** ([plans/02-tasks/](plans/02-tasks/)) — konkretne kroki

Konflikt? Wyższy priorytet wygrywa. Konstytucja zawsze pierwsza.
