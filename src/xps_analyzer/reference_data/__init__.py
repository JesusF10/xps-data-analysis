"""
Módulo de datos de referencia para análisis XPS.

Este módulo contiene las clases y funciones para manejar datos de referencia
de elementos químicos, incluyendo energías de enlace, desplazamientos químicos
y información de compuestos para identificación automática.
"""

from .elements import (
    CompoundReference,
    ElementReference,
    PhotoelectronLine,
    ReferenceDatabase,
    load_reference_database,
)

# from .identification import find_peaks_in_spectrum, identify_peaks, suggest_compounds

__all__ = [
    "PhotoelectronLine",
    "CompoundReference",
    "ElementReference",
    "ReferenceDatabase",
    "load_reference_database",
]
