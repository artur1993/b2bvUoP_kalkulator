# AUDYT UZUPELNIAJACY - Kalkulator B2B vs UoP

**Cel dokumentu**: uzupelnienie `AUDYT.md` o dodatkowe znaleziska wykryte podczas przegladu aktualnego kodu.
**Zakres**: tylko obserwacje lokalne z repozytorium. Nie wykonywano dodatkowego researchu zewnetrznego ani weryfikacji stawek prawno-podatkowych.
**Status**: addendum do raportu Claude'a, bez nadpisywania `AUDYT.md`.

---

## 1. Dodatkowe Znaleziska

### [WYSOKIE] 1.1 Eksport PDF jest deklarowany, ale nie istnieje w aktualnym kodzie

- **Lokalizacja**: `README.md`, `src/app.py`, `src/dashboard/src/App.jsx`, `src/dashboard/src/components/ResultsDisplay.jsx`, `src/dashboard/src/locales/*/translation.json`, `tests/e2e/calculator.spec.js`
- **Problem**: dokumentacja i tlumaczenia deklaruja eksport PDF podstawowy oraz zaawansowany, ale aktualny backend udostepnia tylko `/api/export/excel`, a aktualny UI pokazuje tylko przycisk eksportu Excel. Test E2E dla PDF jest pominiety (`test.skip`).
- **Dlaczego wazne**: uzytkownik i kontrybutor widza funkcje, ktore nie sa realnie dostepne. To obniza wiarygodnosc aplikacji i moze ukrywac porzucony kod lub niedokonczona migracje.
- **Naprawa**: wybrac jedna sciezke: zaimplementowac endpointy i przyciski PDF albo usunac deklaracje PDF z README, tlumaczen i testow. Jesli PDF ma wrocic, dodac test integracyjny API oraz E2E pobrania pliku.
- **Wysilek**: M

### [WYSOKIE] 1.2 `equalizePension` zwraca dane z backendu, ale UI ich nie pokazuje

- **Lokalizacja**: `src/app.py`, `src/pension_calculator.py`, `src/dashboard/src/App.jsx`, `src/dashboard/src/components/ResultsDisplay.jsx`
- **Problem**: backend dodaje `pension_details` do odpowiedzi, gdy `b2b.equalizePension` jest wlaczone. Aktualny `ResultsDisplay` nie renderuje jednak tej sekcji, a `App.jsx` nie wykorzystuje `invoice_increase` do ponownej kalkulacji ani do jasnego pokazania wymaganej podwyzki faktury.
- **Dlaczego wazne**: checkbox obiecuje uzytkownikowi konkretna funkcje biznesowa, ale wynik tej funkcji nie jest widoczny w interfejsie. Uzytkownik moze uznac, ze emerytura zostala uwzgledniona w porownaniu, mimo ze UI tego nie komunikuje.
- **Naprawa**: albo pokazac sekcje emerytalna w wynikach, albo czasowo ukryc checkbox. Docelowo rozdzielic: "wymagana miesieczna oszczednosc" i "wymagana podwyzka faktury B2B" oraz jasno wskazac, czy kwota zostala doliczona do wyniku.
- **Wysilek**: S/M

### [SREDNIE] 1.3 Benefit UoP `life_insurance` jest widoczny w formularzu, ale nie ma w konfiguracji

- **Lokalizacja**: `src/dashboard/src/components/CalculatorForm.jsx`, `src/calculations.py`, `dane_wejsciowe_kalkulator.json`
- **Problem**: formularz UoP pozwala wybrac `life_insurance`, ale `dane_wejsciowe_kalkulator.json` nie zawiera takiego klucza w sekcji `benefits`. Logika w `calculate_uop_results` sumuje tylko benefity obecne w configu, wiec wybranie ubezpieczenia na zycie nie zmienia wyniku.
- **Dlaczego wazne**: widoczna kontrolka formularza jest funkcjonalnie martwa. To moze prowadzic do blednych porownan, jesli uzytkownik zaklada, ze benefit zostal wliczony.
- **Naprawa**: dodac `life_insurance` do configu z udokumentowana wartoscia albo usunac opcje z UI. Dodatkowo dodac test, ze kazdy benefit widoczny w formularzu ma odpowiadajacy wpis w configu lub jest jawnie oznaczony jako informacyjny.
- **Wysilek**: S

### [SREDNIE] 1.4 Braki i18n widoczne w aktualnym UI i logach testow

