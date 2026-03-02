# XPS Analyzer - Roadmap de Desarrollo

**Versión actual:** 0.7.0-beta  
**Estado:** Fase 1 (75% completado)  
**Actualización:** Marzo 2026

Este documento describe el plan de desarrollo del proyecto XPS Analyzer organizado en fases progresivas. Cada fase construye sobre la anterior, agregando funcionalidad crítica y mejorando la robustez del software.

---

## Visión General

El desarrollo de XPS Analyzer sigue un enfoque iterativo de 4 fases:

1. **Fase 0 (Actual)** - Fundamentos y documentación
2. **Fase 1** - Funcionalidad core de análisis
3. **Fase 2** - Robustez y formatos múltiples
4. **Fase 3** - Características avanzadas

**Principios guía:**
- Priorizar funcionalidad core sobre características avanzadas
- Mantener alta cobertura de tests (>60% desde Fase 1)
- Documentación exhaustiva en español
- Validación robusta de datos en todas las capas

---

## Fase 0: Fundamentos [COMPLETADO]

**Estado:** 100% completo  
**Objetivo:** Establecer base sólida con documentación completa y validación básica

### Completado [COMPLETADO]

**Carga de Datos**
- [x] Parser para formato propietario de texto
- [x] Detección básica de formato (multiplex vs survey)
- [x] Estructuras `XPSSpectrum`, `XPSDataset`, `XPSSample`
- [x] Validación manual con `__post_init__`

**Visualización**
- [x] Plots básicos de espectros (survey y regiones)
- [x] Convenciones XPS (eje x invertido)

**Calibración**
- [x] Calibración por elemento de referencia (C 1s)
- [x] Aplicación de shift a todos los espectros

**CLI**
- [x] Comando `analyze` para análisis básico
- [x] Comando `show-element` para info de referencia

**Datos de Referencia**
- [x] Base de datos JSON de ~25 elementos comunes
- [x] Carga con patrón singleton/cache
- [x] Búsqueda por energía de enlace con tolerancia

**Configuración**
- [x] Archivos TOML documentados (`config/`)
- [x] Perfiles de instrumentos XPS
- [x] Base de datos extendida de elementos

### Completado (Fase 0 finalizada)

**Testing**
- [x] Aumentar cobertura a 87% (superando objetivo de 20%)
- [x] Tests para validación de `XPSSpectrum`
- [x] Tests para validación de `XPSDataset`
- [x] Tests de integración básicos
- [x] 208 tests totales (100% passing)

**Documentación**
- [x] CONTEXT.md completo
- [x] ROADMAP.md (este archivo)
- [x] Todos los docs principales completados
- [x] READMEs en todos los subdirectorios

---

## Fase 1: Análisis Core [75% COMPLETADO]

**Estado:** 75% completo (3 de 4 sesiones completadas)  
**Objetivo:** Implementar funcionalidad esencial de análisis XPS

**Commits principales:**
- `fa8bcb8` - Sesión 1: Background Subtraction
- `da698d2` - Sesión 2: Peak Fitting  
- `097c3ca` - Sesión 3: Quantification

### 1.1 Sustracción de Fondo [COMPLETADO]

**Prioridad:** Alta (bloqueador para análisis cuantitativo)

**Métodos implementados:**
- [x] **Shirley background** (prioridad máxima)
  - Método iterativo estándar de la industria
  - Parámetros: max_iterations, tolerance
  - Validación con datos de referencia
  - 96% cobertura de tests
  
- [x] **Tougaard background**
  - Para análisis más preciso de profundidad
  - Parámetros B, C, D configurables
  - 4 variantes implementadas (B, C, D, D*)
  
- [x] **Linear background**
  - Para regiones planas sin picos intensos
  - Implementación completa

