import sys
from common import *

md(r"""
# Práctica 2 · Paso 2 — Lluvia de diseño de tu cuenca para 10, 25 y 100 años
### Hidrología (1CIA-502) · Ingeniería Ambiental · ESPAM MFL · Unidad II
**Docente:** Ing. Cristian Paliz Acosta, MSc.

Un puente, una alcantarilla o un muro de encauzamiento no se diseñan para la lluvia de un año cualquiera,
sino para una lluvia que **se iguala o supera, en promedio, una vez cada T años**. Este cuaderno responde:
**¿cuánta lluvia debe soportar una obra en tu cuenca para T = 10, 25 y 100 años?**

| Bloque | Qué haces | Producto |
|---|---|---|
| 3 | Serie de **máximos anuales** de lluvia diaria de la cuenca, 1995–2014 | Tabla y gráfico de 20 máximos |
| 4 | Posición de graficación (Weibull) | Periodo de retorno empírico de cada máximo |
| 5 | **Gumbel** por momentos (primero P₁₀ a mano) | P diaria para T = 2…100 años |
| 6 | Bondad de ajuste (Kolmogorov–Smirnov) e incertidumbre | ¿Gumbel sirve? ¿Cuánto confiar en P₁₀₀? |
| 7 | Lluvia de 24 h y comparación con 1964–2018 | P₂₄ de diseño |
| 8 | Curvas **IDF** (intensidad–duración–frecuencia) | Gráfico y ecuación I = K·Tᵐ/Dⁿ |
| 9 | **Hietogramas de diseño** de 24 h (bloques alternos) | Hietogramas horarios T = 10, 25, 100 |
| 10 | Expediente del capítulo 2 | `expediente_P2p2_….csv` |

**Mano antes que modelo:** en la sección 5 calculas P₁₀ con la media, la desviación y la fórmula de K_T
antes de que el cuaderno ajuste la distribución.

`Archivo → Guardar una copia en Drive`, llena **solo la celda 1** y ejecuta
`Entorno de ejecución → Reiniciar sesión y ejecutar todo`.
""")

md(r"""
## 1 · CONFIGURACIÓN ✍️ (única celda que editas)
- **CUENCA, USAR_MI_CUENCA, RADIO_KM:** los mismos del paso 1, para que los pesos de Thiessen coincidan.
- **P10_MANO:** tu P₁₀ diaria calculada a mano en la sección 5 (mm).
- **T_DISENO:** periodos de retorno que pide la práctica.
""")
code(CONFIG_BASE + r'''P10_MANO   = None          # mm, después de leer la sección 5
T_DISENO   = (10, 25, 100)
''')

md(r"""
## 2 · Cargar datos y recuperar los pesos de Thiessen del paso 1
La celda repite el cálculo de Thiessen del paso 1 (sin gráficos) para obtener la **lluvia media diaria de la
cuenca**. Si los pesos no coinciden con los de tu paso 1, revisa que `CUENCA`, `USAR_MI_CUENCA` y `RADIO_KM`
sean los mismos.
""")
code(CARGA)

