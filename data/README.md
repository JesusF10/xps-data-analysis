# Directorio de Datos - XPS Analyzer

Este directorio contiene todos los datos relacionados con el proyecto XPS Analyzer, organizados en subdirectorios según su propósito.

---

## Estructura de Directorios

```
data/
├── raw/                    # Datos originales (NUNCA modificar)
│   └── samples/            # Archivos XPS de muestras
├── processed/              # Datos procesados
│   ├── calibrated/         # Datos calibrados
│   └── normalized/         # Datos normalizados
├── test_data/              # Datos para testing
│   ├── valid/              # Archivos válidos para tests
│   └── invalid/            # Archivos inválidos para tests de error
├── results/                # Resultados de análisis
│   ├── reports/            # Reportes JSON/texto
│   ├── plots/              # Gráficas generadas
│   └── exports/            # Datos exportados (CSV, Excel)
└── README.md               # Este archivo
```

---

## Descripción de Subdirectorios

### `raw/` - Datos Originales

**Propósito:** Almacenar datos XPS sin procesar tal como salen del instrumento.

**Reglas:**
- **NUNCA modificar** archivos en este directorio
- Solo lectura para análisis
- Mantener backup externo
- Usar nombres descriptivos: `muestra001_fecha_YYYYMMDD.txt`

**Formatos soportados (Fase 0):**
- Archivos de texto propietarios (`.txt`)
- Formato multiplex (múltiples regiones)
- Formato survey (espectro completo)

**Formatos planeados (Fase 2):**
- VAMAS (`.vms`) - ISO 14976
- CASA XPS (`.casa`)
- HDF5 (`.h5`)

**Ejemplo de estructura:**
```
raw/
└── samples/
    ├── proyecto_A/
    │   ├── muestra001_20240115.txt
    │   ├── muestra002_20240115.txt
    │   └── metadata.json
    └── proyecto_B/
        └── muestra010_20240201.txt
```

### `processed/` - Datos Procesados

**Propósito:** Almacenar datos después de procesamiento (calibración, normalización, etc.).

**Subdirectorios:**
- `calibrated/`: Datos calibrados con elementos de referencia
- `normalized/`: Datos normalizados por intensidad
- `smoothed/`: Datos suavizados (Fase 1)
- `background_subtracted/`: Con fondo sustraído (Fase 1)

**Formato:** Pickle (`.pkl`) para preservar objetos Python completos

**Ejemplo:**
```python
# Guardar datos calibrados
import pickle
with open("data/processed/calibrated/muestra001_calibrated.pkl", 'wb') as f:
    pickle.dump(calibrated_dataset, f)

# Cargar después
with open("data/processed/calibrated/muestra001_calibrated.pkl", 'rb') as f:
    dataset = pickle.load(f)
```

### `test_data/` - Datos para Testing

**Propósito:** Archivos pequeños para ejecutar tests unitarios y de integración.

**Subdirectorios:**
- `valid/`: Archivos bien formados para tests positivos
- `invalid/`: Archivos malformados para tests de manejo de errores

**Características:**
- Archivos pequeños (<1 MB)
- Datos sintéticos o reducidos
- Formatos variados para testing

**NO usar datos reales de investigación aquí** (por tamaño y privacidad).

### `results/` - Resultados de Análisis

**Propósito:** Almacenar outputs de análisis y visualizaciones.

**Subdirectorios:**

#### `reports/`
Reportes de análisis en JSON o texto:
```json
{
  "filename": "muestra001.txt",
  "timestamp": "2024-01-15T10:30:00",
  "elements": {
    "C": {"confidence": 0.95, "peak_energy": 284.8},
    "O": {"confidence": 0.87, "peak_energy": 531.2}
  },
  "calibration": {
    "reference_element": "C",
    "shift_applied": -0.8
  }
}
```

#### `plots/`
Gráficas en formato PNG/PDF:
- `muestra001_survey.png`
- `muestra001_C1s_fitted.pdf`
- `comparison_all_samples.png`

#### `exports/`
Datos exportados para otros software:
- CSV: Para Excel, Origin
- JSON: Para análisis con otros lenguajes
- HDF5: Para grandes volúmenes (Fase 2)

---

## Convenciones de Nombres de Archivo

### Datos Raw

```
{proyecto}_{muestra}{numero}_{fecha}.txt

Ejemplos:
- polimeros_muestra001_20240115.txt
- metales_sample_A1_20240201.txt
- catalizador_Cu_post_20240315.txt
```