- **Lokalizacja**: `src/dashboard/src/locales/en/translation.json`, `src/dashboard/src/locales/pl/translation.json`, `src/dashboard/src/components/*`
- **Problem**: komponenty uzywaja kluczy, ktorych brakuje w tlumaczeniach albo sa niespojnie umieszczone. Przyklady: `form.age`, `form.equalize_pension` w EN, `analysis.summary_title`, `analysis.risk_title`, globalne `loading`, `no_data`, a takze brakujace etykiety `sensitivity.monthly_business_costs` i `sensitivity.stoppage_months`.
- **Dlaczego wazne**: i18next wyswietla fallbacki/klucze zamiast tekstow. Testy frontendu sa zielone, ale ich logi ujawniaja `missingKey`, wiec obecny test suite przepuszcza realne usterki UX.
- **Naprawa**: uzupelnic brakujace klucze, ujednolicic nazwy (`results.loading` vs `loading`) i dodac test parity EN/PL oraz test, ktory traktuje `missingKey` jako blad.
- **Wysilek**: S

### [SREDNIE] 1.5 Konfigurator ubezpieczen zawiera polskie teksty zaszyte w danych

- **Lokalizacja**: `src/dashboard/src/data/insuranceOptions.js`, `src/dashboard/src/components/InsuranceConfigurator.jsx`, `src/dashboard/src/i18n.js`
- **Problem**: `insuranceOptions.js` zawiera polskie nazwy modulow, tooltipy, szczegoly pokrycia i porownania z UoP. Jednoczesnie `InsuranceConfigurator` probuje tlumaczyc tooltip przez `t(module.tooltip, { ns: 'insurance' })`, mimo ze namespace `insurance` nie jest zarejestrowany w `i18n.js`.
- **Dlaczego wazne**: angielska wersja UI bedzie miala polskie fragmenty, a i18n generuje brakujace klucze. To rowniez utrudnia pozniejsza aktualizacje cen/opisow ubezpieczen.
- **Naprawa**: przeniesc teksty do `translation.json` albo zmienic model danych tak, by przechowywal klucze tlumaczen, a nie gotowe zdania. Dla cen i mnoznikow zostawic dane liczbowe w osobnym configu.
- **Wysilek**: M

### [SREDNIE] 1.6 Metodologia wspomina VAT i koszty pracodawcy, ale model ich nie liczy

- **Lokalizacja**: `README.md`, `src/analysis.py`, `src/calculations.py`, `src/validation.py`
- **Problem**: opis metodologii mowi o VAT oraz "all employer costs", ale model B2B nie przyjmuje realnego statusu VAT i nie liczy VAT, a model UoP liczy glownie perspektywe pracownika, nie pelny koszt pracodawcy.
- **Dlaczego wazne**: rozjazd miedzy deklarowana metodologia a faktycznym modelem obliczen moze prowadzic do blednej interpretacji wyniku. Jesli kalkulator ma porownywac perspektywe pracownika, powinien to powiedziec wprost; jesli ma porownywac koszt firmy, wymaga dodatkowego modelu.
- **Naprawa**: doprecyzowac zakres kalkulatora. Albo usunac VAT/koszty pracodawcy z metodologii, albo dodac jawne pola i obliczenia dla tych elementow.
- **Wysilek**: M

### [NISKIE] 1.7 Artefakty coverage i egg-info sa obecne w repo/statusie, co moze mylic audyt

- **Lokalizacja**: `src/dashboard/coverage/`, `src/b2b_vs_uop_calculator.egg-info/`, `git status`
- **Problem**: w repo sa artefakty wygenerowane lub nie sledzone, a stary coverage zawiera snapshoty kodu rozniace sie od aktualnych plikow zrodlowych. Grep bez filtrowania coverage moze dawac falszywe tropy.
- **Dlaczego wazne**: audytor moze analizowac historyczny kod z coverage zamiast aktualnego zrodla.
- **Naprawa**: usunac artefakty z indeksu, dopelnic `.gitignore` i w audytach filtrowac `src/dashboard/coverage/**`.
- **Wysilek**: S

---

## 2. Rzeczy Do Pozniejszego Sprawdzenia Pod Katem Aktualnosci

Te punkty nalezy zebrac i zweryfikowac pozniej, z data sprawdzenia i linkami do zrodel. Na tym etapie nie wykonano researchu zewnetrznego.

### Podatki PIT

