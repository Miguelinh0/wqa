"""Lee el chat de Twitch, detecta codigos que ponen los MODS y los canjea solo.

Uso (en tu PC):
    pip install playwright pyperclip
    python -m playwright install chromium
    python chat_bot.py rubius

Se abre un navegador: inicia sesion en la pagina de canje UNA vez, deja la
pagina abierta y presiona Enter en la terminal. Desde ahi el bot mete cada
codigo apenas un mod lo escribe en el chat.
"""
import argparse
import random
import re
import socket
import sys
import time

# 12 caracteres en grupos de 4, con o sin guiones: F355-HPQJ-B5B8 / F355HPQJB5B8
CODE_RE = re.compile(r"(?<![A-Z0-9])([A-Z0-9]{4})[-\s]?([A-Z0-9]{4})[-\s]?([A-Z0-9]{4})(?![A-Z0-9])")

REDEEM_URLS = {
    "ps": "https://store.playstation.com/redeem",
    "google": "https://play.google.com/redeem?code={code}",
}
BUTTONS = re.compile(r"canjear|redeem|continuar|continue|confirmar|confirm|aceptar|ok", re.I)


def beep():
    try:
        import winsound
        winsound.Beep(1500, 300)
    except Exception:
        print("\a", end="", flush=True)


def find_codes(text):
    out = []
    for m in CODE_RE.finditer(text.upper()):
        raw = m.group(0)
        code = "-".join(m.groups())
        # sin guiones exige al menos un numero (evita palabras de 12 letras)
        if "-" not in raw and not any(c.isdigit() for c in code):
            continue
        out.append(code)
    return out


def parse(line):
    """Devuelve (usuario, es_mod, mensaje) de una linea IRC de Twitch, o None."""
    if " PRIVMSG " not in line:
        return None
    tags = {}
    if line.startswith("@"):
        raw_tags, line = line[1:].split(" ", 1)
        for kv in raw_tags.split(";"):
            k, _, v = kv.partition("=")
            tags[k] = v
    prefix, _, rest = line.partition(" PRIVMSG ")
    _, _, msg = rest.partition(" :")
    user = tags.get("display-name") or prefix.lstrip(":").split("!")[0]
    badges = tags.get("badges", "")
    is_mod = tags.get("mod") == "1" or "broadcaster/" in badges or "moderator/" in badges
    return user, is_mod, msg


def chat_lines(channel):
    while True:
        try:
            s = socket.create_connection(("irc.chat.twitch.tv", 6667), timeout=300)
            nick = f"justinfan{random.randint(10000, 99999)}"  # anonimo, solo lectura
            s.sendall(b"CAP REQ :twitch.tv/tags\r\n")
            s.sendall(f"NICK {nick}\r\nJOIN #{channel.lower()}\r\n".encode())
            print(f"Conectado al chat de {channel}. Esperando codigos de mods...", flush=True)
            buf = b""
            while True:
                data = s.recv(65536)
                if not data:
                    break
                buf += data
                *lines, buf = buf.split(b"\r\n")
                for raw in lines:
                    line = raw.decode("utf-8", "ignore")
                    if line.startswith("PING"):
                        s.sendall(b"PONG :tmi.twitch.tv\r\n")
                        continue
                    yield line
        except Exception as e:
            print("Chat desconectado, reconectando...", e, flush=True)
        time.sleep(1)


class Redeemer:
    def __init__(self, url):
        from playwright.sync_api import sync_playwright
        self.url = url
        self.pw = sync_playwright().start()
        kw = dict(user_data_dir="perfil_canje", headless=False, no_viewport=True)
        try:
            self.ctx = self.pw.chromium.launch_persistent_context(channel="chrome", **kw)
        except Exception:
            self.ctx = self.pw.chromium.launch_persistent_context(**kw)
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()
        self.page.goto(url.replace("?code={code}", "").replace("{code}", ""))

    def ready(self):
        if "{code}" not in self.url:
            self.page.goto(self.url)

    def redeem(self, code):
        page = self.page
        t0 = time.time()
        if "{code}" in self.url:
            page.goto(self.url.format(code=code))
        else:
            inp = page.locator("input:visible").first
            inp.click(timeout=3000)
            inp.fill("")
            page.keyboard.type(code.replace("-", ""))  # sirve para 1 caja o varias cajas
            page.keyboard.press("Enter")
        print(f"   escrito en {time.time() - t0:.2f}s, confirmando...", flush=True)
        end = time.time() + 8
        while time.time() < end:
            try:
                page.get_by_role("button", name=BUTTONS).first.click(timeout=400)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("canal", nargs="?", default="rubius")
    ap.add_argument("--tienda", choices=["ps", "google"], default="ps",
                    help="ps = PlayStation Store, google = Google Play")
    ap.add_argument("--url", default=None, help="URL de canje propia (usa {code} si va en la URL)")
    ap.add_argument("--todos", action="store_true",
                    help="Acepta codigos de cualquiera, no solo mods (ojo: trolls con codigos falsos)")
    ap.add_argument("--solo-avisar", action="store_true",
                    help="No canjea: solo copia al portapapeles y pita")
    args = ap.parse_args()

    red = None
    if not args.solo_avisar:
        red = Redeemer(args.url or REDEEM_URLS[args.tienda])
        input("\n>>> Inicia sesion en el navegador, deja abierta la pagina de CANJEAR CODIGO "
              "y presiona Enter aqui... ")

    used = set()
    for line in chat_lines(args.canal):
        p = parse(line)
        if not p:
            continue
        user, is_mod, msg = p
        if not (is_mod or args.todos):
            continue
        for code in find_codes(msg):
            if code in used:
                continue
            used.add(code)
            print(f"\n>>> {time.strftime('%H:%M:%S')} CODIGO de {user}: {code}", flush=True)
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
