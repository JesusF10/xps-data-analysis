"""
Tests para el módulo de calibración de espectros XPS.
"""

from xps_analyzer.data_loader import XPSDataset, XPSSpectrum
from xps_analyzer.preprocessing.calibration import calibrate_sample, calibrate_spectrum
from xps_analyzer.reference_data import ElementReference, PhotoelectronLine

import numpy as np
import pytest


# Fixtures
@pytest.fixture
def simple_spectrum():
    """Crea un espectro XPS simple para testing."""
    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.array([280.0, 282.0, 284.0, 286.0, 288.0]),
        intensity=np.array([100.0, 200.0, 500.0, 300.0, 150.0]),
        metadata={"sweeps": 5, "dwell_time": 0.1},
    )


@pytest.fixture
def simple_dataset():
    """Crea un dataset XPS simple con múltiples espectros."""
    c1s_spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.array([280.0, 282.0, 284.0, 286.0, 288.0]),
        intensity=np.array([100.0, 200.0, 500.0, 300.0, 150.0]),
        metadata={"sweeps": 5},
    )

    o1s_spectrum = XPSSpectrum(
        region_name="O 1s",
        binding_energy=np.array([528.0, 530.0, 532.0, 534.0, 536.0]),
        intensity=np.array([150.0, 300.0, 400.0, 250.0, 100.0]),
        metadata={"sweeps": 5},
    )

    return XPSDataset(
        filename="test_sample.txt",
        header={"sample_name": "Test Sample", "date": "2024-01-01"},
        spectra={"C 1s": c1s_spectrum, "O 1s": o1s_spectrum},
    )


@pytest.fixture
def carbon_reference():
    """Crea una referencia de carbono para calibración."""
    return ElementReference(
        symbol="C",
        element="Carbon",
        atomic_number=6,
        photoelectron_lines=[
            PhotoelectronLine(
                line="1s",
                binding_energy=284.8,
                x_ray_source="Al_Ka",
                type="core",
            )
        ],
        compounds={},
        binding_energy_most_useful=284.8,  # C 1s carbono adventicio
        spin_orbital_splitting=None,
    )


@pytest.fixture
def oxygen_reference():
    """Crea una referencia de oxígeno para calibración."""
    return ElementReference(
        symbol="O",
        element="Oxygen",
        atomic_number=8,
        photoelectron_lines=[
            PhotoelectronLine(
                line="1s",
                binding_energy=531.0,
                x_ray_source="Al_Ka",
                type="core",
            )
        ],
        compounds={},
        binding_energy_most_useful=531.0,
        spin_orbital_splitting=None,
    )


# Tests para calibrate_spectrum
def test_calibrate_spectrum_inplace_false(simple_spectrum):
    """Test calibración sin modificar espectro original."""
    original_energy = simple_spectrum.binding_energy.copy()
    shift = 0.8  # Desplazamiento positivo

    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    # Verificar que el original no cambió
    np.testing.assert_array_equal(simple_spectrum.binding_energy, original_energy)

    # Verificar que el calibrado tiene el desplazamiento correcto
    expected = original_energy + shift
    np.testing.assert_array_almost_equal(calibrated.binding_energy, expected)


def test_calibrate_spectrum_inplace_true(simple_spectrum):
    """Test calibración modificando espectro original."""
    original_energy = simple_spectrum.binding_energy.copy()
    shift = -2.0  # Desplazamiento negativo

    result = calibrate_spectrum(simple_spectrum, shift, inplace=True)

    # Verificar que retorna None cuando inplace=True
    assert result is None

    # Verificar que el original cambió
    expected = original_energy + shift
    np.testing.assert_array_almost_equal(simple_spectrum.binding_energy, expected)


def test_calibrate_spectrum_negative_shift(simple_spectrum):
    """Test calibración con desplazamiento negativo."""
    shift = -1.5
    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    # Verificar que todas las energías se desplazaron correctamente
    expected = simple_spectrum.binding_energy + shift
    np.testing.assert_array_almost_equal(calibrated.binding_energy, expected)


