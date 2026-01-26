"""Insert an item into a scene using a layout with a red dot placement marker."""

import argparse
from pathlib import Path
from PIL import Image
from google import genai
from src.config import Config


def insert_item_with_location(
    object_image_path: str,
    layout_with_marker_path: str,
    original_room_path: str,
    text_prompt: str,
    output_path: str = None,
    model: str = "nano-banana-pro-preview"
):
    """
    Insert an object into a room using a layout with red dot placement marker.

    Args:
        object_image_path: Path to the object/furniture image
        layout_with_marker_path: Path to layout image with red dot showing placement
        original_room_path: Path to the original room photograph
        text_prompt: Additional text instructions (orientation, style, etc.)
        output_path: Optional output path (defaults to data/output/)
        model: Gemini model to use

    Returns:
        Path to the generated image
    """
    # Validate inputs
    object_path = Path(object_image_path)
    layout_path = Path(layout_with_marker_path)
    room_path = Path(original_room_path)

    if not object_path.exists():
        raise FileNotFoundError(f"Object image not found: {object_path}")
    if not layout_path.exists():
        raise FileNotFoundError(f"Layout image not found: {layout_path}")
    if not room_path.exists():
        raise FileNotFoundError(f"Room image not found: {room_path}")

    # Load images
    print(f"Loading object image: {object_path.name}")
    object_image = Image.open(object_path)

    print(f"Loading layout with marker: {layout_path.name}")
    layout_image = Image.open(layout_path)

    print(f"Loading original room: {room_path.name}")
    room_image = Image.open(room_path)

    # Initialize Gemini client
    Config.validate_api_key("google")
    client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    # Create a detailed prompt for spatial-aware composition
    full_prompt = f"""You are an expert interior designer and image compositor with spatial reasoning capabilities.

I have three images for you:
1. OBJECT IMAGE: The furniture/decor item to be placed (first image)
2. LAYOUT IMAGE: A floor plan/layout view with a RED DOT indicating exactly where to place the object (second image)
3. ROOM PHOTOGRAPH: The original room photograph (third image)

Your task:
- Study the RED DOT location on the layout image (image 2) to understand the spatial placement
- Map this location from the floor plan to the corresponding position in the room photograph (image 3)
- Place the object (image 1) at that exact location in the room photograph
- Apply the following additional instructions: {text_prompt}

Requirements:
- Use the red dot marker as your PRIMARY spatial guide for placement
- Translate the floor plan position to the correct perspective in the photograph
- Maintain realistic lighting that matches the room
- Ensure proper perspective, scale, and depth
- Create natural shadows and reflections
- Blend the object seamlessly into the scene
- Preserve the room's existing style and atmosphere

Generate a photorealistic composite showing the object placed at the location indicated by the red dot."""

    print(f"\nGenerating composite with spatial placement...")
    print(f"Additional instructions: {text_prompt}")

    # Call Gemini with all three images in order
    response = client.models.generate_content(
        model=model,
        contents=[full_prompt, object_image, layout_image, room_image]
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
        object_stem = object_path.stem
        output_file = Config.OUTPUT_DIR / f"{room_stem}_with_{object_stem}_placed.jpg"

    # Save the generated image
    with open(output_file, 'wb') as f:
        f.write(image_part.inline_data.data)

    print(f"\nSuccess! Composite image saved to: {output_file}")
    return output_file


def main():
    """Command-line interface for location-based item insertion."""
    parser = argparse.ArgumentParser(
        description="Insert an item using layout with red dot placement marker"
    )
    parser.add_argument(
        "object_image",
        help="Path to the object/furniture image"
    )
    parser.add_argument(
        "layout_with_marker",
        help="Path to layout/floor plan image with red dot marker"
    )
    parser.add_argument(
        "room_image",
        help="Path to the original room photograph"
    )
    parser.add_argument(
        "text_prompt",
        help="Additional instructions (e.g., 'facing forward, modern style')"
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
        insert_item_with_location(
            object_image_path=args.object_image,
            layout_with_marker_path=args.layout_with_marker,
            original_room_path=args.room_image,
            text_prompt=args.text_prompt,
            output_path=args.output,
            model=args.model
        )
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
