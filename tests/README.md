# Tests - XPS Analyzer

Este directorio contiene la suite completa de tests para XPS Analyzer.

---

## Resumen Ejecutivo

**Total de tests:** 90 tests  
**Cobertura estimada:** ~25-30%  
**Framework:** pytest  
**Objetivo Fase 0:** 20% cobertura (ALCANZADO)  
**Objetivo Fase 2:** 80% cobertura

---

## Estructura de Tests

```
tests/
├── test_calibration.py         # 18 tests - Calibración de espectros
├── test_cli.py                 # 11 tests - Interfaz de línea de comandos
├── test_data_loader.py         # 20 tests - Carga de datos
├── test_reference_data.py      # 29 tests - Base de datos de referencia
├── test_visualization.py       # 12 tests - Funciones de plotting
└── README.md                   # Este archivo
```

---

## Ejecutar Tests

### Opción 1: Con uv (Recomendado)

```bash
# Todos los tests
uv run pytest

# Con output verbose
uv run pytest -v

# Tests específicos
uv run pytest tests/test_calibration.py

# Un test individual
uv run pytest tests/test_calibration.py::test_calibrate_spectrum_basic -v

# Con cobertura
uv run pytest --cov=src --cov-report=html --cov-report=term

# Generar reporte HTML (ver en htmlcov/index.html)
uv run pytest --cov=src --cov-report=html
```

### Opción 2: Con pytest directo (si está instalado)

```bash
pytest
pytest -v
pytest --cov=src
```

### Opción 3: Con Python

```bash
python -m pytest
python -m pytest -v
```

---

## Descripción de Módulos de Test

### `test_calibration.py` (18 tests)

**Cobertura:** Módulo `preprocessing/calibration.py`

**Tests incluidos:**
- Calibración de espectros individuales (`calibrate_spectrum`)
- Calibración de datasets completos (`calibrate_sample`)
- Comportamiento con `inplace=True` vs `inplace=False`
- Edge cases: shift cero, shifts grandes, espectro de un solo punto
- Validación: preservación de intensidad y metadata
- Manejo de errores: elemento no encontrado, dataset vacío

**Fixtures:**
- `simple_spectrum`: Espectro C 1s de prueba
- `simple_dataset`: Dataset con C 1s y O 1s
- `carbon_reference`: ElementReference para carbono
- `oxygen_reference`: ElementReference para oxígeno

**Ejemplo:**
```python
def test_calibrate_spectrum_basic(simple_spectrum):
    """Test calibración básica de un espectro."""
    shift = 0.8
    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)
    # Verificaciones...
```

### `test_cli.py` (11 tests)

**Cobertura:** Módulo `cli/main.py`

**Tests incluidos:**
- Comando `analyze`: análisis de archivos
- Comando `show-element`: información de elementos
- Flags: `--help`, `--version`, `--verbose`
- Manejo de errores: archivo no encontrado, errores de carga
- Validación de outputs

**Técnica:** Uso de `Click.testing.CliRunner` y mocks

**Ejemplo:**
```python
def test_analyze_basic(mock_load_file, runner, tmp_path):
    """Test comando analyze con archivo válido."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy content")
    
    result = runner.invoke(analyze, [str(test_file)])
    assert result.exit_code == 0
```

### `test_data_loader.py` (20 tests)

**Cobertura:** Módulo `data_loader/core.py`

**Tests incluidos:**
- Carga de archivos individuales (`load_single_file`)
- Carga de directorios (`load_all_data`)
- Detección de formatos (`detect_file_format`)
- Parsing de metadata y datos
- Validación de estructuras de datos
- Manejo de errores: archivos inválidos, formatos desconocidos

**Fixtures:**
- `tmp_path`: Directorio temporal de pytest
- Archivos de prueba creados dinámicamente

**Ejemplo:**
```python
def test_load_all_data_basic(tmp_path):
    """Test carga recursiva de directorio."""
    # Crear archivos de prueba
    file1 = tmp_path / "sample1.txt"
    file1.write_text("dummy content")
    
    datasets = load_all_data(tmp_path)
    assert len(datasets) == 1
```

### `test_reference_data.py` (29 tests)

**Cobertura:** Módulos `reference_data/elements.py` y `identification.py`

**Tests incluidos:**
- Carga de base de datos (`load_reference_database`)
- Estructura de clases: `ElementReference`, `PhotoelectronLine`, `CompoundReference`
- Búsqueda por energía (`search_by_binding_energy`)
- Identificación de elementos (`identify_elements_in_spectrum`)
- Sugerencia de compuestos (`suggest_compounds`)
- Validación de datos JSON

**Ejemplo:**
```python
def test_search_by_binding_energy():
    """Test búsqueda de elementos por energía de enlace."""
    db = load_reference_database()
    results = db.search_by_binding_energy(284.8, tolerance=2.0)
    
    assert len(results) > 0
    assert any(elem.symbol == "C" for elem in results)
```

### `test_visualization.py` (12 tests)

**Cobertura:** Módulo `visualization/plotting.py`

**Tests incluidos:**
- `plot_spectrum`: plots de espectros individuales
- `plot_survey_spectrum`: plots de espectros survey
- Verificación de inversión de eje X (convención XPS)
- Validación de títulos, etiquetas y colores
- Tests con títulos personalizados

**Técnica:** Uso de `unittest.mock.patch` para evitar ventanas de matplotlib

**Ejemplo:**
```python
@patch("xps_analyzer.visualization.plotting.plt.show")
def test_plot_spectrum_basic(mock_show, simple_spectrum):
    """Test que plot_spectrum ejecuta sin errores."""
    plot_spectrum(simple_spectrum)
    mock_show.assert_called_once()
```

