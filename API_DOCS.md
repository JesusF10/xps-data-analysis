# XPS Analyzer - Referencia de API

**Versión:** 0.8.0-beta  
**Estado:** Fase 1 COMPLETADA (100%) - Análisis Core + Exportación  
**Última actualización:** Marzo 2026

Esta es la referencia completa de la API pública de XPS Analyzer. Incluye todas las funciones, clases y métodos disponibles para usuarios finales.

**ACTUALIZACIÓN v0.8.0**: Sistema de exportación completo (CSV, Excel, JSON) - Fase 1 100% completada
**ACTUALIZACIÓN v0.7.0**: Agregado módulo completo de análisis (background, peak_fitting, quantification)

---

## Tabla de Contenidos

1. [Instalación](#instalación)
2. [API de Alto Nivel](#api-de-alto-nivel)
3. [Estructuras de Datos](#estructuras-de-datos)
4. [Carga de Datos](#carga-de-datos)
5. [Preprocesamiento](#preprocesamiento)
6. [Análisis Espectral](#análisis-espectral)
7. [Datos de Referencia](#datos-de-referencia)
8. [Visualización](#visualización)
9. [Exportación](#exportación)
10. [CLI](#cli)

---

## Instalación

```bash
# Con uv (recomendado)
uv pip install xps-analyzer

# Con pip
pip install xps-analyzer

# Desde código fuente
git clone https://github.com/tu-usuario/xps-analyzer.git
cd xps-analyzer
uv sync
```

**Importar:**
```python
import xps_analyzer
from xps_analyzer import load_single_file, load_reference_database
```

---

## API de Alto Nivel

### load_single_file

```python
def load_single_file(filepath: str | Path) -> XPSDataset
```

Carga un archivo XPS individual y retorna dataset completo.

**Parámetros:**
- `filepath` : `str` o `Path`  
  Path al archivo XPS (formato propietario de texto)

**Retorna:**
- `XPSDataset`  
  Dataset con todos los espectros y metadata

**Lanza:**
- `FileNotFoundError` - Si el archivo no existe
- `ValueError` - Si el formato es inválido

**Ejemplo:**
```python
from xps_analyzer import load_single_file

# Cargar archivo
dataset = load_single_file("data/raw/samples/muestra1.txt")

# Acceder a espectros
c1s = dataset.spectra["C 1s"]
print(f"Región: {c1s.region_name}")
print(f"Puntos: {len(c1s.binding_energy)}")

# Ver metadata
print(dataset.header)  # {'sample_name': 'muestra1', 'date': '2023-10-01', ...}
```

**Ver también:**
- [`load_all_data()`](#load_all_data) - Cargar múltiples archivos (Fase 1)
- [`XPSDataset`](#xpsdataset) - Estructura de datos retornada

---

### load_reference_database

```python
def load_reference_database() -> ReferenceDatabase
```

Carga base de datos de elementos de referencia (cached singleton).

**Retorna:**
- `ReferenceDatabase`  
  Base de datos completa con ~25 elementos

**Ejemplo:**
```python
from xps_analyzer import load_reference_database

# Cargar base de datos (primera llamada: ~100ms, subsecuentes: ~1μs)
db = load_reference_database()

# Buscar elemento
carbon = db.get_element("C")
print(carbon.name)  # "Carbon"
print(carbon.photoelectron_lines["1s"].peak_position)  # 284.8

# Identificar por energía
matches = db.find_element_by_energy(531.0, tolerance=2.0)
print(matches)  # [("O", "1s"), ...]
```

**Ver también:**
- [`ReferenceDatabase`](#referencedatabase) - Clase de base de datos
- [`ElementReference`](#elementreference) - Clase de elemento individual

---

### load_all_data

```python
def load_all_data(
    directory: str | Path,
    pattern: str = "*.txt",
    recursive: bool = False
) -> XPSSample
```

**Estado:** PENDIENTE - Fase 1

Carga todos los archivos XPS en un directorio.

**Parámetros:**
- `directory` : `str` o `Path`  
  Path al directorio con archivos XPS
- `pattern` : `str`, default `"*.txt"`  
  Patrón glob para filtrar archivos
- `recursive` : `bool`, default `False`  
  Si True, busca en subdirectorios

**Retorna:**
- `XPSSample`  
  Muestra con todos los datasets cargados

**Ejemplo futuro:**
```python
from xps_analyzer import load_all_data

# Cargar todos los archivos .txt
sample = load_all_data("data/raw/samples/muestra1/")

# Acceder a datasets individuales
for filename, dataset in sample.datasets.items():
    print(f"{filename}: {len(dataset.spectra)} regiones")
```

---

## Estructuras de Datos

### XPSSpectrum

```python
@dataclass
class XPSSpectrum:
    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)
```

Representa un espectro XPS individual (survey o región de alta resolución).

**Atributos:**

- **region_name** : `str`  
  Identificador de región (ej: "C 1s", "O 1s", "Survey")

- **binding_energy** : `np.ndarray`  
  Array 1D de energías de enlace en eV (shape: `(n,)`)

- **intensity** : `np.ndarray`  
  Array 1D de intensidades en cuentas arbitrarias (shape: `(n,)`)

- **metadata** : `dict[str, Any]`  
  Metadata adicional (sweeps, dwell_time, pass_energy, etc.)

**Invariantes:**
- `len(binding_energy) == len(intensity)` (validado en `__post_init__`)
- Ambos arrays tienen longitud > 0
- `binding_energy` contiene solo valores positivos
- `region_name` no está vacío

**Métodos futuros (Fase 1):**
```python
def copy(self) -> XPSSpectrum:
    """Crea copia profunda del espectro."""
    
def to_dict(self) -> dict:
    """Serializa a diccionario."""
    
@classmethod
def from_dict(cls, data: dict) -> "XPSSpectrum":
    """Deserializa desde diccionario."""
```

**Ejemplo:**
```python
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum

# Crear espectro manualmente
spectrum = XPSSpectrum(
    region_name="C 1s",
    binding_energy=np.array([280.0, 281.0, 282.0, 283.0, 284.0]),
    intensity=np.array([100, 150, 200, 250, 300]),
    metadata={"sweeps": 5, "dwell_time": 0.1}
)

# Acceder a datos
print(f"Región: {spectrum.region_name}")
print(f"Rango de energía: {spectrum.binding_energy.min():.1f} - {spectrum.binding_energy.max():.1f} eV")
print(f"Intensidad máxima: {spectrum.intensity.max()}")

# Operaciones NumPy
mean_intensity = spectrum.intensity.mean()
peak_position = spectrum.binding_energy[spectrum.intensity.argmax()]
```

**Ver también:**
- [`XPSDataset`](#xpsdataset) - Contenedor de múltiples espectros

---

### XPSDataset

```python
@dataclass
class XPSDataset:
    filename: str
    header: dict[str, Any] = field(default_factory=dict)
    spectra: dict[str, XPSSpectrum] = field(default_factory=dict)
```

Representa un archivo XPS completo con múltiples espectros (survey + regiones).

**Atributos:**

- **filename** : `str`  
  Path al archivo original

- **header** : `dict[str, Any]`  
  Metadata global (sample_name, date, operator, instrument, etc.)

- **spectra** : `dict[str, XPSSpectrum]`  
  Mapeo de `region_name` → `XPSSpectrum`

**Invariantes:**
- `filename` no está vacío
- `spectra` contiene al menos un espectro

**Métodos futuros (Fase 1):**
```python
def get_spectrum(self, region_name: str) -> XPSSpectrum | None:
    """Obtiene espectro por nombre de región."""
    
def get_high_resolution_spectra(self) -> dict[str, XPSSpectrum]:
    """Retorna solo espectros de alta resolución (excluye Survey)."""
    
def get_survey(self) -> XPSSpectrum | None:
    """Retorna espectro survey si existe."""
```

**Ejemplo:**
```python
from xps_analyzer import load_single_file

# Cargar dataset
dataset = load_single_file("data/raw/muestra1.txt")

# Acceder a header
print(f"Muestra: {dataset.header.get('sample_name', 'Desconocida')}")
print(f"Fecha: {dataset.header.get('date', 'N/A')}")

# Iterar sobre espectros
for region_name, spectrum in dataset.spectra.items():
    print(f"{region_name}: {len(spectrum.binding_energy)} puntos")

# Acceder a espectro específico
if "C 1s" in dataset.spectra:
    c1s = dataset.spectra["C 1s"]
    print(f"C 1s tiene {len(c1s.binding_energy)} puntos de datos")

# Filtrar regiones de alta resolución
high_res = {k: v for k, v in dataset.spectra.items() if k != "Survey"}
print(f"Regiones de alta resolución: {list(high_res.keys())}")
```

**Ver también:**
- [`XPSSpectrum`](#xpsspectrum) - Espectro individual
- [`XPSSample`](#xpssample) - Múltiples datasets

---

### XPSSample

```python
@dataclass
class XPSSample:
    sample_name: str
    datasets: dict[str, XPSDataset] = field(default_factory=dict)
```

Representa una muestra física con múltiples mediciones (múltiples archivos).

**Atributos:**

- **sample_name** : `str`  
  Identificador único de muestra

- **datasets** : `dict[str, XPSDataset]`  
  Mapeo de `filename` → `XPSDataset`

**Casos de uso:**
- Depth profiling (múltiples mediciones a diferentes profundidades)
- Time series (mediciones a lo largo del tiempo)
- Análisis comparativo (diferentes condiciones de tratamiento)

**Ejemplo futuro (Fase 1):**
```python
from xps_analyzer import load_all_data

# Cargar muestra con múltiples archivos
sample = load_all_data("data/raw/TiO2_depth_profile/", pattern="*.txt")

# Iterar sobre datasets
for filename, dataset in sample.datasets.items():
    print(f"{filename}:")
    for region_name in dataset.spectra:
        print(f"  - {region_name}")

# Análisis comparativo
compositions = {}
for filename, dataset in sample.datasets.items():
    comp = quantify(dataset)
    compositions[filename] = comp

# Plotear depth profile
import matplotlib.pyplot as plt
depths = [0, 10, 20, 30, 40]  # nm
ti_content = [compositions[f]["Ti"] for f in sorted(compositions)]
plt.plot(depths, ti_content)
plt.xlabel("Depth (nm)")
plt.ylabel("Ti atomic %")
```

---

## Carga de Datos

### Namespace: `xps_analyzer.data_loader`

**Importar:**
```python
from xps_analyzer.data_loader import XPSSpectrum, XPSDataset, XPSSample
```

**API pública:**
- [`XPSSpectrum`](#xpsspectrum) - Espectro individual
- [`XPSDataset`](#xpsdataset) - Archivo completo
- [`XPSSample`](#xpssample) - Múltiples archivos

**Funciones de parsing (internas):**
```python
# NO usar directamente - usar load_single_file() en su lugar
def parse_metadata(lines: list[str] | str, header: bool = False) -> dict[str, Any]
def get_spectrum_data(lines: list[str]) -> dict[str, XPSSpectrum]
```

---

## Preprocesamiento

### Namespace: `xps_analyzer.preprocessing`

**Estado:** 25% completo

**Importar:**
```python
from xps_analyzer.preprocessing import calibrate_spectrum, calibrate_dataset
```

---

### calibrate_spectrum

```python
def calibrate_spectrum(
    spectrum: XPSSpectrum,
    reference_element: str,
    reference_energy: float | None = None,
    inplace: bool = False
) -> XPSSpectrum
```

Calibra un espectro XPS usando un elemento de referencia.

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a calibrar

- `reference_element` : `str`  
  Símbolo del elemento de referencia (ej: "C", "Au")

- `reference_energy` : `float | None`, default `None`  
  Energía de referencia manual en eV. Si `None`, usa valor de base de datos.

- `inplace` : `bool`, default `False`  
  Si `True`, modifica el espectro en lugar. Si `False`, retorna copia.

**Retorna:**
- `XPSSpectrum`  
  Espectro calibrado (nuevo objeto si `inplace=False`, mismo si `inplace=True`)

**Lanza:**
- `ValueError` - Si el elemento de referencia no está en la base de datos

**Ejemplo:**
```python
from xps_analyzer import load_single_file
from xps_analyzer.preprocessing import calibrate_spectrum

# Cargar datos
dataset = load_single_file("data/raw/muestra1.txt")
c1s = dataset.spectra["C 1s"]

# Calibración (retorna copia)
calibrated = calibrate_spectrum(
    spectrum=c1s,
    reference_element="C",  # C 1s @ 284.8 eV
    inplace=False
)

# Original no modificado
assert c1s.binding_energy[0] == calibrated.binding_energy[0] - shift

# Calibración inplace
calibrate_spectrum(c1s, "C", inplace=True)
# Ahora c1s está modificado
```

**Notas:**
- Elemento de referencia por defecto: C 1s @ 284.8 eV (carbono adventicio)
- El desplazamiento se calcula como: `shift = reference_energy - observed_peak_max`
- Solo ajusta `binding_energy`, no modifica `intensity`

**Ver también:**
- [`calibrate_dataset()`](#calibrate_dataset) - Calibrar dataset completo

---

### calibrate_dataset

```python
def calibrate_dataset(
    dataset: XPSDataset,
    reference_element: str = "C",
    reference_energy: float | None = None,
    inplace: bool = True
) -> XPSDataset
```

Calibra todos los espectros en un dataset usando elemento de referencia.

**Parámetros:**
- `dataset` : `XPSDataset`  
  Dataset con múltiples espectros

- `reference_element` : `str`, default `"C"`  
  Símbolo del elemento de referencia

- `reference_energy` : `float | None`, default `None`  
  Energía de referencia manual en eV

- `inplace` : `bool`, default `True`  
  Si `True`, modifica dataset en lugar (default diferente a `calibrate_spectrum`)

**Retorna:**
- `XPSDataset`  
  Dataset calibrado

**Lanza:**
- `ValueError` - Si el elemento de referencia no existe en ningún espectro del dataset

**Ejemplo:**
```python
from xps_analyzer import load_single_file
from xps_analyzer.preprocessing import calibrate_dataset

# Cargar datos
dataset = load_single_file("data/raw/muestra1.txt")

# Calibrar todos los espectros con C 1s
calibrate_dataset(dataset, reference_element="C", inplace=True)

# Ahora todos los espectros están calibrados
for region_name, spectrum in dataset.spectra.items():
    print(f"{region_name}: calibrado")
```

**Ver también:**
- [`calibrate_spectrum()`](#calibrate_spectrum) - Calibrar espectro individual

---

### subtract_background

**Estado:** PENDIENTE - Fase 1

```python
def subtract_background(
    spectrum: XPSSpectrum,
    method: str = "shirley",
    energy_range: tuple[float, float] | None = None,
    inplace: bool = False
) -> XPSSpectrum
```

Sustrae fondo (background) de un espectro XPS.

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a procesar

- `method` : `str`, default `"shirley"`  
  Método de sustracción: `"shirley"`, `"tougaard"`, `"linear"`

- `energy_range` : `tuple[float, float] | None`, default `None`  
  Rango de energía en eV `(min, max)`. Si `None`, usa rango completo.

- `inplace` : `bool`, default `False`  
  Si `True`, modifica espectro en lugar

**Retorna:**
- `XPSSpectrum`  
  Espectro con fondo sustraído

**Ejemplo futuro:**
```python
from xps_analyzer.preprocessing import subtract_background

# Método Shirley (más común)
clean = subtract_background(
    spectrum=c1s,
    method="shirley",
    energy_range=(280, 295)
)

# Método Tougaard (más físico)
clean = subtract_background(c1s, method="tougaard")

# Fondo lineal (simple)
clean = subtract_background(c1s, method="linear")
```

---

## Análisis Espectral

### Namespace: `xps_analyzer.analysis`

**Estado:** MÓDULO VACÍO - Fase 1

**API planeada:**
```python
from xps_analyzer.analysis import (
    find_peaks,
    fit_peaks,
    quantify
)
```

---

### find_peaks

**Estado:** PENDIENTE - Fase 1

```python
def find_peaks(
    spectrum: XPSSpectrum,
    threshold: float = 0.1,
    min_distance: float = 2.0,
    prominence: float | None = None
) -> list[float]
```

Detecta picos en un espectro XPS automáticamente.

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a analizar

- `threshold` : `float`, default `0.1`  
  Umbral como fracción de intensidad máxima (0-1)

- `min_distance` : `float`, default `2.0`  
  Separación mínima entre picos en eV

- `prominence` : `float | None`, default `None`  
  Prominencia mínima de picos. Si `None`, usa automático.

**Retorna:**
- `list[float]`  
  Lista de posiciones de picos en eV (ordenadas por intensidad descendente)

**Ejemplo futuro:**
```python
from xps_analyzer.analysis import find_peaks

# Detección automática
peaks = find_peaks(spectrum, threshold=0.2)
print(f"Encontrados {len(peaks)} picos: {peaks}")

# Ajustar sensibilidad
peaks = find_peaks(
    spectrum,
    threshold=0.05,      # Más sensible
    min_distance=1.0,    # Picos más cercanos
    prominence=100       # Mayor prominencia requerida
)
```

---

### fit_peaks

**Estado:** PENDIENTE - Fase 1

```python
def fit_peaks(
    spectrum: XPSSpectrum,
    peak_positions: list[float],
    peak_shapes: list[str] | None = None,
    background: str = "shirley",
    max_iterations: int = 1000,
    tolerance: float = 1e-6
) -> FitResult
```

Ajusta picos gaussianos/lorentzianos/voigt a un espectro XPS.

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a ajustar

- `peak_positions` : `list[float]`  
  Posiciones iniciales de picos en eV

- `peak_shapes` : `list[str] | None`, default `None`  
  Formas de pico para cada posición: `"gaussian"`, `"lorentzian"`, `"voigt"`.  
  Si `None`, usa `"voigt"` para todos.

- `background` : `str`, default `"shirley"`  
  Método de fondo: `"shirley"`, `"tougaard"`, `"linear"`, `"none"`

- `max_iterations` : `int`, default `1000`  
  Máximo de iteraciones para convergencia

- `tolerance` : `float`, default `1e-6`  
  Tolerancia para convergencia

**Retorna:**
- `FitResult`  
  Objeto con resultados del ajuste (ver [`FitResult`](#fitresult))

**Lanza:**
- `ValueError` - Si `peak_positions` está vacío o tiene longitud diferente a `peak_shapes`
- `FitError` - Si el ajuste no converge

**Ejemplo futuro:**
```python
from xps_analyzer.analysis import fit_peaks

# Ajuste básico
result = fit_peaks(
    spectrum=c1s,
    peak_positions=[284.8, 286.5, 288.9],  # 3 picos en C 1s
    peak_shapes=["voigt", "voigt", "voigt"]
)

print(f"χ² = {result.chi_squared:.4f}")
print(f"Convergió: {result.success}")

# Acceder a parámetros ajustados
for i, peak in enumerate(result.peak_params):
    print(f"Pico {i+1}:")
    print(f"  Posición: {peak['position']:.2f} eV")
    print(f"  Amplitud: {peak['amplitude']:.1f}")
    print(f"  FWHM: {peak['fwhm']:.2f} eV")
    print(f"  Área: {peak['area']:.1f}")
```

---

### FitResult

**Estado:** PENDIENTE - Fase 1

```python
@dataclass
class FitResult:
    peak_params: list[dict[str, float]]
    fitted_curve: np.ndarray
    residuals: np.ndarray
    chi_squared: float
    success: bool
    message: str
```

Resultado de ajuste de picos.

**Atributos:**

- **peak_params** : `list[dict[str, float]]`  
  Parámetros ajustados para cada pico. Cada dict contiene:
  - `position`: Posición del pico (eV)
  - `amplitude`: Amplitud
  - `fwhm`: Full Width at Half Maximum (eV)
  - `area`: Área bajo el pico
  - `gaussian_fraction`: Fracción gaussiana (solo voigt)

- **fitted_curve** : `np.ndarray`  
  Curva ajustada total (sum de todos los picos + fondo)

- **residuals** : `np.ndarray`  
  Diferencia entre datos experimentales y ajuste

- **chi_squared** : `float`  
  Bondad de ajuste (χ²)

- **success** : `bool`  
  `True` si el ajuste convergió

- **message** : `str`  
  Mensaje descriptivo del resultado

---

### quantify

**Estado:** PENDIENTE - Fase 1

```python
def quantify(
    dataset: XPSDataset,
    use_sensitivity_factors: bool = True,
    normalize: bool = True,
    reference_element: str | None = None
) -> dict[str, float]
```

Cuantifica composición elemental a partir de un dataset XPS.

**Parámetros:**
- `dataset` : `XPSDataset`  
  Dataset con espectros calibrados

- `use_sensitivity_factors` : `bool`, default `True`  
  Si `True`, aplica factores de sensibilidad atómica

- `normalize` : `bool`, default `True`  
  Si `True`, normaliza a 100% (retorna porcentajes atómicos)

- `reference_element` : `str | None`, default `None`  
  Elemento de referencia para normalización relativa

**Retorna:**
- `dict[str, float]`  
  Mapeo de `symbol` → concentración (porcentaje atómico o relativo)

**Ejemplo futuro:**
```python
from xps_analyzer.analysis import quantify

# Cuantificación estándar
composition = quantify(dataset, use_sensitivity_factors=True, normalize=True)
print(composition)
# {'C': 65.2, 'O': 28.3, 'N': 6.5}

# Sin factores de sensibilidad (áreas crudas)
raw_areas = quantify(dataset, use_sensitivity_factors=False, normalize=False)

# Normalización relativa a carbono
relative = quantify(dataset, normalize=False, reference_element="C")
print(relative)
# {'C': 1.0, 'O': 0.43, 'N': 0.10}  # Ratios atómicos
```

---

## Datos de Referencia

### Namespace: `xps_analyzer.reference_data`

**Estado:** 85% completo

**Importar:**
```python
from xps_analyzer.reference_data import (
    load_reference_database,
    ReferenceDatabase,
    ElementReference,
    PhotoelectronLine
)
```

---

### ReferenceDatabase

```python
@dataclass
class ReferenceDatabase:
    elements: dict[str, ElementReference]
```

Base de datos completa de elementos XPS.

**Atributos:**
- **elements** : `dict[str, ElementReference]`  
  Mapeo de símbolo (ej: "C") → `ElementReference`

**Métodos:**

#### get_element

```python
def get_element(self, symbol: str) -> ElementReference | None
```

Obtiene elemento por símbolo (case-insensitive).

**Ejemplo:**
```python
db = load_reference_database()

carbon = db.get_element("C")
print(carbon.name)  # "Carbon"

# Case-insensitive
oxygen = db.get_element("o")  # Funciona con minúscula
print(oxygen.name)  # "Oxygen"
```

#### find_element_by_energy

```python
def find_element_by_energy(
    self,
    energy: float,
    tolerance: float = 2.0
) -> list[tuple[str, str]]
```

Encuentra elementos con líneas cerca de una energía dada.

**Parámetros:**
- `energy` : `float` - Energía de enlace en eV
- `tolerance` : `float`, default `2.0` - Tolerancia de búsqueda en eV

**Retorna:**
- `list[tuple[str, str]]` - Lista de `(symbol, orbital)` dentro de tolerancia

**Ejemplo:**
```python
db = load_reference_database()

# Buscar qué elementos tienen picos cerca de 284.8 eV
matches = db.find_element_by_energy(284.8, tolerance=1.0)
print(matches)
# [("C", "1s"), ("Cd", "3d5/2"), ...]

# Buscar con mayor tolerancia
matches = db.find_element_by_energy(531.0, tolerance=3.0)
print(matches)
# [("O", "1s"), ("Sb", "3d3/2"), ...]
```

---

### ElementReference

```python
@dataclass
class ElementReference:
    symbol: str
    name: str
    atomic_number: int
    photoelectron_lines: dict[str, PhotoelectronLine]
    common_compounds: list[dict]
```

Información de referencia de un elemento químico.

**Atributos:**
- **symbol** : `str` - Símbolo químico (ej: "C", "O")
- **name** : `str` - Nombre completo (ej: "Carbon", "Oxygen")
- **atomic_number** : `int` - Número atómico
- **photoelectron_lines** : `dict[str, PhotoelectronLine]` - Líneas espectrales
- **common_compounds** : `list[dict]` - Estados de oxidación comunes

**Ejemplo:**
```python
db = load_reference_database()
carbon = db.get_element("C")

print(f"Símbolo: {carbon.symbol}")
print(f"Nombre: {carbon.name}")
print(f"Z: {carbon.atomic_number}")

# Líneas fotoelectrónicas
c1s = carbon.photoelectron_lines["1s"]
print(f"C 1s @ {c1s.peak_position} eV")

# Compuestos comunes
for compound in carbon.common_compounds:
    print(f"{compound['name']}: {compound['binding_energy']} eV")
```

---

### PhotoelectronLine

```python
@dataclass
class PhotoelectronLine:
    orbital: str
    peak_position: float
    line_width: float
    relative_intensity: float
```

Línea fotoelectrónica individual (ej: C 1s, O 1s).

**Atributos:**
- **orbital** : `str` - Orbital atómico (ej: "1s", "2p3/2")
- **peak_position** : `float` - Energía de enlace en eV
- **line_width** : `float` - Ancho de línea natural (FWHM) en eV
- **relative_intensity** : `float` - Intensidad relativa (0-1)

**Ejemplo:**
```python
db = load_reference_database()
carbon = db.get_element("C")
c1s = carbon.photoelectron_lines["1s"]

print(f"Orbital: {c1s.orbital}")
print(f"Posición: {c1s.peak_position} eV")
print(f"Ancho: {c1s.line_width} eV")
print(f"Intensidad: {c1s.relative_intensity}")
```

---

## Visualización

### Namespace: `xps_analyzer.visualization`

**Estado:** 20% completo

**Importar:**
```python
from xps_analyzer.visualization import plot_spectrum, plot_survey
```

---

### plot_spectrum

```python
def plot_spectrum(
    spectrum: XPSSpectrum,
    title: str | None = None,
    show: bool = True
) -> None
```

Genera plot simple de un espectro XPS.

**Parámetros:**
- `spectrum` : `XPSSpectrum` - Espectro a plotear
- `title` : `str | None`, default `None` - Título custom (usa `region_name` si None)
- `show` : `bool`, default `True` - Si `True`, llama `plt.show()`

**Ejemplo:**
```python
from xps_analyzer import load_single_file
from xps_analyzer.visualization import plot_spectrum

dataset = load_single_file("data/raw/muestra1.txt")
c1s = dataset.spectra["C 1s"]

# Plot básico
plot_spectrum(c1s)

# Plot con título custom
plot_spectrum(c1s, title="C 1s - Muestra TiO2")

# Plot sin mostrar (para guardar)
plot_spectrum(c1s, show=False)
import matplotlib.pyplot as plt
plt.savefig("c1s.png", dpi=300)
plt.close()
```

**Convenciones:**
- Eje X invertido (alta energía a la izquierda) - estándar XPS
- Xlabel: "Binding Energy (eV)"
- Ylabel: "Intensity (a.u.)"

---

### plot_survey

```python
def plot_survey(
    spectrum: XPSSpectrum,
    reference_db: ReferenceDatabase | None = None,
    annotate_peaks: bool = False,
    title: str | None = None,
    show: bool = True
) -> None
```

Plotea espectro survey con identificación opcional de picos.

**Parámetros:**
- `spectrum` : `XPSSpectrum` - Espectro survey
- `reference_db` : `ReferenceDatabase | None`, default `None` - Base de datos para identificación
- `annotate_peaks` : `bool`, default `False` - Si `True`, anota picos identificados
- `title` : `str | None`, default `None` - Título custom
- `show` : `bool`, default `True` - Si `True`, llama `plt.show()`

**Ejemplo:**
```python
from xps_analyzer import load_single_file, load_reference_database
from xps_analyzer.visualization import plot_survey

dataset = load_single_file("data/raw/muestra1.txt")
survey = dataset.spectra["Survey"]
db = load_reference_database()

# Plot con anotaciones
plot_survey(
    spectrum=survey,
    reference_db=db,
    annotate_peaks=True,
    title="Survey - Muestra TiO2"
)
```

---

### plot_fitted_spectrum

**Estado:** PENDIENTE - Fase 1

```python
def plot_fitted_spectrum(
    spectrum: XPSSpectrum,
    fit_result: FitResult,
    show_components: bool = True,
    show_residuals: bool = True,
    show: bool = True
) -> None
```

Plotea espectro con fit de picos.

**Ejemplo futuro:**
```python
from xps_analyzer.analysis import fit_peaks
from xps_analyzer.visualization import plot_fitted_spectrum

result = fit_peaks(c1s, peak_positions=[284.8, 286.5, 288.9])

plot_fitted_spectrum(
    spectrum=c1s,
    fit_result=result,
    show_components=True,   # Mostrar picos individuales
    show_residuals=True     # Panel de residuales debajo
)
```

---

## Exportación

### Namespace: `xps_analyzer.export`

**Estado:** COMPLETADO - v0.8.0

Módulo completo para exportar espectros XPS y datasets a formatos estándar (CSV, Excel, JSON) con metadata completa.

**API pública:**
```python
from xps_analyzer.export import export_to_csv, export_to_excel, export_to_json
```

---

### export_to_csv

**Estado:** COMPLETADO - v0.8.0

```python
def export_to_csv(
    data: XPSSpectrum | XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True,
    decimal_places: int = 6
) -> Path
```

Exporta espectro o dataset XPS a archivo(s) CSV.

**Parámetros:**
- `data` : `XPSSpectrum` o `XPSDataset`  
  Datos a exportar. Si es XPSSpectrum, crea un archivo CSV. Si es XPSDataset, crea un directorio con múltiples archivos CSV (uno por región).
- `output_path` : `str` o `Path`  
  Ruta del archivo o directorio de salida.
- `include_metadata` : `bool`, default `True`  
  Si True, genera archivos `.metadata.csv` adicionales con metadata.
- `decimal_places` : `int`, default `6`  
  Número de decimales para valores numéricos.

**Retorna:**
- `Path`  
  Ruta del archivo o directorio creado.

**Lanza:**
- `TypeError` - Si data no es XPSSpectrum ni XPSDataset

**Ejemplo:**
```python
from xps_analyzer import load_single_file
from xps_analyzer.export import export_to_csv

dataset = load_single_file("muestra1.txt")
spectrum = dataset.get_spectrum("C 1s")

# Exportar espectro individual
export_to_csv(spectrum, "output/c1s.csv", include_metadata=True)
# Crea: output/c1s.csv + output/c1s.metadata.csv

# Exportar dataset completo
export_to_csv(dataset, "output/dataset_export/", include_metadata=True)
# Crea: output/dataset_export/C_1s.csv, O_1s.csv, dataset_metadata.csv, ...

# Controlar precisión
export_to_csv(spectrum, "output/high_prec.csv", decimal_places=10)
```

**Estructura CSV - Espectro:**
```csv
binding_energy,intensity
280.0,145.234567
280.2,148.123456
...
```

**Estructura CSV - Metadata:**
```csv
key,value
region_name,C 1s
sweeps,10
dwell_time,0.1
pass_energy,20.0
```

---

### export_to_excel

**Estado:** COMPLETADO - v0.8.0

```python
def export_to_excel(
    data: XPSSpectrum | XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True,
    decimal_places: int = 6
) -> Path
```

Exporta espectro o dataset XPS a archivo Excel (.xlsx).

Crea un archivo Excel con múltiples hojas:
- Para `XPSSpectrum`: hoja "Data" con datos + hoja "Metadata" opcional
- Para `XPSDataset`: una hoja por espectro + hojas "Dataset_Metadata" y "Spectra_Metadata"

**Parámetros:**
- `data` : `XPSSpectrum` o `XPSDataset`  
  Datos a exportar.
- `output_path` : `str` o `Path`  
  Ruta del archivo Excel de salida (debe terminar en .xlsx).
- `include_metadata` : `bool`, default `True`  
  Si True, incluye hojas con metadata.
- `decimal_places` : `int`, default `6`  
  Número de decimales para valores numéricos.

**Retorna:**
- `Path`  
  Ruta del archivo Excel creado.

**Lanza:**
- `TypeError` - Si data no es XPSSpectrum ni XPSDataset
- `ValueError` - Si output_path no termina en .xlsx

**Ejemplo:**
```python
from xps_analyzer.export import export_to_excel

# Exportar espectro individual
export_to_excel(spectrum, "output/c1s.xlsx", include_metadata=True)
# Hojas: "Data", "Metadata"

# Exportar dataset completo
export_to_excel(dataset, "output/muestra1.xlsx", include_metadata=True)
# Hojas: "C_1s", "O_1s", "N_1s", "Dataset_Metadata", "Spectra_Metadata"
```

**Estructura Excel - Dataset:**
- **Hoja "C_1s"**: Columnas `binding_energy`, `intensity`
- **Hoja "O_1s"**: Columnas `binding_energy`, `intensity`
- **Hoja "Dataset_Metadata"**: Columnas `key`, `value` (sample_name, date, instrument, etc.)
- **Hoja "Spectra_Metadata"**: Columnas `region`, `key`, `value`

**Notas:**
- Requiere librería `openpyxl` instalada (incluida en dependencias)
- Nombres de hoja limitados a 31 caracteres (restricción Excel)
- Caracteres especiales en nombres de región se reemplazan por "_"

---

### export_to_json

**Estado:** COMPLETADO - v0.8.0

```python
def export_to_json(
    data: XPSSpectrum | XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True,
    indent: int = 2
) -> Path
```

Exporta espectro o dataset XPS a archivo JSON con estructura jerárquica.

**Parámetros:**
- `data` : `XPSSpectrum` o `XPSDataset`  
  Datos a exportar.
- `output_path` : `str` o `Path`  
  Ruta del archivo JSON de salida.
- `include_metadata` : `bool`, default `True`  
  Si True, incluye metadata en el JSON.
- `indent` : `int`, default `2`  
  Nivel de indentación para formato legible. Use `None` para compacto.

**Retorna:**
- `Path`  
  Ruta del archivo JSON creado.

**Lanza:**
- `TypeError` - Si data no es XPSSpectrum ni XPSDataset

**Ejemplo:**
```python
from xps_analyzer.export import export_to_json

# Exportar con formato legible
export_to_json(dataset, "output/muestra1.json", indent=2)

# Exportar compacto (sin indentación)
export_to_json(dataset, "output/compact.json", indent=None)

# Exportar sin metadata
export_to_json(spectrum, "output/data_only.json", include_metadata=False)
```

**Estructura JSON - XPSSpectrum:**
```json
{
  "region_name": "C 1s",
  "binding_energy": [280.0, 280.2, 280.4, ...],
  "intensity": [145.23, 148.12, 150.45, ...],
  "metadata": {
    "sweeps": 10,
    "dwell_time": 0.1,
    "pass_energy": 20.0
  }
}
```

**Estructura JSON - XPSDataset:**
```json
{
  "filename": "muestra1_multiplex.txt",
  "header": {
    "sample_name": "Test Sample",
    "date": "2026-03-01",
    "instrument": "Thermo K-Alpha"
  },
  "spectra": {
    "C 1s": {
      "region_name": "C 1s",
      "binding_energy": [...],
      "intensity": [...],
      "metadata": {...}
    },
    "O 1s": {...}
  }
}
```

**Notas:**
- Arrays NumPy se convierten automáticamente a listas
- Valores `NaN` e `Inf` se convierten a `null`
- Usa `NumpyEncoder` personalizado para manejar tipos NumPy

---

### NumpyEncoder

**Estado:** COMPLETADO - v0.8.0

```python
class NumpyEncoder(json.JSONEncoder)
```

Encoder JSON personalizado para manejar tipos NumPy.

**Convierte:**
- `np.ndarray` → `list` (con NaN/Inf → null)
- `np.integer` → `int`
- `np.floating` → `float` (con NaN/Inf → null)
- `np.bool_` → `bool`

**Uso:**
```python
import json
import numpy as np
from xps_analyzer.export.exporters import NumpyEncoder

data = {
    "array": np.array([1.0, 2.0, np.nan, 4.0]),
    "float": np.float64(3.14),
    "int": np.int32(42)
}

with open("output.json", "w") as f:
    json.dump(data, f, cls=NumpyEncoder)

# Resultado:
# {"array": [1.0, 2.0, null, 4.0], "float": 3.14, "int": 42}
```

---

## CLI

### Namespace: `xps_analyzer.cli`

**Estado:** 40% completo

**Entry point:** `xps-analyzer` (instalado con paquete)

---

### Comando: analyze

```bash
xps-analyzer analyze <data_dir> [options]
```

Analiza archivos XPS en un directorio.

**Argumentos:**
- `data_dir` : Path al directorio con archivos XPS

**Opciones:**
- `--output-dir PATH` : Directorio de salida (default: `data/results/`)
- `--reference-element TEXT` : Elemento de referencia para calibración (default: `C`)
- `--format TEXT` : Formato de exportación: `csv`, `excel`, `json` (default: `csv`)

**Ejemplo:**
```bash
# Análisis básico
xps-analyzer analyze data/raw/samples/

# Con opciones
xps-analyzer analyze data/raw/samples/ \
    --output-dir results/muestra1/ \
    --reference-element Au \
    --format excel
```

---

### Comando: show-element

```bash
xps-analyzer show-element <symbol>
```

Muestra información de un elemento de la base de datos.

**Argumentos:**
- `symbol` : Símbolo químico (ej: `C`, `O`, `Au`)

**Ejemplo:**
```bash
# Ver información de carbono
xps-analyzer show-element C

# Output:
# Element: Carbon (C)
# Atomic Number: 6
# Photoelectron Lines:
#   1s: 284.8 eV (width: 1.0 eV)
# Common Compounds:
#   Graphite: 284.5 eV
#   C-O: 286.5 eV
#   C=O: 288.0 eV
#   O-C=O: 289.0 eV
```

---

### Comando: calibrate

**Estado:** PENDIENTE - Fase 1

```bash
xps-analyzer calibrate <file> --element <symbol> [options]
```

Calibra un archivo XPS.

**Ejemplo futuro:**
```bash
xps-analyzer calibrate data/raw/muestra1.txt --element C --output calibrated.txt
```

---

## Apéndices

### A. Convenciones de Energía

- **Binding Energy (BE):** Energía de enlace en eV (relativa al nivel de Fermi)
- **Kinetic Energy (KE):** Energía cinética del fotoelectrón = hν - BE - Φ
- **Rango típico:** 0-1486 eV (para fuente Al Kα)
- **Dirección de eje:** Alta energía a la izquierda (convención XPS)

### B. Elementos de Referencia Comunes

| Elemento | Línea | Energía (eV) | Uso |
|----------|-------|--------------|-----|
| C | 1s | 284.8 | Carbono adventicio (más común) |
| Au | 4f7/2 | 84.0 | Muestras conductoras |
| Cu | 2p3/2 | 932.7 | Muestras sobre cobre |
| Ag | 3d5/2 | 368.3 | Muestras sobre plata |

### C. Factores de Sensibilidad Típicos

| Elemento | Línea | Factor RSF |
|----------|-------|------------|
| C | 1s | 0.278 |
| O | 1s | 0.711 |
| N | 1s | 0.477 |
| Si | 2p | 0.328 |
| Ti | 2p | 2.001 |

*Nota: Valores para espectrómetro Kratos con fuente Al Kα*

---

## Referencias

### Documentos Relacionados
- `README.md` - Quick start guide
- `ARCHITECTURE.md` - Arquitectura técnica detallada
- `DEVELOPMENT.md` - Guía de desarrollo
- `TESTING.md` - Estrategia de testing

### Recursos Externos
- **NIST XPS Database** - https://srdata.nist.gov/xps/
- **CASA XPS** - http://www.casaxps.com/
- **ISO 14976** - Estándar VAMAS

---

**Última actualización:** Febrero 2026  
**Próxima revisión:** Después de completar Fase 1  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)

---

## ACTUALIZACIÓN FASE 1 - Módulo de Análisis Completo

### Namespace: `xps_analyzer.analysis`

**Estado:** COMPLETADO - v0.7.0-beta (75% Fase 1)

API completa implementada:
```python
from xps_analyzer.analysis import (
    # Sustracción de fondo
    shirley_background,
    tougaard_background,
    linear_background,
    # Ajuste de picos
    fit_gaussian,
    fit_lorentzian,
    fit_voigt,
    fit_multiple_peaks,
    estimate_peak_positions,
    # Cuantificación
    load_sensitivity_factors,
    calculate_atomic_concentration,
    normalize_to_100,
    quantify_dataset,
    # Dataclasses
    PeakParameters,
    FitResult
)
```

---

### shirley_background

**Estado:** COMPLETADO - v0.5.5-beta

```python
def shirley_background(
    spectrum: XPSSpectrum,
    tol: float = 1e-5,
    max_iter: int = 100,
    inplace: bool = False
) -> XPSSpectrum
```

Calcula y sustrae fondo Shirley (método iterativo estándar en XPS).

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a procesar
- `tol` : `float`, default `1e-5`  
  Tolerancia para convergencia
- `max_iter` : `int`, default `100`  
  Máximo de iteraciones
- `inplace` : `bool`, default `False`  
  Si `True`, modifica el espectro original

**Retorna:**
- `XPSSpectrum`  
  Espectro con fondo sustraído

**Ejemplo:**
```python
from xps_analyzer.analysis import shirley_background

# Crear copia sin fondo
c1s_nobg = shirley_background(c1s_spectrum, inplace=False)

# Ver metadata del proceso
print(c1s_nobg.metadata['background_method'])  # 'shirley'
print(c1s_nobg.metadata['background_iterations'])  # 12
```

**Referencia:** Shirley, D.A. (1972), Phys Rev B, 5(12), 4709-4714

---

### tougaard_background

**Estado:** COMPLETADO - v0.5.5-beta

```python
def tougaard_background(
    spectrum: XPSSpectrum,
    B: float = 2866.0,
    C: float = 1643.0,
    D: float = 1.0,
    inplace: bool = False
) -> XPSSpectrum
```

Calcula fondo Tougaard (modelo de dispersión inelástica).

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a procesar
- `B`, `C`, `D` : `float`  
  Parámetros del modelo. Defaults para materiales orgánicos.
  Para metales usar: B=1600, C=400
- `inplace` : `bool`, default `False`

**Retorna:**
- `XPSSpectrum`  
  Espectro con fondo sustraído

**Ejemplo:**
```python
from xps_analyzer.analysis import tougaard_background

# Materiales orgánicos (default)
organic_nobg = tougaard_background(spectrum)

# Metales
metal_nobg = tougaard_background(spectrum, B=1600, C=400)
```

**Referencia:** Tougaard, S. (1997), Surf Interface Anal, 25(3), 137-154

---

### fit_gaussian

**Estado:** COMPLETADO - v0.6.0-beta

```python
def fit_gaussian(
    spectrum: XPSSpectrum,
    position: float | None = None,
    amplitude: float | None = None,
    width: float | None = None,
    bounds: dict | None = None
) -> FitResult
```

Ajusta pico gaussiano: A * exp(-(x-x0)²/(2σ²))

**Parámetros:**
- `spectrum` : `XPSSpectrum`  
  Espectro a ajustar
- `position`, `amplitude`, `width` : `float | None`  
  Parámetros iniciales. Si `None`, estimación automática.
- `bounds` : `dict | None`  
  Bounds para optimización: `{'position': (min, max), ...}`

**Retorna:**
- `FitResult`  
  Resultado con picos ajustados, R², residuales

**Ejemplo:**
```python
from xps_analyzer.analysis import fit_gaussian

result = fit_gaussian(c1s_spectrum, position=284.8)
print(f"R² = {result.r_squared:.4f}")
print(f"Área = {result.peaks[0].area:.2f}")
```

---

### fit_voigt

**Estado:** COMPLETADO - v0.6.0-beta

```python
def fit_voigt(
    spectrum: XPSSpectrum,
    position: float | None = None,
    amplitude: float | None = None,
    sigma: float | None = None,
    gamma: float | None = None,
    bounds: dict | None = None
) -> FitResult
```

Ajusta perfil Voigt (convolución gaussiano-lorentziano). Más realista para XPS.

**Parámetros:**
- `sigma` : `float | None`  
  Ancho gaussiano (ensanchamiento instrumental)
- `gamma` : `float | None`  
  Ancho lorentziano (tiempo de vida del estado)

**Ejemplo:**
```python
from xps_analyzer.analysis import fit_voigt

result = fit_voigt(
    c1s_spectrum,
    position=284.8,
    sigma=0.6,  # Instrumental
    gamma=0.3   # Natural
)
```

**Referencia:** Thompson et al. (1987), J. Appl. Cryst. 20, 79-83

---

### fit_multiple_peaks

**Estado:** COMPLETADO - v0.6.0-beta

```python
def fit_multiple_peaks(
    spectrum: XPSSpectrum,
    n_peaks: int,
    peak_shape: Literal["gaussian", "lorentzian", "voigt"] = "voigt",
    initial_positions: list[float] | None = None
) -> FitResult
```

Ajusta múltiples picos simultáneamente.

**Parámetros:**
- `n_peaks` : `int`  
  Número de picos a ajustar
- `peak_shape` : `str`  
  Forma de pico para todos
- `initial_positions` : `list[float] | None`  
  Posiciones iniciales. Si `None`, usa estimación automática.

**Retorna:**
- `FitResult`  
  Resultado con lista de picos en `result.peaks`

**Ejemplo:**
```python
from xps_analyzer.analysis import fit_multiple_peaks

# C 1s con 3 componentes
result = fit_multiple_peaks(
    c1s_spectrum,
    n_peaks=3,
    peak_shape="voigt",
    initial_positions=[284.8, 286.2, 288.5]  # C-C, C-O, C=O
)

for i, peak in enumerate(result.peaks):
    print(f"Pico {i+1}: {peak.position:.2f} eV, Área: {peak.area:.2f}")
```

---

### PeakParameters

**Estado:** COMPLETADO - v0.6.0-beta

```python
@dataclass
class PeakParameters:
    position: float            # Binding energy (eV)
    amplitude: float           # Intensidad máxima
    width: float               # FWHM (eV)
    area: float                # Área integrada
    shape: Literal["gaussian", "lorentzian", "voigt"]
    gamma: float | None = None              # Para Voigt
    position_error: float | None = None     # Error estándar
    amplitude_error: float | None = None
    width_error: float | None = None
```

Parámetros de un pico ajustado individual.

---

### FitResult

**Estado:** COMPLETADO - v0.6.0-beta

```python
@dataclass
class FitResult:
    peaks: list[PeakParameters]  # Lista de picos ajustados
    fitted_spectrum: np.ndarray  # Espectro ajustado completo
    residual: np.ndarray         # Datos - ajuste
    r_squared: float             # Bondad de ajuste
    chi_squared: float           # Chi-cuadrado reducido
    success: bool                # Si convergió
    message: str                 # Mensaje descriptivo
```

Resultado completo de ajuste de pico(s).

---

### load_sensitivity_factors

**Estado:** COMPLETADO - v0.7.0-beta

```python
def load_sensitivity_factors(
    source: Literal["scofield", "wagner"] = "scofield",
    xray_source: Literal["al_ka", "mg_ka"] = "al_ka"
) -> dict[str, float]
```

Carga factores de sensibilidad relativa (RSF) para cuantificación XPS.

**Parámetros:**
- `source` : `"scofield"` o `"wagner"`  
  Fuente de factores. Scofield (teórico), Wagner (empírico).
- `xray_source` : `"al_ka"` o `"mg_ka"`  
  Fuente de rayos X del instrumento

**Retorna:**
- `dict[str, float]`  
  Factores RSF por línea: `{"C 1s": 0.296, "O 1s": 0.711, ...}`

**Ejemplo:**
```python
from xps_analyzer.analysis import load_sensitivity_factors

# Scofield para Al Kα (más común)
rsf = load_sensitivity_factors()

# Wagner empírico
rsf_wagner = load_sensitivity_factors(source="wagner")

# Mg Kα
rsf_mg = load_sensitivity_factors(xray_source="mg_ka")
```

**Elementos soportados:** C, N, O, F, Na, Mg, Al, Si, P, S, Cl, K, Ca, Ti, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ag, Au (23 elementos)

**Referencias:**
- Scofield, J.H. (1976) LLNL Report UCRL-51326
- Wagner, C.D. et al. (1981) Surf. Interface Anal. 3(5), 211-225

---

### calculate_atomic_concentration

**Estado:** COMPLETADO - v0.7.0-beta

```python
def calculate_atomic_concentration(
    peaks: list[PeakParameters],
    sensitivity_factors: dict[str, float],
    element_names: list[str],
    normalize: bool = True
) -> dict[str, float]
```

Calcula concentraciones atómicas usando fórmula estándar XPS:  
**C_i = (A_i / S_i) / Σ(A_j / S_j) × 100%**

**Parámetros:**
- `peaks` : `list[PeakParameters]`  
  Picos ajustados con áreas
- `sensitivity_factors` : `dict[str, float]`  
  Factores RSF (de `load_sensitivity_factors()`)
- `element_names` : `list[str]`  
  Nombres de elementos: `["C 1s", "O 1s", ...]`
- `normalize` : `bool`, default `True`  
  Normalizar a 100%

**Retorna:**
- `dict[str, float]`  
  Concentraciones atómicas en %: `{"C 1s": 75.02, "O 1s": 24.98}`

**Lanza:**
- `ValueError` - Si áreas negativas, RSF faltantes, o longitudes no coinciden

**Ejemplo completo:**
```python
from xps_analyzer.analysis import (
    shirley_background,
    fit_gaussian,
    load_sensitivity_factors,
    calculate_atomic_concentration
)

# 1. Sustracción de fondo
c1s_nobg = shirley_background(c1s_spectrum, inplace=False)
o1s_nobg = shirley_background(o1s_spectrum, inplace=False)

# 2. Ajuste de picos
c_fit = fit_gaussian(c1s_nobg, position=284.8)
o_fit = fit_gaussian(o1s_nobg, position=531.0)

# 3. Cargar RSF
rsf = load_sensitivity_factors()

# 4. Cuantificar
concentrations = calculate_atomic_concentration(
    peaks=[c_fit.peaks[0], o_fit.peaks[0]],
    sensitivity_factors=rsf,
    element_names=["C 1s", "O 1s"]
)

print(concentrations)
# {'C 1s': 75.02, 'O 1s': 24.98}
```

---

### normalize_to_100

**Estado:** COMPLETADO - v0.7.0-beta

```python
def normalize_to_100(
    concentrations: dict[str, float]
) -> dict[str, float]
```

Normaliza concentraciones para suma exacta 100%.

**Parámetros:**
- `concentrations` : `dict[str, float]`  
  Concentraciones que pueden no sumar 100%

**Retorna:**
- `dict[str, float]`  
  Concentraciones normalizadas

**Ejemplo:**
```python
conc = {"C 1s": 65.1, "O 1s": 34.2}  # Suma = 99.3%
normalized = normalize_to_100(conc)
# {'C 1s': 65.57, 'O 1s': 34.43}  # Suma = 100.0%
```

