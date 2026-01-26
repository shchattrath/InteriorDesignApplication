"""Example: Insert a furniture item into a room scene."""

from pathlib import Path
from insertItem import insert_item_into_scene


def main():
    """Example of inserting an item into a scene."""

    # Paths to your images
    room_image = "data/input/MyRoomExample.png"
    item_image = "data/input/MyRoomExampleCircledObject.png"  # You'll need to add an item image

    # Description of where to place the item
    placement_prompt = "turn off the lamp circled in red"

    try:
        # Generate the composite
        result_path = insert_item_into_scene(
            room_image_path=room_image,
            item_image_path=item_image,
            prompt=placement_prompt
        )

        print(f"\n✓ Item successfully inserted!")
        print(f"  Result: {result_path}")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTo run this example:")
        print("1. Place your room image in data/input/")
        print("2. Place your furniture/item image in data/input/")
        print("3. Update the paths in this script")
        print("4. Run: python insertItemExample.py")
    except Exception as e:
        print(f"\nError during processing: {e}")


if __name__ == "__main__":
    main()
