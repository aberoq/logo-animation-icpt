# ICPT — Entrance animation: spec Power Fx (v3)

Esta spec reemplaza la v2. El prototipo de referencia es `prototype/icpt-entrance.html`. Cada función de esta spec tiene una función con el mismo nombre en el prototipo, con la misma lógica.

Fuente de timing: `test-entrance-animation.mp4`, medido cuadro a cuadro (30 fps, con análisis de píxeles de cada punto y de cada línea de texto). En esta spec, t = 0 es el primer cuadro negro (0.47 s en el video).

---

## 1. Qué no se traduce tal cual a Power Fx, y la solución

| # | Qué hay en el prototipo v2 o en el video | Por qué no funciona en Canvas Apps | Solución en v3 |
|---|---|---|---|
| 1 | Revelado letra por letra con un `<span>` por letra y `@keyframes` | Un Label no tiene transform por carácter. Una galería con una letra por item rompe el kerning (las letras tienen anchos distintos). | `RevealSvg()`: un Image control por línea. Su `Image` es un SVG con un `<tspan>` por letra, generado con `Concat(Sequence(Len(txt)), …)`. El kerning es correcto con cualquier nombre. |
| 2 | Cada `<tspan>` con `y` absoluto | **Error que encontré al probar:** un `y` absoluto abre un "text chunk" nuevo, y `text-anchor='middle'` centra cada letra por separado ("W e lcom e"). | Usar `dy` relativo: desplazamiento de la letra i menos el de la letra i−1. |
| 3 | `transform: scale()` + `transform-origin` en los puntos | Power Apps no tiene escala. | Circle controls. Escalar = `Width`/`Height` × s, y recentrar `X`/`Y` con `Self.Width / 2`. |
| 4 | Texto con gradiente (`background-clip:text`) | Un Label solo tiene un color sólido. | `linearGradient` dentro del SVG (`objectBoundingBox`: se adapta al ancho de cualquier nombre). |
| 5 | Cadena de `setTimeout` + `transition` CSS | No existe. Además, los tiempos se desfasan entre sí. | Un Timer y una variable de tiempo real. Todo es función pura de `varT`. Easing escrito como fórmula. |
| 6 | Opacidad del grupo del logo | Un Container no tiene `Transparency`. | Opacidad por control: `Image.Transparency` en el bulbo, `RGBA(r,g,b,alpha)` en cada Circle. |
| 7 | Puntos que crecen a 2.1× y se separan del bulbo | Un Container recorta a sus hijos. En el pico, el punto de arriba y los de la izquierda salen hasta 20 px del borde y se cortan. | El Container del logo tiene 22 px de padding en cada lado (`LogoPad`). |
| 8 | Timer que suma `varT + 30` en cada tick | El Timer no es preciso (jitter, pestaña en segundo plano). La animación se atrasa. | `varT = DateDiff(varT0, Now(), TimeUnit.Milliseconds)`. Si un tick se atrasa, el siguiente cuadro igual es correcto. |
| 9 | Números dentro del SVG | `Text(12.5)` en un tenant es-CO / es-MX da `"12,5"` y el SVG se rompe. | `N(x) = Text(Round(x, 2), "0.##", "en-US")`. Siempre con `"en-US"`. |
| 10 | Fuente del wordmark (geométrica ancha, parecida a Montserrat Bold) | Un SVG dentro de un Image control se renderiza como imagen y **no carga fuentes web**. Solo usa fuentes del sistema. | Nombre y "Welcome": `Segoe UI` (sistema, en Windows). Wordmark: paths de Figma, una letra por `<g>` (pendiente, ver §8). |
| 11 | Logo que sube con un "dissolve" (cuadros fantasma de 8.6 s a 8.8 s en el video) | Es el Smart Animate de Figma: un crossfade entre dos posiciones. No hay crossfade de posición en Power Apps. | Tween de `Y` con `EaseInOut`. Se ve más limpio. |
| 12 | El logo "salta" 15 px hacia abajo al salir (10.55 s en el video) | Es un artefacto del prototipo de Figma. | Lo omití. El logo sale con fade en su lugar. |
| 13 | El `Image` cambia en cada tick | Riesgo: re-decodificar un SVG a 30 fps puede parpadear en algunos players. | El SVG cambia solo durante entradas y salidas (~2.5 s en total). La respiración y los fades van en `Transparency`, no en el SVG. **Probar esto primero en el dispositivo real** (§9). |

