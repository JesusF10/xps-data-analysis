"""
Módulo de análisis de espectros XPS.

Este módulo contiene funciones para análisis avanzado de datos XPS, incluyendo:
- Sustracción de fondo (Shirley, Tougaard, linear)
- Ajuste de picos (gaussian, lorentzian, voigt) - PENDIENTE
- Cuantificación - PENDIENTE
"""

from xps_analyzer.analysis.background import (
    linear_background,
    shirley_background,
    tougaard_background,
)

__all__ = [
    "shirley_background",
    "tougaard_background",
    "linear_background",
]
