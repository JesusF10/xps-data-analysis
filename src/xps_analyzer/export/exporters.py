"""
Funciones de exportación de datos XPS a diferentes formatos.

Este módulo proporciona funciones para exportar espectros XPS y resultados
de análisis a formatos comunes como CSV, Excel y JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from xps_analyzer.data_loader import XPSDataset, XPSSpectrum


def export_to_csv(
    data: XPSSpectrum | XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True,
    decimal_places: int = 6,
) -> Path:
    """
    Exporta espectro o dataset XPS a archivo CSV.

    Si se proporciona un XPSSpectrum, crea un archivo CSV con dos columnas
    (binding_energy, intensity). Si se proporciona un XPSDataset, crea un
    archivo CSV por cada espectro en subdirectorios organizados.

    Parámetros
    ----------
    data : XPSSpectrum | XPSDataset
        Espectro individual o dataset completo a exportar.
    output_path : str | Path
        Ruta del archivo de salida. Para datasets, será el directorio base.
    include_metadata : bool, default True
        Si True, incluye archivo separado con metadata en formato CSV.
    decimal_places : int, default 6
        Número de decimales para valores numéricos.

    Retorna
    -------
    Path
        Ruta del archivo (o directorio) creado.

    Raises
    ------
    TypeError
        Si data no es XPSSpectrum ni XPSDataset.
    ValueError
        Si output_path existe y es un archivo cuando se exporta XPSDataset.

    Ejemplos
    --------
    >>> from xps_analyzer import load_single_file
    >>> from xps_analyzer.export import export_to_csv
    >>> dataset = load_single_file("muestra.txt")
    >>> spectrum = dataset.spectra["C 1s"]
    >>>
    >>> # Exportar espectro individual
    >>> export_to_csv(spectrum, "output/c1s.csv")
    PosixPath('output/c1s.csv')
    >>>
    >>> # Exportar dataset completo
    >>> export_to_csv(dataset, "output/muestra/", include_metadata=True)
    PosixPath('output/muestra/')

    Referencias
    -----------
    - Formato CSV estándar (RFC 4180)
    """
    output_path = Path(output_path)

    if isinstance(data, XPSSpectrum):
        return _export_spectrum_to_csv(
            data, output_path, include_metadata, decimal_places
        )
    elif isinstance(data, XPSDataset):
        return _export_dataset_to_csv(
            data, output_path, include_metadata, decimal_places
        )
    else:
        raise TypeError(
            f"data debe ser XPSSpectrum o XPSDataset, no {type(data).__name__}"
        )


def _export_spectrum_to_csv(
    spectrum: XPSSpectrum,
    output_path: Path,
    include_metadata: bool,
    decimal_places: int,
) -> Path:
    """Exporta un espectro individual a CSV."""
    # Crear directorio padre si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Crear DataFrame con los datos
    df = pd.DataFrame(
        {
            "binding_energy": spectrum.binding_energy,
            "intensity": spectrum.intensity,
        }
    )

    # Exportar datos
    df.to_csv(output_path, index=False, float_format=f"%.{decimal_places}f")

    # Exportar metadata si se solicita
    if include_metadata and spectrum.metadata:
        metadata_path = output_path.with_suffix(".metadata.csv")
        metadata_df = pd.DataFrame(
            [{"key": k, "value": str(v)} for k, v in spectrum.metadata.items()]
        )
        metadata_df.to_csv(metadata_path, index=False)

    return output_path


def _export_dataset_to_csv(
    dataset: XPSDataset,
    output_path: Path,
    include_metadata: bool,
    decimal_places: int,
) -> Path:
    """Exporta un dataset completo a múltiples archivos CSV."""
    # Crear directorio de salida
    output_path.mkdir(parents=True, exist_ok=True)

    # Exportar cada espectro
    for region_name, spectrum in dataset.spectra.items():
        # Crear nombre de archivo seguro (reemplazar espacios y caracteres especiales)
        safe_name = region_name.replace(" ", "_").replace("/", "_")
        spectrum_path = output_path / f"{safe_name}.csv"

        _export_spectrum_to_csv(
            spectrum,
            spectrum_path,
            include_metadata=False,
            decimal_places=decimal_places,
        )

    # Exportar metadata del dataset
    if include_metadata:
        # Metadata del header
        if dataset.header:
            header_path = output_path / "dataset_metadata.csv"
            header_df = pd.DataFrame(
                [{"key": k, "value": str(v)} for k, v in dataset.header.items()]
            )
            header_df.to_csv(header_path, index=False)

        # Metadata de cada espectro
        all_metadata = []
        for region_name, spectrum in dataset.spectra.items():
            for key, value in spectrum.metadata.items():
                all_metadata.append(
                    {"region": region_name, "key": key, "value": str(value)}
                )

        if all_metadata:
            spectra_metadata_path = output_path / "spectra_metadata.csv"
            spectra_df = pd.DataFrame(all_metadata)
            spectra_df.to_csv(spectra_metadata_path, index=False)

    return output_path


def export_to_excel(
    data: XPSSpectrum | XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True,
    decimal_places: int = 6,
) -> Path:
    """
    Exporta espectro o dataset XPS a archivo Excel (.xlsx).

    Crea un archivo Excel con múltiples hojas:
    - Para XPSSpectrum: hoja "Data" con datos, hoja "Metadata" opcional
    - Para XPSDataset: una hoja por espectro + hojas de metadata

    Parámetros
    ----------
    data : XPSSpectrum | XPSDataset
        Espectro individual o dataset completo a exportar.
    output_path : str | Path
        Ruta del archivo Excel de salida (debe terminar en .xlsx).
    include_metadata : bool, default True
        Si True, incluye hojas con metadata.
    decimal_places : int, default 6
        Número de decimales para valores numéricos.

    Retorna
    -------
    Path
        Ruta del archivo Excel creado.

    Raises
    ------
    TypeError
        Si data no es XPSSpectrum ni XPSDataset.
    ValueError
        Si output_path no termina en .xlsx.

    Ejemplos
    --------
    >>> from xps_analyzer import load_single_file
    >>> from xps_analyzer.export import export_to_excel
    >>> dataset = load_single_file("muestra.txt")
    >>>
    >>> # Exportar dataset completo a Excel
    >>> export_to_excel(dataset, "output/muestra.xlsx", include_metadata=True)
    PosixPath('output/muestra.xlsx')
    >>>
    >>> # Estructura del archivo Excel:
    >>> # - Hoja "C_1s": datos del espectro C 1s
    >>> # - Hoja "O_1s": datos del espectro O 1s
    >>> # - Hoja "Dataset_Metadata": metadata del dataset
    >>> # - Hoja "Spectra_Metadata": metadata de cada espectro

    Notas
    -----
    - Requiere la librería openpyxl instalada.
    - Los nombres de hojas tienen límite de 31 caracteres (Excel).
    - Caracteres especiales en nombres de región se reemplazan por "_".

    Referencias
    -----------
    - Formato Office Open XML (ECMA-376)
    """
    output_path = Path(output_path)

    # Validar extensión
    if output_path.suffix.lower() != ".xlsx":
        raise ValueError(f"output_path debe terminar en .xlsx, no {output_path.suffix}")

    # Crear directorio padre si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(data, XPSSpectrum):
        return _export_spectrum_to_excel(
            data, output_path, include_metadata, decimal_places
        )
    elif isinstance(data, XPSDataset):
        return _export_dataset_to_excel(
            data, output_path, include_metadata, decimal_places
        )
    else:
        raise TypeError(
            f"data debe ser XPSSpectrum o XPSDataset, no {type(data).__name__}"
        )


def _export_spectrum_to_excel(
    spectrum: XPSSpectrum,
    output_path: Path,
    include_metadata: bool,
    decimal_places: int,
) -> Path:
    """Exporta un espectro individual a Excel."""
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Hoja de datos
        df = pd.DataFrame(
            {
                "binding_energy": np.round(spectrum.binding_energy, decimal_places),
                "intensity": np.round(spectrum.intensity, decimal_places),
            }
        )
        df.to_excel(writer, sheet_name="Data", index=False)

        # Hoja de metadata
        if include_metadata and spectrum.metadata:
            metadata_df = pd.DataFrame(
                [{"key": k, "value": str(v)} for k, v in spectrum.metadata.items()]
            )
            metadata_df.to_excel(writer, sheet_name="Metadata", index=False)

    return output_path


def _export_dataset_to_excel(
    dataset: XPSDataset,
    output_path: Path,
    include_metadata: bool,
    decimal_places: int,
) -> Path:
    """Exporta un dataset completo a Excel con múltiples hojas."""
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Hoja por cada espectro
        for region_name, spectrum in dataset.spectra.items():
            # Nombre de hoja seguro (max 31 caracteres, sin caracteres especiales)
            safe_name = (
                region_name.replace(" ", "_").replace("/", "_").replace(":", "_")[:31]
            )

            df = pd.DataFrame(
                {
                    "binding_energy": np.round(spectrum.binding_energy, decimal_places),
                    "intensity": np.round(spectrum.intensity, decimal_places),
                }
            )
            df.to_excel(writer, sheet_name=safe_name, index=False)

        # Hojas de metadata
        if include_metadata:
            # Metadata del dataset
            if dataset.header:
                header_df = pd.DataFrame(
                    [{"key": k, "value": str(v)} for k, v in dataset.header.items()]
                )
                header_df.to_excel(writer, sheet_name="Dataset_Metadata", index=False)

            # Metadata de espectros
            all_metadata = []
            for region_name, spectrum in dataset.spectra.items():
                for key, value in spectrum.metadata.items():
                    all_metadata.append(
                        {"region": region_name, "key": key, "value": str(value)}
                    )

            if all_metadata:
                spectra_df = pd.DataFrame(all_metadata)
                spectra_df.to_excel(writer, sheet_name="Spectra_Metadata", index=False)

    return output_path


def export_to_json(
    data: XPSSpectrum | XPSDataset,
    output_path: str | Path,
    include_metadata: bool = True,
    indent: int = 2,
) -> Path:
    """
    Exporta espectro o dataset XPS a archivo JSON.

    Crea un archivo JSON con estructura jerárquica que incluye datos y metadata.
    Los arrays NumPy se convierten a listas para compatibilidad JSON.

    Parámetros
    ----------
    data : XPSSpectrum | XPSDataset
        Espectro individual o dataset completo a exportar.
    output_path : str | Path
        Ruta del archivo JSON de salida.
    include_metadata : bool, default True
        Si True, incluye campos de metadata en el JSON.
    indent : int, default 2
        Espacios de indentación para formato legible (None = compacto).

    Retorna
    -------
    Path
        Ruta del archivo JSON creado.

    Raises
    ------
    TypeError
        Si data no es XPSSpectrum ni XPSDataset.

    Ejemplos
    --------
    >>> from xps_analyzer import load_single_file
    >>> from xps_analyzer.export import export_to_json
    >>> dataset = load_single_file("muestra.txt")
    >>>
    >>> # Exportar dataset completo a JSON
    >>> export_to_json(dataset, "output/muestra.json", indent=2)
    PosixPath('output/muestra.json')
    >>>
    >>> # Estructura del JSON:
    >>> # {
    >>> #   "type": "XPSDataset",
    >>> #   "filename": "muestra.txt",
    >>> #   "header": {...},
    >>> #   "spectra": {
    >>> #     "C 1s": {
    >>> #       "region_name": "C 1s",
    >>> #       "binding_energy": [280.0, 281.0, ...],
    >>> #       "intensity": [100.0, 200.0, ...],
    >>> #       "metadata": {...}
    >>> #     },
    >>> #     ...
    >>> #   }
    >>> # }

    Notas
    -----
    - Los arrays NumPy se convierten a listas de Python.
    - Los valores NaN/Inf se convierten a null.
    - El formato JSON es ideal para interoperabilidad con otras herramientas.

    Referencias
    -----------
    - JSON Schema: https://json-schema.org/
    - RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format
    """
    output_path = Path(output_path)

    # Crear directorio padre si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(data, XPSSpectrum):
        json_data = _spectrum_to_dict(data, include_metadata)
    elif isinstance(data, XPSDataset):
        json_data = _dataset_to_dict(data, include_metadata)
    else:
        raise TypeError(
            f"data debe ser XPSSpectrum o XPSDataset, no {type(data).__name__}"
        )

    # Escribir JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=indent, cls=NumpyEncoder)

    return output_path


def _spectrum_to_dict(spectrum: XPSSpectrum, include_metadata: bool) -> dict[str, Any]:
    """Convierte XPSSpectrum a diccionario serializable."""
    data = {
        "type": "XPSSpectrum",
        "region_name": spectrum.region_name,
        "binding_energy": spectrum.binding_energy.tolist(),
        "intensity": spectrum.intensity.tolist(),
        "data_points": len(spectrum.binding_energy),
    }

    if include_metadata and spectrum.metadata:
        data["metadata"] = spectrum.metadata

    return data


def _dataset_to_dict(dataset: XPSDataset, include_metadata: bool) -> dict[str, Any]:
    """Convierte XPSDataset a diccionario serializable."""
    data = {
        "type": "XPSDataset",
        "filename": dataset.filename,
        "num_spectra": len(dataset.spectra),
        "regions": list(dataset.spectra.keys()),
        "spectra": {
            name: _spectrum_to_dict(spec, include_metadata)
            for name, spec in dataset.spectra.items()
        },
    }

    if include_metadata and dataset.header:
        data["header"] = dataset.header

    return data


class NumpyEncoder(json.JSONEncoder):
    """
    Encoder JSON personalizado para manejar tipos NumPy.

    Convierte:
    - np.ndarray -> list
    - np.integer -> int
    - np.floating -> float
    - np.bool_ -> bool
    - np.nan, np.inf -> null
    """

    def default(self, o):
        """Override del método default para tipos NumPy."""
        if isinstance(o, np.ndarray):
            # Convertir array a lista, manejando NaN/Inf
            return [
                None if (isinstance(x, float) and (np.isnan(x) or np.isinf(x))) else x
                for x in o.tolist()
            ]
        elif isinstance(o, (np.integer, int)):
            return int(o)
        elif isinstance(o, (np.floating, float)):
            # Manejar NaN e Inf (tanto np.nan como math.nan)
            if np.isnan(o) or np.isinf(o):
                return None
            return float(o)
        elif isinstance(o, np.bool_):
            return bool(o)
        return super().default(o)
