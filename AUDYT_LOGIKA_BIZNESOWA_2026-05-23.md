# Audyt Logiki Biznesowej - Stan Na 2026-05-23

## Zakres

Ten dokument jest osobnym przegladem aktualnosci logiki biznesowej kalkulatora B2B vs UoP. Nie nadpisuje `AUDYT.md` ani `AUDYT_UZUPELNIENIE.md` i nie zaklada zmian w kodzie aplikacji.

Porownanie obejmuje wartosci i zalozenia znalezione w:

- `dane_wejsciowe_kalkulator.json`
- `src/calculations.py`
- `AUDYT.md`
- `AUDYT_UZUPELNIENIE.md`

Źrodla uzyte do weryfikacji sa oficjalne albo branzowo-oficjalne: ZUS, podatki.gov.pl, KNF, gov.pl oraz oficjalny portal PPK MojePPK.pl.

## Najwazniejsze Rozjazdy

- **BŁĄD:** skladka zdrowotna na ryczalcie w konfiguracji jest nieaktualna dla 2026 r. Aplikacja ma `432,54 / 720,90 / 1 297,62`, a ZUS podaje `498,35 / 830,58 / 1 495,04`.
- **BŁĄD / uproszczenie:** minimalna zdrowotna dla skali, liniowego i IP Box ma dwie kwoty w roku skladkowym 2026: `314,96` za styczen 2026 oraz `432,54` od lutego 2026 do stycznia 2027. Kod uzywa jednej wartosci `432,54` dla calego roku.
- **BŁĄD:** ulga dla mlodych jest stosowana w kalkulacji B2B, chociaz oficjalny zakres ulgi nie obejmuje przychodow z dzialalnosci gospodarczej.
- **BŁĄD:** IP Box jest liczony jak `5%` calej podstawy, bez wydzielenia kwalifikowanego dochodu i bez wskaznika nexus.
- **BŁĄD:** PPK jako benefit UoP jest modelowany jako `2%` brutto. To odpowiada podstawowej wplacie pracownika, nie pracodawcy; podstawowa wplata pracodawcy wynosi `1,5%` i stanowi przychod pracownika.
- **OK:** skala PIT, prog `120 000`, kwota zmniejszajaca `3 600`, spoleczne ZUS 2026 oraz limity IKE/IKZE wygladaja zgodnie z oficjalnymi zrodlami.
- **WYMAGA DECYZJI:** VAT i koszty pracodawcy sa deklarowane w metodologii, ale nie sa realnie modelowane. Trzeba zdecydowac, czy aplikacja ma je liczyc, czy jawnie oznaczyc jako poza zakresem.

## Tabela Kontrolna

