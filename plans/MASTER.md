# MASTER PLAN — Remont kalkulatora B2B vs UoP 2026

> Kanoniczny meta-plan w repo. Codex i ludzie pracują z tym plikiem. Plan trzymany lokalnie w `~/.claude/plans/` jest jego kopią roboczą.

## Context

Trzy uzupełniające się audyty (`AUDYT.md`, `AUDYT_UZUPELNIENIE.md`, `AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md`) odsłoniły dwie klasy problemów:

1. **Aplikacja liczy źle**. Stawki zdrowotne ryczałtu na 2024 zamiast 2026 (`432.54` zamiast `498.35`), PIT-0 dla B2B (sprzeczne z art. 21 ust. 1 pkt 148 PIT), PPK modelowane jako 2% benefit (myli wpłatę pracownika z pracodawcy), podwójne liczenie dni wolnych w UoP, IP Box na całej podstawie bez kwalifikowanego dochodu, ZeroDivisionError w `author_costs`.
2. **Aplikacja jest zbyt rozbudowana**. Deklarowane funkcjonalności (PDF) nie istnieją; insurance configurator ma polskie teksty wbite w kod + side-effect na koszty; pension calculator sztywny; sensitivity chart z 3 hardkodowanymi parametrami.

**Cel remontu**: prosty, rzetelny kalkulator B2B vs UoP 2026.

## Decyzje (rozstrzygnięte)

- **Tnijmy**: PDF export, sensitivity chart, equalize pension + `pension_calculator.py`, insurance configurator
- **Zostaje**: dark mode, share URL, break-even chart, waterfall chart, comparison chart, framer-motion
- **Formy podatku B2B**: wszystkie 4 (lump_sum_it, flat_tax, tax_scale, ip_box) — IP Box z polem „udział kwalifikowanego dochodu"
- **Stawki 2026**: [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) = ground truth
- **Danina solidarnościowa 4%**: implementujemy prosty model z disclaimerem (B12)
- **IP Box base form**: wybór użytkownika (B08)
- **Reorganizacja katalogów** `src/` → `backend/` + `frontend/`: w fazie D (D08)
- **`small_business` ZUS**: usuwamy z walidatora (B09), Mały ZUS Plus → [backlog](03-backlog/maly-zus-plus.md)

## Cztery zasady (lean & correct)

1. **Correctness > features**. Zero znanych błędów obliczeniowych po fazie B.
2. **Lean over rich**. Tnijmy każdą funkcję bez obrony „programista nie podejmie decyzji bez tego".
3. **Truthful UI**. Backend liczy → UI pokazuje. Backend nie liczy → UI nie obiecuje.
4. **Auditable config**. Każda kwota ma `source_url`, `source_checked_at`, `valid_from`, `valid_to`.

## Mapowanie SDD ↔ pliki

| Faza SDD | Lokalizacja | Co |
|----------|-------------|-----|
| Constitution | [/constitution.md](../constitution.md) | Sztywne reguły |
| Specify | [plans/00-spec/](00-spec/) | Cele, persona, scope |
| Plan | [plans/01-arch/](01-arch/) | Architektura + budżet cech |
| Tasks | [plans/02-tasks/](02-tasks/) | Atomowe pod-plany |
| Backlog | [plans/03-backlog/](03-backlog/) | Co odkładamy |

**Reguła git**: 1 pod-plan = 1 branch `feature/<id>-<slug>` = 1 PR do `master`. Plan-file = opis PR. `progress` w tej samej PR.

## Kolejność wykonania (przepływ dla Codexa)

```
1. T00          Konstytucja istnieje (DONE — patrz /constitution.md)
2. 00-spec/     Specify (DONE — patrz plans/00-spec/)
3. 01-arch/     Plan (DONE — patrz plans/01-arch/)
4. 02-tasks/A/  Faza A (trim) — równolegle PR-y
5. checkpoint   E2E + integration tests pass
6. 02-tasks/B/  Faza B (math fix) — sekwencyjnie (config conflicts)
7. 02-tasks/C/  Faza C (security) — równolegle z B
8. checkpoint   3 przypadki użycia z 00-spec/0002 przechodzą
9. D, E, F, G   równolegle, w miarę możliwości
```