Errores de la v2 contra el video, ya corregidos en v3:

| v2 | Video (v3) |
|---|---|
| Las letras bajan desde arriba con fade | Las letras suben desde abajo a través de una máscara (línea de corte en la baseline) |
| Nombre con colores cíclicos por letra (rojo, naranja, amarillo…) | Nombre con un gradiente continuo: menta → amarillo → naranja → rojo |
| Pulso de los 6 elementos, base incluida, en orden p0…p5 | Solo los 5 puntos. Orden horario desde abajo a la izquierda: LB → LT → arriba → RT → RB. 110 ms entre puntos en A, 95 ms en B y C (más superposición = se lee como una sola ola). |
| Pulso simple 1 → 1.4 → 1 | 1 → 0.8 → 2.1 → 1 en ~810 ms. El punto sigue un objetivo con un resorte de amortiguamiento crítico (`Follow`), la misma curva ease-out de la entrada orbit. Velocidad continua: sin pausas ni quiebres. |
| Los puntos crecen en su lugar | Mientras crece, cada punto se aleja ~13 px del centro de la bombilla (máximo en el 210 %, vuelve a 0 en el 100 %) sobre su propio rayo (como un asterisco). En la anticipación no se mueve hacia adentro. |
| La bombilla está fija | La bombilla flota ~3.5 px hacia abajo y vuelve, un ciclo por ola, con el mismo `Follow` que los puntos (baja rápido, sube con una cola larga). Los puntos no flotan. |
| El logo se achica a 0.82 para el wordmark | El logo no cambia de tamaño. Sube 15 px. |
| El wordmark aparece con fade | El wordmark entra letra por letra, igual que "Welcome" |
| Loop infinito | Termina y navega a la app (`Navigate(…, ScreenTransition.Fade)`) |
| El texto no cambia durante el hold | El texto "respira": la opacidad baja a 0.65 en cada ola, desde la ola 2 |

---

## 2. Arquitectura

- Una pantalla `scrSplash`, fondo negro.
- Un Timer `tmrSplash` actualiza `varT` (ms desde el inicio), `varShift` y `varTb`.
- Cada propiedad animada es una fórmula sobre esas variables. Ningún control tiene estado propio.
- "Hold hasta que haya datos": si la carga no termina, la ola se repite en ciclos completos. Todo lo que pasa después del hold usa `varTb = varT − varShift` (ver `SplashShift`).

Controles:

| Control | Tipo | Qué hace |
|---|---|---|
| `tmrSplash` | Timer | Reloj. `Visible = false`. |
| `conLogo` | Container | Grupo del logo. Solo posición (Y animada). Padding 22 px. |
| `imgBulb` | Image | Bulbo + base (`assets/icpt-bulb.svg`, en Media). Solo se mueve en Y (flote). |
| `cirDotTop`, `cirDotLT`, `cirDotRT`, `cirDotLB`, `cirDotRB` | Circle | Los 5 puntos. Width/Height/X/Y animados. |
| `imgWelcome`, `imgName` | Image | Saludo y nombre (`RevealSvg`). |
| `imgWm1`, `imgWm2` | Image | "Investment" / "Prioritization Tool". |
| `conOU` + `lblOU`, `conVer` + `lblVer` | Container + Label | Tags de abajo. El Container da el radio de 6 px (un Label clásico no tiene radio). |

---

## 3. App.Formulas

> Requiere **User-defined functions** (Settings → Updates). Si no las pueden activar en el tenant, peguen el cuerpo de cada función inline en el control. Es más largo, pero funciona igual.