| Obszar | Obecnie w aplikacji | Źrodlo / stan aktualny | Status | Rekomendacja |
| --- | --- | --- | --- | --- |
| Skala PIT | `12% / 32%`, prog `120 000`, kwota zmniejszajaca `3 600`, kwota wolna `30 000` | podatki.gov.pl potwierdza skale od 2022 r.: do `120 000` podatek `12% minus 3 600`, powyzej `10 800 + 32%` nadwyzki. Źrodlo: https://www.podatki.gov.pl/podatki-osobiste/pit/stawki-i-limity/ | OK | Zostawic wartosci. Dodac test regresyjny na prog `120 000` i kwote zmniejszajaca. |
| Podatek liniowy | `19%` | podatki.gov.pl wymienia `19%` jako stawke dla podatku liniowego w kontekstach PIT/IP Box i odliczenia zdrowotnej. Źrodla: https://www.podatki.gov.pl/poradniki-i-informatory/ip-box-rozliczenie-dochodow-z-kwalifikowanych-praw-wlasnosci-intelektualnej-pit/ oraz https://www.podatki.gov.pl/ulgi-i-odliczenia/odliczenie-skladek-na-ubezpieczenie-zdrowotne-pit/ | OK | Zostawic stawke. Zweryfikowac tylko szczegoly odliczen zdrowotnych przy implementacji poprawek. |
| ZUS spoleczny pelny 2026 | Podstawa `5 652`; emerytalna `1 103,27`, rentowa `452,16`, wypadkowa `94,39`, chorobowa `138,47`, FP `138,47` | ZUS podaje te same wartosci dla stycznia-grudnia 2026. Źrodlo: https://www.zus.pl/baza-wiedzy/skladki-wskazniki-odsetki/skladki/wysokosc-skladek-na-ubezpieczenia-spoleczne | OK | Zostawic wartosci. Dobrze byloby opisac, ze wypadkowa zalezy od stopy procentowej i tu przyjeto `1,67%`. |
| ZUS preferencyjny 2026 | Podstawa `1 441,80`; emerytalna `281,44`, rentowa `115,34`, wypadkowa `24,08`, chorobowa `35,32` | ZUS podaje te same wartosci dla stycznia-grudnia 2026. Źrodlo: https://www.zus.pl/baza-wiedzy/skladki-wskazniki-odsetki/skladki/wysokosc-skladek-na-ubezpieczenia-spoleczne | OK | Zostawic wartosci. |
| Limit 30-krotnosci UoP | `282 600` | ZUS podaje maksymalna roczna podstawe wymiaru skladek emerytalnych i rentowych w 2026 r. `282 600`. Źrodlo: https://www.zus.pl/baza-wiedzy/skladki-wskazniki-odsetki/skladki/wysokosc-skladek-na-ubezpieczenia-spoleczne | OK | Zostawic wartosc. Dodac przypadki testowe przekroczenia limitu. |
| Zdrowotna B2B - ryczalt | Progi `60 000` i `300 000`; skladki `432,54`, `720,90`, `1 297,62` | ZUS dla 2026 r. podaje `498,35` do `60 000`, `830,58` powyzej `60 000` do `300 000`, `1 495,04` powyzej `300 000`. Źrodlo: https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r. | BŁĄD | Zmienic config ryczaltu na `498.35`, `830.58`, `1495.04`. Dodac testy graniczne dla przychodow `60 000` i `300 000`. |
| Zdrowotna B2B - skala/liniowy/IP Box minimum | Jedna wartosc `minimum_health_contribution: 432.54`, uzywana w calym roku | ZUS podaje minimum `314,96` za styczen 2026 oraz `432,54` za miesiace od lutego 2026 do stycznia 2027. Źrodlo: https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r. | BŁĄD | Model powinien uwzglednic miesiace albo jasno przyjac uproszczenie roczne. Dla rocznej kalkulacji poprawniejsza wartosc minimalna to suma `314,96 + 11 * 432,54`, jezeli liczony jest rok kalendarzowy 2026. |
| Odliczenie zdrowotnej - liniowy | Limit `14 100` w configu | podatki.gov.pl potwierdza limit `14 100 zl` dla 2026 r. Źrodlo: https://www.podatki.gov.pl/ulgi-i-odliczenia/odliczenie-skladek-na-ubezpieczenie-zdrowotne-pit/ | OK | Zostawic limit. Sprawdzic, czy sposob zastosowania w kodzie odpowiada wybranej metodzie: odliczenie od dochodu vs koszt. |
| Ulga dla mlodych | Limit `85 528`; kod stosuje ulge takze w B2B dla ryczaltu, skali, liniowego i IP Box | podatki.gov.pl wymienia przychody objete ulga: etat, okreslone umowy zlecenia, praktyki absolwenckie, staz uczniowski i zasilek macierzynski; nie ma przychodow z dzialalnosci gospodarczej. Limit `85 528` jest poprawny. Źrodlo: https://podatki.gov.pl/ulgi-i-odliczenia/ulga-dla-mlodych-pit/ | BŁĄD | Usunac ulge dla mlodych z B2B albo oznaczyc ja jako niedostepna dla B2B. Pozostawic dla UoP, z uwzglednieniem limitu i wieku. |
| IP Box | `5%` od calej podstawy B2B po kosztach/skladkach | podatki.gov.pl opisuje IP Box jako `5%` od sumy kwalifikowanych dochodow z kwalifikowanych IP; wymaga wyodrebnienia dochodu IP oraz obliczenia wskaznika nexus. Źrodlo: https://www.podatki.gov.pl/poradniki-i-informatory/ip-box-rozliczenie-dochodow-z-kwalifikowanych-praw-wlasnosci-intelektualnej-pit/ | BŁĄD | Nie liczyc IP Box jako prostego wariantu podatku. Dodac pola na udzial kwalifikowanego dochodu, koszty IP/nexus albo ukryc tryb za ostrzezeniem i konsultacja. |
| Ryczalt IT `12%` | Jedna stawka `0.12` dla `lump_sum_it` | podatki.gov.pl potwierdza, ze stawki ryczaltu sa okreslone w ustawie o ryczalcie, ale dla klasyfikacji konkretnych uslug IT potrzebna jest analiza PKWiU/zakresu uslug. Źrodlo ogolne: https://www.podatki.gov.pl/podatki-osobiste/pit/stawki-i-limity/ | WYMAGA KONSULTACJI | Pozostawic jako zalozenie dla "IT 12%", ale dodac opis, ze stawka zalezy od faktycznych uslug i klasyfikacji. |
| PPK jako benefit | `ppk: 0.02`; kod dodaje `2%` wynagrodzenia brutto jako wartosc benefitu | MojePPK.pl podaje wplate pracownika `2%` brutto i podstawowa wplate pracodawcy `1,5%` brutto; wplata pracodawcy jest korzyscia, ale jest tez przychodem pracownika. Źrodlo: https://www.mojeppk.pl/ | BŁĄD | Dla benefitu liczyc wplate pracodawcy `1,5%` plus opcjonalna dodatkowa, a w wyniku netto uwzglednic opodatkowanie/oskladkowanie przychodu z wplaty pracodawcy. Wplaty pracownika nie traktowac jako benefit. |
| PPK doplata roczna panstwa | `ppk.state_annual_subsidy: 240`; doliczana do kapitalu PPK (nieopodatkowana) gdy PPK wybrane | MojePPK.pl oraz ustawa o PPK potwierdzaja doplate roczna `240 zl` przy spelnieniu minimalnych wplat w roku; jednorazowa doplata powitalna `250 zl` celowo pominieta (decyzja produktowa). Źrodlo: https://www.mojeppk.pl/ | OK | Zostawic `240 zl` jako doplate roczna. Zalozenie pelnej eligibility (roczne wplaty podstawowe spelnione) opisane w komentarzu w kodzie. |
| IKE 2026 | `28 260` | KNF potwierdza limit IKE `28 260 zl` w 2026 r. Źrodlo: https://www.knf.gov.pl/?articleId=81021&p_id=18 | OK | Zostawic wartosc. |
| IKZE 2026 | `11 304`, B2B `16 956` | gov.pl potwierdza limit IKZE `11 304 zl` i `16 956 zl` dla osob prowadzacych pozarolnicza dzialalnosc. Źrodlo: https://www.gov.pl/web/rodzina/ikze-limit-wplat | OK | Zostawic wartosci. |
| VAT | Dokumentacja/metodologia sugeruje temat VAT, ale kalkulacja nie modeluje faktury netto/brutto ani VAT naleznego/naliczonego | VAT nie musi wplywac na dochod netto w prostym modelu, ale ma znaczenie dla cash flow, kontraktow B2B i porownania kwot netto/brutto. Źrodlo kategorii VAT: https://www.podatki.gov.pl/ | WYMAGA DECYZJI | Zdecydowac, czy VAT jest poza zakresem i opisac to w UI/README, czy dodac tryb faktury netto/brutto oraz zalozenia odliczenia VAT. |
| Koszty pracodawcy UoP | Dokumentacja/metodologia wspomina koszty pracodawcy, ale kalkulacja porownuje glownie perspektywe pracownika/kontraktora | Koszt pracodawcy wymaga doliczenia skladek finansowanych przez pracodawce i potencjalnie PPK pracodawcy. | WYMAGA DECYZJI | Ustalic perspektywe kalkulatora: pracownik vs pracodawca vs negocjacja ekwiwalentu B2B. Jesli ma byc koszt pracodawcy, dodac osobny wynik. |
| KUP autorskie 50% | Config ma limit `120 000`, kod liczy autorskie KUP jako wariant UoP | Limit wymaga potwierdzenia w konkretnych przypadkach, a stosowanie 50% KUP zalezy od przeniesienia praw autorskich, ewidencji i charakteru utworow. | WYMAGA KONSULTACJI | Zachowac jako zaawansowana opcje, ale oznaczyc warunkowosc i skierowac do konsultacji ksiegowej/podatkowej. |
| Danina solidarnosciowa | Nie widac realnego modelowania w kalkulacji | Dla wysokich dochodow moze zmieniac wynik, ale wymaga osobnego progu i definicji podstawy. | WYMAGA KONSULTACJI | Zdecydowac, czy kalkulator obejmuje dochody wysokie. Jesli tak, dodac model daniny i testy progowe. |

