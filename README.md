# logo-animation-icpt

Pantalla de entrada (splash) de ICPT para Power Apps Canvas.

| Archivo | Qué es |
|---|---|
| `prototype/icpt-entrance.html` | Prototipo v3. Abrir en el navegador. Tiene 4 variantes (default: D · Orbit + 3 olas), 3 modos de movimiento, scrub de timeline, simulación de tick del Timer, modo `<img>` (igual que el Image control) y campos dinámicos editables. |
| `docs/DEV_HANDOFF.md` | **Empezar acá.** Qué recibe el dev, decisiones tomadas, plan de prueba por etapas, checklist y preguntas abiertas. |
| `docs/ICPT_Entrance_PowerFx_Spec.md` | Traducción a Power Fx: qué no se traduce y por qué, App.Formulas (UDFs), fórmulas por control, timelines y pendientes. |
| `assets/icpt-bulb.svg` | Bulbo + base sin los puntos, para Media en Power Apps. Los puntos son Circle controls. |

Campos dinámicos (no hardcodear): nombre de usuario, Organizational Unit y versión. En el prototipo están en `DYNAMIC`. También se pasan por URL: `icpt-entrance.html?name=Ana%20P%C3%A9rez&ou=Europe%20OU&v=4.2`.
