import sys
from common import *

md(r"""
# Práctica 2 · Paso 5 — Balance hídrico de tu cuenca y la señal de El Niño
### Hidrología (1CIA-502) · Ingeniería Ambiental · ESPAM MFL · Unidad II
**Docente:** Ing. Cristian Paliz Acosta, MSc.

En el capítulo 1 mediste **lo que sale** (caudal); en los pasos 1 a 4, **lo que entra** (lluvia). Ahora se cierra
la cuenta: **de cada 100 mm que llueven sobre tu cuenca, ¿cuántos salen por el río y cuántos se evaporan o se
quedan?** y **¿qué hace El Niño con esa cuenta?**

$$P = Q + ET + \Delta S \qquad\Rightarrow\qquad ET + \Delta S = P - Q$$
En periodos largos el almacenamiento (ΔS: suelo, acuífero, embalse) casi no cambia, y P − Q estima la
**evapotranspiración real**. En un mes cualquiera, P − Q mezcla ET y almacenamiento.

> **Analogía.** La cuenca es una cuenta bancaria: la lluvia es el sueldo, el río y la evapotranspiración son los
> gastos, y el suelo y el acuífero son los ahorros. En un año la cuenta casi cuadra; en un mes, los ahorros suben
> o bajan.

| Bloque | Qué haces | Producto |
|---|---|---|
| 3 | Lluvia y caudal de la cuenca **en la misma unidad (mm)** | Series mensuales 1995–2014 |
| 4 | **Balance anual** (primero el coeficiente de escorrentía a mano) | Tabla P, Q, P − Q, Q/P |
| 5 | **Balance mensual medio** | Régimen de P, Q y P − Q |
| 6 | **Señal de El Niño** 1982–83, 1997–98 y 2015–16 | Anomalías de lluvia y caudal |
| 7 | Lectura de la **bitácora de El Niño** | Tu bitácora frente a 1997–98 |
| 8 | Expediente del capítulo 2 | `expediente_P2p5_….csv` |
""")

md(r"""
## 1 · CONFIGURACIÓN ✍️ (única celda que editas)
- **CUENCA, USAR_MI_CUENCA, RADIO_KM:** los mismos de los pasos anteriores.
- **ESTACION_Q:** estación de caudal (None = la del paso 3 de la Práctica 1).
- **C_MANO:** tu coeficiente de escorrentía medio calculado a mano en la sección 4.
- **SUBIR_BITACORA:** `True` para subir tu bitácora de El Niño (CSV con columnas `fecha, fuente, variable, valor, observacion`).
""")
code(CONFIG_BASE + r'''ESTACION_Q = None
C_MANO     = None          # después de la sección 4
SUBIR_BITACORA = False
''')

md("## 2 · Cargar lluvia (Thiessen del paso 1) y caudal en la salida (Práctica 1, paso 3)")
code(CARGA + "\n" + CAUDAL)

md(r"""
## 3 · Lluvia y caudal en milímetros
Para sumar y restar, el caudal se convierte en **lámina** sobre la cuenca:
$$Q\,(\text{mm}) = \frac{Q\,(\text{m}^3/\text{s}) \cdot 86\,400 \cdot \text{días}}{A\,(\text{km}^2) \cdot 1000}$$
Es la altura de agua que tendría toda la cuenca si el volumen que salió por el río se repartiera sobre ella.
""")
code(r'''
Qmm_d = Q_all * 86400 / (A_km2 * 1e6) * 1000
comun = Pd_all.index.intersection(Qmm_d.dropna().index)
Pm_s = Pd_all.loc[comun].resample("MS").sum(); Qm_s = Qmm_d.loc[comun].resample("MS").sum()
M = pd.DataFrame({"P": Pm_s, "Q": Qm_s}); M["P_Q"] = M.P - M.Q
Mp = M.loc[f"{PERIODO[0]}":f"{PERIODO[1]}"]
fig, ax = plt.subplots(figsize=(14, 4.5))
ax.bar(Mp.index, Mp.P, width=25, color="#9CC3D5", label="Lluvia P (mm/mes)")
ax.plot(Mp.index, Mp.Q, color="#B3541A", lw=1.6, label="Caudal Q (mm/mes)")
ax.set_ylabel("mm/mes"); ax.legend(frameon=False); ax.grid(axis="y", alpha=0.3)
ax.set_title(f"Lluvia y caudal mensuales de {CUENCA} en la misma unidad · {PERIODO[0]}–{PERIODO[1]}", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p5_01_series_mensuales.png", dpi=150); plt.show()
print(f"Meses con lluvia y caudal: {len(M)} ({M.index.min():%Y-%m} a {M.index.max():%Y-%m}) · en {PERIODO[0]}–{PERIODO[1]}: {len(Mp)}")
''')

