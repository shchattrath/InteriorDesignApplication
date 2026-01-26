# Temporary Implementation Files

This folder contains example scripts and alternative implementations that were used during development. These are kept for reference but are not part of the main application workflow.

## Files

### Core Implementation Files

- **`insertItem.py`** - Basic 2-image item insertion (room + item)
  - Takes room image and item image
  - Uses text prompt for placement
  - Simpler than the red dot workflow

- **`insertItemWithLocation.py`** - 3-image insertion with red dot (direct approach)
  - Takes object, layout with red dot, and room
  - Passes red dot image directly to model (less reliable)
  - Replaced by the 2-step workflow in `tools/workflows/insertItemWithLocationAuto.py`

### Example Scripts

- **`insertItemExample.py`** - Example usage of `insertItem.py`
- **`insertItemWithLocationExample.py`** - Example usage of `insertItemWithLocation.py`
- **`insertItemWithLocationAutoExample.py`** - Example usage of automatic 2-step workflow

## Notes

- These files are working implementations but are being phased out
- The main application will use the tools in `tools/workflows/` and `tools/helpers/`
- Keep these for reference during development
- Can be deleted once the main application is complete
