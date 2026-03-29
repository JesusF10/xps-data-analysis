"""
Módulo para ajuste de picos en espectros XPS.

Implementa ajustes de picos usando perfiles gaussiano, lorentziano y Voigt.
Permite ajustar picos individuales o múltiples picos simultáneamente.

Funciones principales:
- fit_gaussian: Ajusta un pico gaussiano
- fit_lorentzian: Ajusta un pico lorentziano
- fit_voigt: Ajusta un pico Voigt (convolución gaussiano-lorentziano)
- fit_multiple_peaks: Ajusta múltiples picos simultáneamente
- estimate_peak_positions: Estima posiciones iniciales de picos automáticamente

Referencias:
- Voigt profile: Thompson et al. (1987), J. Appl. Cryst. 20, 79-83
- Peak fitting in XPS: Biesinger (2017), Appl. Surf. Sci. 597, 156681
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from xps_analyzer.data_loader import XPSSpectrum

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.special import voigt_profile


@dataclass
class PeakParameters:
    """
    Parámetros de un pico ajustado.

    Atributos
    ----------
    position : float
        Posición del pico (binding energy en eV).
    amplitude : float
        Amplitud del pico (intensidad máxima en cuentas).
    width : float
        Ancho del pico (FWHM en eV para gaussiano/lorentziano, sigma para Voigt).
    area : float
        Área integrada bajo el pico.
    shape : str
        Tipo de perfil ("gaussian", "lorentzian", "voigt").
    gamma : float, opcional
        Parámetro gamma para perfil Voigt (ancho lorentziano).
    position_error : float, opcional
        Error estándar en la posición del pico.
    amplitude_error : float, opcional
        Error estándar en la amplitud.
    width_error : float, opcional
        Error estándar en el ancho.
    """

    position: float
    amplitude: float
    width: float
    area: float
    shape: Literal["gaussian", "lorentzian", "voigt"]
    gamma: float | None = None
    position_error: float | None = None
    amplitude_error: float | None = None
    width_error: float | None = None


@dataclass
class FitResult:
    """
    Resultado de un ajuste de pico(s).

    Atributos
    ----------
    peaks : list[PeakParameters]
        Lista de parámetros de picos ajustados.
    fitted_spectrum : np.ndarray
        Espectro ajustado (suma de todos los picos).
    residual : np.ndarray
        Residual (espectro original - ajuste).
    r_squared : float
        Coeficiente de determinación R² (bondad de ajuste).
    chi_squared : float
        Chi-cuadrado reducido.
    success : bool
        Si el ajuste convergió exitosamente.
    message : str
        Mensaje sobre el resultado del ajuste.
    """

    peaks: list[PeakParameters]
    fitted_spectrum: np.ndarray
    residual: np.ndarray
    r_squared: float
    chi_squared: float
    success: bool
    message: str


def _gaussian(
    x: np.ndarray, amplitude: float, position: float, width: float
) -> np.ndarray:
    """
    Función gaussiana para ajuste de picos.

    Parámetros
    ----------
    x : np.ndarray
        Array de energías de enlace (eV).
    amplitude : float
        Amplitud del pico.
    position : float
        Posición del pico (centro).
    width : float
        Ancho del pico (sigma, desviación estándar).

    Retorna
    -------
    np.ndarray
        Valores de la función gaussiana.
    """
    return amplitude * np.exp(-((x - position) ** 2) / (2 * width**2))


def _lorentzian(
    x: np.ndarray, amplitude: float, position: float, width: float
) -> np.ndarray:
    """
    Función lorentziana para ajuste de picos.

    Parámetros
    ----------
    x : np.ndarray
        Array de energías de enlace (eV).
    amplitude : float
        Amplitud del pico.
    position : float
        Posición del pico (centro).
    width : float
        Ancho del pico (gamma, ancho a media altura / 2).

    Retorna
    -------
    np.ndarray
        Valores de la función lorentziana.
    """
    return amplitude * (width**2) / ((x - position) ** 2 + width**2)


def _voigt(
    x: np.ndarray, amplitude: float, position: float, sigma: float, gamma: float
) -> np.ndarray:
    """
    Función Voigt para ajuste de picos (convolución gaussiano-lorentziano).

    Parámetros
    ----------
    x : np.ndarray
        Array de energías de enlace (eV).
    amplitude : float
        Amplitud del pico.
    position : float
        Posición del pico (centro).
    sigma : float
        Ancho gaussiano (desviación estándar).
    gamma : float
        Ancho lorentziano (HWHM - half width at half maximum).

    Retorna
    -------
    np.ndarray
        Valores de la función Voigt.
    """
    # voigt_profile toma (x, sigma, gamma) donde x es el array desplazado
    # Normalización: calcular perfil centrado en position
    x_centered = x - position

    # scipy.special.voigt_profile(x, sigma, gamma)
    profile = voigt_profile(x_centered, sigma, gamma)

    # Normalizar y escalar por amplitud
    max_profile = np.max(profile)
    if max_profile > 0:
        return amplitude * profile / max_profile
    else:
        return np.zeros_like(x)


def estimate_peak_positions(
    spectrum: XPSSpectrum,
    prominence: float = 0.05,
    min_distance: float = 0.5,
) -> list[float]:
    """
    Estima automáticamente las posiciones de picos en un espectro.

    Usa detección de picos basada en scipy.signal.find_peaks.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro XPS del cual detectar picos.
    prominence : float, default=0.1
        Prominencia mínima de picos (fracción de intensidad máxima).
    min_distance : float, default=1.0
        Distancia mínima entre picos (en eV).

    Retorna
    -------
    list[float]
        Lista de posiciones de picos detectados (binding energies en eV).

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.

    Notas
    -----
    - La prominencia se calcula como fracción de la intensidad máxima del espectro
    - min_distance se convierte a número de puntos basándose en el paso de energía
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError("El espectro debe tener al menos 3 puntos para detectar picos")

    # Calcular prominencia absoluta
    max_intensity = np.max(spectrum.intensity)
    prominence_abs = prominence * max_intensity

    # Calcular distancia mínima en número de puntos
    energy_step = np.mean(np.abs(np.diff(spectrum.binding_energy)))
    min_distance_points = int(min_distance / energy_step) if energy_step > 0 else 1

    # Detectar picos
    peaks_indices, _ = find_peaks(
        spectrum.intensity,
        prominence=prominence_abs,
        distance=min_distance_points,
    )

    # Convertir índices a posiciones de energía
    peak_positions = spectrum.binding_energy[peaks_indices].tolist()

    return peak_positions


