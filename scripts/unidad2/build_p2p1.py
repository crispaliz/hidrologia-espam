import nbformat as nbf, sys
C = []
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip("\n")))
def code(s): C.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# Práctica 2 · Paso 1 — Precipitación media de tu cuenca, 1995–2014
### Hidrología (1CIA-502) · Ingeniería Ambiental · ESPAM MFL · Unidad II
**Docente:** Ing. Cristian Paliz Acosta, MSc.

Una estación mide la lluvia en un punto de unos 200 cm². Tu cuenca tiene cientos de km². Este cuaderno
responde: **¿cuánta lluvia cae, en promedio, sobre toda tu cuenca?** con los tres métodos clásicos, y luego
mira cómo se reparte esa lluvia en el tiempo (hietogramas).

| Bloque | Qué haces | Producto |
|---|---|---|
| 3 | Ubicar las estaciones dentro y alrededor de tu cuenca | Mapa y tabla de estaciones |
| 4 | **Media aritmética** (primero a mano) | P media 1 |
| 5 | **Polígonos de Thiessen** | Pesos por estación · P media 2 |
| 6 | **Isoyetas** | Mapa de isoyetas · P media 3 |
| 7 | Comparar los tres métodos | ¿Cuál usar y por qué? |
| 8 | Serie anual 1995–2014 | Años secos, húmedos y El Niño |
| 9 | Hietograma mensual medio | Régimen de lluvias |
| 10 | Hietograma de la tormenta mayor | Hietograma diario y curva de masa |
| 11 | Expediente del capítulo 2 | `expediente_P2p1_….csv` |

**Mano antes que modelo:** en la sección 4 calculas la media aritmética con la tabla impresa antes de que
el cuaderno la calcule.

`Archivo → Guardar una copia en Drive`, llena **solo la celda 1** y ejecuta
`Entorno de ejecución → Reiniciar sesión y ejecutar todo`.
""")

md(r"""
## 1 · CONFIGURACIÓN ✍️ (única celda que editas)
- **CUENCA:** la misma del capítulo 1.
- **USAR_MI_CUENCA:** `True` para subir tu `cuenca_<cuenca>_<estudiante>.gpkg` del paso 2 de la Práctica 1
  (está en su ZIP). Así trabajas tu cuenca o subcuenca exacta. `False` usa el límite oficial.
- **RADIO_KM:** estaciones vecinas que entran a Thiessen e isoyetas (fuera de la cuenca también informan).
- **P_MEDIA_MANO:** tu media aritmética calculada a mano en la sección 4 (mm/año).
- **INTERVALO_ISOYETAS:** separación entre isoyetas (mm).
""")
code(r"""
ESTUDIANTE = "Apellidos Nombres"
CUENCA     = "Carrizal"      # Ayampe · Carrizal · Chone · Jama · Jipijapa · Portoviejo
USAR_MI_CUENCA = False
RADIO_KM   = 20
P_MEDIA_MANO = None          # mm/año, después de la sección 4
INTERVALO_ISOYETAS = 200     # mm
PERIODO    = (1995, 2014)
DATOS = "https://raw.githubusercontent.com/crispaliz/datos-manabi/main"
""")

md("## 2 · Cargar estaciones, lluvia diaria y el límite de tu cuenca")
code(r"""
import io, os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib.pyplot as plt
from shapely.geometry import MultiPoint
from shapely.ops import voronoi_diagram
import warnings; warnings.filterwarnings("ignore")
SLUG = unicodedata.normalize("NFKD", ESTUDIANTE).encode("ascii", "ignore").decode().replace(" ", "_")
os.makedirs("salidas", exist_ok=True)
EST = pd.read_csv(f"{DATOS}/precipitacion/estaciones_lluvia_diaria.csv")
LL  = pd.read_csv(f"{DATOS}/precipitacion/lluvia_diaria_1964_2018.csv", parse_dates=["fecha"], index_col="fecha")
if USAR_MI_CUENCA:
    from google.colab import files
    print("Sube tu cuenca_<cuenca>_<estudiante>.gpkg del paso 2:"); up = files.upload()
    nombre = list(up)[0]; open(nombre, "wb").write(up[nombre])
    cuenca = gpd.read_file(nombre, layer="cuenca").to_crs(32717)
else:
    cuenca = gpd.read_file(f"{DATOS}/cuencas_oficiales.geojson").query("cuenca == @CUENCA").to_crs(32717)