md(r"""
## 3 · La serie de máximos anuales
De cada año se toma **un solo valor: el día de mayor lluvia media sobre la cuenca**. Así cada dato es
independiente de los demás (no hay dos días de la misma tormenta) y todos representan lo mismo: el peor día del
año. Con 20 años (1995–2014) se tienen 20 máximos.

> **Analogía.** Para saber qué tan alta debe ser la cerca de un corral junto al río, no sirve la altura media del
> agua: sirve **la crecida más alta de cada año**. Con esa lista se estima qué tan alta llega una vez cada 10 o 100 años.

También se muestra el máximo de la **estación de mayor peso**: la lluvia en un punto es mayor que la lluvia
media sobre toda la cuenca, porque los núcleos de tormenta no cubren toda el área a la vez.
""")
code(r'''
Pmax = Pd.groupby(Pd.index.year).max()
fecha_max = Pd.groupby(Pd.index.year).idxmax()
e1 = W.idxmax()
Pmax_est = LL.loc[Pd.index, e1].groupby(Pd.index.year).max()
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.bar(Pmax.index - 0.2, Pmax_est.values, 0.4, color="#C9D6DE", label=f"Estación {e1} {NOMBRE[e1]} (punto)")
ax.bar(Pmax.index + 0.2, Pmax.values, 0.4, color=["#B3541A" if y in (1997, 1998) else "#1F6F8B" for y in Pmax.index],
       label="Media de la cuenca (Thiessen)")
ax.set_xticks(Pmax.index); ax.set_xticklabels(Pmax.index, rotation=90); ax.grid(axis="y", alpha=0.3)
ax.set_ylabel("Lluvia máxima en 24 h del año (mm)"); ax.legend(frameon=False)
ax.set_title(f"Máximos anuales de lluvia diaria · {CUENCA} · {PERIODO[0]}–{PERIODO[1]} · naranja: El Niño 1997–98", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p2_01_maximos_anuales.png", dpi=150); plt.show()
tabla = pd.DataFrame({"Año": Pmax.index, "Fecha del máximo": [f"{d:%d/%m}" for d in fecha_max],
                      "P máx. cuenca (mm)": Pmax.round(1).values, f"P máx. {e1} (mm)": Pmax_est.round(1).values})
display(tabla)
FRA = (Pmax / Pmax_est).median()
print(f"Media de los máximos de la cuenca: {Pmax.mean():.1f} mm · de la estación {e1}: {Pmax_est.mean():.1f} mm")
print(f"Factor de reducción por área (mediana cuenca/punto): {FRA:.2f}")
meses = pd.Series([d.month for d in fecha_max]).value_counts().sort_index()
print("Mes en que ocurrió el máximo anual:", ", ".join(f"{'EFMAMJJASOND'[m - 1]}: {n}" for m, n in meses.items()))
''')

md(r"""
## 4 · Posición de graficación: el periodo de retorno «observado»
Se ordenan los máximos de mayor a menor (rango m = 1 el mayor). La fórmula de **Weibull** da la probabilidad
de excedencia y el periodo de retorno empírico de cada dato:
$$P(X \ge x_m) = \frac{m}{n+1} \qquad T = \frac{n+1}{m}$$
Con n = 20, el mayor máximo tiene T ≈ 21 años. **Ningún dato observado dice nada directo sobre T = 100 años:**
para eso hace falta una distribución de probabilidad (sección 5).
""")
code(r'''
n = len(Pmax)
W_ = pd.DataFrame({"Año": Pmax.index, "P (mm)": Pmax.values}).sort_values("P (mm)", ascending=False).reset_index(drop=True)
W_.insert(0, "m", range(1, n + 1))
W_["P excedencia"] = W_.m / (n + 1)
W_["T (años)"] = (n + 1) / W_.m
display(W_.round(3))
print(f"El mayor máximo ({W_.iloc[0]['P (mm)']:.0f} mm, {W_.iloc[0]['Año']:.0f}) tiene T empírico = {W_.iloc[0]['T (años)']:.0f} años.")
''')

