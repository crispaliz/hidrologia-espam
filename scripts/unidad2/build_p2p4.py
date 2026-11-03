import sys
from common import *

md(r"""
# Práctica 2 · Paso 4 — Caudal pico e hidrograma triangular de tu cuenca
### Hidrología (1CIA-502) · Ingeniería Ambiental · ESPAM MFL · Unidad II
**Docente:** Ing. Cristian Paliz Acosta, MSc.

Este paso **se resuelve a mano** en la hoja de cálculo
[`hojas/P2_paso4_hoja_hidrograma.pdf`](https://github.com/crispaliz/hidrologia-espam/blob/main/hojas/P2_paso4_hoja_hidrograma.pdf).
El cuaderno no reemplaza la hoja: **la revisa**. Escribes tus resultados en la celda 1, el cuaderno los compara con
los suyos y luego te muestra tres comparaciones que no se pueden hacer a mano.

| Bloque | Qué haces | Producto |
|---|---|---|
| 3 | Revisar los datos de entrada (A, tc, CN, P₂₄) | Tabla de datos de tu cuenca |
| 4 | Hidrograma unitario triangular del SCS: de, tp, tb | Tiempos del hidrograma |
| 5 | Lluvia de duración de, lluvia efectiva y **caudal pico** para T = 10, 25, 100 | Tabla y revisión de tus valores |
| 6 | Dibujo de los **hidrogramas triangulares** | Figura para el capítulo |
| 7 | Comparación 1: hidrograma de la tormenta de 24 h (convolución) | ¿Cuánto cambia el pico? |
| 8 | Comparación 2: **método racional** | Por qué no sirve en cuencas grandes |
| 9 | Comparación 3: crecidas del río (caudales máximos 1995–2014) | ¿Es creíble tu caudal pico? |
| 10 | Expediente del capítulo 2 | `expediente_P2p4_….csv` |
""")

md(r"""
## Ejemplo resuelto (cuenca ficticia, para guiarte con la hoja)
Cuenca de **A = 250 km²**, **tc = 4,0 h**, **CN = 75** y **P₂₄ = 110 mm** para T = 25 años.

| Paso | Fórmula | Cálculo | Resultado |
|---|---|---|---|
| 1 · Duración de la lluvia | $d_e = 2\sqrt{t_c}$ | 2·√4,0 | **4,0 h** |
| 2 · Tiempo al pico | $t_p = d_e/2 + 0{,}6\,t_c$ | 2,0 + 2,4 | **4,4 h** |
| 3 · Tiempo base | $t_b = 2{,}67\,t_p$ | 2,67·4,4 | **11,7 h** |
| 4 · Lluvia de duración dₑ | $P_{d_e} = P_{24}\,(d_e·60/1440)^{0{,}25}$ | 110·(240/1440)^0,25 | **70,3 mm** |
| 5 · Retención | $S = 25\,400/CN - 254$ ; $I_a = 0{,}2\,S$ | 338,7 − 254 | **S = 84,7 mm · Ia = 16,9 mm** |
| 6 · Lluvia efectiva | $P_e = (P-I_a)^2/(P-I_a+S)$ | 53,4² / 138,0 | **20,6 mm** |
| 7 · Caudal pico | $Q_p = 0{,}208\,A\,P_e/t_p$ | 0,208·250·20,6/4,4 | **244 m³/s** |

**Verificación del volumen:** el área del triángulo, ½·Qp·tb = ½·244·11,7·3600 ≈ 5,1 hm³, debe ser igual a
Pe·A = 0,0206 m · 250·10⁶ m² ≈ 5,2 hm³. Si no coinciden, hay un error de unidades.

> **Analogía.** Una lámina de agua Pe sobre toda la cuenca sale por el río como un «triángulo» de caudal: sube
> durante tp, baja durante 1,67·tp. Cuanto más corto es tp (cuenca pequeña y empinada), más alto el pico
> para el mismo volumen.

El 0,208 sale de unidades: 1 mm sobre 1 km² en 1 hora, con la forma del triángulo del SCS (0,208 = 2/2,67 ÷ 3,6).
""")

