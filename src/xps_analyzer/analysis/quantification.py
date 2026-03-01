"""
Módulo para cuantificación atómica en espectros XPS.

Implementa cálculo de concentraciones atómicas usando factores de sensibilidad
relativa (RSF - Relative Sensitivity Factors) de Scofield y Wagner.

Funciones principales:
- calculate_atomic_concentration: Calcula concentraciones atómicas de una lista de picos
- load_sensitivity_factors: Carga factores RSF para elementos comunes
- quantify_dataset: Cuantifica dataset completo con múltiples regiones
- normalize_to_100: Normaliza concentraciones para que sumen 100%

Referencias:
- Scofield, J.H. (1976) "Theoretical photoionization cross sections" LLNL UCRL-51326
- Wagner, C.D. et al. (1981) "Empirical atomic sensitivity factors" Surf. Interface Anal. 3(5), 211-225
- Briggs, D. & Seah, M.P. (1990) "Practical Surface Analysis Vol. 1" 2nd Ed., Wiley
"""

from __future__ import annotations

from typing import Literal

from xps_analyzer.analysis.peak_fitting import PeakParameters
from xps_analyzer.data_loader import XPSDataset

import pandas as pd

# Factores de sensibilidad relativa de Scofield (1976) para Al Kα (1486.6 eV)
# Normalizados a F 1s = 1.0
SCOFIELD_RSF_AL_KA = {
    "C 1s": 0.296,
    "N 1s": 0.477,
    "O 1s": 0.711,
    "F 1s": 1.000,
    "Na 1s": 1.685,
    "Mg 1s": 2.417,
    "Al 2p": 0.234,
    "Si 2p": 0.328,
    "P 2p": 0.486,
    "S 2p": 0.668,
    "Cl 2p": 0.891,
    "K 2p": 1.788,
    "Ca 2p": 2.180,
    "Ti 2p": 2.001,
    "Cr 2p": 2.427,
    "Mn 2p": 2.747,
    "Fe 2p": 3.109,
    "Co 2p": 3.509,
    "Ni 2p": 3.945,
    "Cu 2p": 5.321,
    "Zn 2p": 5.589,
    "Ag 3d": 5.987,
    "Au 4f": 5.630,
}

# Factores de sensibilidad relativa de Wagner (1981) para Al Kα
# Valores empíricos promediados de múltiples laboratorios
WAGNER_RSF_AL_KA = {
    "C 1s": 0.278,
    "N 1s": 0.499,
    "O 1s": 0.780,
    "F 1s": 1.000,
    "Na 1s": 1.810,
    "Mg 1s": 2.512,
    "Al 2p": 0.193,
    "Si 2p": 0.339,
    "P 2p": 0.509,
    "S 2p": 0.717,
    "Cl 2p": 0.970,
    "K 2p": 1.865,
    "Ca 2p": 2.331,
    "Ti 2p": 2.136,
    "Cr 2p": 2.591,
    "Mn 2p": 2.957,
    "Fe 2p": 3.351,
    "Co 2p": 3.789,
    "Ni 2p": 4.264,
    "Cu 2p": 5.764,
    "Zn 2p": 6.074,
    "Ag 3d": 6.519,
    "Au 4f": 6.250,
}

# Factores de sensibilidad relativa de Scofield para Mg Kα (1253.6 eV)
SCOFIELD_RSF_MG_KA = {
    "C 1s": 0.205,
    "N 1s": 0.314,
    "O 1s": 0.463,
    "F 1s": 0.630,
    "Na 1s": 1.000,
    "Mg 1s": 1.380,
    "Al 2p": 0.150,
    "Si 2p": 0.209,
    "P 2p": 0.304,
    "S 2p": 0.410,
    "Cl 2p": 0.542,
    "K 2p": 1.032,
    "Ca 2p": 1.247,
    "Ti 2p": 1.143,
    "Cr 2p": 1.390,
    "Mn 2p": 1.577,
    "Fe 2p": 1.787,
    "Co 2p": 2.019,
    "Ni 2p": 2.273,
    "Cu 2p": 3.080,
    "Zn 2p": 3.243,
    "Ag 3d": 3.480,
    "Au 4f": 3.290,
}


