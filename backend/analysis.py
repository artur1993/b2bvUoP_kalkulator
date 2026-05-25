from typing import Dict, Any
from backend.config import config_manager

def generate_executive_summary(b2b_results: Dict[str, Any], uop_results: Dict[str, Any], break_even_faktura: float, lang: str = 'en') -> Dict[str, Any]:
    """Generates a high-level executive summary and recommendation."""
    config = config_manager.get_config()
    rekomendacje = config.get('rekomendacje', {}).get(lang, {})

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

def get_risk_analysis(lang: str = 'en') -> Dict[str, Any]:
    """Retrieves the risk analysis text for the specified language."""
    config = config_manager.get_config()
    return config.get('analiza_ryzyka', {}).get(lang, {})

def get_methodology(lang: str = 'en') -> str:
    """Retrieves the calculation methodology explanation."""
    methodology = {
        "pl": "Obliczenia opierają się na aktualnych przepisach podatkowych i składkowych na rok 2026. W przypadku UoP uwzględniamy limit 30-krotności ZUS, wszystkie koszty pracodawcy, składki ZUS oraz zaliczki na podatek dochodowy. Dla B2B bierzemy pod uwagę wybraną formę opodatkowania, składki ZUS (Polski Ład 2026), koszty prowadzenia działalności oraz podatek VAT. Porównanie roczne obejmuje również benefity, dni wolne oraz płatne urlopy.",
        "en": "Calculations are based on the current tax and social security regulations for 2026. For UoP, we include the ZUS 30-times limit, all employer costs, social security contributions, and income tax advances. For B2B, we consider the chosen form of taxation, ZUS contributions (Polski Ład 2026), business operating costs, and VAT. The annual comparison also includes benefits, days off, and paid holidays."
    }
    return methodology.get(lang, methodology['en'])

def get_checklist(lang: str = 'en') -> Dict[str, Any]:
    """Retrieves the B2B checklist."""
    config = config_manager.get_config()
    return config.get('checklists', {}).get(lang, {})
