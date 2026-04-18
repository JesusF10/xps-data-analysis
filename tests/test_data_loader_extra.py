import pytest
import numpy as np
from pydantic import ValidationError

from xps_analyzer.data_loader.core import (
    XPSSpectrum,
    XPSDataset,
    XPSSample,
    parse_metadata,
    get_spectrum_data,
    load_single_file,
    detect_file_format,
    load_all_data
)

def test_xpsspectrum_validators():
    with pytest.raises((TypeError, ValidationError)):
        XPSSpectrum(region_name="C 1s", binding_energy=[284.8, 285.0], intensity=np.array([100.0, 120.0]), metadata={})
    with pytest.raises((ValueError, ValidationError)):
        XPSSpectrum(region_name="C 1s", binding_energy=np.array([-1.0, 285.0]), intensity=np.array([100.0, 120.0]), metadata={})
    with pytest.raises((ValueError, ValidationError)):
        XPSSpectrum(region_name="", binding_energy=np.array([284.8, 285.0]), intensity=np.array([100.0, 120.0]), metadata={})
    with pytest.raises((ValueError, ValidationError)):
        XPSSpectrum(region_name="C 1s", binding_energy=np.array([284.8, 285.0]), intensity=np.array([100.0]), metadata={})

def test_xpsdataset_sample_validators():
    spec = XPSSpectrum(region_name="C 1s", binding_energy=np.array([1.0]), intensity=np.array([1.0]), metadata={})
    with pytest.raises((ValueError, ValidationError)):
        XPSDataset(filename="", header={}, spectra={"C 1s": spec})
    with pytest.raises((ValueError, ValidationError)):
        XPSDataset(filename="test.txt", header={}, spectra={})
    ds = XPSDataset(filename="test.txt", header={}, spectra={"C 1s": spec})
    assert ds.list_regions() == ["C 1s"]
    with pytest.raises((ValueError, ValidationError)):
        XPSSample(sample_name="", datasets={"test.txt": ds})
    with pytest.raises((ValueError, ValidationError)):
        XPSSample(sample_name="Sample", datasets={})
    samp = XPSSample(sample_name="Sample", datasets={"test.txt": ds})
    assert samp.get_dataset("test.txt") == ds
    assert samp.get_dataset("nonexistent") is None
    assert samp.list_datasets() == ["test.txt"]

def test_parse_metadata_errors():
    # Trigger `len(parts) != 2`
    lines_fallback = ["Sample;", "C", "284.8"]
    meta = parse_metadata(lines_fallback, header=True)
    assert meta["elements"]["C"]["orbital"] == "unknown"

    # Trigger IndexError in header parse
    lines_err = ["Sample;", "C 1s"]
    with pytest.raises(ValueError):
        parse_metadata(lines_err, header=True)
    
    # Empty element metadata fallback to 'survey'
    line = "Element ; Region 1; Depth Cycle 1 of 1; Time Per Step 50; Sweeps 5; Anode Al; Photon energy 1486.6;"
    meta2 = parse_metadata(line, header=False)
    assert meta2.get("element") == "survey"

def test_get_spectrum_data_errors():
    with pytest.raises(ValueError):
        get_spectrum_data(["284.8 100.0"])
    with pytest.raises(ValueError):
        get_spectrum_data(["Element C 1s; Region 1; Depth Cycle 1 of 1; Time Per Step 50; Sweeps 5; Anode Al; Photon energy 1486.6;", "abc def"])
    with pytest.raises(ValueError):
        get_spectrum_data(["Element C 1s; Region 1; Depth Cycle 1 of 1; Time Per Step 50; Sweeps 5; Anode Al; Photon energy 1486.6;"])

def test_load_single_file_survey_fallback(tmp_path):
    f = tmp_path / "survey_only.txt"
    f.write_text("Element Survey; Region 1; Depth Cycle 1 of 1; Time Per Step 50; Sweeps 5; Anode Al; Photon energy 1486.6;\n10.0 100\n20.0 200\n")
    ds = load_single_file(f)
    assert "survey" in ds.list_regions() or "Survey" in ds.list_regions()

def test_load_all_data_errors(tmp_path, capsys):
    for i in range(10):
        (tmp_path / f"bad_{i}.txt").write_text("invalid")
    load_all_data(tmp_path)
    cap = capsys.readouterr()
    assert "más" in cap.out

def test_detect_file_format_extra(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Sample; C 1s; 284.8; multiplex")
    fmt = detect_file_format(f)
    
    f2 = tmp_path / "bad_encoding.txt"
    f2.write_bytes(b"\xff\xfe\x00\x00")
    assert detect_file_format(f2) is None