```powerfx
// =====================================================================
// CAMPOS DINÁMICOS — NO HARDCODEAR
// =====================================================================
SplashUserName = User().FullName;      // TODO: confirmar si usan otro campo de perfil
SplashOrgUnit  = "LATAM OU";           // TODO (Rafa): reemplazar por la fuente real de la OU del usuario logueado
AppVersion     = "4.1";                // Constante por release. Se muestra como "V" & AppVersion

// =====================================================================
// Variante activa. Idea: "A" la primera vez del día, "B" las siguientes.
// =====================================================================
SplashVariant = "C";   // favorita actual: Orbit + compacta

// Layout en unidades de diseño (medido en el video sobre 1366 x 768).
Lay = {
    K: 2.56,            // 1 unidad del SVG del logo (viewBox 38 x 39.07) = 2.56 px
    LogoPad: 22,
    LogoTop: -120,      // top del logo respecto del centro vertical
    LogoRise: 10,
    LogoUp: 15,
    DotD: 4.954,
    DotPeak: 2.1,       // escala máxima del pulso
    DotDrift: 3.5,      // separación máxima sobre el rayo, unidades del SVG (≈ 9 px)
    // Pulso (ms). Las curvas bezier están dentro de DotScale.
    // Pulso fluido (ver DotScale). Los valores lo / hi salen de un cálculo: no cambiar uno sin el otro.
    PulseTau: 65, PulseLo: 0.6871, PulseHi: 2.5997, PulseA: 140, PulseB: 300,
    DriftTau: 80, DriftNorm: 0.6323,      // separación: seguimiento más lento => follow-through
    FloatTau: 0.09, FloatNorm: 0.8525,    // flote de la bombilla (fracciones del período de ola)
    BulbFloat: 3.5,     // flote de la bombilla, px hacia abajo
    TxtSize: 36,
    WelcomeBase: 33,    // baselines respecto del centro vertical
    NameBase: 71,
    NameMaxW: 0.62,
    WmSize: 34,
    Wm1Base: 20,
    Wm2Base: 58
};

// Timelines (ms). Mismos números que TL.A / TL.B / TL.C en el prototipo.
TL = Switch(SplashVariant,
    "A", {orbit: false, logoInDur: 300, orbitAt: 0, orbitStag: 0, orbitDur: 1, sweep: 0, bulbInDur: 1,
          w1In: 30, w1Stag: 25, w1Dur: 220, nmIn: 250, nmStag: 12, nmDur: 380,
          waveAt: 1200, period: 1450, waves: 4, step: 110, breath: 0.35,
          w1Out: 6830, w1OutStag: 25, w1OutDur: 200, nmOut: 7080, nmOutStag: 10, nmOutDur: 330,
          logoUpAt: 8100, logoUpDur: 260, wm1In: 8580, wm1Stag: 30, wm1Dur: 220, wm2In: 8880, wm2Stag: 8, wm2Dur: 180,
          outAt: 10080, wmOutDur: 100, logoOutDur: 250, navAt: 10780},
    "B", {orbit: false, logoInDur: 300, orbitAt: 0, orbitStag: 0, orbitDur: 1, sweep: 0, bulbInDur: 1,
          w1In: 30, w1Stag: 22, w1Dur: 200, nmIn: 200, nmStag: 10, nmDur: 320,
          waveAt: 800, period: 1300, waves: 2, step: 95, breath: 0.25,
          w1Out: 3300, w1OutStag: 22, w1OutDur: 180, nmOut: 3480, nmOutStag: 9, nmOutDur: 300,
          logoUpAt: 3950, logoUpDur: 240, wm1In: 4250, wm1Stag: 26, wm1Dur: 200, wm2In: 4500, wm2Stag: 7, wm2Dur: 170,
          outAt: 5500, wmOutDur: 120, logoOutDur: 250, navAt: 5950},
    /* "C" */
         {orbit: true, logoInDur: 300, orbitAt: 80, orbitStag: 70, orbitDur: 750, sweep: -150, bulbInDur: 450,
          w1In: 780, w1Stag: 22, w1Dur: 200, nmIn: 950, nmStag: 10, nmDur: 320,
          waveAt: 1700, period: 1300, waves: 1, step: 95, breath: 0.25,
          w1Out: 2950, w1OutStag: 22, w1OutDur: 180, nmOut: 3130, nmOutStag: 9, nmOutDur: 300,
          logoUpAt: 3600, logoUpDur: 240, wm1In: 3900, wm1Stag: 26, wm1Dur: 200, wm2In: 4150, wm2Stag: 7, wm2Dur: 170,
          outAt: 5150, wmOutDur: 120, logoOutDur: 250, navAt: 5600}
);

// =====================================================================
// UDFs
// =====================================================================
Clamp01(x: Number): Number = Max(0, Min(1, x));
Prog(t: Number, start: Number, dur: Number): Number = Clamp01((t - start) / dur);
EaseOut(p: Number): Number = 1 - Power(1 - Clamp01(p), 3);
EaseIn(p: Number): Number = Power(Clamp01(p), 3);
EaseInOut(p: Number): Number = With({q: Clamp01(p)}, If(q < 0.5, 4 * Power(q, 3), 1 - Power(-2 * q + 2, 3) / 2));
N(x: Number): Text = Text(Round(x, 2), "0.##", "en-US");

// Seguimiento con resorte de amortiguamiento crítico: 0 -> 1, curva ease-out con velocidad 0 al arrancar.
// Es la misma familia de curva que la entrada orbit. Sumar varios Follow desfasados da un movimiento
// con velocidad continua siempre (no hay quiebres entre tramos).
Follow(x: Number, tau: Number): Number = If(x <= 0, 0, 1 - (1 + x / tau) * Exp(-x / tau));

// Pulso de un punto (~810 ms). u = ms desde que empieza el pulso de ESE punto.
// El objetivo salta 1 -> lo (0 ms) -> hi (a) -> 1 (b) y el punto lo sigue con Follow.
// lo / hi están calculados para tocar exactamente 0.80 (a los 143 ms) y 2.10 (a los 317 ms).
DotScale(u: Number): Number =
    If(u <= 0 || u >= Lay.PulseB + 12 * Lay.PulseTau, 1,
        1 + (Lay.PulseLo - 1)            * Follow(u, Lay.PulseTau)
          + (Lay.PulseHi - Lay.PulseLo)  * Follow(u - Lay.PulseA, Lay.PulseTau)
          + (1 - Lay.PulseHi)            * Follow(u - Lay.PulseB, Lay.PulseTau));

// Separación sobre el rayo (unidades del SVG). Sale en "a" y vuelve en "b", con un seguimiento
// más lento que la escala (DriftTau > PulseTau): eso da el follow-through sin un retraso artificial.
DotDrift(u: Number): Number =
    If(u <= 0, 0,
        Lay.DotDrift * Max(0, Follow(u - Lay.PulseA, Lay.DriftTau) - Follow(u - Lay.PulseB, Lay.DriftTau)) / Lay.DriftNorm);

// Flote de la bombilla (px hacia abajo). Un ciclo por ola; empieza 17 % del período antes de la ola.
// Baja con Follow y sube con Follow (al 30 % del ciclo). Mismo lenguaje de movimiento que los puntos.
BulbFloat(t: Number, shift: Number): Number =
    With({w: t - (TL.waveAt - 0.17 * TL.period)},
        If(w < 0 || w >= (TL.waves + shift / TL.period) * TL.period, 0,
            With({u: Mod(w, TL.period) / TL.period},
                Lay.BulbFloat * Max(0, Follow(u, Lay.FloatTau) - Follow(u - 0.3, Lay.FloatTau)) / Lay.FloatNorm)));

// Ciclos extra si los datos no están listos. readyAt = -1 => todavía cargando.
SplashShift(t: Number, readyAt: Number): Number =
    With({r: If(readyAt < 0, t + TL.period, readyAt)},
        Max(0, RoundUp((r - TL.w1Out) / TL.period, 0)) * TL.period);

// Tiempo local del pulso de un punto en la ola actual (-1 antes de la primera ola).
// order: LB=0, LT=1, Top=2, RT=3, RB=4.
WaveLocal(t: Number, order: Number, shift: Number): Number =
    With({w: t - TL.waveAt},
        If(w < 0, -1,
            With({idx: Min(RoundDown(w / TL.period, 0), TL.waves + shift / TL.period - 1)},
                t - (TL.waveAt + idx * TL.period + order * TL.step))));

// Respiración del texto (0..1), desde la ola 2.
Breath(t: Number, shift: Number): Number =
    With({w: t - (TL.waveAt + TL.period) + 130},
        If(w < 0 || w > (TL.waves + shift / TL.period - 1) * TL.period, 0,
            With({u: Mod(w, TL.period)}, If(u > 1000, 0, Power(Sin(Pi() * u / 1000), 2)))));

// Una línea de texto con revelado letra por letra a través de una máscara.
// Baseline a 1.2 × size. Máscara hasta 1.5 × size (deja lugar a los descendentes: g, j, p, q, y).
RevealSvg(txt: Text, t: Number, size: Number, w: Number, fill: Text, defs: Text, family: Text,
          inAt: Number, inStag: Number, inDur: Number, inFade: Boolean,
          outAt: Number, outStag: Number, outDur: Number, outFade: Boolean): Text =
    "data:image/svg+xml;utf8," & EncodeUrl(
        "<svg xmlns='http://www.w3.org/2000/svg' width='" & N(w) & "' height='" & N(size * 1.6) & "'>" &
        defs &
        "<clipPath id='m'><rect width='" & N(w) & "' height='" & N(size * 1.5) & "'/></clipPath>" &
        "<g clip-path='url(#m)'><text x='" & N(w / 2) & "' y='" & N(size * 1.2) &
        "' text-anchor='middle' font-family=""" & family & """ font-weight='700' font-size='" & N(size) &
        "' fill='" & fill & "'>" &
        Concat(
            Sequence(Len(txt)),
            With(
                {
                    c:   Mid(txt, Value, 1),
                    pi:  EaseOut(Prog(t, inAt + (Value - 1) * inStag, inDur)),
                    po:  EaseIn(Prog(t, outAt + (Value - 1) * outStag, outDur)),
                    pi0: If(Value = 1, 1, EaseOut(Prog(t, inAt + (Value - 2) * inStag, inDur))),
                    po0: If(Value = 1, 0, EaseIn(Prog(t, outAt + (Value - 2) * outStag, outDur)))
                },
                // dy RELATIVO = offset(i) − offset(i−1). No usar "y" absoluto (ver §1, fila 2).
                "<tspan dy='" & N(((1 - pi) + po - (1 - pi0) - po0) * size * 1.2) &
                "' fill-opacity='" & N(If(inFade, pi, If(pi > 0, 1, 0)) * If(outFade, 1 - po, 1)) & "'>" &
                If(c = " ", "&#160;",
                   Substitute(Substitute(Substitute(c, "&", "&amp;"), "<", "&lt;"), ">", "&gt;")) &
                "</tspan>"
            )
        ) &
        "</text></g></svg>"
    );

GradName = "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='0'>" &
           "<stop offset='0' stop-color='#70D6A6'/><stop offset='0.22' stop-color='#F2C12B'/>" &
           "<stop offset='0.42' stop-color='#FFA000'/><stop offset='1' stop-color='#F40008'/></linearGradient></defs>";
GradWm2  = "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='0'>" &
           "<stop offset='0' stop-color='#F40008'/><stop offset='0.28' stop-color='#FFA000'/>" &
           "<stop offset='0.45' stop-color='#D9A31C'/><stop offset='0.68' stop-color='#6ED578'/>" &
           "<stop offset='1' stop-color='#59B8AC'/></linearGradient></defs>";
FontUI = "'Segoe UI', Arial, sans-serif";
```

