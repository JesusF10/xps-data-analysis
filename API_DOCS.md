# XPS Analyzer - Referencia de API

**Versión:** 0.1.0  
**Estado:** Fase 0 (35% completado)  
**Última actualización:** Febrero 2026

Esta es la referencia completa de la API pública de XPS Analyzer. Incluye todas las funciones, clases y métodos disponibles para usuarios finales.

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

**Estado:** MÓDULO VACÍO - Fase 1

**API planeada:**
```python
from xps_analyzer.export import export_csv, export_excel, export_hdf5
```

---

### export_csv

**Estado:** PENDIENTE - Fase 1

```python
def export_csv(
    dataset: XPSDataset,
    output_dir: str | Path,
    separate_files: bool = True
) -> None
```

Exporta dataset a archivo(s) CSV.

**Ejemplo futuro:**
```python
from xps_analyzer.export import export_csv

# Archivo separado por región
export_csv(dataset, output_dir="data/results/exports/", separate_files=True)
# Genera: C_1s.csv, O_1s.csv, N_1s.csv, ...

# Todo en un archivo
export_csv(dataset, output_dir="data/results/", separate_files=False)
# Genera: muestra1.csv con todas las regiones
```

---

### export_excel

**Estado:** PENDIENTE - Fase 1

```python
def export_excel(
    dataset: XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True
) -> None
```

Exporta dataset a Excel con múltiples hojas.

**Ejemplo futuro:**
```python
from xps_analyzer.export import export_excel

export_excel(
    dataset=dataset,
    output_path="data/results/muestra1.xlsx",
    include_metadata=True
)
# Genera Excel con hojas: Metadata, C 1s, O 1s, N 1s, ...
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
