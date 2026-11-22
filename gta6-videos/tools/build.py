"""Build every video in roteiros/ with MoneyPrinterTurbo.

Usage: python build.py MPT_DIR WORK_DIR [slug ...]
For each roteiros/*.json: render cards -> time each card to its narration
(Edge TTS word boundaries) and render it as its own clip -> run the
MoneyPrinterTurbo CLI (local materials, pt-BR voice, subtitles, BGM) -> copy the
final MP4 to WORK_DIR/out/<slug>.mp4.
"""
import asyncio
import json
import math
import os
import re
import shutil
import ssl
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VOICE = "pt-BR-AntonioNeural"
RATE = 1.1
FPS = 30
SUB_MODE = os.environ.get("SUB_MODE", "word_by_word")


def norm(w):
    return re.sub(r"[^\wÀ-ÿ]", "", w.lower())


def card_timings(says, out):
    """Synthesize the narration once and return (start time of each card, total)."""
    import edge_tts
    import edge_tts.communicate as c

    c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    words = []

    async def go():
        com = edge_tts.Communicate(
            " ".join(says), VOICE, rate=f"+{round((RATE - 1) * 100)}%",
            boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY"),
        )
        with open(out, "wb") as f:
            async for m in com.stream():
                if m["type"] == "audio":
                    f.write(m["data"])
                elif m["type"] == "WordBoundary":
                    words.append((m["offset"] / 1e7, norm(m["text"])))

    asyncio.run(go())
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True, check=True,
    )
    total = float(r.stdout.strip())
    toks = [w for _, w in words]
    starts, j = [0.0], 0
    for say in says[1:]:
        words_say = [h for h in (norm(w) for w in say.split()[:3]) if h]
        # first place after the previous card where the card's opening words occur in
        # order; fall back to fewer words when TTS tokenizes them differently ("GTA 5")
        for k in range(len(words_say), 0, -1):
            head, i = words_say[:k], j
            while i < len(toks) and toks[i:i + k] != head:
                i += 1
            if i < len(toks):
                break
        else:
            raise SystemExit(f"could not align card starting with {' '.join(words_say)!r}")
        starts.append(max(words[i][0] - 0.15, starts[-1] + 1))
        j = i + k
    return starts, total


def render_card_clip(img, seconds, out):
    frames = max(1, round(seconds * FPS))
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(img),
        "-vf", (f"scale=2160:3840,zoompan=z='1+0.035*on/{frames}':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={FPS},"
                "format=yuv420p"),
        "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        str(out),
    ], check=True)


def main():
    mpt, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    only = set(sys.argv[3:])
    (work / "out").mkdir(parents=True, exist_ok=True)
    for spec_path in sorted((ROOT / "roteiros").glob("*.json")):
        spec = json.loads(spec_path.read_text())
        slug = spec["slug"]
        if only and slug not in only:
            continue
        cards_dir = work / "cards" / slug
        imgs = subprocess.run(
            [sys.executable, str(HERE / "make_cards.py"), str(spec_path), str(cards_dir)],
            capture_output=True, text=True, check=True,
        ).stdout.strip().split(",")
        says = [c["say"] for c in spec["cards"]]
        script = " ".join(says)
        starts, total = card_timings(says, work / f"{slug}-probe.mp3")
        ends = starts[1:] + [total + 1.0]
        clips = []
        for img, a, b in zip(imgs, starts, ends):
            out = Path(img).with_suffix(".mp4")
            render_card_clip(img, b - a, out)
            clips.append(str(out))
        mats = ",".join(clips)
        clip = math.ceil(max(b - a for a, b in zip(starts, ends))) + 1
        print(f"[{slug}] narration {total:.1f}s, cards at " + ", ".join(f"{x:.1f}" for x in starts), flush=True)
        cmd = [
            sys.executable, str(HERE / "run_mpt.py"), str(mpt),
            "--video-subject", spec["title"],
            "--video-script", script,
            "--video-terms", "GTA 6",
            "--video-language", "pt-BR",
            "--video-source", "local",
            "--video-materials", mats,
            "--video-concat-mode", "sequential",
            "--video-aspect", "9:16",
            "--video-clip-duration", str(clip),
            "--voice-name", f"{VOICE}-Male",
            "--voice-rate", str(RATE),
            "--bgm-type", "random",
            "--bgm-volume", "0.15",
            "--font-name", "BeVietnamPro-Bold.ttf",
            "--font-size", "62",
            "--subtitle-position", "custom",
            "--custom-position", "86",
            "--subtitle-background-enabled",
            "--subtitle-background-color", "#120624",
            "--rounded-subtitle-background",
            "--subtitle-display-mode", SUB_MODE,
            "--subtitle-animation", "pop_spring" if SUB_MODE == "word_by_word" else "none",
            "--n-threads", "4",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        if r.returncode != 0 or not last.startswith("{"):
            print(r.stderr[-3000:])
            raise SystemExit(f"[{slug}] MoneyPrinterTurbo failed")
        video = json.loads(last)["result"]["videos"][0]
        dest = work / "out" / f"{slug}.mp4"
        shutil.copy(video, dest)
        print(f"[{slug}] -> {dest}", flush=True)


if __name__ == "__main__":
    main()
