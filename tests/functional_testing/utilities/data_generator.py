"""
Test Data Generator
Generates realistic test data for functional testing
"""

from faker import Faker
import random
import string
import json
import os
from datetime import datetime

fake = Faker()

class TestDataGenerator:
    def __init__(self):
        self.fake = fake
        
    def generate_user_data(self, valid=True):
        """Generate user registration data"""
        if valid:
            return {
                "name": self.fake.name(),
                "email": self.fake.email(),
                "password": self.generate_strong_password(),
                "phone": self.fake.phone_number(),
                "address": self.fake.address()
            }
        else:
            # Generate invalid data for negative testing
            invalid_types = [
                {"name": "", "email": "invalid-email", "password": "123"},  # Invalid format
                {"name": "A", "email": "test@test", "password": "short"},   # Too short
                {"name": "X" * 256, "email": self.fake.email(), "password": "x"},  # Too long
                {"name": None, "email": None, "password": None},  # Null values
                {"name": self.fake.name(), "email": "test@", "password": ""},  # Empty password
            ]
            return random.choice(invalid_types)
    
    def generate_strong_password(self, length=12):
        """Generate a strong password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    def generate_test_file(self, file_type, size_mb=1, content=None):
        """Generate test files of different types"""
        os.makedirs('test_files', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if file_type == 'pdf':
            filename = f'test_files/test_document_{timestamp}.pdf'
            # Create a simple PDF (requires reportlab)
            try:
                from reportlab.pdfgen import canvas
                c = canvas.Canvas(filename)
                c.drawString(100, 750, content or "Test PDF Document")
                c.save()
            except ImportError:
                # Fallback: create dummy file
                with open(filename, 'wb') as f:
                    f.write(b'%PDF-1.4\n' + b'X' * (size_mb * 1024 * 1024))
        
        elif file_type == 'txt':
            filename = f'test_files/test_document_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                text_content = content or self.fake.text(max_nb_chars=size_mb * 1024 * 1024)
                f.write(text_content)
        
        elif file_type == 'docx':
            filename = f'test_files/test_document_{timestamp}.docx'
            try:
                from docx import Document
                doc = Document()
                doc.add_paragraph(content or self.fake.text(max_nb_chars=1000))
                doc.save(filename)
            except ImportError:
                # Fallback: create dummy file
                with open(filename, 'wb') as f:
                    f.write(b'PK' + b'X' * (size_mb * 1024 * 1024))
        
        elif file_type == 'invalid':
            filename = f'test_files/test_invalid_{timestamp}.xyz'
            with open(filename, 'wb') as f:
                f.write(b'INVALID FILE CONTENT')
        
        return filename
    
    def generate_chat_queries(self):
        """Generate various chat queries for testing"""
        queries = [
            "What is the summary of the document?",
            "Find information about the main topic",
            "Extract key points from the text",
            "What are the conclusions?",
            "Explain the methodology used",
            "",  # Empty query
            "A" * 5000,  # Very long query
            "Test with special characters: @#$%^&*()",
            "Unicode test: 你好世界 مرحبا",
            self.fake.sentence(),
        ]
        return queries
    
    def generate_boundary_data(self):
        """Generate boundary value test cases"""
        return {
            "min_values": {
                "text_length": 1,
                "file_size": 1,  # 1 byte
                "name_length": 1
            },
            "max_values": {
                "text_length": 10000,
                "file_size": 100,  # 100 MB
                "name_length": 255
            },
            "edge_cases": {
                "empty_string": "",
                "null_value": None,
                "special_chars": "!@#$%^&*()_+-=[]{}|;:',.<>?/~`",
                "unicode": "测试数据 テスト данные परीक्षण",
                "sql_injection": "' OR '1'='1",
                "xss_attempt": "<script>alert('XSS')</script>"
            }
        }
    
    def save_test_data(self, filename='test_data.json'):
        """Save generated test data to file"""
        test_data = {
            "valid_users": [self.generate_user_data(True) for _ in range(5)],
            "invalid_users": [self.generate_user_data(False) for _ in range(5)],
            "chat_queries": self.generate_chat_queries(),
            "boundary_data": self.generate_boundary_data(),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        return test_data

if __name__ == "__main__":
    generator = TestDataGenerator()
    
    print("=" * 60)
    print("TEST DATA GENERATOR")
    print("=" * 60)
    
    # Generate test data
    print("\n1. Generating user test data...")
    test_data = generator.save_test_data('config/test_data.json')
    print(f"✓ Generated {len(test_data['valid_users'])} valid users")
    print(f"✓ Generated {len(test_data['invalid_users'])} invalid users")
    
    # Generate test files
    print("\n2. Generating test files...")
    pdf_file = generator.generate_test_file('pdf', 1, "Sample PDF Document for Testing")
    print(f"✓ Generated PDF: {pdf_file}")
    
    txt_file = generator.generate_test_file('txt', 1)
    print(f"✓ Generated TXT: {txt_file}")
    
    invalid_file = generator.generate_test_file('invalid')
    print(f"✓ Generated Invalid File: {invalid_file}")
    
    print("\n3. Test data saved to: config/test_data.json")
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)