Reguła: nie zaczynamy fazy następnej, jeśli regression z poprzedniej jest red.

## Lista faz i tasków

### Faza A — Trim
| ID | Slug |
|----|------|
| [A01](02-tasks/A/A01-usun-pdf-export.md) | Usuń eksport PDF |
| [A02](02-tasks/A/A02-usun-sensitivity-chart.md) | Usuń sensitivity chart |
| [A03](02-tasks/A/A03-usun-equalize-pension.md) | Usuń equalize pension + pension_calculator.py |
| [A04](02-tasks/A/A04-usun-insurance-configurator.md) | Usuń insurance configurator |
| [A05](02-tasks/A/A05-usun-life-insurance-benefit.md) | Usuń life_insurance benefit |
| [A06](02-tasks/A/A06-wyczyszczenie-readme.md) | Wyczyść README z usuniętych cech |

### Faza B — Fix critical math
| ID | Slug |
|----|------|
| [B01](02-tasks/B/B01-2026-w-ui-i-readme.md) | „2025" → „2026" w UI i README |
| [B02](02-tasks/B/B02-stawki-zdrowotne-ryczalt-2026.md) | Stawki zdrowotne ryczałtu 2026 |
| [B03](02-tasks/B/B03-minimalna-zdrowotna-2026.md) | Minimalna zdrowotna styczeń vs luty 2026 |
| [B04](02-tasks/B/B04-usun-pit-0-dla-b2b.md) | Usuń PIT-0 dla B2B |
| [B05](02-tasks/B/B05-usun-podwojne-dni-wolne-uop.md) | Usuń podwójne dni wolne w UoP |
| [B06](02-tasks/B/B06-naprawa-ppk.md) | Naprawa PPK (employee vs employer) |
| [B07](02-tasks/B/B07-zerodiv-author-costs.md) | Uproszczenie wzoru kosztów autorskich |
| [B08](02-tasks/B/B08-ip-box-z-kwalifikowanym-dochodem.md) | IP Box z polem kwalifikowanego dochodu |
| [B09](02-tasks/B/B09-small-business-z-walidatora.md) | Usuń `small_business` z walidatora |
| [B10](02-tasks/B/B10-walidacja-gorne-granice.md) | Górne granice w Pydantic |
| [B11](02-tasks/B/B11-metadane-w-configu.md) | Metadane source_url w configu |
| [B12](02-tasks/B/B12-danina-solidarnosciowa.md) | Danina solidarnościowa 4% > 1M PLN |

### Faza C — Security & validation
| ID | Slug |
|----|------|
| [C01](02-tasks/C/C01-debug-mode-z-env.md) | Debug mode z ENV |
| [C02](02-tasks/C/C02-pydantic-na-wszystkich-endpointach.md) | Pydantic na wszystkich endpointach |
| [C03](02-tasks/C/C03-cors-whitelist.md) | CORS whitelist |
| [C04](02-tasks/C/C04-error-handler-bez-tracebackow.md) | Error handler bez tracebacków |

### Faza D — Architecture refactor
| ID | Slug |
|----|------|
| [D01](02-tasks/D/D01-rozbicie-god-function-b2b.md) | Rozbicie god function `calculate_b2b_results` |
| [D02](02-tasks/D/D02-magic-numbers-do-configu.md) | Magic numbers do configu |
| [D03](02-tasks/D/D03-services-layer-backend.md) | Services layer w backendzie |
| [D04](02-tasks/D/D04-reducer-na-froncie.md) | useReducer na froncie |
| [D05](02-tasks/D/D05-i18n-replace-w-jsx.md) | Usuń `.replace()` w JSX (i18n-safe) |
| [D06](02-tasks/D/D06-calculating-button-i18n.md) | „Calculating..." → t() |
| [D07](02-tasks/D/D07-dark-mode-formularza.md) | Dark mode w sekcjach formularza |
| [D08](02-tasks/D/D08-reorganizacja-katalogow.md) | `src/` → `backend/` + `frontend/` |

