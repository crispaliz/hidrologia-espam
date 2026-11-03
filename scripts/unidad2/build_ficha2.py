import sys
from common import *

md(r"""
# Práctica 2 · Cierre — Ficha de síntesis del capítulo 2 y expediente de la cuenca
### Hidrología (1CIA-502) · Ingeniería Ambiental · ESPAM MFL · Unidad II
**Docente:** Ing. Cristian Paliz Acosta, MSc.

Este cuaderno **no calcula nada nuevo**: junta lo que produjiste en la Práctica 2 y

1. arma la **ficha de síntesis del capítulo 2** (una página, PNG y PDF), con las mismas filas para todos;
2. **añade el capítulo 2 al expediente de tu cuenca** (`expediente_<cuenca>_<estudiante>.csv`), el mismo archivo que
   cerraste en el capítulo 1 y que terminará en el **Compendio hidrológico de cuencas de Manabí**.

**Necesitas:** los ZIP de los pasos 1 a 5 de la Práctica 2 y tu `expediente_<cuenca>_<estudiante>.csv` del
capítulo 1 (si no lo tienes, el cuaderno arma solo el capítulo 2).

| Apartado | Contenido | Cuaderno |
|---|---|---|
| 2.1–2.3 | Precipitación media, variabilidad y tormenta mayor | `P2_paso1` |
| 2.4 | Lluvia de diseño (Gumbel, IDF, hietogramas) | `P2_paso2` |
| 2.5 | Número de curva y lluvia efectiva | `P2_paso3` |
| 2.6 | Caudal pico e hidrograma triangular (a mano) | `P2_paso4` + hoja |
| 2.7 | Balance hídrico y señal de El Niño | `P2_paso5` |
""")

md(r"""
## 1 · CONFIGURACIÓN ✍️ (única celda que editas)
- **SINTESIS:** tres frases tuyas, en lenguaje que entendería un agricultor o un técnico municipal de la cuenca.
""")
code(r'''
ESTUDIANTE = "Apellidos Nombres"
CUENCA     = "Carrizal"
SINTESIS = [
    "",   # 1. cuánta lluvia recibe la cuenca, cuándo y con qué variabilidad
    "",   # 2. qué crecida hay que esperar para 25 y 100 años y en cuántas horas llega
    "",   # 3. qué parte de la lluvia sale por el río y qué cambia con El Niño
]
''')

md("## 2 · Subir los ZIP de los pasos 1 a 5 y el expediente del capítulo 1")
code(r'''
import os, glob, zipfile, unicodedata, textwrap
import numpy as np, pandas as pd, matplotlib.pyplot as plt
SLUG = unicodedata.normalize("NFKD", ESTUDIANTE).encode("ascii", "ignore").decode().replace(" ", "_")
os.makedirs("salidas", exist_ok=True); os.makedirs("entradas", exist_ok=True)
try:
    from google.colab import files
    for nombre, contenido in files.upload().items():
        open(os.path.join("entradas", nombre), "wb").write(contenido)
except ImportError:
    print("Fuera de Colab: se leen los archivos que ya estén en la carpeta 'entradas/'.")
for z in glob.glob("entradas/*.zip"):
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            if os.path.basename(n).startswith("expediente_"):
                open(os.path.join("entradas", os.path.basename(n)), "wb").write(zf.read(n))
COLS = ["capitulo", "apartado", "campo", "valor", "unidad", "fuente"]
def leer(paso):
    cand = sorted(glob.glob(f"entradas/expediente_{paso}_*.csv"))
    if not cand:
        print(f"❌ Falta el expediente del {paso}: ejecuta ese cuaderno y sube su ZIP."); return pd.DataFrame(columns=COLS)
    print(f"✅ {paso}: {os.path.basename(cand[-1])}"); return pd.read_csv(cand[-1], dtype=str).fillna("")
PASOS = {p: leer(p) for p in ["P2p1", "P2p2", "P2p3", "P2p4", "P2p5"]}
cap1 = [f for f in glob.glob(f"entradas/expediente_{CUENCA}_*.csv")]
CAP1 = pd.read_csv(cap1[0], dtype=str).fillna("") if cap1 else pd.DataFrame(columns=COLS)
CAP1 = CAP1[CAP1.capitulo != "2"]
print(("✅ Capítulo 1: " + os.path.basename(cap1[0])) if cap1 else "⚠️  No subiste el expediente del capítulo 1: se arma solo el capítulo 2.")
''')

