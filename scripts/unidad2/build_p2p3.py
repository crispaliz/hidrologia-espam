import sys
from common import *

md(r"""
# Práctica 2 · Paso 3 — Número de curva de tu cuenca y lluvia efectiva para 10, 25 y 100 años
### Hidrología (1CIA-502) · Ingeniería Ambiental · ESPAM MFL · Unidad II
**Docente:** Ing. Cristian Paliz Acosta, MSc.

No toda la lluvia de diseño llega al río: una parte la retienen las hojas y los charcos, otra se **infiltra**.
Lo que queda y escurre por la superficie es la **lluvia efectiva** (Pe). Este cuaderno responde:
**de la lluvia de 10, 25 y 100 años de tu cuenca, ¿cuántos milímetros escurren?**, con el método del
**número de curva (CN)** del Servicio de Conservación de Suelos de EE. UU. (SCS, hoy NRCS).

| Bloque | Qué haces | Producto |
|---|---|---|
| 3 | Mapa de **suelos** → grupo hidrológico A, B, C o D | Mapa y tabla de grupos |
| 4 | Mapa de **cobertura** del suelo | Mapa y tabla de coberturas |
| 5 | Cruce suelo × cobertura → **CN de cada polígono** | Mapa de CN |
| 6 | **CN ponderado** de la cuenca (primero a mano) | CN (AMC II), CN I y CN III |
| 7 | **Lluvia efectiva** para T = 10, 25 y 100 años (primero Pe₂₅ a mano) | Pe y coeficiente de escorrentía |
| 8 | **Hietogramas efectivos** de 24 h | Lluvia, pérdidas y Pe hora a hora |
| 9 | Expediente del capítulo 2 | `expediente_P2p3_….csv` |

`Archivo → Guardar una copia en Drive`, llena **solo la celda 1** y ejecuta
`Entorno de ejecución → Reiniciar sesión y ejecutar todo`.
""")

md(r"""
## 1 · CONFIGURACIÓN ✍️ (única celda que editas)
- **CUENCA, USAR_MI_CUENCA, RADIO_KM:** los mismos de los pasos 1 y 2.
- **CN_MANO:** tu CN ponderado calculado a mano en la sección 6.
- **PE25_MANO:** tu lluvia efectiva de 25 años calculada a mano en la sección 7 (mm).
- **LAMBDA:** fracción de la abstracción inicial, Ia = λ·S. El método clásico usa 0,2.
""")
code(CONFIG_BASE + r'''CN_MANO    = None          # después de la sección 6
PE25_MANO  = None          # mm, después de la sección 7
LAMBDA     = 0.2
T_DISENO   = (10, 25, 100)
''')

md(r"""
## 2 · Cargar datos y recuperar la lluvia de diseño del paso 2
La celda repite, sin gráficos, el Thiessen del paso 1 y el Gumbel del paso 2. Los valores de P₂₄ deben ser los
mismos de tu `expediente_P2p2`.
""")
code(CARGA + "\n" + GUMBEL)

