# XPS Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Software automatizado en Python para análisis de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS).

**Estado:** Beta v0.7.0 - Análisis core funcional  
**Fase:** 1 (Análisis Core) - 75% completado

---

## Características

[COMPLETADO] **Disponible:**

- Carga de datos XPS desde formatos propietarios
- Calibración de energía por elemento de referencia
- Visualización básica de espectros
- Base de datos de ~25 elementos comunes
- CLI para operaciones básicas
- **Sustracción de fondo (Shirley, Tougaard, Linear)**
- **Ajuste de picos (Gaussian, Lorentzian, Voigt)**
- **Cuantificación atómica con factores RSF (Scofield, Wagner)**

[EN DESARROLLO] **En Desarrollo (Fase 1):**

- Exportación a CSV/Excel/JSON (próxima sesión)

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

### Cargar y Visualizar Datos

```python
from xps_analyzer import load_single_file

# Cargar archivo XPS
dataset = load_single_file("data/raw/samples/muestra1.txt")

# Listar regiones disponibles
print(dataset.list_regions())
# ['survey', 'C 1s', 'O 1s', 'N 1s']

# Obtener espectro específico
spectrum = dataset.get_spectrum("C 1s")
print(f"Región: {spectrum.region_name}")
print(f"Puntos de datos: {len(spectrum.binding_energy)}")
```

### Calibración de Energía

```python
from xps_analyzer.preprocessing import calibrate_spectrum

# Calibrar usando C 1s como referencia (284.8 eV)
spectrum_calibrated = calibrate_spectrum(
    spectrum,
    reference_element="C",
    reference_energy=284.8,
    inplace=False
)
```

### Análisis Completo de XPS (NUEVO en v0.7.0)

```python
from xps_analyzer import load_single_file
from xps_analyzer.analysis import (
    shirley_background,
    fit_gaussian,
    load_sensitivity_factors,
    calculate_atomic_concentration
)

# 1. Cargar datos
dataset = load_single_file("data/raw/samples/muestra1.txt")
c1s_spectrum = dataset.get_spectrum("C 1s")
o1s_spectrum = dataset.get_spectrum("O 1s")

# 2. Sustracción de fondo
c1s_nobg = shirley_background(c1s_spectrum, inplace=False)
o1s_nobg = shirley_background(o1s_spectrum, inplace=False)

# 3. Ajuste de picos
c_fit = fit_gaussian(c1s_nobg, position=284.8)
o_fit = fit_gaussian(o1s_nobg, position=531.0)

print(f"R² C 1s: {c_fit.r_squared:.4f}")
print(f"Área C 1s: {c_fit.peaks[0].area:.2f}")

# 4. Cuantificación atómica
rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")
concentrations = calculate_atomic_concentration(
    peaks=[c_fit.peaks[0], o_fit.peaks[0]],
    sensitivity_factors=rsf,
    element_names=["C 1s", "O 1s"]
)

print("\nComposición atómica:")
for element, conc in concentrations.items():
    print(f"  {element}: {conc:.2f}%")
# Salida:
#   C 1s: 75.02%
#   O 1s: 24.98%
```

### Ajuste de Múltiples Picos

```python
from xps_analyzer.analysis import fit_multiple_peaks

# Ajustar espectro C 1s con 3 componentes
result = fit_multiple_peaks(
    c1s_spectrum,
    n_peaks=3,
    peak_shape="voigt",
    initial_positions=[284.8, 286.2, 288.5]  # C-C, C-O, C=O
)

print(f"Picos encontrados: {len(result.peaks)}")
for i, peak in enumerate(result.peaks):
    print(f"Pico {i+1}: {peak.position:.2f} eV, Área: {peak.area:.2f}")
```

### Visualización

```python
from xps_analyzer.visualization import plot_spectrum

# Plotear espectro
plot_spectrum(spectrum)

```

### CLI

```bash
# Analizar directorio de datos
xps-analyzer analyze data/raw/samples/

# Mostrar información de elemento
xps-analyzer show-element C
```

---

## Estructura del Proyecto

```
xps-data-analysis/
├── src/xps_analyzer/        # Código fuente
│   ├── data_loader/         # Carga de datos
│   ├── preprocessing/       # Calibración, normalización
│   ├── analysis/            # Análisis core (COMPLETADO 75%)
│   │   ├── background.py    # Sustracción de fondo
│   │   ├── peak_fitting.py  # Ajuste de picos
│   │   └── quantification.py # Cuantificación atómica
│   ├── reference_data/      # Base de datos de elementos
│   ├── visualization/       # Plotting
│   └── cli/                 # Interfaz CLI
├── config/                  # Archivos de configuración TOML
├── data/                    # Datos y resultados
├── tests/                   # Tests (cobertura 87%)
└── docs/                    # Documentación adicional
```