**API implementada:**
```python
from xps_analyzer.analysis import shirley_background, tougaard_background, linear_background

# Shirley
spectrum_clean = shirley_background(
    spectrum,
    max_iterations=50,
    tolerance=1e-6
)

# Tougaard (4 variantes: B, C, D, D*)
spectrum_clean = tougaard_background(
    spectrum,
    tougaard_type="universal"  # o "B", "C", "D", "D_star"
)

# Linear
spectrum_clean = linear_background(spectrum)
```

**Entregables completados:**
- [x] Módulo `analysis/background.py` (498 líneas)
- [x] 30 tests (100% passing)
- [x] 96% cobertura
- [x] Documentación completa con referencias científicas (Shirley 1972, Tougaard 1997)

### 1.2 Ajuste de Picos [COMPLETADO]

**Prioridad:** Alta (funcionalidad core)

**Formas de pico implementadas:**
- [x] **Gaussian** (más simple, para pruebas)
- [x] **Lorentzian** (XPS típico)
- [x] **Voigt** (convolución Gaussian-Lorentzian, más realista)
- [x] **Pseudo-Voigt** (aproximación rápida)
- [x] **Gaussian-Lorentzian Sum (GL)** (combinación lineal)

**Características implementadas:**
- [x] Ajuste de picos individuales
- [x] Deconvolución de múltiples picos
- [x] Constraints en parámetros (FWHM, posición, amplitud)
- [x] Estimación automática de parámetros iniciales
- [x] Cálculo de incertidumbres (σ)
- [x] Análisis de residuales (R², χ²)

**Dependencias:**
- [x] Usa `lmfit` para fitting robusto
- [x] Integración con base de datos de elementos

**API implementada:**
```python
from xps_analyzer.analysis import fit_gaussian, fit_lorentzian, fit_voigt, fit_multiple_peaks
from xps_analyzer.analysis import PeakParameters, FitResult

# Ajuste individual
result = fit_gaussian(
    spectrum,
    initial_params=PeakParameters(position=284.8, amplitude=1000, fwhm=1.2)
)

# Ajuste múltiple con constraints
result = fit_multiple_peaks(
    spectrum,
    initial_params=[
        PeakParameters(position=284.8, fwhm=1.2),
        PeakParameters(position=286.5, fwhm=1.5)
    ],
    peak_type="voigt",
    shared_fwhm=False
)

# result.best_fit: espectro ajustado
# result.residuals: diferencia observado - ajustado
# result.r_squared: bondad de ajuste
# result.chi_squared: χ² reducido
```

**Entregables completados:**
- [x] Módulo `analysis/peak_fitting.py` (849 líneas)
- [x] Dataclasses `PeakParameters`, `FitResult`
- [x] 45 tests (100% passing)
- [x] 95% cobertura
- [x] Documentación completa con referencias (Thompson 1987)

### 1.3 Cuantificación [COMPLETADO]

**Prioridad:** Alta (análisis fundamental)

**Características implementadas:**
- [x] Cálculo de concentraciones atómicas
- [x] Factores de sensibilidad de Scofield (completos para 89 elementos)
- [x] Factores de Wagner (empíricos, 18 elementos comunes)
- [x] Factores personalizados
- [x] Normalización a 100%
- [x] Validación de inputs robusta

**API implementada:**
```python
from xps_analyzer.analysis import (
    load_sensitivity_factors,
    calculate_atomic_concentration,
    normalize_to_100
)

# Cargar factores RSF
rsf = load_sensitivity_factors(source="scofield")  # o "wagner", "custom"

# Calcular concentraciones
intensities = {"C 1s": 10000, "O 1s": 5000, "N 1s": 1000}
concentrations = calculate_atomic_concentration(
    peak_areas=intensities,
    sensitivity_factors=rsf
)

# Normalizar a 100%
normalized = normalize_to_100(concentrations)
# Retorna: {"C": 62.5, "O": 31.3, "N": 6.2}
```

