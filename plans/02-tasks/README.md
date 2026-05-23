# 02-tasks/ — pod-plany dla Codexa

Każdy plik = jeden atomowy task = jeden branch = jeden PR.

## Struktura folderów

| Folder | Faza | Co |
|--------|------|-----|
| [A/](A/) | Trim | Usuwanie funkcji bez wartości |
| [B/](B/) | Math fix | Naprawa błędów obliczeniowych |
| [C/](C/) | Security | Walidacja, debug mode, CORS |
| [D/](D/) | Refactor | Architektura, magic numbers, services |
| [E/](E/) | Tooling | Lockfile, linters, CI |
| [F/](F/) | Tests | Walidacja, edge cases, parity |
| [G/](G/) | Hygiene | gitignore, log cache, scripts |

## Szablon pod-planu

Każdy plik w `<faza>/<id>-<slug>.md` MUSI zawierać:

```markdown
# <ID> — <Tytuł>

## Cel
Jedno zdanie: co i dlaczego.

## Źródło
Skąd to znalezisko (link do AUDYT.md / AUDYT_UZUPELNIENIE.md / AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md).

## Pliki
Lista plików do zmiany z linkami:
- [src/calculations.py](../../../src/calculations.py)
- ...

## Acceptance
Lista testowalnych kryteriów (TODO checklist):
- [ ] Test X przechodzi
- [ ] Pole Y w configu = wartość Z
- [ ] UI nie pokazuje przycisku W

## Test plan
Co uruchomić, jakie testy dodać:
- `pytest tests/unit/test_calculations.py::test_<name>`
- `cd src/dashboard && npm test -- ComponentName`

## Rollback
Jak cofnąć (revert PR? feature flag? config rollback?).

## Zależności
- Wymaga ukończenia: [<other-id>](../<phase>/<other-id>-<slug>.md)
- Blokuje: [<other-id>](../<phase>/<other-id>-<slug>.md)
```

## Playwright MCP — weryfikacja frontendowa

Zadania dotyczące frontendu mają sekcję **Playwright MCP Verification**. Używaj dostępnych narzędzi MCP bezpośrednio w kontekście Codexa (bez `npx playwright test`):

| Narzędzie | Użycie |
|-----------|--------|
| `playwright_navigate(url=...)` | Otwórz stronę |
| `playwright_screenshot(name=...)` | Zrób screenshot (potwierdza stan wizualny) |
| `playwright_get_visible_text(selector=...)` | Pobierz widoczny tekst elementu |
| `playwright_evaluate(script=...)` | Uruchom JS w przeglądarce (sprawdzenie DOM, styles) |
| `playwright_fill(selector=..., value=...)` | Wypełnij pole input |
| `playwright_click(selector=...)` | Kliknij element |
| `playwright_select_option(selector=..., value=...)` | Wybierz opcję w `<select>` |

**Ważne**: uruchom `./run_app.sh` przed weryfikacją Playwright MCP. Frontend dostępny na `http://localhost:5173`, backend na `http://localhost:5001`.

## Konwencje commitów

- `feat(<id>): <opis>` — nowa funkcjonalność
- `fix(<id>): <opis>` — naprawa błędu
- `refactor(<id>): <opis>` — bez zmiany zachowania
- `chore(<id>): <opis>` — tooling, repo
- `test(<id>): <opis>` — same testy
- `docs(<id>): <opis>` — same docs

Przykład: `fix(B04): remove PIT-0 from B2B calculation path`