---

## Convenciones de Testing

### Nombres de Tests

```python
# Patrón: test_{función}_{aspecto}
def test_calibrate_spectrum_basic():           # Test básico
def test_calibrate_spectrum_inplace_true():    # Caso específico
def test_calibrate_sample_error_handling():    # Manejo de errores
```

### Docstrings

```python
def test_example():
    """
    Test descripción corta en español.
    
    Puede incluir detalles adicionales sobre:
    - Qué se está testeando
    - Por qué es importante
    - Edge cases cubiertos
    """
    pass
```

### Fixtures

```python
@pytest.fixture
def mi_fixture():
    """Descripción de la fixture."""
    # Setup
    data = crear_datos_prueba()
    
    yield data
    
    # Teardown (opcional)
    limpiar_recursos()
```

### Assertions

```python
# Usar asserts específicos de pytest
assert resultado == esperado
assert resultado is not None
assert len(lista) > 0

# NumPy arrays
import numpy as np
np.testing.assert_array_equal(array1, array2)
np.testing.assert_array_almost_equal(array1, array2, decimal=5)

# Exceptions
import pytest
with pytest.raises(ValueError) as excinfo:
    funcion_que_falla()
assert "mensaje esperado" in str(excinfo.value)
```

---

## Marcadores de pytest

### Uso de Marcadores

```python
import pytest

# Test lento (skip en ejecución rápida)
@pytest.mark.slow
def test_procesamiento_grande():
    pass

# Test que requiere datos externos
@pytest.mark.integration
def test_carga_archivo_real():
    pass

# Skip condicional
@pytest.mark.skipif(sys.platform == "win32", reason="No funciona en Windows")
def test_unix_specific():
    pass
```

### Ejecutar con Marcadores

```bash
# Solo tests rápidos
pytest -m "not slow"

# Solo tests de integración
pytest -m integration

# Excluir marcadores
pytest -m "not (slow or integration)"
```

---

## Cobertura de Código

### Generar Reporte de Cobertura

```bash
# Terminal + HTML
uv run pytest --cov=src --cov-report=html --cov-report=term

# Solo HTML (más detallado)
uv run pytest --cov=src --cov-report=html
firefox htmlcov/index.html  # o tu navegador preferido
```

### Interpretar Cobertura

- **Verde (>80%):** Muy bien cubierto
- **Amarillo (50-80%):** Cobertura aceptable, mejorar
- **Rojo (<50%):** Cobertura insuficiente, agregar tests

### Excluir Líneas de Cobertura

```python
def funcion_debug():  # pragma: no cover
    """Función solo para debugging."""
    print("Debug info")
```

---

## Continuous Integration (CI)

### GitHub Actions (Planeado)

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Run tests
        run: uv run pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Debugging de Tests

### Ejecutar con Debugger

```bash
# Con pdb
pytest --pdb

# Parar en primera falla
pytest -x --pdb

# Output completo
pytest -vv -s
```

### Print Debugging

```python
def test_mi_funcion():
    resultado = mi_funcion(input)
    
    # Prints se muestran con -s flag
    print(f"Resultado: {resultado}")
    
    assert resultado == esperado
```

### Captura de Output

```python
def test_con_captura(capsys):
    """Test que captura stdout/stderr."""
    print("mensaje")
    captured = capsys.readouterr()
    assert "mensaje" in captured.out
```

---

## Mejores Prácticas

### DO:
1. **Un assert por test** (idealmente) - tests más claros
2. **Usar fixtures reutilizables** - DRY principle
3. **Tests aislados** - no depender de orden de ejecución
4. **Nombres descriptivos** - `test_calibrate_with_missing_element` > `test1`
5. **Docstrings en español** - consistencia con el proyecto

### DON'T:
1. **No usar datos reales grandes** - crear datos sintéticos pequeños
2. **No testear implementación** - testear comportamiento
3. **No duplicar tests** - consolidar tests similares
4. **No ignorar warnings** - fixtures o imports deprecated
5. **No commitear tests comentados** - eliminar o arreglar

---

## Tests Pendientes (TODOs)

### Fase 1
- [ ] Tests para `analysis/peak_fitting.py`
- [ ] Tests para `analysis/quantification.py`
- [ ] Tests para `preprocessing/background_subtraction.py`
- [ ] Tests para `export/` módulos

### Fase 2
- [ ] Tests de integración end-to-end
- [ ] Tests de performance (benchmarks)
- [ ] Tests para múltiples formatos de archivo
- [ ] Property-based testing con `hypothesis`

---

## Estadísticas

```
Total de tests:         90
Total de líneas:      1,553
Tiempo de ejecución:  ~5-10s (sin dependencias instaladas)
Cobertura:            ~25-30%

Por módulo:
- test_reference_data.py:  29 tests  (415 líneas)
- test_data_loader.py:     20 tests  (354 líneas)
- test_calibration.py:     18 tests  (372 líneas)
- test_visualization.py:   12 tests  (176 líneas)
- test_cli.py:             11 tests  (236 líneas)
```

---

## Recursos

- **pytest docs:** https://docs.pytest.org/
- **pytest-cov docs:** https://pytest-cov.readthedocs.io/
- **Testing Best Practices:** https://docs.python-guide.org/writing/tests/
- **TESTING.md:** Estrategia de testing completa del proyecto

---

**Última actualización:** Marzo 2026  
**Versión:** 0.5.0-alpha
