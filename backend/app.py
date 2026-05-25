from flask import Flask, request, jsonify, send_from_directory, send_file, g
from flask_cors import CORS
from openpyxl import Workbook
from werkzeug.exceptions import HTTPException
import io
import os
import logging
from logging.handlers import RotatingFileHandler
from backend.calculations import (
    calculate_break_even_analysis
)
from backend.services.calculation_service import run_full_calculation
from backend.validation import (
    BreakEvenAnalysisRequest,
    CalculationRequestModel,
    ExcelExportRequest,
    validate,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERNAL_SERVER_ERROR_MESSAGE = "An internal server error occurred."

def get_cors_origins():
    origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')
    return [origin.strip() for origin in origins.split(',') if origin.strip()]

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'frontend/dist'))
CORS(app, origins=get_cors_origins())

# --- Configure Logging ---
file_handler = RotatingFileHandler('flask.log', maxBytes=1024 * 1024 * 10, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

def is_debug_enabled():
    """Enable Flask debug mode only for explicit local development."""
    return os.environ.get('FLASK_ENV') == 'development'

@app.errorhandler(Exception)
def handle_global_error(e):
    """Global error handler to log all unhandled exceptions."""
    if isinstance(e, HTTPException):
        status_code = 404 if e.code == 405 and request.path.startswith('/api/') else e.code
        return jsonify({"error": e.name}), status_code

    app.logger.exception("Unhandled exception")
    return jsonify({"error": INTERNAL_SERVER_ERROR_MESSAGE}), 500

@app.route('/api/calculate/break-even-analysis', methods=['POST'])
@validate(BreakEvenAnalysisRequest)
def break_even_analysis():
    """Endpoint for break-even analysis chart data."""
    try:
        data = g.validated_data
        app.logger.info(f"Received break-even analysis request.")
        uop_data = data.get('uop', {})
        b2b_base_data = data.get('b2b', {})

        analysis_results = calculate_break_even_analysis(uop_data, b2b_base_data)
        return jsonify(analysis_results)
    except Exception:
        app.logger.exception("Error during break-even analysis")
        return jsonify({"error": INTERNAL_SERVER_ERROR_MESSAGE}), 500

@app.route('/api/calculate', methods=['POST'])
@validate(CalculationRequestModel)
def calculate():
    """Main endpoint to calculate and compare B2B vs. UoP earnings with full analysis."""
    try:
        app.logger.info("Received calculation request")
        return jsonify(run_full_calculation(g.validated_data))
    except Exception:
        app.logger.exception("Error during calculation")
        return jsonify({"error": INTERNAL_SERVER_ERROR_MESSAGE}), 500

@app.route('/api/export/excel', methods=['POST'])
@validate(ExcelExportRequest)
def export_to_excel():
    """Exports the calculation results to an Excel file."""
    try:
        data = g.validated_data
        app.logger.info(f"Received request to export to Excel.")
        b2b_results = data.get('b2b_results', {})
        uop_results = data.get('uop_results', {})

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Porównanie B2B vs UoP"

        sheet['A1'] = "Kategoria"
        sheet['B1'] = "B2B"
        sheet['C1'] = "UoP"

        sheet['A2'] = "Total Annual Value"
        sheet['B2'] = b2b_results.get('total_annual_value')
        sheet['C2'] = uop_results.get('total_annual_value')

        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name="kalkulator_wyniki.xlsx", 
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception:
        app.logger.exception("Error exporting to Excel")
        return jsonify({"error": INTERNAL_SERVER_ERROR_MESSAGE}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serves the React frontend."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({"error": "Frontend build not found."}), 404

if __name__ == '__main__':
    app.run(debug=is_debug_enabled(), use_reloader=False, port=5001)
