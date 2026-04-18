import pytest
import numpy as np
from pydantic import ValidationError
from xps_analyzer.models.analysis import PeakParameters, FitResult

def test_peak_parameters_voigt_gamma():
    # Valid
    p = PeakParameters(position=100, amplitude=10, width=2, area=20, shape="voigt", gamma=1.0)
    assert p.gamma == 1.0

    # Invalid: voigt without gamma
    with pytest.raises(ValueError, match="Perfil Voigt requiere parámetro gamma"):
        PeakParameters(position=100, amplitude=10, width=2, area=20, shape="voigt")

def test_peak_parameters_area_consistency():
    # min_expected_area = amplitude * width * 0.5 = 10 * 2 * 0.5 = 10
    # max_expected_area = 10 * 2 * 5.0 = 100
    
    # Valid
    PeakParameters(position=100, amplitude=10, width=2, area=50, shape="gaussian")

    # Invalid: area too small
    with pytest.raises(ValueError, match="inconsistente con amplitud"):
        PeakParameters(position=100, amplitude=10, width=2, area=5, shape="gaussian")

    # Invalid: area too large
    with pytest.raises(ValueError, match="inconsistente con amplitud"):
        PeakParameters(position=100, amplitude=10, width=2, area=150, shape="gaussian")

def test_fit_result_validators():
    peak = PeakParameters(position=100, amplitude=10, width=2, area=50, shape="gaussian")
    
    # Valid
    fit = FitResult(
        peaks=[peak],
        fitted_spectrum=np.array([1, 2, 3]),
        residual=np.array([0.1, 0.2, 0.3]),
        r_squared=0.9,
        chi_squared=1.5,
        success=True,
        message="OK"
    )

    # validate_fitted_spectrum (requires finite)
    with pytest.raises(ValueError, match="solo valores finitos"):
        FitResult(
            peaks=[peak],
            fitted_spectrum=np.array([1, np.inf, 3]),
            residual=np.array([0.1, 0.2, 0.3]),
            r_squared=0.9,
            chi_squared=1.5,
            success=True,
            message="OK"
        )

    # validate_residual (requires finite)
    with pytest.raises(ValueError, match="solo valores finitos"):
        FitResult(
            peaks=[peak],
            fitted_spectrum=np.array([1, 2, 3]),
            residual=np.array([0.1, np.nan, 0.3]),
            r_squared=0.9,
            chi_squared=1.5,
            success=True,
            message="OK"
        )

    # validate_array_lengths
    with pytest.raises(ValueError, match="deben tener la misma longitud"):
        FitResult(
            peaks=[peak],
            fitted_spectrum=np.array([1, 2, 3]),
            residual=np.array([0.1, 0.2]),
            r_squared=0.9,
            chi_squared=1.5,
            success=True,
            message="OK"
        )

    # Test r_squared warning branch (< 0.5)
    FitResult(
        peaks=[peak],
        fitted_spectrum=np.array([1, 2, 3]),
        residual=np.array([0.1, 0.2, 0.3]),
        r_squared=0.2,
        chi_squared=1.5,
        success=True,
        message="OK"
    )

    # Test chi_squared warning branch (> 10)
    FitResult(
        peaks=[peak],
        fitted_spectrum=np.array([1, 2, 3]),
        residual=np.array([0.1, 0.2, 0.3]),
        r_squared=0.9,
        chi_squared=20.0,
        success=True,
        message="OK"
    )
