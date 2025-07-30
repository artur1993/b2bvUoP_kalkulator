import '@testing-library/jest-dom';
import i18n from './src/i18n'; // Import your i18n configuration
import enTranslation from './src/locales/en/translation.json';
import plTranslation from './src/locales/pl/translation.json';

// Polyfill for ResizeObserver
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserver;

// Initialize i18n for tests
i18n.init({
  lng: 'en', // default language for tests
  fallbackLng: 'en',
  debug: false,
  interpolation: {
    escapeValue: false, // React already safes from xss
  },
  resources: {
    en: {
      translation: enTranslation,
    },
    pl: {
      translation: plTranslation,
    },
  },
});