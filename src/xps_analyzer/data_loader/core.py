"""
Funciones principales de carga de datos XPS.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class XPSSpectrum:
    """Representa un espectro XPS individual."""

    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any]

    def __post_init__(self):
        """Validación básica después de inicialización."""
        # Validar tipos
        if not isinstance(self.binding_energy, np.ndarray):
            raise TypeError("binding_energy debe ser un numpy.ndarray")
        if not isinstance(self.intensity, np.ndarray):
            raise TypeError("intensity debe ser un numpy.ndarray")

        # Validar longitudes coincidentes
        if len(self.binding_energy) != len(self.intensity):
            raise ValueError(
                f"binding_energy ({len(self.binding_energy)} puntos) e intensity "
                f"({len(self.intensity)} puntos) deben tener la misma longitud"
            )

        # Validar que no estén vacíos
        if len(self.binding_energy) == 0:
            raise ValueError("Los arrays no pueden estar vacíos")

        # Validar energías positivas
        if np.any(self.binding_energy < 0):
            raise ValueError("Los valores de binding_energy deben ser positivos")

        # Validar region_name
        if not self.region_name or not self.region_name.strip():
            raise ValueError("region_name no puede estar vacío")

    @property
    def data(self) -> pd.DataFrame:
        """Retorna los datos como DataFrame."""
        return pd.DataFrame(
            {"binding_energy": self.binding_energy, "intensity": self.intensity}
        ).set_index("binding_energy")

    def copy(self) -> XPSSpectrum:
        """Retorna una copia del espectro."""
        return XPSSpectrum(
            region_name=self.region_name,
            binding_energy=self.binding_energy.copy(),
            intensity=self.intensity.copy(),
            metadata=self.metadata.copy(),
        )


@dataclass
class XPSDataset:
    """Representa un archivo XPS completo."""

    filename: str
    header: dict[str, Any]
    spectra: dict[str, XPSSpectrum]

    def __post_init__(self):
        """Validación básica después de inicialización."""
        if not self.filename or not self.filename.strip():
            raise ValueError("filename no puede estar vacío")

        if not self.spectra:
            raise ValueError(
                "spectra no puede estar vacío - debe contener al menos un espectro"
            )

    def get_spectrum(self, region_name: str) -> XPSSpectrum | None:
        """Obtiene un espectro específico."""
        return self.spectra.get(region_name)

    def list_regions(self) -> list:
        """Lista todas las regiones disponibles."""
        return list(self.spectra.keys())

    def copy(self) -> XPSDataset:
        """Retorna una copia del dataset."""
        return XPSDataset(
            filename=self.filename,
            header=self.header.copy(),
            spectra={name: spec.copy() for name, spec in self.spectra.items()},
        )


@dataclass
class XPSSample:
    """Representa una muestra XPS que puede contener múltiples archivos."""

    sample_name: str
    datasets: dict[str, XPSDataset]

    def __post_init__(self):
        """Validación básica después de inicialización."""
        if not self.sample_name or not self.sample_name.strip():
            raise ValueError("sample_name no puede estar vacío")

        if not self.datasets:
            raise ValueError(
                "datasets no puede estar vacío - debe contener al menos un dataset"
            )

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

    def copy(self) -> XPSSample:
        """Retorna una copia de la muestra.

        Returns
        -------
        XPSSample
            Copia de la muestra.
        """
        return XPSSample(
            sample_name=self.sample_name,
            datasets={name: ds.copy() for name, ds in self.datasets.items()},
        )


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
            elements_config = lines[1].split()

            for elem, orbital, energy in zip(
                elements_config[::2],
                elements_config[1::2],
                lines[2].split(),
                strict=True,
            ):
                elements[elem] = {"orbital": orbital, "mean_energy": energy}
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

    with open(filepath) as file:
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
                    while (
                        i < len(data)
                        and not data[i].startswith("Element")
                        or len(region_lines) == 0
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
        - "vamas": Formato VAMAS (ISO 14976)
        - "casa": Formato CASA XPS
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
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            first_lines = [f.readline().strip() for _ in range(10)]

        # Concatenar para búsqueda
        content = "\n".join(first_lines)

        # Detección por contenido (prioridad alta)
        if "VAMAS" in content or "ISO 14976" in content:
            return "vamas"

        if "Casa" in content or "CASA" in content:
            return "casa"

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
        # Archivo binario (puede ser VAMAS binario en Fase 2)
        return None
    except Exception:
        return None
