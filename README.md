# Interior Design Image Editing Application

Proper Documentation for this project will be released when full implementation is completed.

This is a personal passion project I'm creating to help me prototype changes that I make to my interior spaces. I often find that interacting with the regular Gemini interface can be quite frustrating at times, especially when I want to add SLIGHT adjustments to my space (ie. a new lamp, a different shade color, etc.). This app will allow for a form of "visual prompting" which allows close-hands control of how the scene changes.

## Approach

The idea I have in mind is to explore the idea of "visual prompting" I mentioned earlier. This is inspired by a work a PhD I've worked under did recently:

**GenEscape: Hierarchical Multi-Agent Generation of Escape Room Puzzles**
Mengyi Shan, Brian Curless, Ira Kemelmacher-Shlizerman, Steve Seitz
[arXiv:2506.21839](https://www.arxiv.org/abs/2506.21839)

What I want to do is use the layout sketch as a base for the user, through an interactive window, to add "prompt" objects, containing the image of the base furniture piece, the orientation of the piece, and descriptions of it's state. They can then directly control WHERE to place the object by dragging a pointer across the layout window to where they'd like the object to lie. 

The hope is that this delivers an easy to control method for prototyping small changes to an interior space.

| Original Image | Generated Floor Plan |
|----------------|----------------------|
| ![Original Room](data/input/MyRoomExample.png) | ![Generated Floor Plan](data/output/MyRoomExample_GeneratedFloorPlan.png) |

*Prompt: "room layout, floor plan, interior layout, top-down, black white"*

### Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure API Keys

Copy the example environment file and add your API keys. Currently I'm buildingt the project around the Google AI studio API services:

```bash
cp .env.example .env
```
```