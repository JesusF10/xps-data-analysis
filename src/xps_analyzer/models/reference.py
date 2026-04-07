"""
Modelos Pydantic para datos de referencia XPS.

Migración de dataclasses -> Pydantic BaseModel para:
- PhotoelectronLine ✓
- CompoundReference ✓
- ElementReference ✓
- ReferenceDatabase (pendiente)

Proporciona validación automática y serialización mejorada para datos de referencia.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from .base import XPSBaseModel, XPSValidators


class PhotoelectronLine(XPSBaseModel):
    """
    Representa una línea fotoeléctrica de un orbital específico.

    Esta clase valida automáticamente energías de enlace positivas,
    fuentes de rayos X válidas y tipos de línea correctos.

    Parámetros
    ----------
    line : str
        Designación de la línea (ej: "1s", "2p1/2", "2p3/2", "KLL").
        Debe ser no vacía.
    binding_energy : float
        Energía de enlace en eV. Debe ser positiva.
    x_ray_source : str, optional
        Fuente de rayos X utilizada (ej: "Mg_Ka", "Al_Ka").
    type : Literal["core", "Auger"], default="core"
        Tipo de línea, debe ser "core" o "Auger".
    kinetic_energy : float, optional
        Energía cinética en eV (solo para líneas Auger). Debe ser positiva si se especifica.

    Ejemplos
    --------
    >>> # Línea core básica
    >>> line = PhotoelectronLine(
    ...     line="1s",
    ...     binding_energy=284.8
    ... )
    >>>
    >>> # Línea Auger completa
    >>> auger_line = PhotoelectronLine(
    ...     line="KLL",
    ...     binding_energy=1200.0,
    ...     x_ray_source="Al_Ka",
    ...     type="Auger",
    ...     kinetic_energy=267.0
    ... )
    """

    line: str = Field(
        ...,
        description="Designación de la línea orbital",
        min_length=1,
        examples=["1s", "2p1/2", "2p3/2", "KLL"],
    )

    binding_energy: float = Field(
        ...,
        description="Energía de enlace en eV",
        gt=0,
        lt=10000,  # Límite realista para XPS
        examples=[284.8, 531.0, 399.0],
    )

    x_ray_source: str | None = Field(
        default=None,
        description="Fuente de rayos X utilizada",
        examples=["Mg_Ka", "Al_Ka", "Cr_Ka"],
    )

    type: Literal["core", "Auger"] = Field(
        default="core", description="Tipo de línea fotoeléctrica"
    )

    kinetic_energy: float | None = Field(
        default=None,
        description="Energía cinética en eV (solo líneas Auger)",
        gt=0,
        lt=2000,  # Límite realista para energías cinéticas
    )

    @field_validator("line")
    @classmethod
    def validate_line_format(cls, v: str) -> str:
        """Valida formato de designación orbital."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("line no puede estar vacía")
        return cleaned

    @model_validator(mode="after")
    def validate_auger_kinetic_energy(self) -> "PhotoelectronLine":
        """Valida que líneas Auger tengan energía cinética."""
        if self.type == "Auger" and self.kinetic_energy is None:
            raise ValueError("Líneas Auger requieren kinetic_energy")
        return self


