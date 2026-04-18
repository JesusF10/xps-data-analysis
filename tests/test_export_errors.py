import pytest
import numpy as np
from xps_analyzer.export.exporters import (
    export_to_excel,
    export_to_json,
    NumpyEncoder
)

def test_export_to_excel_type_error(tmp_path):
    with pytest.raises(TypeError, match="debe ser XPSSpectrum o XPSDataset"):
        export_to_excel("not a spectrum", tmp_path / "test.xlsx")

def test_export_to_json_type_error(tmp_path):
    with pytest.raises(TypeError, match="debe ser XPSSpectrum o XPSDataset"):
        export_to_json("not a spectrum", tmp_path / "test.json")

def test_numpy_encoder_extra_types():
    encoder = NumpyEncoder()
    # int
    assert encoder.default(np.int32(42)) == 42
    # float
    assert encoder.default(np.float64(3.14)) == 3.14
    # NaN
    assert encoder.default(np.float64(np.nan)) is None
    # Inf
    assert encoder.default(np.float64(np.inf)) is None
    # bool
    assert encoder.default(np.bool_(True)) is True
    # unhandled
    with pytest.raises(TypeError):
        encoder.default(object())
