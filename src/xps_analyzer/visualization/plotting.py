"""
Módulo de visualización de datos XPS
"""

from xps_analyzer.data_loader import XPSSpectrum

from matplotlib import pyplot as plt


def plot_spectrum(spectrum: XPSSpectrum, title: str = "Espectro XPS") -> None:
    """
    Genera una gráfica del espectro XPS.

    Parameters
    ----------
    spectrum : XPSSpectrum
        El espectro XPS a graficar.
    title : str, default="Espectro XPS"
        El título de la gráfica.
    """
    plt.figure(figsize=(8, 6))
    plt.plot(spectrum.data, label=spectrum.region_name)
    plt.gca().invert_xaxis()
    plt.title(title)
    plt.xlabel("Energía de enlace (eV)")
    plt.ylabel("Intensidad")
    plt.legend()
    plt.show()


def plot_survey_spectrum(
    spectrum: XPSSpectrum, title: str = "Espectro Survey XPS"
) -> None:
    """
    Genera una gráfica del espectro survey XPS.

    Parameters
    ----------
    spectrum : XPSSpectrum
        El espectro survey XPS a graficar.
    title : str, default="Espectro Survey XPS"
        El título de la gráfica.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(spectrum.data, label=spectrum.region_name, color="orange")
    plt.gca().invert_xaxis()
    plt.title(title)
    plt.xlabel("Energía de enlace (eV)")
    plt.ylabel("Intensidad")
    plt.legend()
    plt.show()