---

## 4. Pantalla y Timer

```powerfx
// scrSplash.Fill
Color.Black

// scrSplash.OnVisible
Set(varT0, Now());
Set(varT, 0); Set(varShift, 0); Set(varTb, 0); Set(varLogoAlpha, 0);
Set(varReadyAt, -1);
Set(varSplashOn, true);
// Carga de datos (la misma que hoy hace la app al entrar):
Concurrent(
    ClearCollect(colRequests, /* … */),
    ClearCollect(colDates, /* … */)
);
Set(varReadyAt, DateDiff(varT0, Now(), TimeUnit.Milliseconds));

// tmrSplash
Duration    = 30
Repeat      = true
AutoStart   = false
Start       = varSplashOn
Visible     = false
OnTimerEnd  =
    Set(varT, DateDiff(varT0, Now(), TimeUnit.Milliseconds));
    Set(varShift, SplashShift(varT, varReadyAt));
    Set(varTb, varT - varShift);
    // Opacidad común del logo (un Container no tiene opacidad; ver §5)
    Set(varLogoAlpha, If(TL.orbit, 1, Prog(varT, 0, 150)) * (1 - Prog(varTb, TL.outAt, TL.logoOutDur)));
    If(varTb >= TL.navAt,
        Set(varSplashOn, false);
        Navigate(scrHome, ScreenTransition.Fade)
    )
```