### Faza E — Tooling & CI
| ID | Slug |
|----|------|
| [E01](02-tasks/E/E01-version-pinning-i-lockfile.md) | Version pinning + lockfile |
| [E02](02-tasks/E/E02-ruff-mypy.md) | Ruff + mypy |
| [E03](02-tasks/E/E03-eslint-flat-config.md) | ESLint flat config |
| [E04](02-tasks/E/E04-github-actions-ci.md) | GitHub Actions CI |
| [E05](02-tasks/E/E05-pre-commit-hooks.md) | Pre-commit hooks |

### Faza F — Tests
| ID | Slug |
|----|------|
| [F01](02-tasks/F/F01-testy-validation.md) | Testy validation.py |
| [F02](02-tasks/F/F02-testy-edge-cases.md) | Testy edge cases |
| [F03](02-tasks/F/F03-testy-z-konkretnymi-liczbami.md) | Testy z konkretnymi liczbami |
| [F04](02-tasks/F/F04-i18n-parity-test.md) | i18n parity test |
| [F05](02-tasks/F/F05-e2e-smoke.md) | E2E smoke test |
| [F06](02-tasks/F/F06-axe-a11y.md) | axe-core a11y testy |

### Faza G — Repo hygiene
| ID | Slug |
|----|------|
| [G01](02-tasks/G/G01-gitignore.md) | Aktualizacja .gitignore |
| [G02](02-tasks/G/G02-flask-log-uncached.md) | flask.log uncached |
| [G03](02-tasks/G/G03-jeden-gemini-md.md) | Jeden GEMINI.md |
| [G04](02-tasks/G/G04-analiza-md-do-docs.md) | analiza.md → docs/ |
| [G05](02-tasks/G/G05-run-stop-app-sh-safe.md) | run/stop_app.sh: set -euo pipefail + PID file |

## Acceptance dla całego remontu (regresja końcowa)

Remont uważamy za zakończony, gdy:

1. Trzy przypadki użycia z [00-spec/0002-przypadki-uzycia.md](00-spec/0002-przypadki-uzycia.md) zwracają netto ±50 PLN.
2. Zero deklaracji w README/UI bez pokrycia w kodzie.
3. CI zielony: pytest, vitest, eslint, ruff, mypy, playwright smoke.
4. `youth_relief` dla B2B niemożliwy (test ujemny).
5. Stawki zdrowotne ryczałtu w configu = `498.35` / `830.58` / `1495.04`.
6. PPK rozdzielone na `_employee_rate` i `_employer_rate`.
7. Brak `app.debug=True` w produkcji.
8. Wszystkie 4 endpointy mają walidację Pydantic.
9. i18n parity test zielony.
10. Audit log w configu: każda kwota ma `source_url` i `source_checked_at`.

## Pliki krytyczne (referencje)

**Audyty** (źródła znalezisk):
- [AUDYT.md](../AUDYT.md)
- [AUDYT_UZUPELNIENIE.md](../AUDYT_UZUPELNIENIE.md)
- [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md)

**Konwencje**:
- [constitution.md](../constitution.md)
- [sdd_summary.md](../sdd_summary.md)
- [CLAUDE.md](../CLAUDE.md)

**Backend** (główni „pacjenci"):
- [src/app.py](../src/app.py)
- [src/calculations.py](../src/calculations.py)
- [src/validation.py](../src/validation.py)
- [src/config.py](../src/config.py)
- [src/pension_calculator.py](../src/pension_calculator.py) — **do usunięcia** w A03
- [dane_wejsciowe_kalkulator.json](../dane_wejsciowe_kalkulator.json)

**Frontend**:
- [src/dashboard/src/App.jsx](../src/dashboard/src/App.jsx)
- [src/dashboard/src/components/CalculatorForm.jsx](../src/dashboard/src/components/CalculatorForm.jsx)
- [src/dashboard/src/components/ResultsDisplay.jsx](../src/dashboard/src/components/ResultsDisplay.jsx)
- [src/dashboard/src/data/insuranceOptions.js](../src/dashboard/src/data/insuranceOptions.js) — **do usunięcia** w A04
- [src/dashboard/src/locales/en/translation.json](../src/dashboard/src/locales/en/translation.json)
- [src/dashboard/src/locales/pl/translation.json](../src/dashboard/src/locales/pl/translation.json)
