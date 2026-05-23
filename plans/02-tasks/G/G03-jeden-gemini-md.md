# G03 — Jeden GEMINI.md

## Cel
Usunąć duplikat `.ai/GEMINI.md` (2025), zostawić tylko `GEMINI.md` w root (2026).

## Źródło
[AUDYT.md §10.3](../../../AUDYT.md)

## Pliki
- [.ai/GEMINI.md](../../../.ai/GEMINI.md) — usunąć
- [GEMINI.md](../../../GEMINI.md) — zostaje

## Acceptance
- [ ] `.ai/GEMINI.md` nie istnieje
- [ ] `GEMINI.md` w root jest aktualny (2026)

## Test plan
```bash
test ! -f .ai/GEMINI.md
test -f GEMINI.md
grep -i 2026 GEMINI.md  # potwierdza aktualność
```

## Rollback
`git restore .ai/GEMINI.md`

## Zależności
- Niezależne.
