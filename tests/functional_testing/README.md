# Functional Testing for Document Analyzer

This directory contains automated functional tests for the Document Analyzer application. The tests are written using Playwright and cover various aspects of the application including authentication, document upload, chat functionality, and summary generation.

## Prerequisites

- Node.js (v14 or later)
- npm (v6 or later)
- Playwright browsers (will be installed automatically)

## Setup

1. Navigate to the functional_testing directory:
   ```bash
   cd tests/functional_testing
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Install Playwright browsers:
   ```bash
   npx playwright install
   ```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests for a specific feature
```bash
# Run authentication tests only
npx playwright test tests/auth.spec.js

# Run document upload tests only
npx playwright test tests/document-upload.spec.js

# Run chat and summary tests only
npx playwright test tests/chat-and-summary.spec.js
```

### Run tests in UI mode
```bash
npx playwright test --ui
```

### Generate HTML report
```bash
npx playwright show-report
```

## Test Structure

- `tests/auth.spec.js` - Tests for user registration and login
- `tests/document-upload.spec.js` - Tests for document upload functionality
- `tests/chat-and-summary.spec.js` - Tests for chat and summary generation

## Viewing Results

After running the tests, you can view the HTML report by running:

```bash
npx playwright show-report
```

This will open a browser window with a detailed test report showing:
- Test execution status (passed/failed)
- Test duration
- Screenshots of failed tests
- Execution traces
- Console logs

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The test results will be available in the CI/CD logs and can be published as artifacts for further analysis.

## Test Data Management

Test data is generated using Faker.js for realistic but random test data. The test files include various test cases covering:
- Valid and invalid user credentials
- Different file types (PDF, DOCX, TXT, JPG)
- Various chat scenarios
- Different summary generation options

## Troubleshooting

If you encounter any issues:
1. Make sure all dependencies are installed
2. Check that the application is running on the expected URL (default: http://localhost:3000)
3. Verify that test data files exist in the specified locations
4. Check the test reports for detailed error information