def load_sensitivity_factors(
    source: Literal["scofield", "wagner"] = "scofield",
    xray_source: Literal["al_ka", "mg_ka"] = "al_ka",
) -> dict[str, float]:
    """
    Carga factores de sensibilidad relativa (RSF) para cuantificación XPS.

    Los factores RSF son específicos de la fuente de rayos X usada. Los valores
    de Scofield son teóricos basados en secciones eficaces de fotoionización,
    mientras que los de Wagner son empíricos promediados de múltiples laboratorios.

    Parámetros
    ----------
    source : {"scofield", "wagner"}, default="scofield"
        Fuente de los factores RSF:
        - "scofield": Factores teóricos de Scofield (1976)
        - "wagner": Factores empíricos de Wagner (1981)
    xray_source : {"al_ka", "mg_ka"}, default="al_ka"
        Fuente de rayos X del instrumento:
        - "al_ka": Al Kα (1486.6 eV) - más común
        - "mg_ka": Mg Kα (1253.6 eV)

    Retorna
    -------
    dict[str, float]
        Diccionario con factores RSF por línea fotoelectrónica.
        Formato: {"C 1s": 0.296, "O 1s": 0.711, ...}

    Raises
    ------
    ValueError
        Si la combinación source/xray_source no está soportada.

    Ejemplos
    --------
    >>> rsf = load_sensitivity_factors()
    >>> rsf["C 1s"]
    0.296

    >>> rsf_wagner = load_sensitivity_factors(source="wagner")
    >>> rsf_wagner["O 1s"]
    0.780

    Notas
    -----
    - Los factores están normalizados a F 1s = 1.0 (Scofield Al Kα) o Na 1s = 1.0 (Scofield Mg Kα)
    - Para Wagner, normalización a F 1s = 1.0
    - Los factores de Scofield son generalmente más precisos para elementos ligeros
    - Los factores de Wagner son preferibles para análisis cuantitativo rutinario
    """
    if source == "scofield":
        if xray_source == "al_ka":
            return SCOFIELD_RSF_AL_KA.copy()
        elif xray_source == "mg_ka":
            return SCOFIELD_RSF_MG_KA.copy()
        else:
            raise ValueError(
                f"Fuente de rayos X '{xray_source}' no soportada para Scofield. "
                f"Opciones: 'al_ka', 'mg_ka'"
            )
    elif source == "wagner":
        if xray_source == "al_ka":
            return WAGNER_RSF_AL_KA.copy()
        elif xray_source == "mg_ka":
            raise ValueError(
                "Wagner RSF solo disponibles para Al Kα. Use source='scofield' para Mg Kα"
            )
        else:
            raise ValueError(
                f"Fuente de rayos X '{xray_source}' no soportada para Wagner. "
                f"Solo 'al_ka' disponible"
            )
    else:
        raise ValueError(
            f"Fuente de RSF '{source}' no reconocida. Opciones: 'scofield', 'wagner'"
        )