CU = cuenca.union_all() if hasattr(cuenca, "union_all") else cuenca.unary_union   # compatible con geopandas < 1.0
A_km2 = CU.area / 1e6
LL = LL.loc[f"{PERIODO[0]}-01-01":f"{PERIODO[1]}-12-31"]
NA = PERIODO[1] - PERIODO[0] + 1
gest = gpd.GeoDataFrame(EST, geometry=gpd.points_from_xy(EST.x_utm, EST.y_utm), crs=32717)
gest["dentro"] = gest.within(CU)
gest["dist_km"] = gest.distance(CU) / 1000
gest["P_anual"] = [LL[c].sum() / NA for c in gest.codigo]
print(f"✅ Cuenca {CUENCA}: {A_km2:,.1f} km² · {len(gest)} estaciones disponibles · lluvia diaria {PERIODO[0]}–{PERIODO[1]}".replace(",", " "))
""")

md(r"""
## 3 · Las estaciones de tu cuenca
Las estaciones **dentro** de la cuenca entran a la media aritmética. Las de **alrededor** (hasta `RADIO_KM`)
también entran a Thiessen e isoyetas: la lluvia no se detiene en la divisoria, y una estación vecina dice
mucho del borde de tu cuenca.

⚠️ Las series del INAMHI de 1964–2018 tienen control de calidad y **relleno** (Climatol con apoyo de CHIRPS):
los días rellenados no son observaciones y no se distinguen en el archivo.
""")
code(r"""
usa = gest[gest.dentro | (gest.dist_km <= RADIO_KM)].copy()
dentro = usa[usa.dentro]
tabla = usa.sort_values(["dentro", "P_anual"], ascending=[False, False])[["codigo", "estacion", "altitud_m", "dentro", "dist_km", "P_anual"]]
tabla["dist_km"] = tabla.dist_km.round(1); tabla["P_anual"] = tabla.P_anual.round(0)
tabla.columns = ["Código", "Estación", "Altitud (m)", "Dentro", "Distancia al borde (km)", f"P media anual {PERIODO[0]}–{PERIODO[1]} (mm)"]
display(tabla.reset_index(drop=True))
fig, ax = plt.subplots(figsize=(8, 7))
cuenca.boundary.plot(ax=ax, color="k", lw=1.4)
gpd.GeoSeries([CU.buffer(RADIO_KM * 1000)], crs=32717).boundary.plot(ax=ax, color="0.6", ls="--", lw=0.8)
sc = ax.scatter(usa.geometry.x, usa.geometry.y, c=usa.P_anual, cmap="YlGnBu", s=80, ec="k", zorder=3)
plt.colorbar(sc, label="P media anual (mm)", shrink=0.8)
for _, r in usa.iterrows():
    ax.annotate(f"{r.codigo}\n{r.P_anual:.0f}", (r.geometry.x, r.geometry.y), fontsize=7, xytext=(4, 4), textcoords="offset points")
ax.set_title(f"Estaciones de lluvia · {CUENCA} · {len(dentro)} dentro, {len(usa) - len(dentro)} alrededor", fontweight="bold")
ax.set_aspect("equal"); ax.ticklabel_format(style="plain"); ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
plt.tight_layout(); plt.savefig("salidas/P2p1_01_estaciones.png", dpi=150); plt.show()
if len(dentro) < 2:
    print(f"⚠️  Solo {len(dentro)} estación dentro de la cuenca: la media aritmética no representa la cuenca. Mira Thiessen e isoyetas.")
""")

md(r"""
## 4 · Media aritmética
$$\bar P = \frac{1}{n}\sum_{i=1}^{n} P_i$$
Todas las estaciones **dentro** de la cuenca pesan lo mismo. Funciona si las estaciones están repartidas de
forma pareja y el terreno es plano. Si se amontonan en una zona, esa zona manda.

✍️ **Antes de ejecutar la celda siguiente:** con la tabla de la sección 3 (solo las que dicen `True` en *Dentro*),
calcula la media a mano y escríbela en `P_MEDIA_MANO` (celda 1).
""")
code(r"""
P_arit = dentro.P_anual.mean() if len(dentro) else np.nan
print(f"Media aritmética ({len(dentro)} estaciones dentro): {P_arit:.0f} mm/año")
if P_MEDIA_MANO is not None:
    print(f"Tu cálculo a mano: {P_MEDIA_MANO:.0f} mm/año · diferencia {P_arit - P_MEDIA_MANO:+.0f} mm")
