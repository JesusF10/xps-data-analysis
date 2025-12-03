"""
Módulo de visualización de datos XPS

Genera gráficas, espectros y reportes visuales de los análisis.
"""

from .plotting import plot_spectrum, plot_survey_spectrum

__all__ = [
    "plot_spectrum",
    "plot_survey_spectrum",
]