# Tests para calibrate_sample
def test_calibrate_sample_basic(simple_dataset, carbon_reference):
    """Test calibración básica de dataset completo."""
    # El pico del espectro C 1s está en 284.0 eV (índice 2, intensidad 500.0)
    # La referencia está en 284.8 eV
    # Desplazamiento esperado: 284.8 - 284.0 = 0.8 eV

    calibrated = calibrate_sample(simple_dataset, carbon_reference, inplace=False)

    # Verificar que todos los espectros se calibraron
    for region_name in calibrated.spectra.keys():
        original_spectrum = simple_dataset.spectra[region_name]
        calibrated_spectrum = calibrated.spectra[region_name]

        expected_energy = original_spectrum.binding_energy + 0.8
        np.testing.assert_array_almost_equal(
            calibrated_spectrum.binding_energy, expected_energy, decimal=5
        )


def test_calibrate_sample_inplace_false(simple_dataset, carbon_reference):
    """Test que calibrate_sample no modifica el original cuando inplace=False."""
    original_c1s_energy = simple_dataset.spectra["C 1s"].binding_energy.copy()
    original_o1s_energy = simple_dataset.spectra["O 1s"].binding_energy.copy()

    calibrated = calibrate_sample(simple_dataset, carbon_reference, inplace=False)

    # Verificar que el original no cambió
    np.testing.assert_array_equal(
        simple_dataset.spectra["C 1s"].binding_energy, original_c1s_energy
    )
    np.testing.assert_array_equal(
        simple_dataset.spectra["O 1s"].binding_energy, original_o1s_energy
    )

    # Verificar que el calibrado es diferente
    assert not np.array_equal(
        calibrated.spectra["C 1s"].binding_energy, original_c1s_energy
    )


def test_calibrate_sample_inplace_true(simple_dataset, carbon_reference):
    """Test que calibrate_sample modifica el original cuando inplace=True."""
    original_c1s_energy = simple_dataset.spectra["C 1s"].binding_energy.copy()

    result = calibrate_sample(simple_dataset, carbon_reference, inplace=True)

    # Verificar que retorna None
    assert result is None

    # Verificar que el original cambió
    assert not np.array_equal(
        simple_dataset.spectra["C 1s"].binding_energy, original_c1s_energy
    )


def test_calibrate_sample_reference_not_found(simple_dataset):
    """Test error cuando elemento de referencia no existe en dataset."""
    # Crear referencia a elemento que no está en el dataset
    nitrogen_ref = ElementReference(
        symbol="N",
        element="Nitrogen",
        atomic_number=7,
        photoelectron_lines=[
            PhotoelectronLine(line="1s", binding_energy=399.0, type="core")
        ],
        compounds={},
        binding_energy_most_useful=399.0,
    )

    with pytest.raises(ValueError) as excinfo:
        calibrate_sample(simple_dataset, nitrogen_ref, inplace=False)

    # Verificar mensaje de error en español
    assert "Elemento de referencia 'N' no encontrado" in str(excinfo.value)
    assert "Regiones disponibles" in str(excinfo.value)


def test_calibrate_sample_no_binding_energy_most_useful(simple_dataset):
    """Test error cuando referencia no tiene binding_energy_most_useful."""
    # Crear referencia sin binding_energy_most_useful
    invalid_ref = ElementReference(
        symbol="C",
        element="Carbon",
        atomic_number=6,
        photoelectron_lines=[
            PhotoelectronLine(line="1s", binding_energy=284.8, type="core")
        ],
        compounds={},
        binding_energy_most_useful=None,  # ← Sin valor
    )

    with pytest.raises(ValueError) as excinfo:
        calibrate_sample(simple_dataset, invalid_ref, inplace=False)

    # Verificar mensaje de error en español
    assert "no tiene binding_energy_most_useful definido" in str(excinfo.value)


def test_calibrate_sample_all_spectra_calibrated(simple_dataset, carbon_reference):
    """Test que TODOS los espectros en el dataset son calibrados."""
    calibrated = calibrate_sample(simple_dataset, carbon_reference, inplace=False)

    # Verificar que todos los espectros están presentes
    assert set(calibrated.spectra.keys()) == set(simple_dataset.spectra.keys())

    # Verificar que cada espectro fue calibrado (diferente del original)
    for region_name in calibrated.spectra.keys():
        original = simple_dataset.spectra[region_name].binding_energy
        calibrated_energy = calibrated.spectra[region_name].binding_energy

        # No deben ser iguales (algún desplazamiento fue aplicado)
        assert not np.array_equal(original, calibrated_energy)


