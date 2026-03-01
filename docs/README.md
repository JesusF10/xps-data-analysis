# Directorio de Documentación

Documentación adicional y tutoriales para usuarios del proyecto.

## Subdirectorios

### `tutorials/`
Tutoriales paso a paso para casos de uso comunes.

### `api/`
Documentación detallada de la API (generada automáticamente con Sphinx en el futuro).

### `examples/`
Ejemplos de código y casos de uso reales.

## Generación de Docs

```bash
# Instalar dependencias (futuro)
pip install ".[docs]"

# Generar documentación
sphinx-build -b html docs/ docs/_build/
```