### Datos Procesados

```
{nombre_original}_{procesamiento}.{ext}

Ejemplos:
- muestra001_20240115_calibrated.pkl
- sample_A1_normalized.pkl
- muestra002_fitted.pkl
```

### Resultados

```
{nombre_muestra}_{tipo_resultado}_{timestamp}.{ext}

Ejemplos:
- muestra001_identification_20240115_1030.json
- sample_A1_survey_plot.png
- batch_analysis_20240115.csv
```

---

## Gestión de Datos

### Tamaño y Limpieza

```bash
# Ver tamaño de cada directorio
du -sh data/*/

# Limpiar resultados antiguos (>30 días)
find data/results/ -type f -mtime +30 -delete

# Comprimir datos procesados antiguos
tar -czf archive_$(date +%Y%m).tar.gz data/processed/
```

### Backup

**Recomendación:**
- Backup de `raw/` diariamente
- Backup de `processed/` semanalmente
- `results/` puede regenerarse (opcional)

```bash
# Ejemplo de backup con rsync
rsync -av --progress data/raw/ /backup/xps-data/raw/
```

### .gitignore

Los siguientes archivos/directorios están ignorados por git:

```gitignore
# Datos grandes
data/raw/**/*.txt
data/processed/**/*.pkl
data/results/plots/**/*.png
data/results/plots/**/*.pdf

# Excepciones (archivos pequeños de ejemplo)
!data/test_data/**/*
```

---

## Metadata

### metadata.json (Recomendado)

Incluir archivo `metadata.json` en cada subdirectorio de proyecto:

```json
{
  "project_name": "Análisis de Polímeros",
  "pi": "Dr. Juan Pérez",
  "date_start": "2024-01-15",
  "instrument": "PHI 5000 VersaProbe",
  "x_ray_source": "Al Kα",
  "samples": [
    {
      "sample_id": "muestra001",
      "description": "Polímero tratado con plasma",
      "treatment": "O2 plasma 5 min",
      "files": ["muestra001_20240115.txt"]
    }
  ],
  "notes": "Serie de experimentos sobre funcionalización de superficies"
}
```

---

## Uso Típico

### 1. Importar Datos Raw

```python
from xps_analyzer import load_single_file, load_all_data

# Archivo individual
dataset = load_single_file("data/raw/samples/muestra001.txt")

# Directorio completo
datasets = load_all_data("data/raw/samples/proyecto_A/")
```

### 2. Procesar y Guardar

```python
from xps_analyzer.preprocessing import calibrate_sample
import pickle

# Calibrar
calibrated = calibrate_sample(dataset, carbon_ref, inplace=False)

# Guardar procesado
output_path = "data/processed/calibrated/muestra001_calibrated.pkl"
with open(output_path, 'wb') as f:
    pickle.dump(calibrated, f)
```

### 3. Exportar Resultados

```python
# Guardar reporte
import json
report = {
    "filename": dataset.filename,
    "elements": identified_elements,
    # ... más datos
}

with open("data/results/reports/muestra001_report.json", 'w') as f:
    json.dump(report, f, indent=2)

# Guardar gráfica
from xps_analyzer.visualization import plot_spectrum
plot_spectrum(spectrum)
plt.savefig("data/results/plots/muestra001_C1s.png", dpi=300)
```

---

## Solución de Problemas

### "FileNotFoundError"

```python
from pathlib import Path

# Verificar que el directorio existe
data_dir = Path("data/raw/samples")
if not data_dir.exists():
    data_dir.mkdir(parents=True)
```

### "PermissionError"

```bash
# Verificar permisos
ls -la data/raw/samples/

# Corregir permisos si es necesario
chmod -R u+rw data/raw/samples/
```

### Archivos Muy Grandes

```python
# Para archivos >100 MB, considerar compresión
import gzip
import pickle

# Guardar comprimido
with gzip.open("data/processed/muestra001.pkl.gz", 'wb') as f:
    pickle.dump(dataset, f)

# Cargar comprimido
with gzip.open("data/processed/muestra001.pkl.gz", 'rb') as f:
    dataset = pickle.load(f)
```

---

## Seguridad y Privacidad

- **NO commitear datos raw** a git (están en .gitignore)
- **NO incluir datos sensibles** en repositorio público
- **Anonimizar muestras** si es necesario antes de compartir
- **Seguir políticas** de tu institución sobre gestión de datos

---

**Última actualización:** Marzo 2026  
**Versión:** 0.5.0-alpha
