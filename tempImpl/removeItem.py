"""Remove a furniture item from a room scene using Gemini API."""

import argparse
from pathlib import Path
from PIL import Image
from google import genai
from src.config import Config


def remove_item_from_scene(
    room_image_path: str,
    location_description: str,
    output_path: str = None,
    model: str = "nano-banana-pro-preview"
):
    """
    Remove a furniture item at the described location from a room scene.

    Args:
        room_image_path: Path to the room/scene image
        location_description: Description of where the item to remove is located
            (as produced by describe_red_dot_location)
        output_path: Optional output path (defaults to data/output/)
        model: Gemini model to use

    Returns:
        Path to the generated image with the item removed
    """
    room_path = Path(room_image_path)

    if not room_path.exists():
        raise FileNotFoundError(f"Room image not found: {room_path}")

    print(f"Loading room image: {room_path.name}")
    room_image = Image.open(room_path)

    Config.validate_api_key("google")
    client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    full_prompt = f"""You are an expert interior designer and photo editor.

I have a photograph of a room (the image provided).

Your task: Remove the furniture or object located at the following position and fill the space naturally.

Location of the item to remove: {location_description}

Requirements:
- Completely remove the item at the described location
- Fill the vacated area with what would realistically be behind it (floor, wall, baseboard, etc.)
- Match the lighting, texture, and perspective of the surrounding area
- The result should look like the item was never there
- Do NOT add any new furniture or objects — only remove
- Preserve everything else in the room exactly as it is

Generate a photorealistic image of the room with that item cleanly removed."""

    print(f"\nRemoving item at: {location_description}")

    response = client.models.generate_content(
        model=model,
        contents=[full_prompt, room_image]
    )

    if not response.parts or len(response.parts) == 0:
        raise ValueError("No image generated in response")

    image_part = response.parts[0]
    if not hasattr(image_part, 'inline_data') or not image_part.inline_data:
        raise ValueError("No image data in response")

    if output_path:
        output_file = Path(output_path)
    else:
        Config.ensure_directories()
        output_file = Config.OUTPUT_DIR / f"{room_path.stem}_item_removed.jpg"

    with open(output_file, 'wb') as f:
        f.write(image_part.inline_data.data)

    print(f"\nSuccess! Image saved to: {output_file}")
    return output_file


def main():
    """Command-line interface for item removal."""
    parser = argparse.ArgumentParser(
        description="Remove a furniture item from a room scene"
    )
    parser.add_argument(
        "room_image",
        help="Path to the room/scene image"
    )
    parser.add_argument(
        "location",
        help="Description of where the item to remove is located"
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
        remove_item_from_scene(
            room_image_path=args.room_image,
            location_description=args.location,
            output_path=args.output,
            model=args.model
        )
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
