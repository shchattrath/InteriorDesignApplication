"""Replicate API client for image editing."""

import replicate
from pathlib import Path
from typing import Union, Dict, Any

from .base import BaseImageEditClient


class ReplicateClient(BaseImageEditClient):
    """Client for Replicate API image editing models."""

    # For image-to-image editing with structure preservation
    DEFAULT_MODEL = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize Replicate client.

        Args:
            api_key: Replicate API key
            model: Model identifier (defaults to SDXL img2img)
        """
        super().__init__(api_key)
        self.client = replicate.Client(api_token=api_key)
        self.model = model or self.DEFAULT_MODEL

    def edit_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        **kwargs
    ) -> str:
        """
        Edit an image using Replicate's image editing models.

        Args:
            image_path: Path to the input image
            prompt: Text description of desired edits
            **kwargs: Additional parameters like:
                - negative_prompt: What to avoid in the image
                - num_inference_steps: Number of denoising steps
                - guidance_scale: How closely to follow the prompt
                - strength: How much to transform the image (0-1)

        Returns:
            URL to the edited image
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Prepare parameters
        params = self.get_default_params()
        params.update(kwargs)

        # Open image file
        with open(image_path, "rb") as image_file:
            # Run the model
            output = self.client.run(
                self.model,
                input={
                    "image": image_file,
                    "prompt": prompt,
                    **params
                }
            )

        # Output is typically a list of URLs or a single URL
        if isinstance(output, list):
            return output[0] if output else None
        return output

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for SDXL img2img."""
        return {
            "guidance_scale": 7.5,
            "num_inference_steps": 50,
            "strength": 0.6,  # How much to change: 0.0=no change, 1.0=complete change
            "negative_prompt": "ugly, blurry, poor quality, distorted",
            "num_outputs": 1,
        }

    def set_model(self, model: str):
        """Change the model being used."""
        self.model = model
