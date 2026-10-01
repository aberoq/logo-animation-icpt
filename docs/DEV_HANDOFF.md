# ICPT — Handoff de la entrance animation para desarrollo

Este documento es el punto de entrada para el dev que implementa la animación en Power Apps Canvas. Primero lean este documento. Después usen la spec como referencia de fórmulas.

## 1. Estado

| Qué | Estado |
|---|---|
| Diseño de la animación | Aprobado. La variante por defecto es **D · Orbit + 3 olas**, con movimiento **Fluido**. |
| Prototipo HTML | Validado en navegador (Chromium). Cada propiedad es una función de una sola variable de tiempo, igual que en Power Apps. |
| Fórmulas Power Fx | **Todavía no se probaron en un tenant.** Están escritas para que el traspaso sea 1:1 con el prototipo, pero puede haber errores de sintaxis. El primer paso del plan (§4) existe para encontrarlos rápido. |

## 2. Qué recibe el dev

| Recurso | Dónde | Para qué |
|---|---|---|
| Repo | `aberoq/logo-animation-icpt`, rama `claude/icpt-entrance-animation-n8erv5` | Todo el material |
| Spec Power Fx | `docs/ICPT_Entrance_PowerFx_Spec.md` | Fórmulas por control, UDFs, timelines, riesgos conocidos |
| Prototipo | `prototype/icpt-entrance.html` (abrir en el navegador) | Referencia visual. La barra de abajo permite pausar, ir a cualquier ms y comparar variantes. |
| Prototipo publicado | Link privado de claude.ai. **Se tiene que compartir desde el menú Share** para que el dev lo pueda abrir. | Lo mismo, sin descargar nada |
| Asset del bulbo | `assets/icpt-bulb.svg` | Cargar en Media. Los 5 puntos **no** están en el SVG: son controles Circle. |
| Video de referencia | `test-entrance-animation.mp4` (no está en el repo, porque tiene marca del cliente) | Compartir por el canal interno del proyecto, si el dev lo necesita |

## 3. Decisiones de diseño ya tomadas

No cambiar estas decisiones sin consultar con diseño:

- **El logo no se mueve** para el wordmark. "Investment / Prioritization Tool" usa las mismas dos líneas que "Welcome" + nombre.
- **Movimiento fluido:** los puntos siguen un objetivo con un resorte de amortiguamiento crítico (`Follow`). No reemplazar por easings por tramos: con easings por tramos el movimiento se ve robótico.
- **Pulso de los puntos:** 100 % → 80 % → 210 % → 100 %, con una separación de 3.5 unidades (~9 px) sobre el rayo de cada punto.
- **Flote:** solo la bombilla flota. Los puntos no.
- **Respiración del texto:** la opacidad baja a 65 % en los 3 loops, sincronizada con la ola.
- **Hold hasta que haya datos:** si la carga tarda, la ola se repite en ciclos completos (`SplashShift`). La animación nunca se corta a mitad de una ola.

## 4. Plan de prueba por etapas

Cada etapa termina con una verificación. No sigan a la etapa siguiente si la verificación falla.

### Etapa 0 — Prueba de riesgo (≈ 1 h, antes de construir nada más)

El riesgo principal es que el Image control parpadee cuando su SVG cambia en cada tick del Timer.

1. Creen una app Canvas en blanco, con tamaño 1366 × 768.
2. Activen **Settings → Updates → User-defined functions**.
3. En `App.Formulas` peguen solo esto, copiado de la spec §3: `Clamp01`, `Prog`, `EaseOut`, `EaseIn`, `N` y `RevealSvg`.
4. Agreguen esta pantalla mínima:

```powerfx
// Screen1.OnVisible
Set(varT0, Now()); Set(varT, 0)

// Timer1: Duration 30, Repeat true, AutoStart true, Visible false
// Timer1.OnTimerEnd
Set(varT, Mod(DateDiff(varT0, Now(), TimeUnit.Milliseconds), 3000))

// Image1: X 0, Y 300, Width Parent.Width, Height 58, ImagePosition Fit
// Image1.Image  (entra a los 0 ms, sale a los 1500 ms, se repite cada 3 s)
RevealSvg("Welcome María José Ñúñez & Co", varT, 36, Parent.Width, "#FFFFFF", "",
          "'Segoe UI', Arial, sans-serif",
          0, 25, 220, false,
          1500, 25, 200, false)

// Screen1.Fill
Color.Black
```