md(r"""
## 3 · Suelos → grupo hidrológico
El método clasifica cada suelo según **qué tan rápido deja entrar el agua cuando ya está mojado**:

| Grupo | Infiltración | Suelos típicos |
|---|---|---|
| **A** | Alta (> 7,6 mm/h) | Arenas, gravas, cenizas volcánicas sueltas |
| **B** | Moderada (3,8–7,6 mm/h) | Francos, franco-arenosos |
| **C** | Lenta (1,3–3,8 mm/h) | Franco-arcillosos, suelos con capa que frena el agua |
| **D** | Muy lenta (< 1,3 mm/h) | Arcillas expansivas, suelos mal drenados o poco profundos |

La capa de suelos trae la **textura** y el **drenaje** en códigos. La tabla siguiente es la regla usada en este
curso; los códigos se verificaron con la taxonomía de cada polígono (por ejemplo, los *Vitrandept*, suelos de
ceniza, tienen textura 1 y drenaje 1; los *Tropaquept*, suelos con agua estancada, drenaje 4). **Decláralo en
tu capítulo:** es una regla de trabajo, no una medición de infiltración.

| Código de textura | Textura | Grupo base | | Código de drenaje | Drenaje | Regla |
|---|---|---|---|---|---|---|
| 1 | Gruesa | A | | 1 | Excesivo | — |
| 2 | Moderadamente gruesa | B | | 2 | Bueno | — |
| 3 | Media | B | | 3 | Moderado | — |
| 4 | Moderadamente fina | C | | 4 | Imperfecto o malo | **pasa a D** |
| 5 | Fina | D | | ≥ 94 | Sin suelo (agua, poblado, erosión) | D |
""")
code(r'''
SUE = gpd.read_file(f"{DATOS}/suelos_cobertura/suelos_cuencas.geojson")
COB = gpd.read_file(f"{DATOS}/suelos_cobertura/cobertura_cuencas.geojson")
SUE = (SUE.set_crs(32717, allow_override=True) if SUE.crs is None else SUE).to_crs(32717)
COB = (COB.set_crs(32717, allow_override=True) if COB.crs is None else COB).to_crs(32717)
SUE = gpd.clip(SUE, CU); COB = gpd.clip(COB, CU)
TEXTURA = {1: "Gruesa", 2: "Moderadamente gruesa", 3: "Media", 4: "Moderadamente fina", 5: "Fina"}
GRUPO_TEXTURA = {1: "A", 2: "B", 3: "B", 4: "C", 5: "D"}
def grupo(textura, drenaje):
    if textura not in GRUPO_TEXTURA: return "D"          # sin suelo: agua, poblado, erosión
    return "D" if drenaje == 4 else GRUPO_TEXTURA[textura]
SUE["grupo"] = [grupo(t, d) for t, d in zip(SUE.textura, SUE.drenaje)]
SUE["textura_txt"] = SUE.textura.map(TEXTURA).fillna("Sin suelo")
SUE["area_km2"] = SUE.area / 1e6
fig, ax = plt.subplots(figsize=(8, 7))
colG = {"A": "#F2E3B3", "B": "#E2B36B", "C": "#B3541A", "D": "#5A2A0C"}
for g, c in colG.items():
    s = SUE[SUE.grupo == g]
    if len(s): s.plot(ax=ax, color=c, ec="none", label=f"Grupo {g}")
cuenca.boundary.plot(ax=ax, color="k", lw=1.2)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=f"Grupo {g}") for g, c in colG.items()], frameon=False, loc="lower left")
ax.set_title(f"Grupo hidrológico de suelo · {CUENCA}", fontweight="bold")
ax.set_aspect("equal"); ax.ticklabel_format(style="plain"); ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
plt.tight_layout(); plt.savefig("salidas/P2p3_01_grupos_suelo.png", dpi=150); plt.show()
tg = SUE.groupby("grupo").area_km2.sum(); tg = pd.DataFrame({"Área (km²)": tg, "%": 100 * tg / tg.sum()})
display(tg.round(1))
tt = SUE.groupby(["orden", "textura_txt", "drenaje", "grupo"]).area_km2.sum().sort_values(ascending=False).head(10).reset_index()
tt.columns = ["Orden de suelo", "Textura", "Drenaje (código)", "Grupo", "Área (km²)"]
display(tt.round(1))
''')

md(r"""
## 4 · Cobertura del suelo
La misma lluvia escurre distinto sobre un bosque (hojarasca, raíces, suelo esponjoso) que sobre un maizal recién
arado o un techo. Las coberturas de la capa son unidades de mapeo; muchas son **mezclas** («Cultivos de ciclo
corto - Pastos plantados»).
""")
code(r'''
COB["area_km2"] = COB.area / 1e6
tc_ = COB.groupby("cobertura").area_km2.sum().sort_values(ascending=False)
tc_ = pd.DataFrame({"Área (km²)": tc_, "%": 100 * tc_ / tc_.sum()})
display(tc_.round(1))
fig, ax = plt.subplots(figsize=(9, 7))
COB.plot(ax=ax, column="cobertura", cmap="tab20", legend=True, ec="none",
         legend_kwds={"loc": "upper left", "bbox_to_anchor": (1, 1), "fontsize": 7, "frameon": False})
cuenca.boundary.plot(ax=ax, color="k", lw=1.2)
ax.set_title(f"Cobertura del suelo · {CUENCA}", fontweight="bold")
ax.set_aspect("equal"); ax.ticklabel_format(style="plain"); ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
plt.tight_layout(); plt.savefig("salidas/P2p3_02_cobertura.png", dpi=150, bbox_inches="tight"); plt.show()
''')

