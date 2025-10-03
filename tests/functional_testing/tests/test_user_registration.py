"""
User Registration Function Tests
Tests user registration with valid and invalid data
"""
import os
import sys
import json
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import BaseTest from the tests directory
from tests.functional_testing.tests.base_test import BaseTest


class TestUserRegistration(BaseTest):
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        # Get the base directory of the test file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load configuration
        config_path = os.path.join(base_dir, '..', 'config', 'config.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Load test data
        test_data_path = os.path.join(base_dir, '..', 'config', 'test_data.json')
        with open(test_data_path, 'r') as f:
            self.test_data = json.load(f)
        
        # Initialize WebDriver
        options = webdriver.ChromeOptions()
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.config['timeout'])
        
        # Test results
        self.results = []
        
        yield
        
        # Teardown
        self.driver.quit()
    
    def take_screenshot(self, name):
        """Take screenshot for documentation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/registration_{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        return filename
    
    def test_valid_registration(self):
        """Test Case 1: User registration with valid data"""
        print("\n" + "="*60)
        print("TEST CASE 1: Valid User Registration")
        print("="*60)
        
        user_data = self.test_data['valid_users'][0]
        
        try:
            # Navigate to registration page
            self.driver.get(f"{self.config['base_url']}/register")
            print(f"✓ Navigated to: {self.config['base_url']}/register")
            
            # Fill registration form
            self.driver.find_element(By.NAME, "name").send_keys(user_data['name'])
            self.driver.find_element(By.NAME, "email").send_keys(user_data['email'])
            self.driver.find_element(By.NAME, "password").send_keys(user_data['password'])
            print(f"✓ Form filled with valid data")
            print(f"  Name: {user_data['name']}")
            print(f"  Email: {user_data['email']}")
            
            screenshot1 = self.take_screenshot("valid_form_filled")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            # Submit form
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            print("✓ Registration form submitted")
            
            # Wait for success message
            success_msg = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
            )
            
            screenshot2 = self.take_screenshot("valid_registration_success")
            print(f"✓ Screenshot saved: {screenshot2}")
            
            result = {
                "test_case": "Valid Registration",
                "status": "PASS",
                "user_data": user_data,
                "message": success_msg.text,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Success message: {success_msg.text}")
            print("\n✅ TEST PASSED: Valid user registration successful")
            
        except Exception as e:
            result = {
                "test_case": "Valid Registration",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
            self.take_screenshot("valid_registration_failed")
        
        self.results.append(result)
        assert result['status'] == 'PASS', f"Registration failed: {result.get('error', 'Unknown error')}"
    
    def test_invalid_email_registration(self):
        """Test Case 2: Registration with invalid email format"""
        print("\n" + "="*60)
        print("TEST CASE 2: Invalid Email Registration")
        print("="*60)
        
        invalid_user = self.test_data['invalid_users'][0]
        
        try:
            self.driver.get(f"{self.config['base_url']}/register")
            print(f"✓ Navigated to registration page")
            
            # Fill with invalid email
            self.driver.find_element(By.NAME, "name").send_keys("Test User")
            self.driver.find_element(By.NAME, "email").send_keys("invalid-email")
            self.driver.find_element(By.NAME, "password").send_keys("ValidPass123!")
            print(f"✓ Form filled with invalid email: invalid-email")
            
            screenshot1 = self.take_screenshot("invalid_email_form")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            # Submit form
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for error message
            error_msg = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-error"))
            )
            
            screenshot2 = self.take_screenshot("invalid_email_error")
            print(f"✓ Screenshot saved: {screenshot2}")
            
            result = {
                "test_case": "Invalid Email",
                "status": "PASS",
                "error_message": error_msg.text,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Error message displayed: {error_msg.text}")
            print("\n✅ TEST PASSED: System correctly rejected invalid email")
            
        except Exception as e:
            result = {
                "test_case": "Invalid Email",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_empty_fields_registration(self):
        """Test Case 3: Registration with empty fields"""
        print("\n" + "="*60)
        print("TEST CASE 3: Empty Fields Registration")
        print("="*60)
        
        try:
            self.driver.get(f"{self.config['base_url']}/register")
            print(f"✓ Navigated to registration page")
            
            # Submit empty form
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            print("✓ Submitted form with empty fields")
            
            screenshot1 = self.take_screenshot("empty_fields_submit")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            # Check for validation errors
            errors = self.driver.find_elements(By.CSS_SELECTOR, ".field-error")
            
            result = {
                "test_case": "Empty Fields",
                "status": "PASS" if len(errors) > 0 else "FAIL",
                "errors_found": len(errors),
                "error_messages": [e.text for e in errors],
                "screenshots": [screenshot1]
            }
            
            print(f"✓ Validation errors found: {len(errors)}")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error.text}")
            
            print("\n✅ TEST PASSED: System validates required fields")
            
        except Exception as e:
            result = {
                "test_case": "Empty Fields",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def generate_report(self):
        """Generate test report"""
        report = {
            "test_suite": "User Registration Tests",
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r['status'] == 'PASS'),
            "failed": sum(1 for r in self.results if r['status'] == 'FAIL'),
            "results": self.results
        }
        
        with open('reports/registration_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*60)
        print("USER REGISTRATION TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {(report['passed']/report['total_tests']*100):.1f}%")
        print("="*60)
        
        return report

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=reports/registration_report.html"])