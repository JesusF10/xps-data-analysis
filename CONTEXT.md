# XPS Analyzer - Contexto Completo del Proyecto

**Versión:** 0.9.0-alpha  
**Estado:** Fase 2 en PROGRESO (Migración Pydantic COMPLETADA)  
**Última actualización:** Abril 2026

Este documento proporciona contexto completo para agentes de IA, desarrolladores y colaboradores sobre el proyecto XPS Analyzer.

---

## Resumen Ejecutivo

**XPS Analyzer** es un paquete Python científico para análisis automatizado de datos de Espectroscopía de Fotoelectrones de Rayos X (XPS), desarrollado como proyecto de servicio social en investigación de química y metalurgia. El software carga formatos propietarios de datos XPS, realiza calibración de energía, identifica elementos/compuestos, sustrae fondos, ajusta picos, cuantifica composición atómica, exporta resultados y genera reportes analíticos.

**Estado actual:** Fase 2 EN PROGRESO (60% completada). Funcionalidad core de análisis implementada y robustecida mediante **Pydantic v2**. Interfaz gráfica (Streamlit) funcional y en mejora continua.

**Público objetivo:**
- Investigadores en química de superficies
- Laboratorios de caracterización de materiales
- Estudiantes de posgrado en ciencia de materiales

---

## Arquitectura del Proyecto

### Jerarquía del Modelo de Datos

El proyecto utiliza una jerarquía de tres niveles basada en **Pydantic v2** (`XPSBaseModel` ubicado en `src/xps_analyzer/utils/models.py`):

```python
class XPSSpectrum(XPSBaseModel):
    """Espectro individual con validación automática Pydantic."""
    region_name: str
    binding_energy: np.ndarray  # eV
    intensity: np.ndarray       # cuentas arbitrarias
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_arrays(self):
        """Validación automática: longitudes coincidentes, no vacíos."""
        ...

class XPSDataset(XPSBaseModel):
    """Archivo completo con múltiples espectros (survey + regiones)."""
    filename: str
    header: dict[str, Any]
    spectra: dict[str, XPSSpectrum]  # key = region_name

class XPSSample(XPSBaseModel):
    """Colección de datasets relacionados (múltiples archivos de una muestra)."""
    sample_name: str
    datasets: dict[str, XPSDataset]  # key = filename
```

**Patrón importante:** Siempre usar `.model_copy(deep=True)` al modificar modelos para asegurar la inmutabilidad de los datos científicos y evitar mutaciones en arrays de NumPy compartidos. Las funciones usan parámetro `inplace=bool` para controlar mutación vs. copia profunda.

### Sistema de Datos de Referencia

La base de datos de elementos (`src/xps_analyzer/reference_data/`) usa patrón singleton con cache global y modelos Pydantic:

- `load_reference_database()` retorna instancia en cache de `ReferenceDatabase`.
- Los modelos `PhotoelectronLine` y `ElementReference` validan automáticamente los datos al cargar desde JSON.
- Búsquedas de energía de enlace usan parámetro `tolerance` (default 2.0 eV).

**Elementos soportados:** ~25 elementos comunes en XPS (C, O, N, Si, Al, Fe, Ti, Cu, Au, etc.)

### Detección de Formato de Archivo

El cargador de datos (`core.py`) auto-detecta tipos de archivo:

- **"multiplex" en nombre de archivo** -> formato multi-región con header.
- **Default** -> espectro survey único.
- **Parser:** usa delimitadores `;` para metadata, valores separados por espacio para columnas de datos.

**Estado actual:** Soporte para formato propietario. **Fase 2** completó la migración a Pydantic para todos los cargadores.

---

## Estructura de Módulos

```
src/xps_analyzer/
├── __init__.py              # API de alto nivel
├── data_loader/             # [COMPLETADO] 100% migrado a Pydantic
│   ├── core.py             # Modelos core + parsing
│   └── __init__.py         
├── preprocessing/           # [COMPLETADO] 100% completo
│   ├── calibration.py      # Calibración profunda (model_copy)
│   └── __init__.py         
├── analysis/                # [COMPLETADO] 100% migrado a Pydantic
│   ├── __init__.py         
│   ├── background.py       # Shirley, Tougaard, Linear (model_copy)
│   ├── peak_fitting.py     # FitResult y PeakParameters (Pydantic)
│   └── quantification.py   # Cuantificación atómica
├── reference_data/          # [COMPLETADO] 100% migrado a Pydantic
│   ├── elements.py         # Modelos de referencia Pydantic
│   ├── identification.py   
│   ├── data/               
│   └── __init__.py
├── visualization/           # [EN PROGRESO] 40% completo
│   ├── plotting.py         # Matplotlib científico
│   └── __init__.py         
├── export/                  # [COMPLETADO] 100% funcional
│   └── exporters.py        # CSV, Excel, JSON
├── gui/                     # [EN PROGRESO] 50% completo
│   ├── app.py              # Interfaz Streamlit
│   └── __init__.py         
├── cli/                     # [COMPLETADO] 90% completo
│   └── main.py             # analyze, show-element
└── utils/                   # [COMPLETADO]
    ├── models.py           # XPSBaseModel (Pydantic base)
    └── __init__.py         
```

### Estado de Implementación por Módulo

| Módulo | Estado | Tests | Cobertura |
|--------|--------|-------|-----------|
| `data_loader` | 100% | 18 tests | ~80% |
| `preprocessing`| 100% | 18 tests | ~95% |
| `analysis`     | 100% | 120+ tests| ~95% |
| `export`       | 100% | 19 tests | 92% |
| `reference`    | 100% | 30 tests | ~85% |
| `gui`          | 50%  | 12 tests | 40% |
| `cli`          | 90%  | 11 tests | 96% |

**Total tests:** 355 (100% passing)  
**Cobertura total:** 87%  
**Líneas de código:** ~5,200

---

## Convenciones del Proyecto

### 1. Idioma

**CRÍTICO:** Todo el código debe estar en español (docstrings, comentarios, errores). Nombres de variables en inglés.

### 2. Inmutabilidad y Pydantic

**IMPORTANTE:** Nunca usar `copy.deepcopy()` directamente en modelos. Usar siempre `modelo.model_copy(deep=True)`.

### 3. Validación

Toda nueva clase de datos debe heredar de `XPSBaseModel` y definir validadores si maneja arrays de NumPy o restricciones físicas.

---

## Roadmap Actualizado

### Fase 1 - Análisis Core [COMPLETADA]

### Fase 2 - Pydantic + GUI Interactiva [EN PROGRESO]
- [x] Migración total a Pydantic v2 (Core, Referencia, Análisis)
- [x] Inmutabilidad via `model_copy(deep=True)`
- [x] GUI inicial con Streamlit
- [ ] Visualización avanzada con Plotly
- [ ] Análisis interactivo en tiempo real

---

**Última revisión:** Abril 2026  
**Próxima revisión:** Lanzamiento v1.0.0  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)