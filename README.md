# Bots de códigos del directo

## video_canje.py — VE el directo, lee el código de la pantalla y lo CANJEA solo
**Windows: doble clic en `INICIAR_VIDEO_GREFG.bat`.**
1. Se abre un navegador: inicia sesión en PlayStation con la cuenta **española** y deja abierta la página de canjear código.
2. Presiona Enter en la ventana negra.
3. Cuando el código salga en pantalla, lo lee y lo canjea solo (también lo copia y pita).

Otro canal: `python video_canje.py NOMBRE_CANAL`. Solo una zona: `--crop x1,y1,x2,y2` (en %). Ver lo que lee: `--debug`.

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
