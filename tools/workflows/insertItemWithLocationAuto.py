"""Automatic item insertion using red dot location (2-step process)."""

import argparse
from pathlib import Path
from describeRedDotLocation import describe_red_dot_location
from insertItem import insert_item_into_scene


def insert_item_auto(
    object_image_path: str,
    layout_with_dot_path: str,
    original_room_path: str,
    additional_instructions: str = "",
    output_path: str = None
):
    """
    Automatically insert an item using red dot marker (2-step process).

    Step 1: Analyze red dot location and convert to text description
    Step 2: Use that description to place the object

    Args:
        object_image_path: Path to the object/furniture image
        layout_with_dot_path: Path to layout with red dot marker
        original_room_path: Path to the original room photograph
        additional_instructions: Optional extra instructions (orientation, style, etc.)
        output_path: Optional output path

    Returns:
        Path to the generated composite image
    """
    print("="*60)
    print("AUTOMATIC ITEM PLACEMENT WORKFLOW")
    print("="*60)
    print(f"\nObject: {object_image_path}")
    print(f"Layout: {layout_with_dot_path}")
    print(f"Room: {original_room_path}")
    if additional_instructions:
        print(f"Additional: {additional_instructions}")
    print("\n" + "="*60)

    # STEP 1: Convert red dot to location description
    print("\n[STEP 1] Analyzing red dot location...")
    print("="*60)

    location_description = describe_red_dot_location(
        original_room_path=original_room_path,
        layout_with_dot_path=layout_with_dot_path
    )

    # Combine location description with additional instructions
    if additional_instructions:
        full_prompt = f"{location_description}. {additional_instructions}"
    else:
        full_prompt = location_description

    # STEP 2: Insert the item using the text description
    print("\n\n[STEP 2] Inserting object at described location...")
    print("="*60)
    print(f"Placement prompt: {full_prompt}")
    print("="*60)

    result_path = insert_item_into_scene(
        room_image_path=original_room_path,
        item_image_path=object_image_path,
        prompt=full_prompt,
        output_path=output_path
    )

    print("\n" + "="*60)
    print("WORKFLOW COMPLETE!")
    print("="*60)
    print(f"Result: {result_path}")

    return result_path


def main():
    """Command-line interface for automatic item insertion."""
    parser = argparse.ArgumentParser(
        description="Automatically insert item using red dot (2-step: location analysis + placement)"
    )
    parser.add_argument(
        "object_image",
        help="Path to the object/furniture image"
    )
    parser.add_argument(
        "layout_with_dot",
        help="Path to layout/floor plan with red dot marker"
    )
    parser.add_argument(
        "original_room",
        help="Path to the original room photograph"
    )
    parser.add_argument(
        "-i", "--instructions",
        help="Additional instructions (e.g., 'facing forward, modern style')",
        default=""
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path for the generated image (optional)",
        default=None
    )

    args = parser.parse_args()

    try:
        insert_item_auto(
            object_image_path=args.object_image,
            layout_with_dot_path=args.layout_with_dot,
            original_room_path=args.original_room,
            additional_instructions=args.instructions,
            output_path=args.output
        )
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
