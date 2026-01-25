"""Main image editing pipeline for interior design modifications."""

import requests
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
from PIL import Image
from tqdm import tqdm

from ..config import Config
from ..api_clients import BaseImageEditClient, ReplicateClient, GoogleGeminiClient


class ImageEditingPipeline:
    """
    Flexible image editing pipeline that supports single and batch processing.

    This pipeline can process one or many images with text prompts to generate
    edited versions for interior design applications.
    """

    def __init__(
        self,
        api_client: Optional[BaseImageEditClient] = None,
        provider: str = None,
        output_dir: Union[str, Path] = None
    ):
        """
        Initialize the image editing pipeline.

        Args:
            api_client: Pre-configured API client (optional)
            provider: API provider name if api_client not provided
            output_dir: Directory to save edited images
        """
        Config.ensure_directories()

        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up API client
        if api_client:
            self.client = api_client
        else:
            provider = provider or Config.DEFAULT_API_PROVIDER
            self.client = self._create_client(provider)

    def _create_client(self, provider: str) -> BaseImageEditClient:
        """Create an API client based on the provider name."""
        Config.validate_api_key(provider)

        if provider.lower() == "replicate":
            return ReplicateClient(api_key=Config.REPLICATE_API_KEY)
        elif provider.lower() == "google":
            return GoogleGeminiClient(api_key=Config.GOOGLE_API_KEY)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def process_single(
        self,
        image_path: Union[str, Path],
        prompt: str,
        output_name: Optional[str] = None,
        **kwargs
    ) -> Path:
        """
        Process a single image with a prompt.

        Args:
            image_path: Path to input image
            prompt: Text description of desired edits
            output_name: Optional custom name for output file
            **kwargs: Additional API-specific parameters

        Returns:
            Path to the edited image
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        print(f"Processing: {image_path.name}")
        print(f"Prompt: {prompt}")

        # Call API to edit image
        result_url = self.client.edit_image(image_path, prompt, **kwargs)

        # Download and save the result
        if output_name:
            output_path = self.output_dir / output_name
        else:
            stem = image_path.stem
            suffix = image_path.suffix
            output_path = self.output_dir / f"{stem}_edited{suffix}"

        self._download_image(result_url, output_path)

        print(f"Saved to: {output_path}")
        return output_path

    def process_batch(
        self,
        image_paths: List[Union[str, Path]],
        prompts: Union[str, List[str]],
        output_names: Optional[List[str]] = None,
        **kwargs
    ) -> List[Path]:
        """
        Process multiple images with prompts.

        Args:
            image_paths: List of paths to input images
            prompts: Single prompt for all images, or list of prompts (one per image)
            output_names: Optional list of custom names for output files
            **kwargs: Additional API-specific parameters

        Returns:
            List of paths to edited images
        """
        # Handle single prompt for all images
        if isinstance(prompts, str):
            prompts = [prompts] * len(image_paths)

        if len(prompts) != len(image_paths):
            raise ValueError(
                f"Number of prompts ({len(prompts)}) must match "
                f"number of images ({len(image_paths)})"
            )

        if output_names and len(output_names) != len(image_paths):
            raise ValueError(
                f"Number of output names ({len(output_names)}) must match "
                f"number of images ({len(image_paths)})"
            )

        results = []
        print(f"\nProcessing {len(image_paths)} images...")

        for i, (img_path, prompt) in enumerate(tqdm(
            zip(image_paths, prompts),
            total=len(image_paths),
            desc="Editing images"
        )):
            output_name = output_names[i] if output_names else None

            try:
                result_path = self.process_single(
                    img_path,
                    prompt,
                    output_name=output_name,
                    **kwargs
                )
                results.append(result_path)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                results.append(None)

        successful = sum(1 for r in results if r is not None)
        print(f"\nCompleted: {successful}/{len(image_paths)} images processed successfully")

        return results

    def process(
        self,
        image_input: Union[str, Path, List[Union[str, Path]]],
        prompt: Union[str, List[str]],
        **kwargs
    ) -> Union[Path, List[Path]]:
        """
        Flexible processing method that handles both single and batch inputs.

        Args:
            image_input: Single image path or list of image paths
            prompt: Single prompt or list of prompts
            **kwargs: Additional API-specific parameters

        Returns:
            Single path or list of paths to edited images
        """
        # Determine if single or batch processing
        if isinstance(image_input, (str, Path)):
            # Single image
            return self.process_single(image_input, prompt, **kwargs)
        else:
            # Batch processing
            return self.process_batch(image_input, prompt, **kwargs)

    def _download_image(self, url_or_path: str, output_path: Path):
        """Download an image from a URL or copy from local path and save it."""
        # Check if it's a local file path (for Google Gemini) or URL (for Replicate)
        if Path(url_or_path).exists():
            # It's a local file path - just copy it
            import shutil
            shutil.copy2(url_or_path, output_path)
            # Clean up temp file if it exists
            try:
                Path(url_or_path).unlink()
            except:
                pass
        else:
            # It's a URL - download it
            response = requests.get(url_or_path, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the current API client."""
        return {
            "client_type": type(self.client).__name__,
            "default_params": self.client.get_default_params(),
        }
