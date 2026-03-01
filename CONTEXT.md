# XPS Analyzer - Contexto Completo del Proyecto

**Versión:** 0.1.0  
**Estado:** Fase 0 (35% completado)  
**Última actualización:** Febrero 2026

Este documento proporciona contexto completo para agentes de IA, desarrolladores y colaboradores sobre el proyecto XPS Analyzer.

---

## Resumen Ejecutivo

**XPS Analyzer** es un paquete Python científico para análisis automatizado de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS), desarrollado como proyecto de servicio social en investigación de química y metalurgia. El software carga formatos propietarios de datos XPS, realiza calibración de energía, identifica elementos/compuestos y genera reportes analíticos.

**Estado actual:** Funcionalidad básica de carga y visualización implementada. Falta análisis completo (sustracción de fondo, ajuste de picos, cuantificación).

**Público objetivo:**
- Investigadores en química de superficies
- Laboratorios de caracterización de materiales
- Estudiantes de posgrado en ciencia de materiales

---

## Arquitectura del Proyecto

### Jerarquía del Modelo de Datos

El proyecto utiliza una jerarquía de tres niveles basada en `@dataclass` (ubicada en `src/xps_analyzer/data_loader/core.py`):

```python
@dataclass
class XPSSpectrum:
    """Espectro individual: arrays de binding_energy + intensity + metadata"""
    region_name: str
    binding_energy: np.ndarray  # eV
    intensity: np.ndarray       # cuentas arbitrarias
    metadata: dict[str, Any]
    
    def __post_init__(self):
        """Validación manual: longitudes coincidentes, no vacíos, energías positivas"""

@dataclass
class XPSDataset:
    """Archivo completo con múltiples espectros (survey + regiones)"""
    filename: str
    header: dict[str, Any]
    spectra: dict[str, XPSSpectrum]  # key = region_name

@dataclass
class XPSSample:
    """Colección de datasets relacionados (múltiples archivos de una muestra)"""
    sample_name: str
    datasets: dict[str, XPSDataset]  # key = filename
```

**Patrón importante:** Siempre usar métodos `.copy()` al modificar espectros para evitar mutar estado compartido. Las funciones usan parámetro `inplace=bool` (ej: `calibrate_spectrum()`) para controlar mutación vs. copia.

### Sistema de Datos de Referencia

La base de datos de elementos (`src/xps_analyzer/reference_data/`) usa patrón singleton con cache global:

- `load_reference_database()` retorna instancia en cache de `ReferenceDatabase` en llamadas subsecuentes
- Deserializador JSON en `_dict_to_element_reference()` maneja líneas fotoelectrónicas anidadas y datos de compuestos
- Búsquedas de energía de enlace usan parámetro `tolerance` (default 2.0 eV) para coincidencia difusa

**Elementos soportados:** ~25 elementos comunes en XPS (C, O, N, Si, Al, Fe, Ti, Cu, Au, etc.)

### Detección de Formato de Archivo

El cargador de datos (`core.py:216-268`) auto-detecta tipos de archivo:

- **"multiplex" en nombre de archivo** -> formato multi-región con header (metadata de 3 líneas + múltiples secciones Element)
- **Default** -> espectro survey único
- **Parser:** usa delimitadores `;` para metadata, valores separados por espacio para columnas de datos

**Estado actual:** Solo soporta un formato propietario de texto. **Fase 2** agregará VAMAS, CASA XPS, HDF5.

---

## Estructura de Módulos

```
src/xps_analyzer/
├── __init__.py              # API de alto nivel: load_single_file(), load_reference_database()
├── data_loader/             # [COMPLETADO] 70% completo
│   ├── core.py             # Clases principales + parsing
│   └── __init__.py         # Re-exporta XPSSpectrum, XPSDataset, XPSSample
├── preprocessing/           # [EN PROGRESO] 25% completo
│   ├── calibration.py      # Calibración básica implementada
│   └── __init__.py         # Falta: background subtraction, smoothing, normalization
├── analysis/                # [PENDIENTE] 0% - MÓDULO VACÍO (GAP CRÍTICO)
│   └── __init__.py         # Falta: peak fitting, quantification, deconvolution
├── reference_data/          # [COMPLETADO] 85% completo
│   ├── elements.py         # Clases de referencia + carga JSON
│   ├── identification.py   # Identificación de elementos por energía
│   ├── data/               # Base de datos JSON de elementos
│   └── __init__.py
├── visualization/           # [EN PROGRESO] 20% completo
│   ├── plotting.py         # Plots básicos (survey, region)
│   └── __init__.py         # Falta: plots avanzados, reports interactivos
├── export/                  # [PENDIENTE] 0% - MÓDULO VACÍO
│   └── __init__.py         # Falta: exportar CSV, Excel, JSON, HDF5
├── cli/                     # [EN PROGRESO] 40% completo
│   ├── main.py             # Comandos básicos: analyze, show-element
│   └── __init__.py         # Falta: más comandos, validación robusta
└── utils/                   # [PENDIENTE] 0% - MÓDULO VACÍO
    └── __init__.py         # Falta: helpers, validators, decorators
```

