# G02 — `flask.log` uncached

## Cel
Usunąć `flask.log` z cache git (`.gitignore` go ma, ale plik wciąż śledzony).

## Źródło
[AUDYT.md §10.2](../../../AUDYT.md)

## Pliki
- `flask.log` (w cache git)

## Zmiana

```bash
git rm --cached flask.log
git commit -m "chore(G02): remove flask.log from git cache"
```

**Wymaga potwierdzenia z człowiekiem przed wykonaniem** (operacja destrukcyjna).

## Acceptance
- [ ] `git ls-files | grep flask.log` zwraca pusto
- [ ] Plik fizyczny zostaje (jeśli istnieje lokalnie)

## Test plan
```bash
git ls-files | grep -c flask.log  # 0
```

## Rollback
`git add flask.log -f && git commit`

## Zależności
- **Wymaga ukończenia**: G01 (.gitignore zawiera flask.log)
- Wymaga potwierdzenia człowieka.
