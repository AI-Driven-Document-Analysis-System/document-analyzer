# Removed OpenAI imports - only using Groq and DeepSeek
from langchain_groq import ChatGroq
from typing import Any, List, Optional, Dict
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional, List, Any
from ....core.langfuse_config import get_langfuse_callbacks

# Import ChatOpenAI for DeepSeek (uses OpenAI-compatible API)
try:
    from langchain_community.chat_models import ChatOpenAI
    OPENAI_COMPATIBLE_AVAILABLE = True
except ImportError:
    OPENAI_COMPATIBLE_AVAILABLE = False





class LLMFactory:
    """
    Factory class for creating Language Model instances.
    
    This class provides static methods to create different types of LLMs:
    - Groq models (fast inference)
    - DeepSeek models (OpenAI-compatible API)
    - Local Llama models using LlamaCpp
    
    The factory handles configuration differences between model types and provides
    a unified interface for LLM creation.
    """
    
    # Removed OpenAI and Gemini methods - only keeping Groq and DeepSeek

    @staticmethod
    def create_groq_llm(api_key: str, model: str = "llama-3.1-8b-instant",
                        temperature: float = 0.7, streaming: bool = False,
                        callbacks: Optional[List[Any]] = None) -> Any:
        """
        Create a Groq chat model instance using the LangChain Groq integration.

        Args:
            api_key (str): Groq API key for authentication
            model (str): Model name (e.g., "llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768")
            temperature (float): Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
            streaming (bool): Whether to enable streaming responses
            callbacks (Optional[List[Any]]): List of callback handlers for monitoring and logging

        Returns:
            ChatGroq: Configured instance for Groq-hosted models
        """
        return ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks,
        )

    @staticmethod
    def create_deepseek_llm(api_key: str, model: str = "deepseek-chat",
                           temperature: float = 0.7, streaming: bool = False,
                           callbacks: Optional[List[Any]] = None) -> Any:
        """
        Create a DeepSeek chat model instance using OpenAI-compatible API.
        
        DeepSeek provides an OpenAI-compatible API, so we can use the ChatOpenAI class
        with a custom base_url pointing to DeepSeek's API endpoint.
        
        Args:
            api_key (str): DeepSeek API key for authentication
            model (str): Model name (e.g., "deepseek-chat", "deepseek-coder")
            temperature (float): Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
            streaming (bool): Whether to enable streaming responses
            callbacks (Optional[List[Any]]): List of callback handlers for monitoring and logging
            
        Returns:
            ChatOpenAI: Configured instance for DeepSeek models using OpenAI-compatible interface
            
        Example:
            # Create a streaming DeepSeek model
            llm = LLMFactory.create_deepseek_llm(
                api_key="your-deepseek-api-key",
                model="deepseek-chat",
                temperature=0.7,
                streaming=True
            )
        """
        return ChatOpenAI(
            openai_api_key=api_key,
            model_name=model,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks,
            openai_api_base="https://api.deepseek.com/v1",  # DeepSeek API endpoint
            max_tokens=4000  # DeepSeek models support up to 4K tokens
        )

    @staticmethod
    def create_llama_llm(model_path: str, temperature: float = 0.7,
                         max_tokens: int = 2000, streaming: bool = False,
                         callbacks: Optional[List[Any]] = None) -> LlamaCpp:
        """
        Create a local Llama Language Model instance using LlamaCpp.
        
        This method creates a LlamaCpp instance for running Llama models locally.
        LlamaCpp provides efficient inference for Llama models on CPU/GPU.
        
        Args:
            model_path (str): Path to the local Llama model file (.gguf, .bin, etc.)
            temperature (float): Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
            max_tokens (int): Maximum number of tokens to generate in response
            streaming (bool): Whether to enable streaming responses
            callbacks (Optional[List[Any]]): List of callback handlers for monitoring and logging
            
        Returns:
            LlamaCpp: Configured LlamaCpp instance for local model inference
            
        Example:
            # Create a local Llama model
            llm = LLMFactory.create_llama_llm(
                model_path="/path/to/llama-2-7b.gguf",
                temperature=0.7,
                max_tokens=2000,
                streaming=True
            )
        """
        # Set up callback manager if callbacks are available
        if callbacks:
            callback_manager = CallbackManager(callbacks)
        else:
            callback_manager = None

        return LlamaCpp(
            model_path=model_path,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            callbacks=callbacks,
            verbose=True
        )