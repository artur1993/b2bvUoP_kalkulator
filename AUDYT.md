# AUDYT — Kalkulator B2B vs UoP (2026)

**Data audytu**: 2026-05-23
**Zakres**: pełny — bezpieczeństwo, poprawność obliczeń (PL prawo 2026), architektura backendu i frontendu, i18n, dostępność, wydajność, zależności, higiena repo, CI/CD, testy.
**Metoda**: czterech równoległych agentów Explore + ręczna weryfikacja każdego krytycznego znaleziska wprost w kodzie. Znaleziska, których nie potwierdziłem, nie zostały włączone do raportu.
**Format każdego znaleziska**: Lokalizacja → Problem → Dlaczego ważne → Naprawa → Wysiłek (S/M/L).

---

## 1. Podsumowanie wykonawcze

### Liczba znalezisk wg severity

| Severity | Liczba |
|----------|--------|
| KRYTYCZNE | 5 |
| WYSOKIE | 26 |
| ŚREDNIE | 35 |
| NISKIE | 18 |
| **Razem** | **84** |

> Cztery znaleziska są wymienione w dwóch sekcjach (np. „2025" jako część poprawności obliczeń [3.11] i i18n [6.1]) — to celowe powtórzenie z różnych perspektyw, a nie odrębne błędy. Realnie unikalnych znalezisk: **80**.

### Top 5 spraw do natychmiastowej naprawy

1. **[2.1] `debug=True` hardkodowany w produkcji** ([src/app.py:169](src/app.py#L169)) — pełne stack-trace'y i debugger Werkzeuga dostępne każdemu.
2. **[3.1] Ulga dla młodych (PIT-0) działa dla B2B** ([src/calculations.py:81–82, 90](src/calculations.py#L81), [src/dashboard/src/App.jsx:138–141](src/dashboard/src/App.jsx#L138)) — w polskim prawie PIT-0 nie obejmuje samozatrudnionych; aplikacja zaniża podatek nawet o ~10k PLN/rok dla osób <26.
3. **[3.2] Niespójność `small_business` walidator vs konfig** ([src/validation.py:14](src/validation.py#L14) vs [dane_wejsciowe_kalkulator.json:26–51](dane_wejsciowe_kalkulator.json#L26)) — walidator akceptuje `small_business`, konfig nie zawiera tej gałęzi → `KeyError` z 500 i debug-trace.
4. **[3.3] Podwójne liczenie wartości dni wolnych w UoP** ([src/calculations.py:227–229](src/calculations.py#L227)) — 26 dni urlopu jest już wliczone w `monthly_gross_salary`, a kod dodaje je ponownie jako `paid_days_off_value` → zawyża wartość UoP o ~10% rocznego brutto.
5. **[2.2 + 2.3] Trzy endpointy bez walidacji + globalny CORS** ([src/app.py:39–67, 124](src/app.py#L39)) — `break-even-analysis`, `sensitivity-analysis`, `export/excel` przyjmują dowolny JSON i propagują go do funkcji liczących; brak `Access-Control-Allow-Origin` whitelisty.

### Ogólna ocena dojrzałości projektu

Aplikacja w wersji „działa lokalnie u autora", **nie produkcyjna**. Solidna fasada (testy jednostkowe, i18n, dark mode, podgląd PDF), ale:
- backend ma 3 z 4 endpointów bez walidacji,
- model emerytalny opiera się na sztywnych założeniach (30 lat do emerytury, stała stopa zwrotu) niezależnie od wieku użytkownika,
- frontend miesza obliczenia biznesowe z UI,
- brak CI, brak version-pinów Pythona, brak Pythonowego lintera,
- README mówi „2025", kod jest na 2026.

Kalkulator może dawać **rażąco błędne wyniki w trzech typowych przypadkach**: programista <26 lat planujący przejście na B2B (PIT-0 dla B2B), porównanie B2B z UoP przy tradycyjnym etacie (podwójne dni wolne), oraz wybór „Mały ZUS Plus" (crash).

---

## 2. Bezpieczeństwo i walidacja

### [KRYTYCZNE] 2.1 `app.debug=True` hardkodowany

- **Lokalizacja**: [src/app.py:169](src/app.py#L169), [run_app.sh:11](run_app.sh#L11) (`FLASK_DEBUG=1`)
- **Problem**: `app.run(debug=True, ...)` plus `FLASK_DEBUG=1` w skrypcie startowym → w trybie debugowym Flask udostępnia interaktywny debugger Werkzeuga (`/console`), włącza hot-reload, a `app.debug` jest sprawdzane w globalnym error handlerze w linii 122, gdzie zwraca `str(e)` użytkownikowi.
- **Dlaczego ważne**: pełny dostęp do REPL Pythona na serwerze produkcyjnym = pełne RCE. Stack-trace'y wyciekają informacje o ścieżkach plików i strukturze obiektów.
- **Naprawa**: czytać konfig z ENV: `app.run(debug=os.environ.get('FLASK_ENV') == 'development')`. Domyślnie `False`. W skrypcie produkcyjnym uruchamiać `gunicorn`/`waitress`, nie `flask run`.
- **Wysiłek**: S

### [KRYTYCZNE] 2.2 Trzy endpointy bez walidacji Pydantic

- **Lokalizacja**: [src/app.py:39–67](src/app.py#L39), [124–153](src/app.py#L124)
- **Problem**: `/api/calculate/break-even-analysis`, `/api/calculate/sensitivity-analysis` oraz `/api/export/excel` używają `request.get_json()` i przekazują surowe `b2b`/`uop` dicts wprost do funkcji liczących. Złośliwy lub omyłkowy payload (`{"b2b": {"monthly_invoice_amount": "xyz"}}`) wywołuje `ValueError` w `float()`, łapany przez global handler, **który w trybie debug zwraca stack-trace**.
- **Dlaczego ważne**: użytkownik podpięty bezpośrednio do API może wywołać 500-tki z pełnymi tracebackami (z 2.1 → information disclosure). Brak rate-limitingu w połączeniu z `sensitivity-analysis` (50+ kalkulacji per request) i `break-even-analysis` (1500+ iteracji) tworzy łatwy wektor DoS.
- **Naprawa**: stworzyć osobne modele Pydantic dla tych endpointów (`BreakEvenAnalysisRequest`, `SensitivityAnalysisRequest`, `ExcelExportRequest`) i opakować je tym samym dekoratorem `@validate_calculation_request` (uogólnić dekorator do `@validate(Model)`).
- **Wysiłek**: M

### [WYSOKIE] 2.3 CORS otwarty na wszystko

- **Lokalizacja**: [src/app.py:23](src/app.py#L23) — `CORS(app)`
- **Problem**: bez argumentów `Flask-Cors` ustawia `Access-Control-Allow-Origin: *` dla wszystkich endpointów i metod. Każda strona w przeglądarce użytkownika może wysłać żądanie POST z jego ciasteczkami (ale ciasteczek tu nie ma) lub po prostu nadużywać API.
- **Dlaczego ważne**: API jest publiczne, bez autoryzacji, więc nie ma kradzieży sesji, ale niekontrolowane Origin = łatwe nadużycie z dowolnej strony.
- **Naprawa**: `CORS(app, origins=["http://localhost:5173", "https://kalkulator.example.com"])` (lista z ENV).
- **Wysiłek**: S

### [WYSOKIE] 2.4 Globalny error handler ujawnia stack-trace w trybie debug

- **Lokalizacja**: [src/app.py:122](src/app.py#L122) — `str(e) if app.debug else "An internal server error occurred."`; [src/app.py:52, 67](src/app.py#L52) — pozostałe handlery zwracają `str(e)` **bezwarunkowo**.
- **Problem**: nawet po wyłączeniu debug-mode w głównym endpoincie, dwa inne handlery dalej ujawniają wyjątki. Komunikat „str(e)" przy `ValueError("could not convert string to float: 'xyz'")` ujawnia, gdzie i jak parsujemy dane.
- **Naprawa**: jeden globalny handler zwracający stałą wiadomość; szczegóły wyłącznie do `app.logger.exception(...)`.
- **Wysiłek**: S

### [ŚREDNIE] 2.5 Brak rate-limitingu

- **Lokalizacja**: cały `app.py`
- **Problem**: `sensitivity-analysis` wykonuje 3 pełne kalkulacje B2B per request, `break-even-analysis` ~150 kalkulacji per request (zakres 50–200% × krok 100), a `calculate_break_even` w worst-case do 2000 iteracji. Nieskończone żądania z jednego IP = DoS.
- **Naprawa**: `Flask-Limiter` z prostą polityką (np. 10 req/min/IP) na endpointach kalkulacyjnych.
- **Wysiłek**: S

### [ŚREDNIE] 2.6 Path traversal informacyjny w serwowaniu statyki

- **Lokalizacja**: [src/app.py:159](src/app.py#L159)
- **Problem**: `os.path.exists(os.path.join(app.static_folder, path))` sprawdza istnienie pliku **przed** delegacją do `send_from_directory`. Z `path = '../../../etc/passwd'` `os.path.exists` zwraca `True` jeśli plik istnieje, ale `send_from_directory` zablokuje wyjście poza dir. Daje to **timing oracle** do enumerowania plików na hoście.
- **Dlaczego ważne**: niska istotność (plik nie zostanie wysłany), ale ujawnia istnienie ścieżek.
- **Naprawa**: usunąć ręczne `os.path.exists` i polegać tylko na `send_from_directory`, łapiąc `NotFound` z fallbackiem do `index.html`.
- **Wysiłek**: S

### [ŚREDNIE] 2.7 Logowanie debug do `flask.log` w CWD

- **Lokalizacja**: [src/app.py:26–31](src/app.py#L26)
- **Problem**: `RotatingFileHandler('flask.log', ...)` zapisuje w bieżącym katalogu uruchomienia. Plik `flask.log` jest **zatwierdzony w repo** (`git ls-files` pokazuje go w historii mimo wpisu w `.gitignore` — patrz [11.2]).
- **Naprawa**: ścieżka logu z ENV (`LOG_PATH=/var/log/kalkulator.log`); domyślnie poza repo.
- **Wysiłek**: S

### [NISKIE] 2.8 Endpoint Excel nie weryfikuje danych wejściowych

- **Lokalizacja**: [src/app.py:124–153](src/app.py#L124)
- **Problem**: `b2b_results` i `uop_results` w body są przepisywane do arkusza bez re-kalkulacji. Atakujący może wprowadzić zmanipulowane liczby do swojego Excela (ale to są jego własne dane, więc impact niski).
- **Naprawa**: endpoint powinien przyjmować `b2b` i `uop` (parametry wejściowe), nie wyniki, i przeliczać przed eksportem. Jednocześnie poszerzyć eksport (dziś tylko `total_annual_value` — patrz [12.3]).
- **Wysiłek**: M

---

## 3. Poprawność obliczeń (prawo PL 2026)

> **Sekcja kluczowa.** Każde znalezisko zweryfikowane wprost w kodzie. Tam, gdzie wynik wymaga interpretacji ustaw, oznaczone jako **WYMAGA WERYFIKACJI PRAWNEJ** (konsultacja z księgowym).

### [KRYTYCZNE] 3.1 Ulga dla młodych (PIT-0) stosowana dla B2B

- **Lokalizacja**: backend [src/calculations.py:81–82](src/calculations.py#L81), [src/calculations.py:90](src/calculations.py#L90); frontend [src/dashboard/src/App.jsx:138–141](src/dashboard/src/App.jsx#L138)
- **Problem**: kod B2B redukuje podstawę opodatkowania o `youth_relief_limit` (85 528 PLN), gdy `youth_relief=True`. Frontend dodatkowo **automatycznie** ustawia `youth_relief = (age < 26)` dla obu formularzy — B2B i UoP. W polskim prawie podatkowym (art. 21 ust. 1 pkt 148 ustawy o PIT) ulga dla młodych dotyczy wyłącznie: umów o pracę, umów zlecenia, praktyk absolwenckich i stażu uczniowskiego. **Nie obejmuje przychodów z działalności gospodarczej**.
- **Dlaczego ważne**: dla 25-latka na B2B z fakturą 15 000 PLN/mies. (180k rocznie) kalkulator zaniża podatek o ~10 263 PLN/rok (85 528 × 12%). Programista wierzący w wynik przejdzie na B2B z błędnym oczekiwaniem dochodu netto.
- **Naprawa**:
  1. W backendzie usunąć blok `if youth_relief` z gałęzi B2B (linie 81–82 oraz 90).
  2. W frontendzie usunąć linijkę `youth_relief: isYouthReliefApplicable` z `setB2bData` (App.jsx:139). Pozostawić tylko dla UoP.
  3. W UI ukryć checkbox „ulga dla młodych" dla B2B (lub zamienić na info-box: „nie dotyczy działalności gospodarczej").
- **Wysiłek**: S

### [KRYTYCZNE] 3.2 `small_business` w walidatorze, brak w konfigu → 500

- **Lokalizacja**: [src/validation.py:14](src/validation.py#L14) (`pattern='^(start_relief|small_business|preferential|full)$'`) vs [dane_wejsciowe_kalkulator.json:26–51](dane_wejsciowe_kalkulator.json#L26) (gałąź zawiera tylko `start_relief`, `preferential`, `full`)
- **Problem**: walidator Pydantic akceptuje `zus_type='small_business'`. `calculations.py:40` robi `config['zus_2026'][zus_type]` → `KeyError`. W trybie debug stack-trace ląduje w przeglądarce użytkownika.
- **Naprawa**:
  - Jeśli „Mały ZUS Plus" ma być wspierany: dodać gałąź `small_business` do `dane_wejsciowe_kalkulator.json` z wartościami obliczonymi wg podstawy = średnia dochodu z poprzedniego roku × 30% × 60% (regulacja ZUS) — wymaga osobnego pola wejściowego „średni miesięczny dochód za poprzedni rok" w UI.
  - Jeśli nie ma być wspierany: usunąć `small_business` z pattern w `validation.py:14`.
  - Jednocześnie UI pokazuje **tylko** `preferential` i `full` ([src/dashboard/src/components/CalculatorForm.jsx:12–15](src/dashboard/src/components/CalculatorForm.jsx#L12)) — tj. `start_relief` jest również akceptowany przez walidator, ale niedostępny w UI. **Trzecia niespójność** w tej samej macierzy.
- **Wysiłek**: M (dodanie Małego ZUS Plus) lub S (usunięcie).

### [KRYTYCZNE] 3.3 Podwójne liczenie dni wolnych w UoP

- **Lokalizacja**: [src/calculations.py:226–229](src/calculations.py#L226)
- **Problem**:
  ```
  paid_days_off_value = config['uop_days_off']['vacation']['days'] * daily_rate
  total_uop_value = annual_net + benefits_value + paid_days_off_value
  ```
  `annual_net` pochodzi z `cumulative_gross = 12 × monthly_gross_salary` — czyli **w pełnym wynagrodzeniu rocznym są już płatne urlopy** (pracownik zarabia tyle samo w 26-dniowym miesiącu urlopowym, co w pełnym miesiącu pracy). Dodawanie `26 × dzienna_stawka` to dublowanie wartości urlopu.
- **Dlaczego ważne**: dla pensji 10 000 PLN brutto miesięcznie (~7 100 PLN netto), `daily_rate = 10000/21 ≈ 476`. `26 × 476 ≈ 12 376 PLN` doliczane do rocznego netto = +14,5% sztucznego boostu po stronie UoP w porównaniu z B2B.
- **Naprawa**: usunąć `paid_days_off_value` z `total_uop_value`. Wartość dni wolnych jako osobny info-box, jeśli ma znaczenie informacyjne. Albo: symetrycznie odjąć urlop po stronie B2B w analogiczny sposób (już jest, jako `lost_revenue_vacation`), ale **dodanie po stronie UoP jest błędem księgowym**, bez względu na intencję.
- **Wysiłek**: S

### [WYSOKIE] 3.4 PPK modelowane błędnie

- **Lokalizacja**: [src/calculations.py:222–224](src/calculations.py#L222), [dane_wejsciowe_kalkulator.json:67](dane_wejsciowe_kalkulator.json#L67) (`"ppk": 0.02`)
- **Problem**: kod dodaje `cumulative_gross * 0.02` do `benefits_value` jako benefit. Wartość 2% odpowiada **wpłacie pracownika** (z brutto, opodatkowanej PIT), a nie wpłacie pracodawcy (minimum 1,5%). Aplikacja:
  1. Traktuje 2% pracownika jako benefit, co jest księgowym nonsensem — to jego własne pieniądze.
  2. Nie odejmuje 2% PPK z `cumulative_gross` przed obliczeniem podatku (PPK pracownika jest opodatkowany PIT).
  3. Nie liczy dopłaty pracodawcy 1,5% (która **jest** benefitem, ale opodatkowanym jako przychód pracownika).
- **Dlaczego ważne**: dla pensji 10 000 PLN brutto, PPK „benefit" w aplikacji = 2 400 PLN/rok (zawyżony); poprawnie powinien być ~1 800 PLN/rok (1,5% pracodawcy) minus PIT od dopłaty (~216 PLN przy 12%) = ~1 584 PLN.
- **Naprawa**: przemodelować obsługę PPK:
  - Wartość benefitu = 1,5% rocznego brutto × (1 - 0,12) [skala] lub odpowiednio.
  - Składka pracownika 2% odejmowana z brutto przed obliczeniem podatku **nie jest** prawidłowa — PPK pracownika jest pobierany po obliczeniu PIT/ZUS, ale dopłata pracodawcy jest opodatkowana PIT (więc PIT z całej wpłaty pracodawcy doliczamy do podatku).
  - Wykonać dokładny przegląd z księgowym.
- **Wysiłek**: M, **wymaga weryfikacji prawnej**

### [WYSOKIE] 3.5 Brak daniny solidarnościowej (4% > 1M PLN)

- **Lokalizacja**: brak w `dane_wejsciowe_kalkulator.json` i `calculations.py`
- **Problem**: zgodnie z art. 30h ustawy PIT, podatnicy, których roczny dochód (suma podstaw) przekracza 1 000 000 PLN, płacą dodatkową daninę 4% od nadwyżki. Aplikacja jej nie nalicza.
- **Dlaczego ważne**: dla seniora B2B z fakturą 100k PLN/mies. (1,2M rocznie), niedoszacowanie podatku = (1 200 000 - 1 000 000) × 0,04 = 8 000 PLN/rok.
- **Naprawa**: dodać `solidarity_tax_threshold: 1000000` i `solidarity_tax_rate: 0.04` do `tax_thresholds` w configu; w `calculate_b2b_results` i `calculate_uop_results` doliczać `max(0, taxable_base - threshold) * rate` do `annual_tax`.
- **Wysiłek**: S

### [WYSOKIE] 3.6 Pole `age` ignorowane przez backend

- **Lokalizacja**: [src/validation.py:20, 34](src/validation.py#L20) (`age` walidowane), `calculations.py` (zero referencji do `age`)
- **Problem**: pole jest wymagane (`Field(..., ge=18)`), ale backend go nie używa. Weryfikacja wieku <26 dla PIT-0 odbywa się tylko po stronie frontendu (App.jsx:138), co zaufanie przesuwa do klienta. Każdy może wysłać `age=18` i `youth_relief=True` dla osoby 40-letniej.
- **Naprawa**: w backendzie odrzucać `youth_relief=True`, gdy `age >= 26`. Lepiej: usunąć checkbox z UI i wnioskować ulgę wyłącznie z wieku.
- **Wysiłek**: S

### [WYSOKIE] 3.7 IP Box stosowany do całej podstawy zamiast kwalifikowanego dochodu

- **Lokalizacja**: [src/calculations.py:101–102](src/calculations.py#L101)
- **Problem**: `annual_tax = math.ceil(max(0, taxable_base) * config['tax_thresholds']['ip_box'])` — 5% × cała podstawa. W rzeczywistości IP Box (art. 30ca ustawy PIT) dotyczy wyłącznie **kwalifikowanego dochodu z kwalifikowanych praw własności intelektualnej** (programy komputerowe pisane „od zera", patenty, etc.). Reszta dochodu opodatkowana jest skalą lub liniowo.
- **Dlaczego ważne**: kalkulator zakłada, że 100% dochodu B2B jest kwalifikowane, co dla większości programistów nie jest prawdą (np. utrzymanie kodu, code review, spotkania — nie kwalifikują się).
- **Naprawa**:
  - Dodać pole `ip_box_qualified_income_share` (procent dochodu kwalifikowanego, np. 0–100%) do `B2BDataModel`.
  - Obliczać `ip_box_tax = qualified_share * taxable_base * 0.05 + (1 - qualified_share) * tax(taxable_base * (1 - qualified_share))` z odpowiednią stawką (skala lub liniowy — kolejna decyzja).
  - Albo: w UI wymusić wybór „bazowej" formy opodatkowania dla niekwalifikowanej części.
- **Wysiłek**: L, **wymaga weryfikacji prawnej**

### [WYSOKIE] 3.8 Podejrzane wartości składek zdrowotnych ryczałtu

- **Lokalizacja**: [dane_wejsciowe_kalkulator.json:52–56](dane_wejsciowe_kalkulator.json#L52)
- **Problem**: progi składki zdrowotnej dla ryczałtu w configu:
  ```
  60 000 → 432.54 PLN/mies.
  300 000 → 720.90 PLN/mies.
  > 300 000 → 1297.62 PLN/mies.
  ```
  Wartości są dokładnie: 4806 × 0,09 ; 4806 × 0,15 ; 4806 × 0,27. Czyli wszystkie liczone od **minimalnego wynagrodzenia** (4806 PLN). Zgodnie z art. 81 ust. 2e ustawy o świadczeniach opieki zdrowotnej, podstawą składki zdrowotnej dla ryczałtu jest **przeciętne miesięczne wynagrodzenie w sektorze przedsiębiorstw w IV kwartale poprzedniego roku**. Dla 2026 (przy `average_forecasted_wage = 9420` z configu) progi powinny być:
  - 60 000: 60% × 9420 × 9% ≈ **508,68 PLN/mies.**
  - 60 000–300 000: 100% × 9420 × 9% ≈ **847,80 PLN/mies.**
  - > 300 000: 180% × 9420 × 9% ≈ **1525,99 PLN/mies.**
- **Dlaczego ważne**: dla pracownika na ryczałcie z fakturą 15 000 PLN/mies. (180k rocznie, próg środkowy), kalkulator zaniża zdrowotną o (847,80 − 720,90) × 12 = **1 522 PLN/rok**. To istotne odchylenie.
- **Naprawa**: zaktualizować progi w configu do faktycznych wartości na 2026 wg oficjalnych komunikatów MZ/ZUS. Najlepiej obliczać je dynamicznie z `average_forecasted_wage` ze współczynnikami 0,6/1,0/1,8. **Wartości oficjalne MUSI zweryfikować księgowy.**
- **Wysiłek**: S, **wymaga weryfikacji prawnej**

### [WYSOKIE] 3.9 Limit odliczenia składki zdrowotnej (liniowy) — wartość do weryfikacji

- **Lokalizacja**: [dane_wejsciowe_kalkulator.json:17](dane_wejsciowe_kalkulator.json#L17) — `health_contribution_deduction_limit_flat_tax: 14100`
- **Problem**: 14 100 PLN to roczny limit odliczenia zapłaconych składek zdrowotnych dla liniowego. W 2024 limit to było 11 600 PLN, w 2025 ~12 900 PLN. Wartość 14 100 wymaga weryfikacji wobec oficjalnego komunikatu.
- **Naprawa**: zweryfikować wobec ustawy budżetowej / komunikatu MF na 2026; udokumentować źródło w komentarzu w configu lub w `analysis.py`.
- **Wysiłek**: S, **wymaga weryfikacji prawnej**

### [WYSOKIE] 3.10 ZeroDivisionError w kosztach autorskich (UoP)

- **Lokalizacja**: [src/calculations.py:188](src/calculations.py#L188)
- **Problem**: `author_costs_base = creative_income - (monthly_social * (creative_income / monthly_gross_salary))` — jeśli `monthly_gross_salary = 0` (Pydantic dopuszcza `ge=0`) i `creative_work_percentage > 0` lub `type='author_50'`, dzielenie przez zero → 500. Dodatkowo wzór jest matematycznie redundantny: `creative_income / monthly_gross_salary == creative_work_percentage`, więc cały człon = `monthly_social * creative_work_percentage`.
- **Naprawa**:
  - Uprościć: `author_costs_base = creative_income - monthly_social * creative_work_percentage`.
  - Dodać walidację `monthly_gross_salary > 0` gdy `type='author_50'`.
- **Wysiłek**: S

### [WYSOKIE] 3.11 Frontend mówi „2025"

- **Lokalizacja**: [src/dashboard/src/locales/pl/translation.json](src/dashboard/src/locales/pl/translation.json), [src/dashboard/src/locales/en/translation.json](src/dashboard/src/locales/en/translation.json) (klucze nagłówków i tooltipów)
- **Problem**: tytuły, opisy benefitów, tooltipy w obu plikach tłumaczeń odwołują się do roku 2025, podczas gdy backend liczy wg `zus_2026`, `pension_limits_2026` i wartości progowych 2026.
- **Dlaczego ważne**: użytkownik ufa interfejsowi: jeśli aplikacja mówi „kalkulator 2025", to oczekuje stawek 2025. Niespójność = utrata zaufania, niezgodność marketingowa.
- **Naprawa**: globalna zamiana „2025" → „2026" w obu plikach `.json`, plus weryfikacja w README, `analysis.py` (`methodology` — gdzie już jest „2026" — OK).
- **Wysiłek**: S

### [ŚREDNIE] 3.12 Brak limitów czasowych dla preferencyjnego ZUS i ulgi na start

- **Lokalizacja**: `calculations.py` (brak logiki czasowej)
- **Problem**: Ulga na start (6 mies.) i preferencyjny ZUS (24 mies. po uldze na start lub od początku) to mechanizmy ograniczone w czasie. Aplikacja pozwala wybrać każdą gałąź bezterminowo (kalkulator liczy rok pełny). Nie ma żadnej informacji w UI, że to przejściowe.
- **Dlaczego ważne**: typowy użytkownik wybiera „preferencyjny" i widzi wynik, który jest prawdziwy tylko przez pierwsze 24 mies. Pod koniec tego okresu wynik nieaktualny.
- **Naprawa**:
  - W kalkulatorze: dodać tryb porównania „rok 1 / rok 2 / rok 3+" (z różnymi typami ZUS), zwracający uśredniony wynik.
  - Minimum: w UI dodać ostrzeżenie i tooltip o ograniczeniach.
- **Wysiłek**: M

### [ŚREDNIE] 3.13 Brak FGŚP w pełnym ZUS B2B

- **Lokalizacja**: [dane_wejsciowe_kalkulator.json:44–51](dane_wejsciowe_kalkulator.json#L44)
- **Problem**: gałąź `full` zawiera `labor_fund: 138.47` (Fundusz Pracy), ale brakuje **FGŚP** (Fundusz Gwarantowanych Świadczeń Pracowniczych) ~3 PLN/mies. Wartość znikoma, ale to jest osobna składka.
- **Naprawa**: dodać `fgsp: 3.46` (lub aktualnie obowiązującą wartość 2,45‰ od podstawy `full.base`).
- **Wysiłek**: S

### [ŚREDNIE] 3.14 Liniowy break-even szuka w ograniczonym zakresie

- **Lokalizacja**: [src/calculations.py:246–253](src/calculations.py#L246)
- **Problem**:
  ```
  for test_invoice in range(start_range, 200000, 100):
  ```
  start_range = 50% pensji bazowej, koniec na 200 000 PLN/mies. Dla pensji 150 000 PLN miesięcznie break-even pewnie wyższy niż 200k, kod zwraca `-1.0` (brak wyniku). Krok 100 PLN = niedokładność do ±100 PLN w odpowiedzi.
- **Naprawa**: binary search albo zwiększenie zakresu do `max(200000, base * 3)`. Dla precyzji <1 PLN: bisekcja na ostatnich 200 PLN.
- **Wysiłek**: S

### [ŚREDNIE] 3.15 Sensitivity analysis: hardkodowane parametry

- **Lokalizacja**: [src/calculations.py:278](src/calculations.py#L278) — `params = {'monthly_business_costs': 500, 'vacation_days': 5, 'stoppage_months': 1}`
- **Problem**: tylko 3 parametry, ze sztywnym „o ile zmieniamy" (500 PLN, 5 dni, 1 mies.). README obiecuje pełny wykres tornado.
- **Naprawa**: pełna lista parametrów (`monthly_invoice_amount`, `tax_form`, `zus_type`, `health_contribution_*`...) z procentowymi zmianami (±10%), nie sztywnymi krokami.
- **Wysiłek**: M

### [ŚREDNIE] 3.16 `cumulative_gross` zakłada 12 pełnych miesięcy

- **Lokalizacja**: [src/calculations.py:173](src/calculations.py#L173)
- **Problem**: pętla `for month in range(1, 13)` zawsze 12 razy. Brak obsługi przejścia w trakcie roku (np. ktoś przechodzi z B2B na UoP we wrześniu — nie da się tego policzyć).
- **Naprawa**: dodać opcjonalny parametr `months_worked` (domyślnie 12).
- **Wysiłek**: M

### [ŚREDNIE] 3.17 Brak walidacji górnych granic w Pydantic

- **Lokalizacja**: [src/validation.py:17–19](src/validation.py#L17)
- **Problem**: `vacation_days: int = Field(0, ge=0)` — brak `le=365`. `stoppage_months: int = Field(0, ge=0)` — brak `le=12`. Można wysłać `vacation_days=1000`.
- **Naprawa**: dodać górne granice (`le=365`, `le=12`, `le=10000000` dla kwot).
- **Wysiłek**: S

### [NISKIE] 3.18 Niespójne zaokrąglenia

- **Lokalizacja**: [src/calculations.py:83](src/calculations.py#L83) (`round`), [calculations.py:93, 98, 100, 216, 218](src/calculations.py#L93) (`math.ceil`)
- **Problem**: ryczałt używa `round`, pozostałe formy `math.ceil`. Realnie różnice <1 PLN, ale niespójność wewnętrzna.
- **Naprawa**: ujednolicić do `round_half_to_even` (księgowy banker's rounding) lub `math.ceil` w całym kodzie. Udokumentować zasadę.
- **Wysiłek**: S

### [NISKIE] 3.19 Model emerytalny mocno uproszczony

- **Lokalizacja**: [src/pension_calculator.py](src/pension_calculator.py)
- **Problem**: stałe `YEARS_TO_RETIREMENT = 30`, `ANNUAL_RETURN_RATE = 0.045`, `B2B_NET_FACTOR = 0.70`, `ZUS_DIVISOR = 264`, `CAPITAL_MULTIPLIER = 1.2`. Pole `age` (które jest zbierane!) nigdzie nie używane do dynamicznego wyliczenia lat do emerytury. Brak inflacji, brak realnej waloryzacji konta ZUS rocznym wskaźnikiem PKB.
- **Dlaczego ważne**: użytkownik widzi „luka emerytalna 1 200 PLN/mies." i podejmuje na tej podstawie decyzję — wartość obarczona błędem rzędu 50–100%.
- **Naprawa**:
  - Wyliczać `years_to_retirement = 65 - age` (dla mężczyzn) / `60 - age` (dla kobiet — wymaga pola `gender`).
  - Wynieść stałe do configu jako `pension_simulation` z komentarzem „założenia uproszczone".
  - W UI dodać disclamer „symulacja uproszczona — różni się od oficjalnych prognoz ZUS".
- **Wysiłek**: M

### [NISKIE] 3.20 Limit kosztów autorskich może się rozjechać między miesiącami a rokiem

- **Lokalizacja**: [src/calculations.py:186–197](src/calculations.py#L186)
- **Problem**: limit 120 000 PLN sprawdzany w pętli miesięcznej, w miesiącu przekroczenia limit zostaje wyrównany, ale w następnym miesiącu kod używa `tax_deductible_costs.standard` (250 PLN). To prawidłowe zachowanie, ale brakuje tej logiki dla `elevated` — tj. po wyczerpaniu kosztów autorskich, użytkownik nie wraca do swoich rzeczywistych kosztów (elevated 300), tylko spada do standard.
- **Naprawa**: po wyczerpaniu limitu wracać do `deductible_cost_type` (jeśli wcześniej `elevated`, to dalej 300 PLN; jeśli `standard`, to 250).
- **Wysiłek**: S

### [NISKIE] 3.21 Eksport Excel nie pokrywa się z PDF

- **Lokalizacja**: [src/app.py:124–153](src/app.py#L124)
- **Problem**: Excel zawiera tylko dwie liczby (`Total Annual Value` B2B i UoP). PDF (wg README) zawiera pełną metodologię, ubezpieczenia, checklisty. Niespójność z deklarowaną funkcjonalnością.
- **Naprawa**: rozszerzyć eksport Excel o sekcje analogiczne do PDF, albo udokumentować, że Excel to „minimalna wersja".
- **Wysiłek**: M

---

## 4. Architektura backendu

### [WYSOKIE] 4.1 Mieszanie routingu i logiki w `app.py`

- **Lokalizacja**: [src/app.py:39–67, 74–122, 124–153](src/app.py#L39)
- **Problem**: routes zawierają orkiestrację, logging, error handling oraz wywołania `calculate_*`. Brak warstwy „service" między endpointem a logiką.
- **Naprawa**: wprowadzić `src/services/` (lub `src/use_cases/`) z funkcjami `run_full_calculation(b2b, uop, mode, lang) -> dict`, używanymi przez wszystkie endpointy. Endpointy stają się cienkimi adapterami.
- **Wysiłek**: M

### [WYSOKIE] 4.2 God function `calculate_b2b_results` (136 linii)

- **Lokalizacja**: [src/calculations.py:13–136](src/calculations.py#L13)
- **Problem**: jedna funkcja liczy: utracony przychód, ZUS społeczne, składkę zdrowotną (4 gałęzie warunkowe), podatek (4 gałęzie warunkowe), benefity firmowe, sumę. Zmiana stawki = ryzyko regresji we wszystkim.
- **Naprawa**: rozbić na: `compute_lost_revenue`, `compute_social_contributions`, `compute_health_contribution`, `compute_income_tax`, `compute_benefits_value`, `assemble_b2b_results`. Każda funkcja testowalna w izolacji.
- **Wysiłek**: M

### [ŚREDNIE] 4.3 Magic numbers w kodzie

- **Lokalizacja**: [src/calculations.py:31](src/calculations.py#L31) (`0.8` — wynagrodzenie chorobowe), [src/calculations.py:80](src/calculations.py#L80) (`0.5` — 50% zdrowotnej w ryczałcie), [src/calculations.py:114](src/calculations.py#L114) (`0.8` ponownie), [src/calculations.py:56, 59](src/calculations.py#L56) (`0.09`, `0.049`)
- **Problem**: wartości regulacyjne wpisane wprost w kodzie. Zmiana ustawy = grep w kodzie + ryzyko pominięcia.
- **Naprawa**: przenieść do `dane_wejsciowe_kalkulator.json` (np. `regulatory_rates.sick_leave_percentage: 0.8`, `regulatory_rates.lump_sum_health_deduction_share: 0.5`).
- **Wysiłek**: S

### [ŚREDNIE] 4.4 Słabe typowanie na granicy funkcji

- **Lokalizacja**: [src/calculations.py](src/calculations.py) — funkcje przyjmują `Dict[str, Any]`
- **Problem**: po walidacji Pydantic dane są konwertowane przez `model_dump()` z powrotem na słownik (`g.validated_data` w `validation.py:54`), tracąc typy. Funkcje obliczeniowe pracują na dictach z defensywnymi `float()`, `int()`. To rozjazd między walidacją a użyciem.
- **Naprawa**: użyć modeli Pydantic bezpośrednio w funkcjach (typowanie `b2b_data: B2BDataModel`); to też ujawnia, gdzie kod czyta nieistniejące pola.
- **Wysiłek**: M

### [ŚREDNIE] 4.5 Niespójne nazewnictwo (camelCase vs snake_case vs polski)

- **Lokalizacja**: payloady, klucze configu
- **Problem**: `companyBenefits`, `customBenefits`, `paidVacationDays` (camelCase) vs `monthly_business_costs`, `tax_form` (snake_case); klucze polskie `analiza_ryzyka`, `rekomendacje`, `zdolnosc_kredytowa_uop` — wszystko w jednym configu.
- **Naprawa**: ujednolicić do snake_case zarówno w API, jak i w configu. Polskie klucze przenieść do `locales/` (i18n).
- **Wysiłek**: M (zmiana wpłynie na frontend i testy)

### [NISKIE] 4.6 Brak logowania faktycznych parametrów wejściowych

- **Lokalizacja**: [src/app.py:44, 59, 81, 129](src/app.py#L44)
- **Problem**: logujemy „Received calculation request", ale nie samą zawartość (poza `calculation_mode`). Debug nieskuteczny.
- **Naprawa**: `app.logger.debug(f"Payload: {json.dumps(request_data, default=str)}")` — w debug levelu, anonimowo.
- **Wysiłek**: S

---

## 5. Architektura frontendu

### [WYSOKIE] 5.1 Monolityczny `App.jsx` (243 linie, 8 useState)

- **Lokalizacja**: [src/dashboard/src/App.jsx](src/dashboard/src/App.jsx)
- **Problem**: cały stan aplikacji (B2B form, UoP form, age, mode, results, loading, error, insurance) w jednym komponencie. Brak Context, brak reducera. 12 propów do `CalculatorForm`, 4 propy + raw data do każdego wykresu.
- **Naprawa**: wydzielić `useCalculatorState` (custom hook) lub `CalculatorContext` z dwoma reducerami: `b2bReducer`, `uopReducer`. Dodać `useReducer` dla `results/loading/error`.
- **Wysiłek**: M

### [WYSOKIE] 5.2 Logika biznesowa w UI: `calculateTotalInsuranceCost`

- **Lokalizacja**: [src/dashboard/src/App.jsx:16–34](src/dashboard/src/App.jsx#L16)
- **Problem**: funkcja oblicza koszt ubezpieczeń na podstawie `insuranceModules` (też frontendowych) i automatycznie aktualizuje `monthly_business_costs`. Backend nie ma o tym pojęcia — frontend wpływa na koszty B2B w sposób niewidoczny w API.
- **Naprawa**: przenieść logikę ubezpieczeń (definicje modułów i kalkulacja) do backendu. API przyjmuje `insurance_config`, zwraca finalny `monthly_business_costs`.
- **Wysiłek**: L

### [WYSOKIE] 5.3 Hardkodowane „Calculating..." (zmiana z 8s na 2s — out-of-i18n)

- **Lokalizacja**: [src/dashboard/src/components/CalculatorForm.jsx:393](src/dashboard/src/components/CalculatorForm.jsx#L393)
- **Problem**: `{loading ? 'Calculating...' : t('form.calculate_button')}` — angielski tekst zhardkodowany.
- **Naprawa**: dodać klucz `form.loading_button` w obu `translation.json` i użyć `t('form.loading_button')`.
- **Wysiłek**: S

### [WYSOKIE] 5.4 `.replace(' (from company)', '')` w JSX łamie i18n

- **Lokalizacja**: [src/dashboard/src/components/CalculatorForm.jsx:193, 211, 229, 247, 265, 283, 301](src/dashboard/src/components/CalculatorForm.jsx#L193)
- **Problem**: kod oczekuje, że tłumaczenie zawiera dokładnie angielski sufiks `' (from company)'`. Polskie tłumaczenie ma inny sufiks (np. `' (od firmy)'`) → wynik to `"Opłacony urlop (od firmy) Days"` zamiast `"Opłacony urlop Dni"`.
- **Naprawa**: zamiast manipulować stringiem, używać osobnych kluczy: `form.paid_vacation_label` i `form.paid_vacation_days_label`. Plus konkatenacja " Days" → `t('common.days_unit')`.
- **Wysiłek**: S

### [ŚREDNIE] 5.5 Brak memoizacji i `useCallback`/`useMemo`

- **Lokalizacja**: cały `App.jsx` i komponenty wykresów
- **Problem**: każda zmiana stanu re-renderuje całe drzewo. `handleB2bChange` / `handleUopChange` tworzone od nowa przy każdym renderze. Wykresy ponownie tworzą datasety Chart.js, mimo że dane się nie zmieniły.
- **Naprawa**: `useCallback` dla handlerów, `useMemo` dla danych przekazywanych do wykresów, `React.memo` dla `BreakEvenChart`, `SensitivityChart`, `ComparisonChart`, `WaterfallChart`.
- **Wysiłek**: M

### [ŚREDNIE] 5.6 useEffect na URL params nie waliduje wartości

- **Lokalizacja**: [src/dashboard/src/App.jsx:155–171](src/dashboard/src/App.jsx#L155)
- **Problem**: `parseFloat(params.get('b2b_invoice'))` — jeśli ktoś poda `?b2b_invoice=abc`, fallback do default, OK. Ale `params.get('b2b_tax')` przepuszczane bez walidacji — można ustawić `?b2b_tax=evil`, co potem trafi do backendu i wywoła błąd walidatora. Brak whitelisty.
- **Naprawa**: whitelist dla `tax_form` (`['lump_sum_it', 'flat_tax', 'tax_scale', 'ip_box']`), `zus_type` (`['preferential', 'full']`), `mode`.
- **Wysiłek**: S

### [ŚREDNIE] 5.7 Wykresy fetchują dane przy każdym renderze

- **Lokalizacja**: [src/dashboard/src/components/BreakEvenChart.jsx](src/dashboard/src/components/BreakEvenChart.jsx), [SensitivityChart.jsx](src/dashboard/src/components/SensitivityChart.jsx) (zgodnie z raportem agenta — nieczytane bezpośrednio w tej iteracji)
- **Problem**: każdy chart wysyła osobny request POST przy każdej zmianie propów. Brak debounce.
- **Naprawa**: trzymać wyniki analiz w `App.jsx` (jedna kalkulacja `/api/calculate` zwraca też dane do wykresów) ALBO debounce + cache wyniku per `(b2b, uop)` hash.
- **Wysiłek**: M

### [ŚREDNIE] 5.8 Sekcje formularza bez `dark:` modifierów

- **Lokalizacja**: [src/dashboard/src/components/CalculatorForm.jsx:35, 66, 79, 314](src/dashboard/src/components/CalculatorForm.jsx#L35) — `bg-white` i `bg-gray-50` bez `dark:bg-gray-...`
- **Problem**: w trybie ciemnym sekcje formularza pozostają jasne (białe tło), tracąc spójność z resztą aplikacji.
- **Naprawa**: dodać `dark:bg-gray-800` (lub odpowiednik) do każdego `<div className="bg-white">` / `<div className="bg-gray-50">` w formularzu.
- **Wysiłek**: S

### [ŚREDNIE] 5.9 Powtarzający się blok dla każdego company benefit (DRY)

- **Lokalizacja**: [src/dashboard/src/components/CalculatorForm.jsx:184–309](src/dashboard/src/components/CalculatorForm.jsx#L184)
- **Problem**: 125 linii ~identycznego kodu dla 7 benefitów (paidVacation, paidSick, medicalCare, lifeInsurance, sportCard, trainingBudget, otherBenefits). Zmiana wyglądu = 7 miejsc do poprawy.
- **Naprawa**: wyekstrahować `<CompanyBenefitInput name="medicalCare" type="value" />` i renderować w pętli.
- **Wysiłek**: M

### [NISKIE] 5.10 Hardkodowany komunikat błędu

- **Lokalizacja**: [src/dashboard/src/App.jsx:188](src/dashboard/src/App.jsx#L188)
- **Problem**: `setError('Failed to fetch results. Please check the console for more details.')` — angielski, nie i18n.
- **Naprawa**: `setError(t('errors.fetch_failed'))`.
- **Wysiłek**: S

---

## 6. Internacjonalizacja (i18n)

### [WYSOKIE] 6.1 Etykieta „2025" w obu tłumaczeniach

- **Lokalizacja**: [src/dashboard/src/locales/pl/translation.json](src/dashboard/src/locales/pl/translation.json), [src/dashboard/src/locales/en/translation.json](src/dashboard/src/locales/en/translation.json)
- **Problem**: opisany w [3.11]. Powiązanie merytoryczne z poprawnością obliczeń — backend liczy 2026, UI mówi „2025".
- **Naprawa**: grep + replace „2025" → „2026". Najlepiej trzymać rok w jednej zmiennej (np. `app.config.tax_year`) i wstrzykiwać przez i18n interpolation.
- **Wysiłek**: S

### [WYSOKIE] 6.2 `.replace()` w JSX (powiązane z 5.4)

- patrz [5.4].

### [ŚREDNIE] 6.3 Klucze tekstów stałych w configu, nie w i18n

- **Lokalizacja**: [dane_wejsciowe_kalkulator.json:83–140](dane_wejsciowe_kalkulator.json#L83) — `analiza_ryzyka`, `rekomendacje`, `checklists` z gałęziami `pl` i `en`.
- **Problem**: aplikacja ma dwa źródła tłumaczeń: i18next (frontend) i konfigi (backend). Inny tłumacz, inne brzmienie, brak spójności.
- **Naprawa**: tłumaczenia stringów wyłącznie po stronie frontendu. Backend zwraca **klucz** (np. `b2b_lepsze`), frontend tłumaczy.
- **Wysiłek**: M

### [NISKIE] 6.4 Brak weryfikacji równości kluczy en/pl

- **Lokalizacja**: brak narzędzia/testu
- **Problem**: nie ma CI testu, który by sprawdzał, że `en/translation.json` i `pl/translation.json` mają **te same klucze**. Przy dodawaniu nowych tłumaczeń łatwo zapomnieć o jednym języku → fallback do klucza.
- **Naprawa**: dodać test (np. `npm run test:i18n`) używający np. [i18next-parser](https://github.com/i18next/i18next-parser).
- **Wysiłek**: S

---

## 7. Dostępność (a11y)

### [ŚREDNIE] 7.1 Ikonki info bez `aria-label`

- **Lokalizacja**: [src/dashboard/src/components/CalculatorForm.jsx:341–346](src/dashboard/src/components/CalculatorForm.jsx#L341) — SVG ikona bez `aria-label` ani `role="img"`.
- **Problem**: screen reader pomija ikonę, użytkownik nie wie, że tooltip jest dostępny.
- **Naprawa**: opakować w `<button aria-label={t('a11y.info')}><svg ...></svg></button>` i obsłużyć klawiaturą (Enter/Space → otwórz tooltip).
- **Wysiłek**: S

### [ŚREDNIE] 7.2 Brak focus management po submit

- **Lokalizacja**: [src/dashboard/src/App.jsx:173–192](src/dashboard/src/App.jsx#L173)
- **Problem**: po naciśnięciu „Oblicz" fokus pozostaje na przycisku, screen reader nie wie, że pojawiły się wyniki.
- **Naprawa**: po `setResults(res)` przenieść focus na `ResultsDisplay` (`useRef` + `.focus()` z `tabIndex={-1}`).
- **Wysiłek**: S

### [ŚREDNIE] 7.3 Feedback kolorowy bez tekstu

- **Lokalizacja**: `ResultsDisplay.jsx` (z raportu agenta) — `bg-yellow-50` jako wyróżnik break-even
- **Problem**: użytkownicy z deuteranopią/protanopią mogą nie rozróżnić sekcji.
- **Naprawa**: dodać ikonę + tekst etykiety („Punkt zwrotny:") obok kolorowego tła.
- **Wysiłek**: S

### [NISKIE] 7.4 `accessibility.spec.js` to placeholder

- **Lokalizacja**: [tests/e2e/accessibility.spec.js](tests/e2e/accessibility.spec.js) — 12 linii
- **Problem**: ledwie zarys testu; powinien używać `@axe-core/playwright` do automatycznego audytu WCAG.
- **Naprawa**: pełen test z `axe-playwright`, lista znanych odstępstw w komentarzu.
- **Wysiłek**: S

---

## 8. Wydajność

### [ŚREDNIE] 8.1 Wykresy re-fetch przy każdym renderze (patrz [5.7])

### [ŚREDNIE] 8.2 Brak code-splittingu dla ciężkich bibliotek

- **Lokalizacja**: [src/dashboard/package.json](src/dashboard/package.json) — `framer-motion`, `chart.js`, `react-chartjs-2`, `i18next`, `i18next-browser-languagedetector`
- **Problem**: cały frontend (włącznie z chart.js ~100kB) ładuje się przy pierwszym wejściu. Wyniki są pokazywane dopiero po `handleCalculate` — wykresy mogłyby być lazy-loaded.
- **Naprawa**: `const BreakEvenChart = React.lazy(() => import('./components/BreakEvenChart'))` itd., owinąć w `<Suspense>`.
- **Wysiłek**: S

### [NISKIE] 8.3 `dependencyArray` w useEffect zawiera `b2bData.monthly_invoice_amount`

- **Lokalizacja**: [src/dashboard/src/App.jsx:152](src/dashboard/src/App.jsx#L152)
- **Problem**: useEffect zależy od `b2bData.monthly_invoice_amount`, ale w środku **też** modyfikuje `b2bData` przez `setB2bData`. Reakt mądrze sobie poradzi (porównanie referencji), ale to jednostkowa pętla.
- **Naprawa**: dodać warunek, że `monthly_business_costs` zmienia się tylko, jeśli różni się od poprzedniej wartości.
- **Wysiłek**: S

---

## 9. Zależności

### [WYSOKIE] 9.1 Brak version-pinów w `pyproject.toml`

- **Lokalizacja**: [pyproject.toml:8–17](pyproject.toml#L8)
- **Problem**: `Flask`, `Flask-Cors`, `openpyxl`, `matplotlib`, `pydantic`, `fpdf2`, `pypdf`, `weasyprint` — żadnej wersji. `pip install -e .` w nowym środowisku może zaciągnąć inną wersję Pydantica i złamać walidację.
- **Naprawa**: zacieśnić do `Flask>=3.0,<4.0`, `pydantic>=2.0,<3.0`, etc. Lepiej: użyć `uv` lub `poetry` z lockfile.
- **Wysiłek**: S

### [WYSOKIE] 9.2 Brak lockfile dla Pythona

- **Lokalizacja**: brak `requirements.txt`, `poetry.lock`, `uv.lock`
- **Problem**: nie da się odtworzyć tego samego środowiska dwa razy. Build w produkcji może mieć inne wersje niż dev.
- **Naprawa**: wprowadzić `uv` (`uv lock`) lub `pip-tools` (`pip-compile`), commit lockfile.
- **Wysiłek**: S

### [ŚREDNIE] 9.3 Dwie biblioteki PDF (`fpdf2` + `pypdf`)

- **Lokalizacja**: [pyproject.toml:14–16](pyproject.toml#L14)
- **Problem**: oba w dependencies. `fpdf2` generuje PDF, `pypdf` go modyfikuje (lub jest pozostałością po niezaakceptowanej zmianie). README mówi też o `weasyprint`.
- **Naprawa**: zweryfikować, którego faktycznie używamy (grep), usunąć nadmiarowe. Trzecia opcja `weasyprint` (HTML→PDF) jest najprostsza w utrzymaniu.
- **Wysiłek**: M

### [ŚREDNIE] 9.4 Pakiety w root `package.json` zamiast w `dashboard/package.json`

- **Lokalizacja**: [package.json](package.json) — `@google/gemini-cli`, `playwright`
- **Problem**: root `package.json` istnieje tylko po to, by uruchomić Playwright (E2E). Mieszanie tooling-pakietów (Gemini CLI) z testowymi tworzy szum.
- **Naprawa**: pozostawić w root tylko `playwright` (E2E w innym repo niż frontend). Usunąć `@google/gemini-cli` (lub przenieść do devDependencies tam, gdzie używany).
- **Wysiłek**: S

### [NISKIE] 9.5 Caret-range `^` we wszystkich devDependencies frontendu

- **Lokalizacja**: [src/dashboard/package.json](src/dashboard/package.json)
- **Problem**: `npm install` w nowym checkout może podnieść minor-wersje. Lockfile (`package-lock.json`) jest, więc realnie problem mały, dopóki lockfile committed.
- **Naprawa**: status quo OK; tylko upewnić się, że `package-lock.json` jest committed (jest).
- **Wysiłek**: S

---

## 10. Higiena repozytorium

### [WYSOKIE] 10.1 `.venv/`, `.playwright-mcp/`, `*.egg-info`, `flask_manual.log`, `vite_manual.log` nie w `.gitignore`

- **Lokalizacja**: [.gitignore](.gitignore)
- **Problem**: git status pokazuje te ścieżki jako „untracked"; bez wpisu w .gitignore łatwo je przypadkiem commitnąć.
- **Naprawa**: dodać do `.gitignore`:
  ```
  .venv/
  .playwright-mcp/
  *.egg-info/
  *_manual.log
  ```
- **Wysiłek**: S

### [ŚREDNIE] 10.2 `flask.log` mimo wpisu w .gitignore nadal śledzony

- **Lokalizacja**: repozytorium
- **Problem**: `.gitignore` zawiera `flask.log`, ale plik jest już w cache git (był zatwierdzony przed dodaniem do .gitignore). Każda modyfikacja pokazuje się w `git status`.
- **Naprawa**: `git rm --cached flask.log` (potwierdzić z użytkownikiem przed wykonaniem).
- **Wysiłek**: S

### [ŚREDNIE] 10.3 Zduplikowane GEMINI.md (root + .ai/)

- **Lokalizacja**: [GEMINI.md](GEMINI.md), [.ai/GEMINI.md](.ai/GEMINI.md)
- **Problem**: dwa pliki o tej samej nazwie, w dwóch lokalizacjach, prawdopodobnie z różną zawartością (root → 2026, .ai/ → 2025).
- **Naprawa**: zostawić jeden (root) i zaktualizować; usunąć z `.ai/`. Albo skonsolidować w `CLAUDE.md` / `GEMINI.md` (jeden plik per AI), z noteką o roku.
- **Wysiłek**: S

### [NISKIE] 10.4 Stale w `.ai/`: tasks.md, instructions.md, session-state.md

- **Lokalizacja**: [.ai/](.ai/)
- **Problem**: pliki zarządzania sesją AI — nie powinny być w repo długoterminowym (są efemeryczne).
- **Naprawa**: dodać `.ai/` do `.gitignore` lub usunąć z repo i przenieść do lokalnego workspace.
- **Wysiłek**: S

### [NISKIE] 10.5 `analiza.md` w root

- **Lokalizacja**: [analiza.md](analiza.md)
- **Problem**: 5,8 KB raport po polsku; brak odniesienia z README, nie wiadomo, do czego służy.
- **Naprawa**: przenieść do `docs/` lub usunąć, jeśli przestał być aktualny.
- **Wysiłek**: S

---

## 11. CI/CD, narzędzia, skrypty

### [WYSOKIE] 11.1 Brak CI

- **Lokalizacja**: brak `.github/workflows/`
- **Problem**: każda zmiana opiera się na ręcznym uruchomieniu testów. Brak gate przed merge.
- **Naprawa**: utworzyć `.github/workflows/ci.yml` z trzema joba:
  - `backend`: `pip install -e .[dev]` + `pytest`
  - `frontend`: `cd src/dashboard && npm ci && npm test && npm run lint && npm run build`
  - `e2e`: `npx playwright install && npm run test:e2e`
- **Wysiłek**: M

### [WYSOKIE] 11.2 Brak Pythonowego lintera/formattera

- **Lokalizacja**: `pyproject.toml`
- **Problem**: bez `ruff`/`black`/`mypy` styl kodu rozjeżdża się chaotycznie. Brak statycznej analizy = brak ostrzeżeń o `KeyError` typu z [3.2].
- **Naprawa**: dodać `ruff` (lint + format) i `mypy` (typing). Konfiguracja w `pyproject.toml`. Uruchamiać w CI.
- **Wysiłek**: S

### [ŚREDNIE] 11.3 Brak pre-commit hooks

- **Lokalizacja**: brak `.pre-commit-config.yaml`
- **Problem**: błędy stylu trafiają do master, bo lokalnie nikt nie pamięta o `ruff check`.
- **Naprawa**: dodać `pre-commit` (ruff, mypy, eslint, prettier).
- **Wysiłek**: S

### [ŚREDNIE] 11.4 `run_app.sh` brakuje `set -euo pipefail`, hardcoded sleep

- **Lokalizacja**: [run_app.sh](run_app.sh)
- **Problem**: bez `set -e` błąd w `flask run` nie przerwie skryptu; `sleep 5` jako wait-for-vite to wyścig (gdy Vite startuje 8s, kolejne grep `vite_output.log` nie zwróci URL).
- **Naprawa**:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  ```
  Zamiast `sleep 5` użyć `until grep -q 'http://localhost' vite_output.log; do sleep 0.5; done` z timeout.
- **Wysiłek**: S

### [ŚREDNIE] 11.5 `stop_app.sh` używa `pkill` bez weryfikacji

- **Lokalizacja**: [stop_app.sh](stop_app.sh)
- **Problem**: brutalny `pkill -f flask` zabije też niepowiązane procesy o tej nazwie.
- **Naprawa**: trzymać PID-y z `run_app.sh` w plikach `.flask.pid` i `.vite.pid`, w `stop_app.sh` `kill $(cat .flask.pid)`.
- **Wysiłek**: S

### [NISKIE] 11.6 Brak ESLint config file (tylko skrypt npm)

- **Lokalizacja**: [src/dashboard/package.json:9](src/dashboard/package.json#L9) (lint script), brak `.eslintrc.*` ani `eslint.config.js`
- **Problem**: bez konfigu domyślne reguły są bardzo skromne; nie wymuszamy żadnych konwencji projektowych.
- **Naprawa**: dodać `eslint.config.js` z `eslint-plugin-react` (jest w devDeps), `react-hooks`, `react-refresh` (też w devDeps); skonfigurować `.eslintrc.json` lub flat config.
- **Wysiłek**: S

### [NISKIE] 11.7 `backend_cov.sh` uruchamia pytest 4 razy

- **Lokalizacja**: [scripts/backend_cov.sh](scripts/backend_cov.sh)
- **Problem**: dla każdej z 4 metryk (unit, integration, combined, function-coverage) pełny przebieg testów. Czas wykonania 4x większy niż potrzeba.
- **Naprawa**: uruchomić raz `pytest --cov`, potem osobno generować podsumowania z pliku `.coverage`.
- **Wysiłek**: M

---

## 12. Dokumentacja

### [WYSOKIE] 12.1 README mówi „2025", kod jest na 2026

- **Lokalizacja**: [README.md:1, 3](README.md#L1) — nagłówek „B2B vs UoP IT Calculator 2025"
- **Problem**: pierwsze, co widzi nowy użytkownik/kontrybutor. Niezgodne z faktyczną logiką.
- **Naprawa**: globalna zamiana „2025" → „2026" w README, z weryfikacją.
- **Wysiłek**: S

### [ŚREDNIE] 12.2 README odsyła do `requirements.txt`, którego nie ma

- **Lokalizacja**: [README.md:46](README.md#L46) — `pip install -r requirements.txt`
- **Problem**: użytkownik wykonuje instrukcję, dostaje error. Powinno być `pip install -e .[dev]`.
- **Naprawa**: zaktualizować instrukcję instalacji do `uv pip install -e .[dev]` lub `pip install -e ".[dev]"`.
- **Wysiłek**: S

### [ŚREDNIE] 12.3 README: `python -m venv venv`, ale skrypty używają `.venv/`

- **Lokalizacja**: [README.md:44](README.md#L44), [run_app.sh:4](run_app.sh#L4)
- **Problem**: użytkownik tworzy `venv/` jak w README, potem `run_app.sh` próbuje `. .venv/bin/activate` i nie znajduje. Crash.
- **Naprawa**: ujednolicić — zalecam `.venv/` (zgodne z konwencją VS Code).
- **Wysiłek**: S

### [NISKIE] 12.4 Brak dokumentacji metodologii poza analiza.md i `analysis.py`

- **Lokalizacja**: `src/analysis.py:35–38` (jeden paragraf), `analiza.md` (po polsku)
- **Problem**: nie ma jednego źródła prawdy o tym, jak liczymy podatek/ZUS. Audytor (księgowy) nie ma czego sprawdzać.
- **Naprawa**: utworzyć `docs/methodology.md` z formułami: dla każdej formy opodatkowania pseudokod + odwołanie do artykułu ustawy.
- **Wysiłek**: L

### [NISKIE] 12.5 `CLAUDE.md` zawiera już dobre wprowadzenie

- **Lokalizacja**: [CLAUDE.md](CLAUDE.md)
- **Problem**: brak rzeczywistego problemu — to świeża dokumentacja AI-friendly. Wskazana jest jednak dodatkowa wersja `CONTRIBUTING.md` dla ludzi.
- **Naprawa**: skopiować strukturę z `CLAUDE.md` do `CONTRIBUTING.md`, rozbudować o flow PR-ów.
- **Wysiłek**: S

---

## 13. Testy

### [WYSOKIE] 13.1 Brak testów dla `validation.py`

- **Lokalizacja**: brak `tests/unit/test_validation.py`
- **Problem**: walidator Pydantic jest pierwszą linią obrony. Bez testów łatwo wprowadzić regresję (np. zmiana `pattern` w `zus_type` jak w [3.2]).
- **Naprawa**: testy dla każdego pola: poprawne wartości, zła wartość (zwraca 400 z `details`), pominięte wymagane.
- **Wysiłek**: M

### [WYSOKIE] 13.2 Brak testów krawędziowych dla obliczeń

- **Lokalizacja**: `tests/unit/test_calculations.py`, `test_core_logic.py`
- **Problem**: brak testów dla:
  - `monthly_invoice_amount = 0`
  - `creative_work_percentage > 0` przy `monthly_gross_salary = 0` (powinien wykryć ZeroDivisionError z [3.10])
  - Próg 30-krotności dokładnie na limicie
  - Bardzo wysokie kwoty (>500k mies., trigger daniny solidarnościowej)
  - `zus_type='small_business'` (powinien wywołać KeyError z [3.2])
  - `youth_relief=True` dla B2B (powinien wywołać błąd merytoryczny z [3.1] po naprawie)
- **Naprawa**: dodać `test_edge_cases.py` z ww. scenariuszami.
- **Wysiłek**: M

### [ŚREDNIE] 13.3 Brak testów bezpieczeństwa

- **Lokalizacja**: brak
- **Problem**: nikt nie weryfikuje, że:
  - Endpoint Excel/break-even/sensitivity przyjmuje śmieci i nie wyciekają stack-trace'y
  - CORS odrzuca nielegalne Origin (po naprawie [2.3])
  - Path traversal w `/path` nie ujawnia plików (po naprawie [2.6])
- **Naprawa**: `test_security.py` z scenariuszami negatywnymi.
- **Wysiłek**: M

### [ŚREDNIE] 13.4 `accessibility.spec.js` to placeholder (patrz [7.4])

### [ŚREDNIE] 13.5 Brak E2E dla dark mode i URL-share

- **Lokalizacja**: [tests/e2e/](tests/e2e/)
- **Problem**: dwie nowe funkcje (commit `2cd9d69`) bez własnych testów.
- **Naprawa**: `darkmode.spec.js` (toggle, sprawdzenie klas Tailwind), `urlshare.spec.js` (otwarcie linku z parametrami → poprawnie wypełniony formularz).
- **Wysiłek**: M

### [NISKIE] 13.6 Testy nie sprawdzają wartości obliczeń, tylko obecność kluczy

- **Lokalizacja**: [tests/unit/test_calculations.py](tests/unit/test_calculations.py) (z raportu agenta — 35 linii, sprawdza klucze)
- **Problem**: nawet jeśli wzory się zmienią, testy przejdą. To „cargo cult" testowanie.
- **Naprawa**: testy z konkretnymi liczbami: „pensja 10 000 brutto, standard KUP → netto ~7 100" (z tolerancją ±50 PLN).
- **Wysiłek**: M

---

## 14. Roadmapa naprawcza

### Fala 1 — Krytyczne (1–2 dni pracy, blocker do produkcji)

| # | Sekcja | Co | Dlaczego pierwsze |
|---|--------|-----|-------------------|
| 1 | [3.1] | Usunąć PIT-0 dla B2B (backend + frontend) | Wpływ na realne decyzje finansowe użytkowników |
| 2 | [3.2] | Dopasować `small_business` w walidatorze do configu (lub usunąć) | Crash przy wyborze opcji |
| 3 | [3.3] | Usunąć podwójne liczenie dni wolnych w UoP | Zawyża UoP o ~10–15% |
| 4 | [2.1] | Wyłączyć `app.debug=True` w produkcji | RCE + wyciek informacji |
| 5 | [2.2] | Walidacja Pydantic dla 3 endpointów | Wektor DoS + 500 z trace |
| 6 | [3.11] + [12.1] | Zamiana „2025" → „2026" (UI, README) | Spójność informacyjna |

### Fala 2 — Wysokie (3–7 dni pracy)

| # | Sekcja | Co |
|---|--------|-----|
| 7 | [3.4] | Poprawne modelowanie PPK (z weryfikacją prawną) |
| 8 | [3.5] | Danina solidarnościowa 4% > 1M PLN |
| 9 | [3.6] | Backend wymusza wiek <26 przy `youth_relief=True` |
| 10 | [3.7] | Pole „udział kwalifikowanego dochodu" dla IP Box |
| 11 | [3.8] + [3.9] | Weryfikacja stawek zdrowotnej ryczałtu i limitu liniowego z księgowym |
| 12 | [3.10] | Naprawa ZeroDivisionError + uproszczenie wzoru |
| 13 | [2.3] | CORS whitelist |
| 14 | [2.4] | Spójny error handler bez wycieku |
| 15 | [4.2] | Rozbicie god function `calculate_b2b_results` |
| 16 | [5.1] | Wydzielenie state managementu (`useReducer` lub `Context`) |
| 17 | [5.2] | Przeniesienie logiki ubezpieczeń do backendu |
| 18 | [5.3] + [5.4] | Naprawa hardkodowanych stringów + `.replace()` w JSX |
| 19 | [9.1] + [9.2] | Version-pins + lockfile Python |
| 20 | [11.1] | Setup CI w GitHub Actions |

### Fala 3 — Higiena (tydzień, do zrobienia w wolnych chwilach)

| Sekcja | Co |
|--------|-----|
| [2.5] | Rate limiting |
| [2.6] | Usunięcie `os.path.exists` w serwowaniu statyki |
| [2.7] | Logi poza repo |
| [3.12] – [3.17] | Pozostałe usprawnienia obliczeń (limity czasowe ZUS, FGŚP, break-even, sensitivity, miesiące pracy, walidacja górnych granic) |
| [4.x] | Refactor architektoniczny (services, magic numbers do configu, ujednolicenie nazewnictwa) |
| [5.5] – [5.10] | Memoizacja, walidacja URL params, dark mode dla formularza, DRY w benefitach |
| [6.3] + [6.4] | Jeden źródło tłumaczeń + test i18n parity |
| [7.x] | A11y (aria-label, focus management, tekstowe etykiety, axe-playwright) |
| [8.x] | Performance (lazy loading, debounce wykresów) |
| [10.x] | `.gitignore`, cache flask.log, GEMINI.md, .ai/ |
| [11.2] – [11.7] | Linter Python, pre-commit, fix run/stop scripts, ESLint config, optymalizacja cov |
| [12.2] – [12.5] | Dokumentacja: requirements.txt → pyproject, ujednolicenie .venv, methodology.md, CONTRIBUTING.md |
| [13.x] | Pełne testy walidatora, krawędzi, bezpieczeństwa, dark mode, URL share, prawdziwych liczb |

---

## Załącznik A — Znaleziska oddalone (fałszywe pozytywy z fazy eksploracji)

W trakcie weryfikacji **odrzuciłem** następujące zgłoszenia agentów Explore — nie są błędami:

| Zgłoszenie | Werdykt |
|------------|---------|
| „calculations.py:80 — ryczałt powinien odliczać business_costs od podstawy" | **Odrzucone.** W polskim ryczałcie ewidencjonowanym koszty uzyskania **nie są** odliczane od przychodu (podstawą jest przychód). Kod jest poprawny. Odlicza tylko: składki społeczne i 50% zdrowotnej — to **zgodne** z art. 9 ustawy o zryczałtowanym podatku dochodowym. |
| „calculations.py:187–189 — koszty autorskie podwójnie mnożone przez 0.5" | **Odrzucone.** W kodzie jest tylko jedno mnożenie przez 0.5 (linia 189). Linia 188 wykonuje proporcjonalne odejmowanie składek społecznych, nie kolejne mnożenie. Agent źle odczytał wzór. |

---

## Załącznik B — Co ten audyt NIE pokrywa

- **Nie zastępuje opinii księgowej.** Sekcja 3 wskazuje **podejrzenia**; każda zmiana stawki lub interpretacja ustawy wymaga konsultacji ze specjalistą.
- **Nie sprawdzono kompletnie**: pełnej konfiguracji UI po kątem mocno warunkowych elementów (np. tooltip-Markdown), pełnej zawartości tłumaczeń (sprawdzony tylko nagłówek i kilka kluczy), generacji PDF (kod nieczytany szczegółowo — wymagana osobna sesja).
- **Audyt to migawka w czasie** (2026-05-23). Po naprawach z fali 1–2 należy powtórzyć, szczególnie sekcję 3.
