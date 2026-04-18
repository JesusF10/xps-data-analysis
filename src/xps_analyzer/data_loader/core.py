"""
Funciones principales de carga de datos XPS.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from xps_analyzer.utils.models import XPSBaseModel

import numpy as np
import pandas as pd
from pydantic import field_validator, model_validator


class XPSSpectrum(XPSBaseModel):
    """Representa un espectro XPS individual."""

    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any]

    @field_validator("binding_energy", "intensity")
    @classmethod
    def validate_arrays(cls, v: np.ndarray) -> np.ndarray:
        """Validar que los campos sean arrays de NumPy y no estén vacíos."""
        if not isinstance(v, np.ndarray):
            raise TypeError(
                f"El campo debe ser un numpy.ndarray, no {type(v).__name__}"
            )
        if len(v) == 0:
            raise ValueError("Los arrays no pueden estar vacíos")
        return v

    @field_validator("binding_energy")
    @classmethod
    def validate_positive_energies(cls, v: np.ndarray) -> np.ndarray:
        """Validar que las energías sean positivas."""
        if np.any(v < 0):
            raise ValueError("Los valores de binding_energy deben ser positivos")
        return v

    @field_validator("region_name")
    @classmethod
    def validate_region_name(cls, v: str) -> str:
        """Validar que el nombre de la región no esté vacío."""
        if not v or not v.strip():
            raise ValueError("region_name no puede estar vacío")
        return v

    @model_validator(mode="after")
    def validate_matching_lengths(self) -> XPSSpectrum:
        """Validar que los arrays tengan la misma longitud."""
        if len(self.binding_energy) != len(self.intensity):
            raise ValueError(
                f"binding_energy ({len(self.binding_energy)} puntos) e intensity "
                f"({len(self.intensity)} puntos) deben tener la misma longitud"
            )
        return self

    @property
    def data(self) -> pd.DataFrame:
        """Retorna los datos como DataFrame."""
        return pd.DataFrame(
            {"binding_energy": self.binding_energy, "intensity": self.intensity}
        ).set_index("binding_energy")


class XPSDataset(XPSBaseModel):
    """Representa un archivo XPS completo."""

    filename: str
    header: dict[str, Any]
    spectra: dict[str, XPSSpectrum]

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validar que el nombre de archivo no esté vacío."""
        if not v or not v.strip():
            raise ValueError("filename no puede estar vacío")
        return v

    @field_validator("spectra")
    @classmethod
    def validate_spectra(cls, v: dict[str, XPSSpectrum]) -> dict[str, XPSSpectrum]:
        """Validar que el diccionario de espectros no esté vacío."""
        if not v:
            raise ValueError(
                "spectra no puede estar vacío - debe contener al menos un espectro"
            )
        return v

    def get_spectrum(self, region_name: str) -> XPSSpectrum | None:
        """Obtiene un espectro específico."""
        return self.spectra.get(region_name)

    def list_regions(self) -> list:
        """Lista todas las regiones disponibles."""
        return list(self.spectra.keys())


class XPSSample(XPSBaseModel):
    """Representa una muestra XPS que puede contener múltiples archivos."""

    sample_name: str
    datasets: dict[str, XPSDataset]

    @field_validator("sample_name")
    @classmethod
    def validate_sample_name(cls, v: str) -> str:
        """Validar que el nombre de muestra no esté vacío."""
        if not v or not v.strip():
            raise ValueError("sample_name no puede estar vacío")
        return v

    @field_validator("datasets")
    @classmethod
    def validate_datasets(cls, v: dict[str, XPSDataset]) -> dict[str, XPSDataset]:
        """Validar que el diccionario de datasets no esté vacío."""
        if not v:
            raise ValueError(
                "datasets no puede estar vacío - debe contener al menos un dataset"
            )
        return v

    def get_dataset(self, filename: str) -> XPSDataset | None:
        """Obtiene un dataset específico.

        Parameters
        ----------
        filename : str
            Nombre del archivo del dataset a obtener.
        Returns
        -------
        XPSDataset | None
            El dataset correspondiente o None si no existe.
        """
        return self.datasets.get(filename)

    def list_datasets(self) -> list:
        """Lista todos los datasets disponibles.

        Returns
        -------
        list
            Lista de nombres de archivos de los datasets.
        """
        return list(self.datasets.keys())


