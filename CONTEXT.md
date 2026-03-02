# XPS Analyzer - Contexto Completo del Proyecto

**Versión:** 0.7.0-beta  
**Estado:** Fase 1 (75% completado)  
**Última actualización:** Marzo 2026

Este documento proporciona contexto completo para agentes de IA, desarrolladores y colaboradores sobre el proyecto XPS Analyzer.

---

## Resumen Ejecutivo

**XPS Analyzer** es un paquete Python científico para análisis automatizado de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS), desarrollado como proyecto de servicio social en investigación de química y metalurgia. El software carga formatos propietarios de datos XPS, realiza calibración de energía, identifica elementos/compuestos, sustrae fondos, ajusta picos, cuantifica composición atómica y genera reportes analíticos.

**Estado actual:** Fase 1 (75% completado). Funcionalidad core de análisis implementada: sustracción de fondo (Shirley, Tougaard, Linear), ajuste de picos (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL), y cuantificación atómica (RSF Scofield, Wagner). Falta sistema de exportación (Sesión 4).

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
├── preprocessing/           # [COMPLETADO] 100% completo
│   ├── calibration.py      # Calibración básica implementada
│   └── __init__.py         
├── analysis/                # [COMPLETADO] 75% completo - FUNCIONALIDAD CORE
│   ├── __init__.py         # Exports principales
│   ├── background.py       # Sustracción de fondo (Shirley, Tougaard, Linear)
│   ├── peak_fitting.py     # Ajuste de picos (Gaussian, Lorentzian, Voigt, etc.)
│   └── quantification.py   # Cuantificación atómica (RSF Scofield, Wagner)
├── reference_data/          # [COMPLETADO] 85% completo
│   ├── elements.py         # Clases de referencia + carga JSON
│   ├── identification.py   # Identificación de elementos por energía
│   ├── data/               # Base de datos JSON de elementos
│   └── __init__.py
├── visualization/           # [EN PROGRESO] 20% completo
│   ├── plotting.py         # Plots básicos (survey, region)
│   └── __init__.py         # Falta: plots avanzados, reports interactivos
├── export/                  # [PENDIENTE] 0% - MÓDULO VACÍO (SESIÓN 4)
│   └── __init__.py         # Falta: exportar CSV, Excel, JSON, HDF5
├── cli/                     # [EN PROGRESO] 40% completo
│   ├── main.py             # Comandos básicos: analyze, show-element
│   └── __init__.py         # Falta: más comandos, validación robusta
└── utils/                   # [PENDIENTE] 0% - MÓDULO VACÍO
    └── __init__.py         # Falta: helpers, validators, decorators
```

### Estado de Implementación por Módulo

| Módulo | Estado | Tests | Cobertura | Líneas de Código |
|--------|--------|-------|-----------|------------------|
| `data_loader` | 70% | 4 tests | ~60% | ~400 |
| `preprocessing` | 100% | Incluidos en analysis | ~90% | ~200 |
| `analysis/background` | 100% | 30 tests | 96% | 498 |
| `analysis/peak_fitting` | 100% | 45 tests | 95% | 849 |
| `analysis/quantification` | 100% | 43 tests | 85% | 498 |
| `reference_data` | 85% | Integrados | ~70% | ~600 |
| `visualization` | 20% | 0 tests | 0% | ~150 |
| `export` | 0% | N/A | N/A | **MÓDULO VACÍO** |
| `cli` | 40% | 0 tests | 0% | ~200 |
| `utils` | 0% | N/A | N/A | **MÓDULO VACÍO** |

**Cobertura total de tests:** 87% (superando objetivo de 80% para v1.0)  
**Total tests:** 208 (100% passing)  
**Líneas de código totales:** ~3,800

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

4. Análisis (COMPLETADO - Fase 1)
   shirley_background(spectrum, max_iterations=50, tolerance=1e-6)
   tougaard_background(spectrum, tougaard_type="universal")
   linear_background(spectrum)
   fit_gaussian(spectrum, initial_params)
   fit_lorentzian(spectrum, initial_params)
   fit_voigt(spectrum, initial_params)
   fit_multiple_peaks(spectrum, initial_params, peak_type)
   load_sensitivity_factors(source="scofield")
   calculate_atomic_concentration(peak_areas, sensitivity_factors)
   normalize_to_100(concentrations)

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
- `lmfit` - Ajuste de picos no lineal (usado en Fase 1)

**Declaradas pero no usadas (planeadas para fases futuras):**
- `scikit-learn` - Machine learning para identificación (Fase 3)
- `h5py` - Exportación HDF5 (Fase 2)
- `PyYAML` - Configuración (Fase 1 - Sesión 4)
- `pydantic` - Validación de datos (Fase 2)
- `tqdm` - Barras de progreso (Fase 1 - Sesión 4)

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

**Cobertura:** 87% (superando objetivo de 80%)

**Tests existentes:**
- `tests/test_data_loader.py` - 4 tests para parsing y validación
- `tests/test_background.py` - 30 tests para sustracción de fondo
- `tests/test_peak_fitting.py` - 45 tests para ajuste de picos
- `tests/test_quantification.py` - 43 tests para cuantificación
- **Total: 208 tests (100% passing)**

**Ejecutar tests:**
```bash
# Con cobertura
pytest --cov=src --cov-report=html

