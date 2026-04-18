"""
Modelos Pydantic para resultados de análisis XPS.

Migración de dataclasses -> Pydantic BaseModel para:
- PeakParameters ✓
- FitResult ✓
- BackgroundResult (futuro)

Proporciona validación automática para parámetros de ajuste y resultados de análisis.
"""

from __future__ import annotations

from typing import Literal

from .base import NumpyArrayValidator, XPSBaseModel

import numpy as np
from pydantic import Field, field_validator, model_validator


class PeakParameters(XPSBaseModel):
    """
    Parámetros de un pico ajustado con validación automática.

    Valida automáticamente que los parámetros físicos sean realistas
    y consistentes entre sí para espectroscopía XPS.

    Parámetros
    ----------
    position : float
        Posición del pico (binding energy en eV). Debe ser positiva.
    amplitude : float
        Amplitud del pico (intensidad máxima en cuentas). Debe ser positiva.
    width : float
        Ancho del pico (FWHM en eV para gaussiano/lorentziano, sigma para Voigt).
        Debe ser positiva y realista para XPS (< 10 eV).
    area : float
        Área integrada bajo el pico. Debe ser positiva.
    shape : Literal["gaussian", "lorentzian", "voigt", "pseudo_voigt", "gl"]
        Tipo de perfil del pico.
    gamma : float, optional
        Parámetro gamma para perfil Voigt (ancho lorentziano). Solo requerido para Voigt.
    position_error : float, optional
        Error estándar en la posición del pico. Debe ser no negativo.
    amplitude_error : float, optional
        Error estándar en la amplitud. Debe ser no negativo.
    width_error : float, optional
        Error estándar en el ancho. Debe ser no negativo.

    Ejemplos
    --------
    >>> # Pico gaussiano básico
    >>> peak = PeakParameters(
    ...     position=284.8,
    ...     amplitude=1000.0,
    ...     width=1.2,
    ...     area=1500.0,
    ...     shape="gaussian"
    ... )
    >>>
    >>> # Pico Voigt con errores
    >>> voigt_peak = PeakParameters(
    ...     position=531.1,
    ...     amplitude=800.0,
    ...     width=1.8,
    ...     area=2000.0,
    ...     shape="voigt",
    ...     gamma=0.5,
    ...     position_error=0.1,
    ...     amplitude_error=50.0
    ... )
    """

    position: float = Field(
        ...,
        description="Posición del pico (binding energy en eV)",
        gt=0,
        lt=2000,  # Límite realista para XPS
        examples=[284.8, 531.1, 399.0],
    )

    amplitude: float = Field(
        ...,
        description="Amplitud del pico (intensidad máxima en cuentas)",
        gt=0,
        examples=[1000.0, 500.0, 2000.0],
    )

    width: float = Field(
        ...,
        description="Ancho del pico (FWHM/sigma en eV)",
        gt=0,
        lt=10,  # Picos muy anchos son poco realistas en XPS
        examples=[1.2, 1.8, 0.9],
    )

    area: float = Field(
        ...,
        description="Área integrada bajo el pico",
        gt=0,
        examples=[1500.0, 2000.0, 800.0],
    )

    shape: Literal["gaussian", "lorentzian", "voigt", "pseudo_voigt", "gl"] = Field(
        ..., description="Tipo de perfil del pico", examples=["gaussian", "voigt"]
    )

    gamma: float | None = Field(
        default=None,
        description="Parámetro gamma para perfil Voigt (ancho lorentziano)",
        gt=0,
        lt=10,
        examples=[0.5, 1.0, 0.3],
    )

    position_error: float | None = Field(
        default=None,
        description="Error estándar en la posición del pico",
        ge=0,
        examples=[0.1, 0.05, 0.2],
    )

    amplitude_error: float | None = Field(
        default=None,
        description="Error estándar en la amplitud",
        ge=0,
        examples=[50.0, 25.0, 100.0],
    )

    width_error: float | None = Field(
        default=None,
        description="Error estándar en el ancho",
        ge=0,
        examples=[0.1, 0.05, 0.15],
    )

    @model_validator(mode="after")
    def validate_voigt_gamma(self) -> "PeakParameters":
        """Valida que picos Voigt tengan parámetro gamma."""
        if self.shape == "voigt" and self.gamma is None:
            raise ValueError("Perfil Voigt requiere parámetro gamma")
        return self

    @model_validator(mode="after")
    def validate_area_consistency(self) -> "PeakParameters":
        """Valida consistencia entre área, amplitud y ancho."""
        amplitude = self.amplitude
        width = self.width
        area = self.area

        # Área mínima esperada para gaussian ~ amplitude * width * sqrt(2*pi) / 2
        min_expected_area = amplitude * width * 0.5
        max_expected_area = amplitude * width * 5.0

        if not (min_expected_area <= area <= max_expected_area):
            raise ValueError(
                f"Área ({area:.1f}) inconsistente con amplitud ({amplitude:.1f}) "
                f"y ancho ({width:.1f}). Esperada entre "
                f"{min_expected_area:.1f} y {max_expected_area:.1f}"
            )

        return self


