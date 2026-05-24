# D04 — useReducer na froncie

## Cel
Wprowadzić `useReducer` (lub `useReducer + Context`) dla state managementu w `App.jsx`. Pozbyć się 8+ `useState`.

## Źródło
[AUDYT.md §5.1](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/dashboard/src/App.jsx](../../../src/dashboard/src/App.jsx)
- Cel: `src/dashboard/src/state/calculatorReducer.js`
- Cel: `src/dashboard/src/state/CalculatorContext.jsx` (opcjonalnie)
- Cel: `src/dashboard/src/hooks/useUrlState.js` (z walidacją parametrów — D05 powiązany)

## Zmiana

`calculatorReducer.js`:
```javascript
export const initialState = {
  calculationMode: 'uop_to_b2b',
  b2bData: { ... },
  uopData: { ... },
  results: null,
  loading: false,
  error: null,
};

export function calculatorReducer(state, action) {
  switch (action.type) {
    case 'SET_B2B_FIELD': ...
    case 'SET_UOP_FIELD': ...
    case 'SET_AGE': ...
    case 'CALCULATE_START': ...
    case 'CALCULATE_SUCCESS': ...
    case 'CALCULATE_FAILURE': ...
    default: return state;
  }
}
```

`App.jsx`:
```javascript
const [state, dispatch] = useReducer(calculatorReducer, initialState);
```

Komponenty dostają `dispatch` zamiast 5 handlerów.

## Acceptance
- [x] `App.jsx` ma ≤2 `useState` (np. tylko dark mode toggle)
- [x] Reducer testowalny w izolacji
- [x] `CalculatorForm` dostaje `state` + `dispatch` zamiast 12 propów
- [x] Frontend testy zielone

## Test plan
```bash
cd src/dashboard && npm test -- --run
./run_app.sh  # smoke
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A04 (insurance configurator nie istnieje, mniej state)
