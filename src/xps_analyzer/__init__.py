"""
XPS Analyzer - Software automatizado para análisis de datos XPS

Este modulo proporciona herramientas para el analisis automatizado de datos
de espectroscopia de fotoelectrones de rayos X (XPS), incluyendo:

- Carga y preprocesamiento de datos
- Calibración automática de energía
- Detección y ajuste de picos
- Cuantificación elemental
- Generación de reportes
- Visualización de resultados

Desarrollado como parte del proyecto de servicio social.
"""

__version__ = "0.1.0"
__author__ = "Jesus Flores Lacarra"
__email__ = "jss.263.fsc@gmail.com"

# Importaciones principales del paquete
from .data_loader.core import load_all_data, load_single_file
from .reference_data import (
    ElementReference,
    ReferenceDatabase,
    identify_peaks,
    load_reference_database,
)

# Hacer disponibles las funciones principales
__all__ = [
    # Carga de datos
    "load_single_file",
    "load_all_data",
    # Referencias
    "ReferenceDatabase",
    "ElementReference",
    "load_reference_database",
    "identify_peaks",
]
