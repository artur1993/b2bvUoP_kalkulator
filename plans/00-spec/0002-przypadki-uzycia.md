# 0002 — Przypadki użycia (fixturki dla testów)

Trzy konkretne scenariusze pokrywające ścieżki, na których historycznie wystąpiły błędy. Każdy zostaje zaimplementowany jako fixture w `tests/integration/test_real_scenarios.py` (task [F03](../02-tasks/F/F03-testy-z-konkretnymi-liczbami.md)).

**Wszystkie liczby na 2026 rok**, źródła stawek: [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md).

Oczekiwane netto należy doprecyzować po wdrożeniu fazy B (math fix) — wartości poniżej to **szacunki orientacyjne** z tolerancją ±50 PLN/rok dla testu akceptacyjnego.

---

## Case A — Mid-career programista, ryczałt vs UoP

**Persona**: 28 lat, 5 lat doświadczenia, mid Software Engineer.

**Wejście**:
```json
{
  "calculation_mode": "uop_to_b2b",
  "b2b": {
    "monthly_invoice_amount": 18000,
    "tax_form": "lump_sum_it",
    "zus_type": "full",
    "sickness_insurance": true,
    "monthly_business_costs": 500,
    "vacation_days": 20,
    "sick_days": 5,
    "stoppage_months": 0,
    "age": 28,
    "youth_relief": false,
    "customBenefits": 0,
    "companyBenefits": {}
  },
  "uop": {
    "monthly_gross_salary": 12000,
    "deductible_cost_settings": { "type": "standard" },
    "selected_benefits": ["medical_care"],
    "age": 28,
    "youth_relief": false
  }
}
```

