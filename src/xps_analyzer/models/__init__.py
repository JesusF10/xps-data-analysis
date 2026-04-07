"""
Modelos de datos Pydantic para XPS Analyzer.

Este módulo contiene todas las estructuras de datos del proyecto migradas a Pydantic
para validación robusta, serialización automática y mejor experiencia de desarrollo.

Migración gradual desde @dataclass (Fase 1) -> Pydantic BaseModel (Fase 2):

Semana 1-2: Dataclasses independientes
- PhotoelectronLine ✓ (Pydantic)
- CompoundReference ✓ (Pydantic)
- PeakParameters ✓ (Pydantic)
- FitResult ✓ (Pydantic)

Semana 3-4: Estructura jerárquica
- ElementReference (pendiente)
- ReferenceDatabase (pendiente)

Semana 5-6: Núcleo principal
- XPSSpectrum (pendiente)
- XPSDataset (pendiente)
- XPSSample (pendiente)

Exports principales:
"""

# Fase 2 - Semana 1-2: Dataclasses independientes (COMPLETADAS)
from .reference import PhotoelectronLine, CompoundReference, ElementReference
from .analysis import PeakParameters, FitResult

# Migración gradual: mantener compatibilidad temporal con dataclasses originales
# TODO: Eliminar una vez completada la migración completa
from ..data_loader.core import XPSSpectrum, XPSDataset, XPSSample

__all__ = [
    # Core data structures (pendientes de migración)
    "XPSSpectrum",
    "XPSDataset",
    "XPSSample",
    # Reference data (migración completa Semana 3-4)
    "PhotoelectronLine",  # ✓ Pydantic
    "CompoundReference",  # ✓ Pydantic
    "ElementReference",  # ✓ Pydantic
    # Analysis results (migración completa)
    "PeakParameters",  # ✓ Pydantic
    "FitResult",  # ✓ Pydantic
]
