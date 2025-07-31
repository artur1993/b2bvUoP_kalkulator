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
DANE['ulga_dla_mlodych_limit'] = 85528
DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek'] = 3600

def _get_float(data, key, default=0.0):
    """Safely gets a float value from a dictionary, returning a default if conversion fails."""
    try:
        return float(data.get(key, default))
    except (ValueError, TypeError):
        return default

def calculate_b2b_results(b2b_data):
    """
    Calculates all financial aspects for a B2B contract.

    Args:
        b2b_data (dict): A dictionary containing all B2B input parameters.

    Returns:
        dict: A dictionary with detailed B2B calculation results.
    """
    faktura_miesieczna = _get_float(b2b_data, 'faktura_miesieczna')
    faktura_rocznie = faktura_miesieczna * 12
    koszty_firmowe_miesieczne = _get_float(b2b_data, 'koszty_firmowe_miesieczne')
    koszty_rocznie = koszty_firmowe_miesieczne * 12

    # ZUS
    zus_type = b2b_data['zus_rodzaj']
    if zus_type == 'mala_firma':
        zus_type = 'preferencyjny'
    elif zus_type == 'duza_firma':
        zus_type = 'pelny'
    zus_details = DANE['zus_2025'][zus_type]
    
    skladki_zus_emerytalna = zus_details.get('emerytalna', 0) * 12
    skladki_zus_rentowa = zus_details.get('rentowa', 0) * 12
    skladki_zus_wypadkowa = zus_details.get('wypadkowa', 0) * 12
    skladki_zus_fundusz_pracy = zus_details.get('fundusz_pracy', 0) * 12
    skladki_zus_chorobowa = zus_details.get('chorobowa', 0) * 12 if b2b_data.get('zus_chorobowe') else 0
    
    skladki_spoleczne_rocznie = skladki_zus_emerytalna + skladki_zus_rentowa + skladki_zus_wypadkowa + skladki_zus_fundusz_pracy + skladki_zus_chorobowa
    skladka_zdrowotna_rocznie = zus_details['zdrowotna'] * 12
    wszystkie_skladki_zus = skladki_spoleczne_rocznie + skladka_zdrowotna_rocznie

    dochod_brutto = faktura_rocznie - koszty_rocznie

    # Podatek
    forma = b2b_data['forma_opodatkowania']
    podatek_roczny = 0
    
    if forma == 'ryczalt_IT':
        podstawa_opodatkowania = faktura_rocznie
        podatek_roczny = round(podstawa_opodatkowania * DANE['progi_podatkowe']['ryczalt_IT'])
    else:
        podstawa_do_opodatkowania = dochod_brutto - skladki_spoleczne_rocznie
        
        if forma == 'liniowy':
            zdrowotna_do_odliczenia = min(skladka_zdrowotna_rocznie, 12900)
            podstawa_do_opodatkowania -= zdrowotna_do_odliczenia
        elif forma == 'skala':
            podstawa_do_opodatkowania -= skladka_zdrowotna_rocznie
        elif forma == 'ip_box':
            podstawa_do_opodatkowania -= skladka_zdrowotna_rocznie

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
            
            kwota_zmniejszajaca_podatek = skladka_zdrowotna_rocznie * (7.75 / 9)
            podatek_roczny = math.ceil(max(0, podatek_roczny - kwota_zmniejszajaca_podatek))
        elif forma == 'ip_box':
            podatek_roczny = math.ceil(podstawa_zaokraglona * DANE['progi_podatkowe']['ip_box'])
            kwota_zmniejszajaca_podatek = skladka_zdrowotna_rocznie * (7.75 / 9)
            podatek_roczny = math.ceil(max(0, podatek_roczny - kwota_zmniejszajaca_podatek))

    if b2b_data.get('ulga_dla_mlodych', False) and faktura_rocznie <= DANE['ulga_dla_mlodych_limit']:
        podatek_roczny = 0

    stawka_dzienna = faktura_miesieczna / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    
    custom_benefits_rocznie = float(b2b_data.get('customBenefits', 0))

    company_benefits = b2b_data.get('companyBenefits', {})
    wartosc_benefitow_od_firmy = 0
    for key, benefit in company_benefits.items():
        if benefit.get('enabled', False):
            if key == 'paidVacationDays':
                wartosc_benefitow_od_firmy += float(benefit.get('days', 0)) * stawka_dzienna
            elif key == 'paidSickDays':
                wartosc_benefitow_od_firmy += float(benefit.get('days', 0)) * stawka_dzienna * 0.8
            else:
                wartosc_benefitow_od_firmy += float(benefit.get('value', 0))

    paid_vacation_days = float(company_benefits.get('paidVacationDays', {}).get('days', 0)) if company_benefits.get('paidVacationDays', {}).get('enabled') else 0
    paid_sick_days = float(company_benefits.get('paidSickDays', {}).get('days', 0)) if company_benefits.get('paidSickDays', {}).get('enabled') else 0
    
    unpaid_vacation_days = max(0, int(_get_float(b2b_data, 'urlop_dni')) - paid_vacation_days)
    unpaid_sick_days = max(0, int(_get_float(b2b_data, 'chorobowe_dni', 0)) - paid_sick_days) 

    utracony_przychod_urlop = unpaid_vacation_days * stawka_dzienna
    utracony_przychod_chorobowe = unpaid_sick_days * stawka_dzienna * 0.8
    utracony_przychod_przestoje = _get_float(b2b_data, 'przestoje_miesiace') * faktura_miesieczna
    
    calkowity_utracony_przychod = utracony_przychod_urlop + utracony_przychod_chorobowe + utracony_przychod_przestoje

    dochod_netto_rocznie = dochod_brutto - wszystkie_skladki_zus - podatek_roczny - calkowity_utracony_przychod
    
    calkowita_wartosc_b2b = dochod_netto_rocznie + wartosc_benefitow_od_firmy + custom_benefits_rocznie

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
    """
    Calculates all financial aspects for an Employment Contract (UoP).

    Args:
        uop_data (dict): A dictionary containing all UoP input parameters.

    Returns:
        dict: A dictionary with detailed UoP calculation results.
    """
    wynagrodzenie_brutto_miesiecznie = _get_float(uop_data, 'wynagrodzenie_brutto')
    kup_settings = uop_data.get('kup_settings', {'type': 'standard', 'creative_work_percentage': 0})
    kup_type = kup_settings.get('type', 'standard')
    creative_percentage = _get_float(kup_settings, 'creative_work_percentage', 0) / 100

    brutto_rocznie = wynagrodzenie_brutto_miesiecznie * 12
    zus_uop = DANE['zus_uop_procentowe']
    limit_kup_autorskie = DANE['progi_podatkowe']['limit_kup_autorskie']

    roczne_skladki_spoleczne = 0
    roczna_skladka_zdrowotna = 0
    roczne_koszty_uzyskania = 0
    roczna_podstawa_opodatkowania = 0
    roczny_podatek = 0
    
    roczne_skladki_zus_emerytalna = 0
    roczne_skladki_zus_rentowa = 0
    roczne_skladki_zus_chorobowa = 0

    steps = {'monthly_calculations': []}
    skumulowane_kup_autorskie = 0

    for month in range(1, 13):
        miesieczna_skladka_emerytalna = wynagrodzenie_brutto_miesiecznie * zus_uop['emerytalna']
        miesieczna_skladka_rentowa = wynagrodzenie_brutto_miesiecznie * zus_uop['rentowa']
        miesieczna_skladka_chorobowa = wynagrodzenie_brutto_miesiecznie * zus_uop['chorobowa']
        miesieczne_skladki_spoleczne = miesieczna_skladka_emerytalna + miesieczna_skladka_rentowa + miesieczna_skladka_chorobowa
        
        roczne_skladki_zus_emerytalna += miesieczna_skladka_emerytalna
        roczne_skladki_zus_rentowa += miesieczna_skladka_rentowa
        roczne_skladki_zus_chorobowa += miesieczna_skladka_chorobowa

        podstawa_zdrowotnej = wynagrodzenie_brutto_miesiecznie - miesieczne_skladki_spoleczne
        miesieczna_skladka_zdrowotna = podstawa_zdrowotnej * zus_uop['zdrowotna']

        miesieczne_kup = 0
        if kup_type == 'standard':
            miesieczne_kup = DANE['koszty_uzyskania_przychodu']['standardowe']
        elif kup_type == 'elevated':
            miesieczne_kup = DANE['koszty_uzyskania_przychodu']['podwyzszone']
        elif kup_type == 'autorskie_50':
            if skumulowane_kup_autorskie < limit_kup_autorskie:
                przychodu_tworczego = wynagrodzenie_brutto_miesiecznie * creative_percentage
                skladki_od_tworczego = przychodu_tworczego * (zus_uop['emerytalna'] + zus_uop['rentowa'] + zus_uop['chorobowa'])
                podstawa_kup_autorskich = przychodu_tworczego - skladki_od_tworczego
                
                potencjalne_kup = podstawa_kup_autorskich * 0.5
                
                if skumulowane_kup_autorskie + potencjalne_kup > limit_kup_autorskie:
                    kup_autorskie = limit_kup_autorskie - skumulowane_kup_autorskie
                    kup_standardowe = DANE['koszty_uzyskania_przychodu']['standardowe']
                    miesieczne_kup = kup_autorskie + kup_standardowe
                    skumulowane_kup_autorskie = limit_kup_autorskie
                else:
                    miesieczne_kup = potencjalne_kup
                    skumulowane_kup_autorskie += potencjalne_kup
            else:
                miesieczne_kup = DANE['koszty_uzyskania_przychodu']['standardowe']
        
        if kup_type in ['standard', 'elevated']:
             limit_roczny = DANE['koszty_uzyskania_przychodu'][f"{kup_type}owe_roczny_limit"]
             if roczne_koszty_uzyskania + miesieczne_kup > limit_roczny:
                 miesieczne_kup = max(0, limit_roczny - roczne_koszty_uzyskania)
        elif kup_type == 'brak':
            miesieczne_kup = 0

        podstawa_opodatkowania_miesieczna = max(0, math.floor(wynagrodzenie_brutto_miesiecznie - miesieczne_skladki_spoleczne - miesieczne_kup))
        
        roczne_skladki_spoleczne += miesieczne_skladki_spoleczne
        roczna_skladka_zdrowotna += miesieczna_skladka_zdrowotna
        roczne_koszty_uzyskania += miesieczne_kup
        roczna_podstawa_opodatkowania += podstawa_opodatkowania_miesieczna
        
        steps['monthly_calculations'].append({
            'month': month,
            'brutto': wynagrodzenie_brutto_miesiecznie,
            'skladki_spoleczne': miesieczne_skladki_spoleczne,
            'skladka_zdrowotna': miesieczna_skladka_zdrowotna,
            'kup': miesieczne_kup,
            'podstawa_opodatkowania': podstawa_opodatkowania_miesieczna
        })

    kwota_wolna = DANE['progi_podatkowe']['kwota_wolna']
    prog = DANE['progi_podatkowe']['skala'][0]['dochod']
    podatek_prog_1 = 0
    podatek_prog_2 = 0
    
    if roczna_podstawa_opodatkowania > kwota_wolna:
        if roczna_podstawa_opodatkowania <= prog:
            podatek_prog_1 = (roczna_podstawa_opodatkowania - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']
            roczny_podatek = podatek_prog_1
        else:
            podatek_prog_1 = (prog - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']
            podatek_prog_2 = (roczna_podstawa_opodatkowania - prog) * DANE['progi_podatkowe']['skala'][1]['stawka']
            roczny_podatek = podatek_prog_1 + podatek_prog_2
    
    kwota_zmniejszajaca_podatek = DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek']
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

    steps.update({
        'Roczne wynagrodzenie brutto': brutto_rocznie,
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
    """
    Iteratively finds the B2B invoice amount to match UoP total value.

    Args:
        uop_total_value (float): The total annual value of the UoP contract.
        b2b_base_data (dict): The base B2B input data.

    Returns:
        float: The monthly B2B invoice amount needed to break even, or -1 if not found.
    """
    start_range = int(_get_float(b2b_base_data, 'faktura_miesieczna', 10000) * 0.5)
    end_range = 100000
    
    for faktura_miesieczna_test in range(start_range, end_range, 100):
        test_data = b2b_base_data.copy()
        test_data['faktura_miesieczna'] = faktura_miesieczna_test
        b2b_res = calculate_b2b_results(test_data)
        if b2b_res['calkowita_roczna_wartosc'] >= uop_total_value:
            return faktura_miesieczna_test
    return -1

def calculate_uop_break_even(b2b_total_value, uop_base_data):
    """
    Iteratively finds the UoP gross salary to match B2B total value.

    Args:
        b2b_total_value (float): The total annual value of the B2B contract.
        uop_base_data (dict): The base UoP input data.

    Returns:
        float: The monthly UoP gross salary needed to break even, or -1 if not found.
    """
    start_range = int(_get_float(uop_base_data, 'wynagrodzenie_brutto', 5000) * 0.5)
    end_range = 50000

    for wynagrodzenie_brutto_test in range(start_range, end_range, 100):
        test_data = uop_base_data.copy()
        test_data['wynagrodzenie_brutto'] = wynagrodzenie_brutto_test
        uop_res = calculate_uop_results(test_data)
        if uop_res['calkowita_roczna_wartosc'] >= b2b_total_value:
            return wynagrodzenie_brutto_test
    return -1

def get_calculation_data():
    """Returns the loaded calculation data."""
    return DANE

def calculate_break_even_analysis(uop_data, b2b_base_data):
    """
    Performs a break-even analysis over a range of B2B invoice values.

    Args:
        uop_data (dict): UoP input data.
        b2b_base_data (dict): B2B input data.

    Returns:
        list: A list of dictionaries with B2B rates and net differences.
    """
    wynagrodzenie_brutto_uop = _get_float(uop_data, 'wynagrodzenie_brutto')
    uop_results = calculate_uop_results(uop_data)

    analysis_results = []
    start_b2b_rate = wynagrodzenie_brutto_uop - 5000
    end_b2b_rate = wynagrodzenie_brutto_uop + 15000

    for b2b_rate in range(int(start_b2b_rate), int(end_b2b_rate), 500):
        b2b_data = b2b_base_data.copy()
        b2b_data['faktura_miesieczna'] = b2b_rate
        
        b2b_results = calculate_b2b_results(b2b_data)
        
        net_difference = b2b_results['calkowita_roczna_wartosc'] - uop_results['calkowita_roczna_wartosc']
        analysis_results.append({
            "b2b_rate": b2b_rate,
            "net_difference": net_difference
        })
        
    return analysis_results

def calculate_sensitivity_analysis(base_b2b_data, base_uop_data):
    """
    Performs a sensitivity analysis on B2B results based on key parameters.

    Args:
        base_b2b_data (dict): Base B2B input data.
        base_uop_data (dict): Base UoP input data.

    Returns:
        list: A list of dictionaries with parameters and their impact.
    """
    base_b2b_results = calculate_b2b_results(base_b2b_data)
    base_uop_results = calculate_uop_results(base_uop_data)

    sensitivity_params = {
        'koszty_firmowe_miesieczne': 0.20,
        'urlop_dni': 5,
        'przestoje_miesiace': 1
    }

    analysis_results = []

    for param, change in sensitivity_params.items():
        min_data = base_b2b_data.copy()
        if isinstance(change, float):
            min_data[param] = _get_float(min_data, param) * (1 - change)
        else:
            min_data[param] = _get_float(min_data, param) - change

        min_b2b_results = calculate_b2b_results(min_data)
        min_net_difference = min_b2b_results['calkowita_roczna_wartosc'] - base_uop_results['calkowita_roczna_wartosc']

        max_data = base_b2b_data.copy()
        if isinstance(change, float):
            max_data[param] = _get_float(max_data, param) * (1 + change)
        else:
            max_data[param] = _get_float(max_data, param) + change

        max_b2b_results = calculate_b2b_results(max_data)
        max_net_difference = max_b2b_results['calkowita_roczna_wartosc'] - base_uop_results['calkowita_roczna_wartosc']
        
        impact = max_net_difference - min_net_difference

        analysis_results.append({
            "parameter": param,
            "impact": impact
        })

    return analysis_results