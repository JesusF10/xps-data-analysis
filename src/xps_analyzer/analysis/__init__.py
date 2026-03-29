"""
Módulo de análisis de espectros XPS.

Este módulo contiene funciones para análisis avanzado de datos XPS, incluyendo:
- Sustracción de fondo (Shirley, Tougaard, linear)
- Ajuste de picos (gaussian, lorentzian, voigt)
- Cuantificación atómica (RSF, concentraciones)
"""

from xps_analyzer.analysis.background import (
    background_with_fallback,
    linear_background,
    shirley_background,
    tougaard_background,
)
from xps_analyzer.analysis.peak_fitting import (
    FitResult,
    PeakParameters,
    estimate_peak_positions,
    fit_doublet,
    fit_gaussian,
    fit_lorentzian,
    fit_multiple_peaks,
    fit_voigt,
)
from xps_analyzer.analysis.quantification import (
    calculate_atomic_concentration,
    load_sensitivity_factors,
    normalize_to_100,
    quantify_dataset,
)

__all__ = [
    # Background subtraction
    "shirley_background",
    "tougaard_background",
    "linear_background",
    "background_with_fallback",
    # Peak fitting
    "fit_gaussian",
    "fit_lorentzian",
    "fit_voigt",
    "fit_multiple_peaks",
    "fit_doublet",
    "estimate_peak_positions",
    # Quantification
    "load_sensitivity_factors",
    "calculate_atomic_concentration",
    "normalize_to_100",
    "quantify_dataset",
    # Data classes
    "PeakParameters",
    "FitResult",
]
