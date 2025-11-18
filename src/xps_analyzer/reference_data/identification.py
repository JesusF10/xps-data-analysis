"""
Funciones para identificación de elementos y compuestos usando datos de referencia.
"""

from typing import Dict, List, Tuple

from .elements import ReferenceDatabase


def identify_peaks(
    peak_energies: List[float],
    reference_db: ReferenceDatabase,
    tolerance: float = 2.0,
) -> List[Dict]:
    """
    Identifica picos comparando con la base de datos de referencia.

    Parameters
    ----------
    peak_energies : List[float]
        Lista de energías de enlace de los picos encontrados
    reference_db : ReferenceDatabase
        Base de datos de elementos de referencia
    tolerance : float, default=2.0
        Tolerancia en eV para considerar una coincidencia

    Returns
    -------
    List[Dict]
        Lista de identificaciones posibles con información detallada
    """
    identifications = []

    for peak_energy in peak_energies:
        # Buscar coincidencias en la base de datos
        matches = reference_db.search_by_binding_energy(peak_energy, tolerance)

        if matches:
            identification = {
                "peak_position": peak_energy,
                "possible_matches": matches,
                "confidence": _calculate_confidence(peak_energy, matches, reference_db),
            }
            identifications.append(identification)

    return identifications


def find_peaks_in_spectrum(
    binding_energy: List[float], intensity: List[float], height_threshold: float = 0.1
) -> List[float]:
    """
    Encuentra picos en un espectro XPS.

    Parameters
    ----------
    binding_energy : List[float]
        Energías de enlace
    intensity : List[float]
        Intensidades correspondientes
    height_threshold : float, default=0.1
        Umbral relativo de altura para detectar picos

    Returns
    -------
    List[float]
        Lista de energías de enlace donde se encontraron picos
    """
    try:
        import numpy as np
        from scipy.signal import find_peaks
    except ImportError:
        # Implementación básica sin scipy
        return _find_peaks_basic(binding_energy, intensity, height_threshold)

    # Normalizar intensidad
    intensity_array = np.array(intensity)
    norm_intensity = intensity_array / intensity_array.max()

    # Encontrar picos
    peaks_idx, _ = find_peaks(norm_intensity, height=height_threshold)

    # Convertir índices a energías de enlace
    binding_energy_array = np.array(binding_energy)
    peak_energies = binding_energy_array[peaks_idx]

    return peak_energies.tolist()


def suggest_compounds(
    element_symbol: str, observed_energy: float, reference_db: ReferenceDatabase
) -> List:
    """
    Sugiere posibles compuestos basados en el desplazamiento químico observado.

    Parameters
    ----------
    element_symbol : str
        Símbolo del elemento
    observed_energy : float
        Energía de enlace observada
    reference_db : ReferenceDatabase
        Base de datos de referencia

    Returns
    -------
    List[CompoundReference]
        Lista de posibles compuestos ordenados por proximidad energética
    """
    element = reference_db.get_element(element_symbol)
    if not element:
        return []

    # Buscar compuestos con energías similares
    candidates = []
    for compound in element.compounds:
        if abs(compound.peak_position - observed_energy) <= 2.0:
            candidates.append(compound)

    # Ordenar por proximidad energética
    candidates.sort(key=lambda c: abs(c.peak_position - observed_energy))

    return candidates


def _calculate_confidence(
    peak_energy: float, matches: List[Tuple[str, str]], reference_db: ReferenceDatabase
) -> float:
    """
    Calcula la confianza de la identificación basada en múltiples factores.

    Parameters
    ----------
    peak_energy : float
        Energía del pico observado
    matches : List[Tuple[str, str]]
        Lista de coincidencias (elemento, orbital/compuesto)
    reference_db : ReferenceDatabase
        Base de datos de referencia

    Returns
    -------
    float
        Valor de confianza entre 0 y 1
    """
    if not matches:
        return 0.0

    # Por ahora, implementación básica
    # TODO: Mejorar con lógica más sofisticada
    num_matches = len(matches)
    base_confidence = min(0.9, 0.3 + 0.1 * num_matches)

    return base_confidence


def _find_peaks_basic(
    binding_energy: List[float], intensity: List[float], height_threshold: float
) -> List[float]:
    """
    Implementación básica de detección de picos sin scipy.

    Parameters
    ----------
    binding_energy : List[float]
        Energías de enlace
    intensity : List[float]
        Intensidades
    height_threshold : float
        Umbral de altura

    Returns
    -------
    List[float]
        Energías donde se encontraron picos
    """
    if len(intensity) < 3:
        return []

    max_intensity = max(intensity)
    min_height = max_intensity * height_threshold
    peaks = []

    # Buscar máximos locales simples
    for i in range(1, len(intensity) - 1):
        if (
            intensity[i] > intensity[i - 1]
            and intensity[i] > intensity[i + 1]
            and intensity[i] >= min_height
        ):
            peaks.append(binding_energy[i])

    return peaks