- Aktualne progi skali podatkowej, kwota wolna i kwota zmniejszajaca podatek.
- Aktualne zasady podatku liniowego, w tym traktowanie skladki zdrowotnej.
- Aktualna stawka ryczaltu dla uslug IT oraz warunki jej zastosowania.
- Aktualne zasady IP Box: kwalifikowany dochod, ewidencja, wskaznik nexus, udzial dochodu kwalifikowanego.
- Danina solidarnosciowa: prog, podstawa, stawka i zakres dochodow.
- Ulga dla mlodych: limit, zakres przychodow i jednoznaczne potwierdzenie braku/zastosowania dla B2B.
- KUP UoP: standardowe, podwyzszone, 50% autorskie, limity roczne oraz zachowanie po przekroczeniu limitu.

### ZUS I Skladka Zdrowotna B2B

- Pelny ZUS przedsiebiorcy: podstawa i aktualne kwoty skladek.
- Preferencyjny ZUS: warunki, czas trwania i aktualne kwoty.
- Ulga na start: zakres skladek, czas trwania i wplyw na zdrowotna.
- Maly ZUS Plus: czy ma byc wspierany oraz jakie pola wejsciowe sa wymagane.
- Skladka zdrowotna dla skali podatkowej.
- Skladka zdrowotna dla podatku liniowego.
- Skladka zdrowotna dla ryczaltu, w tym progi przychodu i kwoty miesieczne.
- Mozliwosc odliczania lub zaliczania skladki zdrowotnej do kosztow/przychodu w zaleznosci od formy opodatkowania.

### UoP

- Aktualne stawki skladek pracownika: emerytalna, rentowa, chorobowa, zdrowotna.
- Limit 30-krotnosci ZUS i sposob liczenia miesiaca przekroczenia.
- PPK: wplata pracownika, wplata pracodawcy, opodatkowanie i sposob prezentacji jako benefit.
- Chorobowe i urlopy: jak traktowac je w modelu wartosci UoP, zeby nie dublowac wynagrodzenia.
- Benefity UoP: aktualne wartosci rynkowe i podatkowe traktowanie opieki medycznej, sportu, szkolen, ubezpieczenia na zycie i sprzetu.

### B2B I Kontrakt

- VAT: czy kalkulator ma jawnie pomijac VAT, czy modelowac fakture netto/brutto i status VAT.
- Koszty firmowe: ktore koszty sa podatkowo rozpoznawalne dla skali, liniowego i ryczaltu.
- Przestoje, urlop i choroba: aktualne zalozenia liczby dni roboczych oraz sposob wyliczania stawki dziennej.
- Ubezpieczenia B2B: aktualne ceny rynkowe i sens porownania z ochrona na UoP.
- Emerytura: limity IKE/IKZE, wiek emerytalny, zalozenia waloryzacji, okres oszczedzania i sposob liczenia luki emerytalnej.

### Zrodla Do Zebrania Pozniej

- ZUS.
- Ministerstwo Finansow i podatki.gov.pl.
- GUS.
- Dziennik Ustaw.
- Panstwowa Inspekcja Pracy / gov.pl dla minimalnego wynagrodzenia i prawa pracy.
- Konsultacja ksiegowa lub podatkowa dla interpretacji IP Box, ryczaltu, PPK i skladki zdrowotnej.

---

## 3. Proponowany Test Plan Dla Tych Usterek

- Dodać test parity i18n: `en` i `pl` maja identyczny zestaw kluczy.
- Dodać test renderowania glownych komponentow bez `missingKey` z i18next.
- Dodać test mapowania benefitow: kazdy benefit widoczny w UI ma odpowiadajacy wpis w configu albo jest jawnie informacyjny.
- Dodać test `equalizePension`: dane emerytalne sa widoczne w UI albo checkbox jest ukryty/wylaczony.
- Dodać test spojnosci eksportow: README, UI i API deklaruja tylko funkcje faktycznie dostepne.
- Dodać test dokumentacyjny/metodologiczny: jesli metodologia wspomina VAT lub koszt pracodawcy, istnieja odpowiadajace pola i obliczenia albo jawna adnotacja o pominieciu.

---

## 4. Wynik Lokalnej Weryfikacji

- `npm test -- --run` w `src/dashboard`: 62 testy przeszly.
- `/home/artur/.local/bin/uv run pytest -q`: 51 testow przeszlo.
- `pytest -q` bezposrednio nie jest dostepny w shellu (`pytest: command not found`).
- W trakcie uruchomienia backendowych testow przez `uv` powstal lokalny `uv.lock`; nie jest to zmiana kodu aplikacji, ale nalezy zdecydowac, czy lockfile ma byc commitowany.

