import nbformat as nbf
C = []
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip("\n")))
def code(s): C.append(nbf.v4.new_code_cell(s.strip("\n")))
def save(path):
    nb = nbf.v4.new_notebook(); nb["cells"] = C
    nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"provenance": []}}
    nbf.write(nb, path); print("ok", len(C), path)

CONFIG_BASE = r'''
ESTUDIANTE = "Apellidos Nombres"
CUENCA     = "Carrizal"      # Ayampe · Carrizal · Chone · Jama · Jipijapa · Portoviejo
USAR_MI_CUENCA = False       # True: sube tu cuenca_<cuenca>_<estudiante>.gpkg (Práctica 1, paso 2)
RADIO_KM   = 20              # el mismo del paso 1
PERIODO    = (1995, 2014)
DATOS = "https://raw.githubusercontent.com/crispaliz/datos-manabi/main"
'''

# Carga + Thiessen compacto (idéntico al paso 1): produce cuenca, CU, A_km2, LL (todo 1964–2018), W, Pd_all, Pd
CARGA = r'''
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
    print("Sube tu cuenca_<cuenca>_<estudiante>.gpkg del paso 2 de la Práctica 1:"); up = files.upload()
    nombre = list(up)[0]; open(nombre, "wb").write(up[nombre])
    cuenca = gpd.read_file(nombre, layer="cuenca").to_crs(32717)
else:
    cuenca = gpd.read_file(f"{DATOS}/cuencas_oficiales.geojson").query("cuenca == @CUENCA").to_crs(32717)
CU = cuenca.union_all(); A_km2 = CU.area / 1e6
# Pesos de Thiessen, igual que en el paso 1
gest = gpd.GeoDataFrame(EST, geometry=gpd.points_from_xy(EST.x_utm, EST.y_utm), crs=32717)
usa = gest[gest.within(CU) | (gest.distance(CU) <= RADIO_KM * 1000)]
vor = voronoi_diagram(MultiPoint(list(usa.geometry)), envelope=CU.buffer(RADIO_KM * 2000))
pol = []
for celda in vor.geoms:
    k = usa.geometry.apply(lambda p: celda.contains(p)).values.nonzero()[0]
    if len(k): pol.append((usa.iloc[k[0]].codigo, celda.intersection(CU).area))
W = pd.DataFrame(pol, columns=["codigo", "a"]).query("a > 0").set_index("codigo").a
W = W / W.sum()
Pd_all = (LL[W.index] * W).sum(axis=1)                     # lluvia media diaria de la cuenca 1964–2018
Pd = Pd_all.loc[f"{PERIODO[0]}-01-01":f"{PERIODO[1]}-12-31"]
NOMBRE = EST.set_index("codigo").estacion
print(f"✅ Cuenca {CUENCA}: {A_km2:,.1f} km² · {len(W)} estaciones en Thiessen · lluvia diaria 1964–2018".replace(",", " "))
print("Pesos de Thiessen:", ", ".join(f"{c} {w:.2f}" for c, w in W.sort_values(ascending=False).items()))
'''

# Gumbel compacto (lo del paso 2): produce PT24(T), P_D(D_h, T), hietograma(T)
GUMBEL = r'''
FACTOR_24H = 1.13
Pmax = Pd.groupby(Pd.index.year).max()
xm, sx = Pmax.mean(), Pmax.std(ddof=1)
alfa = np.sqrt(6) * sx / np.pi; u = xm - 0.5772 * alfa
def KT(T): return -(np.sqrt(6) / np.pi) * (0.5772 + np.log(np.log(T / (T - 1))))
def PT_diaria(T): return xm + KT(T) * sx
def PT24(T): return FACTOR_24H * PT_diaria(T)
def P_D(D_h, T): return PT24(T) * (np.asarray(D_h, float) * 60 / 1440) ** 0.25      # Dyck–Peschke
def hietograma(T, dur_h=24, dt_h=1):
    D = np.arange(dt_h, dur_h + dt_h, dt_h); inc = np.sort(np.diff(np.r_[0, P_D(D, T)]))[::-1]
    n = len(D); c = (n - 1) // 2; idx = [c]; k = 1          # bloque mayor al centro, luego derecha, izquierda…
    while len(idx) < n:
        if c + k < n: idx.append(c + k)
        if len(idx) < n and c - k >= 0: idx.append(c - k)
        k += 1
    orden = np.zeros(n); orden[idx] = inc
    return pd.Series(orden, index=D, name=f"T{T}")
print(f"Máximos anuales {PERIODO[0]}–{PERIODO[1]}: media {xm:.1f} mm · desviación {sx:.1f} mm · "
      + " · ".join(f"P24(T={T}) = {PT24(T):.0f} mm" for T in (10, 25, 100)))
'''