> Verificar: el Timer tiene que seguir corriendo mientras `Concurrent(...)` carga. Si en su tenant el `OnVisible` bloquea el Timer, muevan la carga a `App.OnStart` o a named formulas, y pongan `varReadyAt` al terminar.

---

## 5. Fórmulas por control

### conLogo (Container)
```powerfx
Width  = 38 * Lay.K + 2 * Lay.LogoPad
Height = 39.07 * Lay.K + 2 * Lay.LogoPad
X      = (Parent.Width - Self.Width) / 2
Y      = Parent.Height / 2 + Lay.LogoTop - Lay.LogoPad
         + If(TL.orbit, 0, Lay.LogoRise * (1 - EaseOut(Prog(varT, 0, TL.logoInDur))))
         - Lay.LogoUp * EaseInOut(Prog(varTb, TL.logoUpAt, TL.logoUpDur))
Fill   = Color.Transparent
```

La opacidad común del logo está en `varLogoAlpha` (se calcula en `tmrSplash.OnTimerEnd`). Cada hijo la usa, porque el Container no tiene opacidad.

### imgBulb (Image, `icpt-bulb` en Media)
```powerfx
// bs = escala del bulbo (solo C)
Width        = 38 * Lay.K * If(TL.orbit, 0.85 + 0.15 * EaseOut(Prog(varT, 0, TL.bulbInDur)), 1)
Height       = Self.Width * 39.07 / 38
X            = Lay.LogoPad + (38 * Lay.K - Self.Width) / 2
Y            = Lay.LogoPad + (39.07 * Lay.K - Self.Height) / 2 + BulbFloat(varT, varShift)   // solo la bombilla flota
Transparency = 1 - varLogoAlpha * If(TL.orbit, Prog(varT, 0, TL.bulbInDur), 1)
```

