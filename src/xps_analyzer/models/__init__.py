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
- ElementReference ✓ (Pydantic)
- ReferenceDatabase ✓ (Pydantic)

Semana 5-6: Núcleo principal
- XPSSpectrum ✓ (Pydantic)
- XPSDataset ✓ (Pydantic)
- XPSSample ✓ (Pydantic)

Exports principales:
"""

# Fase 2 - Semana 1-4: Modelos de referencia y análisis (COMPLETADAS)
from .analysis import FitResult, PeakParameters

# Fase 2 - Semana 5-6: Núcleo principal (COMPLETADAS)
from .core import XPSDataset, XPSSample, XPSSpectrum
from .reference import (
    CompoundReference,
    ElementReference,
    PhotoelectronLine,
    ReferenceDatabase,
)

# Migración gradual: Eliminar imports de dataclasses originales
# TODO: Remover completamente una vez validada compatibilidad

__all__ = [
    # Core data structures (Semana 5-6 - COMPLETADAS)
    "XPSSpectrum",  # ✓ Pydantic
    "XPSDataset",  # ✓ Pydantic
    "XPSSample",  # ✓ Pydantic
    # Reference data (Semana 3-4 - COMPLETADAS)
    "PhotoelectronLine",  # ✓ Pydantic
    "CompoundReference",  # ✓ Pydantic
    "ElementReference",  # ✓ Pydantic
    "ReferenceDatabase",  # ✓ Pydantic
    # Analysis results (Semana 1-2 - COMPLETADAS)
    "PeakParameters",  # ✓ Pydantic
    "FitResult",  # ✓ Pydantic
]
