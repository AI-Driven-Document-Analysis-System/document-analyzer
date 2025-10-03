"""
Configuration manager for RAGAS evaluation system.

This module handles reading configuration from .testing file and managing
evaluation recording settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RAGASConfig:
    """Configuration manager for RAGAS evaluation system."""
    
    def __init__(self, config_file: str = ".testing"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (relative to project root)
        """
        self.config_file = config_file
        self.project_root = self._find_project_root()
        self.config_path = self.project_root / config_file
        self._config = {}
        self._load_config()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for common markers."""
        current = Path(__file__).parent
        
        # Look for project markers going up the directory tree
        markers = ['.git', 'requirements.txt', 'pyproject.toml', 'setup.py', '.testing']
        
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
        
        # Fallback to current directory's parent structure
        # Assuming structure: project_root/evaluation/rag-chatbot/config_manager.py
        return Path(__file__).parent.parent.parent
    
    def _load_config(self):
        """Load configuration from .testing file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file {self.config_path} not found. Using defaults.")
                self._set_defaults()
                return
            
            with open(self.config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert boolean strings
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        
                        self._config[key] = value
            
            logger.info(f"Loaded RAGAS configuration from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default configuration values."""
        self._config = {
            'RAGAS_EVALUATION_ENABLED': False,
            'RAGAS_SESSION_NAME': 'Default Evaluation Session',
            'RAGAS_SESSION_DESCRIPTION': 'Chatbot evaluation session',
            'RAGAS_DB_PATH': 'evaluation/rag-chatbot/ragas_evaluation.db',
            'RAGAS_VERBOSE_LOGGING': False
        }
        logger.info("Using default RAGAS configuration")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)
    
    def is_evaluation_enabled(self) -> bool:
        """Check if RAGAS evaluation is enabled."""
        return self.get('RAGAS_EVALUATION_ENABLED', False)
    
    def get_session_name(self) -> str:
        """Get evaluation session name."""
        return self.get('RAGAS_SESSION_NAME', 'Default Evaluation Session')
    
    def get_session_description(self) -> str:
        """Get evaluation session description."""
        return self.get('RAGAS_SESSION_DESCRIPTION', 'Chatbot evaluation session')
    
    def get_db_path(self) -> str:
        """Get database path (relative to project root)."""
        db_path = self.get('RAGAS_DB_PATH', 'evaluation/rag-chatbot/ragas_evaluation.db')
        return str(self.project_root / db_path)
    
    def is_verbose_logging_enabled(self) -> bool:
        """Check if verbose logging is enabled."""
        return self.get('RAGAS_VERBOSE_LOGGING', False)
    
    def reload_config(self):
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self._config.copy()
    
    def update_config(self, key: str, value: Any):
        """
        Update configuration value and save to file.
        
        Args:
            key: Configuration key
            value: New value
        """
        self._config[key] = value
        self._save_config()
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                f.write("# RAGAS Evaluation Configuration\n")
                f.write("# Set to true/false to enable/disable chatbot data recording for evaluation\n\n")
                
                for key, value in self._config.items():
                    if isinstance(value, bool):
                        value_str = str(value).lower()
                    else:
                        value_str = str(value)
                    
                    f.write(f"{key}={value_str}\n")
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")


# Global configuration instance
_config_instance = None

def get_ragas_config() -> RAGASConfig:
    """Get global RAGAS configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = RAGASConfig()
    return _config_instance

def reload_ragas_config():
    """Reload global configuration."""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload_config()

def is_ragas_enabled() -> bool:
    """Quick check if RAGAS evaluation is enabled."""
    return get_ragas_config().is_evaluation_enabled()


if __name__ == "__main__":
    # Test configuration
    config = RAGASConfig()
    
    print("RAGAS Configuration:")
    print(f"  Evaluation enabled: {config.is_evaluation_enabled()}")
    print(f"  Session name: {config.get_session_name()}")
    print(f"  Database path: {config.get_db_path()}")
    print(f"  Verbose logging: {config.is_verbose_logging_enabled()}")
    
    print(f"\nAll config: {config.get_all_config()}")
