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
  - **Waterfall Chart**: Visualizes the breakdown of gross income to net income, showing deductions like ZUS, taxes (with detailed breakdown by tax brackets), and other costs.
  - **Break-Even Analysis Chart**: A line chart illustrating the break-even point between B2B and UoP contracts, showing the net difference across various B2B monthly rates.
  - **Sensitivity (Tornado) Chart**: Identifies and visualizes the impact of key parameters (e.g., business costs, vacation days, stoppage months) on the final net income difference, sorted by impact magnitude.
- **Export Results**: Export the detailed comparison to Excel, a basic PDF report, or an advanced PDF report.
- **Internationalized PDF Reports**: The generated PDF report is fully translated into the language selected in the UI (English or Polish).
- **Advanced PDF Report**: Generate a comprehensive, multi-page PDF report with a professional design, including:
    - **Executive Summary & Risk Analysis**: High-level insights and risk assessment.
    - **Narrative Calculation Methodology**: A clear, step-by-step "waterfall" breakdown of how the final B2B net income is calculated.
    - **Advanced Charts**: Includes a bar chart for overall comparison and a waterfall chart visualizing the B2B cash flow.
    - **B2B Checklist**: A practical checklist for individuals transitioning to a B2B contract.
- **Transparent Methodology**: The PDF report includes a dedicated "How we calculated it?" section that breaks down the key steps of the calculation for both B2B and UoP, ensuring full transparency.
- **Break-Even Analysis**: Automatically calculates the minimum B2B invoice amount required to match the total value of an employment contract.
- **Flexible Break-Even Analysis**: Choose to calculate either the B2B invoice amount needed to match a UoP contract, or the UoP gross salary needed to match a B2B contract.

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
3.  **Install Node.js dependencies for the React frontend:**
    ```bash
    cd src/dashboard
    npm install
    cd ../..
    ```
4.  **Install PDF Font (for PDF export functionality):**
    Download `DejaVuSans.ttf` (or another Unicode-compatible font) and place it in the `src/fonts/` directory within the project root. If the `src/fonts/` directory does not exist, it will be created automatically when the Flask app runs.
    You can find `DejaVuSans.ttf` on the official DejaVu Fonts website or other trusted font repositories.

## Usage

1.  **Start the application (both backend and frontend):**
    ```bash
    ./run_app.sh
    ```
    The Flask backend will run on `http://0.0.0.0:5001` and the React frontend will typically open in your browser at `http://localhost:5173`.
    To access the application from other devices in your local network, replace `localhost` with the IP address of the machine running the application (e.g., `http://192.168.1.100:5173`). Ensure your firewall allows connections on ports 5001 and 5173.
2.  Fill in the form with your data and click "Calculate" to see the comparison.
3.  **To stop the application:**
    ```bash
    ./stop_app.sh
    ```

## Development

### Running Tests

To run the backend unit and integration tests (Python):
```bash
pytest
```
**Note on Test Naming Convention:**
Backend tests now follow a naming convention to classify their purpose:
- `_positive`: Tests verifying expected, successful behavior.
- `_negative`: Tests verifying error handling or unexpected/invalid input.
- `_neutral`: Tests with a mixed purpose or where classification is not straightforward.


To run the end-to-end (E2E) tests (JavaScript/Playwright):
```bash
npm run test:e2e
```

### Internationalization (i18n)
The application supports internationalization using `i18next` for the frontend.
-   **Languages**: Currently supports English (`en`) and Polish (`pl`).
-   **Implementation**: Translations are managed in `src/dashboard/src/locales/en/translation.json` and `src/dashboard/src/locales/pl/translation.json`.
-   **Language Switching**: Users can switch languages using the language switcher in the header.

### Code Coverage

To generate code coverage reports for the backend (Python) with detailed classification:
```bash
./scripts/backend_cov.sh
```
This script will display coverage for unit tests, integration tests, and combined tests, along with a summary of positive, negative, and neutral test counts. Current coverage: Unit tests: >85%, Combined (Unit + Integration): >96%.

For JavaScript frontend:
```bash
./scripts/frontend_cov.sh
```
After running frontend tests, open `src/dashboard/coverage/index.html` in your browser to view the detailed report. Current coverage: >85%.

### CORS Configuration

The Flask backend is configured to handle Cross-Origin Resource Sharing (CORS) requests from the frontend. This is managed by the `Flask-Cors` extension, allowing the frontend (typically running on a different port) to communicate with the backend API.

### Project Structure
The project follows a standard Flask application structure:
- `.ai/`: Contains AI-related instructions and session state.
- `src/`: Main application source code.
  - `app.py`: The Flask backend with all calculation logic.
  - `dashboard/`: React frontend application.
    - `src/`: React source code (components, services, etc.).
    - `public/`: Static assets for React.
    - `dist/`: Compiled React application (generated by `npm run build`).
  - `dane_wejsciowe_kalkulator.json`: Data file with all constants and parameters for calculations.
- `tests/`: Unit, integration, and end-to-end tests.
  - `unit/`: Backend unit tests.
  - `integration/`: Backend integration tests.
  - `e2e/`: Frontend end-to-end tests.
- `package.json`: Node.js project configuration and scripts (for root level, e.g., Playwright).
- `playwright.config.js`: Playwright E2E test configuration.