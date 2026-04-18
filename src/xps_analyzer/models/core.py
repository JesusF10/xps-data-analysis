"""
Modelos Pydantic para estructuras de datos núcleo de XPS.

Migración de dataclasses -> Pydantic BaseModel para:
- XPSSpectrum ✓
- XPSDataset ✓
- XPSSample ✓

Proporciona validación automática avanzada para los datos fundamentales de XPS.
"""

from __future__ import annotations

from typing import Any

from .base import NumpyArrayValidator, XPSBaseModel, XPSValidators

import numpy as np
import pandas as pd
from pydantic import Field, field_validator, model_validator


class XPSSpectrum(XPSBaseModel):
    """
    Representa un espectro XPS individual con validación automática completa.

    Valida automáticamente que las energías de enlace y las intensidades
    sean consistentes, finitas y físicamente realistas para XPS.

    Parámetros
    ----------
    region_name : str
        Nombre de la región espectral (ej: "C 1s", "survey"). No puede estar vacío.
    binding_energy : np.ndarray
        Array de energías de enlace en eV. Debe ser creciente y positivo.
    intensity : np.ndarray
        Array de intensidades en cuentas. Debe ser finito y no negativo.
    metadata : dict[str, Any]
        Metadata adicional del espectro (condiciones de medición, etc.).

    Ejemplos
    --------
    >>> # Espectro básico
    >>> energies = np.array([280.0, 285.0, 290.0])
    >>> intensities = np.array([100.0, 1000.0, 200.0])
    >>> spectrum = XPSSpectrum(
    ...     region_name="C 1s",
    ...     binding_energy=energies,
    ...     intensity=intensities,
    ...     metadata={"pass_energy": 20}
    ... )
    >>>
    >>> # Acceso a datos
    >>> df = spectrum.data  # DataFrame con binding_energy como índice
    >>> copy_spec = spectrum.copy()  # Copia completa
    """

    region_name: str = Field(
        ...,
        description="Nombre de la región espectral",
        min_length=1,
        examples=["C 1s", "O 1s", "survey", "Ti 2p"],
    )

    binding_energy: np.ndarray = Field(
        ..., description="Array de energías de enlace en eV"
    )

    intensity: np.ndarray = Field(..., description="Array de intensidades en cuentas")

    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata adicional del espectro"
    )

    @field_validator("region_name")
    @classmethod
    def validate_region_name_format(cls, v: str) -> str:
        """Valida formato del nombre de región."""
        return XPSValidators.validate_region_name(v)

    @field_validator("binding_energy")
    @classmethod
    def validate_binding_energy_array(cls, v: np.ndarray) -> np.ndarray:
        """Valida array de energías de enlace."""
        validated = XPSValidators.validate_binding_energy(v)

        # Validaciones adicionales específicas para XPS
        if len(validated) < 2:
            raise ValueError("binding_energy debe tener al menos 2 puntos")

        # Verificar que esté aproximadamente ordenado (tolerancia para ruido)
        diffs = np.diff(validated)
        if np.sum(diffs < 0) > len(diffs) * 0.1:  # Máximo 10% decrementos
            raise ValueError(
                "binding_energy debe estar aproximadamente en orden creciente"
            )

        return validated

    @field_validator("intensity")
    @classmethod
    def validate_intensity_array(cls, v: np.ndarray) -> np.ndarray:
        """Valida array de intensidades."""
        return XPSValidators.validate_intensity(v)

    @model_validator(mode="after")
    def validate_array_consistency(self) -> XPSSpectrum:
        """Valida consistencia entre arrays."""
        NumpyArrayValidator.validate_matching_lengths(
            self.binding_energy, self.intensity, "binding_energy", "intensity"
        )
        return self

    @model_validator(mode="after")
    def validate_realistic_data_range(self) -> XPSSpectrum:
        """Valida que los datos estén en rangos físicamente realistas."""
        # Energías de enlace típicas en XPS: 0-2000 eV
        if self.binding_energy.max() > 2000:
            raise ValueError(
                f"binding_energy máxima ({self.binding_energy.max():.1f}) "
                f"excede rango típico de XPS (0-2000 eV)"
            )

        # Rango de energía debe ser razonable (mínimo 1 eV)
        energy_range = self.binding_energy.max() - self.binding_energy.min()
        if energy_range < 1.0:
            raise ValueError(
                f"Rango de energía ({energy_range:.2f} eV) muy pequeño. "
                f"Mínimo 1.0 eV requerido"
            )

        # Intensidades muy altas pueden indicar problemas
        if self.intensity.max() > 1e6:
            # Advertencia, no error
            pass

        return self

    @property
    def data(self) -> pd.DataFrame:
        """
        Retorna los datos como DataFrame con binding_energy como índice.

        Retorna
        -------
        pd.DataFrame
            DataFrame con columna 'intensity' e índice 'binding_energy'.
        """
        return pd.DataFrame(
            {"binding_energy": self.binding_energy, "intensity": self.intensity}
        ).set_index("binding_energy")

    def copy(self) -> XPSSpectrum:
        """
        Retorna una copia completa del espectro.

        Retorna
        -------
        XPSSpectrum
            Copia independiente del espectro.
        """
        return XPSSpectrum(
            region_name=self.region_name,
            binding_energy=self.binding_energy.copy(),
            intensity=self.intensity.copy(),
            metadata=self.metadata.copy(),
        )

    def get_energy_range(self) -> tuple[float, float]:
        """
        Obtiene el rango de energías de enlace.

        Retorna
        -------
        tuple[float, float]
            (energía_mínima, energía_máxima) en eV.
        """
        return (float(self.binding_energy.min()), float(self.binding_energy.max()))

    def get_intensity_stats(self) -> dict[str, float]:
        """
        Obtiene estadísticas básicas de intensidad.

        Retorna
        -------
        dict[str, float]
            Diccionario con estadísticas: max, min, mean, std.
        """
        return {
            "max": float(self.intensity.max()),
            "min": float(self.intensity.min()),
            "mean": float(self.intensity.mean()),
            "std": float(self.intensity.std()),
        }