**Entregables completados:**
- [x] Módulo `analysis/quantification.py` (498 líneas)
- [x] Base de datos RSF Scofield (89 elementos) y Wagner (18 elementos)
- [x] 43 tests (100% passing)
- [x] 85% cobertura
- [x] Documentación completa con referencias (Scofield 1976, Wagner 1981)

### 1.4 Exportación [PENDIENTE - SESIÓN 4]

**Prioridad:** Media (última sesión de Fase 1)

**Formatos a soportar:**
- [ ] **CSV** (datos tabulares)
- [ ] **Excel** (múltiples hojas para datasets)
- [ ] **JSON** (metadata + datos)
- [ ] **Texto plano** (compatible con Origin, Igor)

**Características:**
- [ ] Exportar espectros individuales
- [ ] Exportar datasets completos
- [ ] Exportar resultados de análisis
- [ ] Configuración de precisión decimal
- [ ] Inclusión de metadata

**API propuesta:**
```python
from xps_analyzer.export import export_dataset

export_dataset(
    dataset,
    output_path="results/sample1.xlsx",
    format="excel",
    include_metadata=True,
    decimal_places=3
)
```

**Entregables:**
- Módulo `export/exporters.py`
- Soporte para múltiples formatos
- Tests de round-trip (export -> import)
- Documentación de formatos

### 1.5 Sistema de Configuración

**Prioridad:** Media (mejora usabilidad)

**Características:**
- [ ] Leer archivos TOML de `config/`
- [ ] Override con variables de entorno
- [ ] Override con argumentos CLI
- [ ] Validación de configuración
- [ ] Perfiles de usuario

**Implementación:**
- Usar `tomllib` (Python 3.11+) o `tomli` (backport)
- Validación básica de tipos y rangos
- Sistema de precedencia claro

**Entregables:**
- Módulo `config/loader.py`
- Tests de carga y validación
- Documentación de todas las opciones

### 1.6 Tests y Cobertura [SUPERADO]

**Prioridad:** Alta (calidad del código)

**Objetivo alcanzado:** 87% de cobertura (superando objetivo de 60%)

**Áreas testeadas:**
- [x] Background subtraction (30 tests, 96% cobertura)
- [x] Peak fitting (45 tests, 95% cobertura)
- [x] Quantification (43 tests, 85% cobertura)
- [x] Data loading (4 tests básicos)
- [ ] Export (pendiente - Sesión 4)
- [ ] Config loading (planeado para Fase 2)
- [ ] CLI commands (planeado para Fase 2)

**Tipos de tests implementados:**
- [x] Unit tests para funciones individuales (118 tests)
- [x] Tests paramétricos para múltiples escenarios
- [x] Tests de validación de inputs
- [x] Tests con datos sintéticos y reales

**Estadísticas finales Fase 1 (sesiones 1-3):**
- **Total tests:** 208 (100% passing)
- **Cobertura:** 87%
- **Líneas de código agregadas:** ~2,500

---

## Fase 2: Robustez y Formatos Múltiples

**Estado:** 0% completo  
**Objetivo:** Sistema robusto con soporte para formatos estándar de la industria

**Duración estimada:** 3-4 meses después de completar Fase 1

### 2.1 Migración a Pydantic

**Prioridad:** Alta (mejora arquitectura)

**Migración de data_loader:**
- [ ] Convertir `XPSSpectrum` a Pydantic `BaseModel`
- [ ] Convertir `XPSDataset` a Pydantic `BaseModel`
- [ ] Convertir `XPSSample` a Pydantic `BaseModel`
- [ ] Implementar `@field_validator` para validaciones complejas
- [ ] Agregar custom validators para metadatos
- [ ] Tests de migración (100% backward compatible)

**Beneficios:**
- Validación automática robusta
- Mensajes de error claros y estandarizados
- JSON schema generation para documentación
- Mejor integración con múltiples formatos
- Preparación para API web futura

**Breaking changes:**
- `.model_dump()` en lugar de `dataclasses.asdict()`
- `pydantic.ValidationError` en lugar de `ValueError`
- Guía de migración incluida en CHANGELOG.md

