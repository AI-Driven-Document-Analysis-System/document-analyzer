// @ts-check
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  
  reporter: [
    ['list'],
    ['html', { open: 'on-failure' }]
  ],
  
  use: {
    actionTimeout: 0,
    navigationTimeout: 0,
    trace: 'off',
    screenshot: 'on',
    video: 'off',
    viewport: { width: 1280, height: 720 },
  },
  
  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Disable web security for testing
        bypassCSP: true,
        // Ignore HTTPS errors
        ignoreHTTPSErrors: true,
      },
    },
  ],
});

// Disable test timeouts
process.env.PLAYWRIGHT_TEST_TIMEOUT = '0';
process.env.PLAYWRIGHT_TEST_RETRIES = '0';
process.env.CI = 'false';
