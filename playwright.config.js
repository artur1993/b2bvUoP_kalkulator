
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  timeout: 90000,
  expect: {
    timeout: 10000
  },
  testDir: './tests/e2e',
  webServer: [
    {
      command: "bash -c 'source .venv/bin/activate && FLASK_APP=backend/app.py PYTHONPATH=$(pwd) flask run --host 0.0.0.0 --port 5001'",
      port: 5001,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: 'cd frontend && npm run dev -- --port 5173',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
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
