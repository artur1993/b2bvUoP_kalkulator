# Project-Specific Information for Gemini

This file contains information relevant to the Gemini AI assistant for this specific project.

# Global token saving rules
- Keep answers as concise as possible
- Code without comments, unless required
- Use technical abbreviations
- Avoid “hello world” examples

## Project Overview
- **Name**: B2B vs UoP IT Calculator 2025
- **Purpose**: Web application for comparing B2B and UoP contracts for IT professionals in Poland.
- **Technologies**: Flask (Python backend), React (JavaScript frontend).

## Key Directories
- `src/app.py`: Main Flask application.
- `src/dashboard/`: React frontend source code.
- `dane_wejsciowe_kalkulator.json`: Data file for calculations.
- `tests/`: Contains all test files (unit, integration, e2e).

## Development Workflow Notes
- All communication with the user is in Polish.
- Code, comments, and documentation within the project are in English.
- Follow the 4-phase development workflow outlined in `instructions.md`.
- Use `data-testid` for robust frontend testing.

## Current State
- All previous tasks related to i18n implementation, testing, and code cleanup are complete.
- The project is ready for further development or deployment.