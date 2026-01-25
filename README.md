# Interior Design Image Editing Application

Proper Documentation for this project will be released when full implementation is completed.

This is a personal passion project I'm creating to help me prototype changes that I make to my interior spaces. I often find that interacting with the regular Gemini interface can be quite frustrating at times, especially when I want to add SLIGHT adjustments to my space (ie. a new lamp, a different shade color, etc.). This app will allow for a form of "visual prompting" which allows close-hands control of how the scene changes.

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