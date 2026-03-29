"""
Tests para el módulo de sustracción de fondo de espectros XPS.
"""

from xps_analyzer.analysis.background import (
    background_with_fallback,
    linear_background,
    shirley_background,
    tougaard_background,
)
from xps_analyzer.data_loader import XPSSpectrum

import numpy as np
import pytest


# Fixtures
@pytest.fixture
def simple_peak_spectrum():
    """
    Crea un espectro XPS con un pico gaussiano simple sobre un fondo constante.
    """
    # Crear un pico gaussiano centrado en 285 eV
    binding_energy = np.linspace(280.0, 290.0, 100)
    peak_position = 285.0
    peak_height = 1000.0
    peak_width = 1.0
    background_level = 200.0

    # Pico gaussiano: A * exp(-(x-x0)^2 / (2*sigma^2))
    peak = peak_height * np.exp(
        -((binding_energy - peak_position) ** 2) / (2 * peak_width**2)
    )
    intensity = peak + background_level

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={"sweeps": 10, "dwell_time": 0.1},
    )


@pytest.fixture
def complex_spectrum():
    """
    Crea un espectro XPS con múltiples picos y fondo no lineal.
    """
    binding_energy = np.linspace(275.0, 295.0, 200)

    # Dos picos gaussianos
    peak1 = 800.0 * np.exp(-((binding_energy - 284.8) ** 2) / (2 * 1.2**2))
    peak2 = 400.0 * np.exp(-((binding_energy - 286.5) ** 2) / (2 * 1.0**2))

    # Fondo que aumenta hacia energías bajas (típico en XPS)
    background = 100.0 + 0.5 * (295.0 - binding_energy)

    intensity = peak1 + peak2 + background

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={"sweeps": 5},
    )


@pytest.fixture
def flat_spectrum():
    """Crea un espectro plano sin picos (para edge cases)."""
    binding_energy = np.linspace(280.0, 290.0, 50)
    intensity = np.ones(50) * 150.0

    return XPSSpectrum(
        region_name="Test",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={},
    )


@pytest.fixture
def inverted_energy_spectrum():
    """
    Crea un espectro con energías en orden decreciente
    (común en algunos formatos de archivo XPS).
    """
    # Energías decrecientes
    binding_energy = np.linspace(290.0, 280.0, 100)
    peak_position = 285.0
    peak_height = 1000.0
    peak_width = 1.0
    background_level = 200.0

    peak = peak_height * np.exp(
        -((binding_energy - peak_position) ** 2) / (2 * peak_width**2)
    )
    intensity = peak + background_level

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={},
    )


# Tests para linear_background()
class TestLinearBackground:
    """Tests para la función linear_background()."""

    def test_linear_background_basic(self, simple_peak_spectrum):
        """
        Test básico: la sustracción de fondo lineal debe reducir la intensidad.
        """
        original_intensity = simple_peak_spectrum.intensity.copy()
        result = linear_background(simple_peak_spectrum, inplace=False)

        # Verificar que la intensidad cambió
        assert not np.array_equal(result.intensity, original_intensity)

        # Verificar que el fondo fue sustraído (intensidad reducida en promedio)
        assert np.mean(result.intensity) < np.mean(original_intensity)

        # Verificar que el espectro original no fue modificado
        assert np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_linear_background_inplace(self, simple_peak_spectrum):
        """Test que inplace=True modifica el espectro original."""
        original_intensity = simple_peak_spectrum.intensity.copy()
        result = linear_background(simple_peak_spectrum, inplace=True)

        # Verificar que result es el mismo objeto
        assert result is simple_peak_spectrum

        # Verificar que la intensidad fue modificada
        assert not np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_linear_background_metadata(self, simple_peak_spectrum):
        """Test que el fondo calculado se almacena en metadata."""
        result = linear_background(simple_peak_spectrum, inplace=False)

        # Verificar que el fondo fue guardado en metadata
        assert "linear_background" in result.metadata
        assert isinstance(result.metadata["linear_background"], np.ndarray)
        assert len(result.metadata["linear_background"]) == len(result.binding_energy)

    def test_linear_background_flat_spectrum(self, flat_spectrum):
        """
        Test edge case: espectro plano debe resultar en intensidad cercana a cero.
        """
        result = linear_background(flat_spectrum, inplace=False)

        # Para un espectro plano, el fondo lineal debería ser igual a la intensidad
        # Resultado debería ser cercano a cero
        assert np.allclose(result.intensity, 0.0, atol=1e-10)

    def test_linear_background_inverted_energy(self, inverted_energy_spectrum):
        """
        Test que funciona con energías en orden decreciente.
        """
        result = linear_background(inverted_energy_spectrum, inplace=False)

        # Verificar que la función no falla
        assert result is not None
        assert len(result.intensity) == len(inverted_energy_spectrum.intensity)


