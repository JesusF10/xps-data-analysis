"""Aplicación Streamlit para XPS Analyzer.

Primera versión mínima de la GUI interactiva:

- Carga de un archivo XPS mediante uploader de Streamlit.
- Detección y parsing usando la función existente ``load_single_file``.
- Selección de región espectral disponible en el archivo.
- Visualización del espectro seleccionado con matplotlib respetando
  la convención XPS (eje de energía invertido).

Esta app está pensada como punto de partida para la Fase 2 (GUI
interactiva). La funcionalidad avanzada (calibración, fondo,
ajuste de picos, cuantificación) se integrará en iteraciones
posteriores.

Referencias del artículo "Introductory guide to backgrounds in XPS spectra
and their impact on determining peak intensities" (Engelhard et al., 2020):
- Shirley: recomendado para cambios de paso en fondo (más común)
- Tougaard: teorético, modela inelastic scattering (50-100 eV extensión)
- Linear: solo para fondos planos (no recomendado generalmente)
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from xps_analyzer import load_reference_database, load_single_file
from xps_analyzer.analysis.background import (
    linear_background,
    shirley_background,
    tougaard_background,
)
from xps_analyzer.analysis.peak_fitting import (
    FitResult,
    PeakParameters,
    fit_multiple_peaks,
)
from xps_analyzer.analysis.quantification import (
    _extract_element_from_region_name,
    calculate_atomic_concentration,
    load_sensitivity_factors,
)
from xps_analyzer.data_loader import XPSDataset, XPSSpectrum
from xps_analyzer.preprocessing.calibration import calibrate_sample

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def _save_uploaded_file_to_temp(uploaded_file: Any) -> Path:
    """Guarda un archivo subido por Streamlit en un archivo temporal.

    Parámetros
    ----------
    uploaded_file : Any
        Objeto retornado por ``st.file_uploader``.

    Retorna
    -------
    Path
        Ruta al archivo temporal creado.
    """

    suffix = Path(uploaded_file.name).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = Path(tmp.name)
    return tmp_path


def _slice_spectrum_inplace(
    spectrum: XPSSpectrum, min_be: float, max_be: float
) -> None:
    """Recorta un espectro in-place al rango de energía dado y limpia metadatos."""
    min_val, max_val = sorted([min_be, max_be])
    mask = (spectrum.binding_energy >= min_val) & (spectrum.binding_energy <= max_val)

    spectrum.binding_energy = spectrum.binding_energy[mask]
    spectrum.intensity = spectrum.intensity[mask]

    # Limpiar metadata de procesamientos previos que ya no coinciden en longitud
    keys_to_remove = [
        "shirley_background",
        "tougaard_background",
        "linear_background",
        "background_original_intensity",
        "background_method",
        "fit_result",
    ]
    for k in keys_to_remove:
        if k in spectrum.metadata:
            del spectrum.metadata[k]


@st.cache_data(show_spinner=False)
def _load_dataset_from_bytes(content: bytes, filename: str) -> XPSDataset:
    """Carga un ``XPSDataset`` a partir de contenido binario.

    Esta función está cacheada para evitar recargar el mismo archivo
    en cada interacción de la app.
    """

    path = Path(filename)
    suffix = path.suffix or ".txt"
    # Preservar parte del nombre original (incluyendo "multiplex" si existe)
    prefix = (path.stem.replace(" ", "_") + "_") or "xps_"

    with NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    dataset = load_single_file(tmp_path)
    return dataset


def _get_background_data(spectrum: XPSSpectrum) -> tuple[np.ndarray | None, str]:
    """Obtiene el fondo calculado y su etiqueta desde metadata."""
    if "shirley_background" in spectrum.metadata:
        return spectrum.metadata["shirley_background"], "Background (Shirley)"
    if "tougaard_background" in spectrum.metadata:
        return spectrum.metadata["tougaard_background"], "Background (Tougaard)"
    if "linear_background" in spectrum.metadata:
        return spectrum.metadata["linear_background"], "Background (Linear)"
    return None, ""


def _prepare_spectrum_for_background_subtraction(spectrum: XPSSpectrum) -> None:
    """Prepara el espectro para recalcular fondo sin acumular sustracciones."""
    original_intensity = spectrum.metadata.get("background_original_intensity")
    if original_intensity is not None:
        spectrum.intensity = np.asarray(original_intensity).copy()
    else:
        spectrum.metadata["background_original_intensity"] = spectrum.intensity.copy()

    for key in ["shirley_background", "tougaard_background", "linear_background"]:
        if key in spectrum.metadata:
            del spectrum.metadata[key]


def _analyze_background_characteristics(spectrum: XPSSpectrum) -> dict[str, float]:
    """Analiza características del espectro para recomendar método de fondo.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro a analizar.

    Retorna
    -------
    dict[str, float]
        Diccionario con características:
        - "background_slope": pendiente del fondo normalizada
        - "peak_sharpness": agudeza relativa de los picos (contraste)
        - "noise_level": nivel de ruido normalizado
    """
    intensity = spectrum.intensity

    # Calcular pendiente del fondo: diferencia relativa entre extremos
    # normalizada por el rango de energía
    if len(intensity) > 2:
        intensity_range = np.max(intensity) - np.min(intensity)
        intensity_diff = abs(intensity[-1] - intensity[0])
        bg_slope = (
            intensity_diff / (intensity_range + 1e-6) if intensity_range > 0 else 0.0
        )
    else:
        bg_slope = 0.0

    # Agudeza de picos: relación entre pico máximo y media
    peak_sharpness = (
        (np.max(intensity) - np.mean(intensity)) / (np.mean(intensity) + 1e-6)
        if np.mean(intensity) > 0
        else 0.0
    )

    # Nivel de ruido: desv. estándar normalizada
    noise_level = (
        np.std(np.diff(intensity)) / (np.mean(intensity) + 1e-6)
        if np.mean(intensity) > 0
        else 0.0
    )

    return {
        "background_slope": bg_slope,
        "peak_sharpness": peak_sharpness,
        "noise_level": noise_level,
    }


def _recommend_background_method(spectrum: XPSSpectrum) -> tuple[str, str]:
    """Recomienda método de fondo basado en análisis del espectro.

    Basado en Engelhard et al. (2020) "Introductory guide to backgrounds in XPS spectra":
    - Shirley: para cambios de paso en fondo (más común, ~80% de casos)
    - Tougaard: para comportamiento de inelastic scattering (teórico, 50-100 eV)
    - Linear: solo si fondo casi plano (no recomendado generalmente)

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro a analizar.

    Retorna
    -------
    tuple[str, str]
        (método_recomendado, justificación)
    """
    chars = _analyze_background_characteristics(spectrum)

    bg_slope = chars["background_slope"]
    peak_sharpness = chars["peak_sharpness"]

    # Lógica de recomendación basada en características
    if bg_slope < 0.15:
        # Fondo muy plano
        return "Linear", "Fondo casi plano detectado (cambio < 15%)"
    elif peak_sharpness > 1.5 and bg_slope > 0.3:
        # Picos agudos con cambio de paso marcado
        return "Shirley", "Cambio de paso detectado (recomendado por Engelhard et al.)"
    elif bg_slope > 0.2:
        # Cambio de paso intermedio a fuerte
        return "Shirley", "Cambio de fondo significativo detectado"
    else:
        # Por defecto, Shirley es lo más común según literatura
        return "Shirley", "Método por defecto (recomendado para >80% de casos)"


def _plot_spectrum_streamlit(
    spectrum_proc: XPSSpectrum, spectrum_raw: XPSSpectrum | None = None
) -> None:
    """Genera gráficas con estilo científico.

    Muestra una gráfica con los datos originales. Si existe un fondo calculado o
    ajuste de picos, muestra una segunda gráfica con el procesamiento.
    """

    # Configuración de estilo científico (tipo publicación)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "serif"],
            "axes.linewidth": 1.5,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 6,
            "ytick.major.size": 6,
            "xtick.minor.size": 3,
            "ytick.minor.size": 3,
            "xtick.minor.visible": True,
            "ytick.minor.visible": True,
            "xtick.top": True,
            "ytick.right": True,
            "axes.labelsize": 12,
            "axes.titlesize": 13,
            "legend.fontsize": 10,
            "legend.frameon": False,
        }
    )

    bg, bg_label = _get_background_data(spectrum_proc)
    has_fit = "fit_result" in spectrum_proc.metadata
    original_intensity = spectrum_proc.metadata.get("background_original_intensity")

    if original_intensity is None:
        if spectrum_raw is not None and len(spectrum_raw.intensity) == len(
            spectrum_proc.intensity
        ):
            original_intensity = spectrum_raw.intensity
        else:
            original_intensity = spectrum_proc.intensity

    # --- GRÁFICA 1: DATOS ORIGINALES ---
    fig_raw, ax_raw = plt.subplots(figsize=(10, 4))
    ax_raw.plot(
        spectrum_proc.binding_energy,
        original_intensity,
        color="black",
        linewidth=1.2,
        label="Original Data",
    )

    # Si hay fondo pero no fit, podemos mostrar el fondo en la primera gráfica
    # para compararlo con el raw
    if bg is not None and not has_fit:
        ax_raw.plot(
            spectrum_proc.binding_energy,
            bg,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=bg_label,
        )
        ax_raw.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)

    ax_raw.invert_xaxis()
    ax_raw.set_xlabel("Binding Energy (eV)")
    ax_raw.set_ylabel("Intensity (a.u.)")
    ax_raw.set_title(f"Survey/Region: {spectrum_proc.region_name}")
    fig_raw.tight_layout()

    st.pyplot(fig_raw, clear_figure=True)

    # --- GRÁFICA 2: PROCESAMIENTO (Solo si hay fondo o ajuste) ---
    if bg is not None or has_fit:
        st.markdown("---")
        st.subheader("Análisis de Fondo y Ajuste de Picos")

        fig_proc, ax_proc = plt.subplots(figsize=(10, 4))

        # 1. Mostrar señal base (fondo sustraído si existe)
        if bg is not None:
            # Mostrar espectro con fondo sustraído
            ax_proc.plot(
                spectrum_proc.binding_energy,
                spectrum_proc.intensity,
                label="Signal (BG Subtracted)",
                color="blue",
                linewidth=1.2,
            )
            # Rellenar área bajo la señal
            ax_proc.fill_between(
                spectrum_proc.binding_energy,
                spectrum_proc.intensity,
                alpha=0.1,
                color="blue",
            )
        else:
            # Si solo hay ajuste pero no fondo calculado (raro pero posible)
            ax_proc.plot(
                spectrum_proc.binding_energy,
                spectrum_proc.intensity,
                color="black",
                linewidth=1.2,
                label="Experimental Data",
            )

        # 2. Plot fitted peaks if they exist
        if has_fit:
            fit: FitResult = spectrum_proc.metadata["fit_result"]

            # Plot individual peaks
            from xps_analyzer.analysis.peak_fitting import (
                _gaussian,
                _lorentzian,
                _voigt,
            )

            colors = plt.cm.tab10(np.linspace(0, 1, 10))
            for i, peak in enumerate(fit.peaks):
                if peak.shape == "gaussian":
                    y_peak = _gaussian(
                        spectrum_proc.binding_energy,
                        peak.amplitude,
                        peak.position,
                        peak.width,
                    )
                elif peak.shape == "lorentzian":
                    y_peak = _lorentzian(
                        spectrum_proc.binding_energy,
                        peak.amplitude,
                        peak.position,
                        peak.width,
                    )
                elif peak.shape == "voigt":
                    y_peak = _voigt(
                        spectrum_proc.binding_energy,
                        peak.amplitude,
                        peak.position,
                        peak.width,
                        peak.gamma if peak.gamma else 0.5,
                    )
                else:
                    continue

                ax_proc.plot(
                    spectrum_proc.binding_energy,
                    y_peak,
                    color=colors[i % 10],
                    linewidth=1.0,
                    linestyle="-",
                )
                ax_proc.fill_between(
                    spectrum_proc.binding_energy,
                    0,
                    y_peak,
                    alpha=0.3,
                    color=colors[i % 10],
                    label=f"Peak {i + 1} ({peak.position:.1f} eV)",
                )

            # Plot envelope (Total Fit)
            ax_proc.plot(
                spectrum_proc.binding_energy,
                fit.fitted_spectrum,
                label=f"Total Fit (R²={fit.r_squared:.3f})",
                color="red",
                linewidth=2.0,
                linestyle="-",
                zorder=10,
            )

        ax_proc.invert_xaxis()
        ax_proc.set_xlabel("Binding Energy (eV)")
        ax_proc.set_ylabel("Intensity (a.u.)")
        ax_proc.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
        fig_proc.tight_layout()

        st.pyplot(fig_proc, clear_figure=True)


def main() -> None:
    """Punto de entrada principal de la GUI XPS Analyzer.

    Esta versión inicial permite:

    - Subir un archivo XPS en formato de texto soportado.
    - Ver metadatos básicos de la medición.
    - Seleccionar una región espectral y visualizar su espectro.
    """

    st.set_page_config(
        page_title="XPS Analyzer",
        page_icon="📈",
        layout="wide",
    )

    st.title("XPS Analyzer - GUI interactiva (beta)")
    st.markdown(
        """
        Esta es una primera versión de la interfaz gráfica para XPS Analyzer.

        1. Sube un archivo XPS en formato de texto soportado.
        2. Selecciona la región espectral de interés.
        3. Visualiza el espectro con la convención XPS (alta energía a la izquierda).
        """
    )

    uploaded = st.file_uploader(
        "Selecciona un archivo XPS (texto)",
        type=["txt"],
    )

    if uploaded is None:
        st.info("Sube un archivo para comenzar el análisis.")
        # Limpiar el estado de sesión si no hay archivo
        for key in ["file_name", "raw_dataset", "processed_dataset", "selected_region"]:
            if key in st.session_state:
                del st.session_state[key]
        return

    try:
        # Cargar datos por primera vez o si el archivo cambia
        if (
            "file_name" not in st.session_state
            or st.session_state.file_name != uploaded.name
        ):
            raw = _load_dataset_from_bytes(uploaded.getvalue(), uploaded.name)
            if not isinstance(raw, XPSDataset):
                st.error("El objeto cargado no es un XPSDataset válido.")
                return
            st.session_state.raw_dataset = raw
            st.session_state.processed_dataset = raw.copy()
            st.session_state.file_name = uploaded.name
            st.session_state.selected_region = (
                list(raw.spectra.keys())[0] if raw.spectra else None
            )

        dataset_proc = st.session_state.processed_dataset
    except Exception as exc:  # noqa: BLE001
        st.error(
            "Error al cargar el archivo XPS. "
            "Verifica que el formato sea compatible con el cargador actual."
        )
        st.exception(exc)
        return

    st.success(f"Archivo cargado: {dataset_proc.filename}")

    # === BARRA LATERAL: HERRAMIENTAS DE ANÁLISIS ===
    st.sidebar.header("Herramientas de Análisis")

    # -- 1. CALIBRACIÓN --
    with st.sidebar.expander("Calibración de Energía", expanded=False):
        ref_db = load_reference_database()
        elements = sorted(ref_db.elements.keys())
        default_index = elements.index("C") if "C" in elements else 0

        selected_element_symbol = st.selectbox(
            "Elemento de referencia", elements, index=default_index
        )
        selected_element = ref_db.elements[selected_element_symbol]

        if st.button("Calibrar Todo"):
            try:
                calibrate_sample(dataset_proc, selected_element, inplace=True)
                st.sidebar.success(
                    f"Calibrado a {selected_element_symbol} exitosamente."
                )
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error al calibrar: {e}")

        if st.button("Reiniciar Calibración"):
            # Restaurar desde el dataset crudo
            st.session_state.processed_dataset = st.session_state.raw_dataset.copy()
            st.sidebar.info("Calibración y fondos reiniciados.")
            st.rerun()

    # -- 1.5 DELIMITAR RANGO ESPECTRAL --
    with st.sidebar.expander("Delimitar Rango Espectral", expanded=False):
        st.write("Recorta el espectro actual a un rango de energía específico.")

        if st.session_state.get("selected_region"):
            reg = st.session_state.selected_region
            spectrum = dataset_proc.get_spectrum(reg)

            # Usar SIEMPRE el rango del espectro original para acotar inputs
            raw_spectrum = st.session_state.raw_dataset.get_spectrum(reg)
            raw_min_be = float(np.min(raw_spectrum.binding_energy))
            raw_max_be = float(np.max(raw_spectrum.binding_energy))
            rango_min = min(raw_min_be, raw_max_be)
            rango_max = max(raw_min_be, raw_max_be)

            # Mostrar por defecto el rango actual del espectro procesado
            cur_min_be = float(np.min(spectrum.binding_energy))
            cur_max_be = float(np.max(spectrum.binding_energy))
            default_min = float(
                np.clip(min(cur_min_be, cur_max_be), rango_min, rango_max)
            )
            default_max = float(
                np.clip(max(cur_min_be, cur_max_be), rango_min, rango_max)
            )

            slice_min_input = st.number_input(
                "Energía Mínima (eV)",
                min_value=rango_min,
                max_value=rango_max,
                value=default_min,
                format="%.2f",
            )
            slice_max_input = st.number_input(
                "Energía Máxima (eV)",
                min_value=rango_min,
                max_value=rango_max,
                value=default_max,
                format="%.2f",
            )

            # Clamps defensivos para asegurar límites del espectro original
            slice_min = float(np.clip(slice_min_input, rango_min, rango_max))
            slice_max = float(np.clip(slice_max_input, rango_min, rango_max))

            if (slice_min != slice_min_input) or (slice_max != slice_max_input):
                st.info(
                    "Los límites se ajustaron automáticamente al rango original "
                    f"[{rango_min:.2f}, {rango_max:.2f}] eV."
                )

            rango_valido = slice_min < slice_max
            if not rango_valido:
                st.warning(
                    "La Energía Mínima debe ser menor que la Energía Máxima "
                    "para aplicar el recorte."
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Aplicar Recorte", disabled=not rango_valido):
                    try:
                        _slice_spectrum_inplace(spectrum, slice_min, slice_max)
                        st.sidebar.success(f"Espectro {reg} recortado.")
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"Error al recortar: {e}")
            with col2:
                if st.button("Restaurar Rango"):
                    try:
                        # Restaurar solo esta región desde raw_dataset
                        raw_spectrum = st.session_state.raw_dataset.get_spectrum(reg)
                        dataset_proc.spectra[reg] = raw_spectrum.copy()
                        st.sidebar.info(f"Rango de {reg} restaurado.")
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"Error al restaurar: {e}")
        else:
            st.info("Selecciona una región primero.")

    # -- 2. SUSTRACCIÓN DE FONDO --
    with st.sidebar.expander("Sustracción de Fondo", expanded=False):
        bg_method = st.selectbox("Método", ["Shirley", "Tougaard", "Lineal"])

        shirley_tol = 1e-5
        shirley_max_iter = 100
        tougaard_b = 2866.0
        tougaard_c = 1643.0
        tougaard_d = 1.0

        if bg_method == "Shirley":
            shirley_tol = st.number_input("Tolerancia", value=1e-5, format="%e")
            shirley_max_iter = st.number_input("Máx. Iteraciones", value=100, step=10)
        elif bg_method == "Tougaard":
            tougaard_b = st.number_input("B", value=2866.0)
            tougaard_c = st.number_input("C", value=1643.0)
            tougaard_d = st.number_input("D", value=1.0)

        bg_scope = st.radio("Aplicar a", ["Región seleccionada", "Todo el dataset"])

        if st.button("Sustraer Fondo"):
            try:
                if bg_scope == "Región seleccionada":
                    spectra_to_process = (
                        [st.session_state.selected_region]
                        if st.session_state.selected_region
                        else []
                    )
                else:
                    spectra_to_process = list(dataset_proc.spectra.keys())

                for reg in spectra_to_process:
                    spectrum = dataset_proc.get_spectrum(reg)
                    _prepare_spectrum_for_background_subtraction(spectrum)
                    if bg_method == "Shirley":
                        shirley_background(
                            spectrum,
                            tol=shirley_tol,
                            max_iter=shirley_max_iter,
                            inplace=True,
                        )
                        spectrum.metadata["background_method"] = "shirley"
                    elif bg_method == "Tougaard":
                        tougaard_background(
                            spectrum,
                            B=tougaard_b,
                            C=tougaard_c,
                            D=tougaard_d,
                            inplace=True,
                        )
                        spectrum.metadata["background_method"] = "tougaard"
                    elif bg_method == "Lineal":
                        linear_background(spectrum, inplace=True)
                        spectrum.metadata["background_method"] = "lineal"

                st.sidebar.success(f"Fondo {bg_method} sustraído.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error al sustraer fondo: {e}")

    # -- 3. AJUSTE DE PICOS --
    with st.sidebar.expander("Ajuste de Picos (Peak Fitting)", expanded=False):
        st.write("Configura el ajuste para la región actualmente seleccionada.")

        if st.session_state.get("selected_region"):
            pf_shape = st.selectbox(
                "Perfil de pico", ["gaussian", "lorentzian", "voigt"], index=0
            )

            pf_auto = st.checkbox("Estimar posiciones automáticamente", value=True)

            pf_n_peaks = st.number_input(
                "Número de picos", min_value=1, max_value=10, value=1, step=1
            )

            pf_positions = []
            if not pf_auto:
                st.write("Posiciones iniciales (eV):")
                for i in range(pf_n_peaks):
                    pos = st.number_input(f"Posición Pico {i + 1}", value=0.0, step=0.1)
                    pf_positions.append(pos)

            if st.button("Ajustar Picos"):
                try:
                    reg = st.session_state.selected_region
                    spectrum = dataset_proc.get_spectrum(reg)

                    # Llamar a la función de ajuste
                    if pf_auto:
                        fit_res = fit_multiple_peaks(
                            spectrum,
                            n_peaks=pf_n_peaks,
                            shape=pf_shape,
                            auto_estimate=True,
                        )
                    else:
                        fit_res = fit_multiple_peaks(
                            spectrum,
                            peak_positions=pf_positions,
                            shape=pf_shape,
                            auto_estimate=False,
                        )

                    # Guardar el resultado en la metadata
                    spectrum.metadata["fit_result"] = fit_res

                    if fit_res.success:
                        st.sidebar.success(
                            f"Ajuste convergido (R²={fit_res.r_squared:.3f})"
                        )
                    else:
                        st.sidebar.warning(
                            f"Ajuste completado pero no óptimo: {fit_res.message}"
                        )

                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error en ajuste: {e}")

            if st.button("Limpiar Ajuste"):
                reg = st.session_state.selected_region
                spectrum = dataset_proc.get_spectrum(reg)
                if "fit_result" in spectrum.metadata:
                    del spectrum.metadata["fit_result"]
                    st.sidebar.info("Ajuste removido.")
                    st.rerun()

    # -- 4. CUANTIFICACIÓN --
    with st.sidebar.expander("Cuantificación (Atomic %)", expanded=False):
        st.write("Calcula concentración atómica usando picos ajustados o área cruda.")

        quant_regions = st.multiselect(
            "Regiones a incluir",
            list(dataset_proc.spectra.keys()),
            default=list(dataset_proc.spectra.keys()),
        )

        rsf_source = st.selectbox("Fuente RSF", ["Scofield", "Wagner"])

        if quant_regions:
            st.write("Mapeo de elementos (ej. 'C 1s'):")
            region_map = {}
            for r in quant_regions:
                default_elem = _extract_element_from_region_name(r) or ""
                region_map[r] = st.text_input(f"Elemento para {r}", value=default_elem)

            if st.button("Calcular % Atómico"):
                try:
                    rsf_dict = load_sensitivity_factors(
                        source=rsf_source.lower(),
                        xray_source="al_ka",
                        enable_fallback=True,
                    )

                    peaks = []
                    valid_elements = []

                    for r in quant_regions:
                        elem = region_map[r].strip()
                        if not elem:
                            continue

                        spectrum = dataset_proc.get_spectrum(r)

                        if "fit_result" in spectrum.metadata:
                            fit = spectrum.metadata["fit_result"]
                            total_area = sum(p.area for p in fit.peaks)
                        else:
                            # Integración cruda si no hay ajuste
                            # (Asume que el usuario ya restó el fondo)
                            total_area = abs(
                                np.trapezoid(
                                    spectrum.intensity, spectrum.binding_energy
                                )
                            )

                        # Dummy PeakParameter solo para pasar el área
                        dummy_peak = PeakParameters(
                            position=0.0,
                            amplitude=0.0,
                            width=0.0,
                            area=total_area,
                            shape="gaussian",
                        )
                        peaks.append(dummy_peak)
                        valid_elements.append(elem)

                    if peaks:
                        conc = calculate_atomic_concentration(
                            peaks, rsf_dict, valid_elements, try_fallback=True
                        )
                        st.session_state.quant_results = conc
                        st.sidebar.success("Cuantificación exitosa!")
                        st.rerun()
                    else:
                        st.sidebar.warning("No hay regiones válidas para cuantificar.")
                except Exception as e:
                    st.sidebar.error(f"Error en cuantificación: {e}")

    # Mostrar resultados de cuantificación si existen
    if "quant_results" in st.session_state:
        st.subheader("Resultados de Cuantificación")
        conc = st.session_state.quant_results

        # Format as table
        import pandas as pd

        df = pd.DataFrame(
            {
                "Elemento/Orbital": list(conc.keys()),
                "% Atómico": [f"{v:.2f}" for v in conc.values()],
            }
        )
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Mostrar metadatos globales en un expansor
    with st.expander("Metadatos del archivo", expanded=False):
        if dataset_proc.header:
            st.json(dataset_proc.header)
        else:
            st.write("No hay metadatos disponibles en el header.")

    # Selección de región espectral
    region_names = sorted(dataset_proc.spectra.keys())
    if not region_names:
        st.warning("El dataset no contiene espectros para visualizar.")
        return

    # Usar session_state para mantener la selección
    selected_region = st.selectbox(
        "Selecciona región espectral",
        region_names,
        index=region_names.index(st.session_state.selected_region)
        if st.session_state.selected_region in region_names
        else 0,
    )
    st.session_state.selected_region = selected_region

    spectrum_proc = dataset_proc.get_spectrum(selected_region)
    spectrum_raw = st.session_state.raw_dataset.get_spectrum(selected_region)

    if spectrum_proc is None:
        st.error("No se encontró el espectro seleccionado en el dataset.")
        return

    # Layout de dos columnas: gráfica + metadata local
    col_plot, col_meta = st.columns([3, 1])

    with col_plot:
        st.subheader(f"Espectro: {spectrum_proc.region_name}")
        _plot_spectrum_streamlit(spectrum_proc, spectrum_raw)

    with col_meta:
        st.subheader("Metadata del espectro")
        if spectrum_proc.metadata:
            st.json(spectrum_proc.metadata)
        else:
            st.write("No hay metadata específica para este espectro.")


if __name__ == "__main__":  # pragma: no cover - entrada manual
    main()
