"""Bot que mira un directo, lee codigos con OCR y te los manda al celular.

Uso:
    python bot.py URL_DEL_DIRECTO --topic MI_TEMA_SECRETO
"""
import argparse
import re
import time

import cv2
import requests
import streamlink
from rapidocr_onnxruntime import RapidOCR

# Formato PlayStation: XXXX-XXXX-XXXX (con o sin guiones / espacios)
DEFAULT_REGEX = r"\b([A-Z0-9]{4})[-\s]?([A-Z0-9]{4})[-\s]?([A-Z0-9]{4})\b"


def get_stream_url(page_url):
    streams = streamlink.streams(page_url)
    if not streams:
        raise SystemExit("No encontre el stream. ¿Esta en vivo? ¿El link es correcto?")
    for q in ("720p", "720p60", "best"):
        if q in streams:
            return streams[q].url
    return next(iter(streams.values())).url


def notify(topic, code):
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=code.encode(),
            headers={"Title": "CODIGO NUEVO", "Priority": "urgent", "Tags": "video_game"},
            timeout=5,
        )
    except Exception as e:
        print("Error enviando notificacion:", e)
    try:
        import pyperclip
        pyperclip.copy(code)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="Link del directo (YouTube, Twitch, Kick...)")
    ap.add_argument("--topic", required=True, help="Tema de ntfy al que esta suscrito tu celular")
    ap.add_argument("--regex", default=DEFAULT_REGEX, help="Formato del codigo")
    ap.add_argument("--every", type=float, default=1.0, help="Segundos entre capturas")
    ap.add_argument("--crop", default=None,
                    help="Zona a leer en %% x1,y1,x2,y2 (ej: 0,60,100,100 = mitad inferior). Mas rapido.")
    ap.add_argument("--debug", action="store_true", help="Muestra todo el texto que lee")
    args = ap.parse_args()

    pattern = re.compile(args.regex)
    ocr = RapidOCR()
    seen = set()
    notify(args.topic, "Bot conectado, esperando codigos...")

    while True:
        url = get_stream_url(args.url)
        cap = cv2.VideoCapture(url)
        print("Conectado al directo. Mirando...")
        last = 0.0
        while cap.isOpened():
            if not cap.grab():
                break
            now = time.time()
            if now - last < args.every:
                continue
            last = now
            ok, frame = cap.retrieve()
            if not ok:
                continue
            if args.crop:
                x1, y1, x2, y2 = (float(v) / 100 for v in args.crop.split(","))
                h, w = frame.shape[:2]
                frame = frame[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]
            result, _ = ocr(frame)
            text = " ".join(r[1] for r in (result or [])).upper()
            if args.debug and text:
                print("[OCR]", text)
            for m in pattern.finditer(text):
                code = "-".join(m.groups()) if m.groups() else m.group(0)
                if code in seen:
                    continue
                seen.add(code)
                print(f"\a>>> CODIGO: {code}  ({time.strftime('%H:%M:%S')})")
                notify(args.topic, code)
        cap.release()
        print("Se corto el stream, reconectando...")
        time.sleep(2)


if __name__ == "__main__":
    main()
