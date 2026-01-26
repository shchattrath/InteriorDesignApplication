# Tools Directory

This directory contains the main workflow and helper tools for the Interior Design Application.

## Workflows (`workflows/`)

Main end-to-end workflows for image editing:

- **`singleImagePass.py`** - Generate floor plan layout from room photo
  ```bash
  python tools/workflows/singleImagePass.py
  ```

- **`insertItemWithLocationAuto.py`** - Automatic 2-step item insertion workflow
  - Step 1: Converts red dot location to text description
  - Step 2: Inserts item at described location
  ```bash
  python tools/workflows/insertItemWithLocationAuto.py <object> <layout_with_dot> <room> -i "instructions"
  ```

## Helpers (`helpers/`)

Utility tools that support the main workflows:

- **`describeRedDotLocation.py`** - Analyze red dot and describe location in text
  ```bash
  python tools/helpers/describeRedDotLocation.py <room_image> <layout_with_dot>
  ```

- **`addRedDotInteractive.py`** - Interactively add red dot by clicking on layout
  ```bash
  python tools/helpers/addRedDotInteractive.py <layout_image>
  ```

- **`addRedDotToLayout.py`** - Add red dot using coordinates
  ```bash
  python tools/helpers/addRedDotToLayout.py <layout_image> <x> <y>
  ```

## Complete Workflow Example

```bash
# 1. Generate floor plan from room photo
python tools/workflows/singleImagePass.py

# 2. Add red dot marker to floor plan (interactive)
python tools/helpers/addRedDotInteractive.py data/output/MyRoomExample_GeneratedFloorPlan.png

# 3. Insert item at marked location
python tools/workflows/insertItemWithLocationAuto.py \
    data/input/ExampleChair.png \
    data/output/MyRoomExample_GeneratedFloorPlan_WithRedDot.png \
    data/input/MyRoomExample.png \
    -i "facing forward, modern style"
```
