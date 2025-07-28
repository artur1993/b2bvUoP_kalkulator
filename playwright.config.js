
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  timeout: 90000,
  expect: {
    timeout: 10000
  },
  testDir: './tests/e2e',
  webServer: {
    command: 'npm run dev -- --port 5173',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
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