## Szczegoly: PIT

### Skala podatkowa

Wartosci w `dane_wejsciowe_kalkulator.json` sa spojne z podatki.gov.pl:

- `tax_scale[0].income`: `120000`
- `tax_scale[0].rate`: `0.12`
- drugi prog: `0.32`
- `tax_reducing_amount`: `3600`
- `tax_free_amount`: `30000`

Status: **OK**.

Ryzyko implementacyjne: kod liczy rocznie, wiec trzeba testowac szczegolnie okolice `30 000`, `120 000` oraz moment wejscia w drugi prog.

### Ulga Dla Mlodych

Limit `85 528` jest poprawny, ale zastosowanie w B2B jest bledne. W `src/calculations.py` ulga jest odejmowana od podstawy B2B przy ryczalcie oraz przy pozostalych formach opodatkowania. Oficjalny opis ulgi obejmuje okreslone tytuly przychodow, m.in. etat, wybrane zlecenia, praktyki, staz i zasilek macierzynski; nie obejmuje przychodow z dzialalnosci gospodarczej.

Status: **BŁĄD**.

Rekomendacja: UI i backend powinny zablokowac `youth_relief` dla B2B. Dla UoP mozna zostawic, ale warto dopisac walidacje wieku i test limitu.

## Szczegoly: ZUS I Zdrowotna

