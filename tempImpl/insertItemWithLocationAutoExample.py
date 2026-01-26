"""Example: Automatic item insertion using red dot (2-step process)."""

from insertItemWithLocationAuto import insert_item_auto


def main():
    """Example of automatic item insertion with location analysis."""

    # Object to insert
    object_image = "data/input/ExampleChair.png"

    # Layout with red dot showing where to place it
    layout_with_dot = "data/output/MyRoomExample_GeneratedFloorPlan_WithRedDot.png"

    # Original room photograph
    original_room = "data/input/MyRoomExample.png"

    # Optional additional instructions
    additional_instructions = "facing forward, modern style"

    try:
        result = insert_item_auto(
            object_image_path=object_image,
            layout_with_dot_path=layout_with_dot,
            original_room_path=original_room,
            additional_instructions=additional_instructions
        )

        print(f"\n✓ Success! Check the result at: {result}")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTo run this example:")
        print("1. Generate a floor plan: python singleImagePass.py")
        print("2. Add red dot: python addRedDotInteractive.py data/output/MyRoomExample_GeneratedFloorPlan.png")
        print("3. Run this script: python insertItemWithLocationAutoExample.py")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
