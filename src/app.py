import json
from flask import Flask, request, jsonify, render_template
import os

# Initialize Flask app
app = Flask(__name__)

# --- Determine the absolute path to the project root ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

# Load data from JSON file at startup
with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
    DANE = json.load(f)

# --- Data not present in the specification ---
DANE['zus_uop_procentowe'] = {
    "emerytalna": 0.0976, "rentowa": 0.0150, "chorobowa": 0.0245, "zdrowotna": 0.09
}
DANE['ulga_dla_mlodych_limit'] = 85528

def calculate_b2b_results(b2b_data):
    """Calculates all financial aspects for a B2B contract based on the corrected 2025 rules."""
    faktura_rocznie = b2b_data['faktura_miesieczna'] * 12
    koszty_rocznie = b2b_data['koszty_firmowe_miesieczne'] * 12

    # ZUS
    zus_details = DANE['zus_2025'][b2b_data['zus_rodzaj']]
    skladki_spoleczne_rocznie = sum(v for k, v in zus_details.items() if k in ['emerytalna', 'rentowa', 'wypadkowa', 'fundusz_pracy']) * 12
    if b2b_data['zus_chorobowe']:
        skladki_spoleczne_rocznie += zus_details.get('chorobowa', 0) * 12
    
    # Per spec, health insurance is a fixed value from the JSON, not calculated dynamically.
    skladka_zdrowotna_rocznie = zus_details['zdrowotna'] * 12
    wszystkie_skladki_zus = skladki_spoleczne_rocznie + skladka_zdrowotna_rocznie

    # Dochód Brutto (przed opodatkowaniem)
    dochod_brutto = faktura_rocznie - koszty_rocznie

    # Podatek
    forma = b2b_data['forma_opodatkowania']
    podatek_roczny = 0
    
    if forma == 'ryczalt_IT':
        # On ryczałt, tax is based on revenue. Social contributions are not deducted from the tax base.
        podstawa_opodatkowania = faktura_rocznie
        podatek_roczny = round(podstawa_opodatkowania * DANE['progi_podatkowe']['ryczalt_IT'])
    else: # Liniowy, Skala, IP Box
        podstawa_do_opodatkowania = dochod_brutto - skladki_spoleczne_rocznie
        
        if forma == 'liniowy':
            # Health insurance deduction from income, up to the limit of 12,900 PLN for 2025
            zdrowotna_do_odliczenia = min(skladka_zdrowotna_rocznie, 12900)
            podstawa_do_opodatkowania -= zdrowotna_do_odliczenia
            
            # Round tax base to nearest whole PLN
            podstawa_zaokraglona = round(podstawa_do_opodatkowania)
            podatek_roczny = round(podstawa_zaokraglona * DANE['progi_podatkowe']['liniowy'])

        elif forma == 'skala':
            # No health insurance deduction for 'skala'
            kwota_wolna = DANE['progi_podatkowe']['kwota_wolna']
            prog = DANE['progi_podatkowe']['skala'][0]['dochod']
            
            # Round tax base to nearest whole PLN
            podstawa_zaokraglona = round(podstawa_do_opodatkowania)
            
            if podstawa_zaokraglona <= kwota_wolna:
                podatek_roczny = 0
            elif podstawa_zaokraglona <= prog:
                podatek_roczny = round((podstawa_zaokraglona - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka'])
            else:
                podatek_ponad_prog = (podstawa_zaokraglona - prog) * DANE['progi_podatkowe']['skala'][1]['stawka']
                podatek_roczny = round(((prog - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']) + podatek_ponad_prog)

        elif forma == 'ip_box':
            podstawa_zaokraglona = round(podstawa_do_opodatkowania)
            podatek_roczny = round(podstawa_zaokraglona * DANE['progi_podatkowe']['ip_box'])

    if b2b_data.get('ulga_dla_mlodych', False) and faktura_rocznie <= DANE['ulga_dla_mlodych_limit']:
        podatek_roczny = 0

    # Koszty dodatkowe
    koszt_benefitow = sum(DANE['benefity'][b] for b in b2b_data['wybrane_benefity'] if b in DANE['benefity'])
    stawka_dzienna = b2b_data['faktura_miesieczna'] / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    utracony_przychod_urlop = b2b_data['urlop_dni'] * stawka_dzienna
    utracony_przychod_przestoje = b2b_data['przestoje_miesiace'] * b2b_data['faktura_miesieczna']

    # Wynik końcowy
    dochod_netto_rocznie = dochod_brutto - wszystkie_skladki_zus - podatek_roczny - koszt_benefitow - utracony_przychod_urlop - utracony_przychod_przestoje
    
    return {
        "roczny_przychod": faktura_rocznie, "roczne_koszty": koszty_rocznie, "roczny_zus": wszystkie_skladki_zus,
        "roczny_podatek": podatek_roczny, "roczny_koszt_benefitow": koszt_benefitow,
        "roczny_utracony_przychod": utracony_przychod_urlop + utracony_przychod_przestoje,
        "roczne_netto": dochod_netto_rocznie, "miesieczne_netto": dochod_netto_rocznie / 12
    }

def calculate_uop_results(uop_data):
    """Calculates all financial aspects for an Employment Contract (UoP)."""
    brutto_rocznie = uop_data['wynagrodzenie_brutto'] * 12
    
    zus_uop = DANE['zus_uop_procentowe']
    skladki_spoleczne = brutto_rocznie * (zus_uop['emerytalna'] + zus_uop['rentowa'] + zus_uop['chorobowa'])
    podstawa_zdrowotnej = brutto_rocznie - skladki_spoleczne
    skladka_zdrowotna = podstawa_zdrowotnej * zus_uop['zdrowotna']
    
    koszty_uzyskania = uop_data['koszty_uzyskania_przychodu'] * 12
    podstawa_opodatkowania = max(0, round(brutto_rocznie - skladki_spoleczne - koszty_uzyskania, 0))

    kwota_wolna = DANE['progi_podatkowe']['kwota_wolna']
    prog = DANE['progi_podatkowe']['skala'][0]['dochod']
    podatek_roczny = 0
    if podstawa_opodatkowania > kwota_wolna:
        if podstawa_opodatkowania <= prog:
            podatek_roczny = (podstawa_opodatkowania - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']
        else:
            podatek_ponad_prog = (podstawa_opodatkowania - prog) * DANE['progi_podatkowe']['skala'][1]['stawka']
            podatek_roczny = ((prog - kwota_wolna) * DANE['progi_podatkowe']['skala'][0]['stawka']) + podatek_ponad_prog

    if uop_data.get('ulga_dla_mlodych', False) and brutto_rocznie <= DANE['ulga_dla_mlodych_limit']:
        podatek_roczny = 0

    netto_rocznie = brutto_rocznie - skladki_spoleczne - skladka_zdrowotna - podatek_roczny
    
    wartosc_benefitow = sum(DANE['benefity'][b] for b in uop_data['wybrane_benefity'] if b in DANE['benefity'] and b != 'ppk')
    if 'ppk' in uop_data['wybrane_benefity']:
        wartosc_benefitow += brutto_rocznie * DANE['benefity']['ppk']
        
    stawka_dzienna = uop_data['wynagrodzenie_brutto'] / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    wartosc_dni_wolnych = DANE['dni_wolne_uop']['urlop_wypoczynkowy']['dni'] * stawka_dzienna
    
    return {
        "roczne_brutto": brutto_rocznie, "roczny_zus": skladki_spoleczne + skladka_zdrowotna,
        "roczny_podatek": podatek_roczny, "roczna_wartosc_benefitow": wartosc_benefitow,
        "roczna_wartosc_platnych_dni_wolnych": wartosc_dni_wolnych, "roczne_netto": netto_rocznie,
        "miesieczne_netto": netto_rocznie / 12,
        "calkowita_roczna_wartosc": netto_rocznie + wartosc_benefitow + wartosc_dni_wolnych
    }

def calculate_break_even(uop_total_value, b2b_base_data):
    """Iteratively finds the B2B invoice amount to match UoP total value."""
    for faktura_miesieczna_test in range(int(b2b_base_data['faktura_miesieczna'] / 2), 50000, 100):
        test_data = b2b_base_data.copy()
        test_data['faktura_miesieczna'] = faktura_miesieczna_test
        b2b_res = calculate_b2b_results(test_data)
        if b2b_res['roczne_netto'] >= uop_total_value:
            return faktura_miesieczna_test
    return -1

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Main endpoint to calculate and compare B2B vs. UoP earnings."""
    request_data = request.get_json()
    b2b_data = request_data['b2b']
    uop_data = request_data['uop']
    
    b2b_results = calculate_b2b_results(b2b_data)
    uop_results = calculate_uop_results(uop_data)
    
    break_even_point = calculate_break_even(uop_results['calkowita_roczna_wartosc'], b2b_data)

    response_data = {
        "b2b_results": b2b_results,
        "uop_results": uop_results,
        "break_even_faktura": break_even_point,
        "komentarze": "Porównanie wygenerowane pomyślnie."
    }
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
