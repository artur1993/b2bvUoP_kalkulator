# D07 — Dark mode w sekcjach formularza

## Cel
Dodać `dark:` modifiery do sekcji formularza (`bg-white`, `bg-gray-50`) — w dark mode pozostają jasne.

## Źródło
[AUDYT.md §5.8](../../../AUDYT.md) — ŚREDNIE

## Pliki
- [src/dashboard/src/components/CalculatorForm.jsx:35, 66, 79, 314](../../../src/dashboard/src/components/CalculatorForm.jsx#L35)

## Zmiana

Każdy `bg-white` → `bg-white dark:bg-gray-800`.
Każdy `bg-gray-50` → `bg-gray-50 dark:bg-gray-900`.
Każdy `text-gray-800` → `text-gray-800 dark:text-gray-100`.
Każdy `text-gray-700` → `text-gray-700 dark:text-gray-300`.

## Acceptance
- [x] Wszystkie sekcje formularza wyglądają spójnie w dark mode
- [x] E2E test `darkmode.spec.js` (F05) zielony

## Test plan
```bash
./run_app.sh  # toggle dark mode → sprawdź formularz
cd src/dashboard && npm test -- --run
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_screenshot(name="D07-light-mode")

# Aktywuj dark mode (kliknij toggle):
playwright_click(selector="[data-testid='dark-mode-toggle'],[aria-label*='dark'],[class*='theme-toggle']")
playwright_screenshot(name="D07-dark-mode")

# Sprawdź: sekcje formularza mają ciemne tło (nie białe):
playwright_evaluate(script="window.getComputedStyle(document.querySelector('[class*=bg-white],[class*=bg-gray-50]')).backgroundColor")
# Oczekiwany wynik: ciemny kolor (nie rgb(255, 255, 255))

# Sprawdź spójność — porównaj screenshot light vs dark (wizualnie):
# Kluczowe: sekcje B2B i UoP mają ciemne tło w dark mode
playwright_evaluate(script="[...document.querySelectorAll('section,[class*=card],[class*=panel]')].map(el => ({class: el.className, bg: window.getComputedStyle(el).backgroundColor}))")
# Żaden element nie powinien mieć bg: rgb(255, 255, 255) w dark mode
```

## Rollback
Revert PR.

## Zależności
- Niezależne.
