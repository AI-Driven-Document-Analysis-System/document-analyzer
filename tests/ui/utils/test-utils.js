/**
 * Utility functions for Playwright tests
 */

/**
 * Log in to the application
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {Object} credentials - Login credentials
 * @param {string} credentials.email - User email
 * @param {string} credentials.password - User password
 */
async function login(page, { email, password }) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
}

/**
 * Wait for API response
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} url - API endpoint URL to wait for
 * @param {number} [timeout=10000] - Timeout in milliseconds
 * @returns {Promise<Object>} - Response JSON
 */
async function waitForApiResponse(page, url, timeout = 10000) {
  const response = await page.waitForResponse(
    (response) => 
      response.url().includes(url) && 
      response.status() === 200,
    { timeout }
  );
  return response.json();
}

/**
 * Upload a file using the file input
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} filePath - Path to the file to upload
 * @param {string} [selector='input[type="file"]'] - File input selector
 */
async function uploadFile(page, filePath, selector = 'input[type="file"]') {
  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.click(selector);
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles(filePath);
}

/**
 * Wait for loading to complete
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} [loadingSelector='[data-testid="loading"]'] - Loading indicator selector
 */
async function waitForLoading(page, loadingSelector = '[data-testid="loading"]') {
  await page.waitForSelector(loadingSelector, { state: 'hidden', timeout: 30000 });
}

/**
 * Generate a random string
 * @param {number} length - Length of the random string
 * @returns {string} - Random string
 */
function generateRandomString(length = 10) {
  return Math.random().toString(36).substring(2, 2 + length);
}

module.exports = {
  login,
  waitForApiResponse,
  uploadFile,
  waitForLoading,
  generateRandomString,
};
