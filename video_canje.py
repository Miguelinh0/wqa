"""Mira el directo de Twitch, lee el codigo que aparece en pantalla y lo canjea
solo en PlayStation Store (cuenta con la sesion iniciada en el navegador).

Uso:
    python video_canje.py thegrefg
    python video_canje.py thegrefg --crop 60,55,100,85   (solo una zona de la pantalla, mas rapido)
"""
import argparse
import re
import time

from rapidocr_onnxruntime import RapidOCR

from bot import H, W, frames
from chat_bot import REDEEM_URLS, Redeemer, beep

CODE_RE = re.compile(r"([A-Z0-9]{4})\s*-\s*([A-Z0-9]{4})\s*-\s*([A-Z0-9]{4})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("canal", nargs="?", default="thegrefg")
    ap.add_argument("--crop", default="0,0,100,100",
                    help="Zona a leer en %% x1,y1,x2,y2. Por defecto toda la pantalla.")
    ap.add_argument("--fps", type=float, default=5)
    ap.add_argument("--url", default=REDEEM_URLS["ps"], help="Pagina de canje")
    ap.add_argument("--solo-avisar", action="store_true", help="No canjea, solo copia y pita")
    ap.add_argument("--debug", action="store_true", help="Muestra todo lo que lee")
    args = ap.parse_args()

    red = None
    if not args.solo_avisar:
        red = Redeemer(args.url)
        input("\n>>> Inicia sesion en PlayStation (cuenta ESPAÑOLA), deja abierta la pagina de "
              "CANJEAR CODIGO y presiona Enter aqui... ")
        red.remember()

    ocr = RapidOCR()
    x1, y1, x2, y2 = (float(v) / 100 for v in args.crop.split(","))
    used = set()
    page_url = f"https://www.twitch.tv/{args.canal}"

    while True:
        print(f"Conectando al directo de {args.canal}...", flush=True)
        n, t_status = 0, time.time()
        for frame in frames(page_url, args.fps):
            n += 1
            crop = frame[int(y1 * H):int(y2 * H), int(x1 * W):int(x2 * W)]
            result, _ = ocr(crop)
            text = " ".join(r[1] for r in (result or [])).upper()
            if args.debug and text:
                print("[OCR]", text, flush=True)
            if time.time() - t_status > 60:
                t_status = time.time()
                print(f"  mirando... ({n} imagenes revisadas)", flush=True)
            for m in CODE_RE.finditer(text):
                code = "-".join(m.groups())
                if code in used:
                    continue
                used.add(code)
                print(f"\n>>> {time.strftime('%H:%M:%S')} CODIGO EN PANTALLA: {code}", flush=True)
                beep()
                try:
                    import pyperclip
                    pyperclip.copy(code)
                except Exception:
                    pass
                if red:
                    try:
                        red.redeem(code)
                        print("   listo. Revisa el navegador.", flush=True)
                    except Exception as e:
                        print("   no pude canjearlo solo, esta copiado: pegalo tu.", e, flush=True)
                    try:
                        red.ready()
                    except Exception:
                        pass
        print("Directo no disponible o se corto. Reintento en 10s...", flush=True)
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
