"""Convert red dot marker on layout to text description of location."""

import argparse
from pathlib import Path
from PIL import Image
from google import genai
from src.config import Config


def describe_red_dot_location(
    original_room_path: str,
    layout_with_dot_path: str,
    model: str = "gemini-2.0-flash"
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
Analyze the RED DOT position on the floor plan (image 2) and describe EXACTLY where that spot appears **as seen in the photograph** (image 1).

IMPORTANT — describe the location relative to the camera's frame of the photograph:
- Use directional terms as they appear in the photo: "left side of the frame", "right side of the frame", "centre of the image", "foreground", "background", etc.
- Reference visible furniture or features by their position in the photo (e.g., "just to the left of the couch visible in the centre of the frame").
- Give a sense of depth: is the spot in the foreground (close to the camera), mid-ground, or background (far wall)?
- If near a wall or surface, say which wall as it appears in the photo (e.g., "against the back wall", "along the right-hand wall").

Do NOT use abstract compass directions (north/south/east/west).
Do NOT mention the red dot, the floor plan, or the layout — only describe the physical location as seen in the room photograph.

Format your response as a single, clear sentence or short paragraph.

Example good responses:
- "In the foreground, slightly left of centre, on the open floor between the camera and the sofa"
- "Against the back wall on the right side of the frame, between the bookshelf and the window"
- "In the mid-ground on the left side of the frame, next to the armchair"

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
        default="gemini-2.0-flash"
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
