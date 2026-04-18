# Tutorial 1: Uso Básico de XPS Analyzer

**Nivel:** Principiante  
**Tiempo estimado:** 10-15 minutos  
**Requisitos:** Instalación completa de XPS Analyzer

---

## Objetivos

Al completar este tutorial aprenderás a:

1. Cargar archivos XPS individuales
2. Explorar la estructura de datos
3. Visualizar espectros básicos
4. Usar la interfaz de línea de comandos (CLI)

---

## 1. Cargar un Archivo XPS

### Usando Python

```python
from xps_analyzer import load_single_file

# Cargar un archivo XPS
dataset = load_single_file("data/raw/samples/muestra1.txt")

# Explorar la estructura
print(f"Archivo: {dataset.filename}")
print(f"Espectros disponibles: {list(dataset.spectra.keys())}")
print(f"Metadata: {dataset.header}")
```

**Salida esperada:**
```
Archivo: muestra1.txt
Espectros disponibles: ['survey', 'C 1s', 'O 1s', 'N 1s']
Metadata: {'sample_name': 'Muestra 1', 'date': '2024-01-15', ...}
```

### Estructura de Datos

XPS Analyzer usa una jerarquía de tres niveles:

```
XPSDataset (archivo completo)
├── filename: str
├── header: dict (metadata del archivo)
└── spectra: dict[str, XPSSpectrum]
    └── XPSSpectrum (espectro individual)
        ├── region_name: str (ej: "C 1s")
        ├── binding_energy: np.ndarray (eV)
        ├── intensity: np.ndarray (cuentas)
        └── metadata: dict
```

---

## 2. Acceder a Espectros Individuales

```python
# Obtener un espectro específico
c1s_spectrum = dataset.spectra["C 1s"]

# Examinar datos del espectro
print(f"Región: {c1s_spectrum.region_name}")
print(f"Puntos de datos: {len(c1s_spectrum.binding_energy)}")
print(f"Rango de energía: {c1s_spectrum.binding_energy.min():.1f} - {c1s_spectrum.binding_energy.max():.1f} eV")
print(f"Intensidad máxima: {c1s_spectrum.intensity.max():.0f} cuentas")
```

**Salida esperada:**
```
Región: C 1s
Puntos de datos: 801
Rango de energía: 280.0 - 292.0 eV
Intensidad máxima: 15234 cuentas
```

---

## 3. Visualizar Espectros

### Espectro Individual

```python
from xps_analyzer.visualization import plot_spectrum

# Plotear el espectro C 1s
plot_spectrum(c1s_spectrum, title="Carbono 1s")
```

**Nota:** El eje X se invierte automáticamente (convención XPS: alta energía a la izquierda).

### Espectro Survey

```python
from xps_analyzer.visualization import plot_survey_spectrum

# Obtener y plotear survey
survey = dataset.spectra["survey"]
plot_survey_spectrum(survey, title="Survey Completo - Muestra 1")
```

---

## 4. Cargar Múltiples Archivos

```python
from xps_analyzer.data_loader import load_all_data

# Cargar todos los archivos de un directorio
datasets = load_all_data("data/raw/samples/", recursive=True)

print(f"Total de archivos cargados: {len(datasets)}")

# Iterar sobre todos los datasets
for filename, dataset in datasets.items():
    print(f"\n{filename}:")
    print(f"  Espectros: {list(dataset.spectra.keys())}")
```

**Salida esperada:**
```
Total de archivos cargados: 5

muestra1.txt:
  Espectros: ['survey', 'C 1s', 'O 1s']

muestra2.txt:
  Espectros: ['survey', 'C 1s', 'O 1s', 'N 1s']
...
```

---

## 5. Usar la CLI

### Ver Información de Elementos

```bash
# Mostrar información del elemento carbono
xps-analyzer show-element C
```

**Salida:**
```
Información para el elemento: C
Símbolo: C
Nombre: Carbon
Número atómico: 6
Energías de enlace disponibles:
- PhotoelectronLine(line='1s', binding_energy=284.8, type='core')
Compuestos de referencia:
- Carbonato: Posición pico = (288.0, 290.0) eV Orbital = 1s
```