md(r"""
## 5 · Cruce suelo × cobertura: el CN de cada polígono
El **número de curva** va de 30 (casi todo se infiltra) a 100 (todo escurre: agua o techo). Se lee en una tabla
con dos entradas, cobertura y grupo de suelo, para **humedad antecedente normal (AMC II)**.

Tabla del curso, adaptada de la del NRCS (TR-55, 1986) a las coberturas de Manabí. Para las **mezclas** se usa el
promedio de las dos coberturas (se supone mitad y mitad).

| Cobertura | Equivalente NRCS | A | B | C | D |
|---|---|---|---|---|---|
| Bosque natural | Bosque, condición buena | 30 | 55 | 70 | 77 |
| Bosque natural intervenido | Bosque, condición regular | 36 | 60 | 73 | 79 |
| Vegetación arbustiva | Matorral, condición regular | 35 | 56 | 70 | 77 |
| Pastos plantados | Pasto, condición buena | 39 | 61 | 74 | 80 |
| Pastos naturales | Pasto, condición regular | 49 | 69 | 79 | 84 |
| Cultivos de ciclo corto | Cultivo en hileras, condición buena | 67 | 78 | 85 | 89 |
| Arboricultura · Frutales · Café · Cacao | Huerto o bosque con pasto, regular | 43 | 65 | 76 | 82 |
| Asentamiento poblado | Residencial, 65 % impermeable | 77 | 85 | 90 | 92 |
| Áreas en proceso de erosión | Pasto, condición mala | 68 | 79 | 86 | 89 |
| Áreas erosionadas | Suelo desnudo | 77 | 86 | 91 | 94 |
| Cuerpos de agua · Camaroneras | Agua | 100 | 100 | 100 | 100 |
| Salinas | Superficie casi impermeable | 98 | 98 | 98 | 98 |
""")
code(r'''
CN_TABLA = {
    "Bosque natural": (30, 55, 70, 77), "Bosque natural intervenido": (36, 60, 73, 79),
    "Vegetación arbustiva": (35, 56, 70, 77), "Pastos plantados": (39, 61, 74, 80),
    "Pastos naturales": (49, 69, 79, 84), "Cultivos de ciclo corto": (67, 78, 85, 89),
    "Arboricultura": (43, 65, 76, 82), "Frutales": (43, 65, 76, 82), "Café": (43, 65, 76, 82), "Cacao": (43, 65, 76, 82),
    "Asentamiento poblado": (77, 85, 90, 92), "Areas en proceso de erosión": (68, 79, 86, 89),
    "Areas erosionadas": (77, 86, 91, 94), "Cuerpos de agua": (100,) * 4, "Camaroneras": (100,) * 4, "Salinas": (98,) * 4}
def cn(cobertura, g):
    j = "ABCD".index(g); partes = [p.strip() for p in cobertura.split(" - ")]
    faltan = [p for p in partes if p not in CN_TABLA]
    if faltan: raise KeyError(f"Cobertura sin CN en la tabla: {faltan}. Agrégala a CN_TABLA.")
    return np.mean([CN_TABLA[p][j] for p in partes])
X = gpd.overlay(COB[["cobertura", "geometry"]], SUE[["grupo", "orden", "geometry"]], how="intersection", keep_geom_type=True)
X["area_km2"] = X.area / 1e6
X["CN"] = [cn(c, g) for c, g in zip(X.cobertura, X.grupo)]
print(f"Área cruzada: {X.area_km2.sum():.1f} de {A_km2:.1f} km² ({100 * X.area_km2.sum() / A_km2:.1f} %)")
fig, ax = plt.subplots(figsize=(8, 7))
X.plot(ax=ax, column="CN", cmap="RdYlBu_r", vmin=40, vmax=100, legend=True, ec="none", legend_kwds={"label": "CN (AMC II)", "shrink": 0.8})
cuenca.boundary.plot(ax=ax, color="k", lw=1.2)
ax.set_title(f"Número de curva por polígono · {CUENCA}", fontweight="bold")
ax.set_aspect("equal"); ax.ticklabel_format(style="plain"); ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
plt.tight_layout(); plt.savefig("salidas/P2p3_03_mapa_cn.png", dpi=150); plt.show()
''')

