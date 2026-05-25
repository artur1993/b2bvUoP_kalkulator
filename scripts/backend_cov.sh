#!/bin/bash

# --- Testy Jednostkowe ---
echo "--- Pokrycie testów jednostkowych (Unit Tests) ---"
echo "Poniższa lista 'Missing' wskazuje linie kodu niepokryte testami, co oznacza, że zawierające je funkcje nie są w pełni przetestowane."
UNIT_COV_OUTPUT=$(pytest --color=no tests/unit/ --cov=backend --cov-report=term-missing 2>&1)
echo "$UNIT_COV_OUTPUT"
UNIT_COV=$(echo "$UNIT_COV_OUTPUT" | grep 'TOTAL' | awk '{print $NF}' | sed 's/%//')

# --- Testy Integracyjne ---
echo ""
echo "--- Pokrycie testów integracyjnych (Integration Tests) ---"
echo "Poniższa lista 'Missing' wskazuje linie kodu niepokryte testami, co oznacza, że zawierające je funkcje nie są w pełni przetestowane."
INT_COV_OUTPUT=$(pytest --color=no tests/integration/ --cov=backend --cov-report=term-missing 2>&1)
echo "$INT_COV_OUTPUT"
INT_COV=$(echo "$INT_COV_OUTPUT" | grep 'TOTAL' | awk '{print $NF}' | sed 's/%//')

# --- Testy Łączne ---
echo ""
echo "--- Łączne pokrycie testów (Unit + Integration Tests) ---"
echo "Poniższa lista 'Missing' wskazuje linie kodu niepokryte testami, co oznacza, że zawierające je funkcje nie są w pełni przetestowane."
COMBINED_COV_OUTPUT=$(pytest --color=no tests/ --cov=backend --cov-report=term-missing 2>&1)
echo "$COMBINED_COV_OUTPUT"
COMBINED_COV=$(echo "$COMBINED_COV_OUTPUT" | grep 'TOTAL' | awk '{print $NF}' | sed 's/%//')

# --- Pokrycie Funkcji (Function Coverage) ---
echo ""
echo "--- Pokrycie Funkcji (Function Coverage) ---"
echo "Poniższa lista 'Missing' wskazuje linie kodu, które nie zostały wykonane. W kontekście pokrycia funkcji, oznacza to, że funkcje zawierające te linie nie zostały w pełni wywołane lub przetestowane."
FUNCTION_COV_OUTPUT=$(pytest --color=no --cov=backend --cov-report=term-missing 2>&1)
echo "$FUNCTION_COV_OUTPUT"

# Generowanie raportu JSON dla pokrycia funkcji
coverage run --source=backend -m pytest tests/
coverage json -o coverage_report.json

# Obliczanie procentowego pokrycia funkcji
FUNCTION_PERCENTAGE=$(python scripts/calculate_function_coverage.py coverage_report.json backend)
echo "Procentowe pokrycie funkcji: ${FUNCTION_PERCENTAGE}%"

# --- Podsumowanie Klasyfikacji ---
echo ""
echo "--- Podsumowanie klasyfikacji testów ---"
all_tests_output=$(pytest --color=no --collect-only -q | grep "::test_")
total_tests=$(echo "$all_tests_output" | wc -l)

positive_tests=$(echo "$all_tests_output" | grep "_positive" | wc -l)
negative_tests=$(echo "$all_tests_output" | grep "_negative" | wc -l)
neutral_tests=$(echo "$all_tests_output" | grep "_neutral" | wc -l)

labeled_tests=$((positive_tests + negative_tests + neutral_tests))
unlabeled_tests=$((total_tests - labeled_tests))

echo "Testy pozytywne: $positive_tests"
echo "Testy negatywne: $negative_tests"
echo "Testy neutralne: $neutral_tests"
echo "Testy nieoznaczone: $unlabeled_tests"
echo "Wszystkie testy: $total_tests"

if [ "$total_tests" -gt 0 ]; then
    positive_ratio=$(awk "BEGIN {printf \"%.2f\", ($positive_tests / $total_tests) * 100}")
    negative_ratio=$(awk "BEGIN {printf \"%.2f\", ($negative_tests / $total_tests) * 100}")
    neutral_ratio=$(awk "BEGIN {printf \"%.2f\", ($neutral_tests / $total_tests) * 100}")
    unlabeled_ratio=$(awk "BEGIN {printf \"%.2f\", ($unlabeled_tests / $total_tests) * 100}")

    echo "Stosunek testów:"
    echo "  Pozytywne: ${positive_ratio}%"
    echo "  Negatywne: ${negative_ratio}%"
    echo "  Neutralne: ${neutral_ratio}%"
    echo "  Nieoznaczone: ${unlabeled_ratio}%"
fi

# --- Wygenerowanie Tabeli Podsumowującej ---
echo "DEBUG: UNIT_COV=${UNIT_COV}"
echo "DEBUG: INT_COV=${INT_COV}"
echo "DEBUG: COMBINED_COV=${COMBINED_COV}"
echo "DEBUG: FUNCTION_PERCENTAGE before passing: ${FUNCTION_PERCENTAGE}"
./scripts/generate_coverage_summary.sh "$UNIT_COV" "$INT_COV" "$COMBINED_COV" "$FUNCTION_PERCENTAGE"