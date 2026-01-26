"""Interactive tool to add a red dot marker by clicking on a layout image."""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def add_red_dot_interactive(
    layout_image_path: str,
    output_path: str = None,
    dot_size: int = 20
):
    """
    Interactively add a red dot marker by clicking on the layout image.

    Args:
        layout_image_path: Path to the layout/floor plan image
        output_path: Optional output path (defaults to *_WithRedDot.png)
        dot_size: Diameter of the red dot in pixels

    Returns:
        Path to the marked image
    """
    # Load the image
    layout_path = Path(layout_image_path)
    if not layout_path.exists():
        raise FileNotFoundError(f"Layout image not found: {layout_path}")

    print(f"Loading layout: {layout_path.name}")
    image = Image.open(layout_path).convert("RGB")
    width, height = image.size

    print("\nInstructions:")
    print("- Click on the image where you want to place the red dot")
    print("- Close the window when done")
    print("- The coordinates will be used to create the marked image")

    # Store the clicked coordinates
    clicked_coords = []

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            clicked_coords.append((x, y))
            print(f"\nClicked at: ({x}, {y})")

            # Add a visual marker
            circle = patches.Circle(
                (x, y), dot_size/2,
                color='red',
                fill=True,
                alpha=0.7
            )
            ax.add_patch(circle)
            plt.draw()

    # Display the image
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image)
    ax.set_title('Click where you want to place the object\n(Close window when done)')
    ax.axis('off')

    # Connect the click event
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.tight_layout()
    plt.show()

    if not clicked_coords:
        print("\nNo location selected. Exiting.")
        return None

    # Use the last clicked coordinate
    x, y = clicked_coords[-1]
    print(f"\nUsing coordinates: ({x}, {y})")

    # Create a new image with the red dot
    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)
    radius = dot_size // 2

    # Draw a filled red circle
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill='red',
        outline='darkred',
        width=2
    )

    # Determine output path
    if output_path:
        output_file = Path(output_path)
    else:
        stem = layout_path.stem
        suffix = layout_path.suffix
        output_file = layout_path.parent / f"{stem}_WithRedDot{suffix}"

    # Save the marked image
    image_copy.save(output_file)

    print(f"\nSuccess! Red dot added at ({x}, {y})")
    print(f"Saved to: {output_file}")

    return output_file


def main():
    """Command-line interface for interactive red dot placement."""
    parser = argparse.ArgumentParser(
        description="Interactively add a red dot marker to a layout image"
    )
    parser.add_argument(
        "layout_image",
        help="Path to the layout/floor plan image"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path for the marked image (optional)",
        default=None
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        help="Diameter of the red dot in pixels (default: 20)",
        default=20
    )

    args = parser.parse_args()

    try:
        add_red_dot_interactive(
            layout_image_path=args.layout_image,
            output_path=args.output,
            dot_size=args.size
        )
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