class XPSDataset(XPSBaseModel):
    """
    Representa un archivo XPS completo con múltiples espectros.

    Valida automáticamente que el dataset contenga espectros válidos,
    nombres de archivo apropiados y metadata consistente.

    Parámetros
    ----------
    filename : str
        Nombre del archivo. Debe ser no vacío y válido.
    header : dict[str, Any]
        Metadata del archivo (condiciones instrumentales, fecha, etc.).
    spectra : dict[str, XPSSpectrum]
        Diccionario de espectros indexados por nombre de región.

    Ejemplos
    --------
    >>> # Dataset básico
    >>> spectrum = XPSSpectrum(...)
    >>> dataset = XPSDataset(
    ...     filename="sample1.txt",
    ...     header={"date": "2024-03-15", "operator": "researcher"},
    ...     spectra={"C 1s": spectrum}
    ... )
    >>>
    >>> # Acceso a espectros
    >>> c1s = dataset.get_spectrum("C 1s")
    >>> regions = dataset.list_regions()
    """

    filename: str = Field(
        ...,
        description="Nombre del archivo fuente",
        min_length=1,
        examples=["sample1.txt", "data_multiplex.txt", "survey_scan.dat"],
    )

    header: dict[str, Any] = Field(
        default_factory=dict, description="Metadata del archivo completo"
    )

    spectra: dict[str, XPSSpectrum] = Field(
        ..., description="Diccionario de espectros por región", min_length=1
    )

    @field_validator("filename")
    @classmethod
    def validate_filename_format(cls, v: str) -> str:
        """Valida formato básico del filename."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("filename no puede estar vacío")

        # Validación básica de caracteres
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in cleaned for char in invalid_chars):
            raise ValueError(f"filename contiene caracteres inválidos: {invalid_chars}")

        return cleaned

    @model_validator(mode="after")
    def validate_spectra_consistency(self) -> XPSDataset:
        """Valida consistencia entre espectros y claves del diccionario."""
        for region_name, spectrum in self.spectra.items():
            if region_name != spectrum.region_name:
                raise ValueError(
                    f"Inconsistencia: clave '{region_name}' no coincide "
                    f"con spectrum.region_name '{spectrum.region_name}'"
                )
        return self

    def get_spectrum(self, region_name: str) -> XPSSpectrum | None:
        """
        Obtiene un espectro específico por nombre de región.

        Parámetros
        ----------
        region_name : str
            Nombre de la región a buscar.

        Retorna
        -------
        XPSSpectrum | None
            Espectro encontrado o None si no existe.
        """
        return self.spectra.get(region_name)

    def list_regions(self) -> list[str]:
        """
        Lista todas las regiones espectrales disponibles.

        Retorna
        -------
        list[str]
            Lista de nombres de regiones ordenada alfabéticamente.
        """
        return sorted(self.spectra.keys())

    def copy(self) -> XPSDataset:
        """
        Retorna una copia completa del dataset.

        Retorna
        -------
        XPSDataset
            Copia independiente del dataset.
        """
        return XPSDataset(
            filename=self.filename,
            header=self.header.copy(),
            spectra={name: spec.copy() for name, spec in self.spectra.items()},
        )

    def get_statistics(self) -> dict[str, Any]:
        """
        Obtiene estadísticas del dataset completo.

        Retorna
        -------
        dict[str, Any]
            Diccionario con estadísticas: número de espectros, rangos, etc.
        """
        total_points = sum(len(spec.binding_energy) for spec in self.spectra.values())

        energy_ranges = [spec.get_energy_range() for spec in self.spectra.values()]
        global_min = min(er[0] for er in energy_ranges)
        global_max = max(er[1] for er in energy_ranges)

        return {
            "total_spectra": len(self.spectra),
            "total_data_points": total_points,
            "energy_range": (global_min, global_max),
            "regions": list(self.spectra.keys()),
            "filename": self.filename,
        }


class XPSSample(XPSBaseModel):
    """
    Representa una muestra XPS completa con múltiples archivos/datasets.

    Valida automáticamente que la muestra tenga datasets válidos y
    nombres apropiados, y proporciona acceso unificado a todos los datos.

    Parámetros
    ----------
    sample_name : str
        Nombre identificador de la muestra. Debe ser no vacío.
    datasets : dict[str, XPSDataset]
        Diccionario de datasets indexados por filename.

    Ejemplos
    --------
    >>> # Muestra con múltiples archivos
    >>> survey_dataset = XPSDataset(...)
    >>> multiplex_dataset = XPSDataset(...)
    >>> sample = XPSSample(
    ...     sample_name="Sample_001",
    ...     datasets={
    ...         "survey.txt": survey_dataset,
    ...         "multiplex.txt": multiplex_dataset
    ...     }
    ... )
    >>>
    >>> # Acceso a datos
    >>> survey = sample.get_dataset("survey.txt")
    >>> all_spectra = sample.get_all_spectra()
    """

    sample_name: str = Field(
        ...,
        description="Nombre identificador de la muestra",
        min_length=1,
        examples=["Sample_001", "Al2O3_thin_film", "polymer_coating"],
    )

    datasets: dict[str, XPSDataset] = Field(
        ..., description="Diccionario de datasets por filename", min_length=1
    )

    @field_validator("sample_name")
    @classmethod
    def validate_sample_name_format(cls, v: str) -> str:
        """Valida formato del nombre de muestra."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("sample_name no puede estar vacío")
        return cleaned

    @model_validator(mode="after")
    def validate_datasets_consistency(self) -> XPSSample:
        """Valida consistencia entre datasets y claves del diccionario."""
        for filename, dataset in self.datasets.items():
            if filename != dataset.filename:
                raise ValueError(
                    f"Inconsistencia: clave '{filename}' no coincide "
                    f"con dataset.filename '{dataset.filename}'"
                )
        return self

    def get_dataset(self, filename: str) -> XPSDataset | None:
        """
        Obtiene un dataset específico por filename.

        Parámetros
        ----------
        filename : str
            Nombre del archivo del dataset.

        Retorna
        -------
        XPSDataset | None
            Dataset encontrado o None si no existe.
        """
        return self.datasets.get(filename)

    def list_datasets(self) -> list[str]:
        """
        Lista todos los filenames de datasets disponibles.

        Retorna
        -------
        list[str]
            Lista de filenames ordenada alfabéticamente.
        """
        return sorted(self.datasets.keys())

    def get_all_spectra(self) -> dict[str, dict[str, XPSSpectrum]]:
        """
        Obtiene todos los espectros organizados por dataset y región.

        Retorna
        -------
        dict[str, dict[str, XPSSpectrum]]
            Diccionario anidado: {filename: {region: spectrum}}.
        """
        return {
            filename: dataset.spectra for filename, dataset in self.datasets.items()
        }

    def find_spectra_by_region(self, region_name: str) -> dict[str, XPSSpectrum]:
        """
        Busca espectros de una región específica en todos los datasets.

        Parámetros
        ----------
        region_name : str
            Nombre de la región a buscar.

        Retorna
        -------
        dict[str, XPSSpectrum]
            Diccionario {filename: spectrum} para la región especificada.
        """
        result = {}
        for filename, dataset in self.datasets.items():
            spectrum = dataset.get_spectrum(region_name)
            if spectrum is not None:
                result[filename] = spectrum
        return result

    def get_sample_statistics(self) -> dict[str, Any]:
        """
        Obtiene estadísticas completas de la muestra.

        Retorna
        -------
        dict[str, Any]
            Diccionario con estadísticas agregadas de todos los datasets.
        """
        total_datasets = len(self.datasets)
        total_spectra = sum(len(ds.spectra) for ds in self.datasets.values())
        total_points = sum(
            sum(len(spec.binding_energy) for spec in ds.spectra.values())
            for ds in self.datasets.values()
        )

        # Recopilar todas las regiones únicas
        all_regions = set()
        for dataset in self.datasets.values():
            all_regions.update(dataset.spectra.keys())

        return {
            "sample_name": self.sample_name,
            "total_datasets": total_datasets,
            "total_spectra": total_spectra,
            "total_data_points": total_points,
            "unique_regions": sorted(all_regions),
            "dataset_filenames": list(self.datasets.keys()),
        }
