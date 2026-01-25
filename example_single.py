"""Example: Process a single interior design image."""

from pathlib import Path
from src.pipeline import ImageEditingPipeline


def main():
    """Process a single image with a design prompt."""

    # Initialize the pipeline with Google Gemini (Nano Banana) - FREE!
    pipeline = ImageEditingPipeline(provider="google")

    # Path to your input image
    input_image = Path("data/input/MyRoomExample.png")

    # Design prompt describing the desired changes
    prompt = "night time, ambient lighting, lamps on"

    # Optional: Additional parameters for fine-tuning
    # Note: Google Gemini doesn't use these parameters, control is via prompt
    params = {}

    # Process the image
    try:
        output_path = pipeline.process_single(
            image_path=input_image,
            prompt=prompt,
            **params
        )
        print(f"\nSuccessfully edited image!")
        print(f"Output saved to: {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease place your image in the data/input/ directory")
    except Exception as e:
        print(f"Error during processing: {e}")


if __name__ == "__main__":
    main()