### Spoleczne ZUS 2026

Pelny ZUS, preferencyjny ZUS, ulga na start oraz limit 30-krotnosci sa zgodne z tabela ZUS dla 2026 r. Wypadkowa w configu odpowiada stopie `1,67%`, wiec trzeba zaznaczyc, ze to zalozenie, a nie uniwersalna wartosc dla kazdego platnika.

Status: **OK**.

### Zdrowotna Na Ryczalcie

Config ma wartosci wygladajace na starsze:

- do `60 000`: aplikacja `432,54`, powinno byc `498,35`
- od `60 000` do `300 000`: aplikacja `720,90`, powinno byc `830,58`
- powyzej `300 000`: aplikacja `1 297,62`, powinno byc `1 495,04`

Status: **BŁĄD**.

Rekomendacja: poprawic `health_lump_sum_thresholds` i dodac testy:

- przychod dokladnie `60 000`
- przychod `60 001`
- przychod dokladnie `300 000`
- przychod `300 001`

### Minimalna Zdrowotna Dla Skali, Liniowego I IP Box

Kod uzywa jednej wartosci `432.54`. Dla roku kalendarzowego 2026 ZUS rozroznia:

- `314,96` za styczen 2026
- `432,54` od lutego 2026 do stycznia 2027

Status: **BŁĄD** jako model roczny bez wyjasnienia.

Rekomendacja: dodac miesieczny model skladki zdrowotnej albo jawny parametr "rok skladkowy / rok kalendarzowy". Minimalny wariant poprawki dla kalkulacji roku kalendarzowego 2026 to nie `12 * 432,54`, tylko `314,96 + 11 * 432,54`.

## Szczegoly: UoP I PPK

### PPK

Obecna konfiguracja `ppk: 0.02` i kod dodajacy `2%` brutto do benefitow miesza dwa zjawiska:

- `2%` to podstawowa wplata pracownika, czyli koszt/odlozenie czesci wynagrodzenia pracownika,
- `1,5%` to podstawowa wplata pracodawcy, czyli realny benefit, ale traktowany podatkowo jako przychod pracownika.

Status: **BŁĄD**.

Rekomendacja: rozdzielic:

- `ppk_employee_rate`: domyslnie `0.02`
- `ppk_employer_rate`: domyslnie `0.015`
- opcjonalne wplaty dodatkowe
- efekt na netto i efekt na oszczednosci emerytalne

## Szczegoly: B2B, VAT I IP Box

### Ryczałt IT 12%

Stawka `12%` jako domyslna dla IT jest czestym zalozeniem praktycznym, ale w raporcie nie nalezy oznaczac jej jako bezwarunkowo poprawnej dla kazdego kontraktu. Klasyfikacja zalezy od rzeczywistego zakresu uslug i PKWiU.

Status: **WYMAGA KONSULTACJI**.

Rekomendacja: opisac w UI, ze `12%` dotyczy wybranego zalozenia dla uslug IT, a uzytkownik powinien potwierdzic stawke z ksiegowym/doradca.

### IP Box

Aktualny model jest zbyt prosty: `5%` jest stosowane do calej podstawy. Oficjalny opis wymaga kwalifikowanego IP, dochodu z kwalifikowanego IP oraz wskaznika nexus. To nie jest rownowazne z "cale B2B opodatkowane 5%".

