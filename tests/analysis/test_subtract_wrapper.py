import pytest
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum
from xps_analyzer.analysis import subtract_background

def test_subtract_wrapper_basic():
    # Creamos un espectro falso
    be = np.linspace(290, 280, 100)
    int_ = np.ones(100) * 1000 + np.exp(-((be - 285)**2)/(2*1.5**2)) * 5000
    spec = XPSSpectrum(region_name="C 1s", binding_energy=be, intensity=int_, metadata={})
    
    spec_clean = subtract_background(spec, method="linear")
    assert "linear_background" in spec_clean.metadata
    
    spec_clean2 = subtract_background(spec, method="shirley")
    assert "shirley_background" in spec_clean2.metadata

def test_subtract_wrapper_energy_range():
    be = np.linspace(300, 270, 301) # paso de 0.1
    int_ = np.ones(301) * 1000
    # pico entre 280 y 290
    idx = (be <= 290) & (be >= 280)
    int_[idx] += np.exp(-((be[idx] - 285)**2)/(2*1.5**2)) * 5000
    
    spec = XPSSpectrum(region_name="C 1s", binding_energy=be, intensity=int_, metadata={})
    
    spec_clean = subtract_background(spec, method="linear", energy_range=(280, 290))
    
    # Fuera del rango (295 eV y 275 eV) no debe cambiar
    idx_out_high = np.where(be >= 295)[0]
    idx_out_low = np.where(be <= 275)[0]
    
    np.testing.assert_array_equal(spec.intensity[idx_out_high], spec_clean.intensity[idx_out_high])
    np.testing.assert_array_equal(spec.intensity[idx_out_low], spec_clean.intensity[idx_out_low])
    
    # Adentro sí cambió
    idx_in = np.where((be <= 290) & (be >= 280))[0]
    assert np.any(spec.intensity[idx_in] != spec_clean.intensity[idx_in])

if __name__ == "__main__":
    pytest.main(["-v", "test_subtract_wrapper.py"])
