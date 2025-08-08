#!/usr/bin/env python3
"""
Script to pre-download all required models for the multi-model summarization system.
Run this once before using the main summarization code.
"""

from transformers import pipeline
import os
import time

def download_model(model_name, model_id, description):
    """Download a specific model with progress indication."""
    print(f"\n{'='*60}")
    print(f"📥 Downloading {model_name}")
    print(f"🔗 Model: {model_id}")
    print(f"📝 Description: {description}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        print("🚀 Starting download... This may take a few minutes.")
        
        # Initialize the pipeline (this triggers the download)
        _ = pipeline("summarization", model=model_id, framework="pt")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ {model_name} downloaded successfully!")
        print(f"⏱️ Download time: {duration:.1f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False

def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        print(f"💾 Available disk space: {free_space:.1f} GB")
        
        if free_space < 6:  # Need ~5GB for all models
            print("⚠️ Warning: You may need more disk space (~5GB total for all models)")
        else:
            print("✅ Sufficient disk space available")
            
    except Exception as e:
        print(f"ℹ️ Could not check disk space: {e}")

def main():
    """Main function to download all required models."""
    print("🤖 MULTI-MODEL SUMMARIZATION SETUP")
    print("="*60)
    print("This script will download the following models:")
    print("1. BART Large CNN (~1.6 GB) - Already available")
    print("2. Pegasus CNN DailyMail (~2.3 GB) - NEW")
    print("3. T5 Base (~850 MB) - NEW")
    print("Total new download size: ~3.15 GB")
    print("="*60)
    
    # Check disk space
    check_disk_space()
    
    # Ask for confirmation
    response = input("\n🤔 Do you want to proceed with downloading? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Download cancelled.")
        return
    
    models_to_download = [
        {
            "name": "BART Large CNN",
            "id": "facebook/bart-large-cnn",
            "description": "Best for detailed, comprehensive summaries"
        },
        {
            "name": "Pegasus CNN DailyMail", 
            "id": "google/pegasus-cnn_dailymail",
            "description": "Best for brief, abstractive summaries"
        },
        {
            "name": "T5 Base",
            "id": "t5-base", 
            "description": "Best for structured, flexible summaries"
        }
    ]
    
    print(f"\n🚀 Starting downloads...")
    successful_downloads = []
    failed_downloads = []
    
    total_start_time = time.time()
    
    for model in models_to_download:
        success = download_model(model["name"], model["id"], model["description"])
        
        if success:
            successful_downloads.append(model["name"])
        else:
            failed_downloads.append(model["name"])
    
    total_time = time.time() - total_start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 DOWNLOAD SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {len(successful_downloads)}/{len(models_to_download)} models")
    print(f"⏱️ Total time: {total_time:.1f} seconds")
    
    if successful_downloads:
        print(f"\n✅ Successfully downloaded:")
        for model in successful_downloads:
            print(f"   • {model}")
    
    if failed_downloads:
        print(f"\n❌ Failed to download:")
        for model in failed_downloads:
            print(f"   • {model}")
        print("\n💡 You can try running this script again for failed downloads.")
    else:
        print(f"\n🎉 All models downloaded successfully!")
        print("✅ You're ready to use the multi-model summarization system!")
    
    print(f"\n📁 Models are cached in: ~/.cache/huggingface/transformers/")
    print("💡 Tip: These models will only download once and be reused.")

def check_existing_models():
    """Check which models are already downloaded."""
    print("🔍 CHECKING EXISTING MODELS")
    print("="*60)
    
    models = {
        "BART": "facebook/bart-large-cnn",
        "Pegasus": "google/pegasus-cnn_dailymail", 
        "T5": "t5-base"
    }
    
    for name, model_id in models.items():
        try:
            # Try to load without downloading
            _ = pipeline("summarization", model=model_id, framework="pt")
            print(f"✅ {name} - Already available")
        except:
            print(f"❌ {name} - Needs download")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_existing_models()
    else:
        main()