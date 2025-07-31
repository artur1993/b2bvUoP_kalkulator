import json
import os

def _load_data():
    """Loads the main data file for calculations."""
    script_dir = os.path.dirname(__file__)
    data_path = os.path.join(script_dir, '..', 'dane_wejsciowe_kalkulator.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_executive_summary(b2b_results, uop_results, break_even_faktura, lang='en'):
    """
    Generates a high-level executive summary and recommendation.

    Args:
        b2b_results (dict): The calculated B2B results.
        uop_results (dict): The calculated UoP results.
        break_even_faktura (float): The calculated break-even invoice amount.
        lang (str): The language for the summary ('en' or 'pl').

    Returns:
        dict: A dictionary containing the summary and recommendation.
    """
    data = _load_data()
    rekomendacje = data.get('rekomendacje', {}).get(lang, {})

    b2b_net_annual = b2b_results.get('calkowita_roczna_wartosc', 0)
    uop_net_annual = uop_results.get('calkowita_roczna_wartosc', 0)

    summary = {
        "recommendation": "",
        "b2b_net_annual": b2b_net_annual,
        "uop_net_annual": uop_net_annual,
        "break_even_faktura": break_even_faktura
    }

    if b2b_net_annual > uop_net_annual * 1.05:
        summary["recommendation"] = rekomendacje.get('b2b_lepsze', '')
    elif uop_net_annual > b2b_net_annual * 1.05:
        summary["recommendation"] = rekomendacje.get('uop_lepsze', '')
    else:
        summary["recommendation"] = rekomendacje.get('zblizone', '')

    return summary

def get_risk_analysis(lang='en'):
    """
    Retrieves the risk analysis text for the specified language.

    Args:
        lang (str): The language for the risk analysis ('en' or 'pl').

    Returns:
        dict: A dictionary containing the risk analysis points.
    """
    data = _load_data()
    return data.get('analiza_ryzyka', {}).get(lang, {})