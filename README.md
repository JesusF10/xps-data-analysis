# XPS Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Software automatizado en Python para análisis de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS).

**Estado:** Alpha v0.1.0 - En desarrollo activo  
**Fase:** 0 (Fundamentos) - 35% completado

---

## Características

[COMPLETADO] **Disponible:**
- Carga de datos XPS desde formatos propietarios
- Calibración de energía por elemento de referencia
- Visualización básica de espectros
- Base de datos de ~25 elementos comunes
- CLI para operaciones básicas

[EN DESARROLLO] **En Desarrollo (Fase 1):**
- Sustracción de fondo (Shirley, Tougaard)
- Ajuste de picos (Gaussian, Lorentzian, Voigt)
- Cuantificación con factores de sensibilidad
- Exportación a CSV/Excel/JSON

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
│   ├── analysis/            # Análisis core (EN DESARROLLO)
│   ├── reference_data/      # Base de datos de elementos
│   ├── visualization/       # Plotting
│   └── cli/                 # Interfaz CLI
├── config/                  # Archivos de configuración TOML
├── data/                    # Datos y resultados
├── tests/                   # Tests (cobertura <20%)
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

### Fase 0 (Actual) - Fundamentos
- [x] Carga básica de datos
- [x] Calibración de energía
- [x] Visualización simple
- [x] CLI básico
- [x] Validación manual de datos
- [ ] Tests básicos (20% coverage)

### Fase 1 - Análisis Core
- [ ] Sustracción de fondo (Shirley, Tougaard)
- [ ] Ajuste de picos (Gaussian, Lorentzian, Voigt)
- [ ] Cuantificación
- [ ] Exportación (CSV, Excel, JSON)
- [ ] Sistema de configuración TOML
- [ ] 60% test coverage

### Fase 2 - Robustez
- [ ] Migración a Pydantic para validación
- [ ] Soporte VAMAS (ISO 14976)
- [ ] Soporte CASA XPS
- [ ] Exportación HDF5
- [ ] 80% test coverage

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
1. 🔥 **Alta:** Sustracción de fondo, ajuste de picos
2. [EN PROGRESO] **Media:** Tests, documentación
3. [COMPLETADO] **Baja:** Características avanzadas (Fase 3)

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
- **scipy** (>=1.7.0) - Procesamiento de señales
- **click** (>=8.0.0) - Framework CLI
- **pydantic** (>=2.12.4) - Validación (Fase 2)

**Ver lista completa:** [pyproject.toml](pyproject.toml)

---

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Ver reporte
open htmlcov/index.html
```

**Estado actual:** <20% coverage ([EN PROGRESO] insuficiente)  
**Objetivo Fase 1:** >=60% coverage

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