md(r"""
## 1 · CONFIGURACIÓN ✍️ (única celda que editas)
- **TC_H:** tu **tiempo de concentración (Kirpich)** del capítulo 1, en horas (expediente_P2, apartado 1.3). Obligatorio.
- **CUENCA, USAR_MI_CUENCA, RADIO_KM:** los mismos de los pasos anteriores. Si en el capítulo 1 trabajaste tu
  propia cuenca o subcuenca, usa `USAR_MI_CUENCA = True` para que el área y el tc sean de la misma cuenca.
- **Valores a mano** (de tu hoja): `TP_MANO` y el caudal pico de cada T en `QP_MANO`.
- **ESTACION_Q:** estación de caudal para la comparación 3 (None = la del paso 3 de la Práctica 1).
""")
code(CONFIG_BASE + r'''TC_H       = None          # h, del capítulo 1 (obligatorio)
TP_MANO    = None          # h, de tu hoja
QP_MANO    = {10: None, 25: None, 100: None}   # m³/s, de tu hoja
ESTACION_Q = None
T_DISENO   = (10, 25, 100)
''')

md(r"""
## 2 · Recuperar lo de los pasos 1, 2 y 3
Thiessen (paso 1), Gumbel y P₂₄ (paso 2) y CN ponderado (paso 3), sin gráficos. Deben coincidir con tus expedientes.
""")
code(CARGA + "\n" + GUMBEL + "\n" + CNB)

md("## 3 · Datos de entrada de tu cuenca (cópialos en la hoja)")
code(r'''
if TC_H is None:
    raise ValueError("Escribe en TC_H (celda 1) el tiempo de concentración de tu capítulo 1, en horas.")
DAT = pd.DataFrame({"Dato": ["Área A", "Tiempo de concentración tc", "CN (AMC II)"] + [f"P24 T={T}" for T in T_DISENO],
                    "Valor": [round(A_km2, 1), TC_H, round(CN2, 1)] + [round(PT24(T), 1) for T in T_DISENO],
                    "Unidad": ["km²", "h", "—"] + ["mm"] * len(T_DISENO),
                    "De dónde sale": ["paso 1 (límite de la cuenca)", "capítulo 1 (Kirpich)", "paso 3"] + ["paso 2 (Gumbel × 1,13)"] * len(T_DISENO)})
display(DAT)
''')

md(r"""
## 4 · Tiempos del hidrograma unitario triangular (SCS)
- **Duración de la lluvia en exceso:** $d_e = 2\sqrt{t_c}$ (recomendación para cuencas grandes, Aparicio, 1992).
- **Tiempo de retraso:** $t_r = 0{,}6\,t_c$ ; **tiempo al pico:** $t_p = d_e/2 + t_r$ ; **tiempo base:** $t_b = 2{,}67\,t_p$.
""")
code(r'''
de = 2 * np.sqrt(TC_H); tr = 0.6 * TC_H; tp = de / 2 + tr; tb = 2.67 * tp
print(f"de = {de:.2f} h · tr = {tr:.2f} h · tp = {tp:.2f} h · tb = {tb:.2f} h")
if TP_MANO is not None: print(f"Tu tp a mano: {TP_MANO:.2f} h · diferencia {TP_MANO - tp:+.2f} h")
''')

md(r"""
## 5 · Lluvia efectiva y caudal pico para T = 10, 25 y 100 años
$$P_{d_e} = P_{24}\left(\frac{d_e\cdot 60}{1440}\right)^{0{,}25} \quad\rightarrow\quad P_e \;(\text{CN}) \quad\rightarrow\quad Q_p = \frac{0{,}208\,A\,P_e}{t_p}$$
con A en km², Pe en mm y tp en h → Qp en m³/s.
""")
code(r'''
filas = []
for T in T_DISENO:
    Pde = float(P_D(de, T)); pe = float(Pe(Pde, CN2)); pe3 = float(Pe(Pde, CN3))
    Qp = 0.208 * A_km2 * pe / tp; V = pe / 1000 * A_km2 * 1e6
    filas.append((T, PT24(T), Pde, pe, Qp, 0.208 * A_km2 * pe3 / tp, V / 1e6, QP_MANO.get(T)))
QP = pd.DataFrame(filas, columns=["T (años)", "P24 (mm)", "P_de (mm)", "Pe (mm)", "Qp (m³/s)", "Qp AMC III (m³/s)", "Volumen (hm³)", "Qp a mano (m³/s)"])
display(QP.round(2))
for _, r in QP.iterrows():
    if r["Qp a mano (m³/s)"] is not None and not pd.isna(r["Qp a mano (m³/s)"]):
        e = 100 * (r["Qp a mano (m³/s)"] / r["Qp (m³/s)"] - 1)
        print(f"T={r['T (años)']:.0f}: tu Qp {r['Qp a mano (m³/s)']:.0f} m³/s · cuaderno {r['Qp (m³/s)']:.0f} m³/s · "
              f"{e:+.1f} % → " + ("✅ dentro del 5 %" if abs(e) <= 5 else "⚠️ revisa unidades y redondeos"))
    else:
        print(f"T={r['T (años)']:.0f}: ✍️  escribe tu Qp a mano en QP_MANO[{r['T (años)']:.0f}]")
r = QP.iloc[0]
print(f"Verificación del volumen (T={r['T (años)']:.0f}): ½·Qp·tb = {0.5 * r['Qp (m³/s)'] * tb * 3600 / 1e6:.2f} hm³ · Pe·A = {r['Volumen (hm³)']:.2f} hm³")
''')

