"""Example: Insert an item using layout with red dot placement marker."""

from pathlib import Path
from insertItemWithLocation import insert_item_with_location


def main():
    """Example of inserting an item using spatial layout marker."""

    # Path to the object/furniture you want to place
    object_image = "data/input/ExampleChair.png"

    # Path to the floor plan/layout with a RED DOT showing where to place it
    layout_with_marker = "data/input/MyRoomExample_GeneratedFloorPlan_WithRedDot.png"

    # Path to the original room photograph
    original_room = "data/input/MyRoomExample.png"

    # Additional text instructions for the placement
    text_instructions = "Place the chair facing forward, modern style"

    try:
        print("=" * 60)
        print("SPATIAL PLACEMENT WORKFLOW")
        print("=" * 60)
        print(f"\nObject: {object_image}")
        print(f"Layout guide: {layout_with_marker}")
        print(f"Target room: {original_room}")
        print(f"Instructions: {text_instructions}")
        print("\n" + "=" * 60)

        # Generate the composite
        result_path = insert_item_with_location(
            object_image_path=object_image,
            layout_with_marker_path=layout_with_marker,
            original_room_path=original_room,
            text_prompt=text_instructions
        )

        print("\n" + "=" * 60)
        print("COMPLETE!")
        print("=" * 60)
        print(f"\nResult saved to: {result_path}")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTo run this example:")
        print("1. Place your object image in data/input/")
        print("2. Generate a floor plan of your room")
        print("3. Add a RED DOT to the floor plan where you want the object")
        print("4. Save it as a new file (e.g., *_WithRedDot.png)")
        print("5. Update the paths in this script")
        print("6. Run: python insertItemWithLocationExample.py")
    except Exception as e:
        print(f"\nError during processing: {e}")


if __name__ == "__main__":
    main()
