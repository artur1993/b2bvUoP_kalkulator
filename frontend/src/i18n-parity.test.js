import { expect, test } from 'vitest';
import en from './locales/en/translation.json';
import pl from './locales/pl/translation.json';

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
  
  // Using meaningful error message if they differ
  const missingInPl = enKeys.filter(k => !plKeys.includes(k));
  const missingInEn = plKeys.filter(k => !enKeys.includes(k));
  
  if (missingInPl.length > 0 || missingInEn.length > 0) {
    console.error('Missing in PL:', missingInPl);
    console.error('Missing in EN:', missingInEn);
  }

  expect(plKeys).toEqual(enKeys);
});