**Oczekiwane (orientacyjnie)**:
- UoP `total_annual_value` ≈ 102 000 ± 1 000 PLN (z medical_care benefitem, BEZ podwójnego liczenia dni wolnych po B05).
- B2B `total_annual_value` ≈ 167 000 ± 1 500 PLN (ryczałt 12%, pełny ZUS, składka zdrowotna z progu „60k–300k" = 830.58 PLN/mies. po B02).
- `break_even_invoice_amount` ≈ 11 500 ± 500 PLN/mies.

**Co weryfikuje**:
- Stawka zdrowotna ryczałtu z poprawnego progu (B02).
- Brak PIT-0 dla 28-latka (oczywiste, ale regresja).
- Brak podwójnego liczenia dni wolnych UoP (B05).
- Pełny ZUS B2B 2026 (suma = 5652 PLN składek społecznych = 1103.27 + 452.16 + 138.47 + 94.39 + 138.47 zgodnie z configiem).

---

## Case B — Junior, ulga dla młodych

**Persona**: 24 lata, 2 lata doświadczenia, junior. **Krytyczne**: PIT-0 dotyczy UoP, nie B2B.

**Wejście**:
```json
{
  "calculation_mode": "uop_to_b2b",
  "b2b": {
    "monthly_invoice_amount": 12000,
    "tax_form": "flat_tax",
    "zus_type": "preferential",
    "sickness_insurance": true,
    "monthly_business_costs": 300,
    "vacation_days": 20,
    "sick_days": 0,
    "stoppage_months": 0,
    "age": 24,
    "youth_relief": false,
    "customBenefits": 0,
    "companyBenefits": {}
  },
  "uop": {
    "monthly_gross_salary": 8000,
    "deductible_cost_settings": { "type": "standard" },
    "selected_benefits": [],
    "age": 24,
    "youth_relief": true
  }
}
```

**Oczekiwane (orientacyjnie)**:
- UoP `total_annual_value` ≈ 79 000 ± 800 PLN (PIT-0 do 85 528 PLN aktywne, brak PIT od dochodu).
- B2B `total_annual_value` ≈ 119 000 ± 1 000 PLN (liniowy 19%, preferencyjny ZUS, **bez PIT-0**).
- `break_even_invoice_amount` ≈ 8 500 ± 500 PLN/mies.

**Co weryfikuje**:
- PIT-0 działa dla UoP <26 lat (klasyka).
- **PIT-0 NIE działa dla B2B** — nawet jeśli ktoś wyśle `b2b.youth_relief=true`, backend zwraca **400** (B04).
- Preferencyjny ZUS B2B 2026 (suma 30%-podstawy = 1441.80 × stawki = 281.44 + 115.34 + 24.08 + 35.32).

---

## Case C — Senior, IP Box z częściową kwalifikacją

**Persona**: 35 lat, 10+ lat doświadczenia, senior z udziałem kwalifikowanego dochodu IP.

**Wejście**:
```json
{
  "calculation_mode": "b2b_to_uop",
  "b2b": {
    "monthly_invoice_amount": 25000,
    "tax_form": "ip_box",
    "ip_box_qualified_share": 60,
    "ip_box_base_form": "flat_tax",
    "zus_type": "full",
    "sickness_insurance": true,
    "monthly_business_costs": 1000,
    "vacation_days": 25,
    "sick_days": 10,
    "stoppage_months": 1,
    "age": 35,
    "youth_relief": false,
    "customBenefits": 0,
    "companyBenefits": {}
  },
  "uop": {
    "monthly_gross_salary": 18000,
    "deductible_cost_settings": { "type": "elevated" },
    "selected_benefits": ["medical_care", "sport_card", "training_budget"],
    "age": 35,
    "youth_relief": false
  }
}
```

**Oczekiwane (orientacyjnie)**:
- UoP `total_annual_value` ≈ 155 000 ± 1 500 PLN (z benefitami, podwyższone KUP, **bez PPK** w tym przykładzie).
- B2B `total_annual_value` ≈ 245 000 ± 2 000 PLN (IP Box: 60% × 5% + 40% × 19%, pełny ZUS, ryczałt zdrowotny z progu „60k–300k" jeśli przychód roczny w tym zakresie albo „>300k" jeśli wyżej).
- `break_even_gross_salary` ≈ 28 000 ± 1 000 PLN/mies. (UoP musiałby zarabiać tyle, żeby dorównać B2B IP Box).

**Co weryfikuje**:
- IP Box z polem `ip_box_qualified_share` (B08).
- IP Box z polem `ip_box_base_form` (B08).
- Limit 30-krotności UoP dla wysokich pensji (282 600 PLN, sprawdzenie czy nie blokuje).
- Lost revenue z B2B (stoppage_month, vacation_days, sick_days).

---

## Reguły walidacji testu (dla F03)

1. Każdy case ma trzy asserty: `total_annual_value` B2B, `total_annual_value` UoP, `break_even_*`.
2. Tolerancja: **±50 PLN dla `monthly_net_income`**, **±1500 PLN dla `total_annual_value`**.
3. Wartości oczekiwane wylicza się **raz**, po wdrożeniu fazy B (snapshot), i wpisuje do testu. Każda zmiana implementacji = aktualizacja oczekiwań po review prawnym.
4. Test sprawdza też **strukturę odpowiedzi**: obecność kluczy `b2b_results`, `uop_results`, `break_even_*`, `analysis.summary`, `analysis.methodology`.

## Edge cases (dodatkowe, do testów w F02)

- `monthly_invoice_amount = 0` → wszystkie wartości B2B = 0, bez crasha.
- `monthly_gross_salary = 0` + `deductible_cost_settings.type = 'author_50'` + `creative_work_percentage = 50` → bez ZeroDivisionError (B07).
- `b2b.zus_type = 'small_business'` → 400 Bad Request (B09).
- `b2b.youth_relief = true` → 400 Bad Request (B04).
- `uop.youth_relief = true` + `uop.age = 30` → 400 Bad Request lub silent disable (B04).
- `monthly_invoice_amount = 100000` (>1M rocznie) → naliczona danina solidarnościowa 4% (B12).
- `monthly_invoice_amount = 50000` (600k rocznie) → BEZ daniny.
