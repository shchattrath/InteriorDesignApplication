"""Example: Using the flexible process() method for both single and batch."""

from pathlib import Path
from src.pipeline import ImageEditingPipeline


def main():
    """Demonstrate the flexible process() method."""

    pipeline = ImageEditingPipeline(provider="replicate")

    print("=" * 60)
    print("FLEXIBLE IMAGE EDITING PIPELINE")
    print("=" * 60)

    # Example 1: Process a single image
    print("\n[1] Processing single image...")
    single_result = pipeline.process(
        image_input="data/input/living_room.jpg",
        prompt="modern industrial loft, exposed brick, high ceilings",
        guidance_scale=8.0,
    )
    print(f"    Result: {single_result}")

    # Example 2: Process multiple images with same prompt
    print("\n[2] Processing batch with same prompt...")
    batch_result = pipeline.process(
        image_input=[
            "data/input/room1.jpg",
            "data/input/room2.jpg",
            "data/input/room3.jpg",
        ],
        prompt="bright and airy coastal style interior",
    )
    print(f"    Processed {len([r for r in batch_result if r])} images")

    # Example 3: Process multiple images with different prompts
    print("\n[3] Processing batch with individual prompts...")
    batch_result_custom = pipeline.process(
        image_input=[
            "data/input/living_room.jpg",
            "data/input/bedroom.jpg",
        ],
        prompt=[
            "rustic farmhouse living room with vintage furniture",
            "zen minimalist bedroom with platform bed",
        ],
        num_inference_steps=40,
    )

    # Get info about the current client
    print("\n" + "=" * 60)
    print("CLIENT INFORMATION")
    print("=" * 60)
    client_info = pipeline.get_client_info()
    print(f"Client Type: {client_info['client_type']}")
    print(f"Default Parameters:")
    for param, value in client_info['default_params'].items():
        print(f"  - {param}: {value}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"\n⚠ Error: {e}")
        print("\nTo run this example:")
        print("1. Place some test images in the data/input/ directory")
        print("2. Set up your .env file with API credentials")
        print("3. Run: python example_flexible.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