---

## Documentación

- **[INSTALLATION.md](INSTALLATION.md)** - Guía de instalación detallada
- **[CONTEXT.md](CONTEXT.md)** - Contexto completo del proyecto
- **[ROADMAP.md](ROADMAP.md)** - Plan de desarrollo por fases
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Cómo contribuir
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guía para desarrolladores
- **[API_DOCS.md](API_DOCS.md)** - Referencia completa de API
- **[TESTING.md](TESTING.md)** - Estrategia de testing
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios

---

## Roadmap

### Fase 0 - Fundamentos [COMPLETADO]

- [x] Carga básica de datos
- [x] Calibración de energía
- [x] Visualización simple
- [x] CLI básico
- [x] Validación manual de datos
- [x] Tests básicos (90 tests, 80% coverage)

### Fase 1 - Análisis Core [75% COMPLETADO]

- [x] Sustracción de fondo (Shirley, Tougaard, Linear) - 96% cobertura
- [x] Ajuste de picos (Gaussian, Lorentzian, Voigt) - 95% cobertura
- [x] Cuantificación atómica (RSF Scofield/Wagner) - 85% cobertura
- [ ] Exportación (CSV, Excel, JSON) - **Próxima sesión**
- [ ] Sistema de configuración TOML
- [x] 87% test coverage (208 tests)

### Fase 2 - Robustez

- [ ] Migración a Pydantic para validación
- [ ] Soporte VAMAS (ISO 14976)
- [ ] Soporte CASA XPS
- [ ] Exportación HDF5
- [ ] 90% test coverage

### Fase 3 - Avanzado

- [ ] Machine learning para identificación automática
- [ ] Análisis de profundidad (depth profiling)
- [ ] GUI con Streamlit/Dash
- [ ] API REST con FastAPI

**Ver roadmap completo:** [ROADMAP.md](ROADMAP.md)

---

## Contribuir

¡Las contribuciones son bienvenidas! Especialmente para funcionalidad Fase 1.

**Prioridades:**

1. [COMPLETADO] ~~Sustracción de fondo, ajuste de picos, cuantificación~~
2. **Alta:** Exportación (CSV, Excel, JSON) - **Próxima sesión**
3. **Media:** Sistema de configuración TOML
4. **Baja:** Características avanzadas (Fase 3)

**Proceso:**

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

**Lee:** [CONTRIBUTING.md](CONTRIBUTING.md) antes de contribuir.

---

## Dependencias Principales

- **numpy** (>=1.21.0) - Arrays numéricos
- **pandas** (>=1.3.0) - DataFrames
- **matplotlib** (>=3.4.0) - Visualización
- **scipy** (>=1.7.0) - Procesamiento de señales, ajuste de picos
- **click** (>=8.0.0) - Framework CLI
- **lmfit** (>=1.2.0) - Ajuste de picos avanzado (planeado)
- **openpyxl** (>=3.1.0) - Exportación Excel (próxima sesión)

**Ver lista completa:** [pyproject.toml](pyproject.toml)

---

## Testing

```bash
# Ejecutar todos los tests
uv run pytest tests/

# Con cobertura
uv run pytest tests/ --cov=src --cov-report=html

# Ver reporte
open htmlcov/index.html
```

**Estado actual:** 87% coverage (208 tests pasando) [OBJETIVO SUPERADO]  
**Objetivo Fase 1:** >=80% coverage [COMPLETADO]

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## Contacto

**Autor:** Jesus Flores Lacarra  
**Email:** jss.263.fsc@gmail.com  
**GitHub:** [@JesusF10](https://github.com/JesusF10)

**Repositorio:** https://github.com/JesusF10/xps-data-analysis  
**Issues:** https://github.com/JesusF10/xps-data-analysis/issues

---

## Agradecimientos

- **NIST XPS Database** - Datos de referencia de elementos
- **Comunidad XPS** - Feedback y sugerencias
- **Astral (uv, ruff)** - Herramientas de desarrollo modernas

---

## Referencias

- Shirley, D. A. (1972). "High-Resolution X-Ray Photoemission Spectrum of Valence Bands of Gold"
- Tougaard, S. (2020). "Practical guide to the use of backgrounds in quantitative XPS"
- ISO 14976:1998 - Formato VAMAS para datos de espectroscopía de superficie
