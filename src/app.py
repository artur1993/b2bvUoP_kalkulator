import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from openpyxl import Workbook
from fpdf import FPDF
import io
import os

def _get_float(data, key, default=0.0):
    """Safely gets a float value from a dictionary, returning a default if conversion fails."""
    try:
        return float(data.get(key, default))
    except (ValueError, TypeError):
        return default

def _get_int(data, key, default=0):
    """Safely gets an int value from a dictionary, returning a default if conversion fails."""
    try:
        return int(data.get(key, default))
    except (ValueError, TypeError):
        return default

# --- Determine the absolute path to the project root ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'src/dashboard/dist'))

# Define font path for PDF generation and add to app config
app.config['FONT_DIR'] = os.path.join(BASE_DIR, 'src', 'fonts')
app.config['FONT_PATH'] = os.path.join(app.config['FONT_DIR'], 'DejaVuSans.ttf') # User needs to ensure DejaVuSans.ttf is placed in src/fonts/

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
    skladki_spoleczne_rocznie = sum(v for k, v in zus_details.items() if k in ['emerytalna', 'rentowa', 'wypadkowa', 'fundusz_pracy']) * 12
    if b2b_data['zus_chorobowe']:
        skladki_spoleczne_rocznie += zus_details.get('chorobowa', 0) * 12
    
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
        
        if forma == 'liniowy':
            zdrowotna_do_odliczenia = min(skladka_zdrowotna_rocznie, 12900)
            podstawa_do_opodatkowania -= zdrowotna_do_odliczenia
            podstawa_zaokraglona = round(podstawa_do_opodatkowania)
            podatek_roczny = round(podstawa_zaokraglona * DANE['progi_podatkowe']['liniowy'])
        elif forma == 'skala':
            kwota_wolna = DANE['progi_podatkowe']['kwota_wolna']
            prog = DANE['progi_podatkowe']['skala'][0]['dochod']
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

    # --- New Benefit and Lost Revenue Logic ---
    stawka_dzienna = float(b2b_data['faktura_miesieczna']) / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    
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
    unpaid_vacation_days = max(0, int(b2b_data['urlop_dni']) - paid_vacation_days)
    # Assuming sick days in form are total, subtract paid ones
    unpaid_sick_days = max(0, int(b2b_data.get('chorobowe_dni', 0)) - paid_sick_days) 

    utracony_przychod_urlop = unpaid_vacation_days * stawka_dzienna
    utracony_przychod_chorobowe = unpaid_sick_days * stawka_dzienna * 0.8 # Assuming 80% pay for sick leave
    utracony_przychod_przestoje = _get_float(b2b_data, 'przestoje_miesiace') * faktura_miesieczna
    
    calkowity_utracony_przychod = utracony_przychod_urlop + utracony_przychod_chorobowe + utracony_przychod_przestoje

    # Final Calculation
    dochod_netto_rocznie = dochod_brutto - wszystkie_skladki_zus - podatek_roczny - calkowity_utracony_przychod
    
    # Total value includes net income and all benefits
    calkowita_wartosc_b2b = dochod_netto_rocznie + wartosc_benefitow_od_firmy + custom_benefits_rocznie

    return {
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

def calculate_uop_results(uop_data):
    """Calculates all financial aspects for an Employment Contract (UoP)."""
    wynagrodzenie_brutto = _get_float(uop_data, 'wynagrodzenie_brutto')
    koszty_uzyskania_przychodu = _get_float(uop_data, 'koszty_uzyskania_przychodu')

    brutto_rocznie = wynagrodzenie_brutto * 12
    
    zus_uop = DANE['zus_uop_procentowe']
    skladki_spoleczne = brutto_rocznie * (zus_uop['emerytalna'] + zus_uop['rentowa'] + zus_uop['chorobowa'])
    podstawa_zdrowotnej = brutto_rocznie - skladki_spoleczne
    skladka_zdrowotna = podstawa_zdrowotnej * zus_uop['zdrowotna']
    
    koszty_uzyskania = koszty_uzyskania_przychodu * 12
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

    netto_rocznie_na_reke = brutto_rocznie - skladki_spoleczne - skladka_zdrowotna - podatek_roczny
    
    # The benefit structure for UoP remains simpler unless specified otherwise
    wartosc_benefitow = sum(DANE['benefity'][b] for b in uop_data.get('wybrane_benefity', []) if b in DANE['benefity'] and b != 'ppk')
    if 'ppk' in uop_data.get('wybrane_benefity', []):
        wartosc_benefitow += brutto_rocznie * DANE['benefity']['ppk']
        
    stawka_dzienna = wynagrodzenie_brutto / DANE['dane_ogolne']['dni_robocze_miesiecznie']
    wartosc_dni_wolnych = DANE['dni_wolne_uop']['urlop_wypoczynkowy']['dni'] * stawka_dzienna
    
    calkowita_wartosc_uop = netto_rocznie_na_reke + wartosc_benefitow + wartosc_dni_wolnych

    return {
        "roczne_brutto": brutto_rocznie,
        "roczny_zus": skladki_spoleczne + skladka_zdrowotna,
        "roczny_podatek": podatek_roczny,
        "roczna_wartosc_benefitow": wartosc_benefitow,
        "roczna_wartosc_platnych_dni_wolnych": wartosc_dni_wolnych,
        "roczne_netto_na_reke": netto_rocznie_na_reke,
        "calkowita_roczna_wartosc": calkowita_wartosc_uop,
        "miesieczne_netto": calkowita_wartosc_uop / 12,
    }

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

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Main endpoint to calculate and compare B2B vs. UoP earnings."""
    try:
        request_data = request.get_json()
        
        # Ensure data exists to prevent KeyErrors
        b2b_data = request_data.get('b2b', {})
        uop_data = request_data.get('uop', {})

        if not b2b_data or not uop_data:
            return jsonify({"error": "Missing 'b2b' or 'uop' data in request."}), 400

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
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/export/pdf', methods=['POST'])
def export_to_pdf():
    """Exports the calculation results to a PDF file."""
    data = request.get_json()
    b2b_results = data.get('b2b_results', {})
    uop_results = data.get('uop_results', {})

    pdf = FPDF()
    # Ensure the fonts directory exists
    if not os.path.exists(app.config['FONT_DIR']):
        os.makedirs(app.config['FONT_DIR'])
    
    # Add Unicode font (User needs to ensure DejaVuSans.ttf is placed in src/fonts/)
    try:
        pdf.add_font('DejaVuSans', '', app.config['FONT_PATH'], uni=True)
    except RuntimeError as e:
        # Fallback to a basic font if DejaVuSans.ttf is not found or corrupted
        print(f"Error adding font: {e}. Please ensure DejaVuSans.ttf is in {app.config['FONT_DIR']}")
        pdf.set_font("Helvetica", size=12) # Fallback font
    
    pdf.add_page()
    pdf.set_font("DejaVuSans", size=12) # Use the new font
    
    pdf.cell(200, 10, txt="Wyniki Kalkulatora B2B vs UoP", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Całkowita roczna wartość B2B: {b2b_results.get('calkowita_roczna_wartosc'):.2f} PLN", ln=True)
    pdf.cell(200, 10, txt=f"Całkowita roczna wartość UoP: {uop_results.get('calkowita_roczna_wartosc'):.2f} PLN", ln=True)

    # Save to a memory buffer
    buffer = io.BytesIO(pdf.output()) # pdf.output() returns bytes directly
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="kalkulator_wyniki.pdf", mimetype='application/pdf')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=5001)