Status: **BŁĄD**.

Rekomendacja: albo ukryc IP Box do czasu pelniejszego modelu, albo dodac:

- procent przychodu/dochodow kwalifikowanych jako IP,
- koszty zwiazane z IP,
- parametry do wskaznika nexus,
- ostrzezenie, ze preferencja jest rozliczana rocznie i wymaga ewidencji.

### VAT

VAT jest obecnie bardziej tematem dokumentacyjnym niz elementem modelu. To moze byc poprawne, jezeli kalkulator porownuje netto "do kieszeni", ale wtedy UI/README powinny jasno mowic, ze VAT jest poza zakresem.

Status: **WYMAGA DECYZJI**.

Rekomendacja: wybrac jedna z dwoch sciezek:

1. jawnie pominac VAT i opisac, ze wszystkie stawki B2B sa kwotami netto na fakturze,
2. dodac tryb netto/brutto faktury, VAT nalezny, VAT naliczony i cash-flow podatku.

## Szczegoly: Emerytura

### IKE I IKZE

Limity w configu sa zgodne ze zrodlami:

- IKE 2026: `28 260`
- IKZE 2026: `11 304`
- IKZE 2026 dla B2B: `16 956`

Status: **OK**.

Rekomendacja: zostawic wartosci, ale dodac zrodlo i date w configu albo w osobnej tabeli stalych.

### Projekcja Emerytalna

Sama aktualnosc limitow IKE/IKZE nie wystarcza do oceny calej projekcji. Zalozenia o wieku emerytalnym, waloryzacji, inflacji, stopach zwrotu, podatkach od wyplat i okresie oszczedzania sa zalozeniami modelowymi.

Status: **WYMAGA DECYZJI**.

Rekomendacja: pokazac zalozenia projekcji w UI i dodac testy, ktore sprawdzaja, czy zmiana parametrow emerytalnych faktycznie zmienia wynik.

## Zmiany Sugerowane Do Kolejnej Fali Implementacji

1. Poprawic skladke zdrowotna dla ryczaltu w `dane_wejsciowe_kalkulator.json` na `498.35`, `830.58`, `1495.04`.
2. Zmienic model minimalnej zdrowotnej dla roku 2026 tak, aby uwzglednial `314.96` za styczen i `432.54` od lutego, albo jawnie opisac uproszczenie roczne.
3. Usunac lub zablokowac ulge dla mlodych w B2B.
4. Przebudowac IP Box: bez kwalifikowanego dochodu i nexus nie powinien byc liczony jako proste `5%` od calej podstawy.
5. Przebudowac PPK: rozdzielic wplate pracownika, wplate pracodawcy, opodatkowanie wplaty pracodawcy i efekt emerytalny.
6. Doprecyzowac perspektywe kalkulatora dla VAT i kosztow pracodawcy.
7. Dodac testy graniczne dla PIT, ZUS, zdrowotnej ryczaltowej, limitu 30-krotnosci, ulgi dla mlodych i PPK.
8. Dodac do configu metadane: `source_url`, `source_checked_at`, `valid_from`, `valid_to` dla wartosci rocznych.

## Źrodla

- ZUS, skladki spoleczne 2026: https://www.zus.pl/baza-wiedzy/skladki-wskazniki-odsetki/skladki/wysokosc-skladek-na-ubezpieczenia-spoleczne
- ZUS, skladka zdrowotna 2026: https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r.
- podatki.gov.pl, stawki i limity PIT: https://www.podatki.gov.pl/podatki-osobiste/pit/stawki-i-limity/
- podatki.gov.pl, ulga dla mlodych: https://podatki.gov.pl/ulgi-i-odliczenia/ulga-dla-mlodych-pit/
- podatki.gov.pl, IP Box: https://www.podatki.gov.pl/poradniki-i-informatory/ip-box-rozliczenie-dochodow-z-kwalifikowanych-praw-wlasnosci-intelektualnej-pit/
- podatki.gov.pl, odliczenie skladki zdrowotnej: https://www.podatki.gov.pl/ulgi-i-odliczenia/odliczenie-skladek-na-ubezpieczenie-zdrowotne-pit/
- KNF, limit IKE 2026: https://www.knf.gov.pl/?articleId=81021&p_id=18
- gov.pl, limit IKZE 2026: https://www.gov.pl/web/rodzina/ikze-limit-wplat
- MojePPK.pl, oficjalny portal PPK: https://www.mojeppk.pl/

