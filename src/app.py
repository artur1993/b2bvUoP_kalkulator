import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from openpyxl import Workbook
import io
import os
import math
from src.pdf_generator.generator import PDFReportGenerator
from src.analysis import generate_executive_summary, get_risk_analysis
from src.calculations import _get_float, calculate_uop_break_even
from src.pension_calculator import calculate_pension_details





# --- Determine the absolute path to the project root ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

# Initialize Flask app
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'src/dashboard/dist'))
CORS(app)

# Configure logging
file_handler = RotatingFileHandler('flask.log', maxBytes=1024 * 1024 * 10, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.DEBUG) # Set to DEBUG to capture more details
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG) # Set to DEBUG to capture more details

# Load data from JSON file at startup
with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
    DANE = json.load(f)

# --- Data not present in the specification ---
DANE['zus_uop_procentowe'] = {
    "emerytalna": 0.0976, "rentowa": 0.0150, "chorobowa": 0.0245, "zdrowotna": 0.09
}
DANE['ulga_dla_mlodych_limit'] = 85528
DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek'] = 3600

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
    custom_benefits_rocznie = float(b2b_data.get('customBenefits', 0))

    # Benefits provided by the company
    company_benefits = b2b_data.get('companyBenefits', {})
    wartosc_benefitow_od_firmy = 0
    for key, benefit in company_benefits.items():
        if benefit.get('enabled', False):
            if key == 'paidVacationDays':
                wartosc_benefitow_od_firmy += float(benefit.get('days', 0)) * stawka_dzienna
            elif key == 'paidSickDays':
                wartosc_benefitow_od_firmy += float(benefit.get('days', 0)) * stawka_dzienna * 0.8 # Assuming 80% pay
            else:
                wartosc_benefitow_od_firmy += float(benefit.get('value', 0))

    # Adjust lost revenue based on paid days off from company
    paid_vacation_days = float(company_benefits.get('paidVacationDays', {}).get('days', 0)) if company_benefits.get('paidVacationDays', {}).get('enabled') else 0
    paid_sick_days = float(company_benefits.get('paidSickDays', {}).get('days', 0)) if company_benefits.get('paidSickDays', {}).get('enabled') else 0
    
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
    
    # Detailed annual contributions
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
        
        # Roczny limit KUP standardowych/podwyższonych
        if kup_type in ['standard', 'elevated']:
             limit_roczny = DANE['koszty_uzyskania_przychodu'][f"{kup_type}owe_roczny_limit"]
             if roczne_koszty_uzyskania + miesieczne_kup > limit_roczny:
                 miesieczne_kup = max(0, limit_roczny - roczne_koszty_uzyskania)

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

    return -1 # Indicates break-even point not found in range


@app.route('/api/calculate/break-even-analysis', methods=['POST'])
def break_even_analysis():
    try:
        data = request.get_json()
        uop_data = data.get('uop', {})
        b2b_base_data = data.get('b2b', {})
        wynagrodzenie_brutto_uop = _get_float(uop_data, 'wynagrodzenie_brutto')

        analysis_results = []
        start_b2b_rate = wynagrodzenie_brutto_uop - 5000
        end_b2b_rate = wynagrodzenie_brutto_uop + 15000

        for b2b_rate in range(int(start_b2b_rate), int(end_b2b_rate), 500):
            b2b_data = b2b_base_data.copy()
            b2b_data['faktura_miesieczna'] = b2b_rate
            
            b2b_results = calculate_b2b_results(b2b_data)
            uop_results = calculate_uop_results(uop_data)
            
            net_difference = b2b_results['calkowita_roczna_wartosc'] - uop_results['calkowita_roczna_wartosc']
            analysis_results.append({
                "b2b_rate": b2b_rate,
                "net_difference": net_difference
            })
            
        return jsonify(analysis_results)
    except Exception as e:
        app.logger.exception("Error during break-even analysis:")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate/sensitivity-analysis', methods=['POST'])
