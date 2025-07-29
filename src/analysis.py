import json
import os

def _load_data():
    script_dir = os.path.dirname(__file__)
    data_path = os.path.join(script_dir, '..', 'dane_wejsciowe_kalkulator.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_executive_summary(b2b_results, uop_results, break_even_faktura, lang='en'):
    data = _load_data()
    rekomendacje = data.get('rekomendacje', {}).get(lang, {})

    b2b_net_annual = b2b_results.get('net_annual_income', 0)
    uop_net_annual = uop_results.get('net_annual_income', 0)

    summary = {
        "recommendation": "",
        "b2b_net_annual": b2b_net_annual,
        "uop_net_annual": uop_net_annual,
        "break_even_faktura": break_even_faktura
    }

    if b2b_net_annual > uop_net_annual * 1.05:  # B2B significantly better
        summary["recommendation"] = rekomendacje.get('b2b_lepsze', '')
    elif uop_net_annual > b2b_net_annual * 1.05:  # UoP significantly better
        summary["recommendation"] = rekomendacje.get('uop_lepsze', '')
    else:  # Financially similar
        summary["recommendation"] = rekomendacje.get('zblizone', '')

    return summary

def get_risk_analysis(lang='en'):
    data = _load_data()
    return data.get('analiza_ryzyka', {}).get(lang, {})
