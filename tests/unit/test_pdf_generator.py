import unittest
import os
from src.pdf_generator.generator import PDFReportGenerator

class TestPDFReportGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = PDFReportGenerator(
            template_path='src/pdf_generator/templates',
            static_path='src/pdf_generator/static'
        )
        self.test_data = {
            "b2b_results": {
                "calkowita_roczna_wartosc": 120000,
                "roczne_netto_na_reke": 80000,
                "roczny_podatek": 20000,
                "roczny_zus": 20000,
            },
            "uop_results": {
                "calkowita_roczna_wartosc": 100000,
                "roczne_netto_na_reke": 70000,
                "roczny_podatek": 15000,
                "roczny_zus": 15000,
            },
            "input_data": {
                "b2b": {
                    "faktura_miesieczna": 10000,
                    "forma_opodatkowania": "liniowy",
                },
                "uop": {
                    "wynagrodzenie_brutto": 8000,
                }
            }
        }

    def test_generate_pdf(self):
        pdf_bytes = self.generator.generate(self.test_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)

        # Check if the PDF starts with the PDF magic number
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))

if __name__ == '__main__':
    unittest.main()