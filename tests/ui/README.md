# UI Tests for Document Analyzer

This directory contains end-to-end UI tests for the Document Analyzer application using Playwright.

## Prerequisites

- Node.js 16 or higher
- npm 7 or higher
- Playwright browsers

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install Playwright browsers:
   ```bash
   npx playwright install
   ```

3. Copy the example environment file and update with your test credentials:
   ```bash
   cp .env.example .env
   ```

## Running Tests

### Run all tests in headless mode
```bash
npm test
```

### Run tests in UI mode (interactive)
```bash
npm run test:ui
```

### Run tests on specific browser
```bash
npm run test:chrome   # Run on Chrome
npm run test:firefox  # Run on Firefox
npm run test:safari   # Run on Safari
```

### Run tests with tracing (for debugging)
```bash
npm run test:trace
```

### View test report
```bash
npm run test:report
```

## Test Structure

- `tests/auth.spec.js` - Authentication flow tests (login, register, logout)
- `tests/upload.spec.js` - Document upload and processing tests
- `tests/chat.spec.js` - Chat interface and conversation tests

## Writing Tests

1. Use `test.describe` to group related tests
2. Use `test.beforeEach` for common setup
3. Use `page` fixture to interact with the page
4. Use `expect` for assertions
5. Use `page.waitFor*` methods to wait for elements

## Best Practices

- Use data-testid attributes for reliable element selection
- Keep tests independent and isolated
- Use mocks for external services when needed
- Add comments explaining complex test logic
- Use page object model for complex pages

## Debugging

1. Run tests in UI mode for interactive debugging:
   ```bash
   npm run test:ui
   ```

2. Use `page.pause()` to pause test execution

3. Run with trace for detailed execution information:
   ```bash
   npm run test:trace
   ```

4. View traces in the trace viewer:
   ```bash
   npx playwright show-trace test-results/*/trace.zip
   ```