md(r"""
## 5 · Distribución de Gumbel (valores extremos tipo I)
Gumbel describe bien el **máximo de muchos valores**: el peor día de 365. Por el método de momentos:
$$P_T = \bar x + K_T\, s \qquad K_T = -\frac{\sqrt 6}{\pi}\left[0{,}5772 + \ln\!\left(\ln\frac{T}{T-1}\right)\right]$$

| T (años) | 2 | 5 | 10 | 25 | 50 | 100 |
|---|---|---|---|---|---|---|
| K_T | −0,164 | 0,719 | 1,305 | 2,044 | 2,592 | 3,137 |

✍️ **Antes de ejecutar la celda siguiente:** con la media x̄ y la desviación estándar s que imprime la celda de
abajo (o calculadas tú mismo con la tabla de la sección 3), calcula **P₁₀ = x̄ + 1,305·s** y escríbela en
`P10_MANO` (celda 1).
""")
code(r'''
xm, sx = Pmax.mean(), Pmax.std(ddof=1)
print(f"n = {n} · x̄ = {xm:.1f} mm · s = {sx:.1f} mm   ← con estos dos números calculas P₁₀ a mano")
def KT(T): return -(np.sqrt(6) / np.pi) * (0.5772 + np.log(np.log(T / (T - 1))))
def PT_diaria(T): return xm + KT(T) * sx
alfa = np.sqrt(6) * sx / np.pi; u = xm - 0.5772 * alfa
Ts = np.array([2, 5, 10, 25, 50, 100])
G = pd.DataFrame({"T (años)": Ts, "K_T": KT(Ts), "P diaria (mm)": PT_diaria(Ts)})
display(G.round(3))
print(f"Parámetros: α = {alfa:.2f} mm · u = {u:.2f} mm   (P_T = u − α·ln(−ln(1 − 1/T)))")
if P10_MANO is not None:
    print(f"Tu P₁₀ a mano: {P10_MANO:.1f} mm · cuaderno: {PT_diaria(10):.1f} mm · diferencia {P10_MANO - PT_diaria(10):+.1f} mm")
else:
    print("✍️  Escribe tu P₁₀ a mano en P10_MANO para compararla.")
# Papel de Gumbel: variable reducida y = −ln(−ln(1 − 1/T))
fig, ax = plt.subplots(figsize=(8, 5))
y_obs = -np.log(-np.log(1 - 1 / W_["T (años)"]))
ax.scatter(y_obs, W_["P (mm)"], color="#12263A", zorder=3, label="Máximos observados (Weibull)")
yy = np.linspace(-1.6, 5, 50); ax.plot(yy, u + alfa * yy, color="#B3541A", lw=2, label="Gumbel (momentos)")
for T in (2, 5, 10, 25, 50, 100):
    yT = -np.log(-np.log(1 - 1 / T)); ax.axvline(yT, color="0.8", lw=0.6)
    ax.text(yT, 2, f"{T}", ha="center", va="bottom", fontsize=8, color="0.4")
ax.set_xlabel("Variable reducida de Gumbel y   (números grises: T en años)"); ax.set_ylabel("P máxima diaria de la cuenca (mm)")
ax.set_ylim(0, None); ax.legend(frameon=False); ax.grid(alpha=0.3)
ax.set_title(f"Ajuste de Gumbel · {CUENCA} · {PERIODO[0]}–{PERIODO[1]}", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p2_02_gumbel.png", dpi=150); plt.show()
''')

md(r"""
## 6 · ¿Gumbel sirve? ¿Cuánto confiar en P₁₀₀?
**Prueba de Kolmogorov–Smirnov:** compara la probabilidad acumulada empírica (Weibull) con la de Gumbel. Si la
máxima diferencia **D** es menor que el valor crítico (≈ 1,36/√n al 5 %), no hay razón para rechazar Gumbel.

**Error estándar del cuantil** (Gumbel por momentos):
$$S_T = \frac{s}{\sqrt n}\sqrt{1 + 1{,}1396\,K_T + 1{,}1\,K_T^2}$$
Con 20 años, estimar 100 años es **extrapolar**: el intervalo de ±2·S_T es la forma honesta de decirlo.
""")
code(r'''
from scipy import stats
F_obs = 1 - W_["P excedencia"].values
F_gum = np.exp(-np.exp(-(W_["P (mm)"].values - u) / alfa))
D_ks = np.max(np.abs(F_obs - F_gum)); D_crit = 1.36 / np.sqrt(n)
print(f"Kolmogorov–Smirnov: D = {D_ks:.3f} · D crítico (5 %) ≈ {D_crit:.3f} → "
      + ("Gumbel ACEPTADA" if D_ks < D_crit else "Gumbel RECHAZADA: discútelo en el capítulo"))
def ST(T): k = KT(T); return sx / np.sqrt(n) * np.sqrt(1 + 1.1396 * k + 1.1 * k ** 2)
G["S_T (mm)"] = ST(Ts); G["Banda −2S"] = G["P diaria (mm)"] - 2 * G["S_T (mm)"]; G["Banda +2S"] = G["P diaria (mm)"] + 2 * G["S_T (mm)"]
display(G.round(1))
print(f"P₁₀₀ diaria = {PT_diaria(100):.0f} mm, pero con ±2·S_T va de {PT_diaria(100) - 2 * ST(100):.0f} a {PT_diaria(100) + 2 * ST(100):.0f} mm.")
''')

