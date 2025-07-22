# B2B vs UoP IT Calculator 2025

A simple web application to compare the net income between B2B and Standard Employment Contract (UoP) for IT professionals in Poland for the year 2025.

## Description

This tool provides a detailed and accurate financial comparison, taking into account taxes, social security (ZUS), benefits, and paid time off, based on the regulations for 2025.

### Key Features
- **Advanced B2B Options**: Customize your B2B calculation with company-provided benefits (paid leave, healthcare, training budget) and your own custom tax-deductible benefits.
- **Multiple Tax Forms**: Supports all common tax forms for B2B in Poland: Ryczałt 12% (IT), Liniowy 19%, Skala Podatkowa, and IP Box 5%.
- **Comprehensive Visualizations**: 
  - A grouped bar chart to compare the total annual value of UoP, standard B2B, and B2B with benefits.
  - A pie chart showing the distribution of your B2B revenue (net income, taxes, ZUS, etc.).
- **Export Results**: Export the detailed comparison to PDF or Excel for your records.
- **Break-Even Analysis**: Automatically calculates the minimum B2B invoice amount required to match the total value of an employment contract.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd b2v_UoP_kalkulator
    ```
2.  **Create a virtual environment and install Python dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Install Node.js dependencies (for frontend and E2E tests):**
    ```bash
    npm install
    ```

## Usage

1.  **Run the Flask application:**
    ```bash
    python src/app.py
    ```
2.  **Open your web browser** and navigate to `http://127.0.0.1:5001`.
3.  Fill in the form with your data and click "Calculate" to see the comparison.

## Development

### Running Tests

To run the backend unit and integration tests (Python):
```bash
pytest
```

To run the end-to-end (E2E) tests (JavaScript/Playwright):
```bash
npm run test:e2e
```

### Code Coverage

To generate code coverage reports:

For Python backend:
```bash
pytest --cov=src tests/unit tests/integration
```
This will display a summary in the console.

For JavaScript frontend:
```bash
npm run test:e2e
```
After running E2E tests, open `coverage/frontend/index.html` in your browser to view the detailed report.

### Project Structure
The project follows a standard Flask application structure:
- `.ai/`: Contains AI-related instructions and session state.
- `src/`: Main application source code.
  - `app.py`: The Flask backend with all calculation logic.
  - `templates/`: HTML templates.
  - `static/`: CSS and JavaScript files.
- `tests/`: Unit, integration, and end-to-end tests.
  - `unit/`: Backend unit tests.
  - `integration/`: Backend integration tests.
  - `e2e/`: Frontend end-to-end tests.
- `dane_wejsciowe_kalkulator.json`: Data file with all constants and parameters for calculations.
- `package.json`: Node.js project configuration and scripts.
- `playwright.config.js`: Playwright E2E test configuration.