md(r"""
## 4 · Balance anual
✍️ **Antes de ejecutar la celda de abajo del todo:** con la fila «Media» de la tabla, calcula a mano el
**coeficiente de escorrentía C = Q/P** y escríbelo en `C_MANO`.
""")
code(r'''
An = Mp.groupby(Mp.index.year).sum()
An["Q/P"] = An.Q / An.P
tab = An.round(0).astype({"P": int, "Q": int, "P_Q": int}); tab["Q/P"] = An["Q/P"].round(2)
tab.loc["Media"] = [round(An.P.mean()), round(An.Q.mean()), round(An.P_Q.mean()), round(An.Q.mean() / An.P.mean(), 2)]
tab.columns = ["P (mm)", "Q (mm)", "P − Q (mm)", "Q/P"]
display(tab)
''')
code(r'''
C_med = An.Q.mean() / An.P.mean(); ET_med = An.P_Q.mean()
print(f"De cada 100 mm de lluvia, {100 * C_med:.0f} salen por el río y {100 * (1 - C_med):.0f} se evapotranspiran o se almacenan.")
print(f"Evapotranspiración real estimada (P − Q, {PERIODO[0]}–{PERIODO[1]}): {ET_med:.0f} mm/año")
if C_MANO is not None: print(f"Tu C a mano: {C_MANO:.2f} · cuaderno: {C_med:.2f}")
else: print("✍️  Escribe tu C a mano en C_MANO.")
neg = An[An.P_Q < 0]
if len(neg): print(f"⚠️  Años con Q > P: {list(neg.index)}. Imposible físicamente: revela errores de la lluvia de la cuenca o del caudal del modelo. Discútelo.")
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.bar(An.index, An.Q, color="#B3541A", label="Q (sale por el río)")
ax.bar(An.index, An.P_Q, bottom=An.Q, color="#9CC3D5", label="P − Q (ET + ΔS)")
ax2 = ax.twinx(); ax2.plot(An.index, An["Q/P"], "o-", color="#12263A", label="Q/P"); ax2.set_ylabel("Coeficiente de escorrentía Q/P"); ax2.set_ylim(0, 1)
ax.set_ylim(0, An.P.max() * 1.3); ax.set_ylabel("mm/año"); ax.set_xticks(An.index); ax.set_xticklabels(An.index, rotation=90); ax.grid(axis="y", alpha=0.3)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, frameon=False, loc="upper right")
ax.set_title(f"Balance hídrico anual de {CUENCA}: la barra completa es la lluvia P", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p5_02_balance_anual.png", dpi=150); plt.show()
r = np.corrcoef(An.P, An["Q/P"])[0, 1]
print(f"Correlación entre lluvia anual y Q/P: {r:.2f} → " + ("en años lluviosos escurre una fracción mayor" if r > 0.3 else "relación débil"))
''')

md(r"""
## 5 · Balance mensual medio
En los meses de lluvia, P − Q es grande: parte se evapotranspira y parte **recarga** el suelo y el acuífero. En
el estiaje, P − Q puede ser negativo: el río sigue corriendo con agua **almacenada** en la temporada lluviosa.
""")
code(r'''
Mm = Mp.groupby(Mp.index.month).mean()
fig, ax = plt.subplots(figsize=(9, 4.5)); x = np.arange(1, 13)
ax.bar(x - 0.2, Mm.P, 0.4, color="#9CC3D5", label="P"); ax.bar(x + 0.2, Mm.Q, 0.4, color="#B3541A", label="Q")
ax.plot(x, Mm.P_Q, "o-", color="#12263A", label="P − Q"); ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(list("EFMAMJJASOND")); ax.set_ylabel("mm/mes"); ax.grid(axis="y", alpha=0.3); ax.legend(frameon=False)
ax.set_title(f"Balance mensual medio · {CUENCA} · {PERIODO[0]}–{PERIODO[1]}", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p5_03_balance_mensual.png", dpi=150); plt.show()
display(Mm.round(0).rename(columns={"P_Q": "P − Q"}).T.rename(columns=dict(zip(range(1, 13), "Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic".split()))))
q_seco = Mm.loc[6:11, "Q"].sum() / Mm.Q.sum()
print(f"De junio a noviembre sale el {100 * q_seco:.0f} % del caudal del año con el {100 * Mm.loc[6:11, 'P'].sum() / Mm.P.sum():.0f} % de la lluvia.")
''')

