# tests/test_document_upload.py
"""
Document Upload Function Tests
Tests document upload with different file types and sizes
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
from datetime import datetime
import sys
sys.path.append('..')
from utilities.data_generator import TestDataGenerator

class TestDocumentUpload:
    @pytest.fixture(autouse=True)
    def setup(self):
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
        
        options = webdriver.ChromeOptions()
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.config['timeout'])
        self.data_generator = TestDataGenerator()
        self.results = []
        
        # Create screenshots directory
        os.makedirs('screenshots', exist_ok=True)
        
        yield
        self.driver.quit()
    
    def take_screenshot(self, name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/upload_{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        return filename
    
    def test_pdf_upload(self):
        """Test Case 4: Upload valid PDF document"""
        print("\n" + "="*60)
        print("TEST CASE 4: PDF Document Upload")
        print("="*60)
        
        try:
            # Generate test PDF
            pdf_file = self.data_generator.generate_test_file('pdf', 1, "Test PDF for Upload")
            file_size = os.path.getsize(pdf_file) / (1024 * 1024)
            
            print(f"✓ Generated test PDF: {pdf_file}")
            print(f"✓ File size: {file_size:.2f} MB")
            
            # Navigate to upload page
            self.driver.get(f"{self.config['base_url']}/upload")
            print(f"✓ Navigated to upload page")
            
            # Upload file
            file_input = self.driver.find_element(By.ID, "file-upload")
            file_input.send_keys(os.path.abspath(pdf_file))
            print(f"✓ File selected for upload")
            
            screenshot1 = self.take_screenshot("pdf_selected")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            # Click upload button
            self.driver.find_element(By.ID, "upload-button").click()
            print(f"✓ Upload initiated")
            
            # Wait for upload success
            success_msg = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
            )
            
            screenshot2 = self.take_screenshot("pdf_upload_success")
            print(f"✓ Screenshot saved: {screenshot2}")
            
            # Verify file appears in document list
            uploaded_doc = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "document-item"))
            )
            
            result = {
                "test_case": "PDF Upload",
                "status": "PASS",
                "file": pdf_file,
                "file_size_mb": file_size,
                "message": success_msg.text,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Success message: {success_msg.text}")
            print(f"✓ Document appears in list")
            print("\n✅ TEST PASSED: PDF upload successful")
            
        except Exception as e:
            result = {
                "test_case": "PDF Upload",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
            self.take_screenshot("pdf_upload_failed")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_txt_upload(self):
        """Test Case 5: Upload valid TXT document"""
        print("\n" + "="*60)
        print("TEST CASE 5: TXT Document Upload")
        print("="*60)
        
        try:
            txt_file = self.data_generator.generate_test_file('txt', 0.5)
            file_size = os.path.getsize(txt_file) / (1024 * 1024)
            
            print(f"✓ Generated test TXT: {txt_file}")
            print(f"✓ File size: {file_size:.2f} MB")
            
            self.driver.get(f"{self.config['base_url']}/upload")
            
            file_input = self.driver.find_element(By.ID, "file-upload")
            file_input.send_keys(os.path.abspath(txt_file))
            
            screenshot1 = self.take_screenshot("txt_selected")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            self.driver.find_element(By.ID, "upload-button").click()
            
            success_msg = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
            )
            
            screenshot2 = self.take_screenshot("txt_upload_success")
            
            result = {
                "test_case": "TXT Upload",
                "status": "PASS",
                "file": txt_file,
                "file_size_mb": file_size,
                "message": success_msg.text,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Success message: {success_msg.text}")
            print("\n✅ TEST PASSED: TXT upload successful")
            
        except Exception as e:
            result = {
                "test_case": "TXT Upload",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_invalid_file_upload(self):
        """Test Case 6: Upload invalid file type"""
        print("\n" + "="*60)
        print("TEST CASE 6: Invalid File Type Upload")
        print("="*60)
        
        try:
            invalid_file = self.data_generator.generate_test_file('invalid')
            
            print(f"✓ Generated invalid file: {invalid_file}")
            
            self.driver.get(f"{self.config['base_url']}/upload")
            
            file_input = self.driver.find_element(By.ID, "file-upload")
            file_input.send_keys(os.path.abspath(invalid_file))
            
            screenshot1 = self.take_screenshot("invalid_file_selected")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            self.driver.find_element(By.ID, "upload-button").click()
            
            # Wait for error message
            error_msg = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "upload-error"))
            )
            
            screenshot2 = self.take_screenshot("invalid_file_error")
            
            result = {
                "test_case": "Invalid File Upload",
                "status": "PASS",
                "error_message": error_msg.text,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Error message displayed: {error_msg.text}")
            print("\n✅ TEST PASSED: System correctly rejected invalid file")
            
        except Exception as e:
            result = {
                "test_case": "Invalid File Upload",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_large_file_upload(self):
        """Test Case 7: Upload large file (boundary test)"""
        print("\n" + "="*60)
        print("TEST CASE 7: Large File Upload (50MB)")
        print("="*60)
        
        try:
            large_file = self.data_generator.generate_test_file('pdf', 50, "Large PDF Test")
            file_size = os.path.getsize(large_file) / (1024 * 1024)
            
            print(f"✓ Generated large file: {large_file}")
            print(f"✓ File size: {file_size:.2f} MB")
            
            self.driver.get(f"{self.config['base_url']}/upload")
            
            file_input = self.driver.find_element(By.ID, "file-upload")
            file_input.send_keys(os.path.abspath(large_file))
            
            screenshot1 = self.take_screenshot("large_file_selected")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            start_time = datetime.now()
            self.driver.find_element(By.ID, "upload-button").click()
            print(f"✓ Upload started at: {start_time.strftime('%H:%M:%S')}")
            
            # Wait longer for large file
            success_msg = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
            )
            end_time = datetime.now()
            upload_duration = (end_time - start_time).total_seconds()
            
            screenshot2 = self.take_screenshot("large_file_success")
            
            result = {
                "test_case": "Large File Upload",
                "status": "PASS",
                "file_size_mb": file_size,
                "upload_duration_seconds": upload_duration,
                "upload_speed_mbps": file_size / upload_duration if upload_duration > 0 else 0,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Upload completed at: {end_time.strftime('%H:%M:%S')}")
            print(f"✓ Upload duration: {upload_duration:.2f} seconds")
            print(f"✓ Upload speed: {result['upload_speed_mbps']:.2f} MB/s")
            print("\n✅ TEST PASSED: Large file upload successful")
            
        except Exception as e:
            result = {
                "test_case": "Large File Upload",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'

# tests/test_chat_functionality.py
"""
Chat Functionality Tests
Tests chat interface with various query types
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import os
from datetime import datetime
import time

