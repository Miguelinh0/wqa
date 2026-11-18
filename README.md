# Bot de códigos del directo

Mira el directo, lee el código con OCR y te lo manda al celular (ntfy) + lo copia al portapapeles del PC.

## Pasos (5 min)
1. Celular: instala la app **ntfy** y suscríbete a un tema inventado, ej: `codigos-xyz-8812`.
2. PC: instala Python 3 (en Windows marca "Add to PATH").
3. En una terminal, dentro de esta carpeta:
   ```
   pip install -r requirements.txt
   python bot.py "LINK_DEL_DIRECTO" --topic codigos-xyz-8812
   ```
4. Te llega "Bot conectado". Cuando salga un código, llega al instante: mantén pulsada la notificación → copiar → pégalo en la app.

## Opciones
- `--crop 0,60,100,100` solo lee la mitad inferior de la pantalla (más rápido, menos errores).
- `--debug` muestra todo lo que lee (para ver si capta el código).
- `--regex "..."` si el código no es formato XXXX-XXXX-XXXX.
