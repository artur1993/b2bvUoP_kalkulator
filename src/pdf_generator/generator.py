import io
import base64
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import matplotlib.pyplot as plt

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
        # --- Chart Style Configuration ---
        plt.style.use('seaborn-v0_8-whitegrid')
        primary_color = '#1a237e'
        secondary_color = '#283593'
        accent_color = '#ffab40'
        positive_color = '#2e7d32'
        negative_color = '#c62828'

        # --- Chart 1: Total Annual Value Comparison (Bar Chart) ---
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        labels = ['B2B', 'UoP']
        values = [b2b_results.get('calkowita_roczna_wartosc', 0), uop_results.get('calkowita_roczna_wartosc', 0)]
        bars = ax1.bar(labels, values, color=[primary_color, accent_color])
        ax1.set_title(t['charts']['total_comparison_title'], fontsize=16, weight='bold', color=primary_color)
        ax1.set_ylabel(t.get('charts', {}).get('value_axis_label', 'Wartość (PLN)'), fontsize=12)
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 500, f'{yval:,.0f} zł'.replace(',', ' '), ha='center', va='bottom', fontsize=11)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        total_value_chart = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig1)

        charts = {"total_value_chart": total_value_chart, "b2b_waterfall_chart": None}

        # --- Chart 2: B2B Waterfall Chart (Advanced Report Only) ---
        if report_type == 'advanced':
            steps = b2b_results.get('steps', {})
            waterfall_data = {
                'Przychód': steps.get('Przychód roczny', 0),
                'Koszty': -steps.get('Koszty firmowe roczne', 0),
                'ZUS Społeczny': -steps.get('Składki społeczne ZUS', 0),
                'Podatek': -steps.get('Podatek dochodowy', 0),
                'ZUS Zdrowotny': -steps.get('Składka zdrowotna', 0)
            }
            
            fig2, ax2 = plt.subplots(figsize=(12, 7))
            cumulative = 0
            for i, (label, value) in enumerate(waterfall_data.items()):
                color = positive_color if value > 0 else negative_color
                ax2.bar(label, value, bottom=cumulative, color=color, width=0.6)
                cumulative += value

            # Final Net Value Bar
            net_income = b2b_results.get('roczne_netto_na_reke', 0)
            ax2.bar('Netto', net_income, color=accent_color, width=0.6)

            ax2.set_title(t['charts']['b2b_waterfall_title'], fontsize=16, weight='bold', color=primary_color)
            ax2.set_ylabel(t.get('charts', {}).get('value_axis_label', 'Wartość (PLN)'), fontsize=12)
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            plt.xticks(rotation=45, ha="right")

            img_buffer_waterfall = io.BytesIO()
            plt.savefig(img_buffer_waterfall, format='png', bbox_inches='tight')
            charts['b2b_waterfall_chart'] = base64.b64encode(img_buffer_waterfall.getvalue()).decode('utf-8')
            plt.close(fig2)

        return charts

    def generate(self, data, report_type='basic'):
        lang = data.get('language', 'en')
        t = self.translations.get(lang, self.translations['en'])

        charts = self._generate_charts(data.get('b2b_results', {}), data.get('uop_results', {}), t, report_type)
    
        template_data = {
            "b2b_results": data.get('b2b_results', {}),
            "uop_results": data.get('uop_results', {}),
            "input_data": data.get('input_data', {}),
            "charts": charts,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "t": t,
            "report_type": report_type,
            "pension_details": data.get('pension_details')
        }
        
        if report_type == 'advanced':
            template_data['analysis'] = data.get('analysis', {})
            template_data['insurance_details'] = data.get('insurance_details')
            template_data['total_insurance_cost'] = data.get('total_insurance_cost')
            
            # Calculate individual insurance module costs
            b2b_monthly_invoice = data.get('input_data', {}).get('b2b', {}).get('faktura_miesieczna', 0)
            template_data['insurance_costs'] = self._calculate_all_insurance_costs(
                data.get('insurance_details'), b2b_monthly_invoice
            )

            # Add checklist data for advanced reports
            with open('dane_wejsciowe_kalkulator.json', 'r', encoding='utf-8') as f:
                input_data = json.load(f)
                template_data['checklists'] = input_data.get('checklists', {}).get(lang, {})

        html_out = self.template.render(template_data)
        
        return HTML(string=html_out).write_pdf(stylesheets=[self.css])