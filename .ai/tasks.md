# Tasks

## Phase 1: Project Setup & Backend

- [x] **Task 1: Initial Project Setup**
- [x] **Task 2: Backend - Flask Application Setup**
- [x] **Task 3: Backend - Calculation Logic**
- [x] **Task 4: Backend - Testing**

## Phase 2: Frontend

- [x] **Task 5: Frontend - HTML Structure and Form**
  - [x] Added new sections for custom benefits and company benefits.
  - [x] Moved 'Advanced B2B Options' section to the bottom of the form and improved its visibility.
- [x] **Task 6: Frontend - JavaScript Logic**
  - [x] Implemented dynamic rendering of company benefits.
  - [x] Updated form data collection to include new fields.
  - [x] Added client-side validation for benefit values.
  - [x] Implemented new visualizations (grouped bar chart, pie chart).

## Phase 3: Finalization

- [x] **Task 7: Documentation**
  - [x] Updated `README.md` with new features.
- [x] **Task 8: Final Review**

## Phase 4: Comprehensive Testing

- [x] **Task 9: Implement Advanced Test Scenarios**
  - [x] Refactored existing tests into a new structure.
  - [x] Created `tests/integration/test_scenarios.py`.
  - [x] Implemented the 20 specified test scenarios.
  - [x] Added detailed assertions for all key calculation components in each test.
  - [x] Ensured all tests are runnable via `pytest`.

## Phase 5: UI Modernization with React (Initial Attempt - React Source Missing)

- [x] **Task 10: Integrate React SPA**
  - [x] Update `.ai/context.md` to describe the new Flask + React architecture.
  - [x] Refactor `src/app.py` to serve the React SPA.
  - [x] Update `README.md` to reflect the new architecture.
  - [x] Remove unused Jinja2/Bootstrap files.
  *Note: This phase completed the integration of the pre-built React SPA, but the source code for the React application was later found to be missing, necessitating a rebuild.* 

## Phase 6: Rebuild React Frontend from Scratch

