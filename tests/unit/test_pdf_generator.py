import unittest
import os
import json
from unittest.mock import MagicMock, patch
import jinja2 # Import jinja2
from src.pdf_generator.generator import PDFReportGenerator, format_currency
from pypdf import PdfReader
from io import BytesIO

class PDFGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        # More detailed mock data for testing the waterfall calculation
        self.mock_data = {
            "b2b_results": {
                "calkowita_roczna_wartosc": 240000,
                "roczne_netto_na_reke": 150000,
                "roczny_podatek": 28500,
                "roczny_zus": 25000,
                "steps": {
                    "Przychód roczny": 240000.00,
                    "Koszty firmowe roczne": 36000.00,
                    "Dochód (przed ZUS)": 204000.00,
                    "Składki społeczne ZUS": 19500.00,
                    "Podstawa do opodatkowania": 184500.00,
                    "Podatek dochodowy": 35055.00,
                    "Dochód po opodatkowaniu": 149445.00,
                    "Składka zdrowotna": 15415.56
                }
            },
            "uop_results": {
                "calkowita_roczna_wartosc": 180000,
                "roczne_netto_na_reke": 120000,
                "roczny_podatek": 15000,
                "roczny_zus": 45000,
            },
            "input_data": {
                "b2b": {"faktura_miesieczna": 20000, "forma_opodatkowania": "liniowy"},
                "uop": {"wynagrodzenie_brutto": 15000}
            },
            "analysis": {
                "summary": {"recommendation": "B2B is recommended."},
                "risk": {"stability": "Lower on B2B."}
            },
            "language": "pl",
            "insurance_details": {
                "enabled": True,
                "activeProfile": "standard",
                "totalMonthlyCost": 680.97,
                "breakdown": [
                    {
                        "name": "OC zawodowe",
                        "level": "standard",
                        "cost": 66.67,
                        "details": "Suma ubezpieczenia: 1 000 000 zł",
                        "uop_comparison": "UoP: odp. do 3 pensji"
                    },
                    {
                        "name": "Prywatne zdrowotne",
                        "level": "standard",
                        "cost": 300.00,
                        "details": "Rozszerzony pakiet, dostęp do specjalistów",
                        "uop_comparison": "UoP: pakiet standardowy"
                    }
                ]
            }
        }
        
        # Use the real template rendering for more accurate tests
        self.pdf_generator = PDFReportGenerator(
            template_path='src/pdf_generator/templates',
            static_path='src/pdf_generator/static'
        )

    @patch('weasyprint.HTML')
    def test_advanced_report_contains_narrative_calculation_positive(self, mock_html):
        """Sprawdza, czy raport zaawansowany zawiera narracyjną sekcję 'Jak to policzyliśmy?'"""
        mock_html_instance = mock_html.return_value
        mock_html_instance.write_pdf.return_value = b"dummy pdf content"

        # We need to render the real HTML to check its content
        rendered_html = self.pdf_generator.template.render({
            **self.mock_data,
            "t": self.pdf_generator.translations['pl'],
            "charts": {"total_value_chart": "", "b2b_waterfall_chart": ""},
            "generation_date": "2025-01-01",
            "report_type": "advanced",
            "checklists": {"title": "Test", "items": []}
        })
        
        self.assertIn("Dochód (przed ZUS)", rendered_html)
        self.assertIn("Podstawa do opodatkowania", rendered_html)
        
        # Check for a specific value from the steps, properly formatted
        # Value: 184500.00 -> "184 500,00 zł"
        self.assertIn("184 500,00", rendered_html.replace("\xa0", " "))

    @patch('weasyprint.HTML')
    def test_advanced_report_contains_checklist_positive(self, mock_html):
        """Sprawdza, czy raport zaawansowany zawiera sekcję z checklistą."""
        mock_html_instance = mock_html.return_value
        mock_html_instance.write_pdf.return_value = b"dummy pdf content"

        # Render the template with checklist data
        with open('dane_wejsciowe_kalkulator.json', 'r', encoding='utf-8') as f:
            checklists = json.load(f).get('checklists', {}).get('pl', {})

        rendered_html = self.pdf_generator.template.render({
            **self.mock_data,
            "t": self.pdf_generator.translations['pl'],
            "charts": {"total_value_chart": "", "b2b_waterfall_chart": ""},
            "generation_date": "2025-01-01",
            "report_type": "advanced",
            "checklists": checklists
        })

        self.assertIn("Checklista Przed Przejściem na B2B", rendered_html)
        self.assertIn("Zabezpiecz poduszkę finansową", rendered_html)

    @patch('weasyprint.HTML')
    def test_basic_report_does_not_contain_checklist_negative(self, mock_html):
        """Sprawdza, czy raport podstawowy NIE zawiera checklisty."""
        mock_html_instance = mock_html.return_value
        mock_html_instance.write_pdf.return_value = b"dummy pdf content"

        rendered_html = self.pdf_generator.template.render({
            **self.mock_data,
            "t": self.pdf_generator.translations['pl'],
            "charts": {"total_value_chart": "", "b2b_waterfall_chart": ""},
            "generation_date": "2025-01-01",
            "report_type": "basic"
            # No checklist data passed for basic report
        })
        
        self.assertNotIn("Checklista Przed Przejściem na B2B", rendered_html)

    def test_format_currency_filter_neutral(self):
        """Test the Jinja2 currency formatting filter."""
        self.assertEqual(format_currency(12345.67), "12 345,67 zł")
        self.assertEqual(format_currency(1000), "1 000,00 zł")
        self.assertEqual(format_currency("not a number"), "not a number")

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_generate_charts_basic_report_positive(self, mock_show, mock_savefig):
        """Test that only the total value chart is generated for a basic report."""
        charts = self.pdf_generator._generate_charts(
            self.mock_data['b2b_results'],
            self.mock_data['uop_results'],
            self.pdf_generator.translations['pl'],
            report_type='basic'
        )
        self.assertIn('total_value_chart', charts)
        self.assertIsNotNone(charts['total_value_chart'])
        self.assertIsNone(charts['b2b_waterfall_chart'])
        self.assertEqual(mock_savefig.call_count, 1)

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_generate_charts_advanced_report_positive(self, mock_show, mock_savefig):
        """Test that both charts are generated for an advanced report."""
        charts = self.pdf_generator._generate_charts(
            self.mock_data['b2b_results'],
            self.mock_data['uop_results'],
            self.pdf_generator.translations['pl'],
            report_type='advanced'
        )
        self.assertIn('total_value_chart', charts)
        self.assertIn('b2b_waterfall_chart', charts)
        self.assertIsNotNone(charts['total_value_chart'])
        self.assertIsNotNone(charts['b2b_waterfall_chart'])
        self.assertEqual(mock_savefig.call_count, 2)

    @patch('matplotlib.pyplot.show')
    def test_advanced_report_contains_detailed_insurance_section_positive(self, mock_show):
        """Sprawdza, czy raport zaawansowany zawiera szczegółową sekcję ubezpieczeń w finalnym PDF."""
        # Arrange
        # Ensure translations are loaded
        t = self.pdf_generator.translations['pl']
        
        # Act
        pdf_output = self.pdf_generator.generate(self.mock_data, report_type='advanced')
        
        # Assert
        # To check the content, we need to extract text from the PDF bytes
        from pypdf import PdfReader
        from io import BytesIO

        reader = PdfReader(BytesIO(pdf_output))
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()

        # Normalize whitespace for easier searching
        pdf_text = " ".join(pdf_text.split())

        # Check for section title (using the key from translations)
        self.assertIn(t['insurance']['title'], pdf_text)
        
        # Check for summary details
        self.assertIn("Profil: Standard", pdf_text)
        self.assertIn("Całkowity miesięczny koszt ubezpieczenia: 680,97 zł", pdf_text.replace('\xa0', ' '))

        # Check for table headers
        self.assertIn(t['insurance']['insurance'], pdf_text)
        self.assertIn(t['insurance']['coverage_details'], pdf_text)
        self.assertIn(t['insurance']['uop_comparison'], pdf_text)
        self.assertIn(t['insurance']['monthly_cost'], pdf_text)

        # Check for specific module data
        self.assertIn("OC zawodowe", pdf_text)
        self.assertIn("Suma ubezpieczenia: 1 000 000 zł", pdf_text)
        self.assertIn("UoP: odp. do 3 pensji", pdf_text)
        self.assertIn("66,67 zł", pdf_text.replace('\xa0', ' '))

        self.assertIn("Prywatne zdrowotne", pdf_text)
        self.assertIn("Rozszerzony pakiet, dostęp do specjalistów", pdf_text)
        self.assertIn("UoP: pakiet standardowy", pdf_text)
        self.assertIn("300,00 zł", pdf_text.replace('\xa0', ' '))

    @patch('weasyprint.HTML')
    def test_basic_report_omits_insurance_section_negative(self, mock_html):
        """Sprawdza, czy sekcja ubezpieczeń jest pomijana w raporcie podstawowym."""
        mock_html_instance = mock_html.return_value
        mock_html_instance.write_pdf.return_value = b"dummy pdf content"

        rendered_html = self.pdf_generator.template.render({
            **self.mock_data,
            "t": self.pdf_generator.translations['pl'],
            "charts": {"total_value_chart": "", "b2b_waterfall_chart": ""},
            "generation_date": "2025-01-01",
            "report_type": "basic"
        })

        self.assertNotIn("Konfiguracja Ubezpieczenia B2B", rendered_html)

if __name__ == '__main__':
    unittest.main()