### cirDot* (Circle). Ejemplo: cirDotLB
Datos de cada punto (unidades del SVG):

`ux`, `uy` = dirección del rayo: vector unitario desde el centro del asterisco (19, 19) hasta el punto.

| Control | cx | cy | ux | uy | order | Color (video) | Color (SVG v2) |
|---|---|---|---|---|---|---|---|
| cirDotTop | 19.00 | 2.48 | 0 | −1 | 2 | `#F4330A` | `#F40008` |
| cirDotLT | 2.48 | 12.02 | −0.921 | −0.389 | 1 | `#F40008` | `#FFA000` |
| cirDotRT | 35.52 | 12.02 | 0.921 | −0.389 | 3 | `#6ED578` | `#64BEC2` |
| cirDotLB | 2.48 | 31.09 | −0.807 | 0.591 | 0 | `#F2C12B` | `#F2C12B` |
| cirDotRB | 35.52 | 31.09 | 0.807 | 0.591 | 4 | `#64BEC2` | `#6ED578` |

Variantes A / B:
```powerfx
Width  = Lay.DotD * Lay.K * DotScale(WaveLocal(varT, 0, varShift))
Height = Self.Width
X      = Lay.LogoPad + (2.48  + -0.807 * DotDrift(WaveLocal(varT, 0, varShift))) * Lay.K - Self.Width / 2
Y      = Lay.LogoPad + (31.09 +  0.591 * DotDrift(WaveLocal(varT, 0, varShift))) * Lay.K - Self.Height / 2
Fill   = RGBA(242, 193, 43, varLogoAlpha)
```

