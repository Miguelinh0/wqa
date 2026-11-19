# Bots de códigos del directo

## chat_bot.py (recomendado, el más rápido) — lee el CHAT y canjea solo
Solo acepta códigos escritos por **mods o el streamer** (evita códigos falsos de trolls).

**Windows: doble clic en `INICIAR.bat`** (instala todo solo). O a mano:
```
pip install playwright pyperclip
python -m playwright install chromium
python chat_bot.py rubius
```
1. Se abre un navegador en la página de canje de PlayStation Store. **Inicia sesión** y deja abierta la página donde se escribe el código.
2. Vuelve a la terminal y presiona **Enter**.
3. Cuando un mod escriba un código, el bot lo escribe, presiona Enter y toca Canjear/Continuar/Confirmar solo. También lo copia y pita.

Opciones:
- `--tienda google` para Google Play en vez de PlayStation.
- `--url "https://..."` para otra página de canje (usa `{code}` si el código va en la URL).
- `--solo-avisar` no canjea, solo pita y copia el código.
- `--todos` acepta códigos de cualquiera del chat (no recomendado).

La sesión queda guardada en la carpeta `perfil_canje`, no hace falta loguearse de nuevo.

## bot.py — lee el código desde el VIDEO (OCR)
Más lento (retraso del video). Ver `python bot.py --help`.