md(r"""
## 7 · De lluvia diaria a lluvia de 24 horas, y el peso de El Niño
El pluviómetro se lee **una vez al día a las 07:00**: el máximo de un día fijo es menor que el máximo de
cualquier ventana de 24 horas (la tormenta puede quedar partida entre dos lecturas). Se corrige con el factor de
**Weiss (1964)**: P₂₄ = 1,13 · P diaria.

Luego se repite el ajuste con **toda la serie 1964–2018** (55 años) para ver cuánto cambia la lluvia de diseño
con la longitud del registro, y con El Niño 1982–83 y 1997–98 dentro.
""")
code(r'''
FACTOR_24H = 1.13
def PT24(T): return FACTOR_24H * PT_diaria(T)
Pmax_l = Pd_all.groupby(Pd_all.index.year).max()
xl, sl = Pmax_l.mean(), Pmax_l.std(ddof=1)
sin_nino = Pmax.drop([1997, 1998], errors="ignore")
xs_, ss_ = sin_nino.mean(), sin_nino.std(ddof=1)
C = pd.DataFrame({"T (años)": T_DISENO,
                  f"P24 {PERIODO[0]}–{PERIODO[1]} (mm)": [PT24(T) for T in T_DISENO],
                  "P24 1964–2018 (mm)": [FACTOR_24H * (xl + KT(T) * sl) for T in T_DISENO],
                  "P24 sin 1997–98 (mm)": [FACTOR_24H * (xs_ + KT(T) * ss_) for T in T_DISENO]})
display(C.round(0))
r100 = C.iloc[-1, 1] / C.iloc[-1, 3] - 1
print(f"Sin los dos años de El Niño, P24(100) baja {100 * r100:.0f} %: un solo evento pesa en la lluvia de diseño.")
print(f"P24 de diseño ({PERIODO[0]}–{PERIODO[1]}): " + " · ".join(f"T={T}: {PT24(T):.0f} mm" for T in T_DISENO))
''')

md(r"""
## 8 · Curvas intensidad–duración–frecuencia (IDF)
Para diseñar se necesita la lluvia de **duraciones cortas** (1 h, 3 h, 6 h), pero el INAMHI entrega lluvia
diaria. Sin pluviógrafos, se desagrega con la relación de **Dyck y Peschke (1978)**:
$$P_D = P_{24}\left(\frac{D}{1440}\right)^{0{,}25} \qquad I = \frac{P_D}{D/60}$$
con D en minutos e I en mm/h. Es una **aproximación**: el exponente 0,25 no se calibró en Manabí. Si tienes
la ecuación IDF del INAMHI para tu zona, compárala en el capítulo.

Después se ajusta la forma clásica **I = K·Tᵐ / Dⁿ** por mínimos cuadrados sobre los logaritmos.
""")
code(r'''
def P_D(D_h, T): return PT24(T) * (np.asarray(D_h, float) * 60 / 1440) ** 0.25
Dmin = np.array([10, 15, 30, 60, 120, 180, 360, 720, 1440])
Tidf = [2, 5, 10, 25, 50, 100]
IDF = pd.DataFrame({f"T={T}": P_D(Dmin / 60, T) / (Dmin / 60) for T in Tidf}, index=Dmin); IDF.index.name = "D (min)"
display(IDF.round(1))
X = np.array([[1, np.log(T), np.log(d)] for T in Tidf for d in Dmin]); Y = np.log([IDF.loc[d, f"T={T}"] for T in Tidf for d in Dmin])
b = np.linalg.lstsq(X, Y, rcond=None)[0]; K_idf, m_idf, n_idf = np.exp(b[0]), b[1], -b[2]
print(f"Ecuación IDF ajustada: I = {K_idf:.1f} · T^{m_idf:.3f} / D^{n_idf:.3f}   (I en mm/h, T en años, D en min)")
fig, ax = plt.subplots(figsize=(9, 5.5))
cols = plt.cm.YlGnBu(np.linspace(0.35, 1, len(Tidf)))
for T, c in zip(Tidf, cols):
    ax.plot(Dmin, IDF[f"T={T}"], marker="o", ms=4, color=c, label=f"T = {T} años")
ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(which="both", alpha=0.3)
ax.set_xticks(Dmin); ax.set_xticklabels(Dmin); ax.yaxis.set_major_formatter(plt.ScalarFormatter())
ax.set_xlabel("Duración D (min)"); ax.set_ylabel("Intensidad I (mm/h)"); ax.legend(frameon=False)
ax.set_title(f"Curvas IDF de la cuenca {CUENCA} (Gumbel + Dyck–Peschke)", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p2_03_idf.png", dpi=150); plt.show()
''')