def test_calibrate_sample_with_oxygen_reference(simple_dataset, oxygen_reference):
    """Test calibración usando oxígeno como referencia."""
    # El pico del espectro O 1s está en 532.0 eV (índice 2, intensidad 400.0)
    # La referencia está en 531.0 eV
    # Desplazamiento esperado: 531.0 - 532.0 = -1.0 eV

    calibrated = calibrate_sample(simple_dataset, oxygen_reference, inplace=False)

    # Verificar desplazamiento correcto en espectro O 1s
    original_o1s = simple_dataset.spectra["O 1s"].binding_energy
    calibrated_o1s = calibrated.spectra["O 1s"].binding_energy

    expected = original_o1s - 1.0
    np.testing.assert_array_almost_equal(calibrated_o1s, expected, decimal=5)


# Tests adicionales para edge cases y validación
def test_calibrate_spectrum_zero_shift(simple_spectrum):
    """Test calibración con desplazamiento cero (no cambio)."""
    shift = 0.0
    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    # Verificar que las energías son idénticas
    np.testing.assert_array_equal(
        calibrated.binding_energy, simple_spectrum.binding_energy
    )

    # Verificar que las intensidades no cambiaron
    np.testing.assert_array_equal(calibrated.intensity, simple_spectrum.intensity)


def test_calibrate_spectrum_large_positive_shift(simple_spectrum):
    """Test calibración con desplazamiento grande positivo."""
    shift = 100.0
    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    expected = simple_spectrum.binding_energy + shift
    np.testing.assert_array_almost_equal(calibrated.binding_energy, expected)

    # Verificar que las energías resultantes son positivas
    assert np.all(calibrated.binding_energy > 0)


def test_calibrate_spectrum_large_negative_shift(simple_spectrum):
    """Test calibración con desplazamiento grande negativo."""
    shift = -100.0
    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    expected = simple_spectrum.binding_energy + shift
    np.testing.assert_array_almost_equal(calibrated.binding_energy, expected)


def test_calibrate_spectrum_preserves_intensity(simple_spectrum):
    """Test que calibración no modifica valores de intensidad."""
    shift = 2.5
    original_intensity = simple_spectrum.intensity.copy()

    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    # Verificar que intensidades son idénticas
    np.testing.assert_array_equal(calibrated.intensity, original_intensity)
    np.testing.assert_array_equal(simple_spectrum.intensity, original_intensity)


def test_calibrate_spectrum_preserves_metadata(simple_spectrum):
    """Test que calibración preserva metadata del espectro."""
    shift = 1.2
    calibrated = calibrate_spectrum(simple_spectrum, shift, inplace=False)

    # Verificar que metadata se copió correctamente
    assert calibrated.metadata == simple_spectrum.metadata
    assert calibrated.region_name == simple_spectrum.region_name


def test_calibrate_spectrum_single_point():
    """Test calibración con espectro de un solo punto."""
    single_point = XPSSpectrum(
        region_name="Test",
        binding_energy=np.array([284.0]),
        intensity=np.array([100.0]),
        metadata={},
    )

    shift = 0.8
    calibrated = calibrate_spectrum(single_point, shift, inplace=False)

    expected = np.array([284.8])
    np.testing.assert_array_almost_equal(calibrated.binding_energy, expected)


def test_calibrate_sample_empty_dataset():
    """Test calibración con dataset sin espectros."""
    empty_dataset = XPSDataset(
        filename="empty.txt",
        header={"sample_name": "Empty"},
        spectra={},
    )

    carbon_ref = ElementReference(
        symbol="C",
        element="Carbon",
        atomic_number=6,
        photoelectron_lines=[
            PhotoelectronLine(line="1s", binding_energy=284.8, type="core")
        ],
        compounds={},
        binding_energy_most_useful=284.8,
    )

    with pytest.raises(ValueError) as excinfo:
        calibrate_sample(empty_dataset, carbon_ref, inplace=False)

    assert "Elemento de referencia 'C' no encontrado" in str(excinfo.value)


def test_calibrate_sample_preserves_non_calibrated_metadata(
    simple_dataset, carbon_reference
):
    """Test que calibración preserva metadata del dataset (header)."""
    original_header = simple_dataset.header.copy()

    calibrated = calibrate_sample(simple_dataset, carbon_reference, inplace=False)

    # Verificar que el header se preserva
    assert calibrated.header == original_header
    assert calibrated.filename == simple_dataset.filename