else:
    print("✍️  Escribe tu media a mano en P_MEDIA_MANO para compararla.")
""")

md(r"""
## 5 · Polígonos de Thiessen
Cada punto de la cuenca toma la lluvia de **la estación más cercana**. Las mediatrices entre estaciones vecinas
dividen la cuenca en polígonos; el peso de cada estación es la fracción del área de la cuenca que le toca:
$$\bar P = \sum_{i} \frac{A_i}{A}\,P_i$$
Es como repartir un barrio entre las tiendas: cada casa compra en la tienda más cercana, y cada tienda
«representa» a las casas de su zona.
""")
code(r"""
pts = MultiPoint(list(usa.geometry))
vor = voronoi_diagram(pts, envelope=CU.buffer(RADIO_KM * 2000))
pol = []
for celda in vor.geoms:
    k = usa.geometry.apply(lambda p: celda.contains(p)).values.nonzero()[0]
    if len(k): pol.append((usa.iloc[k[0]].codigo, celda.intersection(CU)))
TH = gpd.GeoDataFrame(pol, columns=["codigo", "geometry"], crs=32717)
TH = TH[~TH.is_empty]
TH["area_km2"] = TH.area / 1e6
TH = TH.merge(usa[["codigo", "estacion", "P_anual", "dentro"]], on="codigo")
TH["peso"] = TH.area_km2 / TH.area_km2.sum()
TH["aporte_mm"] = TH.peso * TH.P_anual
P_thi = TH.aporte_mm.sum()
fig, ax = plt.subplots(figsize=(8, 7))
TH.plot(ax=ax, column="P_anual", cmap="YlGnBu", ec="k", lw=0.8, legend=True, legend_kwds={"label": "P media anual (mm)", "shrink": 0.8})
ax.scatter(usa.geometry.x, usa.geometry.y, c="crimson", s=25, zorder=3)
for _, r in TH.iterrows():
    c = r.geometry.representative_point()
    ax.annotate(f"{r.codigo}\n{100 * r.peso:.0f} %", (c.x, c.y), fontsize=7, ha="center")
ax.set_title(f"Polígonos de Thiessen · P media = {P_thi:.0f} mm/año", fontweight="bold")
ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
b = CU.bounds; ax.set_xlim(b[0] - 3000, b[2] + 3000); ax.set_ylim(b[1] - 3000, b[3] + 3000)
ax.set_aspect("equal"); ax.ticklabel_format(style="plain")
plt.tight_layout(); plt.savefig("salidas/P2p1_02_thiessen.png", dpi=150); plt.show()
t = TH.sort_values("peso", ascending=False)[["codigo", "estacion", "dentro", "area_km2", "peso", "P_anual", "aporte_mm"]].round(3)
t.columns = ["Código", "Estación", "Dentro", "Área (km²)", "Peso", "P (mm)", "Peso × P (mm)"]
display(t.reset_index(drop=True))
print(f"Suma de pesos = {TH.peso.sum():.3f} · P media de Thiessen = {P_thi:.0f} mm/año")
fuera = TH[~TH.dentro].peso.sum()
if fuera > 0: print(f"Las estaciones de fuera de la cuenca pesan {100 * fuera:.0f} % del área.")
""")

md(r"""
## 6 · Isoyetas
Una **isoyeta** une puntos de igual lluvia, como una curva de nivel une puntos de igual altura. Se trazan
interpolando entre estaciones; luego se mide el área entre cada par de isoyetas y se pondera:
$$\bar P = \sum_{j} \frac{A_j}{A}\,\frac{P_j + P_{j+1}}{2}$$
Es el método que mejor recoge el efecto del relieve, **si** el que traza las isoyetas conoce la cuenca. Aquí
se interpolan en forma lineal entre estaciones (como al trazarlas a mano) en una malla de 500 m.
""")
code(r"""
from scipy.interpolate import griddata
import shapely
xs, ys = usa.geometry.x.values, usa.geometry.y.values
b = CU.bounds; dx = 500
gx, gy = np.meshgrid(np.arange(b[0], b[2] + dx, dx), np.arange(b[1], b[3] + dx, dx))
lin = griddata((xs, ys), usa.P_anual.values, (gx, gy), method="linear")
cer = griddata((xs, ys), usa.P_anual.values, (gx, gy), method="nearest")
Z = np.where(np.isnan(lin), cer, lin)
dentro_m = shapely.contains_xy(CU, gx, gy)
P_iso_malla = Z[dentro_m].mean()
niv = np.arange(np.floor(np.nanmin(Z) / INTERVALO_ISOYETAS) * INTERVALO_ISOYETAS,
                np.nanmax(Z) + INTERVALO_ISOYETAS, INTERVALO_ISOYETAS)