md(r"""
## 6 · CN ponderado de la cuenca
$$CN = \frac{\sum_i A_i\,CN_i}{\sum_i A_i}$$
✍️ **Antes de ejecutar la celda siguiente:** con la tabla resumida (combinaciones cobertura × grupo que se imprime
abajo, ordenadas por área), calcula el CN ponderado a mano con **las seis primeras filas** y escríbelo en
`CN_MANO`. Compara después con el CN de toda la cuenca.

**Humedad antecedente.** El CN de la tabla es para condición normal (AMC II). Si el suelo está seco (AMC I) o ya
saturado por lluvias de los días anteriores (AMC III, típico de un invierno con El Niño):
$$CN_I = \frac{4{,}2\,CN_{II}}{10 - 0{,}058\,CN_{II}} \qquad CN_{III} = \frac{23\,CN_{II}}{10 + 0{,}13\,CN_{II}}$$
""")
code(r'''
R = X.groupby(["cobertura", "grupo"]).agg(area_km2=("area_km2", "sum"), CN=("CN", "first")).sort_values("area_km2", ascending=False).reset_index()
R["A × CN"] = R.area_km2 * R.CN
R6 = R.head(6)
display(R.head(12).round(1).rename(columns={"cobertura": "Cobertura", "grupo": "Grupo", "area_km2": "Área (km²)"}))
CN6 = R6["A × CN"].sum() / R6.area_km2.sum()
CN2 = R["A × CN"].sum() / R.area_km2.sum()
CN1 = 4.2 * CN2 / (10 - 0.058 * CN2); CN3 = 23 * CN2 / (10 + 0.13 * CN2)
print(f"CN con las 6 primeras filas ({100 * R6.area_km2.sum() / R.area_km2.sum():.0f} % del área): {CN6:.1f}")
print(f"CN ponderado de toda la cuenca (AMC II): {CN2:.1f} · AMC I: {CN1:.1f} · AMC III: {CN3:.1f}")
if CN_MANO is not None: print(f"Tu CN a mano: {CN_MANO:.1f} · diferencia con el de 6 filas: {CN_MANO - CN6:+.1f}")
else: print("✍️  Escribe tu CN a mano en CN_MANO para compararlo.")
por_cob = X.groupby("cobertura").apply(lambda d: (d.CN * d.area_km2).sum() / d.area_km2.sum())
aporte = X.groupby("cobertura").apply(lambda d: (d.CN * d.area_km2).sum()) / X.area_km2.sum()
print("Coberturas que más aportan al CN (puntos de CN):", ", ".join(f"{k} ({v:.1f})" for k, v in aporte.sort_values(ascending=False).head(3).items()))
''')

