"""Calibración de espectros XPS."""

from typing import Union

from xps_analyzer.data_loader import XPSDataset, XPSSpectrum
from xps_analyzer.reference_data import ElementReference


def calibrate_spectrum(spectrum: XPSSpectrum,
                       shift: float,
                       inplace: bool = False) -> Union[XPSSpectrum, None]:
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
        calibrated_spectrum = spectrum.copy()
        calibrated_spectrum.binding_energy += shift
        return calibrated_spectrum
    spectrum.binding_energy += shift
    return


def calibrate_sample(dataset: XPSDataset,
                      ref_element: ElementReference,
                      inplace: bool = False) -> Union[XPSDataset, None]:
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
    """
    spectrum_reference = [x for x in list(dataset.spectra.keys())\
                          if x.split()[0] == ref_element.symbol][0]
    shift = ref_element.binding_energy_most_useful - \
            dataset.spectra.get(spectrum_reference).data.idxmax().iloc[0]
    if not inplace:
        calibrated_dataset = dataset.copy()
        calibrate_sample(calibrated_dataset, ref_element, inplace=True)
        return calibrated_dataset
    for _, spectrum in dataset.spectra.items():
        calibrate_spectrum(spectrum, shift, inplace=True)
    return

