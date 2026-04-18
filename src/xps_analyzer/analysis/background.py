"""
Módulo para sustracción de fondo en espectros XPS.

Este módulo implementa métodos estándar de sustracción de fondo utilizados
en análisis XPS, incluyendo Shirley y Tougaard.
"""

from __future__ import annotations

from xps_analyzer.data_loader import XPSSpectrum

import numpy as np


def shirley_background(
    spectrum: XPSSpectrum,
    tol: float = 1e-5,
    max_iter: int = 100,
    inplace: bool = False,
) -> XPSSpectrum:
    """
    Calcula y sustrae el fondo Shirley de un espectro XPS.

    El algoritmo de Shirley es el método más utilizado para sustracción de fondo
    en XPS. Asume que el fondo en cada punto es proporcional a la intensidad
    integrada de todos los picos a energías más altas.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        El espectro al cual sustraer el fondo.
    tol : float, default=1e-5
        Tolerancia para convergencia del algoritmo iterativo.
    max_iter : int, default=100
        Número máximo de iteraciones.
    inplace : bool, default=False
        Si True, modifica el espectro original. Si False, retorna una copia.

    Retorna
    -------
    XPSSpectrum
        Espectro con el fondo Shirley sustraído. El fondo calculado se almacena
        en metadata["shirley_background"].

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.
        Si el algoritmo no converge en max_iter iteraciones.

    Notas
    -----
    El algoritmo es iterativo y converge cuando el cambio en el fondo entre
    iteraciones es menor que `tol` veces la intensidad máxima.

    Referencias
    ----------
    Shirley, D. A. (1972). "High-Resolution X-Ray Photoemission Spectrum of
    the Valence Bands of Gold". Physical Review B, 5(12), 4709-4714.

    Ejemplos
    --------
    >>> spectrum = XPSSpectrum(...)
    >>> bg_subtracted = shirley_background(spectrum)
    >>> # El fondo está en bg_subtracted.metadata["shirley_background"]
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError(
            f"El espectro debe tener al menos 3 puntos, tiene {len(spectrum.binding_energy)}"
        )

    # Trabajar con copia si es necesario
    if inplace:
        result = spectrum
    else:
        result = spectrum.model_copy(deep=True)

    # Extraer datos (ordenar por energía creciente para el algoritmo)
    energy = result.binding_energy
    intensity = result.intensity.copy()

    # Verificar que las energías estén ordenadas (asumir orden decreciente típico en XPS)
    if energy[0] < energy[-1]:
        # Ya están en orden creciente
        inverted = False
    else:
        # Invertir para orden creciente
        energy = energy[::-1]
        intensity = intensity[::-1]
        inverted = True

    # Valores iniciales para el algoritmo iterativo
    # El fondo Shirley se estima entre los valores de los extremos
    background = np.linspace(intensity[0], intensity[-1], len(intensity))

    # Iteración del algoritmo de Shirley
    change = 1.0  # Inicializar change antes del loop
    final_iteration = 0  # Contador de iteraciones completadas
    for final_iteration in range(max_iter):
        # Guardar fondo anterior para verificar convergencia
        background_old = background.copy()

        # Calcular intensidad neta (espectro - fondo actual)
        net_intensity = intensity - background

        # Integral acumulada de la intensidad neta desde alta energía
        # (integral desde el final hacia el principio)
        cumsum = np.cumsum(net_intensity[::-1])[::-1]

        # Normalizar por la integral total
        total_area = cumsum[0]
        if total_area > 0:
            # Nuevo fondo: proporcional a la integral desde cada punto
            # hasta el final, escalado entre los valores de los extremos
            background = intensity[-1] + (intensity[0] - intensity[-1]) * (
                cumsum / total_area
            )
        else:
            # Si la integral es cero o negativa, usar fondo lineal
            background = np.linspace(intensity[0], intensity[-1], len(intensity))

        # Verificar convergencia
        max_intensity = np.max(intensity)
        if max_intensity > 0:
            change = np.max(np.abs(background - background_old)) / max_intensity
            if change < tol:
                final_iteration += 1  # Incrementar para contar esta iteración
                break
    else:
        # No convergió en max_iter iteraciones
        final_iteration = max_iter  # Se completaron todas las iteraciones
        raise ValueError(
            f"El algoritmo de Shirley no convergió después de {max_iter} iteraciones "
            f"(iteración {final_iteration}/{max_iter}). "
            f"Cambio final: {change:.2e}, tolerancia: {tol:.2e}"
        )

    # Revertir orden si fue necesario
    if inverted:
        background = background[::-1]

    # Sustraer fondo
    result.intensity = result.intensity - background

    # Almacenar el fondo en metadata para referencia
    result.metadata["shirley_background"] = background
    result.metadata["shirley_iterations"] = final_iteration

    return result


def tougaard_background(
    spectrum: XPSSpectrum,
    B: float = 2866.0,  # noqa: N803 - Parámetro estándar de Tougaard
    C: float = 1643.0,  # noqa: N803 - Parámetro estándar de Tougaard
    D: float = 1.0,  # noqa: N803 - Parámetro estándar de Tougaard
    inplace: bool = False,
) -> XPSSpectrum:
    """
    Calcula y sustrae el fondo Tougaard de un espectro XPS.

    El algoritmo de Tougaard modela el fondo basándose en la dispersión
    inelástica de electrones usando una función universal de pérdida de energía.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        El espectro al cual sustraer el fondo.
    B : float, default=2866.0
        Parámetro B de Tougaard (eV2).
    C : float, default=1643.0
        Parámetro C de Tougaard (eV2).
    D : float, default=1.0
        Parámetro D de Tougaard (adimensional).
    inplace : bool, default=False
        Si True, modifica el espectro original. Si False, retorna una copia.

    Retorna
    -------
    XPSSpectrum
        Espectro con el fondo Tougaard sustraído. El fondo calculado se almacena
        en metadata["tougaard_background"].

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 3 puntos.

    Notas
    -----
    Los parámetros por defecto (B=2866, C=1643, D=1) son para materiales
    orgánicos. Otros materiales pueden requerir parámetros diferentes:
    - Metales: B=1600, C=400
    - Semiconductores: B=2400, C=1200

    Referencias
    ----------
    Tougaard, S. (1997). "QUASES-IMFP-TPP2M: Software Package for Quantitative
    Analysis of Electron Spectra". Surface and Interface Analysis, 25(3), 137-154.

    Ejemplos
    --------
    >>> spectrum = XPSSpectrum(...)
    >>> # Para material orgánico (valores por defecto)
    >>> bg_subtracted = tougaard_background(spectrum)
    >>>
    >>> # Para metal
    >>> bg_subtracted = tougaard_background(spectrum, B=1600, C=400)
    """
    if len(spectrum.binding_energy) < 3:
        raise ValueError(
            f"El espectro debe tener al menos 3 puntos, tiene {len(spectrum.binding_energy)}"
        )

    # Trabajar con copia si es necesario
    if inplace:
        result = spectrum
    else:
        result = spectrum.model_copy(deep=True)

    # Extraer datos
    energy = result.binding_energy
    intensity = result.intensity.copy()

    # Verificar orden de energías (Tougaard necesita orden creciente)
    if energy[0] < energy[-1]:
        # Ya en orden creciente
        inverted = False
    else:
        # Invertir
        energy = energy[::-1]
        intensity = intensity[::-1]
        inverted = True

    # Calcular paso de energía (asumir uniforme)
    de = np.mean(np.diff(energy))  # dE: paso de energía

    # Inicializar fondo
    background = np.zeros_like(intensity)

    # Calcular fondo Tougaard
    # Para cada punto i, el fondo es la suma de contribuciones de todos
    # los puntos j con energía mayor (j > i)
    for i in range(len(energy)):
        # Energía en el punto actual
        e_i = energy[i]  # E_i: energía en punto i

        # Sumar contribuciones de puntos con mayor energía
        for j in range(i + 1, len(energy)):
            e_j = energy[j]  # E_j: energía en punto j
            delta_e = e_j - e_i  # Pérdida de energía (Delta E)

            if delta_e > 0:
                # Función de pérdida de energía de Tougaard
                # K(T) = B*T / [(C + D*T^2)^2]
                # donde T = pérdida de energía
                t = delta_e  # T: pérdida de energía en la fórmula de Tougaard
                k = (B * t) / ((C + D * t**2) ** 2)  # K: función de pérdida

                # Contribución al fondo en i desde j
                background[i] += intensity[j] * k * de

    # Revertir orden si fue necesario
    if inverted:
        background = background[::-1]

    # Sustraer fondo
    result.intensity = result.intensity - background

    # Almacenar el fondo en metadata
    result.metadata["tougaard_background"] = background
    result.metadata["tougaard_params"] = {"B": B, "C": C, "D": D}

    return result


def linear_background(spectrum: XPSSpectrum, inplace: bool = False) -> XPSSpectrum:
    """
    Calcula y sustrae un fondo lineal de un espectro XPS.

    El fondo lineal es simplemente una línea recta entre los puntos extremos
    del espectro. Es el método más simple pero menos preciso.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        El espectro al cual sustraer el fondo.
    inplace : bool, default=False
        Si True, modifica el espectro original. Si False, retorna una copia.

    Retorna
    -------
    XPSSpectrum
        Espectro con el fondo lineal sustraído. El fondo calculado se almacena
        en metadata["linear_background"].

    Raises
    ------
    ValueError
        Si el espectro tiene menos de 2 puntos.

    Ejemplos
    --------
    >>> spectrum = XPSSpectrum(...)
    >>> bg_subtracted = linear_background(spectrum)
    """
    if len(spectrum.binding_energy) < 2:
        raise ValueError(
            f"El espectro debe tener al menos 2 puntos, tiene {len(spectrum.binding_energy)}"
        )

    # Trabajar con copia si es necesario
    if inplace:
        result = spectrum
    else:
        result = spectrum.model_copy(deep=True)

    # Calcular fondo lineal entre extremos
    intensity = result.intensity
    background = np.linspace(intensity[0], intensity[-1], len(intensity))

    # Sustraer fondo
    result.intensity = result.intensity - background

    # Almacenar el fondo en metadata
    result.metadata["linear_background"] = background

    return result


def background_with_fallback(
    spectrum: XPSSpectrum,
    methods: list[str] | None = None,
    shirley_max_iter: int = 100,
    shirley_tol: float = 1e-5,
    tougaard_B: float = 2866.0,
    tougaard_C: float = 1643.0,
    tougaard_D: float = 1.0,
    inplace: bool = False,
) -> XPSSpectrum:
    """
    Calcula y sustrae el fondo de un espectro XPS con cascada de fallbacks.

    Esta función intenta múltiples métodos de sustracción de fondo en orden,
    usando el siguiente método si el anterior falla. Esto aumenta la robustez
    del análisis cuando se trabaja con datos experimentales de calidad variable.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        El espectro al cual sustraer el fondo.
    methods : list[str] | None, default=None
        Lista de métodos a intentar en orden. Si None, usa ["shirley", "tougaard", "linear"].
        Métodos válidos: "shirley", "tougaard", "linear".
    shirley_max_iter : int, default=100
        Número máximo de iteraciones para Shirley.
    shirley_tol : float, default=1e-5
        Tolerancia de convergencia para Shirley.
    tougaard_B : float, default=2866.0
        Parámetro B de Tougaard (eV2).
    tougaard_C : float, default=1643.0
        Parámetro C de Tougaard (eV2).
    tougaard_D : float, default=1.0
        Parámetro D de Tougaard (adimensional).
    inplace : bool, default=False
        Si True, modifica el espectro original. Si False, retorna una copia.

    Retorna
    -------
    XPSSpectrum
        Espectro con el fondo sustraído. El método utilizado se almacena
        en metadata["background_method"].

    Raises
    ------
    ValueError
        Si todos los métodos fallan.
        Si se proporciona un método inválido.

    Notas
    -----
    El orden de fallback por defecto está diseñado según precisión decreciente:
    1. Shirley - Más preciso pero puede no converger en espectros complejos
    2. Tougaard - Más robusto para fondos con estructura
    3. Linear - Siempre funciona pero menos preciso

    En validación con dataset BN-SET-1, esta estrategia aumentó la tasa de
    éxito de sustracción de fondo del 54% al 100%, permitiendo procesar todas
    las regiones incluso con datos de calidad variable.

    Ejemplos
    --------
    >>> # Uso por defecto (cascada completa)
    >>> spectrum_clean = background_with_fallback(spectrum)
    >>> print(spectrum_clean.metadata["background_method"])  # ej: "shirley"

    >>> # Solo intentar Shirley y linear (omitir Tougaard)
    >>> spectrum_clean = background_with_fallback(spectrum, methods=["shirley", "linear"])

    >>> # Ajustar parámetros de Shirley (más iteraciones para espectros difíciles)
    >>> spectrum_clean = background_with_fallback(
    ...     spectrum, shirley_max_iter=200, shirley_tol=1e-4
    ... )

    >>> # Ajustar parámetros de Tougaard
    >>> spectrum_clean = background_with_fallback(
    ...     spectrum, tougaard_B=3000.0, tougaard_C=1500.0
    ... )

    Referencias
    ----------
    Hallazgos de validación documentados en:
    data/results/BN-SET-1/FASE_D_COMPLETADA.md
    data/results/BN-SET-1/COMPARATIVE_ANALYSIS.md
    """
    # Métodos por defecto
    if methods is None:
        methods = ["shirley", "tougaard", "linear"]

    # Validar métodos
    valid_methods = {"shirley", "tougaard", "linear"}
    for method in methods:
        if method not in valid_methods:
            raise ValueError(
                f"Método inválido '{method}'. Métodos válidos: {valid_methods}"
            )

    # Trabajar con copia si es necesario
    if not inplace:
        spectrum = spectrum.model_copy(deep=True)

    # Intentar cada método en orden
    errors = {}
    for method in methods:
        try:
            if method == "shirley":
                result = shirley_background(
                    spectrum,
                    max_iter=shirley_max_iter,
                    tol=shirley_tol,
                    inplace=True,
                )
                result.metadata["background_method"] = "shirley"
                result.metadata["background_fallback_attempted"] = list(methods)
                return result

            elif method == "tougaard":
                result = tougaard_background(
                    spectrum, B=tougaard_B, C=tougaard_C, D=tougaard_D, inplace=True
                )
                result.metadata["background_method"] = "tougaard"
                result.metadata["background_fallback_attempted"] = list(methods)
                result.metadata["background_fallback_errors"] = errors
                return result

            elif method == "linear":
                result = linear_background(spectrum, inplace=True)
                result.metadata["background_method"] = "linear"
                result.metadata["background_fallback_attempted"] = list(methods)
                result.metadata["background_fallback_errors"] = errors
                return result

        except Exception as e:
            # Almacenar error y continuar con siguiente método
            errors[method] = str(e)
            continue

    # Si todos los métodos fallaron, lanzar error con detalles
    error_details = "\n".join([f"  - {m}: {e}" for m, e in errors.items()])
    raise ValueError(
        f"Todos los métodos de sustracción de fondo fallaron:\n{error_details}"
    )
