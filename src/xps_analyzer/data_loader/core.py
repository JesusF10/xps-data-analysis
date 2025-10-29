"""
Funciones principales de carga de datos XPS.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd


@dataclass
class XPSSpectrum:
    """Representa un espectro XPS individual."""

    region_name: str
    binding_energy: List[float]
    intensity: List[float]
    metadata: Dict[str, Any]

    @property
    def data(self) -> pd.DataFrame:
        """Retorna los datos como DataFrame."""
        return pd.DataFrame(
            {"binding_energy": self.binding_energy, "intensity": self.intensity}
        )


@dataclass
class XPSDataset:
    """Representa un archivo XPS completo."""

    filename: str
    header: Dict[str, Any]
    spectra: Dict[str, XPSSpectrum]

    def get_spectrum(self, region_name: str) -> XPSSpectrum:
        """Obtiene un espectro específico."""
        return self.spectra.get(region_name)

    def list_regions(self) -> list:
        """Lista todas las regiones disponibles."""
        return list(self.spectra.keys())


@dataclass
class XPSSample:
    """Representa una muestra XPS que puede contener múltiples archivos."""

    sample_name: str
    datasets: Dict[str, XPSDataset]

    def get_dataset(self, filename: str) -> XPSDataset:
        """Obtiene un dataset específico."""
        return self.datasets.get(filename)

    def list_datasets(self) -> list:
        """Lista todos los datasets disponibles."""
        return list(self.datasets.keys())


def parse_metadata(lines: Union[list, str], header: bool = False) -> Dict[str, Any]:
    """
    Parsea las líneas de metadatos y retorna un diccionario.
    ----------
    Parametersx
    ----------
    lines : [list, str]
        Líneas de texto que contienen metadatos.
    header : bool, default=False
        Si True, parsea metadatos globales, de otro modo, parsea metadatos locales
        (del espectro).
    Returns
    -------
    Dict[str, str]
        Diccionario con pares clave-valor de metadatos.
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
        for meta_line in lines[0].split(";")[:-2]:
            key = "_".join(meta_line.split()[:-1])
            value = meta_line.split()[-1].strip()
            metadata[key] = value

        elements = {}
        elements_config = lines[1].split()

        for elem, orbital, energy in zip(
            elements_config[::2], elements_config[1::2], lines[2].split()
        ):
            elements[elem] = {"orbital": orbital, "mean_energy": energy}
        metadata["elements"] = elements
        return metadata

    elif isinstance(lines, str) and lines.split()[0] == "Element":
        lines = lines.split(";")
        if len(lines[0].split()) < 2:
            metadata["element"] = "survey"
        else:
            metadata["element"] = " ".join(lines[0].split()[1:])
        # Region
        metadata["region"] = int(lines[1].split()[1])
        # Depth cycle
        metadata["depth_cycle"] = (int(lines[2].split()[2]), int(lines[2].split()[4]))
        # Time Per Step
        metadata["time_per_step"] = int(lines[3].split()[-1])
        # Sweeps
        metadata["sweeps"] = int(lines[4].split()[-1])
        # Anode
        metadata["anode"] = lines[5].split()[-1]
        # Photon energy
        metadata["photon_energy"] = float(lines[6].split()[-1])

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
    """
    binding_energy = []
    intensity = []
    metadata = parse_metadata(data_lines[0], header=False)

    for line in data_lines[1:]:
        parts = line.split()
        binding_energy.append(float(parts[0]))
        intensity.append(float(parts[1]))

    spectrum = XPSSpectrum(
        region_name=metadata.get("element", "unknown"),
        binding_energy=binding_energy,
        intensity=intensity,
        metadata=metadata,
    )

    return spectrum


def load_single_file(filepath: Union[str, Path]) -> XPSDataset:
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
    data_path: Union[str, Path], recursive: bool = True
) -> Dict[str, Any]:
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
    Dict[str, Any]
        Diccionario con los datos cargados. Las claves son los nombres
        de archivo y los valores son los datos procesados.
    Examples
    --------
    >>> data = load_all_data("data/raw/samples/")
    >>> print(f"Cargados {len(data)} archivos")
    >>> for filename, dataset in data.items():
    ...     print(f"{filename}: {dataset.shape}")
    """
    # Falta implementar
    pass


def detect_file_format(filepath: Union[str, Path]) -> str:
    """
    Detecta automáticamente el formato del archivo XPS.
    Parameters
    ----------
    filepath : str or Path
        Ruta al archivo a analizar.
    Returns
    -------
    str
        Tipo de formato detectado: 'vamas', 'casa', 'text', 'csv', etc.
    """
    # Falta implementar
    pass
