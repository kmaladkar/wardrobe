"""Virtual try-on: local open-source model via script/command, or placeholder (avatar)."""

import os
import subprocess
import tempfile
import uuid
from pathlib import Path

from wardrobe.data.database import get_connection


def _run_local_command(
    human_path: Path, garment_path: Path, output_path: Path, category: str = "top"
) -> bool:
    """
    Run local try-on. Returns True if output_path was written successfully.
    Uses TRY_ON_COMMAND (shell) or TRY_ON_SCRIPT (python script). Passes category for placement.
    """
    cmd_env = os.environ.get("TRY_ON_COMMAND", "").strip()
    script = os.environ.get("TRY_ON_SCRIPT", "").strip()

    if cmd_env:
        cmd = (
            cmd_env.replace("{human}", str(human_path))
            .replace("{garment}", str(garment_path))
            .replace("{output}", str(output_path))
            .replace("{category}", category)
        )
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=Path.cwd(),
            )
            if result.returncode == 0 and output_path.is_file():
                return True
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        return False

    if script:
        script_path = Path(script).resolve()
        if not script_path.is_file():
            return False
        try:
            result = subprocess.run(
                [
                    "python",
                    str(script_path),
                    "--human",
                    str(human_path),
                    "--garment",
                    str(garment_path),
                    "--output",
                    str(output_path),
                    "--category",
                    category,
                ],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=Path.cwd(),
            )
            if result.returncode == 0 and output_path.is_file():
                return True
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        return False

    return False


def run_try_on(
    avatar_image_id: str,
    garment_image_id: str,
    user_id: str,
    category: str = "top",
) -> str | None:
    """
    Run virtual try-on: avatar + one garment (upper body).
    Uses local TRY_ON_SCRIPT or TRY_ON_COMMAND if set; otherwise returns avatar as placeholder.
    Saves result to images table and returns new image id.
    """
    conn = get_connection()
    try:
        avatar = conn.execute(
            "SELECT data, content_type FROM images WHERE id = ?", (avatar_image_id,)
        ).fetchone()
        garment = conn.execute(
            "SELECT data, content_type FROM images WHERE id = ?", (garment_image_id,)
        ).fetchone()
        if not avatar or not garment:
            return None
        avatar_bytes = bytes(avatar["data"])
        garment_bytes = bytes(garment["data"])
    finally:
        conn.close()

    result_bytes: bytes | None = None
    with tempfile.TemporaryDirectory() as tmp:
        human_path = Path(tmp) / "human.jpg"
        garm_path = Path(tmp) / "garm.jpg"
        out_path = Path(tmp) / "result.jpg"
        human_path.write_bytes(avatar_bytes)
        garm_path.write_bytes(garment_bytes)
        if _run_local_command(human_path, garm_path, out_path, category):
            result_bytes = out_path.read_bytes()

    if result_bytes is None:
        result_bytes = avatar_bytes

    result_image_id = f"img-{uuid.uuid4().hex[:12]}"
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO images (id, user_id, data, filename, content_type, kind)
               VALUES (?, ?, ?, ?, ?, 'wardrobe')""",
            (result_image_id, user_id, result_bytes, "try-on-result.jpg", "image/jpeg"),
        )
        conn.commit()
        return result_image_id
    finally:
        conn.close()