- [x] **Task 11: Scaffold New React Application**
  - [x] Cleanup: Remove the existing `src/dashboard/dist` directory.
  - [x] Scaffold New React App: Create new directory structure for React source code inside `src/dashboard/`.
  - [x] Create Core Files: Generate initial files for the React application (`package.json`, `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `index.html`, `src/main.jsx`, `src/App.jsx`, `src/index.css`, placeholder components, `api.js`).
  - [x] Update `.gitignore`: Add `src/dashboard/node_modules/` and `src/dashboard/dist/`.n  - [x] Update `README.md`: Modify installation and usage instructions.

- [x] **Task 12: Implement Core UI Components (Form & State)**
  - [x] Refactor `App.jsx` to manage application state and handle calculations.
  - [x] Implement `CalculatorForm.jsx` with all necessary input fields and styling.
  - [x] Create reusable `Input.jsx`, `Select.jsx`, and `Checkbox.jsx` components.

- [x] **Task 13: Implement Results Display and Charts**
  - [x] Implement `ResultsDisplay.jsx` to show detailed results and export options.
  - [x] Implement `ComparisonChart.jsx` for visual data representation.
  - [x] Refactor `App.jsx` to handle export functions.
  - [x] Update dependencies to include `file-saver`.

- [x] **Task 15: Create Component Tests for ResultsDisplay.jsx**
  - [x] Create `src/dashboard/src/components/ResultsDisplay.test.jsx`.
  - [x] Implement tests for rendering, currency formatting, conditional logic, and handling of missing props.
  - [x] Ensure all tests pass using the project's component testing framework.

## Phase 7: Visual Tests Debugging

- [x] **Task 14: Debug Playwright Visual Tests**
  - [x] Investigate and fix `net::ERR_CONNECTION_REFUSED` errors in Playwright tests.
  - [x] Debug CSS style assertion failures (e.g., `box-shadow` or `border-color` for input fields).
  - [x] Ensure all visual tests in `tests/e2e/visual.spec.js` pass successfully.

## Phase 8: API Testing & Coverage

- [x] **Task 16: Implement Integration Tests for Flask API**
  - [x] Install `pytest-flask`.
  - [x] Create `tests/integration/test_api.py`.
  - [x] Add tests for successful requests (200 OK).
  - [x] Add tests for invalid requests (400 Bad Request).
  - [x] Verify JSON response structure.
  - [x] Generate a code coverage report for `src/app.py`.
  - [x] **Sub-task 16.1: Increase Coverage for `src/app.py`**
    - [x] Refine test for `skala` tax form in `calculate_b2b_results` to cover `else` branch (line 82).
    - [x] Refine test for `ip_box` tax form in `calculate_b2b_results` to cover line 93.
    - [x] Re-examine `test_calculate_break_even_not_found` to ensure it covers lines 238-241.
    - [x] Add test for `serve` endpoint to cover root path `/` (line 309).
    - [x] Update `.coveragerc` to explicitly exclude lines 280, 285-288, and 312.
    - [x] Re-run coverage report and analyze results.

## Phase 9: Test Classification and Automation

- [x] **Task 17: Classify Backend Tests**
  - [x] Analyze and classify Python backend tests as positive, negative, or neutral.
  - [x] Rename test functions according to the `_positive`, `_negative`, `_neutral` convention.
- [x] **Task 18: Automate Backend Coverage Reporting**
  - [x] Create `scripts/backend_cov.sh` to generate detailed backend coverage reports.
  - [x] Ensure the script displays separate coverage for unit, integration, and combined tests.
  - [x] Add test classification summary (positive, negative, neutral counts) to the `backend_cov.sh` output.
- [x] **Task 19: Automate Frontend Coverage Reporting**
  - [x] Create `scripts/frontend_cov.sh` to generate frontend code coverage reports.
- [x] **Task 20: Fix Frontend Tests**
  - [x] Debug and fix failing frontend tests in `src/components/CalculatorForm.test.jsx`.
  - [x] Ensure all frontend tests pass successfully.
- [x] **Task 21: Update Documentation for Test Changes**
  - [x] Update `README.md` to reflect the new test naming conventions and the new coverage scripts.
- [x] **Task 22: Manual Application Verification**
  - [x] Successfully launched and manually verified the application's functionality.

## Phase 10: Internationalization (i18n)

- [x] **Task 23: Install i18n Dependencies**
  - [x] Installed `i18next`, `react-i18next`, `i18next-browser-languagedetector`.
- [x] **Task 24: Create Translation File Structure**
  - [x] Created `src/locales/en/` and `src/locales/pl/` directories.
  - [x] Created `src/locales/en/translation.json` with English translations.
  - [x] Created `src/locales/pl/translation.json` with Polish translations.
- [x] **Task 25: Configure and Integrate i18next**
  - [x] Created `src/i18n.js` configuration file.
  - [x] Updated `src/main.jsx` to import `i18n.js`.
  - [x] Fixed `setupTests.js` to correctly initialize i18n for tests (using `import` instead of `require`).
- [x] **Task 26: Implement Language Switcher and Refactor Components**
  - [x] Created `src/components/LanguageSwitcher.jsx` component.
  - [x] Refactored `src/components/Header.jsx` to use `useTranslation` and include `LanguageSwitcher`.
  - [x] Refactored `src/components/CalculatorForm.jsx` to use `useTranslation` and translated texts.
  - [x] Refactored `src/components/ResultsDisplay.jsx` to use `useTranslation` and translated texts.
  - [x] Refactored `src/components/ComparisonChart.jsx` to use `useTranslation` and translated texts.
- [x] **Task 27: Create i18n Component Tests**
  - [x] Created `src/components/Header.test.jsx` for i18n component testing.
  - [x] Fixed `CalculatorForm.test.jsx` to use translated texts in assertions.
  - [x] Fixed `App.test.jsx` to use translated texts in assertions.

## Phase 11: Application Debugging and Stability

- [x] **Task 28: Resolve 500 Internal Server Error and CORS Issue**
  - [x] Configured Flask logging to always capture errors.
  - [x] Changed Flask backend port to 5001 to avoid conflicts.
  - [x] Updated frontend API base URL to point to the new backend port.
  - [x] Implemented Flask-CORS to resolve cross-origin issues.

## Phase 12: Implement Flexible Break-Even Analysis

- [x] **Task 29: Implement B2B to UoP Break-Even Calculation in Backend**
  - [x] Added `calculate_uop_break_even` function to `src/app.py`.
  - [x] Modified `/api/calculate` endpoint to accept `calculation_mode` parameter and use `calculate_uop_break_even` when `b2b_to_uop` mode is selected.
- [x] **Task 30: Implement Calculation Mode Selection in Frontend**
  - [x] Added radio buttons for calculation mode selection in `src/dashboard/src/components/CalculatorForm.jsx`.
  - [x] Updated `src/dashboard/src/App.jsx` to manage `calculationMode` state and pass it to `CalculatorForm`.
  - [x] Updated `src/dashboard/src/services/api.js` to send `calculation_mode` to the backend.
  - [x] Updated translation files (`src/dashboard/src/locales/en/translation.json`, `src/dashboard/src/locales/pl/translation.json`) with new translation keys for calculation modes.
- [x] **Task 31: Update Results Display for Flexible Break-Even Analysis**
  - [x] Modified `src/dashboard/src/components/ResultsDisplay.jsx` to dynamically display break-even point based on `calculationMode`.
  - [x] Updated `src/dashboard/src/App.jsx` to pass `calculationMode` to `ResultsDisplay`.
  - [x] Updated translation files (`src/dashboard/src/locales/en/translation.json`, `src/dashboard/src/locales/pl/translation.json`) with new translation keys for break-even titles and subtitles.
- [x] **Task 32: Update Frontend Tests for Flexible Break-Even Analysis**
  - [x] Updated `src/dashboard/src/components/ResultsDisplay.test.jsx` to handle dynamic break-even text and test both calculation modes.
  - [x] Fixed import path for `i18n.js` in `src/dashboard/src/components/ResultsDisplay.test.jsx`.
  - [x] Updated `src/dashboard/src/components/CalculatorForm.test.jsx` to pass `calculationMode` to `CalculatorForm` in tests.
  - [x] Fixed whitespace issue in `formatCurrencyForTest` in `src/dashboard/src/components/ResultsDisplay.test.jsx`.
- [x] **Task 33: Update Documentation for Flexible Break-Even Analysis**
  - [x] Updated `README.md` to describe the new flexible break-even analysis feature.

## Phase 13: Network Access

- [x] **Task 34: Configure Backend for Network Access**
  - [x] Modified `run_app.sh` to make Flask listen on `0.0.0.0`.
- [x] **Task 35: Adjust Frontend API Base URL**
  - [x] Changed `API_BASE_URL` in `src/dashboard/src/services/api.js` back to a relative path (`/api`).
- [x] **Task 36: Update Frontend Tests for Relative API Path**
  - [x] Updated `src/dashboard/src/services/api.test.js` to expect relative API paths in assertions.
- [x] **Task 37: Update Documentation for Network Access**
  - [x] Updated `README.md` with instructions for accessing the application from other devices in the local network.

## Phase 14: PDF Report Generation

- [x] **Task 38: Implement Professional PDF Report Generation**
  - [x] Created `src/pdf_generator.py` with `PDFReport` class.
  - [x] Implemented title page, input summary, financial comparison, and charts pages.
  - [x] Integrated `pdf_generator.py` with `/api/export/pdf` endpoint in `src/app.py`.n  - [x] Added `matplotlib` to `requirements.txt` and installed it.
  - [x] Fixed relative import issue in `src/app.py`.

## Phase 15: Hotfix

- [x] **Task 39: Fix PDF Generator Module Import**
  - [x] Corrected `ModuleNotFoundError` by changing the import statement in `src/app.py` to a relative import.
  - [x] Updated the `PDFReportGenerator` instantiation to use absolute paths to ensure access to templates and static files.
  - [x] Verified the fix by running all backend tests successfully.

## Phase 16: Advanced PDF Report

- [x] **Task 40: Implement Advanced PDF Report**
  - [x] **Sub-task 40.1: Update `dane_wejsciowe_kalkulator.json` with `analiza_ryzyka` and `rekomendacje` sections.**
  - [x] **Sub-task 40.2: Create `src/analysis.py` with `generate_executive_summary` and `get_risk_analysis` functions.**
  - [x] **Sub-task 40.3: Modify `src/dashboard/src/components/ResultsDisplay.jsx` to add new button.**
  - [x] **Sub-task 40.4: Modify `src/dashboard/src/App.jsx` to add `handleExportAdvancedPdf` function.**
  - [x] **Sub-task 40.5: Modify `src/dashboard/src/services/api.js` to add `exportToAdvancedPdf` function.**
  - [x] **Sub-task 40.6: Modify `src/app.py` to add new `/api/export/pdf/advanced` endpoint.**
  - [x] **Sub-task 40.7: Modify `src/pdf_generator/generator.py` to update `generate` method.**
  - [x] **Sub-task 40.8: Modify `src/pdf_generator/templates/report.html` to add conditional rendering.**
  - [x] **Sub-task 40.9: Modify `tests/unit/test_pdf_generator.py` to add new test cases.**
  - [x] **Sub-task 40.10: Update `src/dashboard/src/locales/en/translation.json` and `src/dashboard/src/locales/pl/translation.json` with new translation keys.**

## Phase 17: Improve Test Coverage

- [x] **Task 41: Improve Backend Test Coverage**
  - [x] **Sub-task 41.1: Create `tests/unit/test_analysis.py` and add unit tests for `src/analysis.py`.**
  - [x] **Sub-task 41.2: Create `tests/unit/test_app_utils.py` and add unit tests for `_get_float` function in `src/app.py`.**
  - [x] **Sub-task 41.3: Add integration tests for error paths in `/api/calculate`, `/api/export/excel`, `/api/export/pdf` and `/api/export/pdf/advanced` in `tests/integration/test_api.py`.**
- [x] **Task 42: Improve Frontend Test Coverage**
  - [x] **Sub-task 42.1: Fix failing tests in `src/App.test.jsx` and `src/components/ResultsDisplay.test.jsx` by updating button names and adding advanced PDF test.**

## Phase 18: Advanced Analytics

- [x] **Task 43: Implement Waterfall Chart**
  - [x] **Sub-task 43.1: Modify `calculate_b2b_results` and `calculate_uop_results` in `src/app.py` to return detailed steps.**
  - [x] **Sub-task 43.2: Create `src/dashboard/src/components/WaterfallChart.jsx` component.**
  - [x] **Sub-task 43.3: Integrate `WaterfallChart.jsx` into `App.jsx`.**
- [x] **Task 44: Implement Break-Even Analysis Chart**
  - [x] **Sub-task 44.1: Create `/api/calculate/break-even-analysis` endpoint in `src/app.py`.**
  - [x] **Sub-task 44.2: Create `src/dashboard/src/components/BreakEvenChart.jsx` component.**
  - [x] **Sub-task 44.3: Integrate `BreakEvenChart.jsx` into `App.jsx`.**
- [x] **Task 45: Implement Sensitivity (Tornado) Analysis Chart**
  - [x] **Sub-task 45.1: Create `/api/calculate/sensitivity-analysis` endpoint in `src/app.py`.**
  - [x] **Sub-task 45.2: Create `src/dashboard/src/components/SensitivityChart.jsx` component.**
  - [x] **Sub-task 45.3: Integrate `SensitivityChart.jsx` into `App.jsx`.**
- [x] **Task 46: Implement Tests for New Analytics Features**
  - [x] **Sub-task 46.1: Create `tests/unit/test_calculation_details.py` to test detailed calculation results.**
  - [x] **Sub-task 46.2: Create `tests/unit/test_analysis_endpoints.py` to test new analysis endpoints.**
  - [x] **Sub-task 46.3: Create component tests for `WaterfallChart.jsx`, `BreakEvenChart.jsx`, and `SensitivityChart.jsx`.**
  - [x] **Sub-task 46.4: Fixed all failing backend tests and ensured all tests pass.**
- [x] **Task 47: Update Translations**
  - [x] **Sub-task 47.1: Add new translation keys to `en/translation.json` and `pl/translation.json`.**

## Phase 19: Implement Pension Equalization Feature

- [x] **Task 48: Implement Calculation Logic (Backend)**
  - [x] Create `src/pension_calculator.py`
  - [x] Integrate with `app.py`
- [x] **Task 49: Implement User Interface (Frontend)**
  - [x] Modify `src/App.jsx`
  - [x] Modify `src/components/CalculatorForm.jsx`
  - [x] Modify `src/components/ResultsDisplay.jsx`
- [x] **Task 50: Integrate with PDF Report**
  - [x] Update `report.html`
  - [x] Update `generator.py` and `app.py`
- [x] **Task 51: Implement Test Plan**
  - [x] Unit Tests for Backend (`tests/unit/test_pension_calculator.py`)
  - [x] Integration Tests for `app.py`
  - [x] Component Tests for Frontend (`src/components/CalculatorForm.test.jsx`)
- [x] **Task 52: Debugging and Fixes**
  - [x] Fix TypeError in `src/app.py`
  - [x] Fix i18n translation issue in frontend

## Phase 20: Code Refactoring and Quality Improvement

- [x] **Task 53: Centralize Calculation Logic**
  - [x] Ensure `src/calculations.py` is the single source of truth for all calculation logic.
  - [x] Refactor `src/app.py` to import and use calculation functions from `src/calculations.py`.
  - [x] Remove duplicated calculation functions from `src/app.py`.
  - [x] Run all tests to verify that the refactoring did not introduce regressions.

- [x] **Task 54: Enhance Logging**
  - [x] **Backend:** Add `INFO` and `DEBUG` level logs in `src/app.py` endpoints to record incoming request parameters.
  - [x] **Frontend:** Uncomment and enhance `console.error` calls in `src/dashboard/src/services/api.js` and `src/dashboard/src/App.jsx` to provide more context on failed API requests.

- [x] **Task 55: Update Documentation**
  - [x] Update `README.md` to include a description of the "Pension Equalization" feature.
  - [x] Add comprehensive docstrings to all public functions in `src/app.py`, `src/calculations.py`, and `src/analysis.py`, explaining their purpose, parameters, and return values.

- [x] **Task 56: Clean Up Project**
  - [x] Verify if `tests/e2e/calculator.spec.js` and `tests/e2e/calculator_e2e.spec.js` are redundant and delete them if confirmed.
  - [x] Perform a project-wide search for unnecessary commented-out code blocks and remove them.
