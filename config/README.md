# Directorio de Configuración

Este directorio contiene archivos de configuración TOML para personalizar el comportamiento del análisis XPS.

## Archivos Disponibles

### `default_settings.toml`
Parámetros por defecto para todos los análisis:
- Sustracción de fondo (Shirley, Tougaard, etc.)
- Ajuste de picos (formas, constraints)
- Calibración de energía
- Cuantificación
- Preprocesamiento
- Exportación
- Visualización

**Uso:**
```python
from xps_analyzer.config import load_settings
settings = load_settings("config/default_settings.toml")
```

### `instrument_profiles.toml`
Perfiles de instrumentos XPS/UPS comunes:
- Resolución de energía
- Opciones de pass energy
- Fuentes de rayos X (Al Kα, Mg Kα)
- Factores de sensibilidad específicos del instrumento

**Instrumentos incluidos:**
- Generic XPS/UPS
- Kratos Axis Ultra DLD
- SPECS Phoibos 150
- Thermo Scientific K-Alpha

### `element_database.toml`
Base de datos extendida de elementos:
- Componentes químicos comunes (C 1s, Si 2p, O 1s)
- Spin-orbit coupling parameters
- Desplazamientos químicos por estado de oxidación

## Personalización

Puedes crear tus propios archivos de configuración basándote en estos ejemplos:

```bash
# Copiar configuración por defecto
cp config/default_settings.toml config/my_analysis.toml

# Editar según tus necesidades
nano config/my_analysis.toml
```

## Prioridad de Configuración

El sistema de configuración sigue esta jerarquía (mayor a menor prioridad):

1. **Argumentos CLI**: `--method shirley --iterations 20`
2. **Variables de entorno**: `XPS_BACKGROUND_METHOD=shirley`
3. **Archivo de usuario**: `config/my_analysis.toml`
4. **Valores por defecto**: `config/default_settings.toml`

## Formato TOML

TOML (Tom's Obvious, Minimal Language) es un formato de configuración legible:

```toml
# Comentarios con #
[sección]
clave = "valor"
número = 42
lista = ["a", "b", "c"]
booleano = true

[sección.subsección]
anidado = "también funciona"
```

## Validación

La configuración se valida automáticamente al cargar:
- Tipos de datos correctos
- Valores dentro de rangos válidos
- Claves requeridas presentes

Los errores se reportan claramente:
```
ConfigurationError: 'background_subtraction.iterations' debe ser un entero positivo, recibido: -5
```

## Notas de Implementación

**Estado actual (v0.1.0):** Los archivos TOML están documentados pero la funcionalidad de carga aún no está implementada.

**Fase 1:** Implementar sistema de configuración con `tomllib` (Python 3.11+) o `tomli` (backport).

**Fase 2:** Validación con Pydantic Settings para type safety y mejores mensajes de error.
