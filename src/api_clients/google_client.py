"""Google Gemini API client for image editing (Nano Banana)."""

from google import genai
from pathlib import Path
from typing import Union, Dict, Any
from PIL import Image
import tempfile

from .base import BaseImageEditClient


class GoogleGeminiClient(BaseImageEditClient):
    """Client for Google Gemini API image editing (Nano Banana)."""

    DEFAULT_MODEL = "nano-banana-pro-preview"  # Nano Banana Pro for image editing

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize Google Gemini client.

        Args:
            api_key: Google AI Studio API key
            model: Model identifier (defaults to Gemini 2.0 Flash for image editing)
        """
        super().__init__(api_key)
        self.client = genai.Client(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def edit_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        **kwargs
    ) -> str:
        """
        Edit an image using Google Gemini's image editing.

        Args:
            image_path: Path to the input image
            prompt: Text description of desired edits
            **kwargs: Additional parameters (currently not used for Gemini)

        Returns:
            Path to the edited image (saved locally)
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load the image
        image = Image.open(image_path)

        # Create the prompt for image editing
        edit_prompt = f"Edit this image: {prompt}. Preserve the overall structure and composition while making the requested changes."

        # Generate edited image
        response = self.client.models.generate_content(
            model=self.model,
            contents=[edit_prompt, image]
        )

        # Check if we got a response with image data
        if not response.parts or len(response.parts) == 0:
            raise ValueError(
                "No response parts generated. The model may not support image generation."
            )

        # Get the image data from the response
        image_part = response.parts[0]

        if not hasattr(image_part, 'inline_data') or not image_part.inline_data:
            raise ValueError(
                "No image data in response. The model may not support image generation."
            )

        # Save the generated image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_path = temp_file.name

        # Write the image bytes to file
        with open(temp_path, 'wb') as f:
            f.write(image_part.inline_data.data)

        temp_file.close()

        return temp_path

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for Google Gemini."""
        return {
            # Gemini doesn't expose many parameters for image editing
            # Most control comes from the prompt
        }

    def set_model(self, model: str):
        """Change the model being used."""
        self.model = model
