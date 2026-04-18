"""Calibración de espectros XPS."""

from xps_analyzer.data_loader import XPSDataset, XPSSpectrum
from xps_analyzer.reference_data import ElementReference


def calibrate_spectrum(
    spectrum: XPSSpectrum, shift: float, inplace: bool = False
) -> XPSSpectrum | None:
    """
    Calibra un espectro XPS desplazando las energías de enlace.

    Parameters
    ----------
    spectrum : XPSSpectrum
        El espectro XPS a calibrar.
    shift : float
        El valor de desplazamiento en eV para aplicar.
    inplace : bool, default=False
        Si True, modifica el espectro original. Si False, retorna una copia calibrada.

    Returns
    -------
    XPSSpectrum o None
        El espectro calibrado.
    """
    if not inplace:
        calibrated_spectrum = spectrum.model_copy(deep=True)
        calibrated_spectrum.binding_energy += shift
        return calibrated_spectrum
    spectrum.binding_energy += shift
    return


def calibrate_sample(
    dataset: XPSDataset, ref_element: ElementReference, inplace: bool = False
) -> XPSDataset | None:
    """
    Calibra todos los espectros en un conjunto de datos XPS.

    Parameters
    ----------
    dataset : XPSDataset
        El conjunto de datos XPS a calibrar.
    ref_element : ElementReference
        El elemento químico de referencia para la calibración.
    inplace : bool, default=False
        Si True, modifica el conjunto de datos original. Si False, retorna una copia calibrada.
    Returns
    -------
    XPSDataset o None
        El conjunto de datos calibrado.

    Raises
    ------
    ValueError
        Si el elemento de referencia no se encuentra en el dataset.
    ValueError
        Si el elemento de referencia no tiene binding_energy_most_useful definido.
    """
    # Bug #1 corregido: Buscar espectro de referencia con manejo de errores
    spectrum_reference_list = [
        x for x in list(dataset.spectra.keys()) if x.split()[0] == ref_element.symbol
    ]

    if not spectrum_reference_list:
        raise ValueError(
            f"Elemento de referencia '{ref_element.symbol}' no encontrado en el dataset. "
            f"Regiones disponibles: {', '.join(dataset.spectra.keys())}"
        )

    spectrum_reference = spectrum_reference_list[0]

    # Bug #2 corregido: Verificar que binding_energy_most_useful existe
    if ref_element.binding_energy_most_useful is None:
        raise ValueError(
            f"El elemento de referencia '{ref_element.symbol}' no tiene "
            f"binding_energy_most_useful definido en la base de datos"
        )

    # Bug #3 corregido: Usar numpy directamente en lugar de pandas
    ref_spectrum = dataset.spectra.get(spectrum_reference)
    peak_idx = ref_spectrum.intensity.argmax()
    observed_peak_energy = ref_spectrum.binding_energy[peak_idx]

    # Calcular desplazamiento
    shift = ref_element.binding_energy_most_useful - observed_peak_energy

    if not inplace:
        calibrated_dataset = dataset.model_copy(deep=True)
        calibrate_sample(calibrated_dataset, ref_element, inplace=True)
        return calibrated_dataset
    for _, spectrum in dataset.spectra.items():
        calibrate_spectrum(spectrum, shift, inplace=True)
    return