def fit_gaussian(
    spectrum: XPSSpectrum,
    initial_position: float | None = None,
    initial_amplitude: float | None = None,
    initial_width: float = 1.0,
    bounds: tuple[list, list] | None = None,
) -> FitResult:
    """
    Ajusta un pico gaussiano a un espectro XPS.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro XPS a ajustar.
    initial_position : float, opcional
        Posición inicial del pico (eV). Si None, se usa el máximo del espectro.
    initial_amplitude : float, opcional
        Amplitud inicial. Si None, se usa la intensidad máxima.
    initial_width : float, default=1.0
        Ancho inicial del pico (sigma en eV).
    bounds : tuple[list, list], opcional
        Límites para los parámetros [amplitude, position, width].
        Formato: ([amp_min, pos_min, width_min], [amp_max, pos_max, width_max]).

    Retorna
    -------
    FitResult
        Objeto con los resultados del ajuste.

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.
        Si el ajuste no converge.

    Ejemplos
    --------
    >>> result = fit_gaussian(spectrum)
    >>> print(f"Pico en {result.peaks[0].position:.2f} eV")
    >>> print(f"R² = {result.r_squared:.3f}")
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError("El espectro debe tener al menos 3 puntos para ajustar")

    # Estimación de parámetros iniciales
    if initial_position is None:
        max_idx = np.argmax(spectrum.intensity)
        initial_position = spectrum.binding_energy[max_idx]

    if initial_amplitude is None:
        initial_amplitude = np.max(spectrum.intensity)

    p0 = [initial_amplitude, initial_position, initial_width]

    # Configurar límites si no se proporcionan
    if bounds is None:
        energy_range = np.ptp(spectrum.binding_energy)
        bounds = (
            [0, np.min(spectrum.binding_energy), 0.1],
            [
                np.max(spectrum.intensity) * 2,
                np.max(spectrum.binding_energy),
                energy_range,
            ],
        )

    # Ajustar
    try:
        popt, pcov = curve_fit(
            _gaussian,
            spectrum.binding_energy,
            spectrum.intensity,
            p0=p0,
            bounds=bounds,
            maxfev=10000,
        )
        success = True
        message = "Ajuste convergió exitosamente"
    except RuntimeError as e:
        raise ValueError(f"El ajuste gaussiano no convergió: {e}") from e

    # Extraer parámetros
    amplitude, position, width = popt
    perr = np.sqrt(np.diag(pcov))  # Errores estándar

    # Calcular área (integral de gaussiana = amplitude * width * sqrt(2*pi))
    area = amplitude * width * np.sqrt(2 * np.pi)

    # Calcular espectro ajustado y residual
    fitted = _gaussian(spectrum.binding_energy, amplitude, position, width)
    residual = spectrum.intensity - fitted

    # Calcular R² y chi²
    ss_res = np.sum(residual**2)
    ss_tot = np.sum((spectrum.intensity - np.mean(spectrum.intensity)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Chi-cuadrado reducido
    n_params = 3
    dof = len(spectrum.intensity) - n_params
    chi_squared = ss_res / dof if dof > 0 else np.inf

    # Crear PeakParameters
    peak = PeakParameters(
        position=position,
        amplitude=amplitude,
        width=width,
        area=area,
        shape="gaussian",
        position_error=perr[1],
        amplitude_error=perr[0],
        width_error=perr[2],
    )

    return FitResult(
        peaks=[peak],
        fitted_spectrum=fitted,
        residual=residual,
        r_squared=r_squared,
        chi_squared=chi_squared,
        success=success,
        message=message,
    )


def fit_lorentzian(
    spectrum: XPSSpectrum,
    initial_position: float | None = None,
    initial_amplitude: float | None = None,
    initial_width: float = 1.0,
    bounds: tuple[list, list] | None = None,
) -> FitResult:
    """
    Ajusta un pico lorentziano a un espectro XPS.

    El perfil lorentziano tiene colas más largas que el gaussiano,
    lo cual es más apropiado para algunos estados electrónicos.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro XPS a ajustar.
    initial_position : float, opcional
        Posición inicial del pico (eV). Si None, se usa el máximo del espectro.
    initial_amplitude : float, opcional
        Amplitud inicial. Si None, se usa la intensidad máxima.
    initial_width : float, default=1.0
        Ancho inicial del pico (gamma en eV).
    bounds : tuple[list, list], opcional
        Límites para los parámetros [amplitude, position, width].

    Retorna
    -------
    FitResult
        Objeto con los resultados del ajuste.

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.
        Si el ajuste no converge.
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError("El espectro debe tener al menos 3 puntos para ajustar")

    # Estimación de parámetros iniciales
    if initial_position is None:
        max_idx = np.argmax(spectrum.intensity)
        initial_position = spectrum.binding_energy[max_idx]

    if initial_amplitude is None:
        initial_amplitude = np.max(spectrum.intensity)

    p0 = [initial_amplitude, initial_position, initial_width]

    # Configurar límites si no se proporcionan
    if bounds is None:
        energy_range = np.ptp(spectrum.binding_energy)
        bounds = (
            [0, np.min(spectrum.binding_energy), 0.1],
            [
                np.max(spectrum.intensity) * 2,
                np.max(spectrum.binding_energy),
                energy_range,
            ],
        )

    # Ajustar
    try:
        popt, pcov = curve_fit(
            _lorentzian,
            spectrum.binding_energy,
            spectrum.intensity,
            p0=p0,
            bounds=bounds,
            maxfev=10000,
        )
        success = True
        message = "Ajuste convergió exitosamente"
    except RuntimeError as e:
        raise ValueError(f"El ajuste lorentziano no convergió: {e}") from e

    # Extraer parámetros
    amplitude, position, width = popt
    perr = np.sqrt(np.diag(pcov))

    # Calcular área (integral de lorentziana = amplitude * pi * width)
    area = amplitude * np.pi * width

    # Calcular espectro ajustado y residual
    fitted = _lorentzian(spectrum.binding_energy, amplitude, position, width)
    residual = spectrum.intensity - fitted

    # Calcular R² y chi²
    ss_res = np.sum(residual**2)
    ss_tot = np.sum((spectrum.intensity - np.mean(spectrum.intensity)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    n_params = 3
    dof = len(spectrum.intensity) - n_params
    chi_squared = ss_res / dof if dof > 0 else np.inf

    # Crear PeakParameters
    peak = PeakParameters(
        position=position,
        amplitude=amplitude,
        width=width,
        area=area,
        shape="lorentzian",
        position_error=perr[1],
        amplitude_error=perr[0],
        width_error=perr[2],
    )

    return FitResult(
        peaks=[peak],
        fitted_spectrum=fitted,
        residual=residual,
        r_squared=r_squared,
        chi_squared=chi_squared,
        success=success,
        message=message,
    )


def fit_voigt(
    spectrum: XPSSpectrum,
    initial_position: float | None = None,
    initial_amplitude: float | None = None,
    initial_sigma: float = 0.5,
    initial_gamma: float = 0.5,
    bounds: tuple[list, list] | None = None,
) -> FitResult:
    """
    Ajusta un pico Voigt a un espectro XPS.

    El perfil Voigt es una convolución de perfiles gaussiano y lorentziano,
    lo cual es más realista para XPS ya que considera tanto el ensanchamiento
    instrumental (gaussiano) como el tiempo de vida del estado (lorentziano).

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro XPS a ajustar.
    initial_position : float, opcional
        Posición inicial del pico (eV). Si None, se usa el máximo del espectro.
    initial_amplitude : float, opcional
        Amplitud inicial. Si None, se usa la intensidad máxima.
    initial_sigma : float, default=0.5
        Ancho gaussiano inicial (sigma en eV).
    initial_gamma : float, default=0.5
        Ancho lorentziano inicial (gamma en eV).
    bounds : tuple[list, list], opcional
        Límites para los parámetros [amplitude, position, sigma, gamma].

    Retorna
    -------
    FitResult
        Objeto con los resultados del ajuste.

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.
        Si el ajuste no converge.

    Notas
    -----
    El perfil Voigt es más lento de ajustar que gaussiano o lorentziano,
    pero proporciona un modelo más físicamente preciso para XPS.
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError("El espectro debe tener al menos 3 puntos para ajustar")

    # Estimación de parámetros iniciales
    if initial_position is None:
        max_idx = np.argmax(spectrum.intensity)
        initial_position = spectrum.binding_energy[max_idx]

    if initial_amplitude is None:
        initial_amplitude = np.max(spectrum.intensity)

    p0 = [initial_amplitude, initial_position, initial_sigma, initial_gamma]

    # Configurar límites si no se proporcionan
    if bounds is None:
        energy_range = np.ptp(spectrum.binding_energy)
        bounds = (
            [0, np.min(spectrum.binding_energy), 0.05, 0.05],
            [
                np.max(spectrum.intensity) * 2,
                np.max(spectrum.binding_energy),
                energy_range / 2,
                energy_range / 2,
            ],
        )

    # Ajustar
    try:
        popt, pcov = curve_fit(
            _voigt,
            spectrum.binding_energy,
            spectrum.intensity,
            p0=p0,
            bounds=bounds,
            maxfev=20000,  # Voigt requiere más iteraciones
        )
        success = True
        message = "Ajuste convergió exitosamente"
    except RuntimeError as e:
        raise ValueError(f"El ajuste Voigt no convergió: {e}") from e

    # Extraer parámetros
    amplitude, position, sigma, gamma = popt
    perr = np.sqrt(np.diag(pcov))

    # Calcular área (aproximación para Voigt)
    # Área ≈ amplitude * (sigma + gamma) * sqrt(2*pi)
    area = amplitude * (sigma + gamma) * np.sqrt(2 * np.pi)

    # Calcular espectro ajustado y residual
    fitted = _voigt(spectrum.binding_energy, amplitude, position, sigma, gamma)
    residual = spectrum.intensity - fitted

    # Calcular R² y chi²
    ss_res = np.sum(residual**2)
    ss_tot = np.sum((spectrum.intensity - np.mean(spectrum.intensity)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    n_params = 4
    dof = len(spectrum.intensity) - n_params
    chi_squared = ss_res / dof if dof > 0 else np.inf

    # Crear PeakParameters
    peak = PeakParameters(
        position=position,
        amplitude=amplitude,
        width=sigma,  # FWHM efectivo
        area=area,
        shape="voigt",
        gamma=gamma,
        position_error=perr[1],
        amplitude_error=perr[0],
        width_error=perr[2],
    )

    return FitResult(
        peaks=[peak],
        fitted_spectrum=fitted,
        residual=residual,
        r_squared=r_squared,
        chi_squared=chi_squared,
        success=success,
        message=message,
    )


def fit_multiple_peaks(
    spectrum: XPSSpectrum,
    n_peaks: int | None = None,
    peak_positions: list[float] | None = None,
    shape: Literal["gaussian", "lorentzian", "voigt"] = "gaussian",
    auto_estimate: bool = True,
) -> FitResult:
    """
    Ajusta múltiples picos simultáneamente a un espectro XPS.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro XPS a ajustar.
    n_peaks : int, opcional
        Número de picos a ajustar. Requerido si peak_positions=None.
    peak_positions : list[float], opcional
        Posiciones iniciales de los picos (eV). Si None, se estiman automáticamente.
    shape : {"gaussian", "lorentzian", "voigt"}, default="gaussian"
        Tipo de perfil a usar para todos los picos.
    auto_estimate : bool, default=True
        Si True, estima automáticamente posiciones iniciales si no se proporcionan.

    Retorna
    -------
    FitResult
        Objeto con los resultados del ajuste múltiple.

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.
        Si n_peaks y peak_positions son ambos None.
        Si n_peaks < 1.

    Notas
    -----
    - Para espectros complejos, se recomienda proporcionar peak_positions manualmente
    - El ajuste múltiple es más lento que ajustar picos individuales
    - Se asume que todos los picos tienen el mismo tipo de perfil
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError("El espectro debe tener al menos 3 puntos para ajustar")

    # Validar entrada
    if peak_positions is None and n_peaks is None:
        raise ValueError("Debe proporcionar n_peaks o peak_positions")

    if n_peaks is not None and n_peaks < 1:
        raise ValueError("n_peaks debe ser al menos 1")

    # Estimar posiciones si no se proporcionan
    if peak_positions is None and auto_estimate:
        peak_positions = estimate_peak_positions(spectrum)
        if len(peak_positions) < n_peaks:  # type: ignore
            raise ValueError(
                f"Solo se detectaron {len(peak_positions)} picos, "
                f"pero se solicitaron {n_peaks}"
            )
        peak_positions = peak_positions[:n_peaks]  # type: ignore
    elif peak_positions is None:
        raise ValueError(
            "auto_estimate=False requiere proporcionar peak_positions explícitamente"
        )

    n_peaks_actual = len(peak_positions)

    # Definir función multi-pico según el shape
    if shape == "gaussian":

        def multi_peak_func(x: np.ndarray, *params: float) -> np.ndarray:
            """Suma de gaussianas."""
            result = np.zeros_like(x)
            for i in range(n_peaks_actual):
                amp = params[i * 3]
                pos = params[i * 3 + 1]
                width = params[i * 3 + 2]
                result += _gaussian(x, amp, pos, width)
            return result

        n_params_per_peak = 3
    elif shape == "lorentzian":

        def multi_peak_func(x: np.ndarray, *params: float) -> np.ndarray:
            """Suma de lorentzianas."""
            result = np.zeros_like(x)
            for i in range(n_peaks_actual):
                amp = params[i * 3]
                pos = params[i * 3 + 1]
                width = params[i * 3 + 2]
                result += _lorentzian(x, amp, pos, width)
            return result

        n_params_per_peak = 3
    elif shape == "voigt":

        def multi_peak_func(x: np.ndarray, *params: float) -> np.ndarray:
            """Suma de perfiles Voigt."""
            result = np.zeros_like(x)
            for i in range(n_peaks_actual):
                amp = params[i * 4]
                pos = params[i * 4 + 1]
                sigma = params[i * 4 + 2]
                gamma = params[i * 4 + 3]
                result += _voigt(x, amp, pos, sigma, gamma)
            return result

        n_params_per_peak = 4
    else:
        raise ValueError(
            f"Shape '{shape}' no reconocido. Use 'gaussian', 'lorentzian' o 'voigt'"
        )

    # Construir parámetros iniciales
    p0 = []
    lower_bounds = []
    upper_bounds = []

    max_intensity = np.max(spectrum.intensity)
    energy_min = np.min(spectrum.binding_energy)
    energy_max = np.max(spectrum.binding_energy)
    energy_range = np.ptp(spectrum.binding_energy)

    for pos in peak_positions:
        if shape in ["gaussian", "lorentzian"]:
            # [amplitude, position, width]
            p0.extend([max_intensity / n_peaks_actual, pos, 1.0])
            lower_bounds.extend([0, energy_min, 0.1])
            upper_bounds.extend([max_intensity * 2, energy_max, energy_range])
        else:  # voigt
            # [amplitude, position, sigma, gamma]
            p0.extend([max_intensity / n_peaks_actual, pos, 0.5, 0.5])
            lower_bounds.extend([0, energy_min, 0.05, 0.05])
            upper_bounds.extend(
                [max_intensity * 2, energy_max, energy_range / 2, energy_range / 2]
            )

    bounds = (lower_bounds, upper_bounds)

    # Ajustar
    try:
        popt, pcov = curve_fit(
            multi_peak_func,
            spectrum.binding_energy,
            spectrum.intensity,
            p0=p0,
            bounds=bounds,
            maxfev=30000,  # Ajuste múltiple requiere muchas iteraciones
        )
        success = True
        message = f"Ajuste de {n_peaks_actual} picos convergió exitosamente"
    except RuntimeError as e:
        raise ValueError(f"El ajuste múltiple no convergió: {e}") from e

    # Extraer parámetros de cada pico
    perr = np.sqrt(np.diag(pcov))
    peaks_list = []

    for i in range(n_peaks_actual):
        if shape in ["gaussian", "lorentzian"]:
            idx = i * 3
            amplitude = popt[idx]
            position = popt[idx + 1]
            width = popt[idx + 2]

            if shape == "gaussian":
                area = amplitude * width * np.sqrt(2 * np.pi)
            else:  # lorentzian
                area = amplitude * np.pi * width

            peak = PeakParameters(
                position=position,
                amplitude=amplitude,
                width=width,
                area=area,
                shape=shape,
                position_error=perr[idx + 1],
                amplitude_error=perr[idx],
                width_error=perr[idx + 2],
            )
        else:  # voigt
            idx = i * 4
            amplitude = popt[idx]
            position = popt[idx + 1]
            sigma = popt[idx + 2]
            gamma = popt[idx + 3]
            area = amplitude * (sigma + gamma) * np.sqrt(2 * np.pi)

            peak = PeakParameters(
                position=position,
                amplitude=amplitude,
                width=sigma,
                area=area,
                shape=shape,
                gamma=gamma,
                position_error=perr[idx + 1],
                amplitude_error=perr[idx],
                width_error=perr[idx + 2],
            )

        peaks_list.append(peak)

    # Calcular espectro ajustado total
    fitted = multi_peak_func(spectrum.binding_energy, *popt)
    residual = spectrum.intensity - fitted

    # Calcular R² y chi²
    ss_res = np.sum(residual**2)
    ss_tot = np.sum((spectrum.intensity - np.mean(spectrum.intensity)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    total_params = n_peaks_actual * n_params_per_peak
    dof = len(spectrum.intensity) - total_params
    chi_squared = ss_res / dof if dof > 0 else np.inf

    return FitResult(
        peaks=peaks_list,
        fitted_spectrum=fitted,
        residual=residual,
        r_squared=r_squared,
        chi_squared=chi_squared,
        success=success,
        message=message,
    )


# ============================================================================
# Doublet fitting with spin-orbit constraints (Fase E)
# ============================================================================


def fit_doublet(
    spectrum: XPSSpectrum,
    initial_position: float | None = None,
    splitting: float = 5.7,
    intensity_ratio: float = 2.0,
    shape: Literal["gaussian", "lorentzian", "voigt"] = "voigt",
    constrain_widths: bool = True,
) -> FitResult:
    """
    Ajusta un doblete spin-órbita con constraints físicos.

    Los dobletes spin-órbita son comunes en XPS para orbitales p, d y f.
    Esta función ajusta dos picos simultáneamente con las siguientes constraints:
    - Separación fija (splitting)
    - Ratio de intensidad fijo (determinado por reglas de selección)
    - Mismo ancho (opcional, típicamente válido)

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro XPS a ajustar.
    initial_position : float, opcional
        Posición inicial estimada del pico de mayor intensidad (eV).
        Si None, se estima automáticamente como el máximo del espectro.
    splitting : float, default=5.7
        Separación spin-órbita en eV. Valores típicos:
        - Ti 2p: 5.7 eV
        - Bi 4f: 5.3 eV
        - Sr 3d: 1.8 eV
        - O 1s: no tiene doblete (s orbital)
    intensity_ratio : float, default=2.0
        Ratio de intensidad entre los componentes (I1/I2).
        Determinado por multiplicidad: (2j1+1)/(2j2+1)
        - 2p (2p3/2 : 2p1/2): 2.0
        - 3d (3d5/2 : 3d3/2): 1.5
        - 4f (4f7/2 : 4f5/2): 1.33
    shape : {"gaussian", "lorentzian", "voigt"}, default="voigt"
        Tipo de perfil a usar para ambos picos.
    constrain_widths : bool, default=True
        Si True, ambos picos tienen el mismo ancho (físicamente esperado).
        Si False, permite anchos diferentes.

    Retorna
    -------
    FitResult
        Objeto con los resultados del ajuste del doblete.
        Los dos picos se almacenan en orden de energía decreciente
        (pico más intenso primero).

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 5 puntos.
        Si splitting <= 0.
        Si intensity_ratio <= 0.

    Notas
    -----
    Esta función fue implementada en Fase E para resolver el problema
    identificado en validación (Fase D):
    - Ti 2p con ajuste de pico único: R² = 0.407 (pobre)
    - Bi 4f con ajuste de pico único: R² = 0.619 (moderado)

    Con constraints de doblete, se espera R² > 0.80 para ambos casos.

    Ejemplos
    --------
    >>> # Ajustar Ti 2p (splitting=5.7 eV, ratio=2.0)
    >>> result = fit_doublet(spectrum, splitting=5.7, intensity_ratio=2.0)

    >>> # Ajustar Bi 4f (splitting=5.3 eV, ratio=1.33)
    >>> result = fit_doublet(spectrum, splitting=5.3, intensity_ratio=1.33)

    >>> # Ajustar Sr 3d (splitting=1.8 eV, ratio=1.5)
    >>> result = fit_doublet(spectrum, splitting=1.8, intensity_ratio=1.5)

    Referencias
    ----------
    Hallazgos de validación documentados en:
    data/results/BN-SET-01/FASE_D_COMPLETADA.md (líneas 124-139)
    data/results/BN-SET-01/COMPARATIVE_ANALYSIS.md (líneas 46-54)

    Biesinger, M. C. (2017). "Advanced analysis of copper X-ray photoelectron
    spectra". Surface and Interface Analysis, 49(13), 1325-1334.
    """
    if len(spectrum.binding_energy) < 5:
        raise ValueError(
            "El espectro debe tener al menos 5 puntos para ajustar doblete"
        )

    if splitting <= 0:
        raise ValueError(f"splitting debe ser positivo, recibido: {splitting}")

    if intensity_ratio <= 0:
        raise ValueError(
            f"intensity_ratio debe ser positivo, recibido: {intensity_ratio}"
        )

    # Estimar posición inicial si no se proporciona
    if initial_position is None:
        # Usar máximo del espectro
        max_idx = np.argmax(spectrum.intensity)
        initial_position = spectrum.binding_energy[max_idx]

    # Estimar amplitud y ancho inicial
    max_intensity = np.max(spectrum.intensity)
    estimated_width = 1.5  # eV, típico para XPS

    # Extraer datos
    x = spectrum.binding_energy
    y = spectrum.intensity

    # Definir función de doblete con constraints
    if constrain_widths:
        # Caso 1: Mismo ancho para ambos picos (5 parámetros)
        if shape == "gaussian":

            def doublet_func(
                x: np.ndarray, amp1: float, pos1: float, width: float, offset: float
            ) -> np.ndarray:
                """Doblete gaussiano con constraints."""
                # Pico 1 (más intenso)
                peak1 = _gaussian(x, amp1, pos1, width)
                # Pico 2 (menos intenso, separado por splitting)
                amp2 = amp1 / intensity_ratio
                pos2 = pos1 + splitting
                peak2 = _gaussian(x, amp2, pos2, width)
                return peak1 + peak2 + offset

            n_params = 4

        elif shape == "lorentzian":

            def doublet_func(
                x: np.ndarray, amp1: float, pos1: float, width: float, offset: float
            ) -> np.ndarray:
                """Doblete lorentziano con constraints."""
                peak1 = _lorentzian(x, amp1, pos1, width)
                amp2 = amp1 / intensity_ratio
                pos2 = pos1 + splitting
                peak2 = _lorentzian(x, amp2, pos2, width)
                return peak1 + peak2 + offset

            n_params = 4

        elif shape == "voigt":

            def doublet_func(
                x: np.ndarray,
                amp1: float,
                pos1: float,
                sigma: float,
                gamma: float,
                offset: float,
            ) -> np.ndarray:
                """Doblete Voigt con constraints."""
                peak1 = _voigt(x, amp1, pos1, sigma, gamma)
                amp2 = amp1 / intensity_ratio
                pos2 = pos1 + splitting
                peak2 = _voigt(x, amp2, pos2, sigma, gamma)
                return peak1 + peak2 + offset

            n_params = 5

        else:
            raise ValueError(f"shape inválido: {shape}")

    else:
        # Caso 2: Anchos diferentes (6 parámetros para gaussian/lorentzian, 7 para voigt)
        if shape == "gaussian":

            def doublet_func(
                x: np.ndarray,
                amp1: float,
                pos1: float,
                width1: float,
                width2: float,
                offset: float,
            ) -> np.ndarray:
                """Doblete gaussiano sin constraint de ancho."""
                peak1 = _gaussian(x, amp1, pos1, width1)
                amp2 = amp1 / intensity_ratio
                pos2 = pos1 + splitting
                peak2 = _gaussian(x, amp2, pos2, width2)
                return peak1 + peak2 + offset

            n_params = 5

        elif shape == "lorentzian":

            def doublet_func(
                x: np.ndarray,
                amp1: float,
                pos1: float,
                width1: float,
                width2: float,
                offset: float,
            ) -> np.ndarray:
                """Doblete lorentziano sin constraint de ancho."""
                peak1 = _lorentzian(x, amp1, pos1, width1)
                amp2 = amp1 / intensity_ratio
                pos2 = pos1 + splitting
                peak2 = _lorentzian(x, amp2, pos2, width2)
                return peak1 + peak2 + offset

            n_params = 5

        elif shape == "voigt":

            def doublet_func(
                x: np.ndarray,
                amp1: float,
                pos1: float,
                sigma1: float,
                gamma1: float,
                sigma2: float,
                gamma2: float,
                offset: float,
            ) -> np.ndarray:
                """Doblete Voigt sin constraint de ancho."""
                peak1 = _voigt(x, amp1, pos1, sigma1, gamma1)
                amp2 = amp1 / intensity_ratio
                pos2 = pos1 + splitting
                peak2 = _voigt(x, amp2, pos2, sigma2, gamma2)
                return peak1 + peak2 + offset

            n_params = 7

        else:
            raise ValueError(f"shape inválido: {shape}")

    # Estimar offset (mínimo del espectro)
    offset_estimate = np.min(y)

    # Parámetros iniciales
    if constrain_widths:
        if shape == "voigt":
            p0 = [
                max_intensity,
                initial_position,
                estimated_width,
                estimated_width,
                offset_estimate,
            ]
            bounds_lower = [0, x.min(), 0.1, 0.1, -np.inf]
            bounds_upper = [np.inf, x.max(), 10.0, 10.0, np.inf]
        else:
            p0 = [max_intensity, initial_position, estimated_width, offset_estimate]
            bounds_lower = [0, x.min(), 0.1, -np.inf]
            bounds_upper = [np.inf, x.max(), 10.0, np.inf]
    else:
        if shape == "voigt":
            p0 = [
                max_intensity,
                initial_position,
                estimated_width,
                estimated_width,
                estimated_width,
                estimated_width,
                offset_estimate,
            ]
            bounds_lower = [0, x.min(), 0.1, 0.1, 0.1, 0.1, -np.inf]
            bounds_upper = [np.inf, x.max(), 10.0, 10.0, 10.0, 10.0, np.inf]
        else:
            p0 = [
                max_intensity,
                initial_position,
                estimated_width,
                estimated_width,
                offset_estimate,
            ]
            bounds_lower = [0, x.min(), 0.1, 0.1, -np.inf]
            bounds_upper = [np.inf, x.max(), 10.0, 10.0, np.inf]

    # Ajustar
    try:
        popt, pcov = curve_fit(
            doublet_func, x, y, p0=p0, bounds=(bounds_lower, bounds_upper), maxfev=10000
        )
        success = True
        message = "Ajuste de doblete exitoso"
    except RuntimeError as e:
        success = False
        message = f"Ajuste de doblete falló: {str(e)}"
        # Retornar resultado fallido con parámetros iniciales
        popt = np.array(p0)
        pcov = np.diag(np.ones(len(p0)) * np.inf)

    # Calcular espectro ajustado y residual
    fitted = doublet_func(x, *popt)
    residual = y - fitted

    # Calcular R² y chi²
    ss_res = np.sum(residual**2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    n_points = len(x)
    dof = n_points - n_params
    chi_squared = ss_res / dof if dof > 0 else np.inf

    # Extraer parámetros de los picos
    perr = np.sqrt(np.diag(pcov)) if success else np.ones(len(popt)) * np.inf

    if constrain_widths:
        if shape == "voigt":
            amp1, pos1, sigma, gamma, offset = popt
            amp1_err, pos1_err, sigma_err, gamma_err, _ = perr
            width1 = sigma
            width2 = sigma
            width1_err = sigma_err
            width2_err = sigma_err
            gamma1 = gamma
            gamma2 = gamma
        else:
            amp1, pos1, width, offset = popt
            amp1_err, pos1_err, width_err, _ = perr
            width1 = width
            width2 = width
            width1_err = width_err
            width2_err = width_err
            gamma1 = None
            gamma2 = None
    else:
        if shape == "voigt":
            amp1, pos1, sigma1, gamma1, sigma2, gamma2, offset = popt
            amp1_err, pos1_err, sigma1_err, gamma1_err, sigma2_err, gamma2_err, _ = perr
            width1 = sigma1
            width2 = sigma2
            width1_err = sigma1_err
            width2_err = sigma2_err
        else:
            amp1, pos1, width1, width2, offset = popt
            amp1_err, pos1_err, width1_err, width2_err, _ = perr
            gamma1 = None
            gamma2 = None

    # Pico 1 (más intenso)
    amp2 = amp1 / intensity_ratio
    pos2 = pos1 + splitting
    amp2_err = amp1_err / intensity_ratio
    pos2_err = pos1_err  # Asumimos mismo error en posición

    # Calcular áreas (aproximación para gaussiano/lorentziano: área ≈ amp * width)
    if shape == "gaussian":
        area1 = amp1 * width1 * np.sqrt(2 * np.pi)
        area2 = amp2 * width2 * np.sqrt(2 * np.pi)
    elif shape == "lorentzian":
        area1 = amp1 * width1 * np.pi
        area2 = amp2 * width2 * np.pi
    else:  # voigt
        # Área Voigt: más complejo, usar aproximación
        area1 = amp1 * width1 * np.sqrt(2 * np.pi)
        area2 = amp2 * width2 * np.sqrt(2 * np.pi)

    peak1 = PeakParameters(
        position=pos1,
        amplitude=amp1,
        width=width1,
        area=area1,
        shape=shape,
        gamma=gamma1,
        position_error=pos1_err,
        amplitude_error=amp1_err,
        width_error=width1_err,
    )

    peak2 = PeakParameters(
        position=pos2,
        amplitude=amp2,
        width=width2,
        area=area2,
        shape=shape,
        gamma=gamma2,
        position_error=pos2_err,
        amplitude_error=amp2_err,
        width_error=width2_err,
    )

    return FitResult(
        peaks=[peak1, peak2],
        fitted_spectrum=fitted,
        residual=residual,
        r_squared=r_squared,
        chi_squared=chi_squared,
        success=success,
        message=message,
    )