md(r"""
## 6 · La señal de El Niño en tu cuenca
En la costa de Ecuador, los eventos **El Niño fuertes** de 1982–83, 1997–98 y 2015–16 trajeron lluvias muy por
encima de lo normal. Se compara la temporada **diciembre–mayo** de cada evento con la media de todas las
temporadas con datos (1980–2018). La **anomalía** es el cociente evento/normal: 2,0 significa el doble de lo normal.

Se usa todo el registro común de lluvia y caudal, no solo 1995–2014, para incluir 1982–83.
""")
code(r'''
Mt = M.copy(); Mt["temp"] = [y + 1 if m == 12 else y for y, m in zip(Mt.index.year, Mt.index.month)]
Mt = Mt[Mt.index.month.isin([12, 1, 2, 3, 4, 5])]
TEMP = Mt.groupby("temp")[["P", "Q"]].sum(); n_m = Mt.groupby("temp").size(); TEMP = TEMP[n_m == 6]
norm = TEMP.mean()
EVENTOS = {1983: "1982–83", 1998: "1997–98", 2016: "2015–16"}
fig, axs = plt.subplots(1, 2, figsize=(14, 4.5), sharex=True)
for ax, v, c, lab in [(axs[0], "P", "#1F6F8B", "Lluvia"), (axs[1], "Q", "#B3541A", "Caudal")]:
    an = TEMP[v] / norm[v]
    ax.bar(an.index, an.values, color=["#B3541A" if y in EVENTOS else "#C9D6DE" for y in an.index])
    ax.axhline(1, color="k", lw=0.8); ax.set_ylim(0, an.max() * 1.25); ax.set_ylabel(f"{lab} dic–may / normal"); ax.grid(axis="y", alpha=0.3)
    for y, e in EVENTOS.items():
        if y in an.index: ax.annotate(f"{e}\n×{an[y]:.1f}", (y, an[y]), ha="center", va="bottom", fontsize=8)
    ax.set_title(f"{lab}: anomalía de la temporada lluviosa", fontweight="bold")
fig.suptitle(f"Señal de El Niño en {CUENCA} (naranja: El Niño fuertes)", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p5_04_senal_el_nino.png", dpi=150); plt.show()
EN = pd.DataFrame({"Temporada": [EVENTOS[y] for y in EVENTOS if y in TEMP.index],
                   "P dic–may (mm)": [TEMP.P[y] for y in EVENTOS if y in TEMP.index],
                   "P / normal": [TEMP.P[y] / norm.P for y in EVENTOS if y in TEMP.index],
                   "Q dic–may (mm)": [TEMP.Q[y] for y in EVENTOS if y in TEMP.index],
                   "Q / normal": [TEMP.Q[y] / norm.Q for y in EVENTOS if y in TEMP.index],
                   "Q/P": [TEMP.Q[y] / TEMP.P[y] for y in EVENTOS if y in TEMP.index]})
display(EN.round(2))
print(f"Temporada normal: P = {norm.P:.0f} mm, Q = {norm.Q:.0f} mm, Q/P = {norm.Q / norm.P:.2f}")
if 1998 in TEMP.index:
    print(f"En 1997–98 la lluvia fue ×{TEMP.P[1998] / norm.P:.1f} y el caudal ×{TEMP.Q[1998] / norm.Q:.1f}: "
          + ("el caudal se amplifica más que la lluvia (suelo saturado, CN tipo AMC III)." if TEMP.Q[1998] / norm.Q > TEMP.P[1998] / norm.P else "el caudal no se amplificó más que la lluvia: puede ser la respuesta de la cuenca o el límite de la corrección del modelo (factor máximo 3); discútelo."))
''')

md(r"""
## 7 · Tu bitácora de El Niño
La **bitácora** es el registro que llevas durante el semestre: boletines del INAMHI y del CIIFEN, el índice ONI de
la NOAA, noticias de lluvias y crecidas en tu cuenca. Si la subes (`SUBIR_BITACORA = True`), el cuaderno la
ordena y te pide compararla con 1997–98. Si no, genera la plantilla vacía en `salidas/`.

Columnas: `fecha` (AAAA-MM-DD), `fuente` (INAMHI, CIIFEN, NOAA, prensa…), `variable` (ONI, lluvia, caudal, nivel,
evento), `valor` (número o vacío), `observacion` (una frase).
""")
code(r'''
PLANT = pd.DataFrame(columns=["fecha", "fuente", "variable", "valor", "observacion"])
PLANT.to_csv(f"salidas/plantilla_bitacora_el_nino.csv", index=False, encoding="utf-8-sig")
BIT = None
if SUBIR_BITACORA:
    from google.colab import files
    print("Sube tu bitácora (CSV):"); up = files.upload(); nombre = list(up)[0]
    BIT = pd.read_csv(io.BytesIO(up[nombre]), parse_dates=["fecha"]).sort_values("fecha")
    display(BIT)
    print(f"{len(BIT)} entradas de {BIT.fecha.min():%d/%m/%Y} a {BIT.fecha.max():%d/%m/%Y} · fuentes: {', '.join(BIT.fuente.astype(str).unique())}")
    oni = BIT[BIT.variable.astype(str).str.upper() == "ONI"]
    if len(oni): print(f"Último ONI registrado: {oni.valor.iloc[-1]} ({oni.fecha.iloc[-1]:%m/%Y}). El Niño fuerte: ONI ≥ 1,5 °C.")
else:
    print("Plantilla de bitácora guardada en salidas/plantilla_bitacora_el_nino.csv")
if 1998 in TEMP.index:
    extra = TEMP.P[1998] - norm.P
    print(f"Referencia para leer tu bitácora: si se repitiera un evento como 1997–98, tu cuenca recibiría unos "
          f"{extra:.0f} mm más de lluvia entre diciembre y mayo, y el río llevaría ×{TEMP.Q[1998] / norm.Q:.1f} su caudal normal.")
''')

