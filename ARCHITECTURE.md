# XPS Analyzer - Arquitectura Técnica

**Versión:** 0.7.0-beta  
**Estado:** Fase 1 (75% completado)  
**Última actualización:** Marzo 2026

Este documento describe la arquitectura técnica completa del proyecto XPS Analyzer, incluyendo decisiones de diseño, patrones de implementación, y guías para el desarrollo futuro.

---

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Modelo de Datos](#modelo-de-datos)
3. [Arquitectura de Módulos](#arquitectura-de-módulos)
4. [Sistema de Validación](#sistema-de-validación)
5. [Sistema de Configuración](#sistema-de-configuración)
6. [Gestión de Datos de Referencia](#gestión-de-datos-de-referencia)
7. [Pipeline de Procesamiento](#pipeline-de-procesamiento)
8. [Decisiones de Diseño](#decisiones-de-diseño)
9. [Patrones y Convenciones](#patrones-y-convenciones)
10. [Extensibilidad](#extensibilidad)

---

## Visión General

### Principios de Diseño

XPS Analyzer sigue estos principios fundamentales:

1. **Inmutabilidad por defecto** - Los datos originales nunca se modifican; las operaciones retornan copias
2. **Separación de responsabilidades** - Cada módulo tiene una función clara y bien definida
3. **Validación temprana** - Los errores se detectan al cargar datos, no durante el análisis
4. **Configuración explícita** - Todos los parámetros tienen valores por defecto documentados
5. **Extensibilidad** - Sistema de plugins para formatos de archivo y métodos de análisis

### Stack Tecnológico

**Dependencias Core:**
- `numpy` (>=1.24.0) - Arrays numéricos, operaciones vectorizadas
- `scipy` (>=1.11.0) - Procesamiento de señales, interpolación
- `pandas` (>=2.0.0) - Estructuras de datos tabulares (futuro: deprecar en favor de NumPy puro)
- `matplotlib` (>=3.7.0) - Visualización
- `lmfit` (>=1.2.0) - Ajuste de picos no lineal (Fase 1 - IMPLEMENTADO)

**Dependencias Planeadas:**
- `pydantic` (>=2.0.0) - Validación de datos (Fase 2)
- `h5py` (>=3.9.0) - Exportación HDF5 (Fase 2)
- `scikit-learn` (>=1.3.0) - Machine learning (Fase 3)

**Herramientas de Desarrollo:**
- `ruff` - Linting + formatting
- `pytest` - Testing framework
- `pytest-cov` - Cobertura de tests
- `uv` - Gestión de paquetes

---

## Modelo de Datos

### Jerarquía de Clases

El sistema usa una jerarquía de tres niveles para representar datos XPS:

```
XPSSample (muestra física)
    └── XPSDataset[] (archivos de medición)
            └── XPSSpectrum[] (regiones espectrales)
```

#### 1. XPSSpectrum - Nivel Atómico

**Ubicación:** `src/xps_analyzer/data_loader/core.py:12-36`

```python
@dataclass
class XPSSpectrum:
    """
    Representa un espectro XPS individual (survey o región de alta resolución).
    
    Responsabilidades:
    - Almacenar arrays de energía e intensidad
    - Validar consistencia de datos al inicializar
    - Proveer acceso inmutable a datos raw
    
    Atributos
    ---------
    region_name : str
        Identificador de región (ej: "C 1s", "O 1s", "Survey")
    binding_energy : np.ndarray
        Array 1D de energías de enlace en eV (típicamente 100-10000 puntos)
    intensity : np.ndarray
        Array 1D de intensidades en cuentas arbitrarias
    metadata : dict[str, Any]
        Información adicional (sweeps, dwell_time, pass_energy, etc.)
    """
    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validación manual - se ejecuta después de __init__"""
        # Ver sección "Sistema de Validación" para detalles
```

**Invariantes garantizados:**
- `len(binding_energy) == len(intensity)` siempre
- Ambos arrays tienen longitud > 0
- `binding_energy` contiene solo valores positivos
- `region_name` no está vacío

**Patrón de copia:**
```python
# Implementación futura (Fase 1)
def copy(self) -> XPSSpectrum:
    """Crea copia profunda del espectro."""
    return XPSSpectrum(
        region_name=self.region_name,
        binding_energy=self.binding_energy.copy(),
        intensity=self.intensity.copy(),
        metadata=self.metadata.copy()
    )
```

#### 2. XPSDataset - Nivel de Archivo

**Ubicación:** `src/xps_analyzer/data_loader/core.py:39-55`

```python
@dataclass
class XPSDataset:
    """
    Representa un archivo XPS completo con múltiples espectros.
    
    Responsabilidades:
    - Agrupar espectros relacionados (survey + regiones)
    - Almacenar metadata a nivel de archivo
    - Proveer acceso por nombre de región
    
    Atributos
    ---------
    filename : str
        Path al archivo original
    header : dict[str, Any]
        Metadata global (sample_name, date, operator, instrument, etc.)
    spectra : dict[str, XPSSpectrum]
        Mapeo de region_name -> XPSSpectrum
    """
    filename: str
    header: dict[str, Any] = field(default_factory=dict)
    spectra: dict[str, XPSSpectrum] = field(default_factory=dict)
```

**Operaciones comunes:**
```python
# Acceso por nombre de región
dataset.spectra["C 1s"]  # Retorna XPSSpectrum

# Iterar sobre regiones
for name, spectrum in dataset.spectra.items():
    print(f"{name}: {len(spectrum.binding_energy)} puntos")

# Filtrar por patrón
high_res = {k: v for k, v in dataset.spectra.items() if k != "Survey"}
```

#### 3. XPSSample - Nivel de Muestra

**Ubicación:** `src/xps_analyzer/data_loader/core.py:58-80`

```python
@dataclass
class XPSSample:
    """
    Representa una muestra física con múltiples mediciones.
    
    Responsabilidades:
    - Agrupar datasets de la misma muestra
    - Facilitar análisis comparativos (depth profiling, time series)
    
    Atributos
    ---------
    sample_name : str
        Identificador único de muestra
    datasets : dict[str, XPSDataset]
        Mapeo de filename -> XPSDataset
    """
    sample_name: str
    datasets: dict[str, XPSDataset] = field(default_factory=dict)
```

**Caso de uso típico:**
```python
# Muestra con 3 mediciones a diferentes ángulos
sample = XPSSample(
    sample_name="TiO2_film",
    datasets={
        "angle_0deg.txt": dataset_0,
        "angle_30deg.txt": dataset_30,
        "angle_60deg.txt": dataset_60
    }
)
```

### Diagrama de Flujo de Datos

```
┌─────────────────┐
│  Archivo XPS    │
│  (texto/VAMAS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ load_single_file│
│   (core.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ parse_metadata  │◄─────│ Detecta formato  │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐
│get_spectrum_data│────── Validación
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  XPSDataset     │────── Almacenamiento
│  (en memoria)   │        inmutable
└─────────────────┘
```

---

## Arquitectura de Módulos

### Dependencias entre Módulos

```
                    ┌──────────────┐
                    │     cli/     │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐  ┌────────────┐  ┌──────────────┐
│ visualization/ │  │ analysis/  │  │    export/   │
└────────┬───────┘  └─────┬──────┘  └──────┬───────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ preprocessing/  │
                 └────────┬─────────┘
                          │
         ┌────────────────┼────────────────┐
         │                                 │
         ▼                                 ▼
┌────────────────┐              ┌──────────────────┐
│ data_loader/   │              │ reference_data/  │
└────────────────┘              └──────────────────┘
```

**Reglas de dependencia:**
1. Los módulos de nivel superior pueden importar de nivel inferior
2. Los módulos del mismo nivel NO deben importarse entre sí
3. Nunca crear dependencias circulares

### data_loader - Carga de Datos

**Estado:** 70% completo  
**Ubicación:** `src/xps_analyzer/data_loader/`

**Responsabilidades:**
- Detectar formato de archivo (propietario, VAMAS, CASA)
- Parsear headers y metadata
- Extraer arrays de datos
- Crear objetos `XPSDataset` validados

**API pública:**
```python
# Cargar archivo individual
from xps_analyzer import load_single_file
dataset = load_single_file("data/raw/samples/muestra1.txt")

# Cargar directorio completo (PENDIENTE - Fase 1)
from xps_analyzer import load_all_data
sample = load_all_data("data/raw/samples/", pattern="muestra1*.txt")
```

**Estructura interna:**
```
data_loader/
├── __init__.py          # Re-exporta API pública
├── core.py              # Clases principales + parser propietario
├── vamas.py             # Parser VAMAS (Fase 2)
├── casa.py              # Parser CASA XPS (Fase 2)
└── plugins/             # Sistema de plugins (Fase 3)
    └── __init__.py
```

**Formato actual soportado:**

Texto propietario con estructura:
```
# Header (3 líneas)
Sample Name muestra1; Date 2023-10-01; Operator JFL;
C 1s O 1s N 1s;
284.8 531.0 399.0;

# Regiones (múltiples secciones)
Element C 1s; Region 1; Sweeps 5; Dwell Time 0.1;
290.0 1234.5
289.9 1245.2
...
```

### preprocessing - Preprocesamiento

**Estado:** 25% completo  
**Ubicación:** `src/xps_analyzer/preprocessing/`

**Responsabilidades:**
- Calibración de energía
- Sustracción de fondo (Shirley, Tougaard)
- Suavizado (Savitzky-Golay, moving average)
- Normalización

**Implementado (Fase 0):**
```python
from xps_analyzer.preprocessing import calibrate_spectrum, calibrate_dataset

# Calibrar espectro individual
calibrated = calibrate_spectrum(
    spectrum=dataset.spectra["C 1s"],
    reference_element="C",
    inplace=False  # Retorna copia
)

# Calibrar dataset completo
calibrate_dataset(
    dataset=dataset,
    reference_element="C",
    inplace=True  # Modifica en lugar
)
```

**Implementado (Fase 1):**
```python
# Sustracción de fondo
from xps_analyzer.analysis import shirley_background, tougaard_background, linear_background

clean_spectrum = shirley_background(
    spectrum=spectrum,
    max_iterations=50,
    tolerance=1e-6
)

tougaard_clean = tougaard_background(
    spectrum=spectrum,
    tougaard_type="universal"  # o "B", "C", "D", "D_star"
)

linear_clean = linear_background(spectrum=spectrum)
```
```

### analysis - Análisis Espectral

**Estado:** 75% completo (3 de 4 módulos implementados)  
**Ubicación:** `src/xps_analyzer/analysis/`

**Responsabilidades implementadas:**
- Sustracción de fondo (Shirley, Tougaard, Linear)
- Ajuste de picos (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL)
- Cuantificación elemental (RSF Scofield, Wagner)

**Responsabilidades futuras:**
- Exportación de resultados (Sesión 4 - pendiente)

**API implementada (Fase 1):**
```python
from xps_analyzer.analysis import (
    shirley_background, tougaard_background, linear_background,
    fit_gaussian, fit_lorentzian, fit_voigt, fit_multiple_peaks,
    load_sensitivity_factors, calculate_atomic_concentration, normalize_to_100,
    PeakParameters, FitResult
)

# Sustracción de fondo
clean = shirley_background(spectrum, max_iterations=50, tolerance=1e-6)

# Ajuste de picos
result = fit_voigt(
    spectrum=spectrum,
    initial_params=PeakParameters(position=284.8, amplitude=1000, fwhm=1.2)
)

# Ajuste múltiple
result = fit_multiple_peaks(
    spectrum=spectrum,
    initial_params=[
        PeakParameters(position=284.8, fwhm=1.2),
        PeakParameters(position=286.5, fwhm=1.5)
    ],
    peak_type="voigt"
)

# Cuantificación
rsf = load_sensitivity_factors(source="scofield")  # 89 elementos
concentrations = calculate_atomic_concentration(
    peak_areas={"C 1s": 10000, "O 1s": 5000},
    sensitivity_factors=rsf
)
normalized = normalize_to_100(concentrations)  # {"C": 66.7, "O": 33.3}
```

**Estructura implementada:**
```
analysis/
├── __init__.py           # Exports principales
├── background.py         # Shirley, Tougaard, Linear (498 líneas, 96% cov)
├── peak_fitting.py       # Gaussian, Lorentzian, Voigt, etc. (849 líneas, 95% cov)
└── quantification.py     # RSF Scofield/Wagner (498 líneas, 85% cov)
```

**Tests implementados:**
- 30 tests para background subtraction
- 45 tests para peak fitting
- 43 tests para quantification
- **Total: 118 tests (100% passing), 87% cobertura**

### reference_data - Datos de Referencia

**Estado:** 85% completo  
**Ubicación:** `src/xps_analyzer/reference_data/`

**Responsabilidades:**
- Cargar base de datos de elementos
- Búsqueda de líneas fotoelectrónicas
- Identificación de elementos por energía

**Arquitectura:**

```python
# Patrón Singleton con cache global
_reference_database_cache = None

def load_reference_database() -> ReferenceDatabase:
    """Retorna instancia en cache (carga solo una vez)."""
    global _reference_database_cache
    if _reference_database_cache is None:
        _reference_database_cache = ReferenceDatabase(
            elements=_load_elements_from_json()
        )
    return _reference_database_cache
```

**Clases principales:**

```python
@dataclass
class PhotoelectronLine:
    """Línea espectral individual (ej: C 1s, O 1s)."""
    orbital: str                    # "1s", "2p3/2", etc.
    peak_position: float            # eV
    line_width: float               # FWHM en eV
    relative_intensity: float       # 0-1

@dataclass
class ElementReference:
    """Información completa de un elemento."""
    symbol: str                     # "C", "O", etc.
    name: str                       # "Carbon", "Oxygen"
    atomic_number: int
    photoelectron_lines: dict[str, PhotoelectronLine]
    common_compounds: list[dict]    # Estados de oxidación

@dataclass
class ReferenceDatabase:
    """Base de datos completa."""
    elements: dict[str, ElementReference]  # key = symbol
    
    def get_element(self, symbol: str) -> ElementReference | None:
        """Búsqueda case-insensitive."""
        return self.elements.get(symbol.upper())
    
    def find_element_by_energy(
        self, 
        energy: float, 
        tolerance: float = 2.0
    ) -> list[tuple[str, str]]:
        """Retorna [(symbol, orbital), ...] dentro de tolerancia."""
```

**Formato JSON:**

```json
{
  "C": {
    "symbol": "C",
    "name": "Carbon",
    "atomic_number": 6,
    "photoelectron_lines": {
      "1s": {
        "orbital": "1s",
        "peak_position": 284.8,
        "line_width": 1.0,
        "relative_intensity": 1.0
      }
    },
    "common_compounds": [
      {
        "name": "Graphite",
        "binding_energy": 284.5,
        "chemical_shift": -0.3
      }
    ]
  }
}
```

### visualization - Visualización

**Estado:** 20% completo  
**Ubicación:** `src/xps_analyzer/visualization/`

**Implementado:**
```python
from xps_analyzer.visualization import plot_spectrum, plot_survey

# Plot simple
plot_spectrum(dataset.spectra["C 1s"])

# Survey con identificación
plot_survey(
    dataset.spectra["Survey"],
    reference_db=load_reference_database(),
    annotate_peaks=True
)
```

**Pendiente (Fase 1):**
```python
# Plot con fit
plot_fitted_spectrum(
    spectrum=spectrum,
    fit_result=fit_result,
    show_components=True,
    show_residuals=True
)

# Reporte completo
generate_report(
    dataset=dataset,
    output_format="html",  # o "pdf"
    include_tables=True
)
```

---

## Sistema de Validación

### Fase 0: Validación Manual

**Estado actual:** Implementado en `core.py`

```python
@dataclass
class XPSSpectrum:
    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validación ejecutada después de __init__."""
        # 1. Validar longitudes coincidentes
        if len(self.binding_energy) != len(self.intensity):
            raise ValueError(
                f"binding_energy ({len(self.binding_energy)} puntos) e "
                f"intensity ({len(self.intensity)} puntos) deben tener "
                f"la misma longitud"
            )
        
        # 2. Validar arrays no vacíos
        if len(self.binding_energy) == 0:
            raise ValueError("Los arrays no pueden estar vacíos")
        
        # 3. Validar energías positivas
        if np.any(self.binding_energy <= 0):
            raise ValueError("binding_energy debe contener solo valores positivos")
        
        # 4. Validar nombre de región
        if not self.region_name or not self.region_name.strip():
            raise ValueError("region_name no puede estar vacío")
```

**Ventajas:**
- [COMPLETADO] Simple y explícito
- [COMPLETADO] Sin dependencias externas
- [COMPLETADO] Control total sobre mensajes de error

**Desventajas:**
- [PENDIENTE] Verboso (mucho código boilerplate)
- [PENDIENTE] No reutilizable entre clases
- [PENDIENTE] Sin validación de tipos en runtime

### Fase 2: Migración a Pydantic

**Planeado para v0.3.0** (ver `CHANGELOG.md`)

```python
from pydantic import BaseModel, Field, field_validator
import numpy as np
from numpy.typing import NDArray

class XPSSpectrum(BaseModel):
    """Espectro XPS con validación automática Pydantic."""
    
    region_name: str = Field(..., min_length=1, description="Nombre de región")
    binding_energy: NDArray[np.float64] = Field(..., description="Energías en eV")
    intensity: NDArray[np.float64] = Field(..., description="Intensidades")
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True  # Permite NumPy arrays
    
    @field_validator("binding_energy")
    @classmethod
    def validate_positive_energies(cls, v: NDArray) -> NDArray:
        """Valida que todas las energías sean positivas."""
        if np.any(v <= 0):
            raise ValueError("binding_energy debe contener solo valores positivos")
        return v
    
    @field_validator("intensity")
    @classmethod
    def validate_matching_lengths(cls, v: NDArray, info) -> NDArray:
        """Valida que intensity tenga misma longitud que binding_energy."""
        be = info.data.get("binding_energy")
        if be is not None and len(v) != len(be):
            raise ValueError(
                f"intensity ({len(v)}) debe tener la misma longitud que "
                f"binding_energy ({len(be)})"
            )
        return v
```

**Ventajas de Pydantic:**
- [COMPLETADO] Validación automática de tipos
- [COMPLETADO] JSON schema generation
- [COMPLETADO] Serialización/deserialización automática
- [COMPLETADO] Mensajes de error detallados
- [COMPLETADO] Validación en cascada (dependiente de otros campos)

**Guía de migración:** Ver `CHANGELOG.md` sección `[0.3.0] - Fase 2 - Planeado`

---

## Sistema de Configuración

**Estado:** Documentado en Fase 0, implementación en Fase 1  
**Ubicación:** `config/`

### Estructura de Archivos

```
config/
├── default_settings.toml       # Parámetros de análisis
├── instrument_profiles.toml    # Perfiles de instrumentos XPS
├── element_database.toml       # Base de datos extendida
└── README.md                   # Documentación
```

### Cargador de Configuración (Planeado - Fase 1)

**Ubicación futura:** `src/xps_analyzer/config/loader.py`

```python
from pathlib import Path
import tomli

class ConfigLoader:
    """Carga y valida archivos de configuración TOML."""
    
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            # Buscar en: 1) CWD, 2) ~/.xps_analyzer, 3) package dir
            config_dir = self._find_config_dir()
        self.config_dir = config_dir
    
    def load_settings(self) -> dict:
        """Carga default_settings.toml."""
        path = self.config_dir / "default_settings.toml"
        with open(path, "rb") as f:
            return tomli.load(f)
    
    def load_instrument_profile(self, name: str) -> dict:
        """Carga perfil de instrumento específico."""
        config = self.load_all_instruments()
        if name not in config:
            raise ValueError(f"Instrumento '{name}' no encontrado")
        return config[name]
```

**Uso planeado:**
```python
from xps_analyzer.config import ConfigLoader

# Cargar configuración
config = ConfigLoader()
settings = config.load_settings()

# Usar en análisis
fit_result = fit_peaks(
    spectrum=spectrum,
    method=settings["peak_fitting"]["method"],
    max_iterations=settings["peak_fitting"]["max_iterations"]
)
```

---

## Gestión de Datos de Referencia

### Patrón Singleton

**Problema:** Cargar JSON es lento (~100ms), no queremos cargar múltiples veces.

**Solución:** Cache global con lazy loading.

```python
# Global cache (nivel de módulo)
_reference_database_cache: ReferenceDatabase | None = None

def load_reference_database() -> ReferenceDatabase:
    """
    Retorna base de datos de referencia (cached singleton).
    
    Primera llamada: carga desde JSON (~100ms)
    Llamadas subsecuentes: retorna cache (~1μs)
    """
    global _reference_database_cache
    if _reference_database_cache is None:
        _reference_database_cache = ReferenceDatabase(
            elements=_load_elements_from_json()
        )
    return _reference_database_cache

# Uso
db = load_reference_database()  # Primera llamada: lenta
db = load_reference_database()  # Segunda llamada: instantánea
```

**Trade-off:** Usa ~1MB de memoria durante toda la sesión, pero elimina I/O repetido.

### Deserialización JSON

**Ubicación:** `src/xps_analyzer/reference_data/elements.py:_dict_to_element_reference()`

```python
def _dict_to_element_reference(data: dict) -> ElementReference:
    """
    Convierte dict JSON -> ElementReference.
    
    Maneja líneas fotoelectrónicas anidadas:
    {
      "photoelectron_lines": {
        "1s": {"peak_position": 284.8, ...}
      }
    }
    """
    lines = {
        orbital: PhotoelectronLine(**line_data)
        for orbital, line_data in data.get("photoelectron_lines", {}).items()
    }
    
    return ElementReference(
        symbol=data["symbol"],
        name=data["name"],
        atomic_number=data["atomic_number"],
        photoelectron_lines=lines,
        common_compounds=data.get("common_compounds", [])
    )
```

---

## Pipeline de Procesamiento

### Flujo Típico de Análisis

```python
from xps_analyzer import (
    load_single_file,
    load_reference_database,
    calibrate_dataset,
)
from xps_analyzer.analysis import (
    shirley_background,
    fit_voigt,
    fit_multiple_peaks,
    load_sensitivity_factors,
    calculate_atomic_concentration,
    normalize_to_100,
    PeakParameters
)
from xps_analyzer.visualization import plot_spectrum

# 1. Cargar datos
dataset = load_single_file("data/raw/samples/muestra1.txt")
ref_db = load_reference_database()

# 2. Calibración
calibrate_dataset(dataset, reference_element="C", inplace=True)

# 3. Preprocesamiento (Fase 1)
spectrum = dataset.spectra["C 1s"]
clean = shirley_background(spectrum, max_iterations=50, tolerance=1e-6)

# 4. Análisis (Fase 1)
fit_result = fit_multiple_peaks(
    clean,
    initial_params=[
        PeakParameters(position=284.8, fwhm=1.2),
        PeakParameters(position=286.5, fwhm=1.5)
    ],
    peak_type="voigt"
)

# 5. Visualización
plot_spectrum(clean)

# 6. Cuantificación
rsf = load_sensitivity_factors(source="scofield")
intensities = {"C 1s": 10000, "O 1s": 5000, "N 1s": 1000}
concentrations = calculate_atomic_concentration(intensities, rsf)
normalized = normalize_to_100(concentrations)
print(normalized)  # {"C": 62.5, "O": 31.3, "N": 6.2}
```

### Pipeline Inmutable vs. Mutable

**Patrón 1: Pipeline inmutable (recomendado)**

```python
# Cada paso retorna copia nueva
calibrated = calibrate_spectrum(original, ref_element="C", inplace=False)
cleaned = subtract_background(calibrated, method="shirley")
smoothed = smooth_spectrum(cleaned, method="savgol")

# 'original' nunca se modifica
```

**Patrón 2: Pipeline mutable (performance)**

```python
# Modificar en lugar para evitar copias
spectrum = dataset.spectra["C 1s"].copy()  # Copia una vez
calibrate_spectrum(spectrum, ref_element="C", inplace=True)
subtract_background(spectrum, method="shirley", inplace=True)
smooth_spectrum(spectrum, method="savgol", inplace=True)

# Más eficiente en memoria, pero más peligroso
```

---

## Decisiones de Diseño

### 1. ¿Por qué dataclasses en lugar de clases normales?

**Decisión:** Usar `@dataclass` para estructuras de datos

**Razones:**
- [COMPLETADO] Menos boilerplate (`__init__`, `__repr__` automáticos)
- [COMPLETADO] Integración con type hints
- [COMPLETADO] Fácil migración a Pydantic (sintaxis similar)
- [COMPLETADO] Inmutabilidad opcional con `frozen=True`

**Alternativas rechazadas:**
- [PENDIENTE] Clases normales: demasiado verboso
- [PENDIENTE] NamedTuples: inmutables pero sin validación
- [PENDIENTE] TypedDict: no son objetos reales

### 2. ¿Por qué NumPy en lugar de Pandas?

**Decisión:** Usar NumPy arrays para datos espectrales (deprecar Pandas progresivamente)

**Razones:**
- [COMPLETADO] Más ligero (Pandas depende de NumPy)
- [COMPLETADO] Más rápido para operaciones vectorizadas
- [COMPLETADO] Integración directa con scipy
- [COMPLETADO] Menos overhead de memoria

**Estado actual:** `XPSSpectrum` usa NumPy, pero algunos módulos usan Pandas. Meta: eliminar Pandas en Fase 2.

### 3. ¿Por qué múltiples niveles jerárquicos?

**Decisión:** Jerarquía de 3 niveles (Spectrum -> Dataset -> Sample)

**Razones:**
- [COMPLETADO] Separación clara de responsabilidades
- [COMPLETADO] Facilita depth profiling (múltiples datasets por muestra)
- [COMPLETADO] Permite análisis comparativo
- [COMPLETADO] Refleja organización real de experimentos

**Alternativa rechazada:** Estructura plana con un solo tipo - demasiado limitado para casos avanzados.

### 4. ¿Por qué validación manual en Fase 0?

**Decisión:** Usar `__post_init__` ahora, migrar a Pydantic en Fase 2

**Razones:**
- [COMPLETADO] Sin dependencias extra al inicio
- [COMPLETADO] Más fácil de entender para nuevos desarrolladores
- [COMPLETADO] Suficiente para funcionalidad básica
- [COMPLETADO] Migración a Pydantic es no-breaking (sintaxis compatible)

### 5. ¿Por qué TOML para configuración?

**Decisión:** TOML en lugar de YAML/JSON/INI

**Razones:**
- [COMPLETADO] Más legible que JSON (permite comentarios)
- [COMPLETADO] Más seguro que YAML (no code execution)
- [COMPLETADO] Estándar moderno (usado por `pyproject.toml`)
- [COMPLETADO] Soporte nativo en Python 3.11+ (`tomllib`)

---

## Patrones y Convenciones

### Patrón: Funciones con parámetro `inplace`

**Convención:** Todas las funciones de procesamiento aceptan `inplace: bool`

```python
def calibrate_spectrum(
    spectrum: XPSSpectrum,
    reference_element: str,
    inplace: bool = False
) -> XPSSpectrum:
    """
    Calibra espectro.
    
    Parámetros
    ----------
    inplace : bool, default False
        Si True, modifica el espectro en lugar.
        Si False, retorna copia modificada.
    """
    if inplace:
        spectrum.binding_energy += shift
        return spectrum
    else:
        return spectrum.copy().calibrate(shift)
```

**Razones:**
- Flexibilidad para usuario (performance vs. seguridad)
- Consistencia en toda la API
- Explícito mejor que implícito

### Patrón: Inversión de eje X en plots

**Convención:** SIEMPRE invertir eje X en plots XPS

```python
def plot_spectrum(spectrum: XPSSpectrum):
    plt.plot(spectrum.binding_energy, spectrum.intensity)
    plt.xlabel("Binding Energy (eV)")
    plt.ylabel("Intensity (a.u.)")
    plt.gca().invert_xaxis()  # <- CRÍTICO
    plt.show()
```

**Razón:** Convención universal en espectroscopía XPS (alta energía a la izquierda).

### Patrón: Búsqueda con tolerancia

**Convención:** Búsquedas de energía usan parámetro `tolerance`

```python
def find_element_by_energy(
    energy: float,
    tolerance: float = 2.0  # eV
) -> list[tuple[str, str]]:
    """Retorna elementos dentro de ±tolerance."""
```

**Razón:** Resolución instrumental (~0.5-1 eV) hace matching exacto imposible.

---

## Extensibilidad

### Sistema de Plugins (Fase 3)

**Objetivo:** Permitir formatos de archivo personalizados sin modificar core.

```python
# Futuro: src/xps_analyzer/data_loader/plugins/base.py
from abc import ABC, abstractmethod

class FileFormatPlugin(ABC):
    """Base class para plugins de formato."""
    
    @abstractmethod
    def can_handle(self, filepath: Path) -> bool:
        """Retorna True si el plugin puede leer este archivo."""
    
    @abstractmethod
    def load(self, filepath: Path) -> XPSDataset:
        """Carga archivo y retorna XPSDataset."""

# Implementación
class MyCustomFormatPlugin(FileFormatPlugin):
    def can_handle(self, filepath: Path) -> bool:
        return filepath.suffix == ".custom"
    
    def load(self, filepath: Path) -> XPSDataset:
        # Implementación personalizada
        ...

# Registro
from xps_analyzer.data_loader import register_plugin
register_plugin(MyCustomFormatPlugin())
```

### Métodos de Análisis Personalizados

```python
# Futuro: src/xps_analyzer/analysis/plugins/
class CustomBackgroundMethod:
    """Método personalizado de sustracción de fondo."""
    
    def __call__(
        self,
        spectrum: XPSSpectrum,
        **kwargs
    ) -> XPSSpectrum:
        # Implementación
        ...

# Uso
from xps_analyzer.analysis import subtract_background
from my_package import my_custom_background

result = subtract_background(
    spectrum=spectrum,
    method=my_custom_background,  # Callable personalizado
    custom_param=42
)
```

---

## Referencias

### Estándares XPS
- ISO 14976:2018 - Surface chemical analysis - Data transfer format
- ISO 18115-1:2023 - Surface chemical analysis - Vocabulary

### Publicaciones Científicas
- Shirley, D. A. (1972). "Background in the XPS spectra of metals"
- Tougaard, S. (2020). "Practical guide to the use of backgrounds in XPS"

### Herramientas Relacionadas
- **CASA XPS** - Software comercial líder
- **XPSPy** - Librería Python para XPS (pero sin mantenimiento desde 2019)
- **Larch** - Análisis de espectroscopía (más enfocado en XAS)

---

**Última actualización:** Marzo 2026  
**Próxima revisión:** Después de completar Sesión 4 (Export System)  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
