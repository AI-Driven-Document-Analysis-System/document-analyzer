from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional, List, Any


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
        # Set up callback manager if streaming is enabled and callbacks are provided
        if streaming and callbacks:
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
                callback_manager=callback_manager
            )
        # Use OpenAI for other models (completion-based interface)
        else:
            return OpenAI(
                openai_api_key=api_key,
                model_name=model,
                temperature=temperature,
                streaming=streaming,
                callback_manager=callback_manager
            )

    @staticmethod
    def create_llama_llm(model_path: str, temperature: float = 0.7,
                         max_tokens: int = 1000, streaming: bool = False,
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
                max_tokens=1000,
                streaming=True
            )
        """
        # Set up callback manager if streaming is enabled and callbacks are provided
        if streaming and callbacks:
            callback_manager = CallbackManager(callbacks)
        else:
            callback_manager = None

        # Create and return LlamaCpp instance with specified configuration
        return LlamaCpp(
            model_path=model_path,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            callback_manager=callback_manager,
            verbose=True  # Enable verbose output for debugging
        )