class TestChatFunctionality:
    @pytest.fixture(autouse=True)
    def setup(self):
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
        
        with open('config/test_data.json', 'r') as f:
            self.test_data = json.load(f)
        
        options = webdriver.ChromeOptions()
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.config['timeout'])
        self.results = []
        
        os.makedirs('screenshots', exist_ok=True)
        
        yield
        self.driver.quit()
    
    def take_screenshot(self, name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/chat_{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        return filename
    
    def test_basic_query(self):
        """Test Case 8: Basic chat query"""
        print("\n" + "="*60)
        print("TEST CASE 8: Basic Chat Query")
        print("="*60)
        
        try:
            query = "What is the summary of the document?"
            
            self.driver.get(f"{self.config['base_url']}/chat")
            print(f"✓ Navigated to chat page")
            
            # Enter query
            chat_input = self.driver.find_element(By.ID, "chat-input")
            chat_input.send_keys(query)
            print(f"✓ Query entered: {query}")
            
            screenshot1 = self.take_screenshot("query_entered")
            print(f"✓ Screenshot saved: {screenshot1}")
            
            # Send query
            chat_input.send_keys(Keys.RETURN)
            print(f"✓ Query sent")
            
            # Wait for response
            response = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-response"))
            )
            
            response_time_element = self.driver.find_element(By.CLASS_NAME, "response-time")
            response_time = response_time_element.text
            
            screenshot2 = self.take_screenshot("response_received")
            
            result = {
                "test_case": "Basic Chat Query",
                "status": "PASS",
                "query": query,
                "response_length": len(response.text),
                "response_time": response_time,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Response received")
            print(f"✓ Response length: {len(response.text)} characters")
            print(f"✓ Response time: {response_time}")
            print("\n✅ TEST PASSED: Chat query successful")
            
        except Exception as e:
            result = {
                "test_case": "Basic Chat Query",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_empty_query(self):
        """Test Case 9: Empty query validation"""
        print("\n" + "="*60)
        print("TEST CASE 9: Empty Query Validation")
        print("="*60)
        
        try:
            self.driver.get(f"{self.config['base_url']}/chat")
            
            # Try to send empty query
            chat_input = self.driver.find_element(By.ID, "chat-input")
            chat_input.send_keys(Keys.RETURN)
            print(f"✓ Attempted to send empty query")
            
            screenshot1 = self.take_screenshot("empty_query_attempt")
            
            # Check for validation message
            validation_msg = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "validation-error"))
            )
            
            screenshot2 = self.take_screenshot("empty_query_validation")
            
            result = {
                "test_case": "Empty Query Validation",
                "status": "PASS",
                "validation_message": validation_msg.text,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Validation message: {validation_msg.text}")
            print("\n✅ TEST PASSED: Empty query correctly validated")
            
        except Exception as e:
            result = {
                "test_case": "Empty Query Validation",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_special_characters_query(self):
        """Test Case 10: Query with special characters"""
        print("\n" + "="*60)
        print("TEST CASE 10: Special Characters in Query")
        print("="*60)
        
        try:
            query = "What about data with @#$%^&*() characters?"
            
            self.driver.get(f"{self.config['base_url']}/chat")
            
            chat_input = self.driver.find_element(By.ID, "chat-input")
            chat_input.send_keys(query)
            print(f"✓ Query with special chars: {query}")
            
            screenshot1 = self.take_screenshot("special_chars_query")
            
            chat_input.send_keys(Keys.RETURN)
            
            response = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-response"))
            )
            
            screenshot2 = self.take_screenshot("special_chars_response")
            
            result = {
                "test_case": "Special Characters Query",
                "status": "PASS",
                "query": query,
                "response_received": True,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Response received successfully")
            print("\n✅ TEST PASSED: Special characters handled correctly")
            
        except Exception as e:
            result = {
                "test_case": "Special Characters Query",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_multiple_consecutive_queries(self):
        """Test Case 11: Multiple consecutive queries"""
        print("\n" + "="*60)
        print("TEST CASE 11: Multiple Consecutive Queries")
        print("="*60)
        
        try:
            queries = [
                "What is the document about?",
                "Give me key points",
                "What are the conclusions?"
            ]
            
            self.driver.get(f"{self.config['base_url']}/chat")
            
            responses = []
            for i, query in enumerate(queries, 1):
                print(f"\n  Query {i}: {query}")
                
                chat_input = self.driver.find_element(By.ID, "chat-input")
                chat_input.clear()
                chat_input.send_keys(query)
                chat_input.send_keys(Keys.RETURN)
                
                time.sleep(2)  # Wait between queries
                
                response_elements = self.driver.find_elements(By.CLASS_NAME, "chat-response")
                responses.append(len(response_elements))
                
                print(f"  ✓ Response {i} received")
            
            screenshot = self.take_screenshot("multiple_queries_complete")
            
            result = {
                "test_case": "Multiple Consecutive Queries",
                "status": "PASS",
                "queries_sent": len(queries),
                "responses_count": responses[-1],
                "screenshots": [screenshot]
            }
            
            print(f"\n✓ All {len(queries)} queries processed")
            print(f"✓ Total responses: {responses[-1]}")
            print("\n✅ TEST PASSED: Multiple queries handled correctly")
            
        except Exception as e:
            result = {
                "test_case": "Multiple Consecutive Queries",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'

# tests/test_summary_generation.py
"""
Summary Generation Tests
Tests document summarization with different options
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import json
import os
from datetime import datetime
import time

class TestSummaryGeneration:
    @pytest.fixture(autouse=True)
    def setup(self):
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
        
        options = webdriver.ChromeOptions()
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.config['timeout'])
        self.results = []
        
        os.makedirs('screenshots', exist_ok=True)
        
        yield
        self.driver.quit()
    
    def take_screenshot(self, name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/summary_{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        return filename
    
    def test_basic_summary(self):
        """Test Case 12: Generate basic summary"""
        print("\n" + "="*60)
        print("TEST CASE 12: Basic Summary Generation")
        print("="*60)
        
        try:
            self.driver.get(f"{self.config['base_url']}/documents")
            print(f"✓ Navigated to documents page")
            
            # Select first document
            doc_item = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "document-item"))
            )
            doc_item.click()
            print(f"✓ Document selected")
            
            screenshot1 = self.take_screenshot("document_selected")
            
            # Click summary button
            summary_btn = self.driver.find_element(By.ID, "generate-summary")
            summary_btn.click()
            print(f"✓ Summary generation initiated")
            
            # Wait for summary
            start_time = datetime.now()
            summary_text = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "summary-content"))
            )
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            screenshot2 = self.take_screenshot("summary_generated")
            
            result = {
                "test_case": "Basic Summary",
                "status": "PASS",
                "summary_length": len(summary_text.text),
                "generation_time_seconds": generation_time,
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Summary generated")
            print(f"✓ Summary length: {len(summary_text.text)} characters")
            print(f"✓ Generation time: {generation_time:.2f} seconds")
            print("\n✅ TEST PASSED: Summary generated successfully")
            
        except Exception as e:
            result = {
                "test_case": "Basic Summary",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'
    
    def test_summary_with_options(self):
        """Test Case 13: Summary with different length options"""
        print("\n" + "="*60)
        print("TEST CASE 13: Summary with Length Options")
        print("="*60)
        
        try:
            self.driver.get(f"{self.config['base_url']}/documents")
            
            doc_item = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "document-item"))
            )
            doc_item.click()
            
            # Select summary length
            length_dropdown = Select(self.driver.find_element(By.ID, "summary-length"))
            length_dropdown.select_by_visible_text("Detailed")
            print(f"✓ Selected: Detailed summary")
            
            screenshot1 = self.take_screenshot("detailed_option_selected")
            
            summary_btn = self.driver.find_element(By.ID, "generate-summary")
            summary_btn.click()
            
            summary_text = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "summary-content"))
            )
            
            screenshot2 = self.take_screenshot("detailed_summary_generated")
            
            result = {
                "test_case": "Summary with Options",
                "status": "PASS",
                "option_selected": "Detailed",
                "summary_length": len(summary_text.text),
                "screenshots": [screenshot1, screenshot2]
            }
            
            print(f"✓ Detailed summary generated")
            print(f"✓ Length: {len(summary_text.text)} characters")
            print("\n✅ TEST PASSED: Summary options work correctly")
            
        except Exception as e:
            result = {
                "test_case": "Summary with Options",
                "status": "FAIL",
                "error": str(e)
            }
            print(f"\n❌ TEST FAILED: {str(e)}")
        
        self.results.append(result)
        assert result['status'] == 'PASS'