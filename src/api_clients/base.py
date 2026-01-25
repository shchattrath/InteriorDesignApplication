"""Base class for image editing API clients."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Dict, Any


class BaseImageEditClient(ABC):
    """Abstract base class for image editing API clients."""

    def __init__(self, api_key: str):
        """Initialize the client with an API key."""
        self.api_key = api_key

    @abstractmethod
    def edit_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        **kwargs
    ) -> str:
        """
        Edit an image based on a text prompt.

        Args:
            image_path: Path to the input image
            prompt: Text description of desired edits
            **kwargs: Additional provider-specific parameters

        Returns:
            URL or path to the edited image
        """
        pass

    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this API provider."""
        pass