**Ejemplo de migración:**
```python
from pydantic import BaseModel, field_validator
import numpy as np

class XPSSpectrum(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any]
    
    @field_validator('intensity')
    def validate_arrays_match(cls, v, info):
        be = info.data.get('binding_energy')
        if be is not None and len(v) != len(be):
            raise ValueError(
                f"intensity length ({len(v)}) must match "
                f"binding_energy length ({len(be)})"
            )
        return v
```

### 2.2 Formato VAMAS (ISO 14976)

**Prioridad:** Alta (estándar internacional)

**Características:**
- [ ] Parser completo para VAMAS
- [ ] Soporte para metadata extendida
- [ ] Conversión a estructuras internas
- [ ] Validación con Pydantic schemas
- [ ] Tests con archivos VAMAS reales

**Entregables:**
- Módulo `data_loader/vamas_parser.py`
- Pydantic models para metadata VAMAS
- Documentación de campos soportados
- Ejemplos de conversión

### 2.3 Formato CASA XPS

**Prioridad:** Media (interoperabilidad)

**Características:**
- [ ] Parser para archivos `.casaxps`
- [ ] Importar regiones definidas
- [ ] Importar ajustes de picos
- [ ] Conversión de parámetros de CASA a xps-analyzer

**Nota:** CASA XPS es formato propietario, soporte best-effort

### 2.4 Formato HDF5

**Prioridad:** Media (datasets grandes)

**Características:**
- [ ] Exportar datasets a HDF5
- [ ] Importar desde HDF5
- [ ] Schema HDF5 con jerarquía clara
- [ ] Compresión para archivos grandes
- [ ] Metadata embebida

**Ventajas:**
- Manejo eficiente de datasets grandes
- Formato binario comprimido
- Ampliamente soportado en ciencia

### 2.5 Detección Automática de Formato

**Prioridad:** Alta (usabilidad)

**Características:**
- [ ] `detect_file_format()` completamente implementado
- [ ] Auto-selección de parser correcto
- [ ] Tests para todos los formatos
- [ ] Mensajes de error claros si formato desconocido

**Implementación:**
```python
def detect_file_format(filepath: Path) -> str:
    """Detecta automáticamente el formato del archivo."""
    # Leer primeras líneas
    # Buscar magic numbers/headers
    # Retornar: "vamas", "casa", "text", "hdf5", etc.
```

### 2.6 Sistema de Configuración Avanzado

**Prioridad:** Media (power users)

**Características:**
- [ ] Validación de configuración con Pydantic Settings
- [ ] Perfiles de usuario guardados
- [ ] Configuración por proyecto
- [ ] Plantillas de análisis comunes

### 2.7 Tests y Cobertura

**Objetivo:** 80% de cobertura

**Áreas adicionales:**
- [ ] Tests para todos los parsers de formato
- [ ] Tests de Pydantic validators
- [ ] Integration tests con workflows reales
- [ ] Tests de performance con archivos grandes

---

## Fase 3: Características Avanzadas

**Estado:** 0% completo  
**Objetivo:** Funcionalidad innovadora y herramientas avanzadas

**Duración estimada:** 6-8 meses después de completar Fase 2

### 3.1 Machine Learning para Identificación

**Prioridad:** Media (innovación)

**Características:**
- [ ] Clasificación automática de elementos
- [ ] Predicción de estados de oxidación
- [ ] Detección de contaminación
- [ ] Sugerencias de ajuste de picos

**Tecnologías:**
- scikit-learn para modelos básicos
- Entrenamiento con base de datos NIST
- Validación cruzada con datos reales

### 3.2 Análisis de Profundidad

**Prioridad:** Media (funcionalidad avanzada)

**Características:**
- [ ] Depth profiling con sputtering
- [ ] Análisis de multicapas
- [ ] Visualización 3D (profundidad vs energía)

### 3.3 GUI Interactiva

