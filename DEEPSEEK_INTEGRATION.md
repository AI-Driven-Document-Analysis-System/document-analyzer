# DeepSeek API Integration Guide

This document explains how to use the new DeepSeek API integration alongside your existing Groq API setup.

## Overview

The document analyzer now supports multiple LLM providers:
- **Groq** (existing) - Llama 3.1 8B Instant
- **DeepSeek** (new) - DeepSeek Chat & DeepSeek Coder
- **OpenAI** - GPT models
- **Gemini** - Google's Gemini models

## Quick Setup

### 1. Get DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 2. Update Environment Configuration

Add these lines to your `.env` file:

```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Set active provider (groq, deepseek, openai, gemini)
LLM_PROVIDER=deepseek

# DeepSeek Specific Settings (optional)
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_MAX_TOKENS=4000
```

### 3. Switch Between Providers

To switch between Groq and DeepSeek, simply change the `LLM_PROVIDER` value:

```bash
# Use Groq (your current setup)
LLM_PROVIDER=groq

# Use DeepSeek
LLM_PROVIDER=deepseek
```

## Available DeepSeek Models

- `deepseek-chat` - General purpose conversational model
- `deepseek-coder` - Specialized for code generation and analysis

## Usage Examples

### Using the Provider Service

```python
from app.services.llm_provider_service import get_llm_provider_service, create_default_llm

# Create LLM with active provider (from .env)
llm = create_default_llm()

# Create LLM with specific provider
service = get_llm_provider_service()
deepseek_llm = service.create_llm("deepseek")
groq_llm = service.create_llm("groq")

# Override default parameters
llm = create_default_llm(temperature=0.9, streaming=True)
```

### Checking Available Providers

```python
service = get_llm_provider_service()

# Check which providers have API keys configured
available = service.get_available_providers()
print(available)
# Output: {'groq': True, 'deepseek': True, 'openai': False, 'gemini': True}

# Get current active provider
current = service.get_active_provider()
print(f"Current provider: {current}")
```

### Runtime Provider Switching

```python
service = get_llm_provider_service()

# Switch to DeepSeek
service.switch_provider("deepseek")

# Switch back to Groq
service.switch_provider("groq")
```

## Testing the Integration

Run the test script to verify everything works:

```bash
cd /path/to/document-analyzer
python test_llm_providers.py
```

This will:
- Check which providers are available
- Test configuration loading
- Create LLM instances
- Test provider switching
- Run a simple query (if API keys are valid)

## DeepSeek vs Groq Comparison

| Feature | Groq | DeepSeek |
|---------|------|----------|
| **Speed** | Very Fast | Fast |
| **Models** | Llama 3.1 8B/70B | DeepSeek Chat/Coder |
| **Max Tokens** | 2000 | 4000 |
| **Pricing** | Free tier available | Competitive pricing |
| **Specialization** | General purpose | Chat + Code focused |
| **API Compatibility** | Native Groq API | OpenAI-compatible |

## Configuration Details

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | Active provider | `groq` | No |
| `DEEPSEEK_API_KEY` | DeepSeek API key | None | Yes (for DeepSeek) |
| `DEEPSEEK_MODEL` | DeepSeek model name | `deepseek-chat` | No |
| `DEEPSEEK_TEMPERATURE` | Temperature setting | `0.7` | No |
| `DEEPSEEK_MAX_TOKENS` | Max tokens | `4000` | No |

### Model Configuration

The system automatically selects appropriate settings for each provider:

```python
# Groq Configuration
{
    "provider": "groq",
    "model": "llama-3.1-8b-instant",
    "temperature": 0.7,
    "max_tokens": 2000
}

# DeepSeek Configuration
{
    "provider": "deepseek",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 4000
}
```

## Integration with Existing Chat Engine

The chat engine automatically uses the configured provider:

```python
# In your chat service
from app.services.llm_provider_service import create_default_llm

# This will use whatever provider is set in LLM_PROVIDER
llm = create_default_llm()

# Use in chat engine
chat_engine = LangChainChatEngine(llm, retriever, memory_type)
```

## Error Handling

The system provides clear error messages:

```python
# Missing API key
ValueError: DEEPSEEK_API_KEY is required but not set in environment

# Invalid provider
ValueError: Unsupported provider: invalid_provider. Supported providers: groq, deepseek, openai, gemini

# Configuration validation
if not service.validate_provider_setup("deepseek"):
    print("DeepSeek is not properly configured")
```

## Best Practices

1. **API Key Security**: Never commit API keys to version control
2. **Provider Selection**: Choose based on your use case:
   - Use **Groq** for fastest inference
   - Use **DeepSeek** for longer responses or code analysis
3. **Fallback Strategy**: Configure multiple providers for redundancy
4. **Testing**: Always test with the `test_llm_providers.py` script before deployment

## Troubleshooting

### Common Issues

1. **"DEEPSEEK_API_KEY is required"**
   - Ensure you've added the API key to your `.env` file
   - Restart your application after adding the key

2. **"Failed to create DeepSeek LLM"**
   - Check your API key is valid
   - Verify internet connection
   - Check DeepSeek service status

3. **"Provider switching failed"**
   - Ensure the target provider has a valid API key
   - Check the provider name is correct (lowercase)

### Debug Mode

Enable debug logging to see detailed provider information:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## Migration from Groq-only Setup

If you're currently using only Groq, no changes are required. The system maintains backward compatibility:

1. Your existing `GROQ_API_KEY` continues to work
2. Default provider remains `groq`
3. All existing code continues to function

To start using DeepSeek:
1. Add `DEEPSEEK_API_KEY` to `.env`
2. Set `LLM_PROVIDER=deepseek`
3. Restart your application

## Support

- For DeepSeek API issues: [DeepSeek Documentation](https://platform.deepseek.com/docs)
- For integration issues: Check the test script output and logs
- For configuration help: Review this guide and the `.env.example` file