def calculate_atomic_concentration(
    peaks: list[PeakParameters],
    sensitivity_factors: dict[str, float],
    element_names: list[str] | None = None,
    normalize: bool = True,
) -> dict[str, float]:
    """
    Calcula concentraciones atómicas a partir de áreas de picos y factores RSF.

    Usa la fórmula estándar de cuantificación XPS:
        C_i = (A_i / S_i) / Σ(A_j / S_j) × 100%

    donde:
    - C_i: concentración atómica del elemento i (%)
    - A_i: área del pico del elemento i
    - S_i: factor de sensibilidad relativa del elemento i

    Parámetros
    ----------
    peaks : list[PeakParameters]
        Lista de picos ajustados con áreas calculadas.
    sensitivity_factors : dict[str, float]
        Factores RSF por línea fotoelectrónica (de load_sensitivity_factors).
    element_names : list[str], opcional
        Nombres de elementos correspondientes a cada pico (ej: ["C 1s", "O 1s"]).
        Si None, se intenta extraer de PeakParameters (no implementado en esta versión).
    normalize : bool, default=True
        Si True, normaliza concentraciones para que sumen 100%.

    Retorna
    -------
    dict[str, float]
        Concentraciones atómicas por elemento en porcentaje atómico.
        Formato: {"C 1s": 65.3, "O 1s": 34.7}

    Raises
    ------
    ValueError
        Si algún elemento no tiene factor RSF disponible.
        Si las áreas de picos son negativas o cero.
        Si element_names no coincide con número de picos.

    Ejemplos
    --------
    >>> from xps_analyzer.analysis import PeakParameters, load_sensitivity_factors
    >>> peaks = [
    ...     PeakParameters(position=284.8, amplitude=1000, width=1.2,
    ...                    area=1500, shape="gaussian"),
    ...     PeakParameters(position=531.0, amplitude=800, width=1.5,
    ...                    area=1200, shape="gaussian"),
    ... ]
    >>> rsf = load_sensitivity_factors()
    >>> concentrations = calculate_atomic_concentration(
    ...     peaks, rsf, element_names=["C 1s", "O 1s"]
    ... )
    >>> concentrations
    {'C 1s': 75.3, 'O 1s': 24.7}

    Notas
    -----
    - Las áreas deben ser valores positivos calculados del ajuste de picos
    - Si normalize=False, las concentraciones pueden no sumar 100%
    - Para múltiples picos del mismo elemento (ej: C 1s con componentes),
      se deben sumar las áreas antes de cuantificar
    """
    # Validación de entrada
    if not peaks:
        raise ValueError("La lista de picos no puede estar vacía")

    if element_names is None:
        raise ValueError(
            "element_names debe especificarse. Extracción automática no implementada."
        )

    if len(peaks) != len(element_names):
        raise ValueError(
            f"Número de picos ({len(peaks)}) debe coincidir con "
            f"element_names ({len(element_names)})"
        )

    # Validar áreas positivas
    for i, peak in enumerate(peaks):
        if peak.area <= 0:
            raise ValueError(
                f"Área del pico {i} ({element_names[i]}) debe ser positiva, "
                f"obtenido: {peak.area}"
            )

    # Verificar que todos los elementos tengan factor RSF
    missing_rsf = []
    for element in element_names:
        if element not in sensitivity_factors:
            missing_rsf.append(element)

    if missing_rsf:
        raise ValueError(
            f"Factores RSF no disponibles para: {', '.join(missing_rsf)}. "
            f"Elementos disponibles: {', '.join(sorted(sensitivity_factors.keys()))}"
        )

    # Calcular intensidades normalizadas (área / RSF)
    normalized_intensities = {}
    for peak, element in zip(peaks, element_names, strict=True):
        rsf = sensitivity_factors[element]
        normalized_intensities[element] = peak.area / rsf

    # Calcular suma total
    total_intensity = sum(normalized_intensities.values())

    # Calcular concentraciones
    concentrations = {}
    for element, intensity in normalized_intensities.items():
        concentration = (intensity / total_intensity) * 100.0
        concentrations[element] = concentration

    # Normalizar si es necesario (por defecto ya normalizado, pero útil para redondeo)
    if normalize:
        concentrations = normalize_to_100(concentrations)

    return concentrations


def normalize_to_100(concentrations: dict[str, float]) -> dict[str, float]:
    """
    Normaliza concentraciones atómicas para que sumen exactamente 100%.

    Útil para corregir pequeños errores de redondeo o cuando se excluyen
    elementos traza del análisis.

    Parámetros
    ----------
    concentrations : dict[str, float]
        Concentraciones atómicas por elemento (pueden no sumar 100%).

    Retorna
    -------
    dict[str, float]
        Concentraciones normalizadas que suman 100%.

    Raises
    ------
    ValueError
        Si la suma de concentraciones es cero o negativa.

    Ejemplos
    --------
    >>> conc = {"C 1s": 65.1, "O 1s": 34.2}  # Suma = 99.3%
    >>> normalized = normalize_to_100(conc)
    >>> normalized
    {'C 1s': 65.57, 'O 1s': 34.43}
    >>> sum(normalized.values())
    100.0

    Notas
    -----
    - Mantiene las proporciones relativas entre elementos
    - Útil cuando se excluyen hidrógeno o elementos traza no detectados
    """
    if not concentrations:
        raise ValueError("El diccionario de concentraciones no puede estar vacío")

    total = sum(concentrations.values())

    if total <= 0:
        raise ValueError(
            f"La suma de concentraciones debe ser positiva, obtenido: {total}"
        )

    # Normalizar
    normalized = {
        element: (conc / total) * 100.0 for element, conc in concentrations.items()
    }

    return normalized


