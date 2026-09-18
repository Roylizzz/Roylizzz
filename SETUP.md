# Manual del perfil

Todo lo que se ve en el README sale de este repo. No hay servicios externos
dibujando tarjetas: los SVG los genera Python y los actualiza GitHub Actions.

```txt
Roylizzz/
├── README.md                 la composición
├── assets/                   todos los SVG generados (no editar a mano)
│   └── covers/               portadas y retratos bajados de AniList + meta.json
├── tools/
│   ├── pixelfont.py          fuente de 5x7 px y helpers de pixel art
│   ├── theme.py              paleta morada y chrome de las tarjetas
│   ├── fetch_covers.py       baja portadas/personajes de AniList (se corre a mano)
│   ├── build_assets.py       hero, headings, pills, cards de anime, footer
│   └── build_stats.py        activity / pulse / code time (con datos reales)
└── .github/workflows/
    ├── metrics.yml           recalcula las métricas cada noche
    └── snake.yml             redibuja la snake y la publica en la rama output
```

---

## Checklist

- [ ] **1.** Reemplazar los dos enlaces de contacto del README
- [ ] **2.** Conectar Spotify
- [ ] **3.** Conectar WakaTime *(opcional)*
- [ ] **4.** Crear el secret `METRICS_TOKEN` *(opcional, para contribuciones privadas)*
- [ ] **5.** Dejar que corran los workflows una primera vez

Hasta que hagas 2 y 3, esas dos tarjetas muestran un estado "sin conectar"
diseñado a propósito. Nunca se ve una imagen rota.

---

## 1. Enlaces de contacto

En la sección `connect` del README hay dos placeholders:

```html
<a href="https://www.linkedin.com/in/YOUR_LINKEDIN">
<a href="mailto:YOUR_EMAIL">
```

Cambia `YOUR_LINKEDIN` por tu usuario de LinkedIn y `YOUR_EMAIL` por el correo
que quieras hacer público. Si no quieres publicar correo, borra ese bloque
completo y su `&nbsp;` anterior.

## 2. Spotify

Se usa [spotify-github-profile](https://github.com/kittinan/spotify-github-profile),
que es hosted: no hay que desplegar nada.

1. Entra a <https://spotify-github-profile.kittinan.com/>
2. Dale a **Connect with Spotify** y autoriza tu cuenta.
3. La página te devuelve una URL con tu `uid` (algo como `uid=31abc...`).
4. En el README, busca el comentario `SETUP.md · step 2`, borra el bloque
   `<picture>` de abajo y pega en su lugar la línea que está dentro del
   comentario, cambiando `YOUR_UID` por tu uid real.

La tarjeta ya viene con los colores del perfil (`background_color=0d0718`,
`bar_color=8b5cf6`). Si prefieres otro estilo, cambia `theme=novatorem` por
`default`, `compact` o `natemoo-re`.

## 3. WakaTime

La tarjeta **code time** se dibuja con tus datos reales en cuanto exista el
secret.

1. Crea cuenta en <https://wakatime.com> e instala el plugin en Visual Studio
   y VS Code.
2. Copia tu API key desde <https://wakatime.com/settings/account>.
3. En este repo: **Settings → Secrets and variables → Actions → New repository
   secret**, con nombre `WAKATIME_API_KEY`.

En la siguiente corrida de `metrics.yml` la tarjeta pasa de "no api key yet" a
mostrar tus lenguajes de los últimos 7 días.

## 4. Contribuciones privadas (opcional)

Por defecto las métricas usan el `GITHUB_TOKEN` del workflow, que solo ve
actividad pública. Para que cuente también lo privado:

1. Crea un
   [personal access token clásico](https://github.com/settings/tokens/new) con
   el scope `read:user`.
2. Guárdalo como secret `METRICS_TOKEN`.
3. Activa **Settings → Profile → Include private contributions on my profile**.

## 5. Primera corrida

En la pestaña **Actions** habilita los workflows si GitHub los deja en pausa, y
lanza a mano `metrics` y `snake` con *Run workflow*.

- `snake.yml` crea la rama `output` con `snake-dark.svg` y `snake-light.svg`.
  El README apunta ahí, así que la rama `main` nunca se llena de commits
  automáticos de imágenes.
- `metrics.yml` commitea `assets/stats-*.svg`, `assets/pulse-*.svg` y
  `assets/codetime-*.svg` solo si los números cambiaron.

Si `Actions` no tiene permiso de escritura: **Settings → Actions → General →
Workflow permissions → Read and write permissions**.

---

## Editar el diseño

Los SVG de `assets/` son **generados**. Si editas uno a mano, el siguiente
build lo pisa. Lo que se toca es `tools/`:

```bash
cd tools
python fetch_covers.py    # solo si cambias la lista de animes/mangas
python build_assets.py    # hero, headings, pills, tarjetas de anime, footer
python build_stats.py     # tarjetas con datos (sin token escribe el estado vacío)
```

Cosas fáciles de cambiar:

| Quiero… | Dónde |
| --- | --- |
| Otro morado | `tools/theme.py` → `DARK` / `LIGHT` |
| Cambiar las líneas del neofetch | `tools/build_assets.py` → `NEOFETCH` |
| Cambiar la nota de un anime | `tools/build_assets.py` → `WATCHLIST` |
| Agregar o quitar un anime | `tools/fetch_covers.py` → `WATCHLIST`, correrlo, y espejar la lista en `build_assets.py` |
| Otro texto en los separadores | `tools/build_assets.py` → `NOTES` |
| Otro título de sección | `tools/build_assets.py` → `HEADINGS` |
| Redibujar la máscara oni | `tools/build_assets.py` → `ONI` (grid de 16x16) |

Los glyphs de pixel art son strings: `.` es vacío y cada letra es un color de
la paleta del asset. El script valida el tamaño de cada grid al arrancar, así
que si te equivocas en una fila te lo dice.

## Portadas y personajes

Las portadas y los retratos salen de [AniList](https://anilist.co) vía su API
pública. `fetch_covers.py` los baja, los recorta al tamaño exacto que usan las
tarjetas y guarda el formato, el año y el score reales en
`assets/covers/meta.json`. Después `build_assets.py` los incrusta dentro de los
SVG en base64: el README no hotlinkea el CDN de nadie, así que no se rompe si
AniList cambia una URL.

Si agregas un título, la búsqueda usa el nombre y el tipo (`ANIME` o `MANGA`).
Si AniList devuelve la obra equivocada, afina el término de búsqueda con el
título en romaji.

## Contador de visitas

Usa [moe-counter](https://github.com/journey-ad/Moe-Counter) con el tema
`asoul`. Si algún día deja de responder, cambia esa línea del README por:

```html
<img src="https://komarev.com/ghpvc/?username=Roylizzz&label=VISITORS&color=8b5cf6&style=for-the-badge&labelColor=0d0718" alt="Visitas">
```

## Paleta

| Rol | Dark | Light |
| --- | --- | --- |
| Fondo | `#07040D` | `#FBF9FF` |
| Panel | `#0D0718` | `#FFFFFF` |
| Borde | `#2E1A52` | `#DCCEFA` |
| Acento | `#8B5CF6` | `#7C3AED` |
| Acento 2 | `#A855F7` | `#9333EA` |
| Glow | `#C084FC` | `#A855F7` |
| Fucsia | `#F0ABFC` | `#C026D3` |
