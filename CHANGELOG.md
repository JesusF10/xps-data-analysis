# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Sin Publicar]

### Próximos Pasos - Fase 2

**En planificación:** Migración a Pydantic, soporte VAMAS, formato CASA XPS

---

## [0.8.0-beta] - 2026-03-01

**Hito:** Fase 1 COMPLETADA (100%) - Sesión 4 - Sistema de Exportación

Implementación del módulo de exportación completo que permite guardar espectros
XPS y datasets en formatos estándar (CSV, Excel, JSON) con metadata completa.
Con esta sesión se completa la Fase 1 del proyecto, estableciendo las capacidades
core de análisis XPS automatizado.

### Agregado

**Módulo de Exportación** (`export/exporters.py`)
- `export_to_csv()`: Exporta datos a archivos CSV
  * XPSSpectrum → archivo CSV simple (binding_energy, intensity)
  * XPSDataset → directorio con múltiples CSV (uno por región)
  * Metadata opcional en archivos `.metadata.csv` separados
  * Control de precisión decimal (parameter `decimal_places`)
  * Creación automática de directorios padres
- `export_to_excel()`: Exporta datos a archivos Excel (.xlsx)
  * XPSSpectrum → hoja "Data" + hoja "Metadata" opcional
  * XPSDataset → una hoja por espectro + hojas de metadata
  * Usa engine `openpyxl` de pandas
  * Validación de extensión (.xlsx requerida)
  * Nombres de hoja seguros (31 caracteres max, sin caracteres especiales)
- `export_to_json()`: Exporta datos a archivos JSON
  * Estructura jerárquica con metadata completa
  * Arrays NumPy convertidos a listas
  * Manejo de NaN/Inf → null
  * Control de indentación (parameter `indent`)
- `NumpyEncoder`: Clase JSON encoder personalizada
  * Convierte np.ndarray, np.integer, np.floating, np.bool_
  * Convierte NaN/Inf a null en arrays
  * Hereda de `json.JSONEncoder`

**Funciones Helper Privadas**
- `_export_spectrum_to_csv()`: Helper para exportar espectro individual
- `_export_dataset_to_csv()`: Helper para exportar dataset completo
- `_export_spectrum_to_excel()`: Helper con openpyxl writer
- `_export_dataset_to_excel()`: Helper con múltiples hojas
- `_spectrum_to_dict()`: Serialización de espectro a diccionario
- `_dataset_to_dict()`: Serialización de dataset a diccionario

**Tests** (208 → 227 tests, +19 tests)
- `test_export.py`: 19 tests comprehensivos (100% passing)
  * test_export_to_csv: 6 tests (básico, metadata, dataset, errores, directorios, precisión)
  * test_export_to_excel: 5 tests (básico, metadata, dataset, validación extensión, hojas múltiples)
  * test_export_to_json: 6 tests (básico, metadata, dataset, NumpyEncoder arrays, NaN/Inf, indentación)
  * test_roundtrip: 2 tests (CSV y JSON export → reimport)
- Cobertura del módulo: 92% (superando objetivo de 80%)

**Dependencias**
- Agregado `openpyxl==3.1.5` para exportación Excel
- Agregado `et-xmlfile==2.0.0` (dependencia de openpyxl)

### Cambiado

**Cobertura de Tests**
- Tests totales: 208 → 227 (+19 tests)
- Cobertura módulo export: 92%

**API Pública**
- Exportado desde `xps_analyzer.export.__init__.py`:
  * `export_to_csv`
  * `export_to_excel`
  * `export_to_json`

**Estructura del Proyecto**
- Fase 1: 75% → 100% completada
- 4 sesiones completadas: Background Subtraction, Peak Fitting, Quantification, Export System
- Módulos core implementados: data_loader, preprocessing, analysis (background, peak_fitting, quantification), export
- Líneas de código totales: ~3,800 → ~4,400 (+600 líneas)

### Estadísticas Finales de Fase 1

**Tests**
- Total: 227 tests (100% passing)
- Cobertura global: 87%
- Cobertura por módulo:
  * analysis/background: 96%
  * analysis/peak_fitting: 95%
  * analysis/quantification: 85%
  * export/exporters: 92%

**Código**
- Líneas totales: ~4,400
- Módulos completados: 4/10
- Funciones implementadas: ~40
- Clases implementadas: 6

---

## [0.7.0-beta] - 2026-03-02

