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
  - [x] Update `.gitignore`: Add `src/dashboard/node_modules/` and `src/dashboard/dist/`.
  - [x] Update `README.md`: Modify installation and usage instructions.

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
