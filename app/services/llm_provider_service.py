"""
LLM Provider Service - Centralized LLM provider management based on environment configuration.

This service provides a unified interface for creating LLM instances based on the
LLM_PROVIDER environment variable, automatically selecting the appropriate API key
and model configuration.
"""

from typing import Dict, Any, Optional
import logging
from ..core.config import get_settings
from .chatbot.llm.llm_factory import LLMFactory


class LLMProviderService:
    """
    Service for managing LLM provider selection and configuration.
    
    This service reads the LLM_PROVIDER environment variable and automatically
    configures the appropriate LLM instance with the correct API key and settings.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
    def get_active_provider(self) -> str:
        """
        Get the currently active LLM provider from configuration.
        
        Returns:
            str: The active provider name (groq, deepseek)
        """
        return self.settings.LLM_PROVIDER.lower()
    
    def get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for the specified provider or active provider.
        
        Args:
            provider: Optional provider name. If None, uses active provider.
            
        Returns:
            Dict containing provider configuration
            
        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        if provider is None:
            provider = self.get_active_provider()
        
        provider = provider.lower()
        
        if provider == "groq":
            if not self.settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is required but not set in environment")
            return {
                "provider": "groq",
                "api_key": self.settings.GROQ_API_KEY,
                "model": self.settings.DEFAULT_LLM_MODEL,
                "temperature": self.settings.DEFAULT_TEMPERATURE,
                "max_tokens": self.settings.DEFAULT_MAX_TOKENS
            }
            
        elif provider == "deepseek":
            if not self.settings.DEEPSEEK_API_KEY:
                raise ValueError("DEEPSEEK_API_KEY is required but not set in environment")
            return {
                "provider": "deepseek",
                "api_key": self.settings.DEEPSEEK_API_KEY,
                "model": self.settings.DEEPSEEK_MODEL,
                "temperature": self.settings.DEEPSEEK_TEMPERATURE,
                "max_tokens": self.settings.DEEPSEEK_MAX_TOKENS
            }
            
        # Removed OpenAI and Gemini configurations
            
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: groq, deepseek")
    
    def create_llm(self, provider: Optional[str] = None, **override_params) -> Any:
        """
        Create an LLM instance using the specified or active provider.
        
        Args:
            provider: Optional provider name. If None, uses active provider.
            **override_params: Optional parameters to override default configuration
            
        Returns:
            LLM instance ready for use
            
        Example:
            # Use active provider from environment
            llm = provider_service.create_llm()
            
            # Use specific provider
            llm = provider_service.create_llm("deepseek")
            
            # Override default parameters
            llm = provider_service.create_llm("groq", temperature=0.9, streaming=True)
        """
        config = self.get_provider_config(provider)
        
        # Apply any override parameters
        config.update(override_params)
        
        provider_name = config["provider"]
        
        try:
            if provider_name == "groq":
                return LLMFactory.create_groq_llm(
                    api_key=config["api_key"],
                    model=config["model"],
                    temperature=config["temperature"],
                    streaming=config.get("streaming", False),
                    callbacks=config.get("callbacks")
                )
                
            elif provider_name == "deepseek":
                return LLMFactory.create_deepseek_llm(
                    api_key=config["api_key"],
                    model=config["model"],
                    temperature=config["temperature"],
                    streaming=config.get("streaming", False),
                    callbacks=config.get("callbacks")
                )
                
            # Removed OpenAI and Gemini LLM creation
                
        except Exception as e:
            self.logger.error(f"Failed to create LLM for provider {provider_name}: {str(e)}")
            raise
    
    def get_available_providers(self) -> Dict[str, bool]:
        """
        Get a list of available providers and their API key status.
        
        Returns:
            Dict mapping provider names to boolean indicating if API key is available
        """
        return {
            "groq": bool(self.settings.GROQ_API_KEY),
            "deepseek": bool(self.settings.DEEPSEEK_API_KEY)
        }
    
    def validate_provider_setup(self, provider: Optional[str] = None) -> bool:
        """
        Validate that the specified or active provider is properly configured.
        
        Args:
            provider: Optional provider name. If None, uses active provider.
            
        Returns:
            bool: True if provider is properly configured
        """
        try:
            self.get_provider_config(provider)
            return True
        except ValueError:
            return False
    
    def switch_provider(self, new_provider: str) -> None:
        """
        Switch to a different provider (for runtime switching).
        
        Note: This only affects the current instance, not the environment variable.
        To permanently change the provider, update the LLM_PROVIDER environment variable.
        
        Args:
            new_provider: The provider to switch to
            
        Raises:
            ValueError: If the new provider is not properly configured
        """
        if not self.validate_provider_setup(new_provider):
            raise ValueError(f"Provider {new_provider} is not properly configured")
        
        # Update the settings for this instance
        self.settings.LLM_PROVIDER = new_provider
        self.logger.info(f"Switched LLM provider to: {new_provider}")


# Global instance for easy access
_llm_provider_service: Optional[LLMProviderService] = None


def get_llm_provider_service() -> LLMProviderService:
    """
    Get the global LLMProviderService instance.
    
    Returns:
        LLMProviderService: The global service instance
    """
    global _llm_provider_service
    if _llm_provider_service is None:
        _llm_provider_service = LLMProviderService()
    return _llm_provider_service


def create_default_llm(**override_params) -> Any:
    """
    Convenience function to create an LLM using the active provider.
    
    Args:
        **override_params: Optional parameters to override default configuration
        
    Returns:
        LLM instance using the active provider
        
    Example:
        # Create LLM with default settings
        llm = create_default_llm()
        
        # Create LLM with custom temperature
        llm = create_default_llm(temperature=0.9, streaming=True)
    """
    service = get_llm_provider_service()
    return service.create_llm(**override_params)