fig, ax = plt.subplots(figsize=(8, 7))
Zm = np.where(dentro_m, Z, np.nan)
cf = ax.contourf(gx, gy, Zm, levels=niv, cmap="YlGnBu")
cs = ax.contour(gx, gy, Zm, levels=niv, colors="k", linewidths=0.6)
ax.clabel(cs, fmt="%d", fontsize=7)
cuenca.boundary.plot(ax=ax, color="k", lw=1.2)
ax.scatter(xs, ys, c="crimson", s=20, zorder=3)
plt.colorbar(cf, label="P media anual (mm)", shrink=0.8)
ax.set_xlim(b[0] - 3000, b[2] + 3000); ax.set_ylim(b[1] - 3000, b[3] + 3000)
ax.set_title(f"Isoyetas cada {INTERVALO_ISOYETAS} mm · P media = {P_iso_malla:.0f} mm/año", fontweight="bold")
ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
ax.set_aspect("equal"); ax.ticklabel_format(style="plain")
plt.tight_layout(); plt.savefig("salidas/P2p1_03_isoyetas.png", dpi=150); plt.show()
# Tabla «a mano»: área entre isoyetas consecutivas
vals = Z[dentro_m]; filas = []
for lo, hi in zip(niv[:-1], niv[1:]):
    n = ((vals >= lo) & (vals < hi)).sum()
    if n: filas.append((f"{lo:.0f}–{hi:.0f}", n * dx * dx / 1e6, (lo + hi) / 2))
IB = pd.DataFrame(filas, columns=["Entre isoyetas (mm)", "Área (km²)", "P media de la franja (mm)"])
IB["Peso"] = IB["Área (km²)"] / IB["Área (km²)"].sum()
IB["Peso × P (mm)"] = IB.Peso * IB["P media de la franja (mm)"]
P_iso = IB["Peso × P (mm)"].sum()
display(IB.round(3))
print(f"P media por franjas de isoyetas = {P_iso:.0f} mm/año (con la malla completa: {P_iso_malla:.0f} mm/año)")
""")

md("## 7 · Comparar los tres métodos")
code(r"""
res = pd.Series({"Media aritmética": P_arit, "Thiessen": P_thi, "Isoyetas": P_iso})
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(res.index, res.values, color=["#C9D6DE", "#1F6F8B", "#12263A"])
for r_, v in zip(bars, res.values):
    ax.text(r_.get_x() + r_.get_width() / 2, v, f"{v:.0f}", ha="center", va="bottom")
