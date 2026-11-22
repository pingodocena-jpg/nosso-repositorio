"""Build the TikTok videos in tiktok/*.json with MoneyPrinterTurbo + stock footage.

Usage: python build_tiktok.py MPT_DIR OUT_DIR [slug ...]
Needs pexels_api_keys (and/or pixabay_api_keys) set in MPT_DIR/config.toml.
Env: VIDEO_SOURCE=pexels|pixabay (default pexels).
Tip: in MPT_DIR/app/services/material.py set Pixabay "video_type" to "film" to skip
cartoon/animation results.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    mpt, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    only = set(sys.argv[3:])
    out.mkdir(parents=True, exist_ok=True)
    source = os.environ.get("VIDEO_SOURCE", "pexels")
    for spec_path in sorted((ROOT / "tiktok").glob("*.json")):
        spec = json.loads(spec_path.read_text())
        slug = spec["slug"]
        if only and slug not in only:
            continue
        cmd = [
            sys.executable, str(HERE / "run_mpt.py"), str(mpt),
            "--video-subject", spec["title"],
            "--video-script", spec["script"],
            "--video-terms", ",".join(spec["terms"]),
            "--match-materials-to-script",
            "--video-language", "pt-BR",
            "--video-source", source,
            "--video-concat-mode", "sequential",
            "--video-aspect", "9:16",
            "--video-clip-duration", "3",
            "--video-transition-mode", "fade-in",
            "--voice-name", "pt-BR-AntonioNeural-Male",
            "--voice-rate", "1.15",
            "--bgm-type", "random",
            "--bgm-volume", "0.12",
            "--font-name", "BeVietnamPro-Bold.ttf",
            "--font-size", "88",
            "--subtitle-position", "custom",
            "--custom-position", "72",
            "--subtitle-display-mode", "word_by_word",
            "--subtitle-animation", "pop_spring",
            "--text-fore-color", "#FFE14D",
            "--stroke-color", "#000000",
            "--stroke-width", "3",
            "--n-threads", "4",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        if r.returncode != 0 or not last.startswith("{"):
            print(r.stderr[-2500:])
            print(f"[{slug}] FAILED", flush=True)
            continue
        video = json.loads(last)["result"]["videos"][0]
        shutil.copy(video, out / f"{slug}.mp4")
        print(f"[{slug}] ok", flush=True)


if __name__ == "__main__":
    main()