5. Verifiquen en **Teams desktop**, en el **navegador** y en el **player móvil**:

| Verificación | Resultado esperado |
|---|---|
| Las letras suben una por una a través de la máscara y bajan al salir | Sí, sin parpadeo de la imagen completa |
| El texto queda centrado como una sola línea | Sí. Si cada letra se centra por separado, revisen que se use `dy` y no `y` (spec §1, fila 2). |
| Acentos, `Ñ` y `&` | Se ven bien (prueba de `EncodeUrl` + escape XML) |
| Usuario con configuración regional es-CO o es-MX | El SVG se ve igual. Si se rompe, `N()` no está usando `"en-US"`. |
| Fluidez con `Duration` 30 | Aceptable. Si no, prueben 50 ms y anoten cuál funciona en cada dispositivo. |

**Si hay parpadeo:** paren y avisen a diseño antes de seguir. El plan B es animar el texto por línea en vez de por letra (spec §9, punto 4).

### Etapa 1 — Logo

`conLogo` (Container con padding de 22 px), `imgBulb` y los 5 `cirDot*`, con `Follow`, `DotScale`, `DotDrift`, `WaveLocal` y `BulbFloat` (spec §3 y §5). Usen `TL` variante D.

Verificación: comparen contra el prototipo en los ms 1700, 2000 y 2300 (el scrub de la barra permite ir a cada uno). Los puntos no se cortan en el borde del Container. Solo la bombilla flota.

### Etapa 2 — Texto y wordmark

`imgWelcome`, `imgName`, `imgWm1`, `imgWm2` y los tags (spec §5).

Verificación: la respiración del texto se ve en los 3 loops. Con un nombre de 35 o más caracteres, la fuente se achica, y "Prioritization Tool" espera a que el nombre termine de salir.

### Etapa 3 — Carga de datos y navegación

Mover la carga real de la app a `scrSplash.OnVisible` (spec §4), `SplashShift` y `Navigate(…, ScreenTransition.Fade)`.

Verificación: con una carga lenta (por ejemplo, una colección grande o una demora simulada), la ola se repite y la salida empieza al final de un ciclo completo. **Confirmen que el Timer sigue corriendo mientras corre `Concurrent(...)`.** Si no sigue, muevan la carga a `App.OnStart` (spec §4, nota).

### Etapa 4 — Campos dinámicos reales

Reemplazar los placeholders en `App.Formulas`: `SplashUserName`, `SplashOrgUnit`, `AppVersion` (spec §8).

## 5. Checklist de aceptación

- [ ] Sin parpadeo en Teams desktop, navegador y móvil.
- [ ] Secuencia D completa en ≈ 7.7 s con datos rápidos.
- [ ] Con datos lentos, la animación espera en ciclos completos y nunca se corta.
- [ ] Nombre, OU y versión vienen de datos reales. Nada está hardcodeado.
- [ ] Nombres largos y con caracteres especiales se ven bien.
- [ ] Funciona con configuración regional es-CO / es-MX.
- [ ] El logo no se mueve cuando entra el wordmark.

## 6. Preguntas abiertas

| Pregunta | Quién responde |
|---|---|
| ¿De qué campo sale la OU del usuario logueado? | Rafa |
| ¿`User().FullName` es el nombre correcto, o usan un perfil propio? | Rafa |
| ¿Quién actualiza `AppVersion` en cada release? | Rafa |
| Colores de los puntos: el video y el SVG v2 no coinciden (spec §5) | Diseño, contra Figma |
| Wordmark como paths de Figma, una letra por capa (hoy es texto con Segoe UI) | Diseño exporta, dev reemplaza en `imgWm1` / `imgWm2` |
| Tamaño de diseño real de la app (se asumió 1366 × 768) | Rafa |

## 7. Si el dev usa Claude Code

Prompt sugerido para la primera sesión, con el repo clonado:

```
Voy a implementar en Power Apps Canvas la animación de entrada de ICPT.
Lee primero docs/DEV_HANDOFF.md y después docs/ICPT_Entrance_PowerFx_Spec.md.
El prototipo de referencia es prototype/icpt-entrance.html: cada función de JS tiene
una UDF de Power Fx con el mismo nombre y la misma lógica.
Estoy en la etapa <N> del plan (§4). Te voy a pegar los errores que me da Power Apps Studio;
corrígelos en la spec manteniendo el comportamiento igual al prototipo.
```
