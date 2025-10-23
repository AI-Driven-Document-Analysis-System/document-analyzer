# Migration Scripts

## Generate Missing Thumbnails

Script to generate thumbnails for existing documents that don't have them.

### Usage

**1. Dry Run (Preview Only - Recommended First)**
```bash
python scripts/generate_missing_thumbnails.py
```

**2. Live Run (Apply Changes)**
```bash
python scripts/generate_missing_thumbnails.py --live
```

**3. Process Limited Number**
```bash
python scripts/generate_missing_thumbnails.py --live --limit 50
```

**4. Custom Batch Size**
```bash
python scripts/generate_missing_thumbnails.py --live --batch-size 20
```

### Options

- `--live`: Run in live mode (default is dry-run for safety)
- `--batch-size N`: Process N documents per batch (default: 10)
- `--limit N`: Process maximum N documents (default: all)

### Safety Features

- **Dry-run by default**: Preview changes before applying
- **Batch processing**: Processes documents in small batches
- **Error isolation**: One document failure doesn't stop the entire migration
- **Rollback on failure**: Cleans up uploaded thumbnails if database update fails
- **Detailed logging**: Logs saved to `logs/thumbnail_migration_*.log`
- **Progress tracking**: Shows real-time progress and summary

### What It Does

1. Finds all documents without thumbnails (PDF and image files only)
2. Downloads each document from MinIO
3. Generates a 350x350 thumbnail
4. Uploads thumbnail to MinIO
5. Updates database with thumbnail path

### Example Output

```
================================================================================
Starting Thumbnail Migration - DRY RUN MODE
Batch size: 10
================================================================================
Found 25 documents without thumbnails

Processing 25 documents...
--------------------------------------------------------------------------------

Batch 1/3
----------------------------------------
Processing: report.pdf (ID: abc-123)
  [DRY RUN] Would upload thumbnail (45231 bytes)
  [DRY RUN] Would update database
  ✓ Successfully processed: report.pdf

...

================================================================================
MIGRATION SUMMARY
================================================================================
Mode: DRY RUN
Total documents found: 25
Processed: 25
Successful: 23
Failed: 2
Skipped: 0
```
