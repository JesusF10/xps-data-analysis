# XPS Analyzer - Roadmap de Desarrollo

**Versión actual:** 0.1.0  
**Estado:** Fase 0 (35% completado)  
**Actualización:** Febrero 2026

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

## Fase 0: Fundamentos (Actual)

**Estado:** 35% completo  
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

### Pendiente [EN DESARROLLO]

**Testing**
- [ ] Aumentar cobertura a 20% (actual: <20%)
- [ ] Tests para validación de `XPSSpectrum`
- [ ] Tests para validación de `XPSDataset`
- [ ] Tests de integración básicos

**Documentación**
- [x] CONTEXT.md completo
- [x] ROADMAP.md (este archivo)
- [ ] Completar todos los docs principales
- [ ] READMEs en todos los subdirectorios

---

## Fase 1: Análisis Core

**Estado:** 0% completo  
**Objetivo:** Implementar funcionalidad esencial de análisis XPS

**Duración estimada:** 4-6 meses después de completar Fase 0

### 1.1 Sustracción de Fondo

**Prioridad:** Alta (bloqueador para análisis cuantitativo)

**Métodos a implementar:**
- [ ] **Shirley background** (prioridad máxima)
  - Método iterativo estándar de la industria
  - Parámetros: max_iterations, tolerance
  - Validación con datos de referencia
  
- [ ] **Tougaard background**
  - Para análisis más preciso de profundidad
  - Parámetros B, C, D configurables
  
- [ ] **Linear background**
  - Para regiones planas sin picos intensos
  
- [ ] **Polynomial background**
  - Orden configurable (2-5)

**API propuesta:**
```python
from xps_analyzer.preprocessing import subtract_background

spectrum_clean = subtract_background(
    spectrum,
    method="shirley",
    iterations=10,
    tolerance=1e-5,
    inplace=False
)
```

**Entregables:**
- Módulo `preprocessing/background.py`
- Tests con espectros sintéticos y reales
- Documentación de cada método
- Ejemplos en notebooks

### 1.2 Ajuste de Picos

**Prioridad:** Alta (funcionalidad core)

**Formas de pico a soportar:**
- [ ] **Gaussian** (más simple, para pruebas)
- [ ] **Lorentzian** (XPS típico)
- [ ] **Voigt** (convolución Gaussian-Lorentzian, más realista)
- [ ] **Pseudo-Voigt** (aproximación rápida)

**Características:**
- [ ] Ajuste de picos individuales
- [ ] Deconvolución de múltiples picos
- [ ] Constraints en parámetros (FWHM, posición, amplitud)
- [ ] Soporte para doublets (spin-orbit coupling)
- [ ] Estimación automática de parámetros iniciales

**Dependencias:**
- Usar `lmfit` para fitting robusto
- Integración con base de datos de elementos

**API propuesta:**
```python
from xps_analyzer.analysis import fit_peaks

result = fit_peaks(
    spectrum,
    peak_shapes=["voigt", "voigt"],
    initial_positions=[284.8, 286.0],
    constraints={"fwhm_max": 2.0}
)

# result.peaks: lista de Peak objects
# result.fitted_spectrum: espectro ajustado
# result.residuals: diferencia observado - ajustado
# result.r_squared: bondad de ajuste
```

**Entregables:**
- Módulo `analysis/peak_fitting.py`
- Clase `Peak` para representar picos ajustados
- Tests extensivos con datos sintéticos
- Validación con datos XPS reales
- Tutorial de uso

### 1.3 Cuantificación

**Prioridad:** Alta (análisis fundamental)

**Características:**
- [ ] Cálculo de concentraciones atómicas
- [ ] Factores de sensibilidad de Scofield
- [ ] Factores específicos de instrumento
- [ ] Corrección por ángulo de emisión
- [ ] Normalización a 100%
- [ ] Reportes tabulares

**API propuesta:**
```python
from xps_analyzer.analysis import quantify

results = quantify(
    dataset,
    use_sensitivity_factors=True,
    instrument_profile="kratos_axis_ultra",
    normalize=True,
    exclude_elements=["Ar"]  # contaminación
)

# results.concentrations: dict {element: at.%}
# results.uncertainties: dict {element: error}
# results.table: pandas DataFrame
```

**Entregables:**
- Módulo `analysis/quantification.py`
- Base de datos de factores de sensibilidad
- Tests con datos estándar
- Comparación con CASA XPS
- Documentación de teoría

### 1.4 Exportación

**Prioridad:** Media (no bloqueante pero necesaria)

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

### 1.6 Tests y Cobertura

**Prioridad:** Alta (calidad del código)

**Objetivo:** 60% de cobertura mínima

**Áreas a testear:**
- [ ] Background subtraction (todos los métodos)
- [ ] Peak fitting (todas las formas)
- [ ] Quantification (múltiples escenarios)
- [ ] Export (todos los formatos)
- [ ] Config loading (validación)
- [ ] CLI commands (argumentos, errores)

**Tipos de tests:**
- Unit tests para funciones individuales
- Integration tests para workflows completos
- Tests con datos reales de XPS

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

### Fase 1
- Todas las funcionalidades core implementadas
- Cobertura de tests >=60%
- Validación con datos XPS reales
- Comparación exitosa con CASA XPS

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

**Última actualización:** Febrero 2026  
**Próxima revisión:** Después de completar Fase 0  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