md(r"""
## 3 · Unir el capítulo 2 y revisar coherencia
El cuaderno revisa que no falte ningún campo y cruza resultados de pasos distintos: si no cuadran, hay un paso
que se ejecutó con otra cuenca u otra configuración.
""")
code(r'''
EXTRA = pd.DataFrame([("2", "2.8", f"Síntesis {i + 1}", t, "", "estudiante") for i, t in enumerate(SINTESIS)], columns=COLS)
CAP2 = pd.concat(list(PASOS.values()) + [EXTRA], ignore_index=True)
def val(campo, df=None):
    df = CAP2 if df is None else df
    s = df.loc[df.campo == campo, "valor"]
    try: return float(str(s.iloc[0]).replace(",", ".")) if len(s) else np.nan
    except ValueError: return np.nan
opc = CAP2.fuente.eq("estudiante")
faltan = CAP2[(CAP2.valor.astype(str).str.strip() == "")]
if len(faltan):
    print("⚠️  Campos vacíos (los de «estudiante» son tus valores a mano o tu bitácora):")
    for _, r in faltan.iterrows(): print(f"   · {r.apartado} {r.campo} ({r.fuente})")
else:
    print("✅ Capítulo 2 completo")
cu = set(PASOS["P2p1"].loc[PASOS["P2p1"].campo == "Cuenca", "valor"])
if cu and CUENCA not in cu: print(f"⚠️  El paso 1 es de la cuenca {cu}, no de {CUENCA}.")
A1, A4 = val("Área de la cuenca"), val("Área A")
if np.isfinite(A1) and np.isfinite(A4):
    print(f"Área en el paso 1: {A1:.1f} km² · en el paso 4: {A4:.1f} km² " + ("✅" if abs(A1 - A4) < 0.01 * A1 else "⚠️ distinta: ¿usaste el mismo límite?"))
tc1, tc4 = val("Tiempo de concentración (Kirpich) (tc)", CAP1) if len(CAP1) else np.nan, val("Tiempo de concentración tc")
if np.isfinite(tc1) and np.isfinite(tc4):
    print(f"tc del capítulo 1: {tc1:.1f} h · usado en el paso 4: {tc4:.1f} h " + ("✅" if abs(tc1 - tc4) < 0.05 else "⚠️ distinto"))
for T in (10, 25, 100):
    qm, qc = val(f"Qp a mano T={T}"), val(f"Qp triangular T={T}")
    if np.isfinite(qm) and np.isfinite(qc):
        e = 100 * (qm / qc - 1); print(f"Qp a mano T={T}: {qm:.0f} · cuaderno {qc:.0f} m³/s ({e:+.1f} %) " + ("✅" if abs(e) <= 5 else "⚠️"))
c3, c5 = val("Coeficiente de escorrentía T=25"), val("Coeficiente de escorrentía Q/P")
if np.isfinite(c3) and np.isfinite(c5):
    print(f"Pe/P de la tormenta de 25 años (paso 3): {c3:.2f} · Q/P anual (paso 5): {c5:.2f} → "
          + "son cosas distintas: una tormenta extrema frente al promedio de un año, que incluye flujo base y estiaje.")
EXP = pd.concat([CAP1, CAP2], ignore_index=True)
EXP.to_csv(f"salidas/expediente_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
print(f"✅ Expediente acumulado: {len(EXP)} campos (capítulo 1: {len(CAP1)}, capítulo 2: {len(CAP2)})")
CAP2
''')

