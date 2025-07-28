import io
import base64
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import matplotlib.pyplot as plt

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

    def _generate_charts(self, b2b_results, uop_results, t):
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Chart 1: Total Annual Value Comparison
        plt.figure(figsize=(8, 5))
        labels = ['B2B', 'UoP']
        values = [b2b_results.get('calkowita_roczna_wartosc', 0), uop_results.get('calkowita_roczna_wartosc', 0)]
        plt.bar(labels, values, color=['#2c5282', '#4fd1c5'])
        plt.title(t['charts']['total_comparison_title'])
        plt.ylabel(t.get('charts', {}).get('value_axis_label', 'Value (PLN)')) # Added a default for safety
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        
        total_value_chart = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()

        # In the future, logic for other charts can be added here

        return {"total_value_chart": total_value_chart}

    def generate(self, data):
        lang = data.get('language', 'en')
        t = self.translations.get(lang, self.translations['en'])

        charts = self._generate_charts(data.get('b2b_results', {}), data.get('uop_results', {}), t)
        
        html_out = self.template.render(
            b2b_results=data.get('b2b_results', {}),
            uop_results=data.get('uop_results', {}),
            input_data=data.get('input_data', {}),
            charts=charts,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            t=t # Pass translations to the template
        )
        
        return HTML(string=html_out).write_pdf(stylesheets=[self.css])