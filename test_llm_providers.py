#!/usr/bin/env python3
"""
Test script for LLM provider switching between Groq and DeepSeek.

This script demonstrates how to use the new LLM provider service to switch
between different providers and test their functionality.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_provider_service import get_llm_provider_service, create_default_llm
from app.core.config import get_settings


def test_provider_availability():
    """Test which providers are available based on API keys."""
    print("🔍 Checking LLM Provider Availability...")
    print("=" * 50)
    
    service = get_llm_provider_service()
    available_providers = service.get_available_providers()
    
    for provider, is_available in available_providers.items():
        status = "✅ Available" if is_available else "❌ Missing API Key"
        print(f"{provider.upper():10} - {status}")
    
    print(f"\nActive Provider: {service.get_active_provider().upper()}")
    print("=" * 50)


def test_provider_config():
    """Test provider configuration retrieval."""
    print("\n🔧 Testing Provider Configurations...")
    print("=" * 50)
    
    service = get_llm_provider_service()
    
    for provider in ["groq", "deepseek"]:
        try:
            config = service.get_provider_config(provider)
            print(f"\n{provider.upper()} Configuration:")
            print(f"  Model: {config['model']}")
            print(f"  Temperature: {config['temperature']}")
            print(f"  Max Tokens: {config['max_tokens']}")
            print(f"  API Key: {'***' + config['api_key'][-4:] if config['api_key'] else 'Not set'}")
        except ValueError as e:
            print(f"\n{provider.upper()}: ❌ {str(e)}")


def test_llm_creation():
    """Test LLM instance creation."""
    print("\n🤖 Testing LLM Creation...")
    print("=" * 50)
    
    service = get_llm_provider_service()
    
    # Test active provider
    try:
        active_provider = service.get_active_provider()
        print(f"\nCreating LLM with active provider ({active_provider.upper()})...")
        llm = create_default_llm()
        print(f"✅ Successfully created {active_provider.upper()} LLM instance")
        print(f"   Type: {type(llm).__name__}")
    except Exception as e:
        print(f"❌ Failed to create LLM: {str(e)}")
    
    # Test specific providers if available
    available_providers = service.get_available_providers()
    
    for provider, is_available in available_providers.items():
        if is_available and provider != service.get_active_provider():
            try:
                print(f"\nTesting {provider.upper()} provider...")
                llm = service.create_llm(provider)
                print(f"✅ Successfully created {provider.upper()} LLM instance")
                print(f"   Type: {type(llm).__name__}")
            except Exception as e:
                print(f"❌ Failed to create {provider.upper()} LLM: {str(e)}")


def test_simple_query():
    """Test a simple query with the active provider."""
    print("\n💬 Testing Simple Query...")
    print("=" * 50)
    
    try:
        service = get_llm_provider_service()
        active_provider = service.get_active_provider()
        
        print(f"Using {active_provider.upper()} provider...")
        llm = create_default_llm()
        
        # Simple test query
        query = "What is the capital of France? Please answer in one sentence."
        print(f"Query: {query}")
        
        # Note: This is a basic test. In a real application, you'd use the chat engine
        response = llm.invoke(query)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Query test failed: {str(e)}")
        print("Note: Make sure your API key is valid and you have internet connection.")


def test_provider_switching():
    """Test switching between providers at runtime."""
    print("\n🔄 Testing Provider Switching...")
    print("=" * 50)
    
    service = get_llm_provider_service()
    available_providers = service.get_available_providers()
    available_list = [p for p, available in available_providers.items() if available]
    
    if len(available_list) < 2:
        print("❌ Need at least 2 providers configured to test switching")
        return
    
    original_provider = service.get_active_provider()
    
    for provider in available_list:
        if provider != original_provider:
            try:
                print(f"\nSwitching to {provider.upper()}...")
                service.switch_provider(provider)
                print(f"✅ Successfully switched to {provider.upper()}")
                
                # Test LLM creation with new provider
                llm = service.create_llm()
                print(f"✅ Created LLM instance with {provider.upper()}")
                
                # Switch back
                service.switch_provider(original_provider)
                print(f"✅ Switched back to {original_provider.upper()}")
                break
                
            except Exception as e:
                print(f"❌ Provider switching failed: {str(e)}")


def display_usage_examples():
    """Display usage examples."""
    print("\n📖 Usage Examples...")
    print("=" * 50)
    
    examples = [
        "# Set environment variable to switch providers:",
        "export LLM_PROVIDER=deepseek  # or groq",
        "",
        "# In your Python code:",
        "from app.services.llm_provider_service import create_default_llm",
        "",
        "# Create LLM with active provider",
        "llm = create_default_llm()",
        "",
        "# Create LLM with specific provider",
        "service = get_llm_provider_service()",
        "llm = service.create_llm('deepseek')",
        "",
        "# Override default parameters",
        "llm = create_default_llm(temperature=0.9, streaming=True)",
        "",
        "# Check available providers",
        "available = service.get_available_providers()",
        "print(available)  # {'groq': True, 'deepseek': True, ...}",
    ]
    
    for example in examples:
        print(example)


def main():
    """Main test function."""
    print("🚀 LLM Provider Service Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/core/config.py"):
        print("❌ Please run this script from the document-analyzer root directory")
        return
    
    try:
        # Run all tests
        test_provider_availability()
        test_provider_config()
        test_llm_creation()
        
        # Only test queries if we have at least one provider available
        service = get_llm_provider_service()
        if service.validate_provider_setup():
            test_simple_query()
        else:
            print("\n⚠️  Skipping query test - no valid provider configured")
        
        test_provider_switching()
        display_usage_examples()
        
        print("\n✅ Test suite completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