### Ver Información Detallada

```bash
# Con flag verbose
xps-analyzer show-element O -v
```

### Analizar un Archivo

```bash
# Analizar un archivo específico
xps-analyzer analyze data/raw/samples/muestra1.txt
```

**Salida:**
```
Analizando conjunto: muestra1.txt
Archivo cargado exitosamente
Metadatos: {'sample_name': 'Muestra 1', 'date': '2024-01-15'}
Espectros encontrados: ['survey', 'C 1s', 'O 1s', 'N 1s']
Análisis completado para muestra1.txt
```

---

## 6. Detección Automática de Formatos

XPS Analyzer detecta automáticamente varios formatos de archivo:

```python
from xps_analyzer.data_loader import detect_file_format

# Detectar formato
formato = detect_file_format("data/raw/samples/muestra1.txt")
print(f"Formato detectado: {formato}")
```

**Formatos soportados (Fase 0):**
- `multiplex`: Formato multi-región propietario
- `survey`: Formato survey simple
- `text`: Formato de texto genérico

**Formatos planeados (Fase 2):**


---

## 7. Trabajar con Datos NumPy

Los datos de espectros son arrays de NumPy, permitiendo análisis avanzado:

```python
import numpy as np

# Obtener espectro
spectrum = dataset.spectra["C 1s"]

# Operaciones con NumPy
energy = spectrum.binding_energy
intensity = spectrum.intensity

# Encontrar el pico máximo
max_index = np.argmax(intensity)
peak_energy = energy[max_index]
peak_intensity = intensity[max_index]

print(f"Pico máximo en {peak_energy:.2f} eV con intensidad {peak_intensity:.0f}")

# Calcular estadísticas
mean_intensity = np.mean(intensity)
std_intensity = np.std(intensity)

print(f"Intensidad promedio: {mean_intensity:.0f} ± {std_intensity:.0f}")
```

---

## 8. Acceder a Base de Datos de Referencia

```python
from xps_analyzer import load_reference_database

# Cargar base de datos
db = load_reference_database()

# Obtener información de elemento
carbon = db.elements["C"]
print(f"Energía de referencia para C 1s: {carbon.binding_energy_most_useful} eV")

# Buscar elementos por energía de enlace
candidates = db.search_by_binding_energy(284.5, tolerance=2.0)
print(f"Posibles elementos: {[c.symbol for c in candidates]}")
```

---

## Resumen

En este tutorial aprendiste a:

- Cargar archivos XPS con `load_single_file()`
- Explorar la estructura `XPSDataset` y `XPSSpectrum`
- Visualizar espectros con `plot_spectrum()` y `plot_survey_spectrum()`
- Cargar múltiples archivos con `load_all_data()`
- Usar la CLI con `xps-analyzer`
- Detectar formatos automáticamente
- Trabajar con datos NumPy
- Acceder a la base de datos de referencia

---

## Próximos Pasos

- **Tutorial 2:** [Calibración de Espectros](02_calibration.md)
- **Tutorial 3:** [Identificación de Elementos](03_element_identification.md)

---

## Solución de Problemas

### Error: "Archivo no encontrado"

```python
# Verificar que el path es correcto
from pathlib import Path
filepath = Path("data/raw/samples/muestra1.txt")
print(f"Existe: {filepath.exists()}")
```

### Error: "Formato no reconocido"

```python
# Verificar formato del archivo
formato = detect_file_format(filepath)
if formato is None:
    print("Formato no soportado en esta versión")
```

### Error: "Espectro no encontrado"

```python
# Listar espectros disponibles
print(f"Espectros disponibles: {list(dataset.spectra.keys())}")

# Usar get() para evitar KeyError
spectrum = dataset.spectra.get("C 1s")
if spectrum is None:
    print("Espectro C 1s no está en este dataset")
```

---

**Versión:** 0.5.0-alpha  
**Última actualización:** Marzo 2026