def sensitivity_analysis():
    try:
        data = request.get_json()
        base_b2b_data = data.get('b2b', {})
        base_uop_data = data.get('uop', {})

        base_b2b_results = calculate_b2b_results(base_b2b_data)
        base_uop_results = calculate_uop_results(base_uop_data)
        base_net_difference = base_b2b_results['calkowita_roczna_wartosc'] - base_uop_results['calkowita_roczna_wartosc']

        sensitivity_params = {
            'koszty_firmowe_miesieczne': 0.20,
            'urlop_dni': 5,
            'przestoje_miesiace': 1
        }

        analysis_results = []

        for param, change in sensitivity_params.items():
            # Test min value
            min_data = base_b2b_data.copy()
            if isinstance(change, float):
                min_data[param] = _get_float(min_data, param) * (1 - change)
            else:
                min_data[param] = _get_float(min_data, param) - change

            min_b2b_results = calculate_b2b_results(min_data)
            min_net_difference = min_b2b_results['calkowita_roczna_wartosc'] - base_uop_results['calkowita_roczna_wartosc']

            # Test max value
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

        return jsonify(analysis_results)
    except Exception as e:
        app.logger.exception("Error during sensitivity analysis:")
        return jsonify({"error": str(e)}), 500


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Main endpoint to calculate and compare B2B vs. UoP earnings."""
    try:
        request_data = request.get_json()
        
        # Ensure data exists to prevent KeyErrors
        b2b_data = request_data.get('b2b', {})
        uop_data = request_data.get('uop', {})
        calculation_mode = request_data.get('calculation_mode', 'uop_to_b2b') # Default to uop_to_b2b

        if not b2b_data or not uop_data:
            return jsonify({"error": "Missing 'b2b' or 'uop' data in request."}), 400

        b2b_results = calculate_b2b_results(b2b_data)
        uop_results = calculate_uop_results(uop_data)
        
        break_even_point = -1
        if calculation_mode == 'uop_to_b2b':
            break_even_point = calculate_break_even(uop_results['calkowita_roczna_wartosc'], b2b_data)
            break_even_key = "break_even_faktura"
        elif calculation_mode == 'b2b_to_uop':
            break_even_point = calculate_uop_break_even(b2b_results['calkowita_roczna_wartosc'], uop_data)
            break_even_key = "break_even_wynagrodzenie_brutto"
        else:
            return jsonify({"error": "Invalid calculation_mode provided."}), 400

        response_data = {
            "b2b_results": b2b_results,
            "uop_results": uop_results,
            break_even_key: break_even_point,
            "komentarze": "Porównanie wygenerowane pomyślnie."
        }

        # Nowa logika do obsługi wyrównania emerytury
        if b2b_data.get('equalizePension'):
            uop_gross_salary = _get_float(uop_data, 'wynagrodzenie_brutto', 0)
            pension_details = calculate_pension_details(uop_gross_salary)
            response_data['pension_details'] = pension_details

        return jsonify(response_data)
    except Exception as e:
        app.logger.exception("Error during calculation:")
        return jsonify({"error": str(e) if app.debug else "An internal server error occurred."}), 500

@app.route('/api/export/excel', methods=['POST'])
def export_to_excel():
    """Exports the calculation results to an Excel file."""
    data = request.get_json()
    b2b_results = data.get('b2b_results', {})
    uop_results = data.get('uop_results', {})

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Porównanie B2B vs UoP"

    sheet['A1'] = "Kategoria"
    sheet['B1'] = "B2B"
    sheet['C1'] = "UoP"

    sheet['A2'] = "Całkowita roczna wartość"
    sheet['B2'] = b2b_results.get('calkowita_roczna_wartosc')
    sheet['C2'] = uop_results.get('calkowita_roczna_wartosc')

    # Save to a memory buffer
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="kalkulator_wyniki.xlsx", 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Initialize the generator once when the app starts
pdf_generator = PDFReportGenerator(
    template_path=os.path.join(BASE_DIR, 'src/pdf_generator/templates'),
    static_path=os.path.join(BASE_DIR, 'src/pdf_generator/static')
)

@app.route('/api/export/pdf', methods=['POST'])
def export_to_pdf():
    """Exports the calculation results to a visually rich PDF file."""
    data = request.get_json()
    if not data:
        return {"error": "Invalid request body"}, 400
    
    # Generate the PDF using the new module
    pdf_bytes = pdf_generator.generate(data)
    
    # Send the file to the user
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    return send_file(
        buffer, 
        as_attachment=True, 
        download_name="Raport_B2B_vs_UoP.pdf", 
        mimetype='application/pdf'
    )

@app.route('/api/export/pdf/advanced', methods=['POST'])
def export_to_advanced_pdf():
    data = request.get_json()
    if not data: return {"error": "Invalid request body"}, 400
    
    lang = data.get('language', 'en')
    summary = generate_executive_summary(data.get('b2b_results', {}), data.get('uop_results', {}), data.get('break_even_faktura', 0), lang)
    risk_analysis = get_risk_analysis(lang)
    data['analysis'] = {"summary": summary, "risk": risk_analysis}

    if data.get('input_data', {}).get('b2b', {}).get('equalizePension'):
        uop_gross_salary = data.get('input_data', {}).get('uop', {}).get('wynagrodzenie_brutto', 0)
        pension_details = calculate_pension_details(uop_gross_salary)
        data['pension_details'] = pension_details

    pdf_bytes = pdf_generator.generate(data, report_type='advanced')
    
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Raport_Zaawansowany_B2B_vs_UoP.pdf", mimetype='application/pdf')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=5001)