# Configuration Testing with Docker

This folder contains the setup for testing the application across different Python versions using Docker containers.

## Running Tests

1. Build and run the containers:
```bash
docker-compose up --build
```

2. Check results in the `reports` folder:
- Each Python version has its own report folder
- Screenshots are saved in `reports/screenshots`
- HTML reports show test results
- Summary files provide quick overview

## Test Coverage

- Python version compatibility (3.9, 3.10, 3.11)
- Dependency resolution
- Performance consistency
- Feature compatibility

## Evidence Collection

- Automated screenshots of test results
- HTML test reports
- Summary files with timestamps
