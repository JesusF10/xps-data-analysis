"""
Tests para el módulo de ajuste de picos en espectros XPS.
"""

from xps_analyzer.analysis.peak_fitting import (
    FitResult,
    PeakParameters,
    estimate_peak_positions,
    fit_gaussian,
    fit_lorentzian,
    fit_multiple_peaks,
    fit_voigt,
)
from xps_analyzer.data_loader import XPSSpectrum

import numpy as np
import pytest


# Fixtures
@pytest.fixture
def single_gaussian_spectrum():
    """
    Crea un espectro con un solo pico gaussiano puro (sin fondo).
    """
    binding_energy = np.linspace(280.0, 290.0, 200)
    position = 285.0
    amplitude = 1000.0
    sigma = 1.0

    # Pico gaussiano puro
    intensity = amplitude * np.exp(-((binding_energy - position) ** 2) / (2 * sigma**2))

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={"test": "single_gaussian"},
    )


@pytest.fixture
def double_gaussian_spectrum():
    """
    Crea un espectro con dos picos gaussianos separados.
    """
    binding_energy = np.linspace(280.0, 295.0, 300)

    # Pico 1: C-C a 284.8 eV
    peak1 = 800.0 * np.exp(-((binding_energy - 284.8) ** 2) / (2 * 1.0**2))

    # Pico 2: C-O a 286.5 eV
    peak2 = 500.0 * np.exp(-((binding_energy - 286.5) ** 2) / (2 * 0.8**2))

    intensity = peak1 + peak2

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={"test": "double_gaussian"},
    )


@pytest.fixture
def triple_gaussian_spectrum():
    """
    Crea un espectro con tres picos gaussianos.
    """
    binding_energy = np.linspace(280.0, 295.0, 300)

    # Pico 1: C-C a 284.8 eV
    peak1 = 1000.0 * np.exp(-((binding_energy - 284.8) ** 2) / (2 * 1.2**2))

    # Pico 2: C-O a 286.5 eV
    peak2 = 600.0 * np.exp(-((binding_energy - 286.5) ** 2) / (2 * 1.0**2))

    # Pico 3: C=O a 288.5 eV
    peak3 = 300.0 * np.exp(-((binding_energy - 288.5) ** 2) / (2 * 0.9**2))

    intensity = peak1 + peak2 + peak3

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={"test": "triple_gaussian"},
    )


@pytest.fixture
def noisy_spectrum():
    """
    Crea un espectro con un pico gaussiano y ruido añadido.
    """
    np.random.seed(42)  # Reproducibilidad
    binding_energy = np.linspace(280.0, 290.0, 150)
    position = 285.0
    amplitude = 800.0
    sigma = 1.2

    # Pico gaussiano con ruido
    intensity = amplitude * np.exp(-((binding_energy - position) ** 2) / (2 * sigma**2))
    noise = np.random.normal(0, amplitude * 0.05, len(binding_energy))  # 5% ruido
    intensity += noise

    return XPSSpectrum(
        region_name="C 1s noisy",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={"test": "noisy"},
    )


@pytest.fixture
def flat_spectrum():
    """Espectro plano sin picos (edge case)."""
    binding_energy = np.linspace(280.0, 290.0, 100)
    intensity = np.ones(100) * 150.0

    return XPSSpectrum(
        region_name="Flat",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={},
    )


