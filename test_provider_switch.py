#!/usr/bin/env python3
"""
Quick test to verify that the system uses the correct provider from .env
"""

import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_provider_configuration():
    """Test that the system reads the correct provider from configuration."""
    
    print("🔍 Testing Provider Configuration...")
    print("=" * 50)
    
    try:
        from app.core.config import get_settings
        
        settings = get_settings()
        
        print(f"LLM_PROVIDER from config: {getattr(settings, 'LLM_PROVIDER', 'Not set')}")
        print(f"GROQ_API_KEY present: {'Yes' if getattr(settings, 'GROQ_API_KEY', None) else 'No'}")
        print(f"DEEPSEEK_API_KEY present: {'Yes' if getattr(settings, 'DEEPSEEK_API_KEY', None) else 'No'}")
        
        # Test the chat API configuration logic
        default_provider = getattr(settings, 'LLM_PROVIDER', 'groq').lower()
        print(f"\nDefault provider will be: {default_provider}")
        
        if default_provider == 'deepseek':
            deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            if deepseek_key and deepseek_key != 'your_deepseek_api_key_here':
                print("✅ DeepSeek is properly configured!")
                print(f"   Model: {getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')}")
                print(f"   Temperature: {getattr(settings, 'DEEPSEEK_TEMPERATURE', 0.7)}")
            else:
                print("❌ DeepSeek API key is not set or is placeholder")
        elif default_provider == 'groq':
            groq_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_key:
                print("✅ Groq is configured (current default)")
            else:
                print("❌ Groq API key is not set")
        
        print("\n📋 Configuration Summary:")
        print(f"   Active Provider: {default_provider.upper()}")
        
        if default_provider == 'deepseek':
            print(f"   DeepSeek Model: {getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')}")
            print(f"   Temperature: {getattr(settings, 'DEEPSEEK_TEMPERATURE', 0.7)}")
            print(f"   Max Tokens: {getattr(settings, 'DEEPSEEK_MAX_TOKENS', 4000)}")
        
    except Exception as e:
        print(f"❌ Error testing configuration: {str(e)}")
        import traceback
        traceback.print_exc()


def test_llm_factory():
    """Test that the LLM factory can create DeepSeek instances."""
    
    print("\n🏭 Testing LLM Factory...")
    print("=" * 50)
    
    try:
        from app.services.chatbot.llm.llm_factory import LLMFactory
        from app.core.config import get_settings
        
        settings = get_settings()
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        
        if deepseek_key and deepseek_key != 'your_deepseek_api_key_here':
            print("Testing DeepSeek LLM creation...")
            llm = LLMFactory.create_deepseek_llm(
                api_key=deepseek_key,
                model="deepseek-chat",
                temperature=0.7
            )
            print(f"✅ Successfully created DeepSeek LLM: {type(llm).__name__}")
        else:
            print("⚠️  Skipping DeepSeek LLM test - API key not configured")
            
        # Test Groq for comparison
        groq_key = getattr(settings, 'GROQ_API_KEY', None)
        if groq_key:
            print("Testing Groq LLM creation...")
            llm = LLMFactory.create_groq_llm(
                api_key=groq_key,
                model="llama-3.1-8b-instant",
                temperature=0.7
            )
            print(f"✅ Successfully created Groq LLM: {type(llm).__name__}")
        else:
            print("⚠️  Skipping Groq LLM test - API key not configured")
            
    except Exception as e:
        print(f"❌ Error testing LLM factory: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    print("🚀 Provider Switch Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/core/config.py"):
        print("❌ Please run this script from the document-analyzer root directory")
        return
    
    test_provider_configuration()
    test_llm_factory()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\nTo switch providers, update your .env file:")
    print("   LLM_PROVIDER=deepseek  # or groq")
    print("   DEEPSEEK_API_KEY=your_actual_api_key")


if __name__ == "__main__":
    main()
