import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class TestChatFunctionality:
    @pytest.fixture(autouse=True)
    def setup(self):
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
        
        options = webdriver.ChromeOptions()
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.config['timeout'])
        yield
        self.driver.quit()

    def test_chat_query_response(self):
        try:
            self.driver.get(f"{self.config['base_url']}/chat")
            
            # Send a test query
            chat_input = self.driver.find_element(By.ID, "chat-input")
            chat_input.send_keys("What is this document about?")
            send_button = self.driver.find_element(By.ID, "send-button")
            send_button.click()
            
            # Wait for response
            response = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-response"))
            )
            assert response.text != ""
            
        except Exception as e:
            pytest.fail(f"Chat query test failed: {str(e)}")

    def test_chat_history(self):
        try:
            self.driver.get(f"{self.config['base_url']}/chat")
            
            # Send multiple messages
            messages = ["Hello", "What is the main topic?", "Thank you"]
            for msg in messages:
                chat_input = self.driver.find_element(By.ID, "chat-input")
                chat_input.send_keys(msg)
                send_button = self.driver.find_element(By.ID, "send-button")
                send_button.click()
                self.wait.until(
                    EC.presence_of_element_located((By.xpath, f"//div[contains(text(), '{msg}')]"))
                )
            
        except Exception as e:
            pytest.fail(f"Chat history test failed: {str(e)}")
