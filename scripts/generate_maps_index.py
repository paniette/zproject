"""
Script to generate a static maps index JSON file
This allows the frontend to work without the Python API server
"""
import base64
import json
import re
import shutil
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import app_config  # noqa: E402

app_config.ensure_data_directories()

from editor.map_manager import MapManager  # noqa: E402

try:
    from PIL import Image
except ImportError:
    Image = None

THUMB_MAX_SIZE = (320, 240)
DATA_URL_RE = re.compile(
    r"^data:image/(?:png|jpeg|jpg|webp);base64,(.+)$",
    re.IGNORECASE | re.DOTALL,
)


def write_map_thumbnail(map_id, data_url, thumbs_dir: Path):
    """
    Decode mission.mapImageDataUrl and write maps/thumbs/<map_id>.png.
    Returns relative URL for maps-index (e.g. maps/thumbs/map_abc.png).
    """
    if not data_url or not isinstance(data_url, str):
        return None
    if Image is None:
        print("  Pillow not installed — thumbnails skipped")
        return None

    match = DATA_URL_RE.match(data_url.strip())
    if not match:
        return None

    try:
        raw = base64.b64decode(match.group(1), validate=False)
        img = Image.open(BytesIO(raw))
        img.thumbnail(THUMB_MAX_SIZE, Image.Resampling.LANCZOS)
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            alpha = img.split()[-1] if img.mode == "RGBA" else None
            background.paste(img, mask=alpha)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        thumbs_dir.mkdir(parents=True, exist_ok=True)
        out_path = thumbs_dir / f"{map_id}.png"
        img.save(out_path, "PNG", optimize=True)
        return f"maps/thumbs/{map_id}.png"
    except Exception as e:
        print(f"  Thumbnail failed for {map_id}: {e}")
        return None


def generate_maps_index():
    """Generate maps-index.json, copy map JSON files, and optional PNG thumbnails."""

    print("Indexing maps...")

    all_maps = MapManager.list_all_public_maps()
    print(f"Found {len(all_maps)} maps")

    public_root = Path(__file__).parent.parent / "frontend" / "public"
    maps_public_dir = public_root / "maps"
    thumbs_dir = maps_public_dir / "thumbs"
    maps_public_dir.mkdir(parents=True, exist_ok=True)
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    index = {
        "maps": [],
        "generated_at": datetime.now().isoformat(),
    }

    thumb_count = 0

    for map_data in all_maps:
        map_id = map_data.get("id")
        mission = map_data.get("mission") or {}
        data_url = mission.get("mapImageDataUrl")

        map_entry = {
            "id": map_id,
            "name": map_data.get("name", "Untitled"),
            "metadata": map_data.get("metadata", {}),
        }

        thumb_url = write_map_thumbnail(map_id, data_url, thumbs_dir)
        if thumb_url:
            map_entry["thumbUrl"] = thumb_url
            thumb_count += 1

        index["maps"].append(map_entry)

    output_path = public_root / "maps-index.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Index generated successfully: {output_path}")
    print(f"Total maps: {len(index['maps'])}")
    print(f"Thumbnails written: {thumb_count} -> {thumbs_dir}")

    print("\nCopying map files to public directory...")
    users_dir = Path(app_config.USERS_DIR)
    copied_count = 0

    if users_dir.exists():
        for user_dir in users_dir.iterdir():
            if not user_dir.is_dir():
                continue
            maps_dir = user_dir / "maps"
            if not maps_dir.exists():
                continue
            for map_file in maps_dir.glob("*.json"):
                try:
                    dest_file = maps_public_dir / map_file.name
                    shutil.copy2(map_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    print(f"Error copying map file {map_file}: {e}")

    print(f"Copied {copied_count} map files to {maps_public_dir}")

    return output_path


if __name__ == "__main__":
    try:
        generate_maps_index()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