### Estado de Implementación por Módulo

| Módulo | Estado | Tests | Issues Críticos |
|--------|--------|-------|-----------------|
| `data_loader` | 70% | 4 tests (15% cov) | Parsing hardcoded, bug IndexError |
| `preprocessing` | 25% | 0 tests | Falta background subtraction |
| `analysis` | 0% | N/A | **MÓDULO VACÍO** |
| `reference_data` | 85% | 0 tests | Bugs en elementos.py:170,176 |
| `visualization` | 20% | 0 tests | Solo plots básicos |
| `export` | 0% | N/A | **MÓDULO VACÍO** |
| `cli` | 40% | 0 tests | Falta validación de inputs |
| `utils` | 0% | N/A | **MÓDULO VACÍO** |

**Cobertura total de tests:** <20% (inaceptable - objetivo 80% para v1.0)

---

## Convenciones del Proyecto

### 1. Idioma

**CRÍTICO:** Todo el código debe estar en español:
- Docstrings en español
- Comentarios en español
- Mensajes de error en español
- Nombres de variables en inglés (convención Python)

```python
# [COMPLETADO] CORRECTO
def calibrar_espectro(espectro: XPSSpectrum, elemento_referencia: str) -> XPSSpectrum:
    """
    Calibra un espectro XPS usando un elemento de referencia.
    
    Parámetros
    ----------
    espectro : XPSSpectrum
        El espectro a calibrar.
    elemento_referencia : str
        Símbolo del elemento de referencia (ej: "C").
    
    Retorna
    -------
    XPSSpectrum
        Espectro calibrado.
    """
    pass

# [PENDIENTE] INCORRECTO - docstring en inglés
def calibrar_espectro(espectro: XPSSpectrum) -> XPSSpectrum:
    """Calibrates an XPS spectrum."""
    pass
```

### 2. Patrón de Calibración

La calibración de energía (`preprocessing/calibration.py`) sigue este flujo:

1. Seleccionar espectro de referencia matcheando símbolo de elemento en claves (ej: "C 1s" -> "C")
2. Calcular desplazamiento: `ref_element.binding_energy_most_useful - observed_peak_max`
3. Aplicar desplazamiento a todos los espectros (vectorizado: `binding_energy += shift`)

**Elemento de referencia por defecto:** C 1s @ 284.8 eV (carbono adventicio)

### 3. Convenciones de Visualización

Funciones de plotting (`visualization/plotting.py`) **siempre**:

- Invertir eje x (`plt.gca().invert_xaxis()`) - convención XPS muestra alta energía a la izquierda
- Plotear directamente desde `spectrum.data` DataFrame (indexado por binding_energy)
- Usar funciones separadas para survey vs. espectros de región (diferentes tamaños/colores de figura)

```python
# Patrón estándar de plotting
def plot_spectrum(spectrum: XPSSpectrum):
    plt.plot(spectrum.binding_energy, spectrum.intensity)
    plt.xlabel("Binding Energy (eV)")
    plt.ylabel("Intensity (a.u.)")
    plt.gca().invert_xaxis()  # <- CRÍTICO: alta energía a la izquierda
    plt.show()
```

### 4. Estructura de Imports

Orden de imports configurado en `pyproject.toml` (ruff):

```python
# 1. future
from __future__ import annotations

# 2. standard-library
from pathlib import Path
from typing import Any

# 3. first-party (xps_analyzer)
from xps_analyzer.data_loader import XPSSpectrum

# 4. local-folder (imports relativos)
from .core import parse_metadata

# 5. third-party
import numpy as np
import pandas as pd
```

### 5. Validación de Datos

**Estado actual (v0.1.0):** Validación manual con `__post_init__` en dataclasses.

**Ejemplo:**
```python
def __post_init__(self):
    """Validación básica después de inicialización."""
    if len(self.binding_energy) != len(self.intensity):
        raise ValueError(
            f"binding_energy ({len(self.binding_energy)} puntos) e intensity "
            f"({len(self.intensity)} puntos) deben tener la misma longitud"
        )
    if len(self.binding_energy) == 0:
        raise ValueError("Los arrays no pueden estar vacíos")
```

