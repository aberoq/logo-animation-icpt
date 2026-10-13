# logo-animation-icpt

Pantalla de entrada (splash) de ICPT para Power Apps Canvas.

| Archivo | Qué es |
|---|---|
| `prototype/icpt-entrance.html` | **Laboratorio** (todos los controles). Prototipo v4, fondo blanco (continuidad con el loader nativo de Power Apps). Abrir en el navegador. Tiene 4 variantes (default: D · Orbit + 3 olas), 3 modos de movimiento, dos opciones de indicador de carga, dos gradientes para el nombre, overlay para alinear el logo con el loader nativo, scrub de timeline, simulación de tick del Timer, modo `<img>` (igual que el Image control) y campos dinámicos editables. Termina con "Welcome [NAME]": no tiene wordmark. |
| `prototype/icpt-entrance-po.html` | **Versión para el PO.** Variante D (Orbit + 3 olas), sin opciones de diseño: solo Play/Pausa, Reiniciar, Nombre, OU y "Mostrar antes el loader de Power Apps". Generada: no editar a mano. |
| `prototype/icpt-entrance-dev.html` | **Versión para el dev.** Solo el splash, a pantalla completa, sin controles ni loader nativo simulado. Nombre, OU y versión son variables: bloque `DYNAMIC` o URL (`?name=…&ou=…&v=…`). Tecla R: reinicia. Generada: no editar a mano. |
| `scripts/build_variants.py` | Genera las versiones del PO y del dev a partir de `icpt-entrance.html` (mismo motor de animación): `python3 scripts/build_variants.py`. |
| `docs/DEV_HANDOFF.md` | **Empezar acá.** Qué recibe el dev, decisiones tomadas, plan de prueba por etapas, checklist y preguntas abiertas. |
| `docs/ICPT_Entrance_PowerFx_Spec.md` | Traducción a Power Fx: qué no se traduce y por qué, App.Formulas (UDFs), fórmulas por control, timelines y pendientes. |
| `assets/icpt-bulb.svg` | Bulbo + base sin los puntos, para Media en Power Apps. Los puntos son Circle controls. |

Campos dinámicos (no hardcodear): nombre de usuario, Organizational Unit y versión. En el prototipo están en `DYNAMIC`. También se pasan por URL: `icpt-entrance.html?name=Ana%20P%C3%A9rez&ou=Europe%20OU&v=4.2`.