md(r"""
## 9 · Hietogramas de diseño de 24 horas (método de los bloques alternos)
Un hietograma de diseño reparte la lluvia P₂₄ en 24 bloques de una hora de modo que **cualquier duración
centrada** tenga la lluvia de la curva IDF:
1. Con la IDF, P_D para D = 1, 2, …, 24 h.
2. Incrementos: ΔP_k = P_k − P_{k−1}.
3. El bloque mayor va al centro (hora 12); los siguientes, alternando derecha e izquierda.

> **Analogía.** Es como armar un pastel por capas: la capa más gruesa al centro y las demás, cada vez más
> delgadas, a uno y otro lado. El total de las capas es P₂₄.

Estos hietogramas son el **insumo del paso 3** (lluvia efectiva) y del paso 4 (hidrograma).
""")
code(r'''
def hietograma(T, dur_h=24, dt_h=1):
    D = np.arange(dt_h, dur_h + dt_h, dt_h); inc = np.sort(np.diff(np.r_[0, P_D(D, T)]))[::-1]
    nb = len(D); c = (nb - 1) // 2; idx = [c]; k = 1
    while len(idx) < nb:
        if c + k < nb: idx.append(c + k)
        if len(idx) < nb and c - k >= 0: idx.append(c - k)
        k += 1
    orden = np.zeros(nb); orden[idx] = inc
    return pd.Series(orden, index=D, name=f"T{T}")
H = pd.concat([hietograma(T) for T in T_DISENO], axis=1); H.index.name = "hora"
fig, axs = plt.subplots(1, len(T_DISENO), figsize=(13, 4), sharey=True)
for ax, T in zip(axs, T_DISENO):
    ax.bar(H.index - 0.5, H[f"T{T}"], width=1, align="edge", color="#1F6F8B", ec="white")
    ax.set_title(f"T = {T} años · P24 = {H[f'T{T}'].sum():.0f} mm", fontweight="bold"); ax.set_xlabel("Hora")
    ax.set_xticks([0, 6, 12, 18, 24]); ax.grid(axis="y", alpha=0.3)
axs[0].set_ylabel("Lluvia (mm/h)")
fig.suptitle(f"Hietogramas de diseño de 24 h · {CUENCA} · bloques alternos", fontweight="bold")
plt.tight_layout(); plt.savefig("salidas/P2p2_04_hietogramas_diseno.png", dpi=150); plt.show()
for T in T_DISENO:
    h = H[f"T{T}"]; print(f"T={T}: hora pico {h.idxmax()} con {h.max():.1f} mm · las 3 h centrales suman {h.loc[11:13].sum():.0f} mm ({100 * h.loc[11:13].sum() / h.sum():.0f} %)")
''')

