"""Configuration management for the image editing pipeline."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for API credentials and settings."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    INPUT_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"

    # API Keys
    REPLICATE_API_KEY: Optional[str] = os.getenv("REPLICATE_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    STABILITY_API_KEY: Optional[str] = os.getenv("STABILITY_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

    # Default settings
    DEFAULT_API_PROVIDER: str = os.getenv("DEFAULT_API_PROVIDER", "replicate")

    @classmethod
    def validate_api_key(cls, provider: str) -> bool:
        """Validate that the API key for a given provider exists."""
        key_map = {
            "replicate": cls.REPLICATE_API_KEY,
            "openai": cls.OPENAI_API_KEY,
            "stability": cls.STABILITY_API_KEY,
            "google": cls.GOOGLE_API_KEY,
        }

        key = key_map.get(provider.lower())
        if not key:
            raise ValueError(
                f"No API key found for provider '{provider}'. "
                f"Please set it in your .env file."
            )
        return True

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
