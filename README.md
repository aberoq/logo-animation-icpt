# logo-animation-icpt

Pantalla de entrada (splash) de ICPT para Power Apps Canvas.

| Archivo | Qué es |
|---|---|
| `prototype/icpt-entrance.html` | **Laboratorio** (todos los controles). Prototipo v4, fondo blanco (continuidad con el loader nativo de Power Apps). Abrir en el navegador. Tiene 4 variantes (default: D · Orbit + 3 olas), 3 modos de movimiento, dos opciones de indicador de carga, dos gradientes para el nombre, overlay para alinear el logo con el loader nativo, scrub de timeline, simulación de tick del Timer, modo `<img>` (igual que el Image control) y campos dinámicos editables. Termina con "Welcome [NAME]": no tiene wordmark. |
| `prototype/icpt-entrance-po.html` | **Versión para el PO.** Variante D (Orbit + 3 olas), sin opciones de diseño: solo Play/Pausa, Reiniciar, Nombre, OU y "Mostrar antes el loader de Power Apps". **Se genera** desde el laboratorio con `python3 scripts/build_po.py`: no editar a mano. |
| `scripts/build_po.py` | Genera la versión del PO a partir de `icpt-entrance.html` (mismo motor de animación). |
| `docs/DEV_HANDOFF.md` | **Empezar acá.** Qué recibe el dev, decisiones tomadas, plan de prueba por etapas, checklist y preguntas abiertas. |
| `docs/ICPT_Entrance_PowerFx_Spec.md` | Traducción a Power Fx: qué no se traduce y por qué, App.Formulas (UDFs), fórmulas por control, timelines y pendientes. |
| `assets/icpt-bulb.svg` | Bulbo + base sin los puntos, para Media en Power Apps. Los puntos son Circle controls. |

Campos dinámicos (no hardcodear): nombre de usuario, Organizational Unit y versión. En el prototipo están en `DYNAMIC`. También se pasan por URL: `icpt-entrance.html?name=Ana%20P%C3%A9rez&ou=Europe%20OU&v=4.2`.