**Futuro (v0.3.0 - Fase 2):** Migración a Pydantic `BaseModel` para:
- Validación automática de tipos
- Mensajes de error mejorados
- JSON schema generation
- Integración con múltiples formatos de archivo

---

## Flujo de Datos

### Pipeline Típico de Análisis

```
1. Carga de Datos
   CLI -> load_single_file(filepath) 
       -> parse propietario 
       -> XPSDataset

2. Carga de Referencias
   load_reference_database() 
       -> cache singleton 
       -> ReferenceDatabase

3. Calibración
   calibrate_sample(dataset, ref_element="C") 
       -> modifica todos los espectros
       -> inplace=True/False

4. Análisis (PENDIENTE - Fase 1)
   subtract_background(spectrum, method="shirley")
   fit_peaks(spectrum, peak_shapes=["voigt"])
   quantify(dataset, use_sensitivity_factors=True)

5. Visualización
   plot_spectrum(spectrum) 
       -> matplotlib figure

6. Exportación (PENDIENTE - Fase 1)
   export_results(dataset, format="csv")
       -> guarda en data/results/
```

### Manejo de Archivos

**Convención de paths:** Siempre usar `pathlib.Path`, nunca concatenación de strings.

```python
# [COMPLETADO] CORRECTO
from pathlib import Path
data_dir = Path("data/raw/samples")
filepath = data_dir / "muestra1.txt"

# [PENDIENTE] INCORRECTO
data_dir = "data/raw/samples"
filepath = data_dir + "/" + "muestra1.txt"
```

**Estructura de datos:**
```
data/
├── raw/                    # Datos originales (nunca modificar)
│   └── samples/
├── processed/              # Datos procesados (PENDIENTE)
├── test_data/              # Datos para tests (PENDIENTE)
└── results/                # Resultados de análisis
    ├── reports/
    ├── plots/
    └── exports/
```

---

## Configuración del Entorno

### Opción 1: uv (Recomendado)

**Más rápido que pip/conda** - instalador moderno de Python

```bash
# Instalación completa (dev + jupyter)
uv sync --group dev --group jupyter

# Ejecutar CLI sin activar venv
uv run xps-analyzer --help

# Ejecutar tests
uv run pytest tests/

# Formato de código
uv run ruff format .
uv run ruff check --fix .
```

### Opción 2: Conda

**Para usuarios con stack científico existente**

```bash
# Crear ambiente
conda env create -f environment.yml  # Crea 'xps-analysis'

# Activar
conda activate xps-analysis

# Instalar en modo desarrollo
pip install -e ".[dev]"

# Verificar instalación
python verify_installation.py
```

### Dependencias

**Usadas actualmente:**
- `numpy` - Arrays numéricos
- `pandas` - DataFrames
- `matplotlib` - Visualización
- `scipy` - Procesamiento de señales
- `click` - Framework CLI

**Declaradas pero no usadas (planeadas para fases futuras):**
- `lmfit` - Ajuste de picos (Fase 1)
- `scikit-learn` - Machine learning para identificación (Fase 3)
- `h5py` - Exportación HDF5 (Fase 2)
- `PyYAML` - Configuración (Fase 1)
- `pydantic` - Validación de datos (Fase 2)
- `tqdm` - Barras de progreso (Fase 1)

---

## Configuración de Calidad de Código

### Ruff (Linter + Formatter)

Configurado en `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP", "N"]
ignore = ["E501", "B008"]
```

**Ejecutar:**
```bash
ruff check .           # Linting
ruff format .          # Formatting
ruff check --fix .     # Auto-fix
```

### Type Checking

**ty (experimental, Python 3.12+)** - Configurado pero no estrictamente aplicado

```bash
ty check src/
```

**Estado de type hints:** Parcialmente implementado (~40% del código)

### Pre-commit Hooks

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

---

## Testing

### Estado Actual

**Cobertura:** <20% (CRÍTICO - inaceptable)

**Tests existentes:**
- `tests/test_data_loader.py` - 4 tests para parsing y validación

**Ejecutar tests:**
```bash
# Con cobertura
pytest --cov=src --cov-report=html

# Solo test específico
pytest tests/test_data_loader.py::test_get_spectrum_data_basic -v
```

### Roadmap de Tests

**Fase 0 (actual):** 20% coverage - tests básicos de data_loader  
**Fase 1:** 60% coverage - tests de análisis core  
**Fase 2:** 80% coverage - tests de integración + formatos múltiples  
**Fase 3:** 90% coverage - property-based testing con hypothesis