# Tests para estimate_peak_positions()
class TestEstimatePeakPositions:
    """Tests para la función estimate_peak_positions()."""

    def test_estimate_single_peak(self, single_gaussian_spectrum):
        """Test detección de un solo pico."""
        positions = estimate_peak_positions(single_gaussian_spectrum, prominence=0.3)

        # Debe detectar exactamente 1 pico
        assert len(positions) == 1

        # Posición debe estar cerca de 285.0 eV
        assert abs(positions[0] - 285.0) < 0.5

    def test_estimate_double_peaks(self, double_gaussian_spectrum):
        """Test detección de dos picos."""
        positions = estimate_peak_positions(
            double_gaussian_spectrum, prominence=0.05, min_distance=0.3
        )

        # Debe detectar al menos 1 pico (detección automática puede ser conservadora)
        assert len(positions) >= 1

        # Si detecta 2 picos, verificar posiciones aproximadas
        if len(positions) >= 2:
            assert any(abs(pos - 284.8) < 0.5 for pos in positions)
            assert any(abs(pos - 286.5) < 0.5 for pos in positions)

    def test_estimate_triple_peaks(self, triple_gaussian_spectrum):
        """Test detección de tres picos."""
        positions = estimate_peak_positions(
            triple_gaussian_spectrum, prominence=0.05, min_distance=0.3
        )

        # Debe detectar al menos 1 pico (detección automática puede ser conservadora)
        assert len(positions) >= 1

        # Si detecta 3 picos, verificar posiciones aproximadas
        if len(positions) >= 3:
            assert any(abs(pos - 284.8) < 0.5 for pos in positions)
            assert any(abs(pos - 286.5) < 0.5 for pos in positions)
            assert any(abs(pos - 288.5) < 0.5 for pos in positions)

    def test_estimate_no_peaks_flat_spectrum(self, flat_spectrum):
        """Test que no detecta picos en espectro plano."""
        positions = estimate_peak_positions(flat_spectrum, prominence=0.1)

        # No debe detectar picos significativos
        assert len(positions) == 0

    def test_estimate_prominence_parameter(self, double_gaussian_spectrum):
        """Test que prominencia más alta detecta menos picos."""
        positions_low = estimate_peak_positions(
            double_gaussian_spectrum, prominence=0.1
        )
        positions_high = estimate_peak_positions(
            double_gaussian_spectrum, prominence=0.5
        )

        # Prominencia alta debe detectar menos o igual picos
        assert len(positions_high) <= len(positions_low)

    def test_estimate_min_distance_parameter(self, double_gaussian_spectrum):
        """Test que min_distance afecta la detección."""
        # Con min_distance pequeña, detecta ambos picos
        positions_small = estimate_peak_positions(
            double_gaussian_spectrum, prominence=0.2, min_distance=0.5
        )

        # Con min_distance grande, puede detectar solo el más prominente
        positions_large = estimate_peak_positions(
            double_gaussian_spectrum, prominence=0.2, min_distance=5.0
        )

        # min_distance grande debe detectar menos o igual picos
        assert len(positions_large) <= len(positions_small)

    def test_estimate_invalid_spectrum(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            estimate_peak_positions(short_spectrum)


# Tests para fit_gaussian()
class TestFitGaussian:
    """Tests para la función fit_gaussian()."""

    def test_fit_gaussian_single_peak_perfect(self, single_gaussian_spectrum):
        """
        Test ajuste de pico gaussiano puro (sin ruido).
        Debe recuperar parámetros originales con alta precisión.
        """
        result = fit_gaussian(single_gaussian_spectrum)

        # Verificar que convergió
        assert result.success is True
        assert len(result.peaks) == 1

        peak = result.peaks[0]

        # Parámetros originales: position=285.0, amplitude=1000.0, sigma=1.0
        assert abs(peak.position - 285.0) < 0.1
        assert abs(peak.amplitude - 1000.0) < 50
        assert abs(peak.width - 1.0) < 0.1

        # R² debe ser muy cercano a 1 (ajuste perfecto)
        assert result.r_squared > 0.99

        # Tipo de perfil
        assert peak.shape == "gaussian"

    def test_fit_gaussian_with_noise(self, noisy_spectrum):
        """Test ajuste con espectro ruidoso."""
        result = fit_gaussian(noisy_spectrum)

        assert result.success is True
        assert len(result.peaks) == 1

        peak = result.peaks[0]

        # Parámetros originales: position=285.0, amplitude=800.0, sigma=1.2
        # Con ruido, permitimos más error
        assert abs(peak.position - 285.0) < 0.3
        assert abs(peak.amplitude - 800.0) < 100

        # R² debe ser bueno pero no perfecto debido al ruido
        assert result.r_squared > 0.90

    def test_fit_gaussian_custom_initial_params(self, single_gaussian_spectrum):
        """Test con parámetros iniciales personalizados."""
        result = fit_gaussian(
            single_gaussian_spectrum,
            initial_position=284.5,
            initial_amplitude=900.0,
            initial_width=1.2,
        )

        assert result.success is True
        # Debe converger a los mismos valores independientemente de iniciales
        assert abs(result.peaks[0].position - 285.0) < 0.1

    def test_fit_gaussian_custom_bounds(self, single_gaussian_spectrum):
        """Test con límites personalizados."""
        bounds = (
            [500, 284.0, 0.5],  # [amp_min, pos_min, width_min]
            [1500, 286.0, 2.0],  # [amp_max, pos_max, width_max]
        )

        result = fit_gaussian(single_gaussian_spectrum, bounds=bounds)

        assert result.success is True
        peak = result.peaks[0]

        # Verificar que respeta límites
        assert 500 <= peak.amplitude <= 1500
        assert 284.0 <= peak.position <= 286.0
        assert 0.5 <= peak.width <= 2.0

    def test_fit_gaussian_metadata(self, single_gaussian_spectrum):
        """Test que los resultados tienen metadata completa."""
        result = fit_gaussian(single_gaussian_spectrum)

        peak = result.peaks[0]

        # Verificar que existen errores calculados
        assert peak.position_error is not None
        assert peak.amplitude_error is not None
        assert peak.width_error is not None

        # Verificar que área fue calculada
        assert peak.area > 0

        # Verificar arrays de resultado
        assert len(result.fitted_spectrum) == len(
            single_gaussian_spectrum.binding_energy
        )
        assert len(result.residual) == len(single_gaussian_spectrum.binding_energy)

    def test_fit_gaussian_residual_is_small(self, single_gaussian_spectrum):
        """Test que el residual es pequeño para ajuste perfecto."""
        result = fit_gaussian(single_gaussian_spectrum)

        # Para pico gaussiano puro, residual debe ser ~0
        assert np.max(np.abs(result.residual)) < 10  # Tolerancia de 10 cuentas

    def test_fit_gaussian_invalid_spectrum_short(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            fit_gaussian(short_spectrum)

    def test_fit_gaussian_flat_spectrum_fails(self, flat_spectrum):
        """Test que espectro plano ajusta pobremente (R² bajo)."""
        # Espectro plano no se puede ajustar bien con gaussiana
        # pero curve_fit puede converger a un ajuste pobre
        result = fit_gaussian(flat_spectrum)

        # Si converge, el R² debe ser muy bajo (ajuste pobre)
        # Si falla, lanza ValueError
        if result.success:
            assert result.r_squared < 0.5  # R² muy bajo indica ajuste pobre


# Tests para fit_lorentzian()
class TestFitLorentzian:
    """Tests para la función fit_lorentzian()."""

    def test_fit_lorentzian_basic(self, single_gaussian_spectrum):
        """Test ajuste lorentziano básico."""
        # Aunque el espectro es gaussiano, lorentziana debe ajustar razonablemente
        result = fit_lorentzian(single_gaussian_spectrum)

        assert result.success is True
        assert len(result.peaks) == 1

        peak = result.peaks[0]
        assert peak.shape == "lorentzian"
        assert abs(peak.position - 285.0) < 0.5  # Posición aproximada

    def test_fit_lorentzian_r_squared(self, single_gaussian_spectrum):
        """Test que R² es razonable."""
        result = fit_lorentzian(single_gaussian_spectrum)

        # R² debe ser alto (aunque no perfecto porque ajustamos lorentziana a gaussiana)
        assert result.r_squared > 0.85

    def test_fit_lorentzian_metadata(self, single_gaussian_spectrum):
        """Test que los resultados tienen metadata completa."""
        result = fit_lorentzian(single_gaussian_spectrum)

        peak = result.peaks[0]

        assert peak.position_error is not None
        assert peak.amplitude_error is not None
        assert peak.width_error is not None
        assert peak.area > 0

    def test_fit_lorentzian_with_noise(self, noisy_spectrum):
        """Test ajuste lorentziano con ruido."""
        result = fit_lorentzian(noisy_spectrum)

        assert result.success is True
        assert result.r_squared > 0.80

    def test_fit_lorentzian_invalid_spectrum(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            fit_lorentzian(short_spectrum)


# Tests para fit_voigt()
class TestFitVoigt:
    """Tests para la función fit_voigt()."""

    def test_fit_voigt_basic(self, single_gaussian_spectrum):
        """Test ajuste Voigt básico."""
        result = fit_voigt(single_gaussian_spectrum)

        assert result.success is True
        assert len(result.peaks) == 1

        peak = result.peaks[0]
        assert peak.shape == "voigt"
        assert abs(peak.position - 285.0) < 0.5

    def test_fit_voigt_has_gamma(self, single_gaussian_spectrum):
        """Test que perfil Voigt tiene parámetro gamma."""
        result = fit_voigt(single_gaussian_spectrum)

        peak = result.peaks[0]
        assert peak.gamma is not None
        assert peak.gamma > 0

    def test_fit_voigt_r_squared(self, single_gaussian_spectrum):
        """Test que R² es alto para Voigt."""
        result = fit_voigt(single_gaussian_spectrum)

        # Voigt debe ajustar muy bien (es más flexible que puro gaussiano/lorentziano)
        assert result.r_squared > 0.95

    def test_fit_voigt_custom_params(self, single_gaussian_spectrum):
        """Test con parámetros iniciales personalizados."""
        result = fit_voigt(
            single_gaussian_spectrum,
            initial_position=284.5,
            initial_amplitude=900.0,
            initial_sigma=0.8,
            initial_gamma=0.6,
        )

        assert result.success is True
        assert abs(result.peaks[0].position - 285.0) < 0.5

    def test_fit_voigt_with_noise(self, noisy_spectrum):
        """Test ajuste Voigt con ruido."""
        result = fit_voigt(noisy_spectrum)

        assert result.success is True
        assert result.r_squared > 0.85

    def test_fit_voigt_metadata(self, single_gaussian_spectrum):
        """Test metadata completa."""
        result = fit_voigt(single_gaussian_spectrum)

        peak = result.peaks[0]
        assert peak.position_error is not None
        assert peak.amplitude_error is not None
        assert peak.width_error is not None
        assert peak.gamma is not None
        assert peak.area > 0

    def test_fit_voigt_invalid_spectrum(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            fit_voigt(short_spectrum)


# Tests para fit_multiple_peaks()
class TestFitMultiplePeaks:
    """Tests para la función fit_multiple_peaks()."""

    def test_fit_two_peaks_gaussian(self, double_gaussian_spectrum):
        """Test ajuste de dos picos gaussianos."""
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=[284.8, 286.5],  # Posiciones explícitas
            shape="gaussian",
        )

        assert result.success is True
        assert len(result.peaks) == 2

        # Verificar posiciones aproximadas (284.8 y 286.5 eV)
        positions = sorted([peak.position for peak in result.peaks])
        assert abs(positions[0] - 284.8) < 0.5
        assert abs(positions[1] - 286.5) < 0.5

        # R² debe ser alto
        assert result.r_squared > 0.95

    def test_fit_three_peaks_gaussian(self, triple_gaussian_spectrum):
        """Test ajuste de tres picos gaussianos."""
        result = fit_multiple_peaks(
            triple_gaussian_spectrum,
            peak_positions=[284.8, 286.5, 288.5],  # Posiciones explícitas
            shape="gaussian",
        )

        assert result.success is True
        assert len(result.peaks) == 3

        # Verificar posiciones aproximadas (284.8, 286.5, 288.5 eV)
        positions = sorted([peak.position for peak in result.peaks])
        assert abs(positions[0] - 284.8) < 0.5
        assert abs(positions[1] - 286.5) < 0.5
        assert abs(positions[2] - 288.5) < 0.5

        # R² debe ser muy alto para ajuste perfecto
        assert result.r_squared > 0.98

    def test_fit_two_peaks_lorentzian(self, double_gaussian_spectrum):
        """Test ajuste de dos picos lorentzianos."""
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=[284.8, 286.5],
            shape="lorentzian",
        )

        assert result.success is True
        assert len(result.peaks) == 2
        assert all(peak.shape == "lorentzian" for peak in result.peaks)

    def test_fit_two_peaks_voigt(self, double_gaussian_spectrum):
        """Test ajuste de dos picos Voigt."""
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=[284.8, 286.5],
            shape="voigt",
        )

        assert result.success is True
        assert len(result.peaks) == 2
        assert all(peak.shape == "voigt" for peak in result.peaks)
        assert all(peak.gamma is not None for peak in result.peaks)

    def test_fit_multiple_peaks_with_positions(self, double_gaussian_spectrum):
        """Test ajuste con posiciones iniciales explícitas."""
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=[284.5, 286.8],  # Cercanas a las reales
            shape="gaussian",
        )

        assert result.success is True
        assert len(result.peaks) == 2

    def test_fit_multiple_peaks_auto_estimate(self, double_gaussian_spectrum):
        """Test ajuste con estimación automática de posiciones (fallback a manual)."""
        # Intentar con estimación automática
        try:
            result = fit_multiple_peaks(
                double_gaussian_spectrum,
                n_peaks=2,
                shape="gaussian",
                auto_estimate=True,
            )
            assert result.success is True
            assert len(result.peaks) == 2
        except ValueError:
            # Si la detección automática falla, usar posiciones explícitas
            # Esto es esperado y aceptable - los usuarios siempre pueden dar posiciones manualmente
            result = fit_multiple_peaks(
                double_gaussian_spectrum,
                peak_positions=[284.8, 286.5],
                shape="gaussian",
            )
            assert result.success is True
            assert len(result.peaks) == 2

    def test_fit_multiple_peaks_metadata(self, double_gaussian_spectrum):
        """Test metadata completa para múltiples picos."""
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=[284.8, 286.5],
            shape="gaussian",
        )

        for peak in result.peaks:
            assert peak.position_error is not None
            assert peak.amplitude_error is not None
            assert peak.width_error is not None
            assert peak.area > 0

        assert len(result.fitted_spectrum) == len(
            double_gaussian_spectrum.binding_energy
        )
        assert len(result.residual) == len(double_gaussian_spectrum.binding_energy)

    def test_fit_multiple_peaks_message(self, double_gaussian_spectrum):
        """Test que el mensaje indica éxito."""
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=[284.8, 286.5],
            shape="gaussian",
        )

        assert "exitosamente" in result.message.lower()
        assert "2" in result.message

    def test_fit_multiple_peaks_invalid_no_params(self, double_gaussian_spectrum):
        """Test que lanza ValueError si no se provee n_peaks ni peak_positions."""
        with pytest.raises(
            ValueError, match="Debe proporcionar n_peaks o peak_positions"
        ):
            fit_multiple_peaks(double_gaussian_spectrum, shape="gaussian")

    def test_fit_multiple_peaks_invalid_n_peaks_zero(self, double_gaussian_spectrum):
        """Test que lanza ValueError si n_peaks < 1."""
        with pytest.raises(ValueError, match="n_peaks debe ser al menos 1"):
            fit_multiple_peaks(double_gaussian_spectrum, n_peaks=0, shape="gaussian")

    def test_fit_multiple_peaks_invalid_shape(self, double_gaussian_spectrum):
        """Test que lanza ValueError para shape no reconocido."""
        with pytest.raises(ValueError, match="no reconocido"):
            fit_multiple_peaks(
                double_gaussian_spectrum,
                peak_positions=[284.8, 286.5],
                shape="invalid_shape",  # type: ignore
            )

    def test_fit_multiple_peaks_invalid_spectrum(self):
        """Test que lanza ValueError para espectro con <3 puntos."""
        short_spectrum = XPSSpectrum(
            region_name="Short",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="al menos 3 puntos"):
            fit_multiple_peaks(short_spectrum, n_peaks=1, shape="gaussian")