Variante C (orbit). Centro de giro (19, 18.5). Para cada punto, `r` y `a0` son constantes (calcular una vez con `Sqrt(dx^2 + dy^2)` y `Atan2(dx, dy)`; en Power Fx `Atan2` recibe **(x, y)**):
```powerfx
With({p: EaseOut(Prog(varT, TL.orbitAt + 0 * TL.orbitStag, TL.orbitDur))},
     With({a: a0 + (1 - p) * Radians(TL.sweep)},
          /* X */ Lay.LogoPad + (19 + r * Cos(a)) * Lay.K - Self.Width / 2))
// Y igual con 18.5 + r * Sin(a). Width multiplicado por p. Alpha × Clamp01(p * 3).
// Sumar también el drift: + ux * DotDrift(s) en X, + uy * DotDrift(s) en Y (igual que A / B).
```

### imgWelcome (Image)
```powerfx
X = 0
Width = Parent.Width
Height = Lay.TxtSize * 1.6
Y = Parent.Height / 2 + Lay.WelcomeBase - Lay.TxtSize * 1.2
ImagePosition = ImagePosition.Fit
Image = RevealSvg("Welcome", varT, Lay.TxtSize, Parent.Width, "#FFFFFF", "", FontUI,
                  TL.w1In, TL.w1Stag, TL.w1Dur, false,
                  TL.w1Out + varShift, TL.w1OutStag, TL.w1OutDur, false)
Transparency = TL.breath * Breath(varT, varShift)
Visible = varTb < TL.w1Out + 7 * TL.w1OutStag + TL.w1OutDur + 50
```

### imgName (Image) — DINÁMICO
```powerfx
// Tamaño: no se puede medir texto en Power Fx. Estimación: 0.6 em por letra, máximo 62 % del ancho.
// Nombres largos achican la fuente en lugar de cortarse.
With({s: Min(Lay.TxtSize, Lay.NameMaxW * Parent.Width / (0.6 * Len(SplashUserName)))},
    RevealSvg(SplashUserName, varT, s, Parent.Width, "url(#g)", GradName, FontUI,
              TL.nmIn, TL.nmStag, TL.nmDur, true,
              TL.nmOut + varShift, TL.nmOutStag, TL.nmOutDur, true))
// Y y Height usan el mismo "s": Y = Parent.Height / 2 + Lay.NameBase - s * 1.2 ; Height = s * 1.6
Transparency = TL.breath * Breath(varT, varShift)
Visible = varTb < TL.nmOut + Len(SplashUserName) * TL.nmOutStag + TL.nmOutDur + 50
```

### imgWm1 / imgWm2 (Image)
```powerfx
// imgWm1 (hoy texto con fuente de sistema; reemplazar por paths de Figma, ver §8)
Image = RevealSvg("Investment", varTb, Lay.WmSize, Parent.Width, "#FFFFFF", "", FontUI,
                  TL.wm1In, TL.wm1Stag, TL.wm1Dur, false, 1E9, 0, 1, false)
Y = Parent.Height / 2 + Lay.Wm1Base - Lay.WmSize * 1.2
Transparency = Prog(varTb, TL.outAt, TL.wmOutDur)
Visible = varTb >= TL.wm1In

// imgWm2
Image = RevealSvg("Prioritization Tool", varTb, Lay.WmSize, Parent.Width, "url(#g)", GradWm2, FontUI,
                  TL.wm2In, TL.wm2Stag, TL.wm2Dur, false, 1E9, 0, 1, false)
Y = Parent.Height / 2 + Lay.Wm2Base - Lay.WmSize * 1.2
```

### Tags — DINÁMICO
```powerfx
// lblOU.Text
SplashOrgUnit
// lblVer.Text
"V" & AppVersion
// conOU / conVer: un Label clásico no tiene AutoWidth. Ancho estimado:
Width  = Max(114, Len(lblOU.Text) * 9.5 + 36)
Height = 36
X      = 32                                   // conVer: Parent.Width - 32 - Self.Width
Y      = Parent.Height - 28 - Self.Height
Fill   = RGBA(22, 23, 26, 1)
RadiusTopLeft = 6   // y los otros tres
// lbl*: Color = RGBA(226, 227, 230, 1), Size 12 (≈16 px), FontWeight Semibold, Align Center
```

---

## 6. Timeline variante A (fiel al video)

