"""Insert an interior design item into a room scene using Gemini API."""

import argparse
from pathlib import Path
from PIL import Image
from google import genai
from src.config import Config


def insert_item_into_scene(
    room_image_path: str,
    item_image_path: str,
    prompt: str,
    output_path: str = None,
    model: str = "nano-banana-pro-preview"
):
    """
    Insert an interior design item into a room scene.

    Args:
        room_image_path: Path to the room/scene image
        item_image_path: Path to the furniture/item image to insert
        prompt: Description of where/how to place the item
        output_path: Optional output path (defaults to data/output/)
        model: Gemini model to use

    Returns:
        Path to the generated image
    """
    # Validate inputs
    room_path = Path(room_image_path)
    item_path = Path(item_image_path)

    if not room_path.exists():
        raise FileNotFoundError(f"Room image not found: {room_path}")
    if not item_path.exists():
        raise FileNotFoundError(f"Item image not found: {item_path}")

    # Load images
    print(f"Loading room image: {room_path.name}")
    room_image = Image.open(room_path)

    print(f"Loading item image: {item_path.name}")
    item_image = Image.open(item_path)

    # Initialize Gemini client
    Config.validate_api_key("google")
    client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    # Create a detailed prompt for image composition
    full_prompt = f"""You are an expert interior designer and image compositor.

I have two images:
1. A room/interior space (first image)
2. A furniture/decor item (second image)

Your task: Seamlessly integrate the furniture item from the second image into the room from the first image.

Placement instructions: {prompt}

Requirements:
- Maintain realistic lighting that matches the room
- Ensure proper perspective and scale
- Match shadows and reflections appropriately
- Blend the item naturally into the scene
- Preserve the room's existing style and atmosphere

Generate a photorealistic composite image showing the item placed in the room as described."""

    print(f"\nGenerating composite image...")
    print(f"Prompt: {prompt}")

    # Call Gemini with both images
    response = client.models.generate_content(
        model=model,
        contents=[full_prompt, room_image, item_image]
    )

    # Extract the generated image
    if not response.parts or len(response.parts) == 0:
        raise ValueError("No image generated in response")

    image_part = response.parts[0]
    if not hasattr(image_part, 'inline_data') or not image_part.inline_data:
        raise ValueError("No image data in response")

    # Determine output path
    if output_path:
        output_file = Path(output_path)
    else:
        Config.ensure_directories()
        room_stem = room_path.stem
        item_stem = item_path.stem
        output_file = Config.OUTPUT_DIR / f"{room_stem}_with_{item_stem}.jpg"

    # Save the generated image
    with open(output_file, 'wb') as f:
        f.write(image_part.inline_data.data)

    print(f"\nSuccess! Composite image saved to: {output_file}")
    return output_file


def main():
    """Command-line interface for item insertion."""
    parser = argparse.ArgumentParser(
        description="Insert an interior design item into a room scene"
    )
    parser.add_argument(
        "room_image",
        help="Path to the room/scene image"
    )
    parser.add_argument(
        "item_image",
        help="Path to the furniture/item image to insert"
    )
    parser.add_argument(
        "prompt",
        help="Description of where/how to place the item (e.g., 'place the chair in the corner near the window')"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path for the generated image (optional)",
        default=None
    )
    parser.add_argument(
        "-m", "--model",
        help="Gemini model to use",
        default="nano-banana-pro-preview"
    )

    args = parser.parse_args()

    try:
        insert_item_into_scene(
            room_image_path=args.room_image,
            item_image_path=args.item_image,
            prompt=args.prompt,
            output_path=args.output,
            model=args.model
        )
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
