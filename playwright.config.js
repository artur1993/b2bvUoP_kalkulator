
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  timeout: 90000,
  expect: {
    timeout: 10000
  },
  testDir: './tests/e2e',
  webServer: {
    command: 'python src/app.py & npm run dev --prefix src/dashboard',
    url: 'http://localhost:5173',
    reuseExistingServer: false,
  },
  use: {
    baseURL: 'http://localhost:5173',
    // Collect coverage for JavaScript files
    coverage: {
      enabled: true,
      outputDir: 'coverage/frontend',
      all: true,
    },
    trace: 'on-first-retry',
  },
});
