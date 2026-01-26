"""Helper tool to add a red dot marker to a layout image."""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw


def add_red_dot(
    layout_image_path: str,
    x: int,
    y: int,
    output_path: str = None,
    dot_size: int = 20
):
    """
    Add a red dot marker to a layout image at specified coordinates.

    Args:
        layout_image_path: Path to the layout/floor plan image
        x: X coordinate for the red dot (pixels from left)
        y: Y coordinate for the red dot (pixels from top)
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

    # Validate coordinates
    if x < 0 or x >= width or y < 0 or y >= height:
        raise ValueError(
            f"Coordinates ({x}, {y}) are out of bounds. "
            f"Image size is {width}x{height}"
        )

    # Draw the red dot
    draw = ImageDraw.Draw(image)
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
    image.save(output_file)

    print(f"Red dot added at coordinates ({x}, {y})")
    print(f"Saved to: {output_file}")

    return output_file


def main():
    """Command-line interface for adding red dot markers."""
    parser = argparse.ArgumentParser(
        description="Add a red dot marker to a layout image for spatial placement"
    )
    parser.add_argument(
        "layout_image",
        help="Path to the layout/floor plan image"
    )
    parser.add_argument(
        "x",
        type=int,
        help="X coordinate for the red dot (pixels from left)"
    )
    parser.add_argument(
        "y",
        type=int,
        help="Y coordinate for the red dot (pixels from top)"
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
        add_red_dot(
            layout_image_path=args.layout_image,
            x=args.x,
            y=args.y,
            output_path=args.output,
            dot_size=args.size
        )
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
