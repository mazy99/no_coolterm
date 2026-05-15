

from pathlib import Path


def load_stylesheet(filename="styles.qss"):

    try:
        style_path = Path(__file__).parent.parent / "gui" / "main_window" / filename

        if style_path.exists():
            with open(style_path, "r") as f:
                return f.read()

    except Exception as e:
        print(f"Error loading stylesheet: {e}")


