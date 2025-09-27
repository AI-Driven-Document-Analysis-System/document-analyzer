"""
Langfuse configuration and integration module.

This module provides safe integration with Langfuse for LLM observability
without breaking existing functionality. Langfuse is optional and can be
enabled/disabled via environment variables.
"""

import os
import logging
from typing import Optional, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import Langfuse components
try:
    from langfuse.langchain import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    logger.warning("Langfuse not available - observability disabled")
    CallbackHandler = None
    LANGFUSE_AVAILABLE = False

logger = logging.getLogger(__name__)


class LangfuseConfig:
    """
    Configuration class for Langfuse integration.
    
    This class handles Langfuse initialization and provides callback handlers
    for LLM tracing. It gracefully handles cases where Langfuse is disabled
    or credentials are missing.
    """
    
    def __init__(self):
        self.enabled = self._is_enabled()
        self.client: Optional[Langfuse] = None
        self.callback_handler: Optional[CallbackHandler] = None
        
        if self.enabled:
            self._initialize_langfuse()
    
    def _is_enabled(self) -> bool:
        """Check if Langfuse is enabled via environment variables."""
        print(f"DEBUG: LANGFUSE_AVAILABLE: {LANGFUSE_AVAILABLE}")
        print(f"DEBUG: CallbackHandler: {CallbackHandler}")
        print(f"DEBUG: LANGFUSE_ENABLED env: {os.getenv('LANGFUSE_ENABLED')}")
        print(f"DEBUG: LANGFUSE_SECRET_KEY env: {os.getenv('LANGFUSE_SECRET_KEY')[:10] if os.getenv('LANGFUSE_SECRET_KEY') else 'None'}")
        
        if not LANGFUSE_AVAILABLE or CallbackHandler is None:
            print("DEBUG: Langfuse is not available or CallbackHandler not found. Disabling Langfuse.")
            return False
            
        enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
        has_credentials = all([
            os.getenv("LANGFUSE_SECRET_KEY"),
            os.getenv("LANGFUSE_PUBLIC_KEY")
        ])
        
        print(f"DEBUG: enabled: {enabled}, has_credentials: {has_credentials}")
        
        if enabled and not has_credentials:
            print("DEBUG: Langfuse is enabled but credentials are missing. Disabling Langfuse.")
            return False
        
        return enabled
    
    def _initialize_langfuse(self) -> None:
        """Initialize Langfuse client and callback handler."""
        if not LANGFUSE_AVAILABLE:
            logger.warning("Cannot initialize Langfuse - module not available")
            self.enabled = False
            return
            
        try:
            # Set environment variables for automatic pickup
            os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
            os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY") 
            os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            self.callback_handler = CallbackHandler()
            self.client = None
            
            logger.info("Langfuse initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            self.enabled = False
            self.client = None
            self.callback_handler = None
    
    def get_callback_handler(self) -> Optional[CallbackHandler]:
        """
        Get Langfuse callback handler for LLM tracing.
        
        Returns:
            CallbackHandler if Langfuse is enabled, None otherwise
        """
        return self.callback_handler if self.enabled else None
    
    def get_callbacks(self) -> List[Any]:
        """
        Get list of callbacks for LLM integration.
        
        Returns:
            List containing Langfuse callback if enabled, empty list otherwise
        """
        if self.enabled and self.callback_handler:
            return [self.callback_handler]
        return []
    
    def create_trace(self, name: str, user_id: Optional[str] = None, 
                     session_id: Optional[str] = None, **kwargs) -> Optional[Any]:
        """
        Create a new trace for tracking LLM interactions.
        
        Args:
            name: Name of the trace
            user_id: Optional user identifier
            session_id: Optional session identifier
            **kwargs: Additional trace metadata
            
        Returns:
            Trace object if Langfuse is enabled, None otherwise
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            trace_data = {"name": name, **kwargs}
            if user_id:
                trace_data["user_id"] = user_id
            if session_id:
                trace_data["session_id"] = session_id
                
            return self.client.trace(**trace_data)
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return None
    
    def flush(self) -> None:
        """Flush pending traces to Langfuse."""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to flush Langfuse traces: {e}")


# Global Langfuse configuration instance
_langfuse_config: Optional[LangfuseConfig] = None


def get_langfuse_config() -> LangfuseConfig:
    """
    Get the global Langfuse configuration instance.
    
    Returns:
        LangfuseConfig: Global configuration instance
    """
    global _langfuse_config
    # Force recreation to pick up environment changes
    _langfuse_config = LangfuseConfig()
    return _langfuse_config


def get_langfuse_callbacks() -> List[Any]:
    """
    Get Langfuse callbacks for LLM integration.
    
    This is a convenience function that returns callbacks if Langfuse is enabled,
    or an empty list if disabled. Safe to use in existing LLM configurations.
    
    Returns:
        List of callbacks (empty if Langfuse is disabled)
    """
    config = get_langfuse_config()
    callbacks = config.get_callbacks()
    print(f"DEBUG: Langfuse enabled: {config.enabled}, callbacks: {len(callbacks)}")
    if callbacks:
        print(f"DEBUG: Callback handler: {callbacks[0]}")
        try:
            callbacks[0].langfuse.auth_check()
            print("DEBUG: Langfuse auth check passed")
        except Exception as e:
            print(f"DEBUG: Langfuse auth check failed: {e}")
    return callbacks


def is_langfuse_enabled() -> bool:
    """
    Check if Langfuse is enabled and properly configured.
    
    Returns:
        bool: True if Langfuse is enabled, False otherwise
    """
    return get_langfuse_config().enabled
