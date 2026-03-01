# Directorio de Tests

Tests unitarios, de integración y fixtures para el proyecto.

## Estructura

- `unit/` - Tests unitarios de funciones individuales
- `integration/` - Tests de workflows completos
- `fixtures/` - Datos de test reutilizables

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Solo unit tests
pytest tests/unit/

# Test específico
pytest tests/unit/test_data_loader.py::test_parse_metadata_header_basic -v
```

## Convenciones

- Nombrar archivos: `test_*.py`
- Nombrar funciones: `test_descripcion_clara()`
- Un concepto por test
- Usar fixtures para setup compartido
- Docstrings explicando qué verifica el test