**Prioridad:** Baja (accesibilidad)

**Opciones de implementación:**
- Streamlit (más rápido, menos control)
- Dash (más flexible)
- Qt (nativa, más compleja)

**Características:**
- [ ] Carga de archivos drag-and-drop
- [ ] Visualización interactiva
- [ ] Ajuste de parámetros en tiempo real
- [ ] Exportación de reports

### 3.4 API REST

**Prioridad:** Baja (integración)

**Tecnología:** FastAPI + Pydantic

**Endpoints:**
- `POST /analyze` - Subir archivo y analizar
- `GET /elements` - Base de datos de elementos
- `GET /results/{id}` - Obtener resultados

### 3.5 Property-Based Testing

**Prioridad:** Alta (calidad)

**Objetivo:** 90% de cobertura

**Implementación:**
- Usar hypothesis para tests generativos
- Invariantes del sistema
- Fuzzing de parsers

---

## Criterios de Éxito por Fase

### Fase 0
- [COMPLETADO] Documentación completa (10 docs principales)
- [COMPLETADO] Validación básica implementada
- [EN DESARROLLO] Cobertura de tests >=20%

### Fase 1 (75% completado)
- [x] Background subtraction implementado (Shirley, Tougaard, Linear)
- [x] Peak fitting implementado (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL)
- [x] Quantification implementado (RSF Scofield, Wagner)
- [x] Cobertura de tests 87% (superando objetivo de 60%)
- [x] Validación con datos XPS sintéticos
- [ ] Export system (Sesión 4 pendiente)
- [ ] Comparación con CASA XPS (planeado)

### Fase 2
- Soporte para 4+ formatos de archivo
- Migración a Pydantic completada
- Cobertura de tests >=80%
- Performance acceptable con archivos grandes

### Fase 3
- ML model con accuracy >85%
- GUI funcional
- API REST documentada
- Cobertura de tests >=90%

---

## Dependencias entre Fases

```
Fase 0 (Fundamentos)
    |
Fase 1 (Análisis Core) <- BLOQUEADOR: Sin esto, no hay producto útil
    |
Fase 2 (Robustez) <- Construye sobre Fase 1
    |
Fase 3 (Avanzado) <- Opcional, mejora experiencia
```

**Nota crítica:** Fase 1 es BLOQUEADOR absoluto. Sin sustracción de fondo y ajuste de picos, el software no es útil para investigadores XPS.

---

## Contribuciones y Priorización

Si deseas contribuir al proyecto:

1. **Fase 1 es la prioridad máxima** - Cualquier PR relacionado con análisis core es bienvenido
2. **Tests son críticos** - PRs sin tests no serán mergeados
3. **Documentación en español** - Requisito obligatorio
4. **Seguir convenciones** - Ver CONTRIBUTING.md

**Issues etiquetados:**
- `Phase-1-blocker`: Funcionalidad crítica
- `Phase-2-enhancement`: Mejoras futuras
- `good-first-issue`: Para nuevos contribuidores

---

## Preguntas Frecuentes

**Q: ¿Por qué Pydantic está en Fase 2 y no Fase 0?**  
A: La validación manual es suficiente para un solo formato de archivo. Pydantic agrega valor real cuando soportamos múltiples formatos con diferentes schemas.

**Q: ¿Puedo empezar con Fase 3 si es más interesante?**  
A: No recomendado. El proyecto necesita funcionalidad core (Fase 1) antes que características avanzadas.

**Q: ¿Cuándo estará listo para producción?**  
A: Después de completar Fase 1 con cobertura de tests >=60%. Estimado: 6-8 meses desde ahora.

**Q: ¿Se aceptan contribuciones de características no en el roadmap?**  
A: Sí, pero deben discutirse primero en un issue. Asegúrate de que no compliquen el plan existente.

---

**Última actualización:** Marzo 2026  
**Próxima revisión:** Después de completar Sesión 4 (Export System)  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