# Solo test específico
pytest tests/test_data_loader.py::test_get_spectrum_data_basic -v
```

### Roadmap de Tests

**Fase 0 (completada):** 87% coverage - tests básicos de data_loader + análisis core completo  
**Fase 1 (75% completado):** 87% coverage alcanzado (objetivo 60% superado)  
**Fase 2:** 85% coverage - tests de integración + formatos múltiples  
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

### Funcionalidad Completada (Fase 1 - Sesiones 1-3)

- [x] Sustracción de fondo (Shirley, Tougaard 4 variantes, Linear) - 96% cobertura
- [x] Ajuste de picos (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL) - 95% cobertura
- [x] Cuantificación (RSF Scofield 89 elementos, Wagner 18 elementos) - 85% cobertura
- [x] 208 tests totales (100% passing)
- [x] 87% cobertura total

### Funcionalidad Faltante (Bloqueadores para v1.0)

- [PENDIENTE] Exportación de resultados (CSV, Excel, JSON) - Sesión 4
- [PENDIENTE] Soporte para múltiples formatos (VAMAS, CASA) - Fase 2

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

### Fase 0 (Completada) - Fundamentos
**Estado:** 100% completo  
**Prioridad:** Documentación + validación básica

- [x] Carga de datos básica
- [x] Visualización simple
- [x] Calibración básica
- [x] CLI inicial
- [x] Validación manual en dataclasses
- [x] Configuración TOML documentada
- [x] Tests básicos (87% coverage alcanzado)

### Fase 1 - Análisis Core
**Estado:** 75% completo (3 de 4 sesiones)  
**Prioridad:** Funcionalidad bloqueadora

- [x] Sustracción de fondo (Shirley, Tougaard, Linear) - Sesión 1
- [x] Ajuste de picos (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL) - Sesión 2
- [x] Cuantificación con factores RSF (Scofield, Wagner) - Sesión 3
- [ ] Exportación (CSV, Excel, JSON) - Sesión 4 PENDIENTE
- [x] Tests (87% coverage alcanzado - superando objetivo de 60%)

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

**Alta prioridad (bloqueadores de v1.0):**
- Exportación de resultados (CSV, Excel, JSON) - Sesión 4 Fase 1

**Media prioridad:**
- Tests adicionales (aumentar a 90%)
- Soporte para más formatos (VAMAS, CASA XPS)
- Sistema de configuración avanzado

**Baja prioridad:**
- GUI
- Machine learning
- API REST

### Limitaciones Conocidas

- Solo un formato de archivo soportado (texto propietario) - Fase 2 agregará VAMAS, CASA
- Sin sistema de exportación (Sesión 4 pendiente)
- Tests de módulos CLI y visualization pendientes
- Tipo checking parcial (~60% del código)
- Sistema de configuración documentado pero no implementado

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

- Shirley, D. A. (1972). "High-Resolution X-Ray Photoemission Spectrum of Valence Bands of Gold" Phys Rev B, 5(12), 4709-4714
- Tougaard, S. (1997). "Universality Classes of Inelastic Electron Scattering Cross-sections" Surf Interface Anal, 25(3), 137-154
- Thompson et al. (1987). "Voigt function for XPS line-shape analysis" J. Appl. Cryst. 20, 79-83
- Scofield, J.H. (1976). "Theoretical photoionization cross sections" LLNL Report UCRL-51326
- Wagner, C.D. et al. (1981). "Empirical atomic sensitivity factors" Surf. Interface Anal. 3(5), 211-225

---

## Historial de Cambios del Documento

- **2026-02:** Creación inicial fusionando `.github/copilot-instructions.md`
- **2026-02:** Agregado roadmap de Pydantic (Fase 2)
- **2026-02:** Agregada sección de configuración TOML
- **2026-03:** Actualización completa para Fase 1 (sesiones 1-3 completadas)
  * Módulo analysis/ implementado (background, peak_fitting, quantification)
  * 208 tests, 87% cobertura
  * ~2,500 líneas de código agregadas

---

**Última revisión:** Marzo 2026  
**Próxima revisión:** Después de completar Sesión 4 (Export System)  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
