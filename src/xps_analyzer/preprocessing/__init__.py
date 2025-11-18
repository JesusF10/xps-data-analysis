"""
Módulo de preprocesamiento de datos XPS

Incluye funciones para calibración, suavizado, normalización y
substracción de fondo.
"""

from .calibration import calibrate_sample, calibrate_spectrum

__all__ = [
    'calibrate_spectrum',
    'calibrate_sample'
    ]
