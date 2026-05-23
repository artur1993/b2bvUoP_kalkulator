# T00 — Konstytucja projektu

## Cel
Utworzyć `constitution.md` w korzeniu repo — sztywne reguły dla każdego kontrybutora (człowieka lub AI).

## Źródło
[MASTER.md](../MASTER.md) — sekcja „Mapowanie SDD ↔ pliki".

## Status
**DONE** — [constitution.md](../../constitution.md) istnieje, utworzony w pierwszym kroku planowania.

## Pliki
- [constitution.md](../../constitution.md) — utworzony

## Acceptance
- [x] Plik `constitution.md` w korzeniu repo
- [x] Zawiera sekcje: Stack, Reguły kodu (backend, frontend, testy, CI), Reguły dla automatyzacji, Audyt config, Hierarchia decyzji
- [x] Konwencja [Conventional Commits](https://www.conventionalcommits.org/) udokumentowana

## Test plan
- Manualne: czy każde inne narzędzie (Codex, recenzent człowiek) może powołać się na sekcję konstytucji w PR-ze?

## Rollback
- `git rm constitution.md` + revert.

## Zależności
- Brak. To pierwszy artefakt SDD.
- **Blokuje**: wszystkie pozostałe taski (każdy odwołuje się do konstytucji).