md(r"""
## 7 · Lluvia efectiva para T = 10, 25 y 100 años
$$S = \frac{25\,400}{CN} - 254 \;\text{(mm)} \qquad I_a = \lambda S \qquad
P_e = \frac{(P - I_a)^2}{P - I_a + S}\;\;\text{si } P > I_a \text{, si no } P_e = 0$$
- **S:** retención potencial máxima, lo más que la cuenca podría «tragarse».
- **Ia:** abstracción inicial: lo que se pierde antes de que empiece a escurrir (follaje, charcos, primeros mm de infiltración).

> **Analogía.** La cuenca es una esponja dentro de un balde. Primero la esponja se moja sin soltar nada (Ia); luego
> empieza a gotear, cada vez más, mientras se acerca a su límite (S). Una esponja chica (CN alto) gotea pronto.

✍️ **Antes de ejecutar la celda siguiente:** con tu CN (AMC II) y P₂₄ de 25 años (impresa en la sección 2),
calcula S, Ia y **Pe₂₅** a mano; escríbela en `PE25_MANO`.
""")
code(r'''
def S_mm(CN): return 25400 / CN - 254
def Pe(P, CN, lam=LAMBDA):
    S = S_mm(CN); Ia = lam * S; P = np.asarray(P, float)
    return np.where(P > Ia, (P - Ia) ** 2 / (P - Ia + S), 0.0)
S2 = S_mm(CN2); Ia2 = LAMBDA * S2
print(f"S = {S2:.1f} mm · Ia = {Ia2:.1f} mm  (CN = {CN2:.1f}, AMC II)")
filas = []
for T in T_DISENO:
    P = PT24(T)
    filas.append((T, P, float(Pe(P, CN1)), float(Pe(P, CN2)), float(Pe(P, CN3))))
PE = pd.DataFrame(filas, columns=["T (años)", "P24 (mm)", "Pe AMC I (mm)", "Pe AMC II (mm)", "Pe AMC III (mm)"])
PE["C = Pe/P (AMC II)"] = PE["Pe AMC II (mm)"] / PE["P24 (mm)"]
display(PE.round(2))
pe25 = float(Pe(PT24(25), CN2))
if PE25_MANO is not None: print(f"Tu Pe₂₅ a mano: {PE25_MANO:.1f} mm · cuaderno: {pe25:.1f} mm · diferencia {PE25_MANO - pe25:+.1f} mm")
else: print("✍️  Escribe tu Pe₂₅ a mano en PE25_MANO para compararla.")
fig, ax = plt.subplots(figsize=(8, 5))
Pg = np.linspace(0, max(250, 1.3 * PT24(100)), 200)
for cnv, lab, c in [(CN1, "AMC I (seco)", "#F2A65A"), (CN2, "AMC II (normal)", "#1F6F8B"), (CN3, "AMC III (húmedo)", "#12263A")]:
    ax.plot(Pg, Pe(Pg, cnv), color=c, lw=2, label=f"{lab} · CN {cnv:.0f}")
for T in T_DISENO:
    ax.plot(PT24(T), Pe(PT24(T), CN2), "o", color="#B3541A"); ax.annotate(f"T={T}", (PT24(T), Pe(PT24(T), CN2)), xytext=(4, -12), textcoords="offset points", fontsize=8)
ax.plot(Pg, Pg, color="0.7", ls=":", label="Pe = P (todo escurre)")
ax.set_xlabel("Lluvia P (mm)"); ax.set_ylabel("Lluvia efectiva Pe (mm)"); ax.grid(alpha=0.3); ax.legend(frameon=False)
ax.set_title(f"Lluvia efectiva según el número de curva · {CUENCA}", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p3_04_pe_vs_p.png", dpi=150); plt.show()
''')

md(r"""
## 8 · Hietogramas efectivos de 24 horas
La ecuación de Pe se aplica a la **lluvia acumulada** hora a hora: al principio todo se pierde (Ia), y cada hora
escurre una fracción mayor. La diferencia entre horas da el hietograma efectivo, que es la entrada del
hidrograma del paso 4.
""")
code(r'''
HE = {}
fig, axs = plt.subplots(1, len(T_DISENO), figsize=(13, 4), sharey=True)
for ax, T in zip(axs, T_DISENO):
    h = hietograma(T); Pac = h.cumsum(); Peac = pd.Series(Pe(Pac.values, CN2), index=h.index)
    he = Peac.diff().fillna(Peac.iloc[0]); HE[f"P_T{T}"] = h; HE[f"Pe_T{T}"] = he
    ax.bar(h.index - 0.5, h, width=1, align="edge", color="#C9D6DE", label="Pérdidas")
    ax.bar(h.index - 0.5, he, width=1, align="edge", color="#1F6F8B", label="Lluvia efectiva")
    ax.set_title(f"T = {T} años · Pe = {he.sum():.0f} de {h.sum():.0f} mm", fontweight="bold"); ax.set_xlabel("Hora")
    ax.set_xticks([0, 6, 12, 18, 24]); ax.grid(axis="y", alpha=0.3)
    ini = he[he > 0].index.min(); print(f"T={T}: empieza a escurrir en la hora {ini} · Pe en la hora pico {he.max():.1f} mm")
axs[0].set_ylabel("mm/h"); axs[0].legend(frameon=False)
fig.suptitle(f"Hietogramas efectivos de diseño · {CUENCA} · CN {CN2:.0f} (AMC II)", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p3_05_hietogramas_efectivos.png", dpi=150); plt.show()
HE = pd.DataFrame(HE); HE.index.name = "hora"
''')

