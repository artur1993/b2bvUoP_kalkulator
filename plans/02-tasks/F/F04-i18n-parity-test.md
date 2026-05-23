# F04 — i18n parity test

## Cel
Test, który sprawdza, że `en/translation.json` i `pl/translation.json` mają **identyczny** zestaw kluczy.

## Źródło
[AUDYT.md §6.4](../../../AUDYT.md), [AUDYT_UZUPELNIENIE.md §1.4](../../../AUDYT_UZUPELNIENIE.md)

## Pliki
- `src/dashboard/src/__tests__/i18n-parity.test.js` (nowy)
- (Opcjonalnie) `npm run test:i18n` w `package.json`

## Zmiana

```javascript
import en from '../locales/en/translation.json';
import pl from '../locales/pl/translation.json';

function flattenKeys(obj, prefix = '') {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === 'object' && v !== null
      ? flattenKeys(v, `${prefix}${k}.`)
      : [`${prefix}${k}`]
  );
}

test('en and pl translations have identical keys', () => {
  const enKeys = flattenKeys(en).sort();
  const plKeys = flattenKeys(pl).sort();
  expect(plKeys).toEqual(enKeys);
});
```

Dodatkowo: test sprawdzający, że żaden komponent **nie generuje `missingKey`** w runtime (przeciw fallback'om i18next). Można użyć `i18next` opcji `parseMissingKeyHandler` i throw error.

## Acceptance
- [ ] Test parity zielony
- [ ] Test `missingKey` zielony (po smoke render wszystkich komponentów)

## Test plan
```bash
cd src/dashboard && npm test -- i18n-parity
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A01-A05, B01, D05, D06 (klucze stabilne)
