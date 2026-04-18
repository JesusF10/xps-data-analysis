import pytest
import numpy as np
from pydantic import ValidationError
from xps_analyzer.models.core import XPSSpectrum, XPSDataset, XPSSample

def test_spectrum_validators_missing_branches():
    with pytest.raises(ValidationError):
        XPSSpectrum(region_name="Test", binding_energy="string", intensity=[1, 2], metadata={})

    # Line 135: intensity > 1e6
    spec = XPSSpectrum(
        region_name="Test",
        binding_energy=np.array([1, 2]),
        intensity=np.array([2e6, 3e6]),
        metadata={}
    )
    assert spec.intensity.max() > 1e6

    # Test pd.DataFrame property if not already
    df = spec.data
    assert df.index.name == "binding_energy"
    assert "intensity" in df.columns

def test_dataset_missing_branches():
    spec = XPSSpectrum(
        region_name="Test",
        binding_energy=np.array([1, 2]),
        intensity=np.array([10, 20]),
        metadata={}
    )
    dataset = XPSDataset(filename="file.txt", header={}, spectra={"Test": spec})
    
    # get_statistics
    summ = dataset.get_statistics()
    assert summ["total_spectra"] == 1
    assert summ["total_data_points"] == 2
    assert "Test" in summ["regions"]

def test_sample_missing_branches():
    spec = XPSSpectrum(
        region_name="Test",
        binding_energy=np.array([1, 2]),
        intensity=np.array([10, 20]),
        metadata={}
    )
    dataset = XPSDataset(filename="file.txt", header={}, spectra={"Test": spec})
    sample = XPSSample(sample_name="Sample1", datasets={"file.txt": dataset})

    # get_sample_statistics
    summ = sample.get_sample_statistics()
    assert summ["total_datasets"] == 1
    assert summ["total_spectra"] == 1
    assert "file.txt" in summ["dataset_filenames"]

