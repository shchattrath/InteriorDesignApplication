"""Setup script for quick project initialization."""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✓ .env file already exists")
        return

    if env_example.exists():
        print("Creating .env file from template...")
        env_example.read_text()
        with open(env_file, 'w') as f:
            f.write(env_example.read_text())
        print("✓ Created .env file")
        print("  → Please edit .env and add your API key(s)")
    else:
        print("✗ .env.example not found")


def check_directories():
    """Ensure required directories exist."""
    dirs = [
        "data/input",
        "data/output",
        "src",
        "src/pipeline",
        "src/api_clients",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print("✓ All directories verified")


def check_dependencies():
    """Check if required packages are installed."""
    required = [
        "PIL",
        "requests",
        "dotenv",
        "replicate",
        "tqdm",
        "numpy"
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("  → Run: pip install -r requirements.txt")
        return False
    else:
        print("✓ All dependencies installed")
        return True


def main():
    """Run setup checks."""
    print("=" * 60)
    print("Interior Design Image Editor - Setup")
    print("=" * 60)
    print()

    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Create necessary directories
    check_directories()

    # Create .env file
    create_env_file()

    # Check dependencies
    deps_ok = check_dependencies()

    print()
    print("=" * 60)

    if deps_ok:
        print("Setup Complete!")
        print()
        print("Next steps:")
        print("1. Edit .env and add your API key")
        print("2. Place images in data/input/")
        print("3. Run: python example_single.py")
    else:
        print("Setup Incomplete")
        print()
        print("Please install dependencies:")
        print("  pip install -r requirements.txt")

    print("=" * 60)


if __name__ == "__main__":
    main()
