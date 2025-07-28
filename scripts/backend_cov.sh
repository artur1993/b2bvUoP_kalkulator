#!/bin/bash

echo "--- Pokrycie testów jednostkowych (Unit Tests) ---"
pytest tests/unit/ --cov=src --cov-report=term-missing

echo ""
echo "--- Pokrycie testów integracyjnych (Integration Tests) ---"
pytest tests/integration/ --cov=src --cov-report=term-missing

echo ""
echo "--- Łączne pokrycie testów (Unit + Integration Tests) ---"
pytest tests/ --cov=src --cov-report=term-missing

echo ""
echo "--- Podsumowanie klasyfikacji testów ---"

# Collect all test names
all_tests=$(pytest --collect-only -q | grep "::test_")

positive_tests=$(echo "$all_tests" | grep "_positive" | wc -l)
negative_tests=$(echo "$all_tests" | grep "_negative" | wc -l)
neutral_tests=$(echo "$all_tests" | grep "_neutral" | wc -l)

total_tests=$((positive_tests + negative_tests + neutral_tests))

echo "Testy pozytywne: $positive_tests"
echo "Testy negatywne: $negative_tests"
echo "Testy neutralne: $neutral_tests"
echo "Wszystkie testy: $total_tests"

if [ "$total_tests" -gt 0 ]; then
    positive_ratio=$(awk "BEGIN {printf \"%.2f\", ($positive_tests / $total_tests) * 100}")
    negative_ratio=$(awk "BEGIN {printf \"%.2f\", ($negative_tests / $total_tests) * 100}")
    neutral_ratio=$(awk "BEGIN {printf \"%.2f\", ($neutral_tests / $total_tests) * 100}")

    echo "Stosunek testów:"
    echo "  Pozytywne: ${positive_ratio}%"
    echo "  Negatywne: ${negative_ratio}%"
    echo "  Neutralne: ${neutral_ratio}%"
fi