def parse_metadata(lines: list | str, header: bool = False) -> dict[str, Any]:
    """
    Parsea las líneas de metadatos y retorna un diccionario.
    ----------

    Parameters
    ----------
    lines : [list, str]
        Líneas de texto que contienen metadatos.
    header : bool, default=False
        Si True, parsea metadatos globales, de otro modo, parsea metadatos locales
        (del espectro).
    Returns
    -------
    dict[str, str]
        Diccionario con pares clave-valor de metadatos.

    Raises
    ------
    ValueError
        Si los metadatos están malformados o incompletos.
    -------
    Examples
    --------
    >>> lines = ["Sample Name Sample1; Date 2023-10-01; Operator John Doe;",
    ...          "C 1s O 1s N 1s;",
    ...          "284.8 531.0 399.0;"]
    >>> metadata = parse_metadata(lines, header=True)
    >>> print(metadata)
    {'Sample_Name': 'Sample1', 'Date': '2023-10-01', 'Operator': 'John Doe',
     'elements': {'C': {'orbital': '1s', 'mean_energy': '284.8'},
                  'O': {'orbital': '1s', 'mean_energy': '531.0'},
                  'N': {'orbital': '1s', 'mean_energy': '399.0'}}}
    >>> lines = "Element C 1s; Region 1; Depth Cycle 1 of 3; Time Per Step 50; Sweeps 5; Anode Al Kα; Photon energy 1486.6;"
    >>> metadata = parse_metadata(lines, header=False)
    >>> print(metadata)
    {'element': 'C 1s', 'region': 1, 'depth_cycle': (1, 3), 'time_per_step': 50,
     'sweeps': 5, 'anode': 'Al Kα', 'photon_energy': 1486.6}
    """
    metadata = {}

    if header:
        try:
            for meta_line in lines[0].split(";")[:-2]:
                key = "_".join(meta_line.split()[:-1])
                value = meta_line.split()[-1].strip()
                metadata[key] = value

            elements = {}
            # Línea 2: elementos separados por tabs (ej: "Bi 4f\tNa 1s\t...")
            # Línea 3: energías separadas por tabs (ej: "4767.5\t2226.25\t...")
            elements_list = [e.strip() for e in lines[1].split("\t") if e.strip()]
            energies_list = [e.strip() for e in lines[2].split("\t") if e.strip()]

            for element_full, energy in zip(elements_list, energies_list, strict=True):
                # Separar elemento y orbital (ej: "Bi 4f" -> "Bi", "4f")
                parts = element_full.split()
                if len(parts) == 2:
                    elem, orbital = parts
                    elements[elem] = {"orbital": orbital, "mean_energy": energy}
                else:
                    # Fallback si formato es diferente
                    elements[element_full] = {
                        "orbital": "unknown",
                        "mean_energy": energy,
                    }
            metadata["elements"] = elements
        except (IndexError, ValueError, KeyError) as e:
            raise ValueError(
                f"Error al parsear metadatos del header: {e}. "
                f"Formato esperado: 3 líneas con información de muestra, elementos y energías"
            ) from e
        return metadata

    elif isinstance(lines, str) and lines.split()[0] == "Element":
        try:
            lines = lines.split(";")
            if len(lines[0].split()) < 2:
                metadata["element"] = "survey"
            else:
                metadata["element"] = " ".join(lines[0].split()[1:])
            # Region
            metadata["region"] = int(lines[1].split()[1])
            # Depth cycle
            metadata["depth_cycle"] = (
                int(lines[2].split()[2]),
                int(lines[2].split()[4]),
            )
            # Time Per Step
            metadata["time_per_step"] = int(lines[3].split()[-1])
            # Sweeps
            metadata["sweeps"] = int(lines[4].split()[-1])
            # Anode
            metadata["anode"] = lines[5].split()[-1]
            # Photon energy
            metadata["photon_energy"] = float(lines[6].split()[-1])
        except (IndexError, ValueError, KeyError) as e:
            raise ValueError(
                f"Error al parsear metadatos del espectro: {e}. "
                f"Formato esperado: 'Element X; Region N; Depth Cycle N of M; ...'"
            ) from e

    return metadata


def get_spectrum_data(data_lines: list) -> XPSSpectrum:
    """
    Extrae los datos del espectro de las líneas proporcionadas.
    Parameters
    ----------
    data_lines : list
        Líneas de texto que contienen los datos del espectro.
    Returns
    -------
    XPSSpectrum
        Objeto XPSSpectrum con los datos del espectro.

    Raises
    ------
    ValueError
        Si los datos están malformados o incompletos.
    """
    if not data_lines or len(data_lines) < 2:
        raise ValueError(
            "data_lines debe contener al menos 2 líneas (metadata + datos)"
        )

    binding_energy = []
    intensity = []

    try:
        metadata = parse_metadata(data_lines[0], header=False)
    except (IndexError, ValueError, KeyError) as e:
        raise ValueError(f"Error al parsear metadata del espectro: {e}") from e

    for line_num, line in enumerate(data_lines[1:], start=2):
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(
                f"Línea {line_num} malformada: se esperan 2 columnas "
                f"(binding_energy intensity), se encontraron {len(parts)}"
            )
        try:
            binding_energy.append(float(parts[0]))
            intensity.append(float(parts[1]))
        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Error al convertir datos numéricos en línea {line_num}: {e}"
            ) from e

    # Validación antes de crear el objeto
    if len(binding_energy) == 0:
        raise ValueError("No se encontraron puntos de datos en el espectro")

    if len(binding_energy) != len(intensity):
        raise ValueError(
            f"Desajuste de datos: {len(binding_energy)} valores de energía "
            f"pero {len(intensity)} valores de intensidad"
        )

    spectrum = XPSSpectrum(
        region_name=metadata.get("element", "unknown"),
        binding_energy=np.array(binding_energy),
        intensity=np.array(intensity),
        metadata=metadata,
    )

    return spectrum


def load_single_file(filepath: str | Path) -> XPSDataset:
    """
    Carga un solo archivo de datos XPS.
    Parameters
    ----------
    filepath : str or Path
        Ruta al archivo de datos XPS.
    Returns
    -------
    XPSDataset
        Objeto XPSDataset con los datos cargados.
    """
    survey = True
    header = {}

    if isinstance(filepath, str):
        filepath = Path(filepath)

    with open(filepath, encoding="latin-1") as file:
        data = file.readlines()
        data = [line.strip() for line in data if line.strip()]

        if "multiplex" in filepath.name.lower():
            survey = False
            print("Archivo multiplex detectado")
            header = parse_metadata(data[:3], header=True)
            data = data[3:]

        if survey:
            spectrum = get_spectrum_data(data)
            dataset = XPSDataset(
                filename=filepath.name, header=header, spectra={"survey": spectrum}
            )
        else:
            # Procesar múltiples regiones
            spectra = {}
            i = 0
            while i < len(data):
                if data[i].startswith("Element"):
                    region_lines = []
                    # Recolectar todas las líneas hasta la siguiente región o EOF
                    while i < len(data) and (
                        not data[i].startswith("Element") or len(region_lines) == 0
                    ):
                        region_lines.append(data[i])
                        i += 1
                    spectrum = get_spectrum_data(region_lines)
                    spectra[spectrum.region_name] = spectrum
                else:
                    i += 1
            dataset = XPSDataset(filename=filepath.name, header=header, spectra=spectra)

    return dataset


def load_all_data(
    data_path: str | Path, recursive: bool = True
) -> dict[str, XPSDataset]:
    """
    Carga todos los archivos de datos XPS desde un directorio.

    Parameters
    ----------
    data_path : str or Path
        Ruta al directorio que contiene los datos XPS.
    recursive : bool, default=True
        Si True, busca archivos recursivamente en subdirectorios.

    Returns
    -------
    dict[str, XPSDataset]
        Diccionario con los datos cargados. Las claves son los nombres
        de archivo y los valores son los XPSDataset procesados.

    Raises
    ------
    FileNotFoundError
        Si el directorio no existe.
    ValueError
        Si la ruta no es un directorio.

    Examples
    --------
    >>> data = load_all_data("data/raw/samples/")
    >>> print(f"Cargados {len(data)} archivos")
    >>> for filename, dataset in data.items():
    ...     print(f"{filename}: {len(dataset.spectra)} espectros")
    """
    directory = Path(data_path)

    # Validar que el directorio existe
    if not directory.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {directory}")

    if not directory.is_dir():
        raise ValueError(f"La ruta no es un directorio: {directory}")

    datasets = {}
    errors = []

    # Buscar archivos recursivamente o no
    if recursive:
        pattern = directory.rglob("*.txt")
    else:
        pattern = directory.glob("*.txt")

    # Cargar cada archivo encontrado
    for filepath in pattern:
        try:
            dataset = load_single_file(filepath)
            datasets[filepath.name] = dataset
        except Exception as e:
            # Guardar errores pero continuar con otros archivos
            errors.append((filepath.name, str(e)))

    # Reportar errores al usuario si hubo alguno
    if errors:
        print(f"Advertencia: {len(errors)} archivo(s) no pudieron cargarse:")
        for filename, error in errors[:5]:  # Mostrar solo primeros 5
            print(f"  - {filename}: {error}")
        if len(errors) > 5:
            print(f"  ... y {len(errors) - 5} más")

    return datasets


def detect_file_format(filepath: str | Path) -> str | None:
    """
    Detecta automáticamente el formato del archivo XPS.

    Parameters
    ----------
    filepath : str or Path
        Ruta al archivo a analizar.

    Returns
    -------
    str | None
        Tipo de formato detectado:
        - "multiplex": Formato multiplex propietario
        - "survey": Formato survey simple
        - "text": Formato de texto genérico
        - None: Formato no reconocido

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.

    Examples
    --------
    >>> fmt = detect_file_format("data/sample_multiplex.txt")
    >>> print(f"Formato detectado: {fmt}")
    Formato detectado: multiplex
    """
    filepath = Path(filepath)

    # Validar que el archivo existe
    if not filepath.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    try:
        # Leer primeras 10 líneas para análisis
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            first_lines = [f.readline().strip() for _ in range(10)]

        # Concatenar para búsqueda
        content = "\n".join(first_lines)

        # Detección por nombre de archivo
        filename_lower = filepath.name.lower()
        if "multiplex" in filename_lower:
            return "multiplex"

        # Detección por estructura de contenido
        # Formato multiplex tiene múltiples secciones "Element"
        element_count = content.count("Element")
        if element_count >= 2:
            return "multiplex"

        # Si tiene separadores ";" típicos del formato propietario
        if any(";" in line for line in first_lines):
            # Si solo hay una sección, es survey
            if element_count <= 1:
                return "survey"
            return "text"

        # Formato no reconocido
        return None

    except UnicodeDecodeError:
        # Archivo binario - formato no soportado
        return None
    except Exception:
        return None
