"""
Base Test Class
Provides common setup and teardown for all test cases
"""
import os
import json
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

class BaseTest:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load test data
        test_data_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_data.json')
        with open(test_data_path, 'r') as f:
            self.test_data = json.load(f)
        
        # Initialize WebDriver
        options = Options()
        if self.config.get('headless', False):
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.config['timeout'])
        
        # Test results
        self.results = []
        
        yield
        
        # Teardown
        self.driver.quit()
    
    def take_screenshot(self, name):
        """Take screenshot for documentation"""
        screenshots_dir = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(screenshots_dir, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(filename)
        return filename
    
    def log_result(self, test_name, status, message=""):
        """Log test result"""
        self.results.append({
            "test_name": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