class CompoundReference(XPSBaseModel):
    """
    Datos de referencia para un compuesto específico.

    Valida automáticamente rangos de energía de enlace consistentes
    y posiciones de pico dentro del rango especificado.

    Parámetros
    ----------
    orbital : str
        Orbital asociado (ej: "1s", "2p"). Debe ser no vacío.
    binding_energy_range : tuple[float, float]
        Rango de energías de enlace (min, max) en eV. min < max, ambos > 0.
    peak_position : float, optional
        Posición del pico principal en eV. Debe estar dentro del rango.
    chemical_shift : float, optional
        Desplazamiento químico respecto al elemento puro en eV.

    Ejemplos
    --------
    >>> # Compuesto básico
    >>> compound = CompoundReference(
    ...     orbital="1s",
    ...     binding_energy_range=(284.0, 289.0),
    ...     peak_position=286.5
    ... )
    >>>
    >>> # Con desplazamiento químico
    >>> oxide = CompoundReference(
    ...     orbital="1s",
    ...     binding_energy_range=(531.0, 534.0),
    ...     peak_position=532.1,
    ...     chemical_shift=2.1
    ... )
    """

    orbital: str = Field(
        ...,
        description="Orbital asociado al compuesto",
        min_length=1,
        examples=["1s", "2p", "3d"],
    )

    binding_energy_range: tuple[float, float] = Field(
        ...,
        description="Rango de energías de enlace (min, max) en eV",
        examples=[(284.0, 289.0), (531.0, 534.0)],
    )

    peak_position: float | None = Field(
        default=None,
        description="Posición del pico principal en eV",
        gt=0,
        examples=[286.5, 532.1],
    )

    chemical_shift: float | None = Field(
        default=None,
        description="Desplazamiento químico respecto al elemento puro en eV",
        examples=[0.0, 2.1, -1.5],
    )

    @field_validator("binding_energy_range")
    @classmethod
    def validate_energy_range(cls, v: tuple[float, float]) -> tuple[float, float]:
        """Valida que el rango de energía sea consistente."""
        min_energy, max_energy = v

        if min_energy <= 0 or max_energy <= 0:
            raise ValueError("Las energías de enlace deben ser positivas")

        if min_energy >= max_energy:
            raise ValueError(
                f"min_energy ({min_energy}) debe ser menor que max_energy ({max_energy})"
            )

        if max_energy - min_energy > 50:  # Rango muy amplio es sospechoso
            raise ValueError(
                f"Rango de energías muy amplio: {max_energy - min_energy:.1f} eV"
            )

        return v

    @model_validator(mode="after")
    def validate_peak_in_range(self) -> "CompoundReference":
        """Valida que la posición del pico esté dentro del rango."""
        if self.peak_position is not None:
            min_energy, max_energy = self.binding_energy_range
            if not (min_energy <= self.peak_position <= max_energy):
                raise ValueError(
                    f"peak_position ({self.peak_position}) debe estar en el rango "
                    f"[{min_energy}, {max_energy}]"
                )
        return self

    @field_validator("orbital")
    @classmethod
    def validate_orbital_format(cls, v: str) -> str:
        """Valida formato básico de orbital."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("orbital no puede estar vacío")
        return cleaned


class ElementReference(XPSBaseModel):
    """
    Base de datos completa de un elemento químico con validación automática.

    Valida automáticamente símbolos de elemento, números atómicos,
    energías de enlace y consistencia entre líneas fotoeléctronicas.

    Parámetros
    ----------
    symbol : str
        Símbolo del elemento (ej: "Li", "C", "O"). Debe tener 1-2 caracteres.
    element : str
        Nombre completo del elemento. Debe ser no vacío.
    atomic_number : int
        Número atómico. Debe ser positivo (1-118).
    photoelectron_lines : list[PhotoelectronLine]
        Lista con las líneas fotoeléctronicas por orbital. No puede estar vacía.
    compounds : dict[str, CompoundReference]
        Diccionario de compuestos de referencia por nombre.
    binding_energy_most_useful : float, optional
        Energía de enlace más útil en eV. Debe ser positiva.
    spin_orbital_splitting : float, optional
        Separación spin-orbital en eV. Debe ser positiva.

    Ejemplos
    --------
    >>> # Elemento básico con líneas core
    >>> carbon = ElementReference(
    ...     symbol="C",
    ...     element="Carbon",
    ...     atomic_number=6,
    ...     photoelectron_lines=[
    ...         PhotoelectronLine(line="1s", binding_energy=284.8)
    ...     ],
    ...     compounds={}
    ... )
    >>>
    >>> # Elemento con compuestos
    >>> oxygen = ElementReference(
    ...     symbol="O",
    ...     element="Oxygen",
    ...     atomic_number=8,
    ...     photoelectron_lines=[...],
    ...     compounds={
    ...         "oxide": CompoundReference(
    ...             orbital="1s",
    ...             binding_energy_range=(531.0, 533.0)
    ...         )
    ...     },
    ...     binding_energy_most_useful=531.0
    ... )
    """

    symbol: str = Field(
        ...,
        description="Símbolo del elemento químico",
        min_length=1,
        max_length=2,
        examples=["C", "O", "Al", "Au"],
    )

    element: str = Field(
        ...,
        description="Nombre completo del elemento",
        min_length=1,
        examples=["Carbon", "Oxygen", "Aluminum", "Gold"],
    )

    atomic_number: int = Field(
        ...,
        description="Número atómico del elemento",
        ge=1,
        le=118,  # Últimos elementos conocidos
        examples=[6, 8, 13, 79],
    )

    photoelectron_lines: list[PhotoelectronLine] = Field(
        ..., description="Lista de líneas fotoeléctronicas por orbital", min_length=1
    )

    compounds: dict[str, CompoundReference] = Field(
        default_factory=dict, description="Diccionario de compuestos de referencia"
    )

    binding_energy_most_useful: float | None = Field(
        default=None,
        description="Energía de enlace más útil para calibración en eV",
        gt=0,
        lt=2000,
        examples=[284.8, 531.0, 399.0],
    )

    spin_orbital_splitting: float | None = Field(
        default=None,
        description="Separación spin-orbital en eV",
        gt=0,
        lt=50,  # Separaciones muy grandes son poco realistas
        examples=[0.6, 1.3, 2.4],
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v: str) -> str:
        """Valida formato de símbolo químico."""
        return XPSValidators.validate_element_symbol(v)

    @field_validator("element")
    @classmethod
    def validate_element_name(cls, v: str) -> str:
        """Valida nombre del elemento."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("element no puede estar vacío")
        return cleaned.title()  # Primera letra mayúscula

    @model_validator(mode="after")
    def validate_symbol_atomic_number_consistency(self) -> "ElementReference":
        """Valida consistencia básica entre símbolo y número atómico."""
        # Validación básica de elementos comunes en XPS
        common_elements = {
            "H": 1,
            "C": 6,
            "N": 7,
            "O": 8,
            "F": 9,
            "Na": 11,
            "Mg": 12,
            "Al": 13,
            "Si": 14,
            "P": 15,
            "S": 16,
            "Cl": 17,
            "K": 19,
            "Ca": 20,
            "Ti": 22,
            "V": 23,
            "Cr": 24,
            "Mn": 25,
            "Fe": 26,
            "Co": 27,
            "Ni": 28,
            "Cu": 29,
            "Zn": 30,
            "Ga": 31,
            "Ge": 32,
            "As": 33,
            "Se": 34,
            "Br": 35,
            "Sr": 38,
            "Zr": 40,
            "Mo": 42,
            "Ag": 47,
            "Cd": 48,
            "In": 49,
            "Sn": 50,
            "I": 53,
            "Ba": 56,
            "Au": 79,
            "Pb": 82,
            "Bi": 83,
        }

        if self.symbol in common_elements:
            expected_z = common_elements[self.symbol]
            if self.atomic_number != expected_z:
                raise ValueError(
                    f"Número atómico inconsistente: {self.symbol} debe tener Z={expected_z}, "
                    f"encontrado Z={self.atomic_number}"
                )

        return self

    @model_validator(mode="after")
    def validate_most_useful_energy_exists(self) -> "ElementReference":
        """Valida que la energía más útil corresponda a una línea existente."""
        if self.binding_energy_most_useful is not None:
            # Buscar si existe una línea con energía similar (±1 eV)
            found_matching_line = False
            tolerance = 1.0

            for line in self.photoelectron_lines:
                if (
                    abs(line.binding_energy - self.binding_energy_most_useful)
                    <= tolerance
                ):
                    found_matching_line = True
                    break

            if not found_matching_line:
                raise ValueError(
                    f"binding_energy_most_useful ({self.binding_energy_most_useful:.1f} eV) "
                    f"no corresponde a ninguna línea existente (±{tolerance} eV)"
                )

        return self

    def get_main_line(self) -> PhotoelectronLine:
        """
        Obtiene la línea fotoeléctrica principal (mayor intensidad o más útil).

        Si se especifica binding_energy_most_useful, retorna la línea más cercana.
        De lo contrario, retorna la primera línea disponible.

        Retorna
        -------
        PhotoelectronLine
            Línea fotoeléctrica principal.

        Levanta
        ------
        ValueError
            Si no hay líneas disponibles.
        """
        if not self.photoelectron_lines:
            raise ValueError(
                f"No hay líneas fotoeléctronicas disponibles para {self.symbol}"
            )

        if self.binding_energy_most_useful is not None:
            # Buscar línea más cercana a la energía más útil
            closest_line = min(
                self.photoelectron_lines,
                key=lambda line: abs(
                    line.binding_energy - self.binding_energy_most_useful
                ),
            )
            return closest_line
        else:
            # Retornar primera línea disponible
            return self.photoelectron_lines[0]

    def get_line_by_orbital(self, orbital: str) -> PhotoelectronLine | None:
        """
        Busca una línea específica por nombre de orbital.

        Parámetros
        ----------
        orbital : str
            Nombre del orbital (ej: "1s", "2p").

        Retorna
        -------
        PhotoelectronLine | None
            Línea encontrada o None si no existe.
        """
        for line in self.photoelectron_lines:
            if line.line.lower() == orbital.lower():
                return line
        return None
