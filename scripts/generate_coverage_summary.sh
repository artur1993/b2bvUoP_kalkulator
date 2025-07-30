#!/bin/bash

# Argumenty: 1 - Pokrycie unit, 2 - Pokrycie integration, 3 - Pokrycie combined, 4 - Pokrycie funkcji
UNIT_COV=$1
INT_COV=$2
COMBINED_COV=$3
FUNCTION_COV=$4 # Nowy argument

echo "DEBUG: generate_coverage_summary.sh received arguments:"
echo "DEBUG: UNIT_COV=$UNIT_COV"
echo "DEBUG: INT_COV=$INT_COV"
echo "DEBUG: COMBINED_COV=$COMBINED_COV"
echo "DEBUG: FUNCTION_COV=$FUNCTION_COV"

echo ""
echo "--- Podsumowanie Pokrycia Testami ---"
echo ""
echo "| Metryka                  | Testy Jednostkowe | Testy Integracyjne | Testy Łączne (Unit + Integration) |"
echo "|--------------------------|-------------------|--------------------|-----------------------------------|"
echo "| Pokrycie Kodu (Liniowe)  | ${UNIT_COV}%      | ${INT_COV}%       | ${COMBINED_COV}%                  |"
echo "| Pokrycie Funkcji         | ${FUNCTION_COV}%  | ${FUNCTION_COV}%  | ${FUNCTION_COV}%                  |"
echo ""
echo ""
echo "*Pokrycie Metod jest mierzone przez pokrycie liniowe wewnątrz tych metod. 100% pokrycia liniowego w funkcji oznacza, że wszystkie jej ścieżki wykonania zostały przetestowane.*"
echo ""