md("## 9 · Expediente del capítulo 2 y descarga")
code(r'''
f = "P2_paso3 · NRCS TR-55 (1986) adaptado · capas de suelos y cobertura (datos-manabi)"
exp = [("2.5", "Regla de grupo hidrológico", "textura (1 A · 2–3 B · 4 C · 5 D); drenaje 4 → D; sin suelo → D", "", "celda 3"),
       ("2.5", "Área cruzada suelo × cobertura", round(X.area_km2.sum(), 1), "km²", f)]
exp += [("2.5", f"Grupo {g}", round(r["%"], 1), "% del área", f) for g, r in tg.iterrows()]
exp += [("2.5", f"Cobertura: {k}", round(r["%"], 1), "% del área", f) for k, r in tc_.head(6).iterrows()]
exp += [("2.5", "CN ponderado AMC II", round(CN2, 1), "—", f), ("2.5", "CN AMC I", round(CN1, 1), "—", f),
        ("2.5", "CN AMC III", round(CN3, 1), "—", f), ("2.5", "CN a mano (6 combinaciones)", CN_MANO if CN_MANO is not None else "", "—", "estudiante"),
        ("2.5", "Retención potencial S", round(S2, 1), "mm", f), ("2.5", "Abstracción inicial Ia", round(Ia2, 1), "mm", f),
        ("2.5", "λ", LAMBDA, "—", "celda 1"),
        ("2.5", "Pe T=25 a mano", PE25_MANO if PE25_MANO is not None else "", "mm", "estudiante")]
for _, r in PE.iterrows():
    T = int(r["T (años)"])
    exp += [("2.5", f"Pe T={T} AMC II", round(r["Pe AMC II (mm)"], 1), "mm", f),
            ("2.5", f"Pe T={T} AMC III", round(r["Pe AMC III (mm)"], 1), "mm", f),
            ("2.5", f"Coeficiente de escorrentía T={T}", round(r["C = Pe/P (AMC II)"], 3), "—", f)]
EXP = pd.DataFrame([("2",) + x for x in exp], columns=["capitulo", "apartado", "campo", "valor", "unidad", "fuente"])
EXP.to_csv(f"salidas/expediente_P2p3_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
HE.to_csv(f"salidas/hietogramas_efectivos_{CUENCA}_{SLUG}.csv", encoding="utf-8-sig")
R.to_csv(f"salidas/cn_combinaciones_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
X.to_file(f"salidas/cn_{CUENCA}_{SLUG}.gpkg", layer="cn", driver="GPKG")
import shutil
paquete = shutil.make_archive(f"Practica2_Paso3_{CUENCA}_{SLUG}", "zip", "salidas")
print("✅ Paquete:", paquete)
try:
    from google.colab import files; files.download(paquete)
except ImportError:
    print("Descárgalo desde el panel de archivos de Colab.")
EXP
''')

md(r"""
---
## Para tu capítulo 2 · apartado 2.5 (cinco líneas debajo de cada figura)
1. **Suelos.** ¿Qué grupo domina y dónde? ¿Qué regla usaste para asignarlo y qué límite tiene?
2. **Cobertura y CN.** ¿Qué coberturas suben el CN de tu cuenca? Si el bosque natural se convirtiera en pasto,
   ¿cuánto subiría el CN? (cámbialo en la tabla y vuelve a ejecutar)
3. **Lluvia efectiva.** De la lluvia de 25 años, ¿qué porcentaje escurre? ¿Coincide tu cálculo a mano?
4. **Humedad antecedente.** ¿Cuánto cambia Pe entre AMC II y AMC III? ¿Qué condición esperarías en marzo de un
   año con El Niño y qué significa para el diseño?
""")
save(sys.argv[1] if len(sys.argv) > 1 else "P2_paso3_numero_curva.ipynb")