md("## 6 · Hidrogramas triangulares de diseño")
code(r'''
fig, ax = plt.subplots(figsize=(10, 5))
cols = {10: "#5B9BB5", 25: "#1F6F8B", 100: "#12263A"}
for _, r in QP.iterrows():
    T = int(r["T (años)"]); q = r["Qp (m³/s)"]
    ax.plot([0, tp, tb], [0, q, 0], lw=2.2, color=cols.get(T, "k"), label=f"T = {T} años · Qp = {q:.0f} m³/s")
    ax.annotate(f"{q:.0f}", (tp, q), xytext=(6, 4), textcoords="offset points", fontsize=9)
ax.axvline(tp, color="0.6", ls=":", lw=1); ax.text(tp, 0, f" tp = {tp:.1f} h", va="bottom", fontsize=9, color="0.4")
ax.text(tb, ax.get_ylim()[1] * 0.06, f"tb = {tb:.1f} h ", ha="right", va="bottom", fontsize=9, color="0.4")
ax.set_xlabel("Tiempo desde el inicio de la lluvia en exceso (h)"); ax.set_ylabel("Caudal (m³/s)")
ax.set_xlim(0, tb * 1.05); ax.set_ylim(0, None); ax.grid(alpha=0.3); ax.legend(frameon=False)
ax.set_title(f"Hidrogramas triangulares de diseño · {CUENCA} · A = {A_km2:.0f} km² · tc = {TC_H:.1f} h · CN {CN2:.0f}", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p4_01_hidrogramas_triangulares.png", dpi=150); plt.show()
''')

md(r"""
## 7 · Comparación 1: la tormenta completa de 24 horas
El cálculo a mano usa **un solo bloque** de lluvia de duración dₑ. La tormenta de diseño del paso 2 dura 24 h:
cada hora de lluvia efectiva genera su propio triángulo (hidrograma unitario de 1 h) y los triángulos se
**suman desfasados**. Eso es la **convolución**, la idea central del hidrograma unitario.
""")
code(r'''
dt = 1.0; tp1 = dt / 2 + tr; tb1 = 2.67 * tp1; qp1 = 0.208 * A_km2 / tp1          # m³/s por mm de Pe
t_u = np.arange(0, np.ceil(tb1) + dt, dt)
HU = np.interp(t_u, [0, tp1, tb1], [0, qp1, 0])
CONV = {}
for T in T_DISENO:
    h = hietograma(T); pe_h = np.diff(np.r_[0, Pe(h.cumsum().values, CN2)])
    CONV[T] = np.convolve(pe_h, HU)
tq = np.arange(len(CONV[T_DISENO[0]])) * dt
fig, ax = plt.subplots(figsize=(11, 5))
for T in T_DISENO:
    ax.plot(tq, CONV[T], lw=2, color=cols.get(T, "k"), label=f"T = {T} · 24 h convolución · Qp = {CONV[T].max():.0f} m³/s")
    q = QP.set_index("T (años)").loc[T, "Qp (m³/s)"]
    t0 = 12 - de / 2
    ax.plot([t0, t0 + tp, t0 + tb], [0, q, 0], ls="--", lw=1.2, color=cols.get(T, "k"))
ax.set_xlabel("Hora desde el inicio de la tormenta de 24 h"); ax.set_ylabel("Caudal (m³/s)"); ax.grid(alpha=0.3)
ax.legend(frameon=False, fontsize=8); ax.set_xlim(0, tq[np.nonzero(CONV[T_DISENO[-1]] > 0.01)[0][-1]] + 2)
ax.set_title("Hidrograma de la tormenta de 24 h (línea) frente al triangular a mano (trazos)", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p4_02_convolucion.png", dpi=150); plt.show()
for T in T_DISENO:
    qm = QP.set_index("T (años)").loc[T, "Qp (m³/s)"]
    print(f"T={T}: triangular {qm:.0f} m³/s · tormenta de 24 h {CONV[T].max():.0f} m³/s (× {CONV[T].max() / qm:.2f}) a las {tq[CONV[T].argmax()]:.0f} h")
''')

