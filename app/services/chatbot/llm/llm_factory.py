from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional, List, Any


class LLMFactory:
    @staticmethod
    def create_openai_llm(api_key: str, model: str = "gpt-3.5-turbo",
                          temperature: float = 0.7, streaming: bool = False,
                          callbacks: Optional[List[Any]] = None) -> Any:
        if streaming and callbacks:
            callback_manager = CallbackManager(callbacks)
        else:
            callback_manager = None

        if model.startswith("gpt-"):
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name=model,
                temperature=temperature,
                streaming=streaming,
                callback_manager=callback_manager
            )
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
        if streaming and callbacks:
            callback_manager = CallbackManager(callbacks)
        else:
            callback_manager = None

        return LlamaCpp(
            model_path=model_path,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            callback_manager=callback_manager,
            verbose=True
        )