ax.set_ylabel(f"P media anual {PERIODO[0]}–{PERIODO[1]} (mm)"); ax.grid(axis="y", alpha=0.3)
ax.set_title(f"Precipitación media de {CUENCA} por tres métodos", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p1_04_comparacion.png", dpi=150); plt.show()
dif = 100 * (res.max() - res.min()) / res.mean()
print(res.round(0).to_string()); print(f"Rango entre métodos: {dif:.0f} % de la media.")
print("Lectura: si los tres se parecen (< 10 %), la red es pareja y la lluvia homogénea. Si difieren, pregúntate"
      " dónde están las estaciones y dónde llueve más.")
""")

md(r"""
## 8 · Serie anual de la precipitación media (Thiessen)
Los pesos de Thiessen se aplican a la lluvia de **cada año**. Así ves la variabilidad: años secos, años
húmedos y el efecto de El Niño 1997–98.
""")
code(r"""
W = TH.set_index("codigo").peso
Pd = (LL[W.index] * W).sum(axis=1)                      # lluvia media diaria de la cuenca (mm/día)
Pa = Pd.groupby(Pd.index.year).sum()
fig, ax = plt.subplots(figsize=(11, 4.5))
col = ["#B3541A" if y in (1997, 1998) else "#1F6F8B" for y in Pa.index]
ax.bar(Pa.index, Pa.values, color=col)
ax.axhline(Pa.mean(), color="k", ls="--", lw=1, label=f"media {Pa.mean():.0f} mm")
ax.set_ylabel("P anual de la cuenca (mm)"); ax.legend(frameon=False); ax.grid(axis="y", alpha=0.3)
ax.set_xticks(Pa.index); ax.set_xticklabels(Pa.index, rotation=90)
ax.set_title(f"Precipitación anual media de {CUENCA} · naranja: El Niño 1997–98", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p1_05_serie_anual.png", dpi=150); plt.show()
cv = Pa.std() / Pa.mean()
print(f"Año más lluvioso: {Pa.idxmax()} ({Pa.max():.0f} mm) · más seco: {Pa.idxmin()} ({Pa.min():.0f} mm) · "
      f"coeficiente de variación {cv:.2f}")
print(f"{Pa.max() / Pa.mean():.1f} veces la media en el año más lluvioso.")
""")

md(r"""
## 9 · Hietograma mensual medio: el régimen de lluvias
Un **hietograma** es un gráfico de barras de la lluvia en el tiempo: cada barra es la lámina caída en un
intervalo (mes, día, hora). Este es el hietograma mensual medio de tu cuenca.
""")
code(r"""
Pm = Pd.groupby([Pd.index.year, Pd.index.month]).sum().groupby(level=1).mean()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(range(1, 13), Pm.values, color=["#1F6F8B" if v >= 60 else "#F2A65A" for v in Pm.values])
ax.axhline(60, color="k", lw=0.8, ls=":"); ax.text(12.4, 63, "60 mm", ha="right", fontsize=8)
ax.set_xticks(range(1, 13)); ax.set_xticklabels(list("EFMAMJJASOND")); ax.set_ylabel("P media mensual (mm)")
ax.set_title(f"Hietograma mensual medio · {CUENCA} · {PERIODO[0]}–{PERIODO[1]}", fontweight="bold"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("salidas/P2p1_06_hietograma_mensual.png", dpi=150); plt.show()
ene_may = Pm.loc[1:5].sum() / Pm.sum()
print(f"Enero a mayo concentra el {100 * ene_may:.0f} % de la lluvia del año; meses secos (< 60 mm): {(Pm < 60).sum()}")
""")

md(r"""
## 10 · Hietograma de la tormenta mayor del periodo
Se busca el episodio de **5 días** con más lluvia sobre la cuenca. El hietograma muestra la lluvia de cada día;
la **curva de masa** (lluvia acumulada) muestra cuándo cayó la mayor parte. Para diseñar obras se necesitan
hietogramas horarios: los construirás en la lluvia de diseño (Unidad II).
""")
code(r"""
P5 = Pd.rolling(5).sum(); fin = P5.idxmax(); ini = fin - pd.Timedelta(days=4)
ev = Pd.loc[ini - pd.Timedelta(days=3): fin + pd.Timedelta(days=3)]
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(ev.index, ev.values, color=["#12263A" if ini <= d <= fin else "#C9D6DE" for d in ev.index], width=0.8)
ax.set_ylabel("Lluvia media de la cuenca (mm/día)"); ax.grid(axis="y", alpha=0.3)
acum = Pd.loc[ini:fin].cumsum()
ax2 = ax.twinx(); ax2.plot(acum.index, acum.values, color="#B3541A", lw=2, marker="o", ms=4)
ax2.set_ylabel("Lluvia acumulada en la tormenta (mm)", color="#B3541A"); ax2.set_ylim(0, None)
ax.set_title(f"Hietograma diario de la tormenta mayor · {ini:%d/%m/%Y}–{fin:%d/%m/%Y} · {P5.max():.0f} mm en 5 días", fontweight="bold")
fig.autofmt_xdate(); plt.tight_layout(); plt.savefig("salidas/P2p1_07_hietograma_tormenta.png", dpi=150); plt.show()
print(f"Día más lluvioso de la tormenta: {ev.idxmax():%d/%m/%Y} con {ev.max():.0f} mm · "
      f"día más lluvioso de todo el periodo: {Pd.idxmax():%d/%m/%Y} con {Pd.max():.0f} mm")
print(f"La tormenta equivale al {100 * P5.max() / Pa.mean():.0f} % de la lluvia de un año medio.")
""")

md("## 11 · Expediente del capítulo 2 y descarga")
code(r"""
f = f"P2_paso1 · INAMHI {PERIODO[0]}–{PERIODO[1]}"
exp = [("2.1", "Cuenca", CUENCA, "", "celda 1"),
       ("2.1", "Límite usado", "propio (paso 2)" if USAR_MI_CUENCA else "oficial", "", "celda 1"),
       ("2.1", "Área de la cuenca", round(A_km2, 1), "km²", f),
       ("2.1", "Periodo", f"{PERIODO[0]}–{PERIODO[1]}", "", "celda 1"),
       ("2.1", "Estaciones dentro de la cuenca", len(dentro), "n.º", f),
       ("2.1", "Estaciones usadas en Thiessen e isoyetas", len(usa), "n.º", f),
       ("2.1", "P media aritmética", round(P_arit, 0), "mm/año", f),
       ("2.1", "P media aritmética a mano", P_MEDIA_MANO if P_MEDIA_MANO is not None else "", "mm/año", "estudiante"),
       ("2.1", "P media Thiessen", round(P_thi, 0), "mm/año", f),
       ("2.1", "P media isoyetas", round(P_iso, 0), "mm/año", f),
       ("2.1", "Rango entre métodos", round(dif, 1), "%", f),
       ("2.1", "Peso de estaciones fuera de la cuenca (Thiessen)", round(100 * fuera, 1), "%", f),
       ("2.2", "Año más lluvioso", f"{Pa.idxmax()} ({Pa.max():.0f} mm)", "", f),
       ("2.2", "Año más seco", f"{Pa.idxmin()} ({Pa.min():.0f} mm)", "", f),
       ("2.2", "Coeficiente de variación anual", round(cv, 2), "—", f),
       ("2.2", "Lluvia de enero a mayo", round(100 * ene_may, 0), "%", f),
       ("2.2", "Meses secos (< 60 mm)", int((Pm < 60).sum()), "meses", f),
       ("2.3", "Tormenta mayor de 5 días", f"{ini:%Y-%m-%d} a {fin:%Y-%m-%d}", "", f),
       ("2.3", "Lluvia de la tormenta mayor", round(P5.max(), 0), "mm", f),
       ("2.3", "Lluvia diaria máxima del periodo", round(Pd.max(), 0), "mm", f)]
exp += [("2.1", f"Peso Thiessen {r.codigo} {r.estacion}", round(r.peso, 3), "—", f) for _, r in TH.sort_values("peso", ascending=False).iterrows()]
EXP = pd.DataFrame([("2",) + x for x in exp], columns=["capitulo", "apartado", "campo", "valor", "unidad", "fuente"])
EXP.to_csv(f"salidas/expediente_P2p1_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
Pd.rename("P_media_cuenca_mm").to_frame().to_csv(f"salidas/lluvia_media_diaria_{CUENCA}_{SLUG}.csv", encoding="utf-8-sig")
TH.drop(columns="geometry").to_csv(f"salidas/pesos_thiessen_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
TH.to_file(f"salidas/thiessen_{CUENCA}_{SLUG}.gpkg", layer="thiessen", driver="GPKG")
import shutil
paquete = shutil.make_archive(f"Practica2_Paso1_{CUENCA}_{SLUG}", "zip", "salidas")
print("✅ Paquete:", paquete)
try:
    from google.colab import files; files.download(paquete)
except ImportError:
    print("Descárgalo desde el panel de archivos de Colab.")
EXP.head(20)
""")

md(r"""
---
## Para tu capítulo 2 (cinco líneas cada una, debajo de cada figura)
1. **Red de estaciones.** ¿Cuántas estaciones hay dentro de tu cuenca y cómo están repartidas? ¿Qué zona queda sin estación?
2. **Tres métodos.** ¿Cuál dio más y cuál menos? Explica la diferencia con la ubicación de las estaciones y el relieve.
   ¿Cuál usarías para tu cuenca y por qué?
3. **Variabilidad.** ¿Cuántas veces la media llovió en el año más lluvioso? ¿Qué pasó en 1997–98?
4. **Hietogramas.** ¿Qué parte del año concentra la lluvia? En la tormenta mayor, ¿la lluvia cayó repartida o en uno o dos días?
   ¿Qué significa eso para la crecida, con el tiempo de concentración del capítulo 1?
""")
nb = nbf.v4.new_notebook(); nb["cells"] = C
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"provenance": []}}
nbf.write(nb, sys.argv[1] if len(sys.argv) > 1 else "P2_paso1_precipitacion_media.ipynb"); print("ok", len(C))
