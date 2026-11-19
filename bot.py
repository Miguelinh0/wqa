"""Bot que mira un directo, lee codigos con OCR y te los manda al celular (ntfy).

Uso:
    python bot.py URL_DEL_DIRECTO --topic MI_TEMA
"""
import argparse
import re
import subprocess
import sys
import time

import numpy as np
import requests
import streamlink
from rapidocr_onnxruntime import RapidOCR

# Formato del directo: "CODIGO: F355-HPQJ-B5B8" (guiones obligatorios)
DEFAULT_REGEX = r"([A-Z0-9]{4})\s*-\s*([A-Z0-9]{4})\s*-\s*([A-Z0-9]{4})"
W, H = 1280, 720


def send(topic, msg, title="Bot", prio="default"):
    print(f"[ntfy] {title}: {msg}", flush=True)
    try:
        requests.post(f"https://ntfy.sh/{topic}", data=msg.encode(),
                      headers={"Title": title, "Priority": prio}, timeout=5)
    except Exception as e:
        print("Error ntfy:", e, flush=True)


def get_stream_url(page_url):
    streams = streamlink.streams(page_url)
    if not streams:
        raise RuntimeError("no hay stream (¿esta en vivo?)")
    for q in ("720p", "720p60", "best"):
        if q in streams:
            return streams[q].url
    return next(iter(streams.values())).url


def frames(page_url, fps):
    """streamlink (baja latencia) -> ffmpeg sin buffer -> frames."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = "ffmpeg"
    sl = subprocess.Popen(
        [sys.executable, "-m", "streamlink", "--twitch-low-latency", "--twitch-disable-ads",
         "--hls-live-edge", "1", "--stream-segment-threads", "2",
         "--stdout", page_url, "720p60,720p,best"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    ff = subprocess.Popen(
        [exe, "-loglevel", "error", "-fflags", "nobuffer", "-flags", "low_delay",
         "-probesize", "500000", "-analyzeduration", "0", "-i", "-",
         "-vf", f"fps={fps},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
        stdin=sl.stdout, stdout=subprocess.PIPE)
    size = W * H * 3
    import threading
    latest = {"f": None, "id": 0, "end": False}
    cond = threading.Condition()

    def reader():
        while True:
            buf = ff.stdout.read(size)
            with cond:
                if len(buf) < size:
                    latest["end"] = True
                    cond.notify()
                    return
                latest["f"] = buf  # se queda solo con la mas nueva
                latest["id"] += 1
                cond.notify()

    threading.Thread(target=reader, daemon=True).start()
    seen_id = 0
    try:
        while True:
            with cond:
                while latest["id"] == seen_id and not latest["end"]:
                    cond.wait()
                if latest["end"]:
                    return
                seen_id, buf = latest["id"], latest["f"]
            yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    finally:
        ff.kill()
        sl.kill()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--regex", default=DEFAULT_REGEX)
    ap.add_argument("--fps", type=float, default=5)
    ap.add_argument("--crop", default="68,60,100,80", help="Zona en %% x1,y1,x2,y2")
    args = ap.parse_args()

    pattern = re.compile(args.regex)
    ocr = RapidOCR()
    seen = set()
    x1, y1, x2, y2 = (float(v) / 100 for v in args.crop.split(","))
    send(args.topic, f"Bot iniciado. Buscando el directo {args.url}")
    fails = 0

    while True:
        try:
            url = get_stream_url(args.url)
        except Exception as e:
            fails += 1
            if fails in (1, 10, 40):
                send(args.topic, f"No pude abrir el directo: {e}. Sigo intentando.")
            time.sleep(15)
            continue
        send(args.topic, "Conectado al directo. Mirando la pantalla...")
        n, last_alive, last_hint = 0, time.time(), 0
        for frame in frames(args.url, args.fps):
            n += 1
            crop = frame[int(y1 * H):int(y2 * H), int(x1 * W):int(x2 * W)]
            result, _ = ocr(crop)
            text = " ".join(r[1] for r in (result or [])).upper()
            found = False
            for m in pattern.finditer(text):
                found = True
                code = "-".join(m.groups())
                if code not in seen:
                    seen.add(code)
                    send(args.topic, code, title="CODIGO NUEVO", prio="urgent")
            if not found and "COD" in text and time.time() - last_hint > 30:
                last_hint = time.time()
                send(args.topic, f"Vi el cuadro pero no lei bien: {text}", prio="high")
            if time.time() - last_alive > 600:
                last_alive = time.time()
                send(args.topic, f"Sigo mirando ({n} capturas revisadas)", prio="low")
        send(args.topic, "Se corto el video, reconectando...", prio="low")
        time.sleep(2)


if __name__ == "__main__":
    main()
