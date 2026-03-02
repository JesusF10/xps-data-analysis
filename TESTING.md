# XPS Analyzer - Estrategia de Testing

**Versión:** 0.7.0-beta  
**Estado:** Fase 1 (75% completado)  
**Cobertura actual:** 87% (208 tests existentes)  
**Última actualización:** Marzo 2026

Este documento describe la estrategia completa de testing del proyecto XPS Analyzer, incluyendo convenciones, roadmap de cobertura, y ejemplos prácticos.

---

## Tabla de Contenidos

1. [Estado Actual](#estado-actual)
2. [Filosofía de Testing](#filosofía-de-testing)
3. [Tipos de Tests](#tipos-de-tests)
4. [Estructura de Tests](#estructura-de-tests)
5. [Roadmap de Cobertura](#roadmap-de-cobertura)
6. [Convenciones](#convenciones)
7. [Fixtures y Helpers](#fixtures-y-helpers)
8. [Testing de Validación](#testing-de-validación)
9. [Property-Based Testing](#property-based-testing)
10. [Comandos Útiles](#comandos-útiles)

---

## Estado Actual

### Tests Existentes

**Ubicación:** `tests/`

```python
# 208 tests implementados (todos pasan):

## tests/test_data_loader.py (4 tests)
1. test_parse_metadata_basic()           # Parsing de metadata básica
2. test_parse_metadata_header()          # Parsing de header con 3 líneas
3. test_get_spectrum_data_basic()        # Carga de espectro desde texto
4. test_get_spectrum_data_malformed_line_raises()  # Validación de errores

## tests/test_background.py (30 tests)
- Tests de shirley_background (15 tests)
- Tests de tougaard_background (10 tests) 
- Tests de linear_background (5 tests)

## tests/test_peak_fitting.py (45 tests)
- Tests de fit_gaussian, fit_lorentzian, fit_voigt (30 tests)
- Tests de fit_multiple_peaks (10 tests)
- Tests de PeakParameters y FitResult (5 tests)

## tests/test_quantification.py (43 tests)
- Tests de load_sensitivity_factors (15 tests)
- Tests de calculate_atomic_concentration (20 tests)
- Tests de normalize_to_100 (8 tests)

## tests/test_reference_data.py (86 tests)
- Tests de carga de base de datos
- Tests de búsqueda de elementos
```

### Cobertura por Módulo

```
Módulo                    | Cobertura | Tests | Prioridad
--------------------------|-----------|-------|----------
data_loader/core.py       | 60%       | 4     | Media
preprocessing/            | 90%       | Incl. | Alta
analysis/background       | 96%       | 30    | Alta (COMPLETADO)
analysis/peak_fitting     | 95%       | 45    | Alta (COMPLETADO)
analysis/quantification   | 85%       | 43    | Alta (COMPLETADO)
reference_data/elements   | 70%       | 86    | Media
reference_data/identification | 60%   | Incl. | Media
visualization/            | 0%        | 0     | Baja
cli/                      | 0%        | 0     | Baja
export/                   | N/A       | N/A   | Alta (Sesión 4 pendiente)
--------------------------|-----------|-------|----------
TOTAL                     | 87%       | 208   | -
```

**Meta de cobertura:**
- **Fase 0 (completada):** 20% cobertura significativa ✓ (alcanzado 87%)
- **Fase 1 (75% completado):** 60% ✓ (alcanzado 87%)
- **Fase 2:** 85% (incluir integración multi-formato)
- **Fase 3:** 90% (property-based testing, edge cases)

---

## Filosofía de Testing

### Principios

1. **Tests primero para bugs** - Siempre escribir test que reproduzca el bug antes de arreglarlo
2. **Cobertura con propósito** - No buscar 100% de cobertura, sino tests significativos
3. **Tests como documentación** - Los tests deben mostrar cómo usar la API
4. **Rapidez** - Test suite completo debe correr en <30 segundos
5. **Aislamiento** - Cada test debe ser independiente (sin efectos secundarios)

### Qué Testear

**Alta prioridad:**
- [COMPLETADO] API pública de cada módulo
- [COMPLETADO] Validación de inputs
- [COMPLETADO] Casos límite (edge cases)
- [COMPLETADO] Manejo de errores

**Media prioridad:**
- [EN PROGRESO] Funciones internas complejas
- [EN PROGRESO] Integración entre módulos
- [EN PROGRESO] Performance (tests de benchmark)

**Baja prioridad:**
- [PENDIENTE] Getters/setters simples
- [PENDIENTE] Código trivial sin lógica
- [PENDIENTE] Código de terceros (ya testeado)

---

## Tipos de Tests

### 1. Tests Unitarios

**Propósito:** Testear funciones/clases individuales en aislamiento.

**Ubicación:** `tests/unit/`

**Ejemplo:**

```python
# tests/unit/test_calibration.py
import pytest
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum
from xps_analyzer.preprocessing import calibrate_spectrum

def test_calibrate_spectrum_basic():
    """Test calibración con desplazamiento conocido."""
    # Arrange
    energy = np.array([280.0, 281.0, 282.0, 283.0, 284.0])
    intensity = np.array([100, 200, 300, 400, 500])
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=energy,
        intensity=intensity
    )
    
    # Act: calibrar con C 1s @ 284.8 eV
    # (peak actual en 284.0 -> shift = +0.8 eV)
    calibrated = calibrate_spectrum(
        spectrum=spectrum,
        reference_element="C",
        inplace=False
    )
    
    # Assert
    np.testing.assert_array_almost_equal(
        calibrated.binding_energy,
        np.array([280.8, 281.8, 282.8, 283.8, 284.8]),
        decimal=6
    )
    # Intensidad no cambia
    np.testing.assert_array_equal(calibrated.intensity, intensity)
    # Original no modificado
    np.testing.assert_array_equal(spectrum.binding_energy, energy)

def test_calibrate_spectrum_inplace():
    """Test calibración inplace."""
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.array([280.0, 284.0]),
        intensity=np.array([100, 200])
    )
    
    result = calibrate_spectrum(spectrum, "C", inplace=True)
    
    # Debe modificar el original
    assert result is spectrum
    assert spectrum.binding_energy[1] == pytest.approx(284.8, abs=0.1)

def test_calibrate_spectrum_invalid_element():
    """Test con elemento de referencia inválido."""
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.array([280.0, 284.0]),
        intensity=np.array([100, 200])
    )
    
    with pytest.raises(ValueError, match="Elemento.*no encontrado"):
        calibrate_spectrum(spectrum, "Xx")  # Elemento inexistente
```

### 2. Tests de Integración

**Propósito:** Testear interacción entre múltiples módulos.

**Ubicación:** `tests/integration/`

**Ejemplo:**

```python
# tests/integration/test_full_workflow.py
import pytest
from pathlib import Path
from xps_analyzer import (
    load_single_file,
    load_reference_database,
    calibrate_dataset
)
from xps_analyzer.preprocessing import subtract_background
from xps_analyzer.analysis import find_peaks

def test_complete_analysis_workflow(tmp_path):
    """Test workflow completo: carga -> calibración -> análisis."""
    # 1. Crear archivo de test
    test_file = tmp_path / "test_sample.txt"
    test_file.write_text("""
Sample Name test; Date 2023-01-01;
C 1s O 1s;
284.8 531.0;
Element C 1s; Region 1; Sweeps 5;
280.0 100
282.0 200
284.0 400
286.0 200
288.0 100
    """.strip())
    
    # 2. Cargar datos
    dataset = load_single_file(test_file)
    assert "C 1s" in dataset.spectra
    
    # 3. Calibrar
    calibrate_dataset(dataset, reference_element="C", inplace=True)
    
    # 4. Preprocesar
    spectrum = dataset.spectra["C 1s"]
    clean = subtract_background(spectrum, method="linear")
    
    # 5. Analizar
    peaks = find_peaks(clean, threshold=0.3)
    
    # 6. Verificar
    assert len(peaks) >= 1
    assert any(284.5 < p < 285.0 for p in peaks)  # Peak cerca de C 1s

def test_multi_region_dataset():
    """Test dataset con múltiples regiones."""
    # Implementación futura
    pass
```

### 3. Tests de Validación

**Propósito:** Verificar que validación de datos funciona correctamente.

**Ubicación:** `tests/unit/test_validation.py`

**Ejemplo:**

```python
# tests/unit/test_validation.py
import pytest
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum, XPSDataset

class TestXPSSpectrumValidation:
    """Tests de validación de XPSSpectrum."""
    
    def test_valid_spectrum(self):
        """Espectro válido debe crearse sin errores."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 281.0]),
            intensity=np.array([100.0, 200.0])
        )
        assert spectrum.region_name == "C 1s"
    
    def test_empty_arrays_raise_error(self):
        """Arrays vacíos deben lanzar ValueError."""
        with pytest.raises(ValueError, match="no pueden estar vacíos"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([]),
                intensity=np.array([])
            )
    
    def test_mismatched_lengths_raise_error(self):
        """Arrays con longitudes diferentes deben fallar."""
        with pytest.raises(ValueError, match="misma longitud"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([280.0, 281.0]),
                intensity=np.array([100.0])  # Solo 1 elemento
            )
    
    def test_negative_energies_raise_error(self):
        """Energías negativas deben fallar."""
        with pytest.raises(ValueError, match="valores positivos"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([-280.0, 281.0]),
                intensity=np.array([100.0, 200.0])
            )
    
    def test_empty_region_name_raise_error(self):
        """Nombre de región vacío debe fallar."""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            XPSSpectrum(
                region_name="",
                binding_energy=np.array([280.0]),
                intensity=np.array([100.0])
            )
    
    def test_whitespace_only_region_name_raise_error(self):
        """Nombre con solo espacios debe fallar."""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            XPSSpectrum(
                region_name="   ",
                binding_energy=np.array([280.0]),
                intensity=np.array([100.0])
            )

class TestXPSDatasetValidation:
    """Tests de validación de XPSDataset."""
    
    def test_empty_filename_raise_error(self):
        """Filename vacío debe fallar."""
        with pytest.raises(ValueError, match="filename no puede estar vacío"):
            XPSDataset(filename="", spectra={})
    
    def test_empty_spectra_raise_error(self):
        """Spectra vacío debe fallar."""
        with pytest.raises(ValueError, match="debe contener al menos un espectro"):
            XPSDataset(filename="test.txt", spectra={})
```

### 4. Tests Paramétricos

**Propósito:** Ejecutar mismo test con múltiples inputs.

**Ejemplo:**

```python
import pytest

@pytest.mark.parametrize("energy,expected_element", [
    (284.8, "C"),  # C 1s
    (531.0, "O"),  # O 1s
    (399.0, "N"),  # N 1s
    (102.0, "Si"), # Si 2p
])
def test_identify_element_by_energy(energy, expected_element):
    """Test identificación para múltiples elementos."""
    from xps_analyzer.reference_data import load_reference_database, identify_element
    
    db = load_reference_database()
    matches = db.find_element_by_energy(energy, tolerance=1.0)
    
    symbols = [symbol for symbol, _ in matches]
    assert expected_element in symbols

@pytest.mark.parametrize("method,expected_reduction", [
    ("shirley", 0.2),    # Shirley reduce ~20% de fondo
    ("tougaard", 0.15),  # Tougaard más conservador
    ("linear", 0.1),     # Linear mínimo
])
def test_background_subtraction_methods(method, expected_reduction):
    """Test diferentes métodos de sustracción de fondo."""
    # Implementación futura
    pass
```

### 5. Tests de Regresión

**Propósito:** Prevenir que bugs arreglados vuelvan a aparecer.

**Convención:** Agregar `# Regression test for Issue #XX` al docstring.

**Ejemplo:**

```python
def test_calibration_with_missing_reference_element():
    """
    Test calibración cuando elemento de referencia no existe en dataset.
    
    Regression test for Issue #42.
    Anteriormente lanzaba IndexError, ahora debe lanzar ValueError descriptivo.
    """
    from xps_analyzer.data_loader import XPSSpectrum, XPSDataset
    from xps_analyzer.preprocessing import calibrate_dataset
    
    # Dataset solo con O 1s (sin C 1s)
    o1s = XPSSpectrum(
        region_name="O 1s",
        binding_energy=np.array([528.0, 530.0, 532.0]),
        intensity=np.array([100, 200, 100])
    )
    dataset = XPSDataset(
        filename="test.txt",
        spectra={"O 1s": o1s}
    )
    
    # Intentar calibrar con C (que no existe)
    with pytest.raises(ValueError, match="Elemento de referencia.*no encontrado"):
        calibrate_dataset(dataset, reference_element="C")
```

---

## Estructura de Tests

### Organización de Archivos

```
tests/
├── conftest.py                    # Fixtures compartidos
├── unit/                          # Tests unitarios
│   ├── test_data_loader.py       # Carga de datos
│   ├── test_validation.py        # Validación de dataclasses
│   ├── test_calibration.py       # Calibración
│   ├── test_background.py        # Sustracción de fondo
│   ├── test_peak_fitting.py      # Ajuste de picos
│   └── test_reference_data.py    # Base de datos de referencia
├── integration/                   # Tests de integración
│   ├── test_full_workflow.py     # Workflows completos
│   └── test_multi_format.py      # Múltiples formatos (Fase 2)
├── fixtures/                      # Datos de prueba
│   ├── sample_data/
│   │   ├── simple_spectrum.txt
│   │   ├── multiplex.txt
│   │   └── survey.txt
│   └── expected_results/
│       └── fit_results.json
└── property/                      # Property-based tests (Fase 3)
    └── test_properties.py
```

### Convención de Nombres

```python
# Archivos: test_<módulo>.py
test_data_loader.py
test_calibration.py

# Clases (opcional): Test<Componente>
class TestXPSSpectrum:
    pass

# Funciones: test_<función>_<escenario>
def test_calibrate_spectrum_basic():
    pass

def test_calibrate_spectrum_inplace():
    pass

def test_calibrate_spectrum_invalid_element():
    pass
```

---

## Roadmap de Cobertura

### Fase 0 (Actual) - 20% Cobertura Objetivo

**Prioridad:** Validación básica + funcionalidad existente

```python
# tests/unit/test_validation.py - NUEVO
- TestXPSSpectrumValidation (8 tests)
- TestXPSDatasetValidation (4 tests)
- TestXPSSampleValidation (4 tests)

# tests/unit/test_data_loader.py - EXPANDIR
- test_parse_metadata_basic() [COMPLETADO] (existente)
- test_parse_metadata_header() [COMPLETADO] (existente)
- test_parse_metadata_invalid_format() <- NUEVO
- test_get_spectrum_data_basic() [COMPLETADO] (existente)
- test_get_spectrum_data_malformed_line_raises() [COMPLETADO] (existente)
- test_load_single_file_complete() <- NUEVO
- test_load_single_file_file_not_found() <- NUEVO

# tests/unit/test_calibration.py - NUEVO
- test_calibrate_spectrum_basic() (3 tests)
- test_calibrate_spectrum_inplace() (2 tests)
- test_calibrate_dataset() (2 tests)
- test_calibration_errors() (3 tests)

# tests/unit/test_reference_data.py - NUEVO
- test_load_reference_database() (1 test)
- test_find_element_by_energy() (3 tests)
- test_element_not_found() (1 test)
```

**Total Fase 0:** ~35 tests, 20% cobertura significativa

### Fase 1 - 87% Cobertura Alcanzado (SUPERADO)

**Prioridad:** Módulos core de análisis

```python
# tests/test_background.py - COMPLETADO
- test_shirley_background() (15 tests)
- test_tougaard_background() (10 tests)
- test_linear_background() (5 tests)
- 96% cobertura del módulo

# tests/test_peak_fitting.py - COMPLETADO
- test_fit_gaussian() (10 tests)
- test_fit_lorentzian() (10 tests)
- test_fit_voigt() (10 tests)
- test_fit_pseudo_voigt() (5 tests)
- test_fit_multiple_peaks() (10 tests)
- 95% cobertura del módulo

# tests/test_quantification.py - COMPLETADO
- test_load_sensitivity_factors() (15 tests)
- test_calculate_atomic_concentration() (20 tests)
- test_normalize_to_100() (8 tests)
- 85% cobertura del módulo

# tests/integration/test_full_workflow.py - PENDIENTE
- test_complete_analysis_workflow() (planeado)
- test_batch_processing() (planeado)
```

**Total Fase 1:** 208 tests total (118 tests nuevos), 87% cobertura (superando objetivo de 60%)

### Fase 2 - 85% Cobertura Objetivo

**Prioridad:** Múltiples formatos + exportación

```python
# tests/unit/test_export.py - NUEVO (Sesión 4)
- test_export_csv() (3 tests)
- test_export_excel() (3 tests)
- test_export_json() (2 tests)

# tests/integration/test_multi_format.py - NUEVO
- test_load_vamas() (5 tests)
- test_load_casa_xps() (5 tests)
- test_format_detection() (3 tests)

# tests/unit/test_pydantic_validation.py - NUEVO
- test_pydantic_spectrum_validation() (10 tests)
- test_pydantic_dataset_validation() (8 tests)
- test_json_serialization() (4 tests)
```

**Total Fase 2:** +43 tests -> ~251 tests total, 85% cobertura

### Fase 3 - 90% Cobertura Objetivo

**Prioridad:** Property-based testing + edge cases

```python
# tests/property/test_properties.py - NUEVO
- test_calibration_invariants() (usando hypothesis)
- test_background_subtraction_properties()
- test_peak_fitting_convergence()

# tests/performance/test_benchmarks.py - NUEVO
- test_load_large_file_performance()
- test_fit_many_peaks_performance()
```

**Total Fase 3:** +20 tests -> ~271 tests total, 90% cobertura

---

## Convenciones

### 1. Estructura AAA (Arrange-Act-Assert)

```python
def test_example():
    """Docstring explicando qué testea."""
    # Arrange: preparar datos y estado inicial
    spectrum = XPSSpectrum(...)
    expected_result = 42
    
    # Act: ejecutar la función a testear
    result = process_spectrum(spectrum)
    
    # Assert: verificar resultados
    assert result == expected_result
```

### 2. Nombres Descriptivos

```python
# [COMPLETADO] BUENO - nombre describe el escenario
def test_calibrate_spectrum_with_carbon_reference():
    pass

def test_fit_peaks_converges_with_good_initial_guess():
    pass

# [PENDIENTE] MALO - nombre genérico
def test_calibration():
    pass

def test_fit():
    pass
```

### 3. Un Assert por Concepto

```python
# [COMPLETADO] BUENO - cada assert verifica un concepto diferente
def test_calibrate_spectrum():
    calibrated = calibrate_spectrum(spectrum, "C")
    
    # Concepto 1: energías cambiaron correctamente
    assert calibrated.binding_energy[0] == pytest.approx(280.8)
    
    # Concepto 2: intensidades no cambiaron
    np.testing.assert_array_equal(calibrated.intensity, spectrum.intensity)
    
    # Concepto 3: original no modificado
    assert spectrum.binding_energy[0] == 280.0

# [PENDIENTE] MALO - demasiados asserts mezclados
def test_everything():
    assert a == 1
    assert b == 2
    assert c == 3
    assert d == 4
    # Si falla el primero, no sabemos si los demás pasan
```

### 4. Mensajes de Error Claros

```python
# [COMPLETADO] BUENO - mensaje explica qué se esperaba
def test_peak_count():
    peaks = find_peaks(spectrum)
    assert len(peaks) == 3, (
        f"Esperaba 3 picos en espectro C 1s, "
        f"pero encontró {len(peaks)}: {peaks}"
    )

# [PENDIENTE] MALO - sin mensaje
def test_peak_count():
    peaks = find_peaks(spectrum)
    assert len(peaks) == 3
```

### 5. Tests Independientes

```python
# [COMPLETADO] BUENO - cada test crea sus propios datos
def test_first():
    spectrum = create_test_spectrum()
    result = process(spectrum)
    assert result.success

def test_second():
    spectrum = create_test_spectrum()  # Nueva instancia
    result = process(spectrum)
    assert result.chi_squared < 1.0

# [PENDIENTE] MALO - compartir estado mutable
global_spectrum = create_test_spectrum()

def test_first():
    result = process(global_spectrum)  # Modifica global_spectrum
    assert result.success

def test_second():
    result = process(global_spectrum)  # Usa estado modificado!
    assert result.chi_squared < 1.0
```

---

## Fixtures y Helpers

### Fixtures Básicos

**Ubicación:** `tests/conftest.py`

```python
# tests/conftest.py
import pytest
import numpy as np
from pathlib import Path
from xps_analyzer.data_loader import XPSSpectrum, XPSDataset

@pytest.fixture
def simple_spectrum():
    """Espectro simple para tests rápidos."""
    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.linspace(280, 295, 100),
        intensity=np.random.rand(100) * 1000
    )

@pytest.fixture
def gaussian_peak_spectrum():
    """Espectro con pico gaussiano perfecto."""
    energy = np.linspace(280, 295, 200)
    intensity = 1000 * np.exp(-((energy - 284.8) ** 2) / (2 * 1.0 ** 2))
    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=energy,
        intensity=intensity
    )

@pytest.fixture
def sample_dataset(simple_spectrum):
    """Dataset completo con múltiples regiones."""
    o1s = XPSSpectrum(
        region_name="O 1s",
        binding_energy=np.linspace(525, 540, 100),
        intensity=np.random.rand(100) * 800
    )
    return XPSDataset(
        filename="test_sample.txt",
        header={"sample_name": "Test Sample", "date": "2023-01-01"},
        spectra={"C 1s": simple_spectrum, "O 1s": o1s}
    )

@pytest.fixture
def temp_data_file(tmp_path):
    """Archivo temporal con datos XPS."""
    file_path = tmp_path / "test_data.txt"
    file_path.write_text("""
Sample Name Test;
C 1s;
284.8;
Element C 1s; Region 1;
280.0 100
282.0 200
284.0 400
286.0 200
288.0 100
    """.strip())
    return file_path

@pytest.fixture
def reference_db():
    """Base de datos de referencia cacheada."""
    from xps_analyzer.reference_data import load_reference_database
    return load_reference_database()
```

### Helpers de Comparación

```python
# tests/conftest.py (continuación)

def assert_spectra_equal(spec1: XPSSpectrum, spec2: XPSSpectrum, rtol=1e-5):
    """Helper para comparar dos espectros."""
    assert spec1.region_name == spec2.region_name
    np.testing.assert_allclose(
        spec1.binding_energy,
        spec2.binding_energy,
        rtol=rtol
    )
    np.testing.assert_allclose(
        spec1.intensity,
        spec2.intensity,
        rtol=rtol
    )

def assert_peak_near(found_position: float, expected: float, tolerance: float = 0.5):
    """Helper para verificar posición de pico."""
    assert abs(found_position - expected) < tolerance, (
        f"Peak encontrado en {found_position} eV, "
        f"esperado cerca de {expected} eV (±{tolerance} eV)"
    )
```

---

## Testing de Validación

Ver sección "Tests de Validación" arriba para ejemplos completos.

**Estrategia:**
1. Test casos válidos (happy path)
2. Test cada tipo de error (empty, mismatch, negative, etc.)
3. Test edge cases (arrays de 1 elemento, valores extremos)

---

## Property-Based Testing

**Futuro (Fase 3):** Usar `hypothesis` para generar casos de test automáticamente.

```python
# tests/property/test_properties.py
from hypothesis import given, strategies as st
import hypothesis.extra.numpy as npst
import numpy as np
from xps_analyzer.preprocessing import calibrate_spectrum

@given(
    energy=npst.arrays(
        dtype=np.float64,
        shape=st.integers(min_value=10, max_value=1000),
        elements=st.floats(min_value=1.0, max_value=2000.0)
    ),
    shift=st.floats(min_value=-50.0, max_value=50.0)
)
def test_calibration_is_reversible(energy, shift):
    """Propiedad: calibrar y descalibrar debe retornar al original."""
    intensity = np.random.rand(len(energy))
    spectrum = XPSSpectrum(
        region_name="test",
        binding_energy=energy,
        intensity=intensity
    )
    
    # Calibrar con shift
    calibrated = calibrate_spectrum(spectrum, shift=shift, inplace=False)
    
    # Descalibrar
    uncalibrated = calibrate_spectrum(calibrated, shift=-shift, inplace=False)
    
    # Debe volver al original
    np.testing.assert_allclose(
        uncalibrated.binding_energy,
        spectrum.binding_energy,
        rtol=1e-10
    )

@given(
    spectrum_data=st.lists(
        st.floats(min_value=0.0, max_value=1e6),
        min_size=10,
        max_size=1000
    )
)
def test_background_subtraction_reduces_intensity(spectrum_data):
    """Propiedad: sustracción de fondo debe reducir intensidad total."""
    energy = np.linspace(280, 295, len(spectrum_data))
    spectrum = XPSSpectrum(
        region_name="test",
        binding_energy=energy,
        intensity=np.array(spectrum_data)
    )
    
    cleaned = subtract_background(spectrum, method="shirley")
    
    # Intensidad total debe reducirse
    assert cleaned.intensity.sum() < spectrum.intensity.sum()
```

---

## Comandos Útiles

### Ejecutar Tests

```bash
# Todos los tests
uv run pytest tests/

# Con verbose
uv run pytest tests/ -v

# Con cobertura
uv run pytest --cov=src --cov-report=html

# Ver reporte HTML
open htmlcov/index.html

# Test específico
uv run pytest tests/unit/test_calibration.py::test_calibrate_spectrum_basic -v

# Tests que coinciden con patrón
uv run pytest tests/ -k "calibration" -v

# Tests marcados (usando @pytest.mark.slow)
uv run pytest tests/ -m "not slow"

# Stop al primer fallo
uv run pytest tests/ -x

# Ver print statements
uv run pytest tests/ -s

# Modo verbose con prints
uv run pytest tests/ -vsx

# Ejecutar tests en paralelo (requiere pytest-xdist)
uv run pytest tests/ -n auto
```

### Cobertura Específica

```bash
# Cobertura de un módulo
uv run pytest --cov=src/xps_analyzer/data_loader --cov-report=term-missing

# Cobertura con branches
uv run pytest --cov=src --cov-branch --cov-report=html

# Cobertura mínima requerida (falla si < 80%)
uv run pytest --cov=src --cov-fail-under=80
```

### Debugging Tests

```bash
# Entrar a debugger en fallo
uv run pytest tests/ --pdb

# Entrar a debugger en cada test
uv run pytest tests/ --trace

# Ver output completo (sin captura)
uv run pytest tests/ --capture=no

# Ver warnings
uv run pytest tests/ -W all
```

### Watch Mode

```bash
# Instalar pytest-watch
uv add --group dev pytest-watch

# Ejecutar tests automáticamente al cambiar código
uv run ptw tests/
```

---

## Referencias

### Documentos Relacionados
- `DEVELOPMENT.md` - Workflow de desarrollo completo
- `ARCHITECTURE.md` - Arquitectura técnica
- `CONTRIBUTING.md` - Guía de contribución

### Herramientas
- **pytest** - https://docs.pytest.org/
- **pytest-cov** - https://pytest-cov.readthedocs.io/
- **hypothesis** - https://hypothesis.readthedocs.io/
- **pytest-xdist** - https://pytest-xdist.readthedocs.io/

### Best Practices
- **pytest good practices** - https://docs.pytest.org/en/stable/goodpractices.html
- **Testing Best Practices** - https://testdriven.io/blog/testing-best-practices/

---

**Última actualización:** Marzo 2026  
**Próxima revisión:** Después de completar Sesión 4 (Export System)  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
