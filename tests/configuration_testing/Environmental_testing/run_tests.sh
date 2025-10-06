#!/bin/bash

# Create reports directory if it doesn't exist
mkdir -p reports

# Build and run the containers
echo "Starting configuration tests across Python versions..."
docker-compose up --build

# Check the results
echo -e "\nTest Results:"
for version in "3.9" "3.10" "3.11"; do
    echo "Python ${version} results:"
    ls -l reports/python_${version//./}_*
done

echo -e "\nTest complete! Check the 'reports' directory for detailed results."
