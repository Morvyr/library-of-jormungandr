"""
Base Tool Class for the Library of Jörmungandr

All tools in the library inherit from this base class to ensure 
consistency, maintainability, and composability.
"""

import sys
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseTool(ABC):
    """
    Abstract base class for all library tools.

    Provides standard structure, error handling, and logging.
    All tools must implement the abstract methods.
    """
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize the base tool.

        Args:
            name: Tool name (e.g., "CSV Cleaner", "Web Scraper")
            version: Tool version following semantic versioning
        """

        self.name = name
        self.version = version
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Configure logging for the tool.

        Returns:
            Configured logger instance
        """

        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)

        #Only add handler if this logger doesn't have any yet
        if not logger.handlers:
            # Console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)

            # Format: [TOOL_NAME] MESSAGE
            formatter = logging.Formatter(f'[{self.name}] %(message)s')
            handler.setFormatter(formatter)

            logger.addHandler(handler)
        return logger
    
    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """
        Validate input parameters before processing.

        Must be implemented by each tool.

        Returns:
            True if input is valid, False otherwise
        """
        
        pass

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """
        Core processing logic of the tool.

        Must be implemented by each tool.

        Returns:
            Processed result(type varies by tool)
        """

        pass

    def run(self, *args, **kwargs) -> Optional[Any]:
        """
        Execute the complete tool workflow: validate -> process -> return.
        This method orchestrates the tool execution and handles errors.

        Returns:
            Result from process() or None if validation/processing fails
        """
        try:
            self.logger.info(f"Starting {self.name} v{self.version}")

            # Validate input
            if not self.validate_input(*args, **kwargs):
                self.logger.error("Input validation failed")
                return None
            
            # Process
            result = self.process(*args, **kwargs)

            self.logger.info(f"{self.name} completed successfully")
            return result
        
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            return None
        
    def get_info(self) -> Dict[str, str]:
        """
        Return tool metadata.

        Returns:
        Dictionary containing tool name and version
        """

        return {
            "name": self.name,
            "version": self.version
        }