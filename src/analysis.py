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

    b2b_net_annual = b2b_results.get('total_annual_value', 0)
    uop_net_annual = uop_results.get('total_annual_value', 0)

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

def get_methodology(lang='en'):
    """Retrieves the calculation methodology explanation."""
    methodology = {
        "pl": "Obliczenia opierają się na aktualnych przepisach podatkowych i składkowych na rok 2025. W przypadku UoP uwzględniamy wszystkie koszty pracodawcy, składki ZUS oraz zaliczki na podatek dochodowy. Dla B2B bierzemy pod uwagę wybraną formę opodatkowania, składki ZUS (uwzględniając ulgi), koszty prowadzenia działalności oraz podatek VAT (jeśli dotyczy). Porównanie roczne obejmuje również benefity, dni wolne oraz płatne urlopy.",
        "en": "Calculations are based on the current tax and social security regulations for 2025. For UoP, we include all employer costs, social security contributions, and income tax advances. For B2B, we consider the chosen form of taxation, social security contributions (including reliefs), business operating costs, and VAT (if applicable). The annual comparison also includes benefits, days off, and paid holidays."
    }
    return methodology.get(lang, methodology['en'])

def get_checklist(lang='en'):
    """Retrieves the B2B checklist."""
    data = _load_data()
    return data.get('checklists', {}).get(lang, {})