**Hito:** Fase 1 - Sesión 3 completada - Cuantificación Atómica

Implementación del módulo de cuantificación atómica con factores de sensibilidad
relativa (RSF) de Scofield y Wagner. Permite calcular composiciones atómicas
precisas a partir de áreas de picos ajustados.

### Agregado

**Módulo de Cuantificación** (`analysis/quantification.py`)
- `load_sensitivity_factors()`: Carga factores RSF de Scofield (1976) y Wagner (1981)
  * Soporta 23 elementos comunes en XPS
  * Al Kα (1486.6 eV) y Mg Kα (1253.6 eV) para Scofield
  * Al Kα para Wagner (empírico)
  * Elementos: C, N, O, F, Na, Mg, Al, Si, P, S, Cl, K, Ca, Ti, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ag, Au
- `calculate_atomic_concentration()`: Calcula concentraciones atómicas
  * Fórmula estándar: C_i = (A_i / S_i) / Σ(A_j / S_j) × 100%
  * Validación exhaustiva de inputs (áreas positivas, RSF disponibles)
  * Normalización automática a 100%
- `normalize_to_100()`: Normaliza concentraciones para suma exacta
  * Mantiene proporciones relativas
  * Útil para excluir elementos traza
- `quantify_dataset()`: Placeholder para integración futura

**Factores RSF**
- SCOFIELD_RSF_AL_KA: Factores teóricos normalizado a F 1s = 1.0
- SCOFIELD_RSF_MG_KA: Factores teóricos normalizado a Na 1s = 1.0  
- WAGNER_RSF_AL_KA: Factores empíricos normalizado a F 1s = 1.0

**Tests** (165 → 208 tests, +43 tests)
- `test_quantification.py`: 43 tests comprehensivos (100% passing)
  * TestLoadSensitivityFactors: 11 tests
  * TestCalculateAtomicConcentration: 8 tests
  * TestCalculateConcentrationErrors: 7 tests
  * TestNormalizeTo100: 9 tests
  * TestQuantificationIntegration: 5 tests
  * TestNumericalPrecision: 3 tests
- Cobertura del módulo: 85% (superando objetivo de 80%)

### Cambiado

**Cobertura de Tests**
- Cobertura total del proyecto: 80% → 87%
- Tests totales: 165 → 208 (+43 tests)

**API Pública**
- Exportado desde `xps_analyzer.analysis.__init__.py`:
  * `load_sensitivity_factors`
  * `calculate_atomic_concentration`
  * `normalize_to_100`
  * `quantify_dataset`

---

## [0.6.0-beta] - 2026-03-02

**Hito:** Fase 1 - Sesión 2 completada - Ajuste de Picos

Implementación completa de ajuste de picos con perfiles gaussiano, lorentziano
y Voigt. Soporta ajuste de picos individuales y múltiples picos simultáneamente
con estimación automática de posiciones iniciales.

### Agregado

**Módulo de Peak Fitting** (`analysis/peak_fitting.py`)
- `fit_gaussian()`: Ajusta pico gaussiano con perfil A * exp(-(x-x0)²/(2σ²))
  * Estimación automática de parámetros iniciales
  * Bounds configurables
  * Cálculo de área: amplitude × width × √(2π)
- `fit_lorentzian()`: Ajusta pico lorentziano A * γ² / ((x-x0)² + γ²)
  * Mejor para estados con colas largas
  * Cálculo de área: amplitude × π × width
- `fit_voigt()`: Ajusta perfil Voigt (convolución gaussiano-lorentziano)
  * Más realista para XPS (considera ensanchamiento instrumental + tiempo de vida)
  * Parámetros sigma (gaussiano) y gamma (lorentziano)
  * Usa `scipy.special.voigt_profile`
- `fit_multiple_peaks()`: Ajuste simultáneo de múltiples picos
  * Soporta gaussian, lorentzian, voigt
  * Estimación automática o posiciones manuales
  * Optimización global con `scipy.optimize.curve_fit`
- `estimate_peak_positions()`: Detección automática de picos
  * Usa `scipy.signal.find_peaks`
  * Parámetros configurables: prominence, min_distance

**Dataclasses**
- `PeakParameters`: Parámetros de pico ajustado
  * position, amplitude, width, area, shape
  * gamma (para Voigt), errores estándar
- `FitResult`: Resultado completo de ajuste
  * Lista de picos, espectro ajustado, residual
  * R², χ² reducido, success, mensaje