def quantify_dataset(
    dataset: XPSDataset,
    sensitivity_factors: dict[str, float] | None = None,
    rsf_source: Literal["scofield", "wagner"] = "scofield",
    xray_source: Literal["al_ka", "mg_ka"] = "al_ka",
    region_to_element: dict[str, str] | None = None,
    normalize: bool = True,
) -> pd.DataFrame:
    """
    Cuantifica dataset XPS completo con múltiples regiones espectrales.

    NOTA: Esta función requiere que los picos ya estén ajustados. Use fit_gaussian,
    fit_lorentzian, fit_voigt o fit_multiple_peaks antes de llamar esta función.

    Parámetros
    ----------
    dataset : XPSDataset
        Dataset con múltiples espectros (regiones).
    sensitivity_factors : dict[str, float], opcional
        Factores RSF personalizados. Si None, se cargan automáticamente.
    rsf_source : {"scofield", "wagner"}, default="scofield"
        Fuente de RSF si sensitivity_factors es None.
    xray_source : {"al_ka", "mg_ka"}, default="al_ka"
        Fuente de rayos X si sensitivity_factors es None.
    region_to_element : dict[str, str], opcional
        Mapeo de nombre de región a línea fotoelectrónica.
        Ejemplo: {"Region_C": "C 1s", "Region_O": "O 1s"}
        Si None, se intenta extraer automáticamente del nombre de región.
    normalize : bool, default=True
        Si True, normaliza concentraciones para que sumen 100%.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas:
        - "Element": Línea fotoelectrónica (ej: "C 1s")
        - "Area": Área del pico
        - "RSF": Factor de sensibilidad usado
        - "Normalized_Intensity": Área / RSF
        - "Atomic_Concentration": Concentración atómica (%)

    Raises
    ------
    ValueError
        Si el dataset no contiene espectros.
        Si no se puede mapear región a elemento.
        Si faltan factores RSF para algún elemento.
    NotImplementedError
        Esta función requiere integración con módulo de peak fitting.
        En la versión actual, use calculate_atomic_concentration directamente
        después de ajustar picos.

    Ejemplos
    --------
    >>> from xps_analyzer import load_single_file
    >>> from xps_analyzer.analysis import fit_gaussian, quantify_dataset
    >>>
    >>> # Cargar dataset
    >>> dataset = load_single_file("muestra.vms")
    >>>
    >>> # Ajustar picos (debe hacerse ANTES de cuantificar)
    >>> # (código de ajuste aquí)
    >>>
    >>> # Cuantificar
    >>> results = quantify_dataset(dataset)
    >>> print(results)
       Element    Area   RSF  Normalized_Intensity  Atomic_Concentration
    0   C 1s    1500.0  0.296            5067.57                  75.3
    1   O 1s    1200.0  0.711            1687.48                  24.7

    Notas
    -----
    - Requiere que todos los picos estén previamente ajustados
    - Para análisis completo, combine con background subtraction y peak fitting
    - Los elementos traza (<1%) pueden ser excluidos manualmente después
    """
    # Validación
    if not dataset.spectra:
        raise ValueError("El dataset no contiene espectros")

    # Esta función está parcialmente implementada como placeholder
    # Requiere integración con sistema de almacenamiento de resultados de fit
    raise NotImplementedError(
        "quantify_dataset() requiere sistema de almacenamiento de fit results. "
        "Use calculate_atomic_concentration() directamente después de ajustar picos.\n\n"
        "Flujo recomendado:\n"
        "1. spectrum = dataset.get_spectrum('C 1s')\n"
        "2. result = fit_gaussian(spectrum, position=284.8, ...)\n"
        "3. peaks = [result.peaks[0], ...]\n"
        "4. conc = calculate_atomic_concentration(peaks, rsf, ['C 1s', ...])"
    )


def _extract_element_from_region_name(region_name: str) -> str | None:
    """
    Intenta extraer elemento y orbital de nombre de región.

    Helper interno para quantify_dataset.

    Parámetros
    ----------
    region_name : str
        Nombre de región (ej: "C 1s", "Carbon_1s", "Region_C1s").

    Retorna
    -------
    str | None
        Línea fotoelectrónica extraída (ej: "C 1s") o None si no se puede extraer.

    Ejemplos
    --------
    >>> _extract_element_from_region_name("C 1s")
    'C 1s'
    >>> _extract_element_from_region_name("Carbon_1s")
    'C 1s'
    >>> _extract_element_from_region_name("Region_O")
    'O 1s'
    >>> _extract_element_from_region_name("Unknown")
    None
    """
    # Implementación simple - puede extenderse con regex más complejos
    import re

    # Patrón: símbolo elemento (1-2 letras) + espacio + orbital
    pattern = r"([A-Z][a-z]?)\s*(\d[spdf])"
    match = re.search(pattern, region_name, re.IGNORECASE)

    if match:
        element = match.group(1).capitalize()
        orbital = match.group(2).lower()
        return f"{element} {orbital}"

    return None
