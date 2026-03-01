# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Sin Publicar]

### Agregado
- Validación manual en `__post_init__` para `XPSSpectrum`, `XPSDataset`, `XPSSample`
- Directorio `config/` con archivos TOML de configuración
- Documentación completa del proyecto (10 archivos markdown principales)
- Manejo robusto de errores en `parse_metadata()` y `get_spectrum_data()`

### Cambiado
- `get_spectrum_data()` ahora valida datos antes de crear objeto
- `parse_metadata()` envuelve parsing en try-except con mensajes claros

### Corregido
- Test `test_get_spectrum_data_malformed_line_raises` ahora pasa correctamente

---

## [0.1.0] - 2025-12-25

Lanzamiento inicial alpha del proyecto XPS Analyzer.

### Agregado

**Carga de Datos**
- Estructuras de datos: `XPSSpectrum`, `XPSDataset`, `XPSSample`
- Parser básico para formato propietario de texto
- Detección de formato multiplex vs. survey
- Función `load_single_file()` para carga individual

**Datos de Referencia**
- Base de datos JSON de ~25 elementos comunes (C, O, N, Si, Al, Fe, Ti, Cu, Au, etc.)
- Sistema de carga con patrón singleton/cache
- Búsqueda por energía de enlace con tolerancia ajustable
- Clases `ElementReference`, `PhotoelectronLine`, `CompoundReference`

**Preprocesamiento**
- Calibración de energía por elemento de referencia
- Función `calibrate_spectrum()` con parámetro `inplace`
- Elemento de referencia por defecto: C 1s @ 284.8 eV

**Visualización**
- Plotting básico de espectros survey y regiones
- Convenciones XPS (eje x invertido)
- Funciones `plot_survey()` y `plot_region()`

**CLI**
- Comando `xps-analyzer analyze <data_dir>`
- Comando `xps-analyzer show-element <symbol>`
- Framework Click con validación de paths

**Configuración**
- `pyproject.toml` con todas las dependencias y configuración de herramientas
- `environment.yml` para ambientes conda
- Configuración de ruff (linter + formatter)
- Configuración de pytest

### Conocidos Issues

**Bugs Críticos**
- `calibration.py:56-58`: IndexError cuando elemento de referencia no encontrado (#42)
- `elements.py:170-171`: Acceso incorrecto a `photoelectron_lines.values()`
- `identification.py:117`: Acceso a `.peak_position` en tipo string

**Funcionalidad Faltante**
- Sustracción de fondo (Shirley, Tougaard) - Bloqueador para Fase 1
- Ajuste de picos - Bloqueador para Fase 1
- Cuantificación - Bloqueador para Fase 1
- Exportación de resultados (CSV, Excel, JSON)
- Soporte para múltiples formatos (VAMAS, CASA XPS, HDF5)
- Sistema de configuración (leer TOML)

**Implementaciones Stub**
- `load_all_data()` retorna `None`
- `detect_file_format()` retorna `None`
- `find_peaks_basic()` es `pass`

**Testing**
- Cobertura < 20% (CRÍTICO)
- Solo 4 tests en `test_data_loader.py`
- Ningún test para: preprocessing, visualization, CLI, reference_data

---

## [0.3.0] - Fase 2 (Pendiente)

**BREAKING CHANGES:** Migración a Pydantic

### Changed

**Migración a Pydantic**
- `XPSSpectrum`, `XPSDataset`, `XPSSample` ahora heredan de `pydantic.BaseModel`
- Validación automática de todos los campos
- Mejores mensajes de error en español

**API Changes**
- `spectrum.model_dump()` en lugar de `dataclasses.asdict()`
- `pydantic.ValidationError` en lugar de `ValueError` genérico
- Campos tienen validadores con `@field_validator`

### Agregado

**Formatos Adicionales**
- Soporte para VAMAS ISO 14976
- Soporte para CASA XPS
- Soporte para HDF5
- Detección automática de formato implementada

**Validación Robusta**
- Validación automática de tipos
- Coerción de tipos cuando sea posible
- JSON schema generation para documentación

### Guía de Migración

**Antes (v0.1.0):**
```python
from dataclasses import asdict
spectrum = XPSSpectrum(...)
data = asdict(spectrum)
```

**Después (v0.3.0):**
```python
spectrum = XPSSpectrum(...)
data = spectrum.model_dump()
```

**Manejo de Errores:**
```python
# Antes
try:
    spectrum = XPSSpectrum(...)
except ValueError as e:
    print(f"Error: {e}")

# Después
from pydantic import ValidationError
try:
    spectrum = XPSSpectrum(...)
except ValidationError as e:
    print(f"Errores de validación: {e.json()}")
```

---

## [0.5.0] - Fase 1 Completa (Pendiente)

### Agregado

**Sustracción de Fondo**
- Método Shirley (iterativo)
- Método Tougaard
- Método Linear
- Método Polynomial

**Ajuste de Picos**
- Formas: Gaussian, Lorentzian, Voigt, Pseudo-Voigt
- Deconvolución de múltiples picos
- Soporte para doublets (spin-orbit coupling)
- Estimación automática de parámetros iniciales
- Constraints configurables

**Cuantificación**
- Cálculo de concentraciones atómicas
- Factores de sensibilidad de Scofield
- Factores específicos de instrumento
- Corrección por ángulo de emisión

**Exportación**
- Exportar a CSV
- Exportar a Excel (múltiples hojas)
- Exportar a JSON
- Exportar a texto plano

**Sistema de Configuración**
- Cargar configuración desde `config/*.toml`
- Override con variables de entorno
- Override con argumentos CLI

**Testing**
- Cobertura >= 60%
- Tests para todos los módulos core

---

## [1.0.0] - Fase 3 Completa (Pendiente)

### Agregado

**Machine Learning**
- Clasificación automática de elementos
- Predicción de estados de oxidación
- Detección de contaminación

**Análisis Avanzado**
- Depth profiling
- Análisis de multicapas

**GUI**
- Interfaz gráfica con Streamlit/Dash
- Carga drag-and-drop
- Visualización interactiva

**API REST**
- API con FastAPI
- Endpoints documentados con OpenAPI
- Autenticación

**Calidad**
- Cobertura de tests >= 90%
- Property-based testing con hypothesis
- Documentación completa de API

---

## Tipos de Cambios

- `Added` - Nueva funcionalidad
- `Changed` - Cambios en funcionalidad existente
- `Deprecated` - Funcionalidad que será eliminada
- `Removed` - Funcionalidad eliminada
- `Fixed` - Bugs corregidos
- `Security` - Vulnerabilidades corregidas

---

## Política de Versioning

- **MAJOR** (1.x.x): Cambios incompatibles en API
- **MINOR** (x.1.x): Nueva funcionalidad compatible hacia atrás
- **PATCH** (x.x.1): Correcciones de bugs

**Versiones Pre-1.0:**
- API puede cambiar sin aviso
- No garantía de compatibilidad hacia atrás
- Usar en producción bajo tu propio riesgo

---

**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)  
**Última actualización:** Febrero 2026
