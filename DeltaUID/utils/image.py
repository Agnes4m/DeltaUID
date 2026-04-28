from pathlib import Path
from functools import lru_cache

from PIL import Image

TEXT_PATH = Path(__file__).parent / "texture2d"


@lru_cache(maxsize=1)
def get_footer():
    return Image.open(TEXT_PATH / "footer.png")


@lru_cache(maxsize=1)
def get_ICON():
    icon = Image.open(Path(__file__).parents[2] / "ICON.png")
    if icon.mode != "RGBA":
        icon = icon.convert("RGBA")
    return icon