---

## Problemas Conocidos (Issues)

### Bugs Críticos

1. **Issue #42** - `calibration.py:56-58`: IndexError cuando elemento de referencia no encontrado
   ```python
   # Bug actual
   ref_spectrum = dataset.spectra[ref_element]  # KeyError si no existe
   
   # Fix necesario
   ref_spectrum = dataset.get_spectrum(ref_element)
   if ref_spectrum is None:
       raise ValueError(f"Elemento de referencia '{ref_element}' no encontrado")
   ```

2. **`elements.py:170-171`**: Acceso incorrecto a photoelectron_lines
   ```python
   # Bug: .values no existe en List[PhotoelectronLine]
   lines = element.photoelectron_lines.values()
   ```

3. **`identification.py:117`**: Intento de acceso a `.peak_position` en tipo string

### Funcionalidad Faltante (Bloqueadores para v0.5.0)

- [PENDIENTE] Sustracción de fondo (Shirley, Tougaard)
- [PENDIENTE] Ajuste de picos (gaussian, lorentzian, voigt)
- [PENDIENTE] Cuantificación (factores de sensibilidad)
- [PENDIENTE] Exportación de resultados (CSV, Excel)
- [PENDIENTE] Soporte para múltiples formatos (VAMAS, CASA)

### Implementaciones Stub

Estas funciones retornan `None` o `pass`:
- `load_all_data()` - Carga recursiva de directorio
- `detect_file_format()` - Auto-detección de formato
- `find_peaks_basic()` - Detección de picos

---

## Quirks y Trampas Comunes

### 1. Mutabilidad de Arrays NumPy

**Problema:** Arrays en `XPSSpectrum` son mutables por defecto

```python
# [PENDIENTE] PELIGRO: Modifica el original
spectrum1 = dataset.get_spectrum("C 1s")
spectrum2 = spectrum1  # ¡Mismo objeto!
spectrum2.intensity *= 2  # Modifica spectrum1 también

# [COMPLETADO] CORRECTO: Usar .copy()
spectrum1 = dataset.get_spectrum("C 1s")
spectrum2 = spectrum1.copy()
spectrum2.intensity *= 2  # Solo modifica spectrum2
```

### 2. Parsing de Metadata

`parse_metadata()` maneja DOS formatos distintos:

- **Header mode** (`header=True`): 3 líneas con config de elementos
- **Spectrum mode** (string que empieza con "Element"): Pares clave-valor delimitados por `;`

```python
# Header (3 líneas)
lines = [
    "Sample Name Sample1; Date 2023-10-01;",
    "C 1s O 1s N 1s;",
    "284.8 531.0 399.0;"
]
meta = parse_metadata(lines, header=True)

# Spectrum (1 string)
line = "Element C 1s; Region 1; Sweeps 5;"
meta = parse_metadata(line, header=False)
```

### 3. Estructura de Datos de Referencia JSON

El JSON tiene `line_positions` anidados con múltiples entradas por orbital (maneja diferentes fuentes de rayos X):

```json
{
  "symbol": "C",
  "photoelectron_lines": {
    "1s": {
      "peak_position": 284.8,
      "line_width": 1.0
    }
  }
}
```

### 4. CLI Entry Point

**Comando instalado:** `xps-analyzer` mapea a `src/xps_analyzer/cli/main.py:main()`

**Comandos disponibles:**
- `xps-analyzer analyze <data_dir>` - Analizar directorio
- `xps-analyzer show-element <symbol>` - Mostrar info de elemento

---

## Archivos Clave

### Configuración

- **`pyproject.toml`** - Dependencias, CLI entry points, configuración de herramientas
- **`environment.yml`** - Especificación de ambiente Conda
- **`config/default_settings.toml`** - Parámetros de análisis por defecto (v0.1.0: documentado, no implementado)
- **`config/instrument_profiles.toml`** - Perfiles de instrumentos XPS
- **`config/element_database.toml`** - Base de datos extendida de elementos

### Código Core

- **`src/xps_analyzer/data_loader/core.py`** - Estructuras de datos core + parsing
- **`src/xps_analyzer/reference_data/elements.py`** - Clases de referencia + carga JSON
- **`src/xps_analyzer/preprocessing/calibration.py`** - Calibración de energía
- **`src/xps_analyzer/cli/main.py`** - CLI con Click

### Documentación

