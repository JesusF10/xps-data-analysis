"""
Configuración base y validadores para modelos Pydantic de XPS Analyzer.

Proporciona validadores personalizados y configuración común para todos los
modelos Pydantic del proyecto.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict


class XPSBaseModel(BaseModel):
    """
    Modelo base para todas las estructuras de datos XPS con configuración común.

    Configuración:
    - Validación estricta habilitada
    - Campos extra prohibidos
    - Serialización de tipos numpy habilitada
    - Documentación de campos preservada
    """

    model_config = ConfigDict(
        # Validación estricta para detectar errores tempranamente
        strict=True,
        # No permitir campos extra para evitar errores de tipeo
        extra="forbid",
        # Permitir tipos numpy en serialización
        arbitrary_types_allowed=True,
        # Preservar documentación de campos
        use_enum_values=True,
        # Validar asignaciones después de inicialización
        validate_assignment=True,
    )


class NumpyArrayValidator:
    """Validadores estáticos para arrays de numpy en datos XPS."""

    @staticmethod
    def validate_positive_array(values: np.ndarray, field_name: str) -> np.ndarray:
        """
        Valida que un array numpy contenga solo valores positivos.

        Parámetros
        ----------
        values : np.ndarray
            Array a validar.
        field_name : str
            Nombre del campo para mensajes de error.

        Retorna
        -------
        np.ndarray
            Array validado.

        Levanta
        ------
        ValueError
            Si el array contiene valores negativos o no finitos.
        """
        if not isinstance(values, np.ndarray):
            values = np.asarray(values, dtype=float)

        if len(values) == 0:
            raise ValueError(f"{field_name} no puede estar vacío")

        if not np.isfinite(values).all():
            raise ValueError(f"{field_name} debe contener solo valores finitos")

        if (values < 0).any():
            raise ValueError(f"{field_name} debe contener solo valores positivos")

        return values

    @staticmethod
    def validate_finite_array(values: np.ndarray, field_name: str) -> np.ndarray:
        """
        Valida que un array numpy contenga solo valores finitos.

        Parámetros
        ----------
        values : np.ndarray
            Array a validar.
        field_name : str
            Nombre del campo para mensajes de error.

        Retorna
        -------
        np.ndarray
            Array validado.

        Levanta
        ------
        ValueError
            Si el array contiene valores no finitos.
        """
        if not isinstance(values, np.ndarray):
            values = np.asarray(values, dtype=float)

        if len(values) == 0:
            raise ValueError(f"{field_name} no puede estar vacío")

        if not np.isfinite(values).all():
            raise ValueError(f"{field_name} debe contener solo valores finitos")

        return values

    @staticmethod
    def validate_matching_lengths(
        array1: np.ndarray, array2: np.ndarray, name1: str, name2: str
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Valida que dos arrays tengan la misma longitud.

        Parámetros
        ----------
        array1, array2 : np.ndarray
            Arrays a validar.
        name1, name2 : str
            Nombres de los campos para mensajes de error.

        Retorna
        -------
        tuple[np.ndarray, np.ndarray]
            Tupla con los arrays validados.

        Levanta
        ------
        ValueError
            Si los arrays tienen longitudes diferentes.
        """
        if len(array1) != len(array2):
            raise ValueError(
                f"{name1} ({len(array1)} puntos) y {name2} ({len(array2)} puntos) "
                f"deben tener la misma longitud"
            )
        return array1, array2


class XPSValidators:
    """Validadores específicos para datos XPS."""

    @staticmethod
    def validate_binding_energy(binding_energy: np.ndarray) -> np.ndarray:
        """
        Valida energías de enlace XPS (deben ser positivas y finitas).

        Parámetros
        ----------
        binding_energy : np.ndarray
            Energías de enlace en eV.

        Retorna
        -------
        np.ndarray
            Energías validadas.
        """
        return NumpyArrayValidator.validate_positive_array(
            binding_energy, "binding_energy"
        )

    @staticmethod
    def validate_intensity(intensity: np.ndarray) -> np.ndarray:
        """
        Valida intensidades XPS (deben ser positivas o cero y finitas).

        Parámetros
        ----------
        intensity : np.ndarray
            Intensidades en cuentas.

        Retorna
        -------
        np.ndarray
            Intensidades validadas.
        """
        if not isinstance(intensity, np.ndarray):
            intensity = np.asarray(intensity, dtype=float)

        if len(intensity) == 0:
            raise ValueError("intensity no puede estar vacío")

        if not np.isfinite(intensity).all():
            raise ValueError("intensity debe contener solo valores finitos")

        if (intensity < 0).any():
            raise ValueError("intensity debe contener solo valores no negativos")

        return intensity

    @staticmethod
    def validate_region_name(region_name: str) -> str:
        """
        Valida nombres de regiones XPS (no vacíos, formato típico).

        Parámetros
        ----------
        region_name : str
            Nombre de la región.

        Retorna
        -------
        str
            Nombre validado.
        """
        if not isinstance(region_name, str):
            raise TypeError("region_name debe ser string")

        if not region_name.strip():
            raise ValueError("region_name no puede estar vacío")

        # Formato típico: "C 1s", "O 1s", "survey", etc.
        cleaned_name = region_name.strip()
        return cleaned_name

    @staticmethod
    def validate_element_symbol(symbol: str) -> str:
        """
        Valida símbolos de elementos químicos (1-2 caracteres).

        Parámetros
        ----------
        symbol : str
            Símbolo del elemento.

        Retorna
        -------
        str
            Símbolo validado.
        """
        if not isinstance(symbol, str):
            raise TypeError("symbol debe ser string")

        cleaned_symbol = symbol.strip()

        if not cleaned_symbol:
            raise ValueError("symbol no puede estar vacío")

        if len(cleaned_symbol) > 2:
            raise ValueError("symbol debe tener máximo 2 caracteres")

        # Primera letra mayúscula, segunda minúscula (si existe)
        if len(cleaned_symbol) == 1:
            return cleaned_symbol.upper()
        else:
            return cleaned_symbol[0].upper() + cleaned_symbol[1:].lower()
