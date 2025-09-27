from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from typing import Any, List, Optional, Dict
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional, List, Any
from ....core.langfuse_config import get_langfuse_callbacks

# Optional imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False





class LLMFactory:
    """
    Factory class for creating Language Model instances.
    
    This class provides static methods to create different types of LLMs:
    - OpenAI models (both chat and completion models)
    - Local Llama models using LlamaCpp
    
    The factory handles configuration differences between model types and provides
    a unified interface for LLM creation.
    """
    
    @staticmethod
    def create_openai_llm(api_key: str, model: str = "gpt-3.5-turbo",
                          temperature: float = 0.7, streaming: bool = False,
                          callbacks: Optional[List[Any]] = None) -> Any:
        """
        Create an OpenAI Language Model instance.
        
        This method creates either a ChatOpenAI or OpenAI instance depending on the
        model name. Chat models (starting with "gpt-") use ChatOpenAI, while other
        models use the standard OpenAI completion interface.
        
        Args:
            api_key (str): OpenAI API key for authentication
            model (str): Model name (e.g., "gpt-3.5-turbo", "gpt-4", "text-davinci-003")
            temperature (float): Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
            streaming (bool): Whether to enable streaming responses
            callbacks (Optional[List[Any]]): List of callback handlers for monitoring and logging
            
        Returns:
            Any: Either ChatOpenAI or OpenAI instance configured with the specified parameters
            
        Example:
            # Create a streaming GPT-3.5-turbo model
            llm = LLMFactory.create_openai_llm(
                api_key="your-api-key",
                model="gpt-3.5-turbo",
                temperature=0.7,
                streaming=True
            )
        """
        # Set up callback manager if callbacks are available
        if callbacks:
            callback_manager = CallbackManager(callbacks)
        else:
            callback_manager = None

        # Use ChatOpenAI for GPT models (chat-based interface)
        if model.startswith("gpt-"):
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name=model,
                temperature=temperature,
                streaming=streaming,
                callbacks=callbacks
            )
        # Use OpenAI for other models (completion-based interface)
        else:
            return OpenAI(
                openai_api_key=api_key,
                model_name=model,
                temperature=temperature,
                streaming=streaming,
                callbacks=callbacks
            )

    @staticmethod
    def create_gemini_llm(api_key: str, model: str = "gemini-1.5-flash",
                          temperature: float = 0.7, streaming: bool = False,
                          callbacks: Optional[List[Any]] = None) -> Any:
        """
        This method creates a ChatGoogleGenerativeAI instance for Google's Generative AI models.
        This is the correct integration for the new Google Generative AI API (Gemini models).
        
        Args:
            api_key (str): Google AI API key for authentication
            model (str): Model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro")
            temperature (float): Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
            streaming (bool): Whether to enable streaming responses
            callbacks (Optional[List[Any]]): List of callback handlers for monitoring and logging
            
        Returns:
            ChatGoogleGenerativeAI: Configured instance for Google Generative AI models
            
        Example:
            # Create a streaming Gemini model
            llm = LLMFactory.create_gemini_llm(
                api_key="your-google-api-key",
                model="gemini-1.5-flash",
                temperature=0.7,
                streaming=True
            )
            
            # Create a non-streaming Gemini model
            llm = LLMFactory.create_gemini_llm(
                api_key="your-google-api-key",
                model="gemini-1.5-pro",
                temperature=0.5,
                streaming=False
            )
        """
        # Set up callback manager if callbacks are available
        if callbacks:
            callback_manager = CallbackManager(callbacks)
        else:
            callback_manager = None

        # Check if Gemini is available
        if not GEMINI_AVAILABLE:
            raise ImportError("langchain_google_genai is not installed. Install it with: pip install langchain-google-genai")
        
        # Use ChatGoogleGenerativeAI for all Gemini models
        # This is the correct integration for the new Google Generative AI API
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=temperature,
            callbacks=callbacks
        )

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