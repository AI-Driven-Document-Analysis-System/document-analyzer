import os
import json
import hashlib
import mimetypes
import threading
import multiprocessing
import gc
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
from typing import Tuple, Optional, Dict, Any, List
from uuid import uuid4
import asyncio
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv
import pdf2image
import numpy as np
from PIL import Image
import torch

from ..core.database import db_manager
from ..core.config import settings
from .ocr_service_surya import OCRService, OCRProvider
from ..db.crud import get_document_crud
from .document_embedding_service import document_embedding_service
from .classifcation.classification import DocumentClassifier


class DocumentService:
    def __init__(self):
        # MinIO configuration
        self.minio_endpoint = settings.MINIO_ENDPOINT
        self.minio_access_key = settings.MINIO_ACCESS_KEY
        self.minio_secret_key = settings.MINIO_SECRET_KEY
        self.minio_secure = settings.MINIO_SECURE
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._minio_client = None
        
        # Classification configuration
        self._classifier = None
        self._classifier_lock = threading.Lock()
    
    @property
    def minio_client(self):
        """Lazy initialization of MinIO client"""
        if self._minio_client is None:
            self._minio_client = Minio(
                endpoint=self.minio_endpoint,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=self.minio_secure
            )
            self._ensure_bucket_exists()
        return self._minio_client
    
    @property
    def classifier(self):
        """Lazy initialization of classifier - thread-safe singleton"""
        if self._classifier is None:
            with self._classifier_lock:
                if self._classifier is None:
                    try:
                        self._classifier = DocumentClassifier()
                    except Exception as e:
                        print(f"Failed to initialize classifier: {e}")
                        return None
        return self._classifier

    def _ensure_bucket_exists(self):
        """Ensure the MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
        
    def _upload_to_minio(self, minio_path: str, file_content: bytes, file_size: int, mime_type: str):
        """Upload file to MinIO - thread-safe helper method"""
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=minio_path,
            data=BytesIO(file_content),
            length=file_size,
            content_type=mime_type
        )
        
    def create_thumbnail(self, file_content: bytes, mime_type: str, user_id: str, original_filename: str) -> Optional[str]:
        """
        Generate a thumbnail from the first page of a PDF or an image file, upload to MinIO, and return the MinIO path.
        Returns the MinIO path or None if not generated.
        """
        try:
            if mime_type == "application/pdf":
                # Convert first page of PDF to image for thumbnail
                images = pdf2image.convert_from_bytes(
                    file_content,
                    dpi=72,  # Low DPI for thumbnail
                    fmt='PNG',
                    first_page=1,
                    last_page=1
                )
                if not images:
                    return None
                
                # Convert PIL image to bytes
                img_byte_arr = BytesIO()
                images[0].thumbnail((200, 200), Image.Resampling.LANCZOS)  # Resize for thumbnail
                images[0].save(img_byte_arr, format='PNG')
                thumbnail_bytes = img_byte_arr.getvalue()
                
            elif mime_type in ["image/jpeg", "image/png", "image/gif"]:
                # Create thumbnail from image file
                image = Image.open(BytesIO(file_content))
                img_byte_arr = BytesIO()
                image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                image.save(img_byte_arr, format='PNG')
                thumbnail_bytes = img_byte_arr.getvalue()
            else:
                return None

            # Generate a MinIO path for the thumbnail
            base_path = self._generate_minio_path(user_id, original_filename)
            thumb_minio_path = base_path + ".thumb.png"
            
            # Upload to MinIO
            self._upload_to_minio(thumb_minio_path, thumbnail_bytes, len(thumbnail_bytes), "image/png")
            return thumb_minio_path
            
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
            return None

    def _get_mime_type(self, file_content: bytes, filename: str) -> str:
        """Detect MIME type of file"""
        try:
            # Use mimetypes for MIME type detection
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type:
                return mime_type
        except:
            pass
        
        # Fallback to basic detection based on file extension
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_mapping = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'txt': 'text/plain'
        }
        return mime_mapping.get(ext, 'application/octet-stream')

    def _generate_minio_path(self, user_id: str, filename: str) -> str:
        """Generate a unique path for the file in MinIO"""
        file_id = str(uuid4())
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        ext = filename.split('.')[-1] if '.' in filename else ''
        return f"{user_id}/{timestamp}/{file_id}.{ext}" if ext else f"{user_id}/{timestamp}/{file_id}"

    def _check_document_exists_by_hash(self, file_hash: str, user_id: str) -> Optional[str]:
        """Check if a user's document already exists by hash (per-user deduplication)"""
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM documents WHERE document_hash = %s AND user_id = %s",
                        (file_hash, user_id)
                    )
                    result = cursor.fetchone()
                    return str(result[0]) if result else None
        except Exception as e:
            print(f"Error checking document hash: {e}")
            return None
    
    async def _classify_document_async(self, file_content: bytes, filename: str, document_id: str) -> Optional[str]:
        """
        Classify document asynchronously with proper error handling.
        Returns classification result or None if failed.
        """
        local_path = None
        try:
            # Check if classifier is available
            if self.classifier is None:
                print(f"[Classification] Classifier not available, skipping")
                return None
                
            print(f"[Classification] Starting classification for document {document_id}")

            # Create temp file for classification
            tmp_dir = os.path.join(os.getcwd(), "_classify_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, f"{document_id}_{filename}")
            
            # Write file content to temp
            with open(local_path, "wb") as f:
                f.write(file_content)
            
            # Run classification in thread pool
            result = await self.classifier.classify_document(local_path)

            if result and result[0] != "unknown":
                doc_type = result[0]
                print(f"[Classification] Document {document_id} classified as: {doc_type}")
                
                # Save classification to database
                try:
                    crud = get_document_crud()
                    crud.save_document_classification(
                        document_id=document_id,
                        document_type=doc_type
                    )
                    print(f"[Classification] Classification saved successfully")
                    return doc_type
                except Exception as db_error:
                    print(f"[Classification] Failed to save to DB: {db_error}")
                    return doc_type  # Still return the classification
            else:
                print(f"[Classification] Returned 'unknown'")
                return None
                
        except Exception as e:
            print(f"[Classification] Error: {e}")
            return None
        finally:
            # Always clean up temp file
            if local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except:
                    pass

    async def upload_document(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Upload document with safer sequence: Database first, then MinIO, with proper cleanup on failures
        """
        document_id = None
        minio_path = None
        
        try:
            print(f"DEBUG - Starting upload for user: {user_id}")
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            print(f"DEBUG - File size: {file_size} bytes")

            # Validate file size (max 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
                )

            # Optimize: Run CPU-intensive operations in thread pool
            loop = asyncio.get_event_loop()
            
            # Calculate file hash in thread pool (non-blocking)
            print(f"DEBUG - Calculating file hash...")
            file_hash = await loop.run_in_executor(None, self._calculate_file_hash, file_content)
            print(f"DEBUG - File hash calculated: {file_hash[:16]}...")

            # Check if document already exists (optimized with new index)
            print(f"DEBUG - Checking for existing document...")
            existing_doc_id = await loop.run_in_executor(None, self._check_document_exists_by_hash, file_hash, user_id)
            if existing_doc_id:
                print(f"DEBUG - Document already exists: {existing_doc_id}")
                return {
                    "document_id": existing_doc_id,
                    "message": "Document already exists",
                    "status": "duplicate"
                }

            # Get MIME type
            print(f"DEBUG - Getting MIME type...")
            mime_type = self._get_mime_type(file_content, file.filename or "unknown")
            print(f"DEBUG - MIME type: {mime_type}")

            # Validate file type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/gif',
                'text/plain'
            ]

            if mime_type not in allowed_types:
                print(f"DEBUG - Unsupported file type: {mime_type}")
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {mime_type}"
                )

            # STEP 1: Process document OCR only (NO embedding yet)
            document_id = str(uuid4())
            
            print(f"DEBUG - Starting OCR processing...")
            try:
                await self._process_document_ocr_only(document_id, file_content, file.filename or "unknown")
            except Exception as processing_error:
                print(f"DEBUG - OCR processing failed: {processing_error}")
                # OCR failed - nothing to cleanup (no MinIO, no database, no embeddings)
                raise HTTPException(status_code=500, detail=f"Document processing failed: {str(processing_error)}")

            # STEP 2: Generate MinIO path only after successful OCR
            print(f"DEBUG - Generating MinIO path...")
            minio_path = self._generate_minio_path(user_id, file.filename or "unknown")
            print(f"DEBUG - MinIO path: {minio_path}")

            # STEP 3: Upload to MinIO only after successful OCR
            print(f"DEBUG - Uploading to MinIO...")
            await loop.run_in_executor(None, self._upload_to_minio, minio_path, file_content, file_size, mime_type)
            print(f"DEBUG - MinIO upload successful")

            # Optionally create and store thumbnail 
            print(f"DEBUG - Generating thumbnail...")
            thumb_path = await loop.run_in_executor(None, self.create_thumbnail, file_content, mime_type, user_id, file.filename or "unknown")
            print(f"DEBUG - Thumbnail generated")

            # STEP 4: Create database record ONLY after successful MinIO upload
            now = datetime.utcnow()
            print(f"DEBUG - Creating database record after successful processing...")
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Insert document
                    cursor.execute("""
                        INSERT INTO documents (
                            id, original_filename, file_path_minio, file_size,
                            mime_type, document_hash, user_id, uploaded_by_user_id, upload_timestamp,
                            created_at, updated_at, thumbnail_url
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        document_id, file.filename or "unknown", minio_path,
                        file_size, mime_type, file_hash, user_id, user_id, now, now, now, thumb_path
                    ))

                    # Create processing record with "completed" status
                    processing_id = str(uuid4())
                    cursor.execute("""
                        INSERT INTO document_processing (id, document_id, processing_status, ocr_completed_at)
                        VALUES (%s, %s, %s, %s)
                    """, (processing_id, document_id, "completed", now))

                    conn.commit()
            print(f"DEBUG - Database record created with completed status")

            # STEP 4: Save document content to database
            if hasattr(self, '_temp_processing_results'):
                results = self._temp_processing_results
                crud = get_document_crud()
                crud.save_document_content(
                    document_id=document_id,
                    extracted_text=results['extracted_text'],
                    searchable_content=results['searchable_content'],
                    layout_sections=results['layout_sections'],
                    ocr_confidence_score=results['ocr_confidence_score'],
                    has_tables=results['has_tables'],
                    has_images=results['has_images']
                )
                print(f"DEBUG - Document content saved to database")
                # Clean up temp results
                delattr(self, '_temp_processing_results')

            #Document Classification
            print(f"Starting Document Classification")
            classification_result = await self._classify_document_async(file_content, file.filename, document_id)
            if classification_result:
                print(f"[Processing] Classification complete: {classification_result}")
            else:
                print(f"[Processing] Classification failed or returned unknown")

            # STEP 5: Create embeddings ONLY after everything else succeeds
            print(f"DEBUG - Creating embeddings...")
            try:
                from .document_embedding_service import document_embedding_service
                result = document_embedding_service.embed_document(document_id)
                if not result['success']:
                    raise Exception(f"Embedding failed: {result['error']}")
                print(f"DEBUG - Embeddings created successfully: {result['chunks_created']} chunks")
            except Exception as embedding_error:
                print(f"DEBUG - Embedding failed: {embedding_error}")
                # Embedding failed - cleanup EVERYTHING (MinIO + Database)
                try:
                    self.minio_client.remove_object(self.bucket_name, minio_path)
                    print(f"DEBUG - Cleaned up MinIO file after embedding failure")
                except:
                    pass
                if thumb_path:
                    try:
                        self.minio_client.remove_object(self.bucket_name, thumb_path)
                        print(f"DEBUG - Cleaned up thumbnail after embedding failure")
                    except:
                        pass
                try:
                    with db_manager.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("DELETE FROM document_content WHERE document_id = %s", (document_id,))
                            cursor.execute("DELETE FROM document_processing WHERE document_id = %s", (document_id,))
                            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
                            conn.commit()
                    print(f"DEBUG - Cleaned up database records after embedding failure")
                except:
                    pass
                raise HTTPException(status_code=500, detail=f"Embedding failed: {str(embedding_error)}")

            print(f"DEBUG - Upload and processing completed successfully")
            return {
                "document_id": document_id,
                "file_path": minio_path,
                "message": "Document uploaded and processed successfully - ready for chatbot",
                "status": "completed",
                "file_size": file_size,
                "mime_type": mime_type
            }

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            print(f"DEBUG - Unexpected error during upload: {e}")
            # Clean up any partial state
            if document_id:
                await self._cleanup_failed_upload(document_id)
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    def cleanup_stuck_documents(self):
        """
        Cleanup documents stuck in processing state on server startup
        This handles documents that were interrupted by server crashes
        """
        try:
            print("DEBUG - Starting cleanup of stuck documents...")
            
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Find documents stuck in "uploading" or "processing" status
                    cursor.execute("""
                        SELECT dp.document_id, dp.processing_status, d.original_filename, d.file_path_minio
                        FROM document_processing dp
                        JOIN documents d ON dp.document_id = d.id
                        WHERE dp.processing_status IN ('uploading', 'processing')
                        ORDER BY d.created_at DESC
                    """)
                    stuck_documents = cursor.fetchall()
                    
                    if not stuck_documents:
                        print("DEBUG - No stuck documents found")
                        return
                    
                    print(f"DEBUG - Found {len(stuck_documents)} stuck documents")
                    
                    for doc_id, status, filename, minio_path in stuck_documents:
                        print(f"DEBUG - Processing stuck document: {filename} (Status: {status})")
                        
                        if status == 'uploading':
                            # Document was stuck during upload - likely MinIO upload failed
                            # Check if file actually exists in MinIO
                            try:
                                self.minio_client.stat_object(self.bucket_name, minio_path)
                                # File exists, try to resume processing
                                print(f"DEBUG - File exists in MinIO, resuming processing for {filename}")
                                cursor.execute("""
                                    UPDATE document_processing 
                                    SET processing_status = 'processing' 
                                    WHERE document_id = %s
                                """, (doc_id,))
                                # Start background processing
                                asyncio.create_task(self._start_document_processing(doc_id))
                            except Exception:
                                # File doesn't exist, mark as failed and cleanup
                                print(f"DEBUG - File missing in MinIO, marking as failed: {filename}")
                                error_info = {"message": "Upload incomplete - file missing in storage", "ts": datetime.utcnow().isoformat()}
                                cursor.execute("""
                                    UPDATE document_processing 
                                    SET processing_status = 'failed', processing_errors = %s 
                                    WHERE document_id = %s
                                """, (json.dumps(error_info), doc_id))
                        
                        elif status == 'processing':
                            # Document was stuck during OCR processing
                            # Check if we have extracted text already
                            cursor.execute("SELECT id FROM document_content WHERE document_id = %s", (doc_id,))
                            has_content = cursor.fetchone()
                            
                            if has_content:
                                # OCR was completed, check embeddings
                                try:
                                    from .document_embedding_service import document_embedding_service
                                    # Try to create embeddings
                                    result = document_embedding_service.embed_document(doc_id)
                                    if result['success']:
                                        print(f"DEBUG - Completed embeddings for {filename}")
                                        cursor.execute("""
                                            UPDATE document_processing 
                                            SET processing_status = 'completed', ocr_completed_at = %s 
                                            WHERE document_id = %s
                                        """, (datetime.utcnow(), doc_id))
                                    else:
                                        print(f"DEBUG - Embedding failed for {filename}, marking as failed")
                                        error_info = {"message": "Embedding failed during recovery", "ts": datetime.utcnow().isoformat()}
                                        cursor.execute("""
                                            UPDATE document_processing 
                                            SET processing_status = 'failed', processing_errors = %s 
                                            WHERE document_id = %s
                                        """, (json.dumps(error_info), doc_id))
                                except Exception as e:
                                    print(f"DEBUG - Error during embedding recovery for {filename}: {e}")
                                    error_info = {"message": f"Recovery failed: {str(e)}", "ts": datetime.utcnow().isoformat()}
                                    cursor.execute("""
                                        UPDATE document_processing 
                                        SET processing_status = 'failed', processing_errors = %s 
                                        WHERE document_id = %s
                                    """, (json.dumps(error_info), doc_id))
                            else:
                                # No content extracted, restart OCR processing
                                print(f"DEBUG - Restarting OCR processing for {filename}")
                                asyncio.create_task(self._start_document_processing_safe(doc_id))
                    
                    conn.commit()
                    print(f"DEBUG - Cleanup completed for {len(stuck_documents)} documents")
                    
        except Exception as e:
            print(f"ERROR - Failed to cleanup stuck documents: {e}")

    async def _complete_document_processing_sync(self, document_id: str):
        """
        Complete document processing synchronously - OCR + Embedding
        This ensures the document is fully ready before returning to user
        """
        try:
            print(f"DEBUG - Starting synchronous processing for document: {document_id}")
            
            # Get file path
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT file_path_minio, original_filename FROM documents WHERE id=%s", (document_id,))
                    row = cursor.fetchone()
            if not row:
                raise ValueError("Document not found for OCR")
            file_path_minio, original_filename = row

            # Download file to temp
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, original_filename)
            obj = self.minio_client.get_object(self.bucket_name, file_path_minio)
            try:
                with open(local_path, "wb") as f:
                    for d in obj.stream(32 * 1024):
                        f.write(d)
            finally:
                obj.close(); obj.release_conn()

            # Run OCR processing 
            print(f"Starting OCR processing for document {document_id}")
            
            # Load environment variables
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            
            try:
                ocr_service = OCRService(provider=OCRProvider.SURYA)
            except Exception as e:
                raise Exception("Surya OCR service initialization failed") from e

            # Process document with Surya OCR
            ocr_result = ocr_service.process_document(local_path, document_id)

            # Extract results from Surya OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'surya')
            
            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # Save OCR results to database
            crud = get_document_crud()
            crud.save_document_content(
                document_id=document_id,
                extracted_text=full_text,
                searchable_content=searchable_content,
                layout_sections=layout_sections,
                ocr_confidence_score=avg_conf,
                has_tables=has_tables,
                has_images=has_images
            )
            print(f"Document content saved successfully for {document_id}")
            
            # Create embeddings synchronously
            print(f"Starting embedding creation for document {document_id}")
            from .document_embedding_service import document_embedding_service
            
            result = document_embedding_service.embed_document(document_id)
            if not result['success']:
                raise Exception(f"Embedding failed: {result['error']}")
            
            print(f"Document {document_id} embedded successfully: {result['chunks_created']} chunks created")
            
            # Mark as completed
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, ocr_completed_at=%s WHERE document_id=%s", 
                                 ("completed", datetime.utcnow(), document_id))
                    conn.commit()
            
            print(f"Document processing completed successfully for {document_id}")
            
        except Exception as e:
            # Just re-raise the error - cleanup is handled by the caller
            print(f"Document processing failed for {document_id}: {e}")
            raise

    async def _complete_document_processing_temp(self, document_id: str, minio_path: str, filename: str):
        """
        Complete document processing without database dependencies
        Used for processing before database record creation
        """
        try:
            print(f"DEBUG - Starting temp processing for document: {document_id}")
            
            # Download file to temp
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, filename)
            obj = self.minio_client.get_object(self.bucket_name, minio_path)
            try:
                with open(local_path, "wb") as f:
                    for d in obj.stream(32 * 1024):
                        f.write(d)
            finally:
                obj.close(); obj.release_conn()

            # Run OCR processing 
            print(f"Starting OCR processing for document {document_id}")
            
            # Load environment variables
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            
            
            try:
                ocr_service = OCRService(provider=OCRProvider.SURYA)
            except Exception as e:
                raise Exception("Surya OCR service initialization failed") from e

            # Process document with Surya OCR
            ocr_result = ocr_service.process_document(local_path, document_id)

            # Extract results from Surya OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'surya')
            
            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # Store results temporarily (will be saved to database later)
            self._temp_processing_results = {
                'document_id': document_id,
                'extracted_text': full_text,
                'searchable_content': searchable_content,
                'layout_sections': layout_sections,
                'ocr_confidence_score': avg_conf,
                'has_tables': has_tables,
                'has_images': has_images
            }
            
            # Create embeddings using temporary data
            print(f"Starting embedding creation for document {document_id}")
            from .document_embedding_service import document_embedding_service
            
            # Temporarily create a minimal document content for embedding
            temp_content = {
                'document_id': document_id,
                'extracted_text': full_text,
                'searchable_content': searchable_content
            }
            
            # Create embeddings directly with text content
            result = document_embedding_service.embed_document_with_content(document_id, full_text, searchable_content)
            if not result['success']:
                raise Exception(f"Embedding failed: {result['error']}")
            
            print(f"Document {document_id} embedded successfully: {result['chunks_created']} chunks created")
            print(f"Temp processing completed successfully for {document_id}")
            
        except Exception as e:
            print(f"Temp processing failed for {document_id}: {e}")
            raise

    async def _process_document_ocr_only(self, document_id: str, file_content: bytes, filename: str):
        """
        Process document OCR only - NO embedding
        Store results in memory for later use
        """
        try:
            print(f"DEBUG - Starting OCR-only processing for document: {document_id}")
            
            # Save file content to temp file for OCR processing
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, filename)
            
            with open(local_path, "wb") as f:
                f.write(file_content)

            # Run OCR processing 
            print(f"Starting OCR processing for document {document_id}")
            
            # Load environment variables
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            
            
            try:
                ocr_service = OCRService(provider=OCRProvider.SURYA)
            except Exception as e:
                raise Exception("Surya OCR initialization failed") from e
                
            # Process document with Surya OCR
            ocr_result = ocr_service.process_document(local_path, document_id)

            # Extract results from Surya OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'surya')
            
            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # Store results in memory (will be saved to database later)
            self._temp_processing_results = {
                'document_id': document_id,
                'extracted_text': full_text,
                'searchable_content': searchable_content,
                'layout_sections': layout_sections,
                'ocr_confidence_score': avg_conf,
                'has_tables': has_tables,
                'has_images': has_images
            }
            
            print(f"OCR-only processing completed successfully for {document_id}")
            
        except Exception as e:
            print(f"OCR-only processing failed for {document_id}: {e}")
            # Clean up temp file if it exists
            try:
                if 'local_path' in locals():
                    os.remove(local_path)
            except:
                pass
            raise

    async def _process_document_in_memory(self, document_id: str, file_content: bytes, filename: str):
        """
        Process document completely in memory - OCR + Embedding
        No MinIO or database operations
        """
        try:
            print(f"DEBUG - Starting in-memory processing for document: {document_id}")
            
            # Save file content to temp file for OCR processing
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, filename)
            
            with open(local_path, "wb") as f:
                f.write(file_content)

            # Run OCR processing 
            print(f"Starting OCR processing for document {document_id}")
            
            # Load environment variables
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            
            
            try:
                ocr_service = OCRService(provider=OCRProvider.SURYA)
            except Exception as e:
                raise Exception("Surya OCR service initialization failed") from e

            # Process document with Surya OCR
            ocr_result = ocr_service.process_document(local_path, document_id)

            # Extract results from Surya OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'surya')
            
            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # Store results in memory (will be saved to database later)
            self._temp_processing_results = {
                'document_id': document_id,
                'extracted_text': full_text,
                'searchable_content': searchable_content,
                'layout_sections': layout_sections,
                'ocr_confidence_score': avg_conf,
                'has_tables': has_tables,
                'has_images': has_images
            }
            
            # Create embeddings in memory
            print(f"Starting embedding creation for document {document_id}")
            from .document_embedding_service import document_embedding_service
            
            # Create embeddings directly with text content
            result = document_embedding_service.embed_document_with_content(document_id, full_text, searchable_content)
            if not result['success']:
                raise Exception(f"Embedding failed: {result['error']}")
            
            print(f"Document {document_id} embedded successfully: {result['chunks_created']} chunks created")
            print(f"In-memory processing completed successfully for {document_id}")
            
        except Exception as e:
            print(f"In-memory processing failed for {document_id}: {e}")
            # Clean up temp file if it exists
            try:
                if 'local_path' in locals():
                    os.remove(local_path)
            except:
                pass
            raise

    async def _cleanup_failed_upload(self, document_id: str):
        """Clean up database records for failed uploads"""
        try:
            print(f"DEBUG - Cleaning up failed upload for document: {document_id}")
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Delete processing record first (foreign key constraint)
                    cursor.execute("DELETE FROM document_processing WHERE document_id = %s", (document_id,))
                    # Delete document record
                    cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
                    conn.commit()
            print(f"DEBUG - Cleanup completed for document: {document_id}")
        except Exception as e:
            print(f"ERROR - Failed to cleanup document {document_id}: {e}")

    async def _start_document_processing_safe(self, document_id: str):
        """
        Safer background processing with proper error handling and guaranteed embedding completion
        """
        try:
            print(f"DEBUG - Starting safe processing for document: {document_id}")
            
            # Get file path
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT file_path_minio, original_filename FROM documents WHERE id=%s", (document_id,))
                    row = cursor.fetchone()
            if not row:
                raise ValueError("Document not found for OCR")
            file_path_minio, original_filename = row

            # Download file to temp
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, original_filename)
            obj = self.minio_client.get_object(self.bucket_name, file_path_minio)
            try:
                with open(local_path, "wb") as f:
                    for d in obj.stream(32 * 1024):
                        f.write(d)
            finally:
                obj.close(); obj.release_conn()

            # Run OCR processing 
            print(f"Starting OCR processing for document {document_id}")
            
            # Load environment variables
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            
            try:
                ocr_service = OCRService(provider=OCRProvider.SURYA)
            except Exception as e:
                raise Exception("Surya OCR service initialization failed") from e

            # Process document with SURYA OCR
            ocr_result = ocr_service.process_document(local_path, document_id)

            # Extract results from SURYA OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'surya')

            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # STEP 4: Save OCR results to database
            try:
                crud = get_document_crud()
                crud.save_document_content(
                    document_id=document_id,
                    extracted_text=full_text,
                    searchable_content=searchable_content,
                    layout_sections=layout_sections,
                    ocr_confidence_score=avg_conf,
                    has_tables=has_tables,
                    has_images=has_images
                )
                print(f"Document content saved successfully for {document_id}")
                
            except Exception as content_error:
                print(f"ERROR - Failed to save document content for {document_id}: {content_error}")
                # Mark as failed and don't proceed to embedding
                with db_manager.get_connection() as conn:
                    with conn.cursor() as cursor:
                        error_info = {"message": f"Content save failed: {str(content_error)}", "ts": datetime.utcnow().isoformat()}
                        cursor.execute("UPDATE document_processing SET processing_status=%s, processing_errors=%s WHERE document_id=%s", 
                                     ("failed", json.dumps(error_info), document_id))
                        conn.commit()
                return

            # STEP 5: Start embedding with aggressive retry logic - MUST succeed for chatbot functionality
            embedding_success = False
            max_embedding_retries = 5  # Increased retries
            
            for attempt in range(max_embedding_retries):
                try:
                    print(f"Starting embedding attempt {attempt + 1}/{max_embedding_retries} for document {document_id}")
                    
                    # Import embedding service
                    from .document_embedding_service import document_embedding_service
                    
                    result = document_embedding_service.embed_document(document_id)
                    if result['success']:
                        print(f"Document {document_id} embedded successfully: {result['chunks_created']} chunks created")
                        embedding_success = True
                        break
                    else:
                        print(f"Embedding attempt {attempt + 1} failed: {result['error']}")
                        if attempt < max_embedding_retries - 1:
                            # Exponential backoff: 5s, 10s, 20s, 40s
                            wait_time = 5 * (2 ** attempt)
                            print(f"Waiting {wait_time} seconds before retry...")
                            await asyncio.sleep(wait_time)
                        
                except Exception as embed_error:
                    print(f"Embedding attempt {attempt + 1} error: {str(embed_error)}")
                    if attempt < max_embedding_retries - 1:
                        # Exponential backoff for exceptions too
                        wait_time = 5 * (2 ** attempt)
                        print(f"Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)

            # CRITICAL: If embedding fails, mark entire document as FAILED
            # Users cannot chat with documents without embeddings
            if embedding_success:
                # Mark as completed - both OCR and embedding successful
                with db_manager.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("UPDATE document_processing SET processing_status=%s, ocr_completed_at=%s WHERE document_id=%s", 
                                     ("completed", datetime.utcnow(), document_id))
                        conn.commit()
                print(f"Document processing completed successfully for {document_id}")
            else:
                # EMBEDDING FAILED = ENTIRE DOCUMENT FAILED (cannot use chatbot)
                with db_manager.get_connection() as conn:
                    with conn.cursor() as cursor:
                        error_info = {"message": "CRITICAL: Embedding failed - document cannot be used in chatbot", "ts": datetime.utcnow().isoformat()}
                        cursor.execute("UPDATE document_processing SET processing_status=%s, processing_errors=%s WHERE document_id=%s", 
                                     ("failed", json.dumps(error_info), document_id))
                        conn.commit()
                print(f"CRITICAL: Document {document_id} marked as FAILED - embedding required for chatbot functionality")
            
        except Exception as e:
            # Mark as failed
            print(f"Document processing failed for {document_id}: {e}")
            error_info = {"message": str(e), "ts": datetime.utcnow().isoformat()}
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, processing_errors=%s WHERE document_id=%s", 
                                 ("failed", json.dumps(error_info), document_id))
                    conn.commit()


    async def _start_document_processing(self, document_id: str):
        """Background pipeline: download file, run Surya OCR, store content, update status."""
        try:
            # Mark processing
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s WHERE document_id=%s", ("processing", document_id))
                    conn.commit()

            # Get file path
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT file_path_minio, original_filename FROM documents WHERE id=%s", (document_id,))
                    row = cursor.fetchone()
            if not row:
                raise ValueError("Document not found for OCR")
            file_path_minio, original_filename = row

            # Download file to temp
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, original_filename)
            obj = self.minio_client.get_object(self.bucket_name, file_path_minio)
            try:
                with open(local_path, "wb") as f:
                    for d in obj.stream(32 * 1024):
                        f.write(d)
            finally:
                obj.close(); obj.release_conn()

            #Document Classification
            print(f"Starting Document Classification")
            classification_result = await self._classify_document_async(local_path, document_id)
            if classification_result:
                print(f"[Processing] Classification complete: {classification_result}")
            else:
                print(f"[Processing] Classification failed or returned unknown")

            # Run OCR processing (Surya or AWS Textract fallback)
            print(f"Starting OCR processing for document {document_id}")
            
            # Ensure environment variables are loaded in background task
            # Get the project root directory and load .env file explicitly
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            print(f"DEBUG - Loading .env from: {env_path}")
            print(f"DEBUG - .env file exists: {os.path.exists(env_path)}")
            
            load_dotenv(dotenv_path=env_path, override=True)

            # Force Surya 
            ocr_provider = os.getenv("OCR_PROVIDER", "surya")
            
            
            try:
                ocr_service = OCRService(provider=OCRProvider.SURYA)
            except Exception as e:
                raise Exception("Surya OCR initialization failed") from e

            # Process document with Surya OCR
            ocr_result = ocr_service.process_document(local_path, document_id)

            # Extract results from Surya OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'surya')
            
            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # Persist document_content
            try:
                crud = get_document_crud()
                crud.save_document_content(
                    document_id=document_id,
                    extracted_text=full_text,
                    searchable_content=searchable_content,
                    layout_sections=layout_sections,
                    ocr_confidence_score=avg_conf,
                    has_tables=has_tables,
                    has_images=has_images
                )
                print(f"Document content saved successfully for {document_id}")
                
                # Start automatic embedding in background thread
                def embed_document_background():
                    try:
                        # Import inside thread to ensure module availability
                        import sys
                        import os
                        app_dir = os.path.join(os.path.dirname(__file__), '..')
                        if app_dir not in sys.path:
                            sys.path.append(app_dir)
                        
                        from services.document_embedding_service import document_embedding_service
                        
                        print(f"Starting automatic embedding for document {document_id}")
                        result = document_embedding_service.embed_document(document_id)
                        if result['success']:
                            print(f"Document {document_id} embedded successfully: {result['chunks_created']} chunks created")
                        else:
                            print(f"Document {document_id} embedding failed: {result['error']}")
                    except Exception as e:
                        print(f"Background embedding error for {document_id}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                # Start embedding in background thread (non-blocking)
                embedding_thread = threading.Thread(target=embed_document_background)
                embedding_thread.daemon = True
                embedding_thread.start()
                
            except Exception as ce:
                print(f"Warning: could not save document_content for {document_id}: {ce}")

            # Mark completed
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, ocr_completed_at=%s WHERE document_id=%s", ("completed", datetime.utcnow(), document_id))
                    conn.commit()
                    
            print(f"Document processing completed successfully for {document_id}")
            
        except Exception as e:
            # Mark failed
            print(f"Document processing failed for {document_id}: {e}")
            err = {"message": str(e), "ts": datetime.utcnow().isoformat()}
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, processing_errors=%s WHERE document_id=%s", ("failed", json.dumps(err), document_id))
                    conn.commit()

    def get_document_download_url(self, file_path: str, expires_in_hours: int = 1) -> str:
        """Generate a presigned URL for downloading the document"""
        try:
            from datetime import timedelta
            url = self.minio_client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                expires=timedelta(hours=expires_in_hours)
            )
            return url
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")

    def delete_document(self, file_path: str, thumb_path: str, document_id: str):
        """Delete document from MinIO and database"""
        try:
            # Delete from MinIO
            self.minio_client.remove_object(self.bucket_name, file_path)
            if thumb_path:
                try:
                    self.minio_client.remove_object(self.bucket_name, thumb_path)
                    print(f"DEBUG - Cleaned up thumbnail after embedding failure")
                except:
                    pass

            # Delete from database (CASCADE will handle related records)
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
                    conn.commit()

        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


# Initialize Surya-enabled service instance
document_service = DocumentService()
