from pathlib import Path

import numpy as np
import pytest

from xps_analyzer.data_loader.core import (
    XPSSpectrum,
    detect_file_format,
    get_spectrum_data,
    load_all_data,
    parse_metadata,
)


def test_parse_metadata_header_basic():
    """
    Caso básico para header=True (tres líneas: meta, elementos, energías).
    Verifica que devuelva claves normalizadas y la estructura 'elements'.
    """
    lines = [
        "Sample Name Sample1; Date 2023-10-01; Operator John Doe;",
        "C 1s O 1s N 1s;",
        "284.8 531.0 399.0;",
    ]
    meta = parse_metadata(lines, header=True)

    assert "Sample_Name" in meta
    assert meta["Sample_Name"] == "Sample1"
    assert "Date" in meta and meta["Date"] == "2023-10-01"

    assert "elements" in meta and isinstance(meta["elements"], dict)
    elems = meta["elements"]
    assert "C" in elems and elems["C"]["orbital"] == "1s"
    assert elems["C"]["mean_energy"] == "284.8"


def test_parse_metadata_spectrum_basic():
    """
    Caso básico para metadata de espectro (línea única con ; delimitando campos).
    """
    line = "Element C 1s; Region 1; Depth Cycle 1 of 3; Time Per Step 50; Sweeps 5; Anode Al Kα; Photon energy 1486.6;"
    meta = parse_metadata(line, header=False)
    assert meta["element"] == "C 1s"
    assert meta["region"] == 1
    assert meta["depth_cycle"] == (1, 3)
    assert meta["time_per_step"] == 50
    assert meta["sweeps"] == 5
    assert pytest.approx(meta["photon_energy"], rel=1e-6) == 1486.6


def test_get_spectrum_data_basic():
    """
    Construye un espectro sencillo: primera línea metadata, luego pares BE intensity.
    Verifica que retorne un XPSSpectrum con arrays numéricos correctos.
    """
    data_lines = [
        "Element C 1s; Region 1; Depth Cycle 1 of 3; Time Per Step 50; Sweeps 5; Anode Al Kα; Photon energy 1486.6;",
        "284.8 100.0",
        "285.0 120.0",
        "286.0 80.0",
    ]
    spec = get_spectrum_data(data_lines)
    assert isinstance(spec, XPSSpectrum)
    assert spec.region_name == "C 1s"
    # Checar arrays
    np.testing.assert_allclose(spec.binding_energy, np.array([284.8, 285.0, 286.0]))
    np.testing.assert_allclose(spec.intensity, np.array([100.0, 120.0, 80.0]))
    # DataFrame property
    df = spec.data
    assert list(df.index) == [284.8, 285.0, 286.0]
    assert list(df["intensity"].values) == [100.0, 120.0, 80.0]


def test_get_spectrum_data_malformed_line_raises():
    """
    Si alguna línea de datos no tiene al menos dos columnas (BE + intensity),
    asumimos que es un error de formato y la función debería lanzar ValueError.
    (Este test indica el comportamiento esperado; si actualmente hay IndexError,
    lo usaremos para guiar la refactorización).
    """
    data_lines = [
        "Element C 1s; Region 1; Time Per Step 50; Sweeps 5; Anode Al Kα; Photon energy 1486.6;",
        "284.8 100.0",
        "285.0",  # línea mal formada
        "286.0 80.0",
    ]
    with pytest.raises(ValueError):
        get_spectrum_data(data_lines)


# ==================== Tests para load_all_data() ====================


