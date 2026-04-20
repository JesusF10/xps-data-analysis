# XPS Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Software automatizado en Python para análisis de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS).

---

## Funcionalidades Principales

El proyecto está estructurado en módulos especializados con un enfoque matemático, validación estricta (Pydantic v2) e inmutabilidad de los datos científicos.

| Módulo | Funciones Principales | Características Técnicas |
| :--- | :--- | :--- |
| **`data_loader`** | Carga y estructuración de espectros y datasets. | Auto-detección de formato, validación dimensional de arrays (NumPy). |
| **`preprocessing`** | Calibración del eje de energía de enlace. | Corrección por elemento de referencia (ej. Ti 2p, O 1s), operaciones inmutables. |
| **`analysis`** | Sustracción de fondo, deconvolución de picos y cuantificación atómica. | Fondos Shirley/Tougaard/Linear; perfiles Voigt/Gaussian/Lorentzian; RSF Scofield/Wagner. |
| **`reference_data`**| Búsqueda de líneas fotoelectrónicas y orbitales. | Base de datos JSON, patrón singleton con caché en memoria. |
| **`export`** | Salida de datos a formatos estandarizados (CSV, Excel, JSON). | Codificador JSON personalizado para tipos NumPy, metadatos jerárquicos. |
| **`gui` / `cli`** | Interfaces de usuario para análisis exploratorio e iterativo. | Aplicación interactiva basada en Streamlit y utilidades de terminal con Click. |

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

### Interfaz Gráfica (GUI)

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
│   ├── analysis/            # Análisis core
│   ├── gui/                 # Interfaz gráfica (Streamlit)
│   ├── export/              # Exportación (CSV, Excel, JSON)
│   ├── reference_data/      # Base de datos de elementos
│   ├── visualization/       # Plotting estilo científico
│   └── cli/                 # Interfaz CLI
├── tests/                   # Tests (355 tests, 93% coverage)
└── config/                  # Archivos de configuración TOML
```

---



## Contribuir

**Prioridades actuales:**

1. Mejoras en la interactividad de la GUI.
2. Visualización avanzada.
3. Documentación de API avanzada.

**Lee:** [CONTRIBUTING.md](CONTRIBUTING.md) antes de contribuir.

---

## Testing

```bash
# Ejecutar todos los tests
uv run pytest tests/

# Con cobertura
uv run pytest tests/ --cov=src --cov-report=term-missing
```

**Estado actual:** 93% coverage (355 tests pasando)

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

**Autor:** Jesus Flores Lacarra  
**Email:** jss.263.fsc@gmail.com
