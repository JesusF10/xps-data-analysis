**Versión:** 0.9.0-alpha  
**Estado:** Fase 2 en PROGRESO (Arquitectura Pydantic Implementada)  
**Última actualización:** Abril 2026

Este documento describe la arquitectura técnica completa del proyecto XPS Analyzer, incluyendo decisiones de diseño, patrones de implementación, y guías para el desarrollo futuro.

---

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Modelo de Datos](#modelo-de-datos)
3. [Arquitectura de Módulos](#arquitectura-de-módulos)
4. [Sistema de Validación (Pydantic)](#sistema-de-validación-pydantic)
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

1. **Inmutabilidad por defecto** - Los datos originales nunca se modifican; las operaciones retornan copias profundas via `.model_copy(deep=True)`
2. **Separación de responsabilidades** - Cada módulo tiene una función clara y bien definida
3. **Validación robusta en runtime** - Uso de Pydantic para garantizar la integridad física de los datos espectrales
4. **Configuración explícita** - Todos los parámetros tienen valores por defecto documentados
5. **Extensibilidad** - Arquitectura preparada para plugins y nuevos formatos

### Stack Tecnológico

**Dependencias Core:**
- `numpy` (>=1.24.0) - Arrays numéricos, operaciones vectorizadas
- `scipy` (>=1.11.0) - Procesamiento de señales, interpolación
- `pydantic` (>=2.5.0) - Validación de datos y modelos (Fase 2 - COMPLETADO)
- `matplotlib` (>=3.7.0) - Visualización científica
- `lmfit` (>=1.2.0) - Ajuste de picos no lineal (Fase 1 - COMPLETADO)

**Dependencias de GUI y UI:**
- `streamlit` (>=1.30.0) - Interfaz interactiva (Fase 2 - EN PROGRESO)
- `plotly` (>=5.18.0) - Visualización dinámica (Fase 2 - PENDIENTE)

**Herramientas de Desarrollo:**
- `ruff` - Linting + formatting
- `pytest` - Testing framework (326+ tests)
- `uv` - Gestión de paquetes y entornos

---

## Modelo de Datos

### Jerarquía de Clases (Pydantic v2)

El sistema utiliza **Pydantic v2** para todos sus modelos de datos, heredando de `XPSBaseModel` (`src/xps_analyzer/utils/models.py`).

#### 1. XPSSpectrum - Nivel Atómico

**Ubicación:** `src/xps_analyzer/data_loader/core.py`

```python
class XPSSpectrum(XPSBaseModel):
    """
    Representa un espectro XPS individual.
    
    Responsabilidades:
    - Almacenar arrays de energía e intensidad (NumPy)
    - Validar automáticamente consistencia de datos
    - Proveer inmutabilidad mediante copias profundas
    """
    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_arrays(self):
        """Validación automática de longitudes y valores positivos."""
        ...
```

#### 2. XPSDataset - Nivel de Archivo

```python
class XPSDataset(XPSBaseModel):
    """Agrupa espectros relacionados de un mismo archivo físico."""
    filename: str
    header: dict[str, Any] = Field(default_factory=dict)
    spectra: dict[str, XPSSpectrum] = Field(default_factory=dict)
```

---

## Arquitectura de Módulos

```
src/xps_analyzer/
├── utils/models.py          # Clase base XPSBaseModel (Pydantic)
├── data_loader/core.py      # Modelos Core y Parsers
├── preprocessing/           # Calibración y normalización
├── analysis/                # Fondo, Ajuste de picos y Cuantificación
├── reference_data/          # Base de datos de elementos (Pydantic)
├── gui/                     # Interfaz Streamlit
└── export/                  # Exporters CSV, Excel, JSON
```

---

## Sistema de Validación (Pydantic)

**Estado:** 100% Implementado (Fase 2)

XPS Analyzer utiliza `XPSBaseModel` con la siguiente configuración:
* `arbitrary_types_allowed = True`: Permite el uso de arrays de NumPy.
* `validate_assignment = True`: Valida los datos incluso al reasignar atributos.

**Validadores Críticos:**
1. **Coincidencia de Longitud:** `binding_energy` e `intensity` deben tener el mismo tamaño.
2. **Energías Positivas:** No se permiten energías negativas o cero en el eje X.
3. **Inmutabilidad:** Se promueve el uso de `.model_copy(deep=True)` para evitar efectos secundarios en arrays de NumPy compartidos.

---

## Decisiones de Diseño

### 1. ¿Por qué Pydantic v2 en lugar de dataclasses?

**Decisión:** Migración total completada en Abril 2026.

**Razones:**
- [COMPLETADO] Validación robusta en tiempo real (evita estados inconsistentes).
- [COMPLETADO] Mensajes de error amigables para el usuario.
- [COMPLETADO] Serialización a JSON nativa para exportación y GUI.
- [COMPLETADO] Manejo superior de tipos complejos (arrays de NumPy).

### 2. Inmutabilidad Científica

**Decisión:** Se rechaza la mutación directa de datos espectrales.

**Razón:** Para mantener la trazabilidad de los datos científicos, cada paso del pipeline (calibración -> fondo -> ajuste) genera un nuevo objeto espectral. Esto evita errores comunes donde se "pierde" el dato original durante una sesión de análisis interactiva.

---

**Última actualización:** Abril 2026  
**Próxima revisión:** Lanzamiento v1.0.0  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