def test_load_all_data_basic(tmp_path):
    """Test carga básica de directorio con archivos válidos."""
    # Crear archivos de prueba
    file1 = tmp_path / "sample1.txt"
    file1.write_text(
        "Sample Name Test1; Date 2024-01-01;\n"
        "C 1s;\n"
        "284.8;\n"
        "Element C 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "284.8 100.0\n"
        "285.0 120.0\n"
    )

    file2 = tmp_path / "sample2.txt"
    file2.write_text(
        "Sample Name Test2; Date 2024-01-02;\n"
        "O 1s;\n"
        "531.0;\n"
        "Element O 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "531.0 200.0\n"
        "532.0 180.0\n"
    )

    # Cargar todos los datos
    datasets = load_all_data(tmp_path)

    # Verificar que cargó ambos archivos
    assert len(datasets) == 2
    assert "sample1.txt" in datasets
    assert "sample2.txt" in datasets

    # Verificar contenido básico
    assert "C 1s" in datasets["sample1.txt"].spectra
    assert "O 1s" in datasets["sample2.txt"].spectra


def test_load_all_data_empty_directory(tmp_path):
    """Test con directorio vacío."""
    datasets = load_all_data(tmp_path)
    assert datasets == {}


def test_load_all_data_directory_not_found():
    """Test error cuando directorio no existe."""
    with pytest.raises(FileNotFoundError) as excinfo:
        load_all_data("/path/that/does/not/exist")

    assert "Directorio no encontrado" in str(excinfo.value)


def test_load_all_data_not_a_directory(tmp_path):
    """Test error cuando la ruta es un archivo, no directorio."""
    # Crear un archivo
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    with pytest.raises(ValueError) as excinfo:
        load_all_data(file_path)

    assert "no es un directorio" in str(excinfo.value)


def test_load_all_data_with_invalid_files(tmp_path, capsys):
    """Test con mezcla de archivos válidos e inválidos."""
    # Archivo válido
    valid_file = tmp_path / "valid.txt"
    valid_file.write_text(
        "Sample Name Test; Date 2024-01-01;\n"
        "C 1s;\n"
        "284.8;\n"
        "Element C 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "284.8 100.0\n"
    )

    # Archivo inválido (no tiene formato correcto)
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("Invalid content without proper structure\n")

    # Cargar datos (debe continuar con errores)
    datasets = load_all_data(tmp_path)

    # Debe haber cargado solo el archivo válido
    assert len(datasets) == 1
    assert "valid.txt" in datasets

    # Debe haber impreso advertencia
    captured = capsys.readouterr()
    assert (
        "Advertencia" in captured.out
        or "archivo(s) no pudieron cargarse" in captured.out
    )


def test_load_all_data_recursive_subdirectories(tmp_path):
    """Test búsqueda recursiva en subdirectorios."""
    # Crear estructura con subdirectorios
    subdir1 = tmp_path / "dir1"
    subdir1.mkdir()
    file1 = subdir1 / "sample1.txt"
    file1.write_text(
        "Sample Name Test1;\n"
        "C 1s;\n"
        "284.8;\n"
        "Element C 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "284.8 100.0\n"
    )

    subdir2 = tmp_path / "dir2"
    subdir2.mkdir()
    file2 = subdir2 / "sample2.txt"
    file2.write_text(
        "Sample Name Test2;\n"
        "O 1s;\n"
        "531.0;\n"
        "Element O 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "531.0 200.0\n"
    )

    # Cargar recursivamente
    datasets = load_all_data(tmp_path, recursive=True)

    # Debe encontrar ambos archivos en subdirectorios
    assert len(datasets) == 2
    assert "sample1.txt" in datasets
    assert "sample2.txt" in datasets


def test_load_all_data_non_recursive(tmp_path):
    """Test carga no recursiva (solo directorio raíz)."""
    # Archivo en raíz
    root_file = tmp_path / "root.txt"
    root_file.write_text(
        "Sample Name Root;\n"
        "C 1s;\n"
        "284.8;\n"
        "Element C 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "284.8 100.0\n"
    )

    # Archivo en subdirectorio
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    sub_file = subdir / "sub.txt"
    sub_file.write_text(
        "Sample Name Sub;\n"
        "O 1s;\n"
        "531.0;\n"
        "Element O 1s; Region 1; Sweeps 5; Anode Al Kα; Photon energy 1486.6;\n"
        "531.0 200.0\n"
    )

    # Cargar sin recursión
    datasets = load_all_data(tmp_path, recursive=False)

    # Debe encontrar solo el archivo raíz
    assert len(datasets) == 1
    assert "root.txt" in datasets
    assert "sub.txt" not in datasets


