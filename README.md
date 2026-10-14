# Hidrología (1CIA-502) · Prácticas en Colab

Ingeniería Ambiental · 5.º nivel · Escuela Superior Politécnica Agropecuaria de Manabí
*Manuel Félix López* (ESPAM MFL)

Docente: Ing. Cristian Paliz Acosta, MSc. · ORCID 0000-0002-1738-8131

---

## Cómo trabajar una práctica

1. Pulsa el botón **Open in Colab** de la práctica.
2. En Colab: **Archivo → Guardar una copia en Drive**. Trabajas sobre tu copia.
3. Edita solo la **celda 1** (tu nombre, tu cuenca, tu exutorio y tus valores a mano).
4. Ejecuta las celdas en orden con **Shift + Enter**.
5. Descarga el ZIP de resultados al final.

Los datos se descargan solos desde [datos-manabi](https://github.com/crispaliz/datos-manabi):
no necesitas Drive ni bajar nada a mano.

**Regla del curso: mano antes que modelo.** Antes de ejecutar, calcula a mano lo que
el cuaderno va a calcular, y al final explica la diferencia.

---

## Prácticas

| Práctica | Tema | Cuaderno |
|---|---|---|
| 1 · paso 2 | Delimitación desde el MDE, tabla morfométrica y ficha de la estación | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/crispaliz/hidrologia-espam/blob/main/notebooks/P1_paso2_delimitacion_morfometria.ipynb) |

## Cuencas disponibles

Ayampe · Carrizal · Chone · Jama · Jipijapa · Portoviejo

---

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| *Falló la descarga* | Revisa el nombre de la cuenca en la celda 1: mayúscula inicial y sin tildes |
| La cuenca sale muy pequeña | Revisa tu `EXUTORIO`; si cae en un afluente, sube `AJUSTE_KM2` |
| El cuaderno va lento | Sube `FACTOR_REMUESTREO` a 4 |
| Se cortó la energía o la conexión | Vuelve a ejecutar desde la celda 0; tu copia en Drive conserva la celda 1 |

---

Licencia: CC BY-NC-SA 4.0 (ver `LICENSE`). Los datos tienen su propia licencia en
[datos-manabi](https://github.com/crispaliz/datos-manabi).