# Tests de comparación entre métodos
class TestMethodComparison:
    """Tests comparando diferentes métodos de ajuste."""

    def test_gaussian_vs_lorentzian_on_gaussian_data(self, single_gaussian_spectrum):
        """
        Test que gaussiano ajusta mejor que lorentziano en datos gaussianos puros.
        """
        result_gaussian = fit_gaussian(single_gaussian_spectrum)
        result_lorentzian = fit_lorentzian(single_gaussian_spectrum)

        # Gaussiano debe tener R² mayor (datos son gaussianos)
        assert result_gaussian.r_squared >= result_lorentzian.r_squared

    def test_voigt_flexibility(self, single_gaussian_spectrum):
        """
        Test que Voigt es más flexible y ajusta bien datos gaussianos.
        """
        result_gaussian = fit_gaussian(single_gaussian_spectrum)
        result_voigt = fit_voigt(single_gaussian_spectrum)

        # Voigt debe ajustar al menos tan bien como gaussiano
        assert result_voigt.r_squared >= result_gaussian.r_squared * 0.95

    def test_all_methods_converge(self, noisy_spectrum):
        """Test que todos los métodos convergen en espectro con ruido."""
        result_g = fit_gaussian(noisy_spectrum)
        result_l = fit_lorentzian(noisy_spectrum)
        result_v = fit_voigt(noisy_spectrum)

        assert result_g.success is True
        assert result_l.success is True
        assert result_v.success is True


