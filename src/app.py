import json
from flask import Flask, request, jsonify, send_from_directory, send_file, g
from flask_cors import CORS
from openpyxl import Workbook
import io
import os
import logging
import time
from logging.handlers import RotatingFileHandler
from src.analysis import generate_executive_summary, get_risk_analysis, get_methodology, get_checklist
from src.calculations import (
    calculate_b2b_results,
    calculate_uop_results,
    calculate_break_even,
    calculate_uop_break_even,
    _get_float,
    calculate_break_even_analysis,
    calculate_sensitivity_analysis
)
from src.pension_calculator import calculate_pension_details
from src.validation import validate_calculation_request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'src/dashboard/dist'))
CORS(app)

# --- Configure Logging ---
file_handler = RotatingFileHandler('flask.log', maxBytes=1024 * 1024 * 10, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

@app.errorhandler(Exception)
def handle_global_error(e):
    """Global error handler to log all unhandled exceptions."""
    app.logger.exception(f"Unhandled Exception: {e}")
    return jsonify({"error": "An unexpected server error occurred."}), 500

@app.route('/api/calculate/break-even-analysis', methods=['POST'])
def break_even_analysis():
    """Endpoint for break-even analysis chart data."""
    try:
        data = request.get_json()
        app.logger.info(f"Received break-even analysis request.")
        app.logger.debug(f"Break-even analysis request data: {data}")
        uop_data = data.get('uop', {})
        b2b_base_data = data.get('b2b', {})

        analysis_results = calculate_break_even_analysis(uop_data, b2b_base_data)
        return jsonify(analysis_results)
    except Exception as e:
        app.logger.exception("Error during break-even analysis:")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate/sensitivity-analysis', methods=['POST'])
def sensitivity_analysis():
    """Endpoint for sensitivity analysis chart data."""
    try:
        data = request.get_json()
        app.logger.info(f"Received sensitivity analysis request.")
        app.logger.debug(f"Sensitivity analysis request data: {data}")
        base_b2b_data = data.get('b2b', {})
        base_uop_data = data.get('uop', {})

        analysis_results = calculate_sensitivity_analysis(base_b2b_data, base_uop_data)
        return jsonify(analysis_results)
    except Exception as e:
        app.logger.exception("Error during sensitivity analysis:")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
@validate_calculation_request
def calculate():
    """Main endpoint to calculate and compare B2B vs. UoP earnings with full analysis."""
    try:
        request_data = g.validated_data
        lang = request_data.get('language', 'pl')

        # Initialize b2b_data and uop_data from request_data
        b2b_data = request_data.get('b2b', {}).copy()
        uop_data = request_data.get('uop', {}).copy()
        calculation_mode = request_data.get('calculation_mode', 'uop_to_b2b')

        app.logger.info(f"Received calculation request with mode: {calculation_mode}")
        app.logger.debug(f"Full request data: {request_data}")

        b2b_results = calculate_b2b_results(b2b_data)
        uop_results = calculate_uop_results(uop_data)
        
        break_even_point = -1
        break_even_key = "break_even_invoice_amount" # Default value
        if calculation_mode == 'uop_to_b2b':
            break_even_point = calculate_break_even(uop_results['total_annual_value'], b2b_data)
            break_even_key = "break_even_invoice_amount"
        elif calculation_mode == 'b2b_to_uop':
            break_even_point = calculate_uop_break_even(b2b_results['total_annual_value'], uop_data)
            break_even_key = "break_even_gross_salary"

        # Generate advanced analysis
        summary = generate_executive_summary(b2b_results, uop_results, break_even_point, lang)
        risk_analysis = get_risk_analysis(lang)
        methodology = get_methodology(lang)
        checklist = get_checklist(lang)

        response_data = {
            "b2b_results": b2b_results,
            "uop_results": uop_results,
            break_even_key: break_even_point,
            "analysis": {
                "summary": summary,
                "risk": risk_analysis,
                "methodology": methodology,
                "checklist": checklist
            },
            "comments": "Comparison and full analysis generated successfully."
        }

        if b2b_data.get('equalizePension'):
            app.logger.info("Equalize pension requested.")
            uop_gross_salary = _get_float(uop_data, 'monthly_gross_salary', 0)
            pension_details = calculate_pension_details(uop_gross_salary)
            response_data['pension_details'] = pension_details

        return jsonify(response_data)
    except Exception as e:
        app.logger.exception("Error during calculation:")
        return jsonify({"error": str(e) if app.debug else "An internal server error occurred."}), 500

@app.route('/api/export/excel', methods=['POST'])
def export_to_excel():
    """Exports the calculation results to an Excel file."""
    try:
        data = request.get_json()
        app.logger.info(f"Received request to export to Excel.")
        app.logger.debug(f"Export to Excel request data: {data}")
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
    except Exception as e:
        app.logger.exception("Error exporting to Excel:")
        return jsonify({"error": "Failed to generate Excel file."}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serves the React frontend."""
    app.logger.debug(f"Serving path: {path}")
    app.logger.debug(f"Static folder: {app.static_folder}")
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            app.logger.error(f"index.html not found at: {index_path}")
            return jsonify({"error": "Frontend build not found. Please run 'npm run build' in src/dashboard."}), 404

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5001)