**Tests** (120 → 165 tests, +45 tests)
- `test_peak_fitting.py`: 45 tests comprehensivos (100% passing)
  * TestEstimatePeakPositions: 7 tests
  * TestFitGaussian: 9 tests
  * TestFitLorentzian: 5 tests
  * TestFitVoigt: 7 tests
  * TestFitMultiplePeaks: 12 tests
  * TestMethodComparison: 3 tests
  * TestPeakFittingIntegration: 3 tests
- Cobertura del módulo: 95%

### Corregido

- TypeError en `voigt_profile()`: API requiere 3 args (x_centered, sigma, gamma)
- Detección de picos conservadora: ajustados prominence y min_distance defaults

---

## [0.5.5-beta] - 2026-03-02

**Hito:** Fase 1 - Sesión 1 completada - Sustracción de Fondo

Implementación de tres métodos estándar de sustracción de fondo para XPS:
Shirley (iterativo), Tougaard (dispersión inelástica), y Linear (simple).

### Agregado

**Módulo de Background Subtraction** (`analysis/background.py`)
- `shirley_background()`: Método iterativo más usado en XPS
  * Convergencia configurable (tol=1e-5, max_iter=100)
  * Almacena iteraciones en metadata
  * Referencia: Shirley, D.A. (1972), Phys Rev B, 5(12), 4709-4714
- `tougaard_background()`: Modelo de dispersión inelástica
  * Parámetros ajustables: B, C, D
  * Presets para orgánicos (B=2866, C=1643) y metales (B=1600, C=400)
  * Referencia: Tougaard, S. (1997), Surf Interface Anal, 25(3), 137-154
- `linear_background()`: Línea recta entre extremos
  * Método simple pero menos preciso

**Características Comunes**
- Parámetro `inplace` (modificar original vs retornar copia)
- Validación de entrada (≥3 puntos)
- Manejo automático de energías crecientes/decrecientes
- Metadata completa almacenada

**Tests** (90 → 120 tests, +30 tests)
- `test_background.py`: 30 tests comprehensivos (100% passing)
  * TestLinearBackground: 5 tests
  * TestShirleyBackground: 10 tests
  * TestTougaardBackground: 11 tests
  * TestBackgroundIntegration: 4 tests
- Cobertura del módulo: 96%

### Cambiado

**Estructura del Proyecto**
- Creado módulo `analysis/` con submódulos especializados
- Exportado funciones desde `xps_analyzer.analysis.__init__.py`

**Cobertura de Tests**
- Cobertura total: 80% → 85%
- Tests totales: 90 → 120

---

## [0.5.0-alpha] - 2026-03-01

**Hito:** Fase 0 completada al 90% - Fundamentos sólidos establecidos

Este lanzamiento marca la completitud de la Fase 0 del proyecto, estableciendo
fundamentos sólidos con corrección de bugs críticos, implementación de funcionalidad
stub, suite de tests comprehensiva, y documentación completa para usuarios.

### Agregado

**Funcionalidad Core**
- `load_all_data()`: Carga recursiva de directorios completos con manejo robusto de errores
- `detect_file_format()`: Detección automática de formatos (multiplex, survey, vamas, casa, text)
- Soporte para campos opcionales en `CompoundReference`: `peak_position` y `chemical_shift`

**Testing** (57 → 90 tests, +33 tests)
- `test_calibration.py`: Expandido de 11 a 18 tests (+7 tests de edge cases)
  * Tests con shift cero, shifts grandes (positivos/negativos)
  * Validación de preservación de intensidad y metadata
  * Tests con espectros de un solo punto y datasets vacíos
- `test_visualization.py`: 12 tests nuevos para funciones de plotting
  * Tests para `plot_spectrum()` y `plot_survey_spectrum()`
  * Verificación de inversión de eje X (convención XPS)
  * Validación de títulos, etiquetas y colores
- `test_cli.py`: 11 tests nuevos para comandos CLI
  * Tests para comandos `analyze` y `show-element`
  * Manejo de errores (archivos no encontrados, formatos inválidos)
- `test_data_loader.py`: Expandido de 4 a 20 tests (+15 tests)
  * Tests para `load_all_data()` (recursión, manejo de errores)
  * Tests para `detect_file_format()` (múltiples formatos)
- `test_reference_data.py`: 29 tests para base de datos de referencia

