"""
Tests para el módulo de visualización de datos XPS.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from xps_analyzer.data_loader import XPSSpectrum
from xps_analyzer.visualization.plotting import plot_spectrum, plot_survey_spectrum


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
def survey_spectrum():
    """Crea un espectro survey para testing."""
    # Survey con rango amplio de energías
    energy_range = np.linspace(0, 1200, 1200)
    intensity = np.random.random(1200) * 1000

    return XPSSpectrum(
        region_name="survey",
        binding_energy=energy_range,
        intensity=intensity,
        metadata={"sweeps": 3, "type": "survey"},
    )


# Tests para plot_spectrum
@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt.figure")
def test_plot_spectrum_basic(mock_figure, mock_show, simple_spectrum):
    """Test que plot_spectrum ejecuta sin errores."""
    plot_spectrum(simple_spectrum)

    # Verificar que se llamó figure y show
    mock_figure.assert_called_once_with(figsize=(8, 6))
    mock_show.assert_called_once()


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt.plot")
def test_plot_spectrum_calls_plot(mock_plot, mock_show, simple_spectrum):
    """Test que plot_spectrum llama a plt.plot con los datos correctos."""
    plot_spectrum(simple_spectrum)

    # Verificar que plt.plot fue llamado
    mock_plot.assert_called_once()

    # Verificar que show fue llamado
    mock_show.assert_called_once()


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_spectrum_inverts_xaxis(mock_plt, mock_show, simple_spectrum):
    """Test que plot_spectrum invierte el eje X (convención XPS)."""
    mock_gca = MagicMock()
    mock_plt.gca.return_value = mock_gca

    plot_spectrum(simple_spectrum)

    # Verificar que se llamó invert_xaxis
    mock_gca.invert_xaxis.assert_called_once()


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_spectrum_custom_title(mock_plt, mock_show, simple_spectrum):
    """Test que plot_spectrum acepta título personalizado."""
    custom_title = "Mi Espectro Personalizado"
    plot_spectrum(simple_spectrum, title=custom_title)

    # Verificar que se llamó title con el valor correcto
    mock_plt.title.assert_called_once_with(custom_title)


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_spectrum_default_title(mock_plt, mock_show, simple_spectrum):
    """Test que plot_spectrum usa título por defecto."""
    plot_spectrum(simple_spectrum)

    # Verificar que se llamó title con el valor por defecto
    mock_plt.title.assert_called_once_with("Espectro XPS")


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_spectrum_sets_labels(mock_plt, mock_show, simple_spectrum):
    """Test que plot_spectrum configura etiquetas de ejes en español."""
    plot_spectrum(simple_spectrum)

    # Verificar que se llamaron xlabel y ylabel
    mock_plt.xlabel.assert_called_once_with("Energía de enlace (eV)")
    mock_plt.ylabel.assert_called_once_with("Intensidad")


# Tests para plot_survey_spectrum
@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt.figure")
def test_plot_survey_spectrum_basic(mock_figure, mock_show, survey_spectrum):
    """Test que plot_survey_spectrum ejecuta sin errores."""
    plot_survey_spectrum(survey_spectrum)

    # Verificar que se llamó figure con tamaño correcto
    mock_figure.assert_called_once_with(figsize=(10, 6))
    mock_show.assert_called_once()


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_survey_spectrum_inverts_xaxis(mock_plt, mock_show, survey_spectrum):
    """Test que plot_survey_spectrum invierte el eje X."""
    mock_gca = MagicMock()
    mock_plt.gca.return_value = mock_gca

    plot_survey_spectrum(survey_spectrum)

    # Verificar que se llamó invert_xaxis
    mock_gca.invert_xaxis.assert_called_once()


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_survey_spectrum_custom_title(mock_plt, mock_show, survey_spectrum):
    """Test que plot_survey_spectrum acepta título personalizado."""
    custom_title = "Survey Completo"
    plot_survey_spectrum(survey_spectrum, title=custom_title)

    # Verificar que se llamó title con el valor correcto
    mock_plt.title.assert_called_once_with(custom_title)


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_survey_spectrum_default_title(mock_plt, mock_show, survey_spectrum):
    """Test que plot_survey_spectrum usa título por defecto."""
    plot_survey_spectrum(survey_spectrum)

    # Verificar que se llamó title con el valor por defecto
    mock_plt.title.assert_called_once_with("Espectro Survey XPS")


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt")
def test_plot_survey_spectrum_sets_labels(mock_plt, mock_show, survey_spectrum):
    """Test que plot_survey_spectrum configura etiquetas en español."""
    plot_survey_spectrum(survey_spectrum)

    # Verificar que se llamaron xlabel y ylabel
    mock_plt.xlabel.assert_called_once_with("Energía de enlace (eV)")
    mock_plt.ylabel.assert_called_once_with("Intensidad")


@patch("xps_analyzer.visualization.plotting.plt.show")
@patch("xps_analyzer.visualization.plotting.plt.plot")
def test_plot_survey_spectrum_uses_orange_color(mock_plot, mock_show, survey_spectrum):
    """Test que plot_survey_spectrum usa color naranja."""
    plot_survey_spectrum(survey_spectrum)

    # Verificar que plt.plot fue llamado con color='orange'
    mock_plot.assert_called_once()
    call_kwargs = mock_plot.call_args[1]
    assert call_kwargs.get("color") == "orange"
