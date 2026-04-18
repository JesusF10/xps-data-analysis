"""
Modelos base para XPS Analyzer.

Este módulo proporciona la clase base XPSBaseModel heredando de Pydantic,
configurada para permitir tipos arbitrarios (como arrays de NumPy) y
validación en la asignación.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class XPSBaseModel(BaseModel):
    """
    Modelo base para todas las estructuras de datos de XPS Analyzer.

    Configurado para:
    - Permitir tipos arbitrarios (NumPy arrays).
    - Validar cambios en los atributos después de la creación.
    - Soportar validación de diccionarios anidados.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="forbid",
    )
