# Podsumowanie: Spec-Driven Development (SDD)

Na podstawie artykułu: [Spec Driven Development (SDD) - A initial review](https://dev.to/danielsogl/spec-driven-development-sdd-a-initial-review-2llp) autorstwa Daniela Sogla.

## Czym jest SDD?
Spec-Driven Development (SDD) to ustrukturyzowana metodologia tworzenia oprogramowania zaprojektowana z myślą o efektywnej współpracy z agentami AI (np. Cursor, GitHub Copilot). Zamiast bezpośredniego pisania kodu ("Vibe Coding"), programista skupia się na precyzyjnym definiowaniu specyfikacji i planów w języku naturalnym, które AI następnie wdraża.

## Cztery Fazy SDD
1.  **Specify (Specyfikacja):** Definiowanie celów biznesowych i ścieżek użytkownika. Skupienie na *co* system ma robić, a nie *jak*.
2.  **Plan (Planowanie):** Określenie architektury, technologii i standardów. AI generuje techniczny blueprint projektu.
3.  **Tasks (Zadania):** Rozbicie planu na małe, atomowe i testowalne kroki. To klucz do uniknięcia halucynacji AI w dużych plikach.
4.  **Implement (Implementacja):** AI wykonuje konkretne zadania, a programista weryfikuje poprawność (Verify) i dba o jakość.

## Kluczowe Koncepcje
- **Konstytucja Projektu (`constitution.md`):** Zbiór sztywnych reguł (standardy kodowania, biblioteki), które ograniczają swobodę AI i zapewniają spójność bazy kodu.
- **Koniec "Vibe Coding":** SDD jest profesjonalną odpowiedzią na chaotyczne promptowanie. Ma na celu dostarczanie kodu jakości produkcyjnej, a nie tylko działających prototypów.
- **Programista jako Architekt/Weryfikator:** Rola przesuwa się z pisania linii kodu na projektowanie systemów i krytyczną ocenę pracy agenta AI.

## SDD vs Inne Metody
- **SDD vs TDD:** SDD wymusza testowalność zadań w izolacji, podobnie jak TDD, ale robi to na poziomie specyfikacji intencji przed implementacją.
- **SDD vs Agile:** SDD wymusza ekstremalną precyzję w User Stories. Jeśli specyfikacja jest niejasna, AI nie dostarczy poprawnego wyniku.

## Wnioski dla projektu "Cyfrowy Dialog"
Metodologia SDD idealnie pasuje do planowanego MVP:
- Mamy już "Konstytucję" w postaci `GEMINI.md`.
- Mamy szczegółowy plan w `plan_lokalne_mvp_weryfikacji_grantow.md` (Faza Specify i Plan).
- Podejście warstwowe (`inventory -> classify -> extract`) to faza zadań (Tasks), którą AI może realizować precyzyjnie bez ryzyka błędów w logice biznesowej.

## Automatyzacja fazy Implement: ralph-loop

Po zatwierdzeniu planu z mierzalnymi kryteriami akceptacji fazę Implement można przeprowadzić w pętli `/ralph-loop` (plugin Claude Code). Reguły, szablony promptu i checklisty są w [plans/workflow_ralph_loop.md](workflow_ralph_loop.md). Ralph-loop nigdy nie zastępuje fazy Plan ani decyzji człowieka po pętli.

Mapping SDD ↔ git: 1 zatwierdzony plan = 1 branch `feature/<id>` = 1 PR do `develop`. Plan-file staje się opisem PR. `progress` aktualizujemy w tej samej PR-ce, w której robimy kod.