| ms | Evento |
|---|---|
| 0 | Corte a negro. El logo aparece (fade 150 ms) y sube 10 px (300 ms). |
| 30 → 400 | "Welcome" letra por letra (stagger 25 ms, 220 ms por letra, sin fade). |
| 250 → ≈ 800 | Nombre letra por letra, con fade (stagger 12 ms, 380 ms). El final depende del largo del nombre. |
| 1200, 2650, 4100, 5550 | 4 olas. Cada una: LB → LT → Top → RT → RB, cada 110 ms. La bombilla flota un ciclo por ola. |
| 2520 → 6420 | El texto respira (opacidad mín. 0.65) en las olas 2 a 4. |
| 6830 → 7180 | "Welcome" baja y sale por la máscara. |
| 7080 → ≈ 7530 | El nombre baja y sale, con fade. |
| 8100 → 8360 | El logo sube 15 px. |
| 8580 → 9070 | "Investment" letra por letra. |
| 8880 → 9200 | "Prioritization Tool" letra por letra. |
| 10080 | Sale el wordmark (100 ms). El logo sale con fade (250 ms). |
| 10780 | `Navigate(scrHome, ScreenTransition.Fade)`. |

Con datos lentos, todo lo que está desde 6830 ms en adelante se corre en ciclos completos de 1450 ms.

---

## 7. Variantes

| | A · Fiel al video | B · Compacta | C · Orbit + compacta |
|---|---|---|---|
| Duración | ≈ 11 s | ≈ 6 s | ≈ 5.9 s |
| Entrada del logo | Fade + sube 10 px | Igual que A | Bulbo escala 0.85 → 1. Los puntos entran orbitando 150° alrededor del bulbo (Cos/Sin), con stagger de 70 ms. |
| Olas | 4 × 1450 ms | 2 × 1300 ms | 1 × 1300 ms (la órbita reemplaza a la primera ola) |
| Respiración | 0.35 | 0.25 | 0.25 |
| Uso sugerido | Primer ingreso del día / demo | Ingresos siguientes | Alternativa de marca, más "viva" en la entrada |

Recomendación: no mostrar 11 s de splash en cada ingreso. Usen A la primera vez del día y B las siguientes. Con `SplashShift` ninguna de las dos corta la animación a mitad de una ola si los datos tardan.

---

## 8. Campos dinámicos

| Campo | Placeholder en el prototipo | Power Apps | Estado |
|---|---|---|---|
| Nombre del usuario | `María Fernanda López` (ficticio) | `SplashUserName = User().FullName` | Confirmar si usan un campo de perfil propio |
| Organizational Unit | `LATAM OU` | `SplashOrgUnit` | **Fuente pendiente (preguntar a Rafa)** |
| Versión | `4.1` → "V4.1" | `AppVersion` (named formula) | Definir quién la actualiza por release |

En el prototipo se pueden probar en la barra de abajo, o por URL: `?name=…&ou=…&v=…`. El nombre acepta acentos, `&`, `<`, `>` y nombres largos (la fuente se achica).

---

## 9. Pendientes

1. **`icpt-logo.svg` no está en el repo.** Usé los paths del prototipo v2. Los colores de los puntos en el video son diferentes de los del SVG v2 (tabla en §5). Uno de los dos está desactualizado. Confirmar contra Figma.
2. **Wordmark como paths.** Hace falta exportar de Figma "Investment" y "Prioritization Tool" con el texto convertido a outlines (Outline / Flatten) y **una letra por capa** (sin hacer Flatten de toda la palabra), para mantener el revelado letra por letra. Cada letra pasa a ser un `<g transform='translate(0, offset)'>`.
3. **Tamaño de diseño de la app.** Usé 1366 × 768. Si la app usa otro tamaño, todo está posicionado desde el centro y se adapta, pero las medidas de `Lay` son px de diseño.
4. **Prueba de parpadeo (riesgo #13).** Antes de construir todo, armen solo `imgWelcome` + `tmrSplash` y pruébenlo en Teams desktop, en el navegador y en el player móvil. Si parpadea: suban `Duration` a 50 ms, o hagan solo el nombre por letra y el resto por línea.
5. **Fuente fuera de Windows.** En el player de iOS/Android no hay Segoe UI. El SVG usa Arial como fallback. Si el splash se usa en móvil, consideren pasar "Welcome" a paths también.