- **`README.md`** - Quick start, instalación, ejemplos
- **`ARCHITECTURE.md`** - Arquitectura técnica detallada
- **`DEVELOPMENT.md`** - Guía para desarrolladores
- **`CONTRIBUTING.md`** - Cómo contribuir
- **`API_DOCS.md`** - Referencia completa de API
- **`TESTING.md`** - Estrategia de testing
- **`ROADMAP.md`** - Plan de desarrollo por fases

---

## Roadmap de Desarrollo

### Fase 0 (Actual) - Fundamentos
**Estado:** 35% completo  
**Prioridad:** Documentación + validación básica

- [x] Carga de datos básica
- [x] Visualización simple
- [x] Calibración básica
- [x] CLI inicial
- [x] Validación manual en dataclasses
- [x] Configuración TOML documentada
- [ ] Tests básicos (target: 20% coverage)

### Fase 1 - Análisis Core
**Estado:** 0% completo  
**Prioridad:** Funcionalidad bloqueadora

- [ ] Sustracción de fondo (Shirley + Tougaard)
- [ ] Ajuste de picos (gaussian, lorentzian, voigt)
- [ ] Cuantificación con factores de sensibilidad
- [ ] Exportación (CSV, Excel, JSON)
- [ ] Sistema de configuración (leer TOML)
- [ ] Tests (target: 60% coverage)

### Fase 2 - Robustez
**Estado:** 0% completo  
**Prioridad:** Escalabilidad + formatos estándar

- [ ] Migración a Pydantic (validación automática)
- [ ] Soporte VAMAS (ISO 14976)
- [ ] Soporte CASA XPS
- [ ] Exportación HDF5
- [ ] Sistema de plugins para formatos
- [ ] Tests de integración (target: 80% coverage)

### Fase 3 - Avanzado
**Estado:** 0% completo  
**Prioridad:** Innovación

- [ ] Machine learning para identificación automática
- [ ] Análisis de profundidad (depth profiling)
- [ ] GUI con Streamlit/Dash
- [ ] API REST con FastAPI
- [ ] Property-based testing (target: 90% coverage)

---

## Notas para Agentes de IA

### Cuando Generes Código

1. **SIEMPRE en español:** docstrings, comentarios, mensajes de error
2. **Validar inputs:** Usar `__post_init__` en dataclasses o Pydantic validators
3. **Type hints completos:** Incluir tipos de retorno y parámetros
4. **Copiar datos cuando modifiques:** Usar `.copy()` o `inplace=False`
5. **Tests primero:** Escribir test antes de implementar (cuando aplique)

### Cuando Modifiques Código Existente

1. **Leer tests existentes** antes de cambiar interfaces públicas
2. **Actualizar docstrings** si cambias comportamiento
3. **Ejecutar ruff** después de cambios: `ruff format . && ruff check .`
4. **Verificar tests** pasan: `pytest tests/`
5. **Actualizar CHANGELOG.md** si es feature/bugfix significativo

### Prioridades de Implementación

**Alta prioridad (bloqueadores de v0.5.0):**
- Sustracción de fondo
- Ajuste de picos
- Cuantificación
- Exportación de resultados

**Media prioridad:**
- Tests (aumentar cobertura)
- Soporte para más formatos
- Sistema de configuración

**Baja prioridad:**
- GUI
- Machine learning
- API REST

### Limitaciones Conocidas

- Solo un formato de archivo soportado (texto propietario)
- Sin manejo de errores robusto
- Tests insuficientes (<20% coverage)
- Tipo checking parcial
- Sin documentación de API completa

---

## Referencias Externas

### Estándares XPS

- **ISO 14976** - Formato VAMAS para datos de espectroscopía de superficie
- **NIST XPS Database** - https://srdata.nist.gov/xps/
- **CASA XPS** - Software comercial líder en análisis XPS

### Herramientas de Desarrollo

- **uv** - https://github.com/astral-sh/uv
- **Ruff** - https://docs.astral.sh/ruff/
- **Click** - https://click.palletsprojects.com/
- **Pydantic** - https://docs.pydantic.dev/

### Publicaciones Científicas

- Shirley, D. A. "Background subtraction in X-ray photoelectron spectroscopy" (1972)
- Tougaard, S. "Practical guide to the use of backgrounds in quantitative XPS" (2020)

---

## Historial de Cambios del Documento

- **2026-02:** Creación inicial fusionando `.github/copilot-instructions.md`
- **2026-02:** Agregado roadmap de Pydantic (Fase 2)
- **2026-02:** Agregada sección de configuración TOML

---

**Última revisión:** Febrero 2026  
**Próxima revisión:** Después de completar Fase 1  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