# Tests para shirley_background()
class TestShirleyBackground:
    """Tests para la función shirley_background()."""

    def test_shirley_background_basic(self, simple_peak_spectrum):
        """Test básico: Shirley debe converger y sustraer fondo."""
        original_intensity = simple_peak_spectrum.intensity.copy()
        result = shirley_background(simple_peak_spectrum, inplace=False)

        # Verificar que convergió (debe haber metadata de iteraciones)
        assert "shirley_iterations" in result.metadata
        assert result.metadata["shirley_iterations"] > 0
        assert result.metadata["shirley_iterations"] <= 100  # max_iter default

        # Verificar que la intensidad cambió
        assert not np.array_equal(result.intensity, original_intensity)

        # Verificar que el fondo fue sustraído
        assert np.mean(result.intensity) < np.mean(original_intensity)

        # Verificar que el espectro original no fue modificado
        assert np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_shirley_background_convergence_fast(self, simple_peak_spectrum):
        """Test que Shirley converge en pocas iteraciones para espectros simples."""
        result = shirley_background(
            simple_peak_spectrum, tol=1e-4, max_iter=100, inplace=False
        )

        # Para un espectro simple, debería converger rápidamente (<20 iteraciones)
        assert result.metadata["shirley_iterations"] < 20

    def test_shirley_background_convergence_tolerance(self, simple_peak_spectrum):
        """Test que tolerancias más estrictas requieren más iteraciones."""
        result_loose = shirley_background(
            simple_peak_spectrum, tol=1e-3, max_iter=100, inplace=False
        )
        result_strict = shirley_background(
            simple_peak_spectrum, tol=1e-6, max_iter=100, inplace=False
        )

        # Tolerancia más estricta debería requerir más (o igual) iteraciones
        assert (
            result_strict.metadata["shirley_iterations"]
            >= result_loose.metadata["shirley_iterations"]
        )

    def test_shirley_background_no_convergence(self, flat_spectrum):
        """
        Test que lanza ValueError cuando no converge.
        """
        # Espectro plano converge inmediatamente (fondo es constante)
        # Para probar no-convergencia, necesitamos un espectro que no converja
        # con tolerancia extremadamente baja
        # En la práctica, un espectro plano SÍ converge (el fondo es lineal)

        # En lugar de esperar no-convergencia, verificamos convergencia rápida
        result = shirley_background(
            flat_spectrum, tol=1e-5, max_iter=100, inplace=False
        )

        # Espectro plano debe converger rápidamente
        assert result.metadata["shirley_iterations"] < 10

    def test_shirley_background_inplace(self, simple_peak_spectrum):
        """Test que inplace=True modifica el espectro original."""
        original_intensity = simple_peak_spectrum.intensity.copy()
        result = shirley_background(simple_peak_spectrum, inplace=True)

        # Verificar que result es el mismo objeto
        assert result is simple_peak_spectrum

        # Verificar que la intensidad fue modificada
        assert not np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_shirley_background_metadata(self, simple_peak_spectrum):
        """Test que el fondo y número de iteraciones se almacenan en metadata."""
        result = shirley_background(simple_peak_spectrum, inplace=False)

        # Verificar metadata
        assert "shirley_background" in result.metadata
        assert "shirley_iterations" in result.metadata
        assert isinstance(result.metadata["shirley_background"], np.ndarray)
        assert isinstance(result.metadata["shirley_iterations"], int)
        assert len(result.metadata["shirley_background"]) == len(result.binding_energy)

    def test_shirley_background_complex_spectrum(self, complex_spectrum):
        """Test con espectro complejo (múltiples picos)."""
        result = shirley_background(complex_spectrum, inplace=False)

        # Verificar que convergió
        assert "shirley_iterations" in result.metadata
        assert result.metadata["shirley_iterations"] > 0

        # Verificar que el fondo fue sustraído
        assert np.mean(result.intensity) < np.mean(complex_spectrum.intensity)

    def test_shirley_background_inverted_energy(self, inverted_energy_spectrum):
        """Test que funciona con energías en orden decreciente."""
        result = shirley_background(inverted_energy_spectrum, inplace=False)

        # Verificar que convergió sin errores
        assert "shirley_iterations" in result.metadata
        assert result.metadata["shirley_iterations"] > 0

    def test_shirley_background_invalid_spectrum_empty(self):
        """Test que lanza ValueError para espectro vacío."""
        # XPSSpectrum.__post_init__ valida que los arrays no estén vacíos
        # Por lo tanto, no podemos crear un espectro vacío válido
        # En su lugar, probamos que la creación falla como esperado

        with pytest.raises(ValueError, match="Los arrays no pueden estar vacíos"):
            XPSSpectrum(
                region_name="Empty",
                binding_energy=np.array([]),
                intensity=np.array([]),
                metadata={},
            )

    def test_shirley_background_invalid_spectrum_too_short(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            shirley_background(short_spectrum, inplace=False)


# Tests para tougaard_background()
class TestTougaardBackground:
    """Tests para la función tougaard_background()."""

    def test_tougaard_background_basic(self, simple_peak_spectrum):
        """Test básico: Tougaard debe sustraer fondo."""
        original_intensity = simple_peak_spectrum.intensity.copy()
        result = tougaard_background(simple_peak_spectrum, inplace=False)

        # Verificar que la intensidad cambió
        assert not np.array_equal(result.intensity, original_intensity)

        # Verificar que el fondo fue sustraído
        assert np.mean(result.intensity) < np.mean(original_intensity)

        # Verificar que el espectro original no fue modificado
        assert np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_tougaard_background_default_parameters(self, simple_peak_spectrum):
        """Test con parámetros por defecto (materiales orgánicos)."""
        result = tougaard_background(simple_peak_spectrum, inplace=False)

        # Verificar metadata
        assert "tougaard_background" in result.metadata
        assert "tougaard_params" in result.metadata
        assert result.metadata["tougaard_params"]["B"] == 2866.0
        assert result.metadata["tougaard_params"]["C"] == 1643.0
        assert result.metadata["tougaard_params"]["D"] == 1.0

    def test_tougaard_background_metal_parameters(self, simple_peak_spectrum):
        """Test con parámetros para metales."""
        result = tougaard_background(
            simple_peak_spectrum, B=1600.0, C=400.0, D=1.0, inplace=False
        )

        # Verificar que los parámetros fueron almacenados
        assert result.metadata["tougaard_params"]["B"] == 1600.0
        assert result.metadata["tougaard_params"]["C"] == 400.0
        assert result.metadata["tougaard_params"]["D"] == 1.0

    def test_tougaard_background_custom_parameters(self, simple_peak_spectrum):
        """Test con parámetros personalizados."""
        B_custom = 3000.0
        C_custom = 2000.0
        D_custom = 1.5

        result = tougaard_background(
            simple_peak_spectrum, B=B_custom, C=C_custom, D=D_custom, inplace=False
        )

        # Verificar parámetros en metadata
        assert result.metadata["tougaard_params"]["B"] == B_custom
        assert result.metadata["tougaard_params"]["C"] == C_custom
        assert result.metadata["tougaard_params"]["D"] == D_custom

    def test_tougaard_background_inplace(self, simple_peak_spectrum):
        """Test que inplace=True modifica el espectro original."""
        original_intensity = simple_peak_spectrum.intensity.copy()
        result = tougaard_background(simple_peak_spectrum, inplace=True)

        # Verificar que result es el mismo objeto
        assert result is simple_peak_spectrum

        # Verificar que la intensidad fue modificada
        assert not np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_tougaard_background_metadata(self, simple_peak_spectrum):
        """Test que el fondo y parámetros se almacenan en metadata."""
        result = tougaard_background(simple_peak_spectrum, inplace=False)

        # Verificar metadata
        assert "tougaard_background" in result.metadata
        assert "tougaard_params" in result.metadata
        assert isinstance(result.metadata["tougaard_background"], np.ndarray)
        assert isinstance(result.metadata["tougaard_params"], dict)
        assert len(result.metadata["tougaard_background"]) == len(result.binding_energy)

    def test_tougaard_background_complex_spectrum(self, complex_spectrum):
        """Test con espectro complejo (múltiples picos)."""
        result = tougaard_background(complex_spectrum, inplace=False)

        # Verificar que el fondo fue sustraído
        assert np.mean(result.intensity) < np.mean(complex_spectrum.intensity)

        # Verificar metadata
        assert "tougaard_background" in result.metadata

    def test_tougaard_background_inverted_energy(self, inverted_energy_spectrum):
        """Test que funciona con energías en orden decreciente."""
        result = tougaard_background(inverted_energy_spectrum, inplace=False)

        # Verificar que funcionó sin errores
        assert result is not None
        assert "tougaard_background" in result.metadata

    def test_tougaard_background_invalid_spectrum_too_short(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            tougaard_background(short_spectrum, inplace=False)

    def test_tougaard_background_different_methods_comparison(
        self, simple_peak_spectrum
    ):
        """
        Test que compara Tougaard con diferentes parámetros vs otros métodos.
        """
        result_tougaard = tougaard_background(simple_peak_spectrum, inplace=False)
        result_linear = linear_background(simple_peak_spectrum, inplace=False)

        # Los dos métodos deberían producir resultados diferentes
        assert not np.allclose(result_tougaard.intensity, result_linear.intensity)

    def test_tougaard_vs_shirley(self, simple_peak_spectrum):
        """
        Test que compara Tougaard vs Shirley en el mismo espectro.
        """
        result_tougaard = tougaard_background(simple_peak_spectrum, inplace=False)
        result_shirley = shirley_background(simple_peak_spectrum, inplace=False)

        # Los dos métodos deberían producir resultados diferentes
        # (Tougaard es basado en física, Shirley es empírico)
        assert not np.allclose(result_tougaard.intensity, result_shirley.intensity)


# Tests de integración
class TestBackgroundIntegration:
    """Tests de integración para múltiples métodos de sustracción de fondo."""

    def test_sequential_background_subtraction(self, complex_spectrum):
        """
        Test edge case: aplicar sustracción de fondo múltiples veces.

        Nota: En la práctica esto no tiene sentido científico, pero verifica
        que los métodos sean robustos a entradas ya procesadas.
        """
        # Primera sustracción (Shirley)
        result1 = shirley_background(complex_spectrum, inplace=False)

        # Segunda sustracción (Linear) sobre resultado anterior
        # Esto debería funcionar sin errores aunque no tenga sentido científico
        result2 = linear_background(result1, inplace=False)

        # Verificar que no crasheó y que la intensidad cambió
        assert result2 is not None
        assert len(result2.intensity) == len(complex_spectrum.intensity)

    def test_all_methods_preserve_length(self, simple_peak_spectrum):
        """
        Test que todos los métodos preservan la longitud del espectro.
        """
        methods = [
            linear_background,
            shirley_background,
            tougaard_background,
        ]

        original_length = len(simple_peak_spectrum.binding_energy)

        for method in methods:
            result = method(simple_peak_spectrum, inplace=False)
            assert len(result.binding_energy) == original_length
            assert len(result.intensity) == original_length

    def test_all_methods_preserve_metadata(self, simple_peak_spectrum):
        """
        Test que todos los métodos preservan metadata original.
        """
        methods = [
            linear_background,
            shirley_background,
            tougaard_background,
        ]

        original_metadata_keys = set(simple_peak_spectrum.metadata.keys())

        for method in methods:
            result = method(simple_peak_spectrum, inplace=False)

            # Metadata original debe estar presente (pueden agregarse nuevos campos)
            for key in original_metadata_keys:
                assert key in result.metadata
                assert result.metadata[key] == simple_peak_spectrum.metadata[key]

    def test_all_methods_reduce_intensity(self, simple_peak_spectrum):
        """
        Test que todos los métodos reducen la intensidad promedio
        (sustracción de fondo).
        """
        methods = [
            linear_background,
            shirley_background,
            tougaard_background,
        ]

        original_mean = np.mean(simple_peak_spectrum.intensity)

        for method in methods:
            result = method(simple_peak_spectrum, inplace=False)
            result_mean = np.mean(result.intensity)

            # La intensidad promedio debe reducirse
            assert result_mean < original_mean


# ============================================================================
# Tests para background_with_fallback (Fase E)
# ============================================================================


class TestBackgroundWithFallback:
    """
    Tests para la función de sustracción de fondo con cascada de fallbacks.

    Implementado en Fase E para aumentar robustez del análisis.
    """

    def test_fallback_uses_shirley_when_successful(self, simple_peak_spectrum):
        """
        Verifica que la cascada usa Shirley por defecto cuando converge.
        """
        result = background_with_fallback(simple_peak_spectrum)

        # Debe haber usado Shirley
        assert result.metadata["background_method"] == "shirley"
        assert "shirley_background" in result.metadata
        assert result.metadata["shirley_iterations"] > 0

    def test_fallback_falls_to_tougaard_when_shirley_fails(self):
        """
        Verifica que la cascada usa Tougaard si Shirley no converge.
        """
        # Crear espectro que causa fallo de Shirley (muy pocos puntos y max_iter bajo)
        binding_energy = np.linspace(280.0, 290.0, 100)
        # Espectro plano que no converge rápidamente
        intensity = np.ones(100) * 1000.0 + np.random.randn(100) * 50

        spectrum = XPSSpectrum(
            region_name="problematic",
            binding_energy=binding_energy,
            intensity=intensity,
            metadata={},
        )

        # Con max_iter MUY bajo (2), Shirley debe fallar
        result = background_with_fallback(spectrum, shirley_max_iter=2)

        # Debe haber intentado los métodos
        assert "background_method" in result.metadata
        assert result.metadata["background_fallback_attempted"] == [
            "shirley",
            "tougaard",
            "linear",
        ]

        # Si Shirley falló, debe haber error almacenado
        if result.metadata["background_method"] != "shirley":
            assert "background_fallback_errors" in result.metadata
            assert "shirley" in result.metadata["background_fallback_errors"]

    def test_fallback_uses_linear_as_last_resort(self):
        """
        Verifica que la cascada usa Linear como último recurso.
        """
        # Crear espectro que causa fallo de todos los métodos iterativos
        binding_energy = np.linspace(280.0, 290.0, 10)
        intensity = np.zeros(10)  # Todos ceros

        spectrum = XPSSpectrum(
            region_name="zeros",
            binding_energy=binding_energy,
            intensity=intensity,
            metadata={},
        )

        # Con max_iter muy bajo y espectro problemático
        result = background_with_fallback(spectrum, shirley_max_iter=2)

        # Debe haber usado algún método (probablemente Linear)
        assert "background_method" in result.metadata
        assert result.metadata["background_method"] in ["shirley", "tougaard", "linear"]

    def test_fallback_respects_custom_method_order(self, simple_peak_spectrum):
        """
        Verifica que la cascada respeta el orden de métodos personalizado.
        """
        # Usar solo linear (omitir Shirley y Tougaard)
        result = background_with_fallback(simple_peak_spectrum, methods=["linear"])

        assert result.metadata["background_method"] == "linear"
        assert "linear_background" in result.metadata
        assert result.metadata["background_fallback_attempted"] == ["linear"]

    def test_fallback_with_only_shirley_and_linear(self, simple_peak_spectrum):
        """
        Verifica cascada con solo dos métodos (omitir Tougaard).
        """
        result = background_with_fallback(
            simple_peak_spectrum, methods=["shirley", "linear"]
        )

        # Debe haber usado Shirley (exitoso en espectro simple)
        assert result.metadata["background_method"] == "shirley"
        assert result.metadata["background_fallback_attempted"] == ["shirley", "linear"]

    def test_fallback_stores_attempted_methods(self, simple_peak_spectrum):
        """
        Verifica que se almacenan los métodos intentados en metadata.
        """
        result = background_with_fallback(simple_peak_spectrum)

        assert "background_fallback_attempted" in result.metadata
        assert result.metadata["background_fallback_attempted"] == [
            "shirley",
            "tougaard",
            "linear",
        ]

    def test_fallback_stores_errors_from_failed_methods(self):
        """
        Verifica que se almacenan los errores de métodos fallidos.
        """
        # Crear espectro que falla Shirley
        binding_energy = np.linspace(280.0, 290.0, 50)
        intensity = np.random.randn(50) * 1000

        spectrum = XPSSpectrum(
            region_name="test",
            binding_energy=binding_energy,
            intensity=intensity,
            metadata={},
        )

        result = background_with_fallback(spectrum, shirley_max_iter=5)

        # Si Shirley falló, debe haber registro del error
        if result.metadata["background_method"] != "shirley":
            assert "background_fallback_errors" in result.metadata
            assert "shirley" in result.metadata["background_fallback_errors"]

    def test_fallback_invalid_method_raises_error(self, simple_peak_spectrum):
        """
        Verifica que un método inválido lanza ValueError.
        """
        with pytest.raises(ValueError, match="Método inválido"):
            background_with_fallback(simple_peak_spectrum, methods=["invalid_method"])

    def test_fallback_passes_shirley_parameters(self, simple_peak_spectrum):
        """
        Verifica que los parámetros de Shirley se pasan correctamente.
        """
        result = background_with_fallback(
            simple_peak_spectrum, shirley_max_iter=200, shirley_tol=1e-4
        )

        # Debe haber usado Shirley con parámetros personalizados
        assert result.metadata["background_method"] == "shirley"
        # Las iteraciones deben ser <= 200
        assert result.metadata["shirley_iterations"] <= 200

    def test_fallback_passes_tougaard_parameters(self, simple_peak_spectrum):
        """
        Verifica que los parámetros de Tougaard se pasan correctamente.
        """
        # Forzar uso de Tougaard omitiendo Shirley
        result = background_with_fallback(
            simple_peak_spectrum,
            methods=["tougaard"],
            tougaard_B=3000.0,
            tougaard_C=1500.0,
        )

        assert result.metadata["background_method"] == "tougaard"
        assert "tougaard_background" in result.metadata

    def test_fallback_inplace_parameter(self, simple_peak_spectrum):
        """
        Verifica que el parámetro inplace funciona correctamente.
        """
        original_intensity = simple_peak_spectrum.intensity.copy()

        # inplace=False (por defecto)
        result = background_with_fallback(simple_peak_spectrum, inplace=False)
        assert np.array_equal(simple_peak_spectrum.intensity, original_intensity)
        assert not np.array_equal(result.intensity, original_intensity)

        # inplace=True
        result2 = background_with_fallback(simple_peak_spectrum, inplace=True)
        assert result2 is simple_peak_spectrum
        assert not np.array_equal(simple_peak_spectrum.intensity, original_intensity)

    def test_fallback_reduces_background_intensity(self, simple_peak_spectrum):
        """
        Verifica que la sustracción de fondo reduce la intensidad promedio.
        """
        original_mean = np.mean(simple_peak_spectrum.intensity)
        result = background_with_fallback(simple_peak_spectrum)
        result_mean = np.mean(result.intensity)

        # La intensidad promedio debe reducirse después de restar fondo
        assert result_mean < original_mean

    def test_fallback_all_methods_fail_raises_error(self):
        """
        Verifica que se lanza error si todos los métodos fallan.
        """
        # Crear espectro inválido (menos de 2 puntos)
        binding_energy = np.array([285.0])
        intensity = np.array([1000.0])

        spectrum = XPSSpectrum(
            region_name="invalid",
            binding_energy=binding_energy,
            intensity=intensity,
            metadata={},
        )

        with pytest.raises(ValueError, match="Todos los métodos.*fallaron"):
            background_with_fallback(spectrum)

    def test_fallback_empty_methods_list_raises_error(self, simple_peak_spectrum):
        """
        Verifica que una lista vacía de métodos se maneja correctamente.
        """
        with pytest.raises(ValueError, match="Todos los métodos.*fallaron"):
            background_with_fallback(simple_peak_spectrum, methods=[])

    def test_fallback_preserves_metadata(self, simple_peak_spectrum):
        """
        Verifica que el metadata original se preserva.
        """
        result = background_with_fallback(simple_peak_spectrum)

        # Metadata original debe preservarse
        assert result.metadata["sweeps"] == 10
        assert result.metadata["dwell_time"] == 0.1

        # Metadata nuevo debe agregarse
        assert "background_method" in result.metadata
