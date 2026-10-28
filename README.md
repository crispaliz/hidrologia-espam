# Hidrología (1CIA-502) · Prácticas en Colab

Ingeniería Ambiental · 5.º nivel · Escuela Superior Politécnica Agropecuaria de Manabí
*Manuel Félix López* (ESPAM MFL)

Docente: Ing. Cristian Paliz Acosta, MSc. · ORCID 0000-0002-1738-8131

---

## Cómo trabajar una práctica

1. Pulsa el botón **Open in Colab** de la práctica.
2. En Colab: **Archivo → Guardar una copia en Drive**. Trabajas sobre tu copia.
3. Edita solo la **celda 1** (tu nombre, tu cuenca, tu exutorio y tus valores a mano).
   Usa el **mismo nombre y la misma cuenca** en todos los cuadernos.
4. Ejecuta las celdas en orden con **Shift + Enter**.
5. Descarga el ZIP de resultados al final.

Los datos se descargan solos desde [datos-manabi](https://github.com/crispaliz/datos-manabi):
no necesitas Drive ni bajar nada a mano.

**Regla del curso: mano antes que modelo.** Antes de ejecutar, calcula a mano lo que
el cuaderno va a calcular, y al final explica la diferencia.

---

## Prácticas

### Unidad I · Hidrometría → Capítulo 1: ficha morfométrica e hidrométrica

| Práctica | Tema | Produce | Cuaderno |
|---|---|---|---|
| 1 · paso 2 | Delimitación desde el MDE, tabla morfométrica y ficha de la estación | `expediente_P2_….csv`, figuras `P2_…` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/crispaliz/hidrologia-espam/blob/main/notebooks/P1_paso2_delimitacion_morfometria.ipynb) |
| 1 · paso 3 | Curva de gasto, serie de caudal y curva de duración | `expediente_P3_….csv`, figuras `P3_…` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/crispaliz/hidrologia-espam/blob/main/notebooks/P1_paso3_curvas.ipynb) |
| 1 · cierre | Ficha de síntesis del capítulo 1 y expediente de la cuenca | `expediente_<cuenca>_<estudiante>.csv`, ficha en PNG y PDF | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/crispaliz/hidrologia-espam/blob/main/notebooks/P1_ficha_capitulo1.ipynb) |

El aforo con flotadores (21 de octubre) se calcula a mano en la hoja de campo y se copia en la celda 1 del cuaderno de cierre.

## El expediente de tu cuenca

Cada práctica guarda sus resultados en un mismo formato (`capitulo, apartado, campo, valor, unidad, fuente`).
El cuaderno de cierre de cada unidad los une en **`expediente_<cuenca>_<estudiante>.csv`**, que crece capítulo a capítulo:

| Capítulo | Unidad | Qué añade al expediente |
|---|---|---|
| 1 | I · Hidrometría | Morfometría, estación de referencia, aforo, curva de gasto y curva de duración |
| 2 | II · Precipitación y escorrentía | Precipitación media, lluvia de diseño, número de curva |
| 3 | III · Modelación | Eventos simulados en HEC-HMS y su desempeño |
| 4 | IV · Agua subterránea | Flujo base y parámetros del acuífero |

Guarda el expediente: es la entrada de la unidad siguiente y la base del proyecto integrador final.
Los expedientes del curso forman el *Compendio hidrológico de cuencas de Manabí*.

## Datos del curso

- `datos/aforos_ejemplo.csv` y `datos/niveles_diarios_ejemplo.csv`: datos **ilustrativos** para el paso 3.
  No son de ninguna cuenca; si los usas, decláralo. Si tienes datos de una estación del INAMHI,
  pon `USAR_MIS_DATOS = True` y sube tus CSV con las mismas columnas.
- Relieve, cuencas, cauces y estaciones: [datos-manabi](https://github.com/crispaliz/datos-manabi).

## Cuencas disponibles

Ayampe · Carrizal · Chone · Jama · Jipijapa · Portoviejo

---

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| *Falló la descarga* | Revisa el nombre de la cuenca en la celda 1: mayúscula inicial y sin tildes |
| La cuenca sale muy pequeña | Revisa tu `EXUTORIO`; si cae en un afluente, sube `AJUSTE_KM2` |
| El cuaderno va lento | Sube `FACTOR_REMUESTREO` a 4 |
| El cuaderno de cierre dice *Falta el expediente* | Vuelve a ejecutar el paso 2 o 3 con la versión actual del repositorio y sube su ZIP |
| Se cortó la energía o la conexión | Vuelve a ejecutar desde la celda 0; tu copia en Drive conserva la celda 1 |

---

Licencia: CC BY-NC-SA 4.0 (ver `LICENSE`). Los datos tienen su propia licencia en
[datos-manabi](https://github.com/crispaliz/datos-manabi).
