# plans/ — SDD workflow

Struktura katalogu zgodna z metodyką Spec-Driven Development ([sdd_summary.md](../sdd_summary.md)).

## Nawigacja

| Folder | Faza SDD | Co tam jest |
|--------|----------|-------------|
| [MASTER.md](MASTER.md) | — | Meta-plan: kierunek remontu + lista wszystkich tasków |
| [00-spec/](00-spec/) | Specify | Cele, persona, scope (in/out), przypadki użycia z fixturkami |
| [01-arch/](01-arch/) | Plan | Architektura docelowa, budżet cech (co tnijmy/zostaje) |
| [02-tasks/](02-tasks/) | Tasks | Atomowe pod-plany; każdy = 1 PR |
| [03-backlog/](03-backlog/) | — | Odłożone na później (Mały ZUS Plus, etc.) |

Konstytucja projektu jest w korzeniu: [../constitution.md](../constitution.md).

## Workflow dla Codexa

1. **Read** [MASTER.md](MASTER.md), żeby zobaczyć kontekst i kolejność faz.
2. **Read** [constitution.md](../constitution.md) — sztywne reguły.
3. **Pick task** z `02-tasks/<faza>/` zgodnie z kolejnością z MASTER.
4. **Branch**: `feature/<id>-<slug>` (np. `feature/A01-usun-pdf-export`).
5. **Implement** zgodnie z pod-planem.
6. **Run tests** z sekcji „Test plan" w pod-planie.
7. **PR**: tytuł = `<typ>(<id>): <opis>`, opis = treść pod-planu + sekcja „Progress" z TODO checklisty.
8. **Merge** po zielonym CI + review człowieka.

## Workflow dla człowieka

- Zatwierdzasz pod-plan przed startem implementacji (review pliku `.md`).
- Reviewujesz PR.
- Aktualizujesz pod-plan jeśli zakres się zmienia w trakcie.

## Konwencje

- ID taska: `<faza><nr>` (np. `A01`, `B07`).
- Slug: kebab-case, polski (np. `usun-pdf-export`).
- Każdy plik taska ma sekcje: **Cel**, **Pliki**, **Acceptance**, **Test plan**, **Rollback**.
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, etc.).
