import io
import base64
import json
import time
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

# --- Configure Logging ---
# Note: This will inherit the logger configuration from the Flask app
# if run within the app context.
log = logging.getLogger(__name__)

# Insurance Modules data (mirroring frontend for calculation)
insurance_modules = {
    "income_protection": {
        "name": "Ubezpieczenie od utraty dochodu",
        "type": "dynamic",
        "options": {
            "basic": {"coverage": 50, "multiplier": 0.008},
            "standard": {"coverage": 65, "multiplier": 0.012},
            "uop_equivalent": {"coverage": 80, "multiplier": 0.015},
            "premium": {"coverage": 100, "multiplier": 0.020}
        }
    },
    "professional_liability": {
        "name": "OC zawodowe",
        "type": "fixed",
        "options": {
            "basic": {"cost": 33.33},
            "standard": {"cost": 66.67},
            "premium": {"cost": 125}
        }
    },
    "private_health": {
        "name": "Prywatne zdrowotne",
        "type": "fixed",
        "options": {
            "basic": {"cost": 150},
            "standard": {"cost": 300},
            "premium": {"cost": 500}
        }
    },
    "equipment": {
        "name": "Ubezpieczenie sprzętu",
        "type": "fixed",
        "options": {
            "basic": {"cost": 50},
            "standard": {"cost": 100},
            "premium": {"cost": 200}
        }
    },
    "zus_voluntary": {
        "name": "ZUS dobrowolne",
        "type": "fixed",
        "options": {
            "enabled": {"cost": 34.30}
        }
    },
    "legal_protection": {
        "name": "Ochrona prawna",
        "type": "fixed",
        "options": {
            "basic": {"cost": 30},
            "standard": {"cost": 60}
        }
    },
    "cyber_insurance": {
        "name": "Ubezpieczenie cyber",
        "type": "fixed",
        "options": {
            "basic": {"cost": 50},
            "standard": {"cost": 100}
        }
    }
}

# A simple Jinja2 filter to format numbers as Polish currency
def format_currency(value):
    if not isinstance(value, (int, float)):
        return value
    return f"{value:,.2f} zł".replace(",", " ").replace(".", ",")

class PDFReportGenerator:
    def __init__(self, template_path, static_path):
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.env.filters['format_currency'] = format_currency
        self.template = self.env.get_template("report.html")
        self.css = CSS(f"{static_path}/report.css")
        # Load translation files
        self.translations = {
            'en': json.load(open('src/dashboard/src/locales/en/translation.json', encoding='utf-8')),
            'pl': json.load(open('src/dashboard/src/locales/pl/translation.json', encoding='utf-8'))
        }

    def _calculate_module_cost(self, module_id, insurance_selections, b2b_monthly_invoice):
        config = insurance_selections.get(module_id)
        module = insurance_modules.get(module_id)
        if config and config.get('enabled') and module:
            option = module['options'].get(config['level'])
            if option:
                if module['type'] == 'dynamic':
                    annual_income = b2b_monthly_invoice * 12
                    return (annual_income * option['multiplier']) / 12
                else:
                    return option['cost']
        return 0

    def _calculate_all_insurance_costs(self, insurance_config, b2b_monthly_invoice):
        costs = {}
        if insurance_config and insurance_config.get('enabled'):
            selections = insurance_config.get('selections', {})
            for module_id in selections:
                costs[module_id] = self._calculate_module_cost(module_id, selections, b2b_monthly_invoice)
        return costs

    def _generate_charts(self, b2b_results, uop_results, t, report_type='basic'):
        # Charts are now generated on the frontend and passed in the `data` object.
        # This function is kept for compatibility but does nothing.
        return {}

    def generate(self, data, report_type='basic'):
        total_start_time = time.time()
        log.info(f"Starting PDF generation (type: {report_type})...")

        lang = data.get('language', 'en')
        t = self.translations.get(lang, self.translations['en'])

        template_data = {
            "b2b_results": data.get('b2b_results', {}),
            "uop_results": data.get('uop_results', {}),
            "input_data": data.get('input_data', {}),
            "charts": data.get('charts', {}),  # Get charts from input data
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "t": t,
            "report_type": report_type,
            "pension_details": data.get('pension_details')
        }
        
        if report_type == 'advanced':
            template_data['analysis'] = data.get('analysis', {})
            template_data['insurance_details'] = data.get('insurance_details')
            template_data['total_insurance_cost'] = data.get('total_insurance_cost')
            
            b2b_monthly_invoice = data.get('input_data', {}).get('b2b', {}).get('monthly_invoice_amount', 0)
            template_data['insurance_costs'] = self._calculate_all_insurance_costs(
                data.get('insurance_details'), b2b_monthly_invoice
            )

            with open('dane_wejsciowe_kalkulator.json', 'r', encoding='utf-8') as f:
                input_data = json.load(f)
                template_data['checklists'] = input_data.get('checklists', {}).get(lang, {})

        # --- HTML Rendering ---
        html_render_start_time = time.time()
        html_out = self.template.render(template_data)
        html_render_end_time = time.time()
        log.info(f"HTML rendering took {html_render_end_time - html_render_start_time:.2f} seconds.")

        # --- PDF Writing ---
        pdf_write_start_time = time.time()
        pdf_bytes = HTML(string=html_out).write_pdf(stylesheets=[self.css])
        pdf_write_end_time = time.time()
        log.info(f"PDF writing took {pdf_write_end_time - pdf_write_start_time:.2f} seconds.")

        total_end_time = time.time()
        log.info(f"Total PDF generation finished in {total_end_time - total_start_time:.2f} seconds.")
        
        return pdf_bytes