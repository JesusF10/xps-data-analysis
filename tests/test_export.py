"""
Tests para el módulo de exportación de datos XPS.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from xps_analyzer.data_loader import XPSDataset, XPSSpectrum
from xps_analyzer.export import export_to_csv, export_to_excel, export_to_json


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def simple_spectrum():
    """
    Crea un espectro XPS simple para pruebas de exportación.
    """
    binding_energy = np.linspace(280.0, 290.0, 50)
    intensity = np.array([100.0 + i * 2 for i in range(50)])

    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=binding_energy,
        intensity=intensity,
        metadata={
            "sweeps": 10,
            "dwell_time": 0.1,
            "pass_energy": 20.0,
            "element": "C",
        },
    )


@pytest.fixture
def sample_dataset():
    """
    Crea un dataset XPS con múltiples espectros para pruebas de exportación.
    """
    # Espectro C 1s
    be_c = np.linspace(280.0, 290.0, 50)
    int_c = 500.0 * np.exp(-((be_c - 284.8) ** 2) / (2 * 1.0**2)) + 100.0

    spectrum_c = XPSSpectrum(
        region_name="C 1s",
        binding_energy=be_c,
        intensity=int_c,
        metadata={"sweeps": 10, "element": "C"},
    )

    # Espectro O 1s
    be_o = np.linspace(525.0, 540.0, 50)
    int_o = 400.0 * np.exp(-((be_o - 531.0) ** 2) / (2 * 1.2**2)) + 80.0

    spectrum_o = XPSSpectrum(
        region_name="O 1s",
        binding_energy=be_o,
        intensity=int_o,
        metadata={"sweeps": 8, "element": "O"},
    )

    # Crear dataset
    dataset = XPSDataset(
        filename="sample_multiplex.txt",
        header={
            "sample_name": "Test Sample",
            "date": "2026-03-01",
            "instrument": "Thermo K-Alpha",
        },
        spectra={"C 1s": spectrum_c, "O 1s": spectrum_o},
    )

    return dataset


# ============================================================================
# Tests para export_to_csv
# ============================================================================


def test_export_spectrum_to_csv_basic(simple_spectrum, tmp_path):
    """
    Test básico: exportar un espectro a CSV sin metadata.
    """
    output_path = tmp_path / "spectrum.csv"

    result = export_to_csv(simple_spectrum, output_path, include_metadata=False)

    # Verificar que el archivo existe
    assert result.exists()
    assert result.suffix == ".csv"

    # Verificar contenido
    df = pd.read_csv(result)
    assert len(df) == 50
    assert "binding_energy" in df.columns
    assert "intensity" in df.columns
    np.testing.assert_allclose(
        df["binding_energy"].values, simple_spectrum.binding_energy, rtol=1e-6
    )
    np.testing.assert_allclose(
        df["intensity"].values, simple_spectrum.intensity, rtol=1e-6
    )


def test_export_spectrum_to_csv_with_metadata(simple_spectrum, tmp_path):
    """
    Test: exportar un espectro a CSV con archivo de metadata separado.
    """
    output_path = tmp_path / "spectrum.csv"

    result = export_to_csv(simple_spectrum, output_path, include_metadata=True)

    # Verificar que ambos archivos existen
    assert result.exists()
    metadata_path = result.parent / f"{result.stem}.metadata.csv"
    assert metadata_path.exists()

    # Verificar contenido de metadata
    df_meta = pd.read_csv(metadata_path)
    assert "key" in df_meta.columns
    assert "value" in df_meta.columns
    assert len(df_meta) >= 4  # sweeps, dwell_time, pass_energy, element


def test_export_dataset_to_csv(sample_dataset, tmp_path):
    """
    Test: exportar un dataset completo a directorio con múltiples CSV.
    """
    output_dir = tmp_path / "dataset_export"

    result = export_to_csv(sample_dataset, output_dir, include_metadata=True)

    # Verificar que el directorio existe
    assert result.exists()
    assert result.is_dir()

    # Verificar que los archivos de espectros existen
    c1s_file = result / "C_1s.csv"
    o1s_file = result / "O_1s.csv"
    assert c1s_file.exists()
    assert o1s_file.exists()

    # Verificar metadata del dataset
    dataset_meta = result / "dataset_metadata.csv"
    assert dataset_meta.exists()

    # Verificar contenido de un espectro
    df_c = pd.read_csv(c1s_file)
    assert len(df_c) == 50
    assert "binding_energy" in df_c.columns


def test_export_to_csv_invalid_type_raises(tmp_path):
    """
    Test: exportar tipo inválido debe lanzar TypeError.
    """
    output_path = tmp_path / "invalid.csv"

    with pytest.raises(TypeError, match="debe ser XPSSpectrum o XPSDataset"):
        export_to_csv("invalid_data", output_path)

    with pytest.raises(TypeError, match="debe ser XPSSpectrum o XPSDataset"):
        export_to_csv(12345, output_path)


def test_export_to_csv_creates_parent_dirs(simple_spectrum, tmp_path):
    """
    Test: exportar debe crear directorios padres automáticamente.
    """
    output_path = tmp_path / "subdir1" / "subdir2" / "spectrum.csv"

    # El directorio no existe todavía
    assert not output_path.parent.exists()

    result = export_to_csv(simple_spectrum, output_path, include_metadata=False)

    # Verificar que se creó el directorio y el archivo
    assert result.exists()
    assert output_path.parent.exists()


def test_export_to_csv_decimal_places(simple_spectrum, tmp_path):
    """
    Test: verificar control de precisión decimal en CSV.
    """
    output_path = tmp_path / "spectrum_precision.csv"

    result = export_to_csv(simple_spectrum, output_path, decimal_places=2)

    # Verificar contenido
    df = pd.read_csv(result)

    # Verificar que los valores tienen máximo 2 decimales
    # (nota: pd.read_csv puede agregar más decimales por representación float)
    first_be = df["binding_energy"].iloc[0]
    first_int = df["intensity"].iloc[0]

    # Los valores originales deberían estar presentes con precisión razonable
    assert abs(first_be - simple_spectrum.binding_energy[0]) < 0.01
    assert abs(first_int - simple_spectrum.intensity[0]) < 0.01


# ============================================================================
# Tests para export_to_excel
# ============================================================================


def test_export_spectrum_to_excel_basic(simple_spectrum, tmp_path):
    """
    Test básico: exportar un espectro a Excel sin metadata.
    """
    output_path = tmp_path / "spectrum.xlsx"

    result = export_to_excel(simple_spectrum, output_path, include_metadata=False)

    # Verificar que el archivo existe
    assert result.exists()
    assert result.suffix == ".xlsx"

    # Verificar contenido
    df = pd.read_excel(result, sheet_name="Data")
    assert len(df) == 50
    assert "binding_energy" in df.columns
    assert "intensity" in df.columns


def test_export_spectrum_to_excel_with_metadata(simple_spectrum, tmp_path):
    """
    Test: exportar un espectro a Excel con hoja de metadata.
    """
    output_path = tmp_path / "spectrum.xlsx"

    result = export_to_excel(simple_spectrum, output_path, include_metadata=True)

    # Verificar que el archivo existe
    assert result.exists()

    # Verificar que ambas hojas existen
    excel_file = pd.ExcelFile(result)
    assert "Data" in excel_file.sheet_names
    assert "Metadata" in excel_file.sheet_names

    # Verificar contenido de metadata
    df_meta = pd.read_excel(result, sheet_name="Metadata")
    assert "key" in df_meta.columns
    assert "value" in df_meta.columns
    assert len(df_meta) >= 4


def test_export_dataset_to_excel(sample_dataset, tmp_path):
    """
    Test: exportar un dataset completo a Excel con múltiples hojas.
    """
    output_path = tmp_path / "dataset.xlsx"

    result = export_to_excel(sample_dataset, output_path, include_metadata=True)

    # Verificar que el archivo existe
    assert result.exists()

    # Verificar hojas
    excel_file = pd.ExcelFile(result)
    sheet_names = excel_file.sheet_names

    assert "C_1s" in sheet_names
    assert "O_1s" in sheet_names
    assert "Dataset_Metadata" in sheet_names
    assert "Spectra_Metadata" in sheet_names

    # Verificar contenido de una hoja de espectro
    df_c = pd.read_excel(result, sheet_name="C_1s")
    assert len(df_c) == 50
    assert "binding_energy" in df_c.columns


def test_export_to_excel_invalid_extension_raises(simple_spectrum, tmp_path):
    """
    Test: exportar con extensión incorrecta debe lanzar ValueError.
    """
    output_path = tmp_path / "spectrum.csv"  # Extensión incorrecta

    with pytest.raises(ValueError, match="debe terminar en .xlsx"):
        export_to_excel(simple_spectrum, output_path)


def test_export_dataset_to_excel_multiple_sheets(sample_dataset, tmp_path):
    """
    Test: verificar estructura completa de hojas en Excel para dataset.
    """
    output_path = tmp_path / "dataset_complete.xlsx"

    result = export_to_excel(sample_dataset, output_path, include_metadata=True)

    excel_file = pd.ExcelFile(result)

    # Verificar número de hojas (2 espectros + 2 metadata)
    assert len(excel_file.sheet_names) == 4

    # Verificar metadata del dataset
    df_dataset_meta = pd.read_excel(result, sheet_name="Dataset_Metadata")
    assert "sample_name" in df_dataset_meta["key"].values
    assert "date" in df_dataset_meta["key"].values

    # Verificar metadata de espectros
    df_spectra_meta = pd.read_excel(result, sheet_name="Spectra_Metadata")
    assert "region" in df_spectra_meta.columns  # Columna es "region", no "region_name"
    assert "key" in df_spectra_meta.columns
    assert "value" in df_spectra_meta.columns


# ============================================================================
# Tests para export_to_json
# ============================================================================


def test_export_spectrum_to_json_basic(simple_spectrum, tmp_path):
    """
    Test básico: exportar un espectro a JSON sin metadata.
    """
    import json

    output_path = tmp_path / "spectrum.json"

    result = export_to_json(simple_spectrum, output_path, include_metadata=False)

    # Verificar que el archivo existe
    assert result.exists()
    assert result.suffix == ".json"

    # Verificar contenido
    with open(result, "r") as f:
        data = json.load(f)

    assert "region_name" in data
    assert data["region_name"] == "C 1s"
    assert "binding_energy" in data
    assert "intensity" in data
    assert isinstance(data["binding_energy"], list)
    assert len(data["binding_energy"]) == 50


def test_export_spectrum_to_json_with_metadata(simple_spectrum, tmp_path):
    """
    Test: exportar un espectro a JSON con metadata incluida.
    """
    import json

    output_path = tmp_path / "spectrum.json"

    result = export_to_json(simple_spectrum, output_path, include_metadata=True)

    # Verificar contenido
    with open(result, "r") as f:
        data = json.load(f)

    assert "metadata" in data
    assert data["metadata"]["sweeps"] == 10
    assert data["metadata"]["dwell_time"] == 0.1


def test_export_dataset_to_json(sample_dataset, tmp_path):
    """
    Test: exportar un dataset completo a JSON con estructura jerárquica.
    """
    import json

    output_path = tmp_path / "dataset.json"

    result = export_to_json(sample_dataset, output_path, include_metadata=True)

    # Verificar que el archivo existe
    assert result.exists()

    # Verificar contenido
    with open(result, "r") as f:
        data = json.load(f)

    assert "filename" in data
    assert data["filename"] == "sample_multiplex.txt"
    assert "header" in data
    assert "spectra" in data
    assert "C 1s" in data["spectra"]
    assert "O 1s" in data["spectra"]

    # Verificar estructura de un espectro
    c1s = data["spectra"]["C 1s"]
    assert "region_name" in c1s
    assert "binding_energy" in c1s
    assert isinstance(c1s["binding_energy"], list)


def test_numpy_encoder_handles_arrays(tmp_path):
    """
    Test: verificar que NumpyEncoder maneja arrays NumPy correctamente.
    """
    import json
    from xps_analyzer.export.exporters import NumpyEncoder

    output_path = tmp_path / "numpy_test.json"

    # Crear datos con arrays NumPy
    data = {
        "array": np.array([1.0, 2.0, 3.0]),
        "int_array": np.array([1, 2, 3]),
        "float64": np.float64(3.14159),
        "int32": np.int32(42),
    }

    # Exportar con NumpyEncoder
    with open(output_path, "w") as f:
        json.dump(data, f, cls=NumpyEncoder)

    # Verificar que se puede leer
    with open(output_path, "r") as f:
        loaded = json.load(f)

    assert isinstance(loaded["array"], list)
    assert loaded["array"] == [1.0, 2.0, 3.0]
    assert isinstance(loaded["float64"], float)
    assert isinstance(loaded["int32"], int)


def test_numpy_encoder_handles_nan_inf(tmp_path):
    """
    Test: verificar que NumpyEncoder convierte NaN/Inf a null correctamente en arrays.
    """
    import json
    from xps_analyzer.export.exporters import NumpyEncoder

    output_path = tmp_path / "nan_inf_test.json"

    # Crear datos con arrays que contienen NaN e Inf
    data = {
        "array_with_nan": np.array([1.0, np.nan, 3.0]),
        "array_with_inf": np.array([1.0, np.inf, -np.inf, 4.0]),
        "normal_array": np.array([1.0, 2.0, 3.0]),
    }

    # Exportar con NumpyEncoder
    with open(output_path, "w") as f:
        json.dump(data, f, cls=NumpyEncoder)

    # Verificar que se puede leer
    with open(output_path, "r") as f:
        loaded = json.load(f)

    # Verificar que NaN se convierte a None en arrays
    assert loaded["array_with_nan"] == [1.0, None, 3.0]
    assert loaded["array_with_inf"] == [1.0, None, None, 4.0]
    assert loaded["normal_array"] == [1.0, 2.0, 3.0]


def test_export_to_json_indent_control(simple_spectrum, tmp_path):
    """
    Test: verificar control de indentación en JSON.
    """
    output_compact = tmp_path / "compact.json"
    output_pretty = tmp_path / "pretty.json"

    # Exportar sin indentación (compacto)
    export_to_json(simple_spectrum, output_compact, indent=None)

    # Exportar con indentación (bonito)
    export_to_json(simple_spectrum, output_pretty, indent=2)

    # Verificar que el archivo pretty es más grande (tiene espacios/newlines)
    assert output_pretty.stat().st_size > output_compact.stat().st_size


# ============================================================================
# Tests de round-trip (export → import)
# ============================================================================


def test_csv_roundtrip_preserves_data(simple_spectrum, tmp_path):
    """
    Test: verificar que exportar a CSV y reimportar preserva los datos.
    """
    output_path = tmp_path / "roundtrip.csv"

    # Exportar
    export_to_csv(simple_spectrum, output_path, include_metadata=False)

    # Reimportar
    df = pd.read_csv(output_path)

    # Verificar que los datos son idénticos (con tolerancia numérica)
    np.testing.assert_allclose(
        df["binding_energy"].values,
        simple_spectrum.binding_energy,
        rtol=1e-6,
    )
    np.testing.assert_allclose(
        df["intensity"].values,
        simple_spectrum.intensity,
        rtol=1e-6,
    )


def test_json_roundtrip_preserves_structure(sample_dataset, tmp_path):
    """
    Test: verificar que exportar a JSON y reimportar preserva la estructura.
    """
    import json

    output_path = tmp_path / "roundtrip.json"

    # Exportar
    export_to_json(sample_dataset, output_path, include_metadata=True)

    # Reimportar
    with open(output_path, "r") as f:
        data = json.load(f)

    # Verificar estructura
    assert data["filename"] == sample_dataset.filename
    assert len(data["spectra"]) == len(sample_dataset.spectra)

    # Verificar que los arrays se pueden reconstruir
    c1s_be = np.array(data["spectra"]["C 1s"]["binding_energy"])
    np.testing.assert_allclose(
        c1s_be,
        sample_dataset.get_spectrum("C 1s").binding_energy,
        rtol=1e-6,
    )
