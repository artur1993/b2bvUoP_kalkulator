# Project Context

The goal of this project is to create a comprehensive B2B vs. UoP (Employment Contract) calculator for the Polish IT market for the year 2025.

The application will be a web-based tool with:
- A Python (Flask) backend responsible for all calculation logic.
- A simple HTML, Bootstrap 5, and Vanilla JS frontend for user interaction.

The core functionality is to provide a clear and realistic comparison of the total financial viability of working on a B2B contract versus a standard employment contract. The calculation will take into account all key aspects, including taxes, social security contributions (ZUS), benefits, paid time off, and the cost of lost benefits.

All calculations must be based *exclusively* on the data provided in the `dane_wejsciowe_kalkulator.json` file. The application should not fetch data from external sources or make assumptions about financial parameters.