md("## 10 · Expediente del capítulo 2 y descarga")
code(r'''
f = f"P2_paso2 · Gumbel momentos · INAMHI {PERIODO[0]}–{PERIODO[1]}"
exp = [("2.4", "Estación de mayor peso (comparación puntual)", f"{e1} {NOMBRE[e1]}", "", f),
       ("2.4", "Máximos anuales usados", n, "años", f),
       ("2.4", "Media de los máximos (x̄)", round(xm, 1), "mm", f),
       ("2.4", "Desviación de los máximos (s)", round(sx, 1), "mm", f),
       ("2.4", "Máximo anual mayor", f"{Pmax.max():.0f} mm ({Pmax.idxmax()})", "", f),
       ("2.4", "Factor de reducción por área (cuenca/punto)", round(FRA, 2), "—", f),
       ("2.4", "Gumbel α", round(alfa, 2), "mm", f), ("2.4", "Gumbel u", round(u, 2), "mm", f),
       ("2.4", "Kolmogorov–Smirnov D", round(D_ks, 3), "—", f), ("2.4", "KS D crítico 5 %", round(D_crit, 3), "—", f),
       ("2.4", "P10 diaria a mano", P10_MANO if P10_MANO is not None else "", "mm", "estudiante"),
       ("2.4", "Factor lluvia diaria → 24 h", FACTOR_24H, "—", "Weiss (1964)")]
for T in T_DISENO:
    exp += [("2.4", f"P diaria T={T}", round(PT_diaria(T), 1), "mm", f),
            ("2.4", f"P24 T={T}", round(PT24(T), 1), "mm", f),
            ("2.4", f"P24 T={T} banda ±2S", f"{FACTOR_24H * (PT_diaria(T) - 2 * ST(T)):.0f}–{FACTOR_24H * (PT_diaria(T) + 2 * ST(T)):.0f}", "mm", f),
            ("2.4", f"P24 T={T} con 1964–2018", round(FACTOR_24H * (xl + KT(T) * sl), 1), "mm", f)]
exp += [("2.4", "IDF K", round(K_idf, 2), "—", "Dyck–Peschke (1978)"), ("2.4", "IDF m", round(m_idf, 4), "—", "Dyck–Peschke (1978)"),
        ("2.4", "IDF n", round(n_idf, 4), "—", "Dyck–Peschke (1978)"),
        ("2.4", "Hietograma de diseño", "24 h, bloques de 1 h, alternos, pico en la hora 12", "", f)]
EXP = pd.DataFrame([("2",) + x for x in exp], columns=["capitulo", "apartado", "campo", "valor", "unidad", "fuente"])
EXP.to_csv(f"salidas/expediente_P2p2_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
H.to_csv(f"salidas/hietogramas_diseno_{CUENCA}_{SLUG}.csv", encoding="utf-8-sig")
IDF.to_csv(f"salidas/idf_{CUENCA}_{SLUG}.csv", encoding="utf-8-sig")
W_.to_csv(f"salidas/maximos_anuales_{CUENCA}_{SLUG}.csv", index=False, encoding="utf-8-sig")
import shutil
paquete = shutil.make_archive(f"Practica2_Paso2_{CUENCA}_{SLUG}", "zip", "salidas")
print("✅ Paquete:", paquete)
try:
    from google.colab import files; files.download(paquete)
except ImportError:
    print("Descárgalo desde el panel de archivos de Colab.")
EXP
''')

md(r"""
---
## Para tu capítulo 2 · apartado 2.4 (cinco líneas debajo de cada figura)
1. **Máximos anuales.** ¿En qué meses ocurren? ¿Qué años sobresalen y por qué? ¿Cuánto menor es la lluvia media
   de la cuenca que la del punto (factor de reducción por área)?
2. **Gumbel.** ¿Coincide tu P₁₀ a mano? ¿Los puntos observados siguen la recta? ¿Qué dice la prueba KS?
3. **Incertidumbre.** ¿Entre qué valores puede estar P₁₀₀? ¿Qué pasa si quitas El Niño 1997–98 o usas 55 años?
   ¿Qué valor recomendarías para una obra y por qué?
4. **IDF y hietogramas.** ¿Qué intensidad tendría una lluvia de 1 h para T = 25 años? ¿Qué límite tiene la
   desagregación de Dyck–Peschke?
""")
save(sys.argv[1] if len(sys.argv) > 1 else "P2_paso2_lluvia_diseno.ipynb")
