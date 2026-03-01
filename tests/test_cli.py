"""
Tests para el módulo CLI de XPS Analyzer.
"""

from unittest.mock import MagicMock, patch

from xps_analyzer.cli.main import analyze, cli, show_element
from xps_analyzer.data_loader import XPSDataset, XPSSpectrum
from xps_analyzer.reference_data import ElementReference, PhotoelectronLine

import pytest
from click.testing import CliRunner


# Fixtures
@pytest.fixture
def runner():
    """Crea un CliRunner para testing de comandos Click."""
    return CliRunner()


@pytest.fixture
def sample_dataset():
    """Crea un dataset XPS de ejemplo."""
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=[280.0, 282.0, 284.0, 286.0],
        intensity=[100.0, 200.0, 500.0, 300.0],
        metadata={"sweeps": 5},
    )

    return XPSDataset(
        filename="test_sample.txt",
        header={"sample_name": "Test", "date": "2024-01-01"},
        spectra={"C 1s": spectrum},
    )


@pytest.fixture
def carbon_element():
    """Crea una referencia de elemento carbono."""
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
        binding_energy_most_useful=284.8,
    )


# Tests para comando CLI principal
def test_cli_help(runner):
    """Test que el comando --help funciona."""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "XPS Analyzer" in result.output
    assert "Software para análisis de datos XPS" in result.output


def test_cli_version(runner):
    """Test que el comando --version funciona."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0


# Tests para comando analyze
@patch("xps_analyzer.cli.main.load_reference_database")
@patch("xps_analyzer.cli.main.load_single_file")
def test_analyze_basic(mock_load_file, mock_load_db, runner, sample_dataset, tmp_path):
    """Test comando analyze con archivo válido."""
    # Configurar mocks
    mock_load_file.return_value = sample_dataset
    mock_db = MagicMock()
    mock_load_db.return_value = mock_db

    # Crear archivo temporal
    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy content")

    # Ejecutar comando
    result = runner.invoke(analyze, [str(test_file)])

    # Verificar resultado
    assert result.exit_code == 0
    assert "Analizando conjunto" in result.output
    assert "Archivo cargado exitosamente" in result.output
    assert "Espectros encontrados" in result.output


@patch("xps_analyzer.cli.main.load_reference_database")
@patch("xps_analyzer.cli.main.load_single_file")
def test_analyze_shows_metadata(
    mock_load_file, mock_load_db, runner, sample_dataset, tmp_path
):
    """Test que analyze muestra metadata del archivo."""
    mock_load_file.return_value = sample_dataset
    mock_load_db.return_value = MagicMock()

    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy")

    result = runner.invoke(analyze, [str(test_file)])

    assert result.exit_code == 0
    assert "Metadatos" in result.output
    assert "sample_name" in result.output or "Test" in result.output


@patch("xps_analyzer.cli.main.load_reference_database")
@patch("xps_analyzer.cli.main.load_single_file")
def test_analyze_file_not_found(mock_load_file, mock_load_db, runner):
    """Test error cuando archivo no existe."""
    result = runner.invoke(analyze, ["nonexistent_file.txt"])

    # Click valida que el path existe antes de llamar a la función
    assert result.exit_code != 0


@patch("xps_analyzer.cli.main.load_reference_database")
@patch("xps_analyzer.cli.main.load_single_file")
def test_analyze_load_error(mock_load_file, mock_load_db, runner, tmp_path):
    """Test manejo de error al cargar archivo."""
    mock_load_file.side_effect = ValueError("Formato inválido")
    mock_load_db.return_value = MagicMock()

    test_file = tmp_path / "bad_file.txt"
    test_file.write_text("invalid content")

    result = runner.invoke(analyze, [str(test_file)])

    # Debe manejar el error y retornar exit_code != 0
    assert result.exit_code != 0
    assert "Error" in result.output


# Tests para comando show-element
@patch("xps_analyzer.cli.main.load_reference_database")
def test_show_element_basic(mock_load_db, runner, carbon_element):
    """Test comando show-element con elemento válido."""
    mock_db = MagicMock()
    mock_db.elements = {"C": carbon_element}
    mock_load_db.return_value = mock_db

    result = runner.invoke(show_element, ["C"])

    assert result.exit_code == 0
    assert "Información para el elemento: C" in result.output
    assert "Símbolo: C" in result.output
    assert "Nombre: Carbon" in result.output
    assert "Número atómico: 6" in result.output


@patch("xps_analyzer.cli.main.load_reference_database")
def test_show_element_shows_photoelectron_lines(mock_load_db, runner, carbon_element):
    """Test que show-element muestra líneas fotoelectrónicas."""
    mock_db = MagicMock()
    mock_db.elements = {"C": carbon_element}
    mock_load_db.return_value = mock_db

    result = runner.invoke(show_element, ["C"])

    assert result.exit_code == 0
    assert "Energías de enlace disponibles" in result.output


@patch("xps_analyzer.cli.main.load_reference_database")
def test_show_element_not_found(mock_load_db, runner):
    """Test error cuando elemento no existe en base de datos."""
    mock_db = MagicMock()
    mock_db.elements = {}
    mock_load_db.return_value = mock_db

    result = runner.invoke(show_element, ["Xx"])

    assert result.exit_code != 0
    assert "no encontrado" in result.output


@patch("xps_analyzer.cli.main.load_reference_database")
def test_show_element_verbose_flag(mock_load_db, runner, carbon_element):
    """Test flag verbose en comando show-element."""
    mock_db = MagicMock()
    mock_db.elements = {"C": carbon_element}
    mock_load_db.return_value = mock_db

    # Ejecutar con flag -v
    result = runner.invoke(show_element, ["C", "-v"])

    assert result.exit_code == 0
    assert "Información para el elemento: C" in result.output


@patch("xps_analyzer.cli.main.load_reference_database")
def test_show_element_shows_compounds(mock_load_db, runner):
    """Test que show-element muestra información de compuestos."""
    # Crear elemento con compuestos
    from xps_analyzer.reference_data import CompoundReference

    carbon_with_compounds = ElementReference(
        symbol="C",
        element="Carbon",
        atomic_number=6,
        photoelectron_lines=[
            PhotoelectronLine(line="1s", binding_energy=284.8, type="core")
        ],
        compounds={
            "Carbonato": CompoundReference(
                orbital="1s",
                binding_energy_range=(288.0, 290.0),
                peak_position=289.0,
                chemical_shift=4.2,
            )
        },
        binding_energy_most_useful=284.8,
    )

    mock_db = MagicMock()
    mock_db.elements = {"C": carbon_with_compounds}
    mock_load_db.return_value = mock_db

    result = runner.invoke(show_element, ["C"])

    assert result.exit_code == 0
    assert "Compuestos de referencia" in result.output
    assert "Carbonato" in result.output
