import math
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
    DANE = json.load(f)

DANE['zus_uop_procentowe'] = {
    "emerytalna": 0.0976, "rentowa": 0.0150, "chorobowa": 0.0245, "zdrowotna": 0.09
}
DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek'] = 3600

def _get_float(data, key, default=0.0):
    """Safely gets a float value from a dictionary, returning a default if conversion fails."""
    try:
        return float(data.get(key, default))
    except (ValueError, TypeError):
        return default

def calculate_b2b_results(b2b_data):
    """Calculates all financial aspects for a B2B contract based on the corrected 2025 rules."""
    faktura_miesieczna = _get_float(b2b_data, 'faktura_miesieczna')
    faktura_rocznie = faktura_miesieczna * 12
    koszty_firmowe_miesieczne = _get_float(b2b_data, 'koszty_firmowe_miesieczne')
    koszty_rocznie = koszty_firmowe_miesieczne * 12

    # ZUS
    zus_type = b2b_data['zus_rodzaj']
    if zus_type == 'mala_firma':
        zus_type = 'preferencyjny' # Map 'mala_firma' to 'preferencyjny' ZUS
    elif zus_type == 'duza_firma':
        zus_type = 'pelny' # Map 'duza_firma' to 'pelny' ZUS
    zus_details = DANE['zus_2025'][zus_type]
    
    # Detailed ZUS contributions
    skladki_zus_emerytalna = zus_details.get('emerytalna', 0) * 12
    skladki_zus_rentowa = zus_details.get('rentowa', 0) * 12
    skladki_zus_wypadkowa = zus_details.get('wypadkowa', 0) * 12
    skladki_zus_fundusz_pracy = zus_details.get('fundusz_pracy', 0) * 12
    skladki_zus_chorobowa = zus_details.get('chorobowa', 0) * 12 if b2b_data.get('zus_chorobowe') else 0
    
    skladki_spoleczne_rocznie = skladki_zus_emerytalna + skladki_zus_rentowa + skladki_zus_wypadkowa + skladki_zus_fundusz_pracy + skladki_zus_chorobowa
    skladka_zdrowotna_rocznie = zus_details['zdrowotna'] * 12
    wszystkie_skladki_zus = skladki_spoleczne_rocznie + skladka_zdrowotna_rocznie

    # Dochód Brutto (przed opodatkowaniem)
    dochod_brutto = faktura_rocznie - koszty_rocznie

    # Podatek
    forma = b2b_data['forma_opodatkowania']
    podatek_roczny = 0
    
    if forma == 'ryczalt_IT':
        podstawa_opodatkowania = faktura_rocznie
        podatek_roczny = round(podstawa_opodatkowania * DANE['progi_podatkowe']['ryczalt_IT'])
    else:
        podstawa_do_opodatkowania = dochod_brutto - skladki_spoleczne_rocznie
        
        # Składka zdrowotna obniża podstawę dla liniowego, skali i IP Box
        if forma == 'liniowy':
            zdrowotna_do_odliczenia = min(skladka_zdrowotna_rocznie, 12900) # Limit odliczenia dla liniowego
            podstawa_do_opodatkowania -= zdrowotna_do_odliczenia
        elif forma == 'skala':
            podstawa_do_opodatkowania -= skladka_zdrowotna_rocznie # Dla skali cała składka zdrowotna obniża podstawę
        elif forma == 'ip_box':
            podstawa_do_opodatkowania -= skladka_zdrowotna_rocznie # Dla IP Box cała składka zdrowotna obniża podstawę

        podstawa_zaokraglona = round(podstawa_do_opodatkowania)
        
        kwota_wolna = DANE['progi_podatkowe']['kwota_wolna']
        prog = DANE['progi_podatkowe']['skala'][0]['dochod']
        podatek_prog_1 = 0
        podatek_prog_2 = 0

        if forma == 'liniowy':
            podatek_roczny = math.ceil(podstawa_zaokraglona * DANE['progi_podatkowe']['liniowy'])
        elif forma == 'skala':
            if podstawa_zaokraglona <= kwota_wolna:
                podatek_roczny = 0
            elif podstawa_zaokraglona <= prog:
                podatek_prog_1 = math.ceil((podstawa_zaokraglona - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka'])
                podatek_roczny = podatek_prog_1
            else:
                podatek_prog_1 = math.ceil((prog - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka'])
                podatek_prog_2 = math.ceil((podstawa_zaokraglona - prog) * DANE['progi_podatkowe']['skala'][1]['stawka'])
                podatek_roczny = podatek_prog_1 + podatek_prog_2
            
            # Odliczenie od podatku jest bardziej skomplikowane, na razie upraszczamy
            kwota_zmniejszajaca_podatek = skladka_zdrowotna_rocznie * (7.75 / 9)
            podatek_roczny = math.ceil(max(0, podatek_roczny - kwota_zmniejszajaca_podatek))
        elif forma == 'ip_box':
            podatek_roczny = math.ceil(podstawa_zaokraglona * DANE['progi_podatkowe']['ip_box'])
            kwota_zmniejszajaca_podatek = skladka_zdrowotna_rocznie * (7.75 / 9)
            podatek_roczny = math.ceil(max(0, podatek_roczny - kwota_zmniejszajaca_podatek))

    if b2b_data.get('ulga_dla_mlodych', False) and faktura_rocznie <= DANE['ulga_dla_mlodych_limit']:
        podatek_roczny = 0

    # --- New Benefit and Lost Revenue Logic ---
    stawka_dzienna = faktura_miesieczna / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    
    # Custom benefits provided by the user
    custom_benefits_rocznie = _get_float(b2b_data, 'customBenefits', 0)

    # Benefits provided by the company
    company_benefits = b2b_data.get('companyBenefits', {})
    wartosc_benefitow_od_firmy = 0
    for key, benefit in company_benefits.items():
        if benefit.get('enabled', False):
            if key == 'paidVacationDays':
                wartosc_benefitow_od_firmy += _get_float(benefit, 'days', 0) * stawka_dzienna
            elif key == 'paidSickDays':
                wartosc_benefitow_od_firmy += _get_float(benefit, 'days', 0) * stawka_dzienna * 0.8 # Assuming 80% pay
            else:
                wartosc_benefitow_od_firmy += _get_float(benefit, 'value', 0)

    # Adjust lost revenue based on paid days off from company
    paid_vacation_days = _get_float(company_benefits.get('paidVacationDays', {}), 'days', 0) if company_benefits.get('paidVacationDays', {}).get('enabled') else 0
    paid_sick_days = _get_float(company_benefits.get('paidSickDays', {}), 'days', 0) if company_benefits.get('paidSickDays', {}).get('enabled') else 0
    
    # Calculate lost revenue for UNPAID days
    unpaid_vacation_days = max(0, int(_get_float(b2b_data, 'urlop_dni')) - paid_vacation_days)
    # Assuming sick days in form are total, subtract paid ones
    unpaid_sick_days = max(0, int(_get_float(b2b_data, 'chorobowe_dni', 0)) - paid_sick_days) 

    utracony_przychod_urlop = unpaid_vacation_days * stawka_dzienna
    utracony_przychod_chorobowe = unpaid_sick_days * stawka_dzienna * 0.8 # Assuming 80% pay for sick leave
    utracony_przychod_przestoje = _get_float(b2b_data, 'przestoje_miesiace') * faktura_miesieczna
    
    calkowity_utracony_przychod = utracony_przychod_urlop + utracony_przychod_chorobowe + utracony_przychod_przestoje

    # Final Calculation
    dochod_netto_rocznie = dochod_brutto - wszystkie_skladki_zus - podatek_roczny - calkowity_utracony_przychod
    
    # Total value includes net income and all benefits
    calkowita_wartosc_b2b = dochod_netto_rocznie + wartosc_benefitow_od_firmy + custom_benefits_rocznie

    # --- Calculation Steps for Methodology Section ---
    calculation_steps = {
        'Przychód roczny': faktura_rocznie,
        'Koszty firmowe roczne': koszty_rocznie,
        'Dochód (przed ZUS)': dochod_brutto,
        'skladki_zus_emerytalna': skladki_zus_emerytalna,
        'skladki_zus_rentowa': skladki_zus_rentowa,
        'skladki_zus_chorobowa': skladki_zus_chorobowa,
        'skladki_zus_wypadkowa': skladki_zus_wypadkowa,
        'skladki_zus_fundusz_pracy': skladki_zus_fundusz_pracy,
        'skladka_zdrowotna': skladka_zdrowotna_rocznie,
        'Podstawa do opodatkowania': podstawa_do_opodatkowania if 'podstawa_do_opodatkowania' in locals() else podstawa_opodatkowania,
        'podatek_prog_1': podatek_prog_1 if 'podatek_prog_1' in locals() else (podatek_roczny if forma != 'skala' else 0),
        'podatek_prog_2': podatek_prog_2 if 'podatek_prog_2' in locals() else 0,
        'kwota_zmniejszajaca_podatek': kwota_zmniejszajaca_podatek if 'kwota_zmniejszajaca_podatek' in locals() else 0,
        'Roczny podatek': podatek_roczny,
        'Utracony przychód': calkowity_utracony_przychod
    }

    results = {
        "roczny_przychod": faktura_rocznie,
        "roczne_koszty_firmowe": koszty_rocznie,
        "roczny_zus": wszystkie_skladki_zus,
        "roczny_podatek": podatek_roczny,
        "roczny_utracony_przychod": calkowity_utracony_przychod,
        "roczne_netto_na_reke": dochod_netto_rocznie,
        "roczna_wartosc_benefitow_od_firmy": wartosc_benefitow_od_firmy,
        "roczna_wartosc_wlasnych_korzysci": custom_benefits_rocznie,
        "calkowita_roczna_wartosc": calkowita_wartosc_b2b,
        "miesieczne_netto": calkowita_wartosc_b2b / 12
    }
    results['steps'] = calculation_steps
    return results

def calculate_uop_results(uop_data):
    """Calculates all financial aspects for an Employment Contract (UoP) with dynamic tax-deductible costs."""
    steps = {}
    wynagrodzenie_brutto_miesiecznie = _get_float(uop_data, 'wynagrodzenie_brutto')
    brutto_rocznie = wynagrodzenie_brutto_miesiecznie * 12

    zus_uop = DANE['zus_uop_procentowe']
    roczne_skladki_spoleczne = brutto_rocznie * (zus_uop['emerytalna'] + zus_uop['rentowa'] + zus_uop['chorobowa'])
    roczna_skladka_zdrowotna = (brutto_rocznie - roczne_skladki_spoleczne) * zus_uop['zdrowotna']

    kup_settings = uop_data.get('kup_settings', {'type': 'standard', 'creative_work_percentage': 0})
    kup_type = kup_settings.get('type', 'standard')
    creative_percentage = _get_float(kup_settings, 'creative_work_percentage', 0) / 100
    limit_kup_autorskie = DANE['progi_podatkowe']['limit_kup_autorskie']

    if kup_type == 'standard':
        roczne_koszty_uzyskania = DANE['koszty_uzyskania_przychodu']['standardowe'] * 12
    elif kup_type == 'elevated':
        roczne_koszty_uzyskania = DANE['koszty_uzyskania_przychodu']['podwyzszone'] * 12
    elif kup_type == 'autorskie_50':
        przychodu_tworczego = brutto_rocznie * creative_percentage
        skladki_od_tworczego = przychodu_tworczego * (zus_uop['emerytalna'] + zus_uop['rentowa'] + zus_uop['chorobowa'])
        podstawa_kup_autorskich = przychodu_tworczego - skladki_od_tworczego
        roczne_koszty_uzyskania = min(podstawa_kup_autorskich * 0.5, limit_kup_autorskie)
    else:
        roczne_koszty_uzyskania = 0

    roczna_podstawa_opodatkowania = max(0, round(brutto_rocznie - roczne_skladki_spoleczne - roczne_koszty_uzyskania))

    kwota_wolna = DANE['progi_podatkowe']['kwota_wolna']
    prog = DANE['progi_podatkowe']['skala'][0]['dochod']
    podatek_prog_1 = 0
    podatek_prog_2 = 0
    roczny_podatek = 0

    if roczna_podstawa_opodatkowania > kwota_wolna:
        if roczna_podstawa_opodatkowania <= prog:
            podatek_prog_1 = (roczna_podstawa_opodatkowania - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']
            roczny_podatek = podatek_prog_1
        else:
            podatek_prog_1 = (prog - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']
            podatek_prog_2 = (roczna_podstawa_opodatkowania - prog) * DANE['progi_podatkowe']['skala'][1]['stawka']
            roczny_podatek = podatek_prog_1 + podatek_prog_2

    kwota_zmniejszajaca_podatek = DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek']
    if roczna_podstawa_opodatkowania > kwota_wolna:
        roczny_podatek -= kwota_zmniejszajaca_podatek

    roczny_podatek = math.ceil(max(0, roczny_podatek))

    if uop_data.get('ulga_dla_mlodych', False) and brutto_rocznie <= DANE['ulga_dla_mlodych_limit']:
        roczny_podatek = 0

    netto_rocznie_na_reke = brutto_rocznie - roczne_skladki_spoleczne - roczna_skladka_zdrowotna - roczny_podatek
    
    wartosc_benefitow = sum(DANE['benefity'][b] for b in uop_data.get('wybrane_benefity', []) if b in DANE['benefity'] and b != 'ppk')
    if 'ppk' in uop_data.get('wybrane_benefity', []):
        wartosc_benefitow += brutto_rocznie * DANE['benefity']['ppk']
        
    stawka_dzienna = wynagrodzenie_brutto_miesiecznie / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    wartosc_dni_wolnych = DANE['dni_wolne_uop']['urlop_wypoczynkowy']['dni'] * stawka_dzienna
    
    calkowita_wartosc_uop = netto_rocznie_na_reke + wartosc_benefitow + wartosc_dni_wolnych

    roczne_skladki_zus_emerytalna = brutto_rocznie * zus_uop['emerytalna']
    roczne_skladki_zus_rentowa = brutto_rocznie * zus_uop['rentowa']
    roczne_skladki_zus_chorobowa = brutto_rocznie * zus_uop['chorobowa']
    steps.update({
        'Roczne wynagrodzenie brutto': brutto_rocznie,
        'skladki_zus_emerytalna': roczne_skladki_zus_emerytalna,
        'skladki_zus_rentowa': roczne_skladki_zus_rentowa,
        'skladki_zus_chorobowa': roczne_skladki_zus_chorobowa,
        'skladki_zus_emerytalna': roczne_skladki_zus_emerytalna,
        'skladki_zus_rentowa': roczne_skladki_zus_rentowa,
        'skladki_zus_chorobowa': roczne_skladki_zus_chorobowa,
        'skladka_zdrowotna': roczna_skladka_zdrowotna,
        'Koszty uzyskania przychodu': roczne_koszty_uzyskania,
        'Podstawa do opodatkowania': roczna_podstawa_opodatkowania,
        'podatek_prog_1': podatek_prog_1,
        'podatek_prog_2': podatek_prog_2,
        'kwota_zmniejszajaca_podatek': kwota_zmniejszajaca_podatek,
        'Roczny podatek': roczny_podatek,
        'Wartość benefitów': wartosc_benefitow,
        'Wartość płatnych dni wolnych': wartosc_dni_wolnych
    })

    results = {
        "roczne_brutto": brutto_rocznie,
        "roczny_zus": roczne_skladki_spoleczne + roczna_skladka_zdrowotna,
        "roczny_podatek": roczny_podatek,
        "roczna_wartosc_benefitow": wartosc_benefitow,
        "roczna_wartosc_platnych_dni_wolnych": wartosc_dni_wolnych,
        "roczne_netto_na_reke": netto_rocznie_na_reke,
        "calkowita_roczna_wartosc": calkowita_wartosc_uop,
        "miesieczne_netto": calkowita_wartosc_uop / 12,
    }
    results['steps'] = steps
    return results

def calculate_break_even(uop_total_value, b2b_base_data):
    """Iteratively finds the B2B invoice amount to match UoP total value."""
    # Use a wider and more dynamic range for searching
    start_range = int(_get_float(b2b_base_data, 'faktura_miesieczna', 10000) * 0.5)
    end_range = 100000 # Set a reasonable upper limit for search
    
    for faktura_miesieczna_test in range(start_range, end_range, 100):
        test_data = b2b_base_data.copy()
        test_data['faktura_miesieczna'] = faktura_miesieczna_test
        b2b_res = calculate_b2b_results(test_data)
        # Compare the total value of both contracts
        if b2b_res['calkowita_roczna_wartosc'] >= uop_total_value:
            return faktura_miesieczna_test
    return -1 # Indicates break-even point not found in range

def calculate_uop_break_even(b2b_total_value, uop_base_data):
    """Iteratively finds the UoP gross salary to match B2B total value."""
    # Use a wider and more dynamic range for searching
    start_range = int(_get_float(uop_base_data, 'wynagrodzenie_brutto', 5000) * 0.5)
    end_range = 50000 # Set a reasonable upper limit for search

    for wynagrodzenie_brutto_test in range(start_range, end_range, 100):
        test_data = uop_base_data.copy()
        test_data['wynagrodzenie_brutto'] = wynagrodzenie_brutto_test
        uop_res = calculate_uop_results(test_data)
        # Compare the total value of both contracts
        if uop_res['calkowita_roczna_wartosc'] >= b2b_total_value:
            return wynagrodzenie_brutto_test
    return -1 # Indicates break-even point not found in range
