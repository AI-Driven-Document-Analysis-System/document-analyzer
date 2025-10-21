import asyncio
import os
from typing import Optional, Tuple, Dict
from gradio_client import Client, handle_file

class DocumentClassifier:
    
    def __init__(self):
        """Initialize the classifier client"""
        self.space_name = "RavindiG/document_classification"
        self.client = None
        print(f"[Classification] Initialized for Space: {self.space_name}")
    
    def initialize_sync_client(self):
        """Initialize Gradio client (call once at startup)"""
        try:
            self.client = Client(self.space_name)
            print(f"[Classification] Gradio client initialized successfully")
            return True
        except Exception as e:
            print(f"[Classification] Failed to initialize client: {e}")
            return False

    async def classify_document(self, file_path: str) -> Optional[Tuple[str, Dict]]:
        """
        Classify document directly from file path
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple of (document_type, confidence_scores) or None if failed
        """
        try:
            if not os.path.exists(file_path):
                print(f"[Classification] File not found: {file_path}")
                return None
                
            print(f"[Classification] Calling API for {file_path}")
            
            # Call Gradio API in executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._call_gradio_predict,
                file_path
            )
            
            if result:
                doc_type = result[0]  # Document type string
                confidence = result[1]  # Confidence scores dict
                # result[2] is the image, which we can ignore
                print(f"[Classification] Success - Type: {doc_type}")
                print(f"[Classification] Confidence: {confidence}")
                return (doc_type, confidence)
            else:
                print(f"[Classification] No result returned")
                return None
                
        except Exception as e:
            print(f"[Classification] Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _call_gradio_predict(self, file_path: str):
        """Synchronous Gradio API call"""
        try:
            # Initialize client if needed
            if self.client is None:
                if not self.initialize_sync_client():
                    return None
            
            # Method 1: Using handle_file (recommended for gradio_client >= 0.10.0)
            try:
                result = self.client.predict(
                    file=handle_file(file_path),
                    api_name="/classify_upload"  # This matches the function name
                )
                return result
            except Exception as e:
                print(f"[Classification] Method 1 failed: {e}")
                
                # Method 2: Direct file path (for older versions or different setup)
                try:
                    result = self.client.predict(
                        file_path,
                        api_name="/classify_upload"
                    )
                    return result
                except Exception as e2:
                    print(f"[Classification] Method 2 failed: {e2}")
                    
                    # Method 3: Without explicit api_name (auto-detect)
                    try:
                        result = self.client.predict(handle_file(file_path))
                        return result
                    except Exception as e3:
                        print(f"[Classification] Method 3 failed: {e3}")
                        return None
            
        except Exception as e:
            print(f"[Classification] Gradio API error: {e}")
            import traceback
            traceback.print_exc()
            return None