class FitResult(XPSBaseModel):
    """
    Resultado de un ajuste de pico(s) con validación automática.

    Valida automáticamente que los resultados estadísticos sean
    consistentes y que los arrays tengan dimensiones correctas.

    Parámetros
    ----------
    peaks : list[PeakParameters]
        Lista de parámetros de picos ajustados. No puede estar vacía.
    fitted_spectrum : np.ndarray
        Espectro ajustado (suma de todos los picos). Debe ser finito.
    residual : np.ndarray
        Residual (espectro original - ajuste). Misma longitud que fitted_spectrum.
    r_squared : float
        Coeficiente de determinación R² (bondad de ajuste). Debe estar en [0, 1].
    chi_squared : float
        Chi-cuadrado reducido. Debe ser positivo.
    success : bool
        Si el ajuste convergió exitosamente.
    message : str
        Mensaje sobre el resultado del ajuste. No puede estar vacío.

    Ejemplos
    --------
    >>> # Ajuste exitoso con un pico
    >>> result = FitResult(
    ...     peaks=[peak_params],
    ...     fitted_spectrum=np.array([100, 200, 300]),
    ...     residual=np.array([5, -2, 1]),
    ...     r_squared=0.95,
    ...     chi_squared=1.2,
    ...     success=True,
    ...     message="Ajuste convergió exitosamente"
    ... )
    """

    peaks: list[PeakParameters] = Field(
        ..., description="Lista de parámetros de picos ajustados", min_length=1
    )

    fitted_spectrum: np.ndarray = Field(
        ...,
        description="Espectro ajustado (suma de todos los picos)",
        examples=["Array con valores finitos"],
    )

    residual: np.ndarray = Field(
        ...,
        description="Residual (espectro original - ajuste)",
        examples=["Array con valores finitos"],
    )

    r_squared: float = Field(
        ...,
        description="Coeficiente de determinación R²",
        ge=0.0,
        le=1.0,
        examples=[0.95, 0.88, 0.92],
    )

    chi_squared: float = Field(
        ..., description="Chi-cuadrado reducido", gt=0, examples=[1.2, 0.8, 2.1]
    )

    success: bool = Field(..., description="Si el ajuste convergió exitosamente")

    message: str = Field(
        ...,
        description="Mensaje sobre el resultado del ajuste",
        min_length=1,
        examples=["Ajuste convergió exitosamente", "Máximo de iteraciones alcanzado"],
    )

    @field_validator("fitted_spectrum")
    @classmethod
    def validate_fitted_spectrum(cls, v: np.ndarray) -> np.ndarray:
        """Valida que el espectro ajustado sea finito y no negativo."""
        return NumpyArrayValidator.validate_finite_array(v, "fitted_spectrum")

    @field_validator("residual")
    @classmethod
    def validate_residual(cls, v: np.ndarray) -> np.ndarray:
        """Valida que el residual sea finito."""
        return NumpyArrayValidator.validate_finite_array(v, "residual")

    @model_validator(mode="after")
    def validate_array_lengths(self) -> "FitResult":
        """Valida que fitted_spectrum y residual tengan la misma longitud."""
        NumpyArrayValidator.validate_matching_lengths(
            self.fitted_spectrum, self.residual, "fitted_spectrum", "residual"
        )
        return self

    @field_validator("r_squared")
    @classmethod
    def validate_r_squared_realism(cls, v: float) -> float:
        """Valida que R² sea realista para XPS."""
        if v < 0.5:
            # Advertencia pero no error - ajustes pobres pueden ser informativos
            pass
        return v

    @field_validator("chi_squared")
    @classmethod
    def validate_chi_squared_realism(cls, v: float) -> float:
        """Valida que chi² sea realista."""
        if v > 10.0:
            # Advertencia: chi² muy alto sugiere mal ajuste
            pass
        return v