# Caudal diario en la salida de la cuenca (igual que el paso 3 de la Práctica 1), 1980–2023
CAUDAL = r'''
DQ = f"{DATOS}/caudales"
SAL = pd.read_csv(f"{DQ}/salidas_cuencas.csv").set_index("cuenca")
ESTQ = pd.read_csv(f"{DQ}/estaciones_hidrologicas.csv").set_index("estacion_id")
SIM = pd.read_csv(f"{DQ}/geoglows_simulado_1980_2023.csv", parse_dates=["fecha"], index_col="fecha")
COR = pd.read_csv(f"{DQ}/geoglows_corregido_estaciones_1980_2023.csv", parse_dates=["fecha"], index_col="fecha")
REF = {"Carrizal": "H229", "Chone": "H229", "Portoviejo": "H1081", "Jipijapa": "H272", "Ayampe": "H267", "Jama": None}
EQ = ESTACION_Q if ESTACION_Q else REF[CUENCA]
s_sal = SIM[str(int(SAL.loc[CUENCA, "comid_salida"]))]
if EQ and EQ in COR:
    s_est = SIM[str(int(ESTQ.loc[EQ, "comid_geoglows"]))]
    razon = s_sal.groupby(s_sal.index.month).mean() / s_est.groupby(s_est.index.month).mean()
    Q_all = COR[EQ] * COR.index.month.map(razon).values
    ORIGEN_Q = f"GEOGloWS corregido en {EQ} ({ESTQ.loc[EQ, 'calidad_correccion']}) llevado a la salida"
else:
    Q_all = s_sal.copy(); ORIGEN_Q = "GEOGloWS sin corregir en la salida (no hay estación con corrección aceptable)"
f_area = A_km2 / SAL.loc[CUENCA, "area_oficial_km2"]
Q_all = (Q_all * f_area).rename("Q_m3s")
Qd = Q_all.loc[f"{PERIODO[0]}-01-01":f"{PERIODO[1]}-12-31"].dropna()
print(f"✅ Caudal diario en la salida: {ORIGEN_Q}" + (f" · escalado por área ×{f_area:.2f}" if abs(f_area - 1) > 0.01 else ""))
'''

# CN ponderado (lo del paso 3, sin gráficos)
CNB = r'''
SUE = gpd.read_file(f"{DATOS}/suelos_cobertura/suelos_cuencas.geojson"); COB = gpd.read_file(f"{DATOS}/suelos_cobertura/cobertura_cuencas.geojson")
SUE = gpd.clip((SUE.set_crs(32717, allow_override=True) if SUE.crs is None else SUE).to_crs(32717), CU)
COB = gpd.clip((COB.set_crs(32717, allow_override=True) if COB.crs is None else COB).to_crs(32717), CU)
GT = {1: "A", 2: "B", 3: "B", 4: "C", 5: "D"}
SUE["grupo"] = ["D" if (t not in GT or d == 4) else GT[t] for t, d in zip(SUE.textura, SUE.drenaje)]
CN_TABLA = {"Bosque natural": (30, 55, 70, 77), "Bosque natural intervenido": (36, 60, 73, 79), "Vegetación arbustiva": (35, 56, 70, 77),
    "Pastos plantados": (39, 61, 74, 80), "Pastos naturales": (49, 69, 79, 84), "Cultivos de ciclo corto": (67, 78, 85, 89),
    "Arboricultura": (43, 65, 76, 82), "Frutales": (43, 65, 76, 82), "Café": (43, 65, 76, 82), "Cacao": (43, 65, 76, 82),
    "Asentamiento poblado": (77, 85, 90, 92), "Areas en proceso de erosión": (68, 79, 86, 89), "Areas erosionadas": (77, 86, 91, 94),
    "Cuerpos de agua": (100,) * 4, "Camaroneras": (100,) * 4, "Salinas": (98,) * 4}
X = gpd.overlay(COB[["cobertura", "geometry"]], SUE[["grupo", "geometry"]], how="intersection", keep_geom_type=True)
X["CN"] = [np.mean([CN_TABLA[p.strip()]["ABCD".index(g)] for p in c.split(" - ")]) for c, g in zip(X.cobertura, X.grupo)]
CN2 = float(np.average(X.CN, weights=X.area))
CN3 = 23 * CN2 / (10 + 0.13 * CN2)
def S_mm(CN): return 25400 / CN - 254
def Pe(P, CN, lam=0.2):
    S = S_mm(CN); Ia = lam * S; P = np.asarray(P, float)
    return np.where(P > Ia, (P - Ia) ** 2 / (P - Ia + S), 0.0)
print(f"CN ponderado (AMC II) = {CN2:.1f} · AMC III = {CN3:.1f}")
'''
