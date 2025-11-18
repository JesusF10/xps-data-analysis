"""
Clases principales para manejo de datos de referencia XPS.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_reference_db_cache = None

@dataclass
class PhotoelectronLine:
    """
    Representa una línea fotoeléctrica de un orbital específico.

    Parameters
    ----------
    line : str
        Designación de la línea (ej: "1s", "2p1/2", "2p3/2", "KLL")
    binding_energy : float
        Energía de enlace en eV
    x_ray_source : str, optional
        Fuente de rayos X utilizada (ej: "Mg_Ka", "Al_Ka
    type : str, default="core"
        Tipo de línea ("core" o "Auger")
    kinetic_energy : float, optional
        Energía cinética en eV (solo para líneas Auger)
    """

    line: str
    binding_energy: float
    x_ray_source: Optional[str] = None
    type: str = "core"
    kinetic_energy: Optional[float] = None


@dataclass
class CompoundReference:
    """
    Datos de referencia para un compuesto específico.

    Parameters
    ----------
    orbital : str
        Orbital asociado (ej: "1s", "2p")
    binding_energy_range : tuple of float
        Energía o rango de energías de enlace (min, max) en eV
    """

    orbital: str
    binding_energy_range: Tuple[float, float]


@dataclass
class ElementReference:
    """
    Base de datos completa de un elemento químico.

    Parameters
    ----------
    symbol : str
        Símbolo del elemento (ej: "Li", "C", "O")
    element : str
        Nombre completo del elemento
    atomic_number : int
        Número atómico
    photoelectron_lines : List[PhotoelectronLine]
        Lista con las líneas fotoeléctronicas por orbital
    compounds : list
        Lista de compuestos de referencia
    binding_energy_most_useful : float, optional
        Energía de enlace más útil en eV
    spin_orbital_splitting : float, optional
        Separación spin-orbital en eV
    """

    symbol: str
    element: str
    atomic_number: int
    photoelectron_lines: List[PhotoelectronLine]
    compounds: Dict[str, CompoundReference]
    binding_energy_most_useful: Optional[float] = None
    spin_orbital_splitting: Optional[float] = None

    def get_main_line(self) -> PhotoelectronLine:
        """
        Obtiene la línea fotoeléctrica principal (mayor intensidad).

        Returns
        -------
        PhotoelectronLine
            Línea con mayor intensidad relativa
        """
        return self.binding_energy_most_useful

    def get_compound(self, name: str) -> Optional[CompoundReference]:
        """
        Busca un compuesto por nombre.

        Parameters
        ----------
        name : str
            Nombre del compuesto a buscar

        Returns
        -------
        CompoundReference or None
            Referencia del compuesto si se encuentra
        """
        return self.compounds.get(name)


@dataclass
class ReferenceDatabase:
    """
    Base de datos completa de elementos de referencia.

    Parameters
    ----------
    elements : dict
        Diccionario con elementos indexados por símbolo
    version : str
        Versión de la base de datos
    source : str
        Fuente de los datos de referencia
    """

    elements: Dict[str, ElementReference]
    version: str = "1.0"
    source: str = "Handbook of X-ray Photoelectron Spectroscopy"

    def get_element(self, symbol: str) -> Optional[ElementReference]:
        """
        Obtiene datos de un elemento por símbolo.

        Parameters
        ----------
        symbol : str
            Símbolo del elemento

        Returns
        -------
        ElementReference or None
            Referencia del elemento si existe
        """
        return self.elements.get(symbol.upper())

    def search_by_binding_energy(
        self, energy: float, tolerance: float = 2.0
    ) -> List[Tuple[str, str]]:
        """
        Busca elementos/compuestos por energía de enlace.

        Parameters
        ----------
        energy : float
            Energía de enlace a buscar (eV)
        tolerance : float, default=2.0
            Tolerancia de búsqueda (eV)

        Returns
        -------
        List[Tuple[str, str]]
            Lista de tuplas (elemento, orbital/compuesto)
        """
        matches = []
        for element in self.elements.values():
            # Buscar en líneas fotoeléctronicas
            for line in element.photoelectron_lines.values():
                if abs(line.binding_energy - energy) <= tolerance:
                    matches.append((element.symbol, line.orbital))

            # Buscar en compuestos
            for compound_name, compound in element.compounds.items():
                if abs(compound.peak_position - energy) <= tolerance:
                    matches.append((element.symbol, compound_name))

        return matches

    def get_chemical_shifts(self, element_symbol: str) -> Dict[str, float]:
        """
        Obtiene todos los desplazamientos químicos de un elemento.

        Parameters
        ----------
        element_symbol : str
            Símbolo del elemento

        Returns
        -------
        Dict[str, float]
            Diccionario con compuesto -> desplazamiento químico
        """
        element = self.get_element(element_symbol)
        if not element:
            return {}

        return {comp_name: comp.chemical_shift for comp_name, comp in element.compounds.items()}

    def list_elements(self) -> List[str]:
        """
        Lista todos los elementos disponibles.

        Returns
        -------
        List[str]
            Lista de símbolos de elementos
        """
        return list(self.elements.keys())


def load_reference_database(data_path: Optional[Path] = None) -> ReferenceDatabase:
    """
    Carga la base de datos de referencia desde archivo JSON.

    Parameters
    ----------
    data_path : Path, optional
        Ruta al archivo de datos JSON. Si None, usa ubicación por defecto.

    Returns
    -------
    ReferenceDatabase
        Base de datos cargada
    """

    global _reference_db_cache

    # Verificar caché
    if _reference_db_cache is not None:
        return _reference_db_cache

    if data_path is None:
        data_path = Path(__file__).parent / "data" / "reference_elements.json"

    try:
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)

        # Deserializar elementos
        elements = {}
        for symbol, element_data in data.get('elements', {}).items():
            elements[symbol] = _dict_to_element_reference(element_data)

        _reference_db_cache =  ReferenceDatabase(
            elements=elements,
            version=data.get('version', '1.0'),
            source=data.get('source', 'Unknown')
        )

        return _reference_db_cache

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error cargando base de datos: {e}")
        return ReferenceDatabase(elements={})


def _dict_to_element_reference(data: Dict) -> ElementReference:
    """
    Convierte un diccionario en una instancia de ElementReference.

    Parameters
    ----------
    data : Dict
        Diccionario con datos del elemento

    Returns
    -------
    ElementReference
        Instancia creada
    """
    photoelectron_lines = []

    for line, line_data in data.get("line_positions", {}).items():
        for values in line_data:
            photoelectron_lines.append(PhotoelectronLine(
                line=values.get("line", None),
                binding_energy=values.get("binding_energy_eV", None),
                x_ray_source="Al_Ka" if "Al_Ka" in line.lower() else "Mg_Ka",
                type="auger" if "auger" in line.lower() else "core",
                kinetic_energy=values.get("kinetic_energy_eV", None),
            ))

    compounds = {}
    for compound_data in data.get("chemical_state_data", []):
        compound_name = compound_data.get("compound_type", "unknown")
        compounds[compound_name] = CompoundReference(
            orbital=compound_data.get("orbital", "unknown"),
            binding_energy_range=compound_data.get("binding_energy_eV", (0.0, 0.0)),
        )

    return ElementReference(
        symbol=data.get('symbol', None),
        element=data.get('element', None),
        atomic_number=data.get('atomic_number', None),
        binding_energy_most_useful=data.get('binding_energy_of_most_useful_line_eV', None),
        spin_orbital_splitting=data.get('spin_orbit_splitting_eV', None),
        photoelectron_lines=photoelectron_lines,
        compounds=compounds
    )