md("## 4 · La ficha de síntesis del capítulo 2 (una página)\nVa al final de tu capítulo 2 y se suma al Compendio.")
code(r'''
def v(campo, d=None):
    s = CAP2.loc[CAP2.campo == campo, "valor"]; s = str(s.iloc[0]) if len(s) else ""
    if d is not None:
        try: s = f"{float(s.replace(',', '.')):,.{d}f}".replace(",", " ").replace(".", ",")
        except ValueError: pass
    return s or "—"
filas = [
 ("Área · estaciones dentro / usadas", f"{v('Área de la cuenca', 1)} · {v('Estaciones dentro de la cuenca', 0)} / {v('Estaciones usadas en Thiessen e isoyetas', 0)}", "km² · n.º", "2.1"),
 ("P media: aritmética / Thiessen / isoyetas", f"{v('P media aritmética', 0)} / {v('P media Thiessen', 0)} / {v('P media isoyetas', 0)}", "mm/año", "2.1"),
 ("Año más lluvioso / más seco · CV", f"{v('Año más lluvioso')} / {v('Año más seco')} · {v('Coeficiente de variación anual', 2)}", "— · —", "2.2"),
 ("Lluvia de enero a mayo · meses secos", f"{v('Lluvia de enero a mayo', 0)} % · {v('Meses secos (< 60 mm)', 0)}", "% · meses", "2.2"),
 ("Tormenta mayor de 5 días", f"{v('Lluvia de la tormenta mayor', 0)} mm · {v('Tormenta mayor de 5 días')}", "mm", "2.3"),
 ("P24 para T = 10 / 25 / 100 años", f"{v('P24 T=10', 0)} / {v('P24 T=25', 0)} / {v('P24 T=100', 0)}", "mm", "2.4"),
 ("Gumbel: KS D / D crítico", f"{v('Kolmogorov–Smirnov D', 3)} / {v('KS D crítico 5 %', 3)}", "—", "2.4"),
 ("IDF: I = K·T^m / D^n", f"K {v('IDF K', 1)} · m {v('IDF m', 3)} · n {v('IDF n', 3)}", "mm/h, años, min", "2.4"),
 ("CN AMC I / II / III", f"{v('CN AMC I', 1)} / {v('CN ponderado AMC II', 1)} / {v('CN AMC III', 1)}", "—", "2.5"),
 ("Pe para T = 10 / 25 / 100 (24 h, AMC II)", f"{v('Pe T=10 AMC II', 0)} / {v('Pe T=25 AMC II', 0)} / {v('Pe T=100 AMC II', 0)}", "mm", "2.5"),
 ("tc / tp / tb", f"{v('Tiempo de concentración tc', 1)} / {v('Tiempo al pico tp', 1)} / {v('Tiempo base tb', 1)}", "h", "2.6"),
 ("Qp triangular T = 10 / 25 / 100", f"{v('Qp triangular T=10', 0)} / {v('Qp triangular T=25', 0)} / {v('Qp triangular T=100', 0)}", "m³/s", "2.6"),
 ("Qp a mano T = 10 / 25 / 100", f"{v('Qp a mano T=10', 0)} / {v('Qp a mano T=25', 0)} / {v('Qp a mano T=100', 0)}", "m³/s", "2.6"),
 ("Crecida de registros T = 100 (instantánea)", v("Q instantáneo de crecidas T=100", 0), "m³/s", "2.6"),
 ("Balance: P / Q / P − Q · Q/P", f"{v('P media anual (balance)', 0)} / {v('Q media anual', 0)} / {v('P − Q (ET real + ΔS)', 0)} · {v('Coeficiente de escorrentía Q/P', 2)}", "mm/año · —", "2.7"),
 ("El Niño 1997–98: lluvia / caudal frente a lo normal", f"×{v('El Niño 1997–98: P / normal', 1)} / ×{v('El Niño 1997–98: Q / normal', 1)}", "—", "2.7"),
]
fig = plt.figure(figsize=(8.27, 11.69))
ax = fig.add_axes([0.07, 0.04, 0.86, 0.92]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.autoscale(False)
ax.text(0, 1.0, f"Ficha de síntesis · Cuenca {CUENCA}", fontsize=17, fontweight="bold", va="top", color="#12263A")
ax.text(0, 0.965, f"Capítulo 2 · Precipitación y escorrentía · Hidrología 1CIA-502 · ESPAM MFL · {ESTUDIANTE}", fontsize=10, va="top", color="#44525E")
y = 0.92; ax.plot([0, 1], [y + 0.008, y + 0.008], color="#12263A", lw=1.2)
for campo, valor, unidad, ap in filas:
    lin = textwrap.wrap(valor, 38) or ["—"]
    ax.text(0, y, campo, fontsize=9, fontweight="bold", va="top", color="#12263A")
    for i, l in enumerate(lin): ax.text(0.45, y - i * 0.017, l, fontsize=9, va="top")
    ax.text(0.80, y, unidad, fontsize=7.5, va="top", color="#5B6B78"); ax.text(1.0, y, ap, fontsize=8.5, va="top", ha="right", color="#B3541A")
    y -= 0.02 + 0.017 * len(lin); ax.plot([0, 1], [y + 0.011, y + 0.011], color="#D9D3C4", lw=0.6)
y -= 0.01
ax.text(0, y, "Qué dice el capítulo 2 de la cuenca", fontsize=11, fontweight="bold", va="top", color="#12263A"); y -= 0.03
for i, t in enumerate(SINTESIS):
    for l in textwrap.wrap(f"{i + 1}. {t or '—'}", 95): ax.text(0, y, l, fontsize=9.5, va="top"); y -= 0.019
    y -= 0.008
ax.text(0, 0.0, "Fuente: expediente de la cuenca (P2_paso1 a P2_paso5 y hoja de cálculo del hidrograma). Lluvia diaria INAMHI 1964–2018 (relleno Climatol con CHIRPS); "
        "CN NRCS TR-55 adaptado; caudales GEOGloWS corregidos con anuarios INAMHI. Cuadernos CC BY-NC-SA 4.0 · github.com/crispaliz/hidrologia-espam",
        fontsize=7, color="#5B6B78", va="bottom", wrap=True)
for ext in ("png", "pdf"):
    plt.savefig(f"salidas/ficha_sintesis_cap2_{CUENCA}_{SLUG}.{ext}", dpi=200 if ext == "png" else None)
plt.show()
''')

md("## 5 · Descargar")
code(r'''
import shutil
paquete = shutil.make_archive(f"Capitulo2_{CUENCA}_{SLUG}", "zip", "salidas")
print("✅ Paquete:", paquete)
try:
    from google.colab import files; files.download(paquete)
except ImportError:
    print("Descárgalo desde el panel de archivos de Colab.")
''')
save(sys.argv[1] if len(sys.argv) > 1 else "P2_ficha_capitulo2.ipynb")
