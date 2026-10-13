#!/usr/bin/env python3
"""Genera las versiones derivadas del prototipo a partir del laboratorio (prototype/icpt-entrance.html):

  prototype/icpt-entrance-po.html   Versión para el PO: Play/Pausa, Reiniciar, Nombre, OU y el switch
                                    "Mostrar antes el loader de Power Apps".
  prototype/icpt-entrance-dev.html  Versión para el dev: solo el splash, a pantalla completa, sin
                                    controles ni loader nativo simulado. Nombre, OU y versión son
                                    variables (bloque DYNAMIC o parámetros de URL).

Uso:  python3 scripts/build_variants.py

Las dos usan el MISMO motor de animación que el laboratorio, con las decisiones fijas:
variante D (Orbit + 3 olas), movimiento fluido, entrada continua desde el loader nativo,
gradiente Vivo e indicador "Loading..." en el splash.
Valores por defecto: María López, LA OU, versión 4.2.

No editar los archivos generados a mano: editar el laboratorio y volver a correr este script.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "prototype" / "icpt-entrance.html"


class Doc:
    def __init__(self, text):
        self.h = text

    def replace(self, old, new, count=1):
        found = self.h.count(old)
        if found != count:
            raise SystemExit(f"build_variants: se esperaban {count} coincidencias y hay {found}:\n{old[:120]}")
        self.h = self.h.replace(old, new)

    def replace_between(self, start, end, new):
        """Reemplaza desde `start` (incluido) hasta `end` (excluido)."""
        i = self.h.index(start)
        j = self.h.index(end, i)
        self.h = self.h[:i] + new + self.h[j:]


def common(d):
    """Decisiones fijas y valores por defecto, iguales en PO y dev."""
    d.replace("  userName:   'María Fernanda López',", "  userName:   'María López',")
    d.replace("  orgUnit:    'LATAM OU',", "  orgUnit:    'LA OU',")
    d.replace("  appVersion: '4.1',", "  appVersion: '4.2',")
    d.replace("let LOADER = 'text';", "let LOADER = 'text';   // \"Loading...\" en el splash; el loader nativo conserva su barra")
    d.replace("<span>scrHome — Navigate(scrHome, ScreenTransition.Fade)</span>", "<span>Aquí entra la app</span>")


def build_po():
    d = Doc(SRC.read_text(encoding="utf-8"))
    common(d)
    d.replace("<title>ICPT Entrance Prototype</title>",
              "<title>ICPT Welcome Splash</title>\n"
              "<!-- GENERADO por scripts/build_variants.py a partir de icpt-entrance.html. No editar a mano. -->")
    d.replace("  #readout{",
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
    d.replace("  :root{\n", "  :root{\n    color-scheme:dark;\n")
    d.replace_between('<div id="bar">', "\n<script>",
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
    d.replace_between("  const scrub = $('scrub');", "  requestAnimationFrame(loop);\n}",
                      "  $('progFill').style.width = (100 * Math.min(1, t / (endOf() + shift))).toFixed(2) + '%';\n")
    d.replace_between("document.querySelectorAll('button[data-v]')", "function fit(){",
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
    return d.h


def build_dev():
    d = Doc(SRC.read_text(encoding="utf-8"))
    common(d)
    d.replace("<title>ICPT Entrance Prototype</title>",
              "<title>ICPT Splash Dev</title>\n"
              "<!-- GENERADO por scripts/build_variants.py a partir de icpt-entrance.html. No editar a mano.\n"
              "     Versión de referencia para desarrollo: solo el splash, sin controles ni loader nativo simulado.\n"
              "     Variables: bloque DYNAMIC del script, o por URL: ?name=Ana%20P%C3%A9rez&ou=LA%20OU&v=4.2\n"
              "     Tecla R: reinicia la animación. -->")
    # Página blanca a pantalla completa, como la app
    d.replace("  html,body{margin:0;height:100%;background:var(--ui-bg);color:var(--ui-text);",
              "  html,body{margin:0;height:100%;background:#FFFFFF;color:var(--ui-text);")
    d.replace("  :root{\n", "  :root{\n    color-scheme:light;\n")
    d.replace("box-shadow:0 0 0 1px #2a2a2f;}", "}")
    d.replace("  const s = Math.min(vp.width / W, vp.height / H) * 0.96;", "  const s = Math.min(vp.width / W, vp.height / H);")
    # Sin barra de controles
    d.replace_between('<div id="bar">', "\n<script>", "")
    # Sin loader nativo simulado: en la app real lo pone Power Apps
    d.replace("let SHOW_NATIVE = true;", "let SHOW_NATIVE = false;   // dev: solo el splash (el loader nativo lo pone Power Apps)")
    # Reloj sin reproductor
    d.replace("    if (t >= end){ t = end; playing = false; $('btnPlay').textContent = '▶ Play'; }",
              "    if (t >= end){ t = end; playing = false; }")
    d.replace_between("  const scrub = $('scrub');", "  requestAnimationFrame(loop);\n}", "")
    d.replace("function restart(){ t = 0; playing = true; $('btnPlay').textContent = '⏸ Pausa'; }",
              "function restart(){ t = 0; playing = true; }")
    d.replace_between("document.querySelectorAll('button[data-v]')", "function fit(){",
"""// Sin controles visibles. Tecla R: reinicia. window.icptRestart() hace lo mismo desde la consola.
addEventListener('keydown', e => { if (e.key === 'r' || e.key === 'R') restart(); });
window.icptRestart = restart;

""")
    return d.h


for name, builder in [("icpt-entrance-po.html", build_po), ("icpt-entrance-dev.html", build_dev)]:
    out = ROOT / "prototype" / name
    html = builder()
    out.write_text(html, encoding="utf-8")
    print(f"build_variants: {out.relative_to(ROOT)} generado ({len(html):,} bytes)")
