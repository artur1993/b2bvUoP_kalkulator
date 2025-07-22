
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  webServer: {
    command: 'python3 src/app.py',
    url: 'http://127.0.0.1:5001',
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://127.0.0.1:5001',
    // Collect coverage for JavaScript files
    coverage: {
      enabled: true,
      outputDir: 'coverage/frontend',
      all: true,
    },
  },
});