md(r"""
## 8 · Comparación 2: método racional
$$Q = 0{,}278\;C\;I\;A$$
con I la intensidad de una lluvia de duración igual a tc (mm/h), C el coeficiente de escorrentía (aquí Pe/P de
esa lluvia) y A en km². Supone que **toda la cuenca aporta a la vez** con lluvia uniforme: es válido en cuencas
pequeñas (del orden de unos pocos km², como un barrio o una vía), **no** en cuencas de cientos de km².
""")
code(r'''
RAC = []
for T in T_DISENO:
    Ptc = float(P_D(TC_H, T)); I = Ptc / TC_H; Cc = float(Pe(Ptc, CN2)) / Ptc
    RAC.append((T, I, Cc, 0.278 * Cc * I * A_km2))
RAC = pd.DataFrame(RAC, columns=["T (años)", "I (mm/h)", "C", "Q racional (m³/s)"])
RAC["Q triangular (m³/s)"] = QP["Qp (m³/s)"].values
display(RAC.round(2))
print(f"Tu cuenca tiene {A_km2:.0f} km²: el método racional está fuera de su rango de validez. Úsalo solo para comparar.")
''')

md(r"""
## 9 · Comparación 3: ¿qué crecidas ha tenido el río?
Gumbel sobre los **caudales medios diarios máximos** de cada año en la salida (1995–2014). Un caudal medio diario
es menor que el pico instantáneo; se corrige con el factor de **Fuller**: $Q_{inst} = Q_{día}\,(1 + 2{,}66\,A^{-0{,}3})$.
Los caudales son de GEOGloWS corregido con los anuarios del INAMHI (Práctica 1, paso 3): los picos de un modelo
global son la parte menos confiable de la serie.
""")
code(CAUDAL + r'''
Qmax = Qd.groupby(Qd.index.year).max()
qm_, qs_ = Qmax.mean(), Qmax.std(ddof=1); FULLER = 1 + 2.66 * A_km2 ** -0.3
OBSQ = pd.DataFrame({"T (años)": T_DISENO, "Q día máx (m³/s)": [qm_ + KT(T) * qs_ for T in T_DISENO]})
OBSQ["Q instantáneo Fuller (m³/s)"] = OBSQ["Q día máx (m³/s)"] * FULLER
OBSQ["Q triangular (m³/s)"] = QP["Qp (m³/s)"].values
OBSQ["Q 24 h convolución (m³/s)"] = [CONV[T].max() for T in T_DISENO]
display(OBSQ.round(0))
fig, ax = plt.subplots(figsize=(11, 4))
ax.bar(Qmax.index, Qmax.values, color=["#B3541A" if y in (1997, 1998) else "#1F6F8B" for y in Qmax.index])
for T in T_DISENO:
    ax.axhline(QP.set_index("T (años)").loc[T, "Qp (m³/s)"], color=cols.get(T, "k"), ls="--", lw=1)
    ax.text(Qmax.index.min() - 0.5, QP.set_index("T (años)").loc[T, "Qp (m³/s)"], f"Qp triangular T={T}", fontsize=7, va="bottom")
ax.set_xticks(Qmax.index); ax.set_xticklabels(Qmax.index, rotation=90); ax.grid(axis="y", alpha=0.3)
ax.set_ylabel("Caudal medio diario máximo del año (m³/s)")
ax.set_title(f"Crecidas anuales en la salida de {CUENCA} ({PERIODO[0]}–{PERIODO[1]}) y caudales de diseño", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p4_03_crecidas_vs_diseno.png", dpi=150); plt.show()
print(f"Mayor crecida diaria del periodo: {Qmax.max():.0f} m³/s en {Qmax.idxmax()} · factor de Fuller {FULLER:.2f}")
q100 = QP.set_index("T (años)")["Qp (m³/s)"].max()
if Qmax.max() * FULLER > q100:
    print(f"⚠️  La mayor crecida registrada (≈ {Qmax.max() * FULLER:.0f} m³/s instantáneos) supera tu Qp de {max(T_DISENO)} años ({q100:.0f} m³/s): "
          "revisa tc y CN, o la calidad del caudal del modelo, y discútelo en 2.6.")
''')