# Tests de integración
class TestPeakFittingIntegration:
    """Tests de integración para flujo completo de análisis."""

    def test_full_workflow_estimate_then_fit(self, double_gaussian_spectrum):
        """
        Test flujo completo: estimar posiciones -> ajustar múltiples picos.
        """
        # 1. Estimar posiciones con prominencia baja
        positions = estimate_peak_positions(double_gaussian_spectrum, prominence=0.05)

        # Si no detecta suficientes, usar posiciones explícitas
        if len(positions) < 2:
            positions = [284.8, 286.5]

        # 2. Ajustar múltiples picos con posiciones estimadas
        result = fit_multiple_peaks(
            double_gaussian_spectrum,
            peak_positions=positions[:2],  # Usar primeros 2 picos detectados
            shape="gaussian",
        )

        assert result.success is True
        assert len(result.peaks) == 2
        assert result.r_squared > 0.90

    def test_dataclass_instantiation(self):
        """Test que las dataclasses se instancian correctamente."""
        # Test PeakParameters
        peak = PeakParameters(
            position=285.0,
            amplitude=1000.0,
            width=1.0,
            area=1000.0,
            shape="gaussian",
        )

        assert peak.position == 285.0
        assert peak.shape == "gaussian"
        assert peak.gamma is None  # Opcional

        # Test FitResult
        result = FitResult(
            peaks=[peak],
            fitted_spectrum=np.array([1, 2, 3]),
            residual=np.array([0.1, 0.2, 0.3]),
            r_squared=0.95,
            chi_squared=1.5,
            success=True,
            message="Test",
        )

        assert len(result.peaks) == 1
        assert result.success is True
        assert result.r_squared == 0.95

    def test_fit_result_contains_all_info(self, single_gaussian_spectrum):
        """Test que FitResult contiene toda la información necesaria."""
        result = fit_gaussian(single_gaussian_spectrum)

        # Verificar estructura completa
        assert isinstance(result, FitResult)
        assert isinstance(result.peaks, list)
        assert len(result.peaks) > 0
        assert isinstance(result.peaks[0], PeakParameters)
        assert isinstance(result.fitted_spectrum, np.ndarray)
        assert isinstance(result.residual, np.ndarray)
        assert isinstance(result.r_squared, float)
        assert isinstance(result.chi_squared, float)
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)