# ==================== Tests para detect_file_format() ====================


def test_detect_file_format_multiplex(tmp_path):
    """Test detección de formato multiplex."""
    file_path = tmp_path / "multiplex_sample.txt"
    file_path.write_text(
        "Sample Name Test; Date 2024-01-01;\n"
        "C 1s O 1s N 1s;\n"
        "284.8 531.0 399.0;\n"
        "Element C 1s; Region 1; Sweeps 5;\n"
        "284.8 100.0\n"
        "Element O 1s; Region 2; Sweeps 5;\n"
        "531.0 200.0\n"
    )

    fmt = detect_file_format(file_path)
    assert fmt == "multiplex"


def test_detect_file_format_multiplex_by_filename(tmp_path):
    """Test detección por nombre de archivo con 'multiplex'."""
    file_path = tmp_path / "sample_multiplex.txt"
    file_path.write_text("Sample Name Test;\n")

    fmt = detect_file_format(file_path)
    assert fmt == "multiplex"


def test_detect_file_format_survey(tmp_path):
    """Test detección de formato survey."""
    file_path = tmp_path / "survey.txt"
    file_path.write_text(
        "Sample Name Test; Date 2024-01-01;\n"
        "Survey;\n"
        "1000.0;\n"
        "Element Survey; Region 1; Sweeps 5;\n"
        "0.0 100.0\n"
        "100.0 120.0\n"
    )

    fmt = detect_file_format(file_path)
    assert fmt == "survey"


def test_detect_file_format_vamas(tmp_path):
    """Test detección de formato VAMAS."""
    file_path = tmp_path / "vamas_sample.vms"
    file_path.write_text(
        "VAMAS Surface Chemical Analysis Standard Data Transfer Format\n"
        "ISO 14976\n"
        "Version 2.3\n"
    )

    fmt = detect_file_format(file_path)
    assert fmt == "vamas"


def test_detect_file_format_casa(tmp_path):
    """Test detección de formato CASA XPS."""
    file_path = tmp_path / "casa_sample.txt"
    file_path.write_text("CASA XPS Data Export\nVersion 2.3.23\nSample: Test Sample\n")

    fmt = detect_file_format(file_path)
    assert fmt == "casa"


def test_detect_file_format_text_generic(tmp_path):
    """Test detección de formato texto genérico."""
    file_path = tmp_path / "generic.txt"
    file_path.write_text("Sample Name Test;\nRegion C 1s;\n284.8 100.0\n285.0 120.0\n")

    fmt = detect_file_format(file_path)
    assert fmt in ["survey", "text"]


def test_detect_file_format_unknown(tmp_path):
    """Test archivo con formato no reconocido."""
    file_path = tmp_path / "unknown.txt"
    file_path.write_text("Random content\nwithout XPS structure\n")

    fmt = detect_file_format(file_path)
    assert fmt is None


def test_detect_file_format_file_not_found():
    """Test error cuando archivo no existe."""
    with pytest.raises(FileNotFoundError) as excinfo:
        detect_file_format("/path/that/does/not/exist.txt")

    assert "Archivo no encontrado" in str(excinfo.value)


def test_detect_file_format_binary_file(tmp_path):
    """Test con archivo binario."""
    file_path = tmp_path / "binary.dat"
    file_path.write_bytes(b"\x00\x01\x02\x03\x04\x05")

    fmt = detect_file_format(file_path)
    # Debe retornar None para archivos binarios
    assert fmt is None