md("## 10 · Expediente del capítulo 2 y descarga")
code(r'''
f = "P2_paso4 · hidrograma unitario triangular SCS"
exp = [("2.6", "Área A", round(A_km2, 1), "km²", "paso 1"), ("2.6", "Tiempo de concentración tc", TC_H, "h", "capítulo 1 (Kirpich)"),
       ("2.6", "CN (AMC II)", round(CN2, 1), "—", "paso 3"),
       ("2.6", "Duración de la lluvia en exceso de", round(de, 2), "h", "de = 2√tc (Aparicio, 1992)"),
       ("2.6", "Tiempo al pico tp", round(tp, 2), "h", f), ("2.6", "Tiempo base tb", round(tb, 2), "h", f),
       ("2.6", "tp a mano", TP_MANO if TP_MANO is not None else "", "h", "estudiante (hoja)")]
for _, r in QP.iterrows():
    T = int(r["T (años)"])
    exp += [("2.6", f"P de duración de, T={T}", round(r["P_de (mm)"], 1), "mm", f), ("2.6", f"Pe T={T}", round(r["Pe (mm)"], 1), "mm", f),
            ("2.6", f"Qp triangular T={T}", round(r["Qp (m³/s)"], 0), "m³/s", f),
            ("2.6", f"Qp a mano T={T}", QP_MANO.get(T) if QP_MANO.get(T) is not None else "", "m³/s", "estudiante (hoja)"),
            ("2.6", f"Qp tormenta 24 h T={T}", round(CONV[T].max(), 0), "m³/s", "convolución HU 1 h"),
            ("2.6", f"Q racional T={T}", round(RAC.set_index('T (años)').loc[T, 'Q racional (m³/s)'], 0), "m³/s", "solo comparación"),
            ("2.6", f"Q instantáneo de crecidas T={T}", round(OBSQ.set_index('T (años)').loc[T, 'Q instantáneo Fuller (m³/s)'], 0), "m³/s", ORIGEN_Q)]
exp += [("2.6", "Mayor crecida diaria 1995–2014", f"{Qmax.max():.0f} m³/s ({Qmax.idxmax()})", "", ORIGEN_Q)]
EXP = pd.DataFrame([("2",) + x for x in exp], columns=["capitulo", "apartado", "campo", "valor", "unidad", "fuente"])
EXP.to_csv(f"salidas/expediente_P2p4_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
pd.DataFrame({f"Q_T{T}": CONV[T] for T in T_DISENO}, index=pd.Index(tq, name="hora")).to_csv(f"salidas/hidrogramas_24h_{CUENCA}_{SLUG}.csv", encoding="utf-8-sig")
import shutil
paquete = shutil.make_archive(f"Practica2_Paso4_{CUENCA}_{SLUG}", "zip", "salidas")
print("✅ Paquete:", paquete)
try:
    from google.colab import files; files.download(paquete)
except ImportError:
    print("Descárgalo desde el panel de archivos de Colab.")
EXP
''')

md(r"""
---
## Para tu capítulo 2 · apartado 2.6 (cinco líneas debajo de cada figura)
1. **Caudal pico a mano.** Presenta tu hoja (foto o escaneo) y la tabla de Qp. ¿Coincidió con el cuaderno?
   Si no, ¿dónde estuvo el error?
2. **Hidrograma.** ¿Cuántas horas tarda en llegar el pico y cuánto dura la crecida? ¿Qué significa para una alerta temprana?
3. **Tres comparaciones.** ¿Por qué la tormenta de 24 h da otro pico? ¿Por qué el racional no sirve aquí? ¿Tu Qp de
   100 años es mayor que la crecida de 1997–98?
4. **Límites.** Nombra dos supuestos del método que no se cumplen del todo en tu cuenca.
""")
save(sys.argv[1] if len(sys.argv) > 1 else "P2_paso4_hidrograma_triangular.ipynb")
