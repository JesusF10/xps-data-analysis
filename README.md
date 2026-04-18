# XPS Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Software automatizado en Python para análisis de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS).

**Estado:** Beta v0.8.0-beta - Fase 2 EN PROGRESO  
**Fase:** 2 (Pydantic + GUI Interactiva) - 60% completado

---

## Características

[COMPLETADO] **Disponible:**

- Carga de datos XPS desde formatos propietarios
- Calibración de energía por elemento de referencia
- Visualización básica de espectros
- Base de datos de ~25 elementos comunes
- CLI para operaciones básicas
- Sustracción de fondo (Shirley, Tougaard, Linear)
- Ajuste de picos (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL)
- Cuantificación atómica con factores RSF (Scofield, Wagner)
- **Exportación completa a CSV, Excel y JSON**
- **Migración total a Pydantic v2** para validación robusta
- **Interfaz gráfica interactiva (Streamlit)** con estilo científico

[EN DESARROLLO] **Próximamente:**

- Visualización avanzada con Plotly
- Análisis interactivo en tiempo real en la GUI
- Reportes automáticos en PDF

---

## Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# Instalar con uv (recomendado)
uv sync --group dev --group jupyter

# Verificar instalación
uv run xps-analyzer --version
```

**Instalación detallada:** Ver [INSTALLATION.md](INSTALLATION.md)

---

## Uso Básico

### Interfaz Gráfica (GUI) - ¡Nuevo!

La forma más sencilla de usar XPS Analyzer es a través de su interfaz interactiva:

```bash
uv run streamlit run src/xps_analyzer/gui/app.py
```

### Ejemplo de Script de Análisis

```python
from xps_analyzer import load_single_file
from xps_analyzer.analysis import (
    shirley_background,
    fit_gaussian,
    load_sensitivity_factors,
    calculate_atomic_concentration
)
from xps_analyzer.export import export_to_excel

# 1. Cargar y calibrar
dataset = load_single_file("data/raw/samples/muestra1.txt")
c1s = dataset.get_spectrum("C 1s")

# 2. Procesar (Fondo + Ajuste)
c1s_nobg = shirley_background(c1s, inplace=False)
fit_result = fit_gaussian(c1s_nobg, position=284.8)

# 3. Exportar resultados
export_to_excel(dataset, "resultados_analisis.xlsx")
```

---

## Estructura del Proyecto

```
xps-data-analysis/
├── src/xps_analyzer/        # Código fuente
│   ├── data_loader/         # Carga de datos
│   ├── preprocessing/       # Calibración, normalización
│   ├── analysis/            # Análisis core (COMPLETADO 100%)
│   ├── gui/                 # Interfaz gráfica (Streamlit)
│   ├── export/              # Exportación (CSV, Excel, JSON)
│   ├── reference_data/      # Base de datos de elementos
│   ├── visualization/       # Plotting estilo científico
│   └── cli/                 # Interfaz CLI
├── tests/                   # Tests (326 tests, 72% coverage)
└── config/                  # Archivos de configuración TOML
```

---

## Roadmap

### Fase 1 - Análisis Core [100% COMPLETADO]

- [x] Sustracción de fondo (Shirley, Tougaard, Linear)
- [x] Ajuste de picos (Gaussian, Lorentzian, Voigt)
- [x] Cuantificación atómica (RSF Scofield/Wagner)
- [x] Exportación (CSV, Excel, JSON)
- [x] 326 tests unitarios pasando

### Fase 2 - Pydantic + GUI Interactiva [EN PROGRESO]

- [x] Migración a Pydantic para validación (100%)
- [x] GUI inicial con Streamlit (Estilo científico)
- [ ] Visualización avanzada con Plotly
- [ ] Análisis interactivo en tiempo real
- [ ] Target: 85% test coverage

---

## Contribuir

**Prioridades actuales:**

1. **Alta:** Mejoras en la interactividad de la GUI (Streamlit).
2. **Media:** Visualización avanzada con Plotly.
3. **Baja:** Documentación de API avanzada.

**Lee:** [CONTRIBUTING.md](CONTRIBUTING.md) antes de contribuir.

---

## Testing

```bash
# Ejecutar todos los tests
uv run pytest tests/

# Con cobertura
uv run pytest tests/ --cov=src --cov-report=term-missing
```

**Estado actual:** 72% coverage (326 tests pasando)  
**Objetivo Fase 2:** >=85% coverage

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

**Autor:** Jesus Flores Lacarra  
**Email:** jss.263.fsc@gmail.com
