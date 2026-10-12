#!/usr/bin/env python3
"""Genera prototype/icpt-entrance-po.html (versión para el PO) a partir de prototype/icpt-entrance.html
(el laboratorio, con todos los controles).

Uso:  python3 scripts/build_po.py

La versión del PO usa el MISMO motor de animación que el laboratorio. Solo cambia:
- Fija las decisiones: variante D (Orbit + 3 olas), movimiento fluido, entrada continua desde el
  loader nativo, gradiente Vivo, indicador "Loading..." en el splash (el nativo conserva su barra).
- Deja solo estos controles: Play/Pausa, Reiniciar, Nombre, OU y "Mostrar loader de Power Apps".
- Valores por defecto: María López, LA OU, versión 4.2.

No editar icpt-entrance-po.html a mano: editar el laboratorio y volver a correr este script.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "prototype" / "icpt-entrance.html"
DST = ROOT / "prototype" / "icpt-entrance-po.html"

h = SRC.read_text(encoding="utf-8")


def replace(old, new, count=1):
    global h
    found = h.count(old)
    if found != count:
        raise SystemExit(f"build_po: se esperaban {count} coincidencias y hay {found}:\n{old[:120]}")
    h = h.replace(old, new)


def replace_between(start, end, new):
    """Reemplaza desde `start` (incluido) hasta `end` (excluido)."""
    global h
    i = h.index(start)
    j = h.index(end, i)
    h = h[:i] + new + h[j:]


# ---- Título y aviso de archivo generado
replace("<title>ICPT Entrance Prototype</title>",
        "<title>ICPT Welcome Splash</title>\n"
        "<!-- GENERADO por scripts/build_po.py a partir de icpt-entrance.html. No editar a mano. -->")

# ---- Estilos de la barra del PO
replace("  #readout{",
        "  /* Barra del PO */\n"
        "  #bar.po{gap:10px;padding:12px 16px calc(12px + env(safe-area-inset-bottom, 0px));}\n"
        "  #prog{height:3px;border-radius:2px;background:var(--ui-line);overflow:hidden;}\n"
        "  #progFill{height:100%;width:0;background:var(--ui-accent);}\n"
        "  .po .row{gap:12px 16px;}\n"
        "  .po button{min-width:104px;}\n"
        "  .po input.field{width:200px;max-width:100%;}\n"
        "  .po .sep{flex:1;}\n"
        "  .po label.switch{color:var(--ui-text);}\n"
        "  button:focus-visible,input:focus-visible{outline:2px solid var(--ui-accent);outline-offset:2px;}\n"
        "  #readout{")
replace("  :root{\n", "  :root{\n    color-scheme:dark;\n")

# ---- Barra de controles reducida
replace_between('<div id="bar">', "\n<script>",
"""<div id="bar" class="po">
  <div id="prog" aria-hidden="true"><div id="progFill"></div></div>
  <div class="row">
    <button id="btnPlay" class="on">⏸ Pausa</button>
    <button id="btnReplay">↺ Reiniciar</button>
    <label>Nombre <input class="field" id="inName" aria-label="Nombre del usuario"></label>
    <label>OU <input class="field" id="inOU" style="width:120px" aria-label="Organizational Unit"></label>
    <span class="sep"></span>
    <label class="switch"><input type="checkbox" id="chkNative" checked> Mostrar antes el loader de Power Apps</label>
  </div>
</div>
""")

# ---- Pantalla final
replace("<span>scrHome — Navigate(scrHome, ScreenTransition.Fade)</span>", "<span>Aquí entra la app</span>")

# ---- Valores por defecto
replace("  userName:   'María Fernanda López',", "  userName:   'María López',")
replace("  orgUnit:    'LATAM OU',", "  orgUnit:    'LA OU',")
replace("  appVersion: '4.1',", "  appVersion: '4.2',")

# ---- Decisiones fijas (ya son el default del laboratorio; se fijan explícitamente)
replace("let variant = 'D',", "let variant = 'D',")
replace("let LOADER = 'text';", "let LOADER = 'text';   // PO: \"Loading...\" en el splash; el loader nativo conserva su barra")

# ---- Loop: barra de progreso en vez de scrub + readout
replace_between("  const scrub = $('scrub');", "  requestAnimationFrame(loop);\n}",
"""  $('progFill').style.width = (100 * Math.min(1, t / (endOf() + shift))).toFixed(2) + '%';
""")

# ---- Controles: solo Play/Pausa, Reiniciar, Nombre, OU y loader nativo
replace_between("document.querySelectorAll('button[data-v]')", "function fit(){",
"""$('btnPlay').onclick = () => {
  if (!playing && t >= endOf()) t = 0;
  playing = !playing; $('btnPlay').textContent = playing ? '⏸ Pausa' : '▶ Play';
};
$('btnReplay').onclick = restart;
if (qs.get('native') === '0') { SHOW_NATIVE = false; $('chkNative').checked = false; }
$('chkNative').onchange = e => { SHOW_NATIVE = e.target.checked; restart(); };
for (const [inp, key] of [['inName','userName'],['inOU','orgUnit']]){
  $(inp).value = DYNAMIC[key];
  $(inp).oninput = e => { DYNAMIC[key] = e.target.value; };
}

""")

DST.write_text(h, encoding="utf-8")
print(f"build_po: {DST.relative_to(ROOT)} generado ({len(h):,} bytes)")
