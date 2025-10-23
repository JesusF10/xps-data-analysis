"""
Módulo de carga de datos XPS

Este módulo maneja la importación de datos desde diferentes instrumentos XPS
y formatos de archivo.
"""

from .core import detect_file_format, load_all_data, load_single_file

__all__ = [
    "detect_file_format",
    "load_all_data",
    "load_single_file",
]
