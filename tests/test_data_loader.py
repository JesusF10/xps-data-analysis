from xps_analyzer.data_loader.core import XPSSpectrum, get_spectrum_data, parse_metadata

import numpy as np
import pytest


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
