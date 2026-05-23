# G04 — `analiza.md` → `docs/`

## Cel
Przenieść `analiza.md` (5,8 KB polski raport bez kontekstu) do `docs/` lub usunąć.

## Źródło
[AUDYT.md §10.5](../../../AUDYT.md)

## Pliki
- [analiza.md](../../../analiza.md)

## Zmiana

Opcja A (przenosimy):
```bash
mkdir -p docs
git mv analiza.md docs/analiza-2025.md
```

Opcja B (usuwamy, jeśli treść nieaktualna):
```bash
git rm analiza.md
```

**Wymaga decyzji człowieka** przed wykonaniem (czy treść jest aktualna).

## Acceptance
- [ ] `analiza.md` nie istnieje w root
- [ ] Albo `docs/analiza-2025.md` istnieje, albo plik został usunięty

## Test plan
- Manualne: czy plik nadal odwołuje się z czegokolwiek?

## Rollback
`git restore analiza.md`

## Zależności
- Niezależne. Wymaga decyzji człowieka.