md("## 8 · Expediente del capítulo 2 y descarga")
code(r'''
f = f"P2_paso5 · lluvia Thiessen INAMHI + {ORIGEN_Q}"
exp = [("2.7", "Origen del caudal", ORIGEN_Q, "", "Práctica 1, paso 3"),
       ("2.7", "P media anual (balance)", round(An.P.mean(), 0), "mm/año", f), ("2.7", "Q media anual", round(An.Q.mean(), 0), "mm/año", f),
       ("2.7", "P − Q (ET real + ΔS)", round(ET_med, 0), "mm/año", f), ("2.7", "Coeficiente de escorrentía Q/P", round(C_med, 3), "—", f),
       ("2.7", "Q/P a mano", C_MANO if C_MANO is not None else "", "—", "estudiante"),
       ("2.7", "Q/P mínimo y máximo anual", f"{An['Q/P'].min():.2f} ({An['Q/P'].idxmin()}) – {An['Q/P'].max():.2f} ({An['Q/P'].idxmax()})", "", f),
       ("2.7", "Años con Q > P", ", ".join(map(str, neg.index)) if len(neg) else "ninguno", "", f),
       ("2.7", "Caudal de junio a noviembre", round(100 * q_seco, 0), "% del anual", f),
       ("2.7", "Temporada dic–may normal P / Q", f"{norm.P:.0f} / {norm.Q:.0f}", "mm", "1980–2018")]
for _, r in EN.iterrows():
    exp += [("2.7", f"El Niño {r.Temporada}: P / normal", round(r["P / normal"], 2), "—", f),
            ("2.7", f"El Niño {r.Temporada}: Q / normal", round(r["Q / normal"], 2), "—", f)]
exp += [("2.7", "Entradas en la bitácora", len(BIT) if BIT is not None else "", "n.º", "estudiante")]
EXP = pd.DataFrame([("2",) + x for x in exp], columns=["capitulo", "apartado", "campo", "valor", "unidad", "fuente"])
EXP.to_csv(f"salidas/expediente_P2p5_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
M.to_csv(f"salidas/balance_mensual_{CUENCA}_{SLUG}.csv", encoding="utf-8-sig")
import shutil
paquete = shutil.make_archive(f"Practica2_Paso5_{CUENCA}_{SLUG}", "zip", "salidas")
print("✅ Paquete:", paquete)
try:
    from google.colab import files; files.download(paquete)
except ImportError:
    print("Descárgalo desde el panel de archivos de Colab.")
EXP
''')

md(r"""
---
## Para tu capítulo 2 · apartado 2.7 (cinco líneas debajo de cada figura)
1. **Balance anual.** De cada 100 mm de lluvia, ¿cuántos salen por el río? ¿Es razonable la ET real para un clima
   tropical seco a húmedo (consulta un valor de referencia y cítalo)? ¿Hay años imposibles (Q > P) y por qué?
2. **Balance mensual.** ¿En qué meses la cuenca «ahorra» agua y en cuáles la «gasta»? Relaciónalo con la curva de
   duración del capítulo 1.
3. **El Niño.** ¿Cuántas veces lo normal llovió y escurrió en 1997–98? ¿Por qué el caudal se amplifica más que la
   lluvia? Relaciónalo con el CN en AMC III del paso 3.
4. **Bitácora.** ¿Qué dicen hoy tus fuentes? Si se repitiera 1997–98, ¿qué esperarías en tu cuenca?
""")
save(sys.argv[1] if len(sys.argv) > 1 else "P2_paso5_balance_hidrico.ipynb")
