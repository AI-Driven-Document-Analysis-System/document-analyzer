"""
Migration script to generate thumbnails for existing documents that don't have them.

This script:
1. Finds all documents without thumbnails (thumbnail_url IS NULL)
2. Downloads each document from MinIO
3. Generates a thumbnail
4. Uploads thumbnail to MinIO
5. Updates the database with the thumbnail path

Safety features:
- Dry-run mode to preview changes
- Batch processing with configurable batch size
- Comprehensive error handling per document
- Progress tracking
- Rollback on critical failures
- Detailed logging
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime
from typing import List, Dict, Optional
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes

from app.core.database import db_manager
from app.core.config import settings
from minio import Minio
from minio.error import S3Error

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            f'logs/thumbnail_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ThumbnailMigration:
    """Handles thumbnail generation for existing documents."""
    
    def __init__(self, dry_run: bool = True, batch_size: int = 10):
        """
        Initialize the migration.
        
        Args:
            dry_run: If True, only preview changes without modifying data
            batch_size: Number of documents to process in each batch
        """
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.stats = {
            'total': 0,
            'processed': 0,
            'success': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }
        
        # Initialize MinIO client
        try:
            self.minio_client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            self.bucket_name = settings.MINIO_BUCKET_NAME
            logger.info(f"Connected to MinIO at {settings.MINIO_ENDPOINT}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise
    
    def get_documents_without_thumbnails(self, limit: int = None) -> List[Dict]:
        """
        Fetch documents that don't have thumbnails.
        
        Args:
            limit: Maximum number of documents to fetch (None for all)
            
        Returns:
            List of document dictionaries
        """
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            d.id, 
                            d.original_filename, 
                            d.file_path_minio, 
                            d.mime_type,
                            d.user_id
                        FROM documents d
                        WHERE d.thumbnail_url IS NULL
                        AND d.mime_type IN (
                            'application/pdf',
                            'image/jpeg',
                            'image/png',
                            'image/gif'
                        )
                        ORDER BY d.upload_timestamp DESC
                    """
                    
                    if limit:
                        query += f" LIMIT {limit}"
                    
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    documents = []
                    for row in results:
                        documents.append({
                            'id': row[0],
                            'filename': row[1],
                            'file_path': row[2],
                            'mime_type': row[3],
                            'user_id': row[4]
                        })
                    
                    logger.info(f"Found {len(documents)} documents without thumbnails")
                    return documents
                    
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise
    
    def download_from_minio(self, file_path: str) -> Optional[bytes]:
        """
        Download file content from MinIO.
        
        Args:
            file_path: MinIO object path
            
        Returns:
            File content as bytes, or None if failed
        """
        try:
            response = self.minio_client.get_object(self.bucket_name, file_path)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            logger.error(f"MinIO error downloading {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading {file_path}: {e}")
            return None
    
    def generate_thumbnail(self, file_content: bytes, mime_type: str) -> Optional[bytes]:
        """
        Generate thumbnail from file content.
        
        Args:
            file_content: Original file content
            mime_type: MIME type of the file
            
        Returns:
            Thumbnail image as PNG bytes, or None if failed
        """
        try:
            if mime_type == "application/pdf":
                # Convert first page of PDF to image with poppler path
                import os
                poppler_path = os.path.join(os.getcwd(), 'poppler', 'poppler-23.01.0', 'Library', 'bin')
                
                images = convert_from_bytes(
                    file_content, 
                    first_page=1, 
                    last_page=1, 
                    fmt="png",
                    poppler_path=poppler_path if os.path.exists(poppler_path) else None
                )
                if not images:
                    logger.warning("No images extracted from PDF")
                    return None
                img = images[0]
            elif mime_type in ["image/jpeg", "image/png", "image/gif"]:
                # Open image file
                img = Image.open(BytesIO(file_content))
            else:
                logger.warning(f"Unsupported MIME type: {mime_type}")
                return None
            
            # Create thumbnail (350x350 max, maintaining aspect ratio)
            img.thumbnail((350, 350), Image.Resampling.LANCZOS)
            
            # Convert to PNG bytes
            buf = BytesIO()
            img.save(buf, format="PNG", optimize=True)
            thumbnail_bytes = buf.getvalue()
            
            logger.debug(f"Generated thumbnail: {len(thumbnail_bytes)} bytes")
            return thumbnail_bytes
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None
    
    def upload_thumbnail_to_minio(self, thumbnail_bytes: bytes, base_path: str) -> Optional[str]:
        """
        Upload thumbnail to MinIO.
        
        Args:
            thumbnail_bytes: Thumbnail image bytes
            base_path: Base path for the original file
            
        Returns:
            MinIO path of uploaded thumbnail, or None if failed
        """
        try:
            # Generate thumbnail path based on original file path
            thumb_path = base_path + ".thumb.png"
            
            # Upload to MinIO
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=thumb_path,
                data=BytesIO(thumbnail_bytes),
                length=len(thumbnail_bytes),
                content_type="image/png"
            )
            
            logger.debug(f"Uploaded thumbnail to: {thumb_path}")
            return thumb_path
            
        except S3Error as e:
            logger.error(f"MinIO error uploading thumbnail: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading thumbnail: {e}")
            return None
    
    def update_database(self, document_id: str, thumbnail_path: str) -> bool:
        """
        Update document record with thumbnail path.
        
        Args:
            document_id: Document ID
            thumbnail_path: MinIO path of the thumbnail
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE documents SET thumbnail_url = %s WHERE id = %s",
                        (thumbnail_path, document_id)
                    )
                    conn.commit()
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No document updated for ID: {document_id}")
                        return False
                    
                    logger.debug(f"Updated database for document: {document_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating database for {document_id}: {e}")
            return False
    
    def process_document(self, doc: Dict) -> bool:
        """
        Process a single document to generate and store its thumbnail.
        
        Args:
            doc: Document dictionary
            
        Returns:
            True if successful, False otherwise
        """
        doc_id = doc['id']
        filename = doc['filename']
        
        logger.info(f"Processing: {filename} (ID: {doc_id})")
        
        try:
            # Step 1: Download from MinIO
            logger.debug(f"  Downloading from MinIO: {doc['file_path']}")
            file_content = self.download_from_minio(doc['file_path'])
            if not file_content:
                logger.error(f"  Failed to download file")
                return False
            
            # Step 2: Generate thumbnail
            logger.debug(f"  Generating thumbnail...")
            thumbnail_bytes = self.generate_thumbnail(file_content, doc['mime_type'])
            if not thumbnail_bytes:
                logger.error(f"  Failed to generate thumbnail")
                return False
            
            if self.dry_run:
                logger.info(f"  [DRY RUN] Would upload thumbnail ({len(thumbnail_bytes)} bytes)")
                logger.info(f"  [DRY RUN] Would update database")
                return True
            
            # Step 3: Upload thumbnail to MinIO
            logger.debug(f"  Uploading thumbnail to MinIO...")
            thumb_path = self.upload_thumbnail_to_minio(thumbnail_bytes, doc['file_path'])
            if not thumb_path:
                logger.error(f"  Failed to upload thumbnail")
                return False
            
            # Step 4: Update database
            logger.debug(f"  Updating database...")
            if not self.update_database(doc_id, thumb_path):
                # Rollback: Delete uploaded thumbnail
                logger.warning(f"  Database update failed, cleaning up thumbnail...")
                try:
                    self.minio_client.remove_object(self.bucket_name, thumb_path)
                except:
                    pass
                return False
            
            logger.info(f"  ✓ Successfully processed: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"  Unexpected error processing {filename}: {e}")
            return False
    
    def run(self, limit: int = None):
        """
        Run the migration.
        
        Args:
            limit: Maximum number of documents to process (None for all)
        """
        mode = "DRY RUN" if self.dry_run else "LIVE"
        logger.info(f"=" * 80)
        logger.info(f"Starting Thumbnail Migration - {mode} MODE")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"=" * 80)
        
        try:
            # Get documents without thumbnails
            documents = self.get_documents_without_thumbnails(limit)
            self.stats['total'] = len(documents)
            
            if not documents:
                logger.info("No documents found that need thumbnails. Migration complete!")
                return
            
            logger.info(f"\nProcessing {len(documents)} documents...")
            logger.info("-" * 80)
            
            # Process in batches
            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches = (len(documents) + self.batch_size - 1) // self.batch_size
                
                logger.info(f"\nBatch {batch_num}/{total_batches}")
                logger.info("-" * 40)
                
                for doc in batch:
                    self.stats['processed'] += 1
                    
                    success = self.process_document(doc)
                    if success:
                        self.stats['success'] += 1
                    else:
                        self.stats['failed'] += 1
                        self.stats['errors'].append({
                            'document_id': doc['id'],
                            'filename': doc['filename'],
                            'error': 'Processing failed'
                        })
            
            # Print summary
            logger.info("\n" + "=" * 80)
            logger.info("MIGRATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Mode: {mode}")
            logger.info(f"Total documents found: {self.stats['total']}")
            logger.info(f"Processed: {self.stats['processed']}")
            logger.info(f"Successful: {self.stats['success']}")
            logger.info(f"Failed: {self.stats['failed']}")
            logger.info(f"Skipped: {self.stats['skipped']}")
            
            if self.stats['errors']:
                logger.info(f"\nErrors encountered:")
                for error in self.stats['errors'][:10]:  # Show first 10 errors
                    logger.info(f"  - {error['filename']} (ID: {error['document_id']})")
                if len(self.stats['errors']) > 10:
                    logger.info(f"  ... and {len(self.stats['errors']) - 10} more")
            
            if self.dry_run:
                logger.info("\n" + "!" * 80)
                logger.info("This was a DRY RUN - no changes were made to the database or MinIO")
                logger.info("Run with --live flag to apply changes")
                logger.info("!" * 80)
            
        except Exception as e:
            logger.error(f"Migration failed with critical error: {e}")
            raise


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate thumbnails for existing documents without them'
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in live mode (default is dry-run)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of documents to process in each batch (default: 10)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of documents to process (default: all)'
    )
    parser.add_argument(
        '--skip-missing',
        action='store_true',
        help='Skip documents where files are missing from MinIO (default: process all)'
    )
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Run migration
    migration = ThumbnailMigration(
        dry_run=not args.live,
        batch_size=args.batch_size
    )
    
    try:
        migration.run(limit=args.limit)
    except KeyboardInterrupt:
        logger.info("\n\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nMigration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
