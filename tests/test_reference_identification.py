import sys
from unittest.mock import patch

from xps_analyzer.reference_data.identification import (
    _find_peaks_basic,
    find_peaks_in_spectrum,
)

import pytest


def test_find_peaks_basic():
    binding_energy = [10.0, 20.0, 30.0, 40.0, 50.0]
    intensity = [1.0, 100.0, 2.0, 50.0, 1.0]

    peaks = _find_peaks_basic(binding_energy, intensity, height_threshold=0.1)
    assert peaks == [20.0, 40.0]

    peaks2 = _find_peaks_basic(binding_energy, intensity, height_threshold=0.6)
    assert peaks2 == [20.0]

    assert _find_peaks_basic([10.0, 20.0], [1.0, 2.0], height_threshold=0.1) == []


def test_find_peaks_no_scipy():
    # Simulate missing scipy
    import builtins

    real_import = builtins.__import__

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scipy.signal":
            raise ImportError("No module named 'scipy.signal'")
        return real_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=mock_import):
        binding_energy = [10.0, 20.0, 30.0, 40.0, 50.0]
        intensity = [1.0, 100.0, 2.0, 50.0, 1.0]
        peaks = find_peaks_in_spectrum(binding_energy, intensity, height_threshold=0.1)
        assert peaks == [20.0, 40.0]
