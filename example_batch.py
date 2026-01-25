"""Example: Process multiple interior design images in batch."""

from pathlib import Path
from src.pipeline import ImageEditingPipeline


def main():
    """Process multiple images with design prompts."""

    # Initialize the pipeline
    pipeline = ImageEditingPipeline(provider="replicate")

    # List of input images
    input_images = [
        Path("data/input/living_room.jpg"),
        Path("data/input/bedroom.jpg"),
        Path("data/input/kitchen.jpg"),
    ]

    # Option 1: Use the same prompt for all images
    single_prompt = "modern scandinavian interior, bright and airy, natural materials"

    # Option 2: Use different prompts for each image
    individual_prompts = [
        "cozy living room with fireplace, warm lighting, comfortable seating",
        "serene bedroom with soft colors, minimalist design, natural textures",
        "modern kitchen with marble countertops, stainless steel appliances, island",
    ]

    # Process with a single prompt (uncomment to use)
    # results = pipeline.process_batch(
    #     image_paths=input_images,
    #     prompts=single_prompt,
    #     guidance_scale=7.5,
    # )

    # Process with individual prompts
    try:
        results = pipeline.process_batch(
            image_paths=input_images,
            prompts=individual_prompts,
            guidance_scale=7.5,
            num_inference_steps=50,
        )

        print("\n" + "=" * 50)
        print("Batch Processing Complete!")
        print("=" * 50)

        for input_img, output_path in zip(input_images, results):
            if output_path:
                print(f"✓ {input_img.name} → {output_path.name}")
            else:
                print(f"✗ {input_img.name} → Failed")

    except Exception as e:
        print(f"Error during batch processing: {e}")


def process_directory():
    """Alternative: Process all images in a directory."""

    pipeline = ImageEditingPipeline(provider="replicate")

    # Get all images from input directory
    input_dir = Path("data/input")
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    input_images = [
        img for img in input_dir.iterdir()
        if img.suffix.lower() in image_extensions
    ]

    if not input_images:
        print("No images found in data/input/")
        return

    print(f"Found {len(input_images)} images to process")

    # Use the same prompt for all
    prompt = "luxury interior design, elegant furniture, professional photography"

    results = pipeline.process_batch(
        image_paths=input_images,
        prompts=prompt,
    )

    print(f"\nProcessed {sum(1 for r in results if r)} images successfully")


if __name__ == "__main__":
    # Run the main batch example
    main()

    # Or process an entire directory
    # process_directory()
