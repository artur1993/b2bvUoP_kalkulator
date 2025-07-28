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


- [ ] **Task 15: Zwiększenie pokrycia testów jednostkowych do 95%**
- [ ] **Task 16: Wczytanie przygotowanego planu dla zadań po zwiększeniu pokrycia testów jednostkowych**

## OTHER:

- [ ] **Task 14: Implement E2E Tests with Playwright**
