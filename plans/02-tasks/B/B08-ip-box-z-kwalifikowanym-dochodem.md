# B08 — IP Box z polem kwalifikowanego dochodu

## Cel
Zastąpić uproszczenie „cała podstawa B2B × 5%" modelem realistycznym: tylko `ip_box_qualified_share` × podstawy idzie po 5%, reszta — po stawce wybranej w `ip_box_base_form` (`flat_tax` lub `tax_scale`).

## Źródło
- [AUDYT.md §3.7](../../../AUDYT.md) — WYSOKIE
- [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) — sekcja „IP Box", **BŁĄD**

Źródło: https://www.podatki.gov.pl/poradniki-i-informatory/ip-box-rozliczenie-dochodow-z-kwalifikowanych-praw-wlasnosci-intelektualnej-pit/

## Pliki
- [src/validation.py:11-25](../../../src/validation.py#L11) — `B2BDataModel` — dodać pola
- [src/calculations.py:101-102](../../../src/calculations.py#L101) — gałąź `ip_box`
- [src/dashboard/src/components/CalculatorForm.jsx](../../../src/dashboard/src/components/CalculatorForm.jsx) — nowe pola UI (warunkowo wyświetlane gdy `tax_form='ip_box'`)
- [src/dashboard/src/App.jsx:42-63](../../../src/dashboard/src/App.jsx#L42) — defaulty w `b2bData`
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze `form.ip_box_qualified_share*`, `form.ip_box_base_form*`, `form.ip_box_warning*`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — nowe testy

## Zmiana w `B2BDataModel`

Dodać:
```python
ip_box_qualified_share: float = Field(100.0, ge=0, le=100)  # procent kwalifikowanego dochodu
ip_box_base_form: str = Field('flat_tax', pattern='^(flat_tax|tax_scale)$')  # stawka dla części niekwalifikowanej
```

Walidator: te pola wymagane **tylko** gdy `tax_form='ip_box'`. Dla innych form ignorowane (warto dodać model-level validator).

## Zmiana w `calculate_b2b_results`

Zamiast (linia 101-102):
```python
elif tax_form == 'ip_box':
    annual_tax = math.ceil(max(0, taxable_base) * config['tax_thresholds']['ip_box'])
```

Nowe:
```python
elif tax_form == 'ip_box':
    qualified_share = float(b2b_data.get('ip_box_qualified_share', 100)) / 100.0
    base_form = b2b_data.get('ip_box_base_form', 'flat_tax')

    qualified_base = max(0, taxable_base) * qualified_share
    other_base = max(0, taxable_base) * (1.0 - qualified_share)

    qualified_tax = math.ceil(qualified_base * config['tax_thresholds']['ip_box'])

    if base_form == 'flat_tax':
        other_tax = math.ceil(other_base * config['tax_thresholds']['flat_tax'])
    elif base_form == 'tax_scale':
        # Wykorzystać tę samą logikę co dla tax_form='tax_scale' (linia 94-100)
        tax_threshold = config['tax_thresholds']['tax_scale'][0]['income']
        tax_reducing = config['tax_thresholds']['tax_reducing_amount']
        if other_base <= tax_threshold:
            other_tax = max(0, math.ceil(other_base * 0.12) - tax_reducing)
        else:
            other_tax = math.ceil((tax_threshold * 0.12) - tax_reducing + (other_base - tax_threshold) * 0.32)

    annual_tax = qualified_tax + other_tax
```

(Codex może wyodrębnić `compute_scale_tax(base)` jako helper — patrz D01.)

## Zmiana w UI

W `CalculatorForm.jsx`, w sekcji B2B, gdy `b2bData.tax_form === 'ip_box'`:
1. Pole `<Input>` `ip_box_qualified_share` (0–100, slider lub number) z tooltipem „Procent dochodu kwalifikującego się jako kwalifikowane prawa IP. Pozostała część rozliczana wg `ip_box_base_form`."
2. Pole `<Select>` `ip_box_base_form` z opcjami `flat_tax`, `tax_scale`.
3. Alert (`<Alert type="warning">`): „IP Box wymaga prowadzenia ewidencji kwalifikowanych dochodów oraz obliczenia wskaźnika nexus. Skonsultuj się z księgowym przed wyborem tej formy."

## Acceptance
- [x] `B2BDataModel` ma pola `ip_box_qualified_share` i `ip_box_base_form` z walidacją
- [x] Backend liczy IP Box jako sumę dwóch komponentów (kwalifikowany × 5% + reszta × wybrana stawka)
- [x] UI pokazuje pola IP Box **tylko** dla `tax_form='ip_box'` z disclaimerem
- [x] Test `test_ip_box_100_percent_qualified` — `qualified_share=100` → wynik = `taxable_base × 5%` (regresja)
- [x] Test `test_ip_box_60_percent_qualified_flat_base` — `qualified_share=60`, `base_form='flat_tax'` → `60%×5% + 40%×19%` (Case C z 0002)
- [x] Test `test_ip_box_60_percent_qualified_scale_base` — analogicznie dla `tax_scale`

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_ip_box_* -v
pytest -q
cd src/dashboard && npm test -- CalculatorForm
./run_app.sh  # smoke: wybierz IP Box → pojawia się pole + warning
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
# Sprawdź domyślny stan — pola IP Box NIE są widoczne przy innej formie podatku:
playwright_screenshot(name="B08-default-no-ipbox-fields")
playwright_evaluate(script="document.querySelector('[name*=ip_box_qualified],[id*=ip_box_qualified]') !== null")
# Oczekiwany wynik: false (pole ukryte gdy tax_form != ip_box)

# Zmień formę podatku na IP Box:
playwright_select_option(selector="select[name*=tax_form],select[id*=tax_form]", value="ip_box")
playwright_screenshot(name="B08-after-select-ipbox")

# Sprawdź, że pojawiło się pole kwalifikowanego dochodu:
playwright_evaluate(script="document.querySelector('[name*=ip_box_qualified],[id*=ip_box_qualified]') !== null")
# Oczekiwany wynik: true

# Sprawdź, że pojawiło się pole ip_box_base_form:
playwright_evaluate(script="document.querySelector('select[name*=ip_box_base],[select[id*=ip_box_base]') !== null")
# Oczekiwany wynik: true

# Sprawdź, że pojawił się alert / warning o ewidencji:
playwright_get_visible_text(selector="[class*=alert],[class*=warning],[role=alert]")
# Sprawdź: tekst zawiera "ewidencji" lub "konsultuj" lub "nexus"
```

## Rollback
Revert PR + zostaje stary uproszczony model. Realne ryzyko: użytkownicy IP Box zobaczą wyższy podatek (poprawiony). To pożądana zmiana, rollback tylko w wyjątkowym przypadku.

## Zależności
- Niezależne od B01-B07, B09-B12.
- **Blokuje**: F03 (Case C).
