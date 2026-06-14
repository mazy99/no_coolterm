

from pathlib import Path


def load_stylesheet(filename: str) -> str:

    try:
        style_path = Path(filename)
        with open(style_path, "r") as file:
            return file.read()

    except Exception as e:
        print(f"Error loading stylesheet: {e}")

