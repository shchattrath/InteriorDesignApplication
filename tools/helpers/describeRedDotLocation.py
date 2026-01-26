"""Convert red dot marker on layout to text description of location."""

import argparse
from pathlib import Path
from PIL import Image
from google import genai
from src.config import Config


def describe_red_dot_location(
    original_room_path: str,
    layout_with_dot_path: str,
    model: str = "gemini-2.0-flash-exp"
):
    """
    Analyze the red dot on a layout and describe its location in natural language.

    Args:
        original_room_path: Path to the original room photograph
        layout_with_dot_path: Path to the layout with red dot marker
        model: Gemini model to use for vision analysis

    Returns:
        Text description of where the red dot is located
    """
    # Validate inputs
    room_path = Path(original_room_path)
    layout_path = Path(layout_with_dot_path)

    if not room_path.exists():
        raise FileNotFoundError(f"Room image not found: {room_path}")
    if not layout_path.exists():
        raise FileNotFoundError(f"Layout image not found: {layout_path}")

    # Load images
    print(f"Loading original room: {room_path.name}")
    room_image = Image.open(room_path)

    print(f"Loading layout with marker: {layout_path.name}")
    layout_image = Image.open(layout_path)

    # Initialize Gemini client
    Config.validate_api_key("google")
    client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    # Create prompt for spatial analysis
    analysis_prompt = """You are an expert at spatial reasoning and interior design.

I have two images:
1. ORIGINAL ROOM PHOTOGRAPH: A photograph of an interior space (first image)
2. FLOOR PLAN WITH RED DOT: A top-down floor plan/layout of the same room with a RED DOT marking a specific location (second image)

Your task:
Analyze the RED DOT position on the floor plan (image 2) and describe EXACTLY where this location is in the actual room (image 1).

Provide a clear, detailed description of the location that includes:
- Position relative to walls (center, left side, right side, near back wall, near front, etc.)
- Position relative to major furniture or features visible in the room
- Distance from key landmarks (e.g., "2 feet from the couch", "next to the coffee table")
- Any other spatial context that would help precisely locate this spot

Format your response as a single, clear sentence or short paragraph describing the location.
Do NOT mention the red dot itself in your description - only describe the physical location in the room.

Example good responses:
- "In the center of the room, directly in front of the couch and about 3 feet from the coffee table"
- "In the left corner near the window, against the wall beside the bookshelf"
- "To the right of the dining table, about 2 feet from the wall"

Your location description:"""

    print("\nAnalyzing red dot location...")

    # Call Gemini with both images
    response = client.models.generate_content(
        model=model,
        contents=[analysis_prompt, room_image, layout_image]
    )

    # Extract the text description
    if not response.text:
        raise ValueError("No text description generated")

    location_description = response.text.strip()

    print(f"\n{'='*60}")
    print("LOCATION DESCRIPTION:")
    print('='*60)
    print(location_description)
    print('='*60)

    return location_description


def main():
    """Command-line interface for red dot location description."""
    parser = argparse.ArgumentParser(
        description="Describe the location of a red dot marker in natural language"
    )
    parser.add_argument(
        "original_room",
        help="Path to the original room photograph"
    )
    parser.add_argument(
        "layout_with_dot",
        help="Path to the layout/floor plan with red dot marker"
    )
    parser.add_argument(
        "-m", "--model",
        help="Gemini model to use for vision analysis",
        default="gemini-2.0-flash-exp"
    )

    args = parser.parse_args()

    try:
        location_desc = describe_red_dot_location(
            original_room_path=args.original_room,
            layout_with_dot_path=args.layout_with_dot,
            model=args.model
        )

        print(f"\nYou can now use this description with insertItem.py:")
        print(f'python insertItem.py <object_image> "{args.original_room}" "{location_desc}"')

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