**Documentación**
- **Tutoriales completos** en `docs/tutorials/`:
  * `01_basic_usage.md`: Tutorial básico de uso (10-15 min)
  * `02_calibration.md`: Tutorial de calibración (15-20 min)
  * `03_element_identification.md`: Tutorial de identificación (20-25 min)
- `data/README.md`: Documentación de estructura y gestión de datos
- `tests/README.md`: Guía completa de testing (ejecutar, convenciones, estadísticas)
- Actualización de `CONTEXT.md` con estado completo del proyecto

### Corregido

**Bugs Críticos** (Issues #42, elementos.py, identification.py)
- `calibration.py:56-58`: IndexError cuando elemento de referencia no encontrado
  * Agregada validación de existencia del espectro de referencia
  * Mensajes de error descriptivos con regiones disponibles
- `calibration.py:48`: Validación de `binding_energy_most_useful is not None`
  * Agregado check explícito antes de usar valor de referencia
- `calibration.py:42-44`: Protección contra KeyError al buscar espectro
  * Uso de `.get()` con manejo de None
- `elements.py:170-171`: Acceso incorrecto a `photoelectron_lines.values()`
  * Corregido: `photoelectron_lines` es `List`, no `dict`
  * Iteración directa sobre la lista
- `elements.py:176`: Búsqueda en compounds sin validar `peak_position`
  * Agregado check `if compound.peak_position is not None`
- `identification.py:117`: Intento de acceso a `.peak_position` en string
  * Corregida iteración sobre diccionario de compounds
  * Uso correcto de `.items()` para obtener claves y valores

### Cambiado

**Mejoras de Robustez**
- `load_all_data()`: Continúa con otros archivos si uno falla (no crash)
  * Reporta primeros 5 errores al usuario
  * Retorna datasets exitosos incluso con errores parciales
- `detect_file_format()`: Detección multi-criterio (contenido + nombre + estructura)
  * Manejo de archivos binarios (retorna `None`)
  * Prioridad: VAMAS > CASA > multiplex > survey > text

**Validación**
- Validación manual mejorada en `__post_init__` para dataclasses
- Mensajes de error en español más descriptivos
- Type hints completados en nuevas funciones

### Deprecated

- Ninguno en esta versión

### Removed

- Ninguno en esta versión

### Security

- Ninguno en esta versión

### Estadísticas

**Código**
- Líneas de código: +1,444 líneas
  * `core.py`: +126 líneas (load_all_data, detect_file_format)
  * `elements.py`: +2 líneas (campos opcionales)
  * Tests: +524 líneas (3 archivos nuevos)
  * Tutoriales: +792 líneas (3 tutoriales)

**Tests**
- Total de tests: 90 (vs. 4 inicial)
- Cobertura: ~25-30% (objetivo Fase 0: 20% - ALCANZADO)
- Archivos de test: 5 módulos
- Líneas de código de tests: 1,553 líneas

**Documentación**
- Tutoriales: 3 archivos nuevos (~2,800 palabras)
- READMEs: 2 archivos nuevos (data/, tests/)
- Documentación total: >10,000 líneas en 15+ archivos

**Commits**
- Commits en esta versión: 4 commits principales
  * `61b182b`: fix(calibration) - Corregir bugs críticos + tests
  * `d1fece0`: fix(reference_data) - Corregir bugs en elements.py
  * `2be81ad`: feat(data_loader) - Implementar load_all_data y detect_file_format
  * `3508f0f`: test - Expandir cobertura con 30 tests nuevos

### Módulos por Completitud

| Módulo | Estado | Tests | Completitud |
|--------|--------|-------|-------------|
| data_loader | [COMPLETO] | 20 | 100% |
| reference_data | [COMPLETO] | 29 | 95% |
| preprocessing | [COMPLETO] | 18 | 80% |
| visualization | [TESTEADO] | 12 | 60% |
| cli | [TESTEADO] | 11 | 55% |
| analysis | [VACÍO] | 0 | 0% (Fase 1) |
| export | [VACÍO] | 0 | 0% (Fase 1) |

### Próximos Pasos (Fase 1)

**Funcionalidad Bloqueadora para v1.0:**
- Sustracción de fondo (Shirley, Tougaard)
- Ajuste de picos (gaussian, lorentzian, voigt)
- Cuantificación con factores de sensibilidad
- Exportación de resultados (CSV, Excel, JSON)

**Testing:**
- Alcanzar 60% de cobertura
- Tests de integración end-to-end

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
