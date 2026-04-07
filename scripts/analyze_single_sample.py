"""
Pipeline completo de análisis XPS para una muestra individual.

Este script ejecuta el pipeline completo de análisis XPS:
1. Carga de datos (multiplex + survey)
2. Calibración de energía (C 1s @ 284.8 eV)
3. Sustracción de fondo (Shirley)
4. Detección y ajuste de picos (Voigt fitting)
5. Cuantificación atómica (RSF Scofield para Mg Kα)
6. Exportación de resultados (JSON + plots PNG)

Uso:
    uv run python scripts/analyze_single_sample.py \\
        --input "data/raw/BN-SET-01/BN-BS-3/BN-BS-3 MULTIPLEX.txt" \\
        --survey "data/raw/BN-SET-01/BN-BS-3/BN-BS-3 SURVEY.txt" \\
        --output "data/results/BN-SET-01/BN-BS-3"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from xps_analyzer import load_single_file
from xps_analyzer.analysis.background import shirley_background
from xps_analyzer.analysis.peak_fitting import FitResult, fit_voigt
from xps_analyzer.analysis.quantification import (
    calculate_atomic_concentration,
    load_sensitivity_factors,
    normalize_to_100,
)
from xps_analyzer.data_loader import XPSDataset, XPSSpectrum

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

# Posiciones esperadas de picos (literatura para Mg Kα)
EXPECTED_PEAKS = {
    "Ti 2p": 458.8,  # Ti 2p3/2 en TiO2
    "O 1s": 530.0,  # O en óxidos metálicos
    "C 1s": 284.8,  # C adventicio
    "Bi 4f": 159.0,  # Bi 4f7/2 metálico
    "Na 1s": 1071.0,  # Na 1s
    "Sr 3d": 133.0,  # Sr 3d5/2
}


def calibrate_dataset(dataset: XPSDataset, reference_energy: float = 284.8) -> float:
    """
    Calibra dataset usando C 1s como referencia.

    Parámetros
    ----------
    dataset : XPSDataset
        Dataset a calibrar (será modificado in-place).
    reference_energy : float
        Energía de referencia para C 1s (default 284.8 eV - carbono adventicio).

    Retorna
    -------
    float
        Shift aplicado en eV.

    Raises
    ------
    ValueError
        Si no se encuentra región C 1s.
    """
    # Encontrar espectro de C 1s
    c1s_spectrum = None
    for region_name in dataset.list_regions():
        if "C" in region_name and "1s" in region_name:
            c1s_spectrum = dataset.get_spectrum(region_name)
            break

    if c1s_spectrum is None:
        raise ValueError("No se encontró región C 1s para calibración")

    # Encontrar máximo (pico de C adventicio)
    max_idx = np.argmax(c1s_spectrum.intensity)
    observed_energy = c1s_spectrum.binding_energy[max_idx]

    # Calcular shift
    shift = reference_energy - observed_energy

    print(f"  Calibración: C 1s observado @ {observed_energy:.2f} eV")
    print(f"  Shift aplicado: {shift:+.2f} eV")

    # Aplicar shift a todas las regiones
    for region_name in dataset.list_regions():
        spectrum = dataset.get_spectrum(region_name)
        spectrum.binding_energy += shift

    return shift


def detect_peaks_hybrid(
    spectrum: XPSSpectrum, region_name: str, prominence: float = 100
) -> tuple[np.ndarray, np.ndarray]:
    """
    Detecta picos usando método híbrido (auto-detect + validación).

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro donde detectar picos.
    region_name : str
        Nombre de la región (para validación con literatura).
    prominence : float
        Prominencia mínima para detección de picos.

    Retorna
    -------
    tuple[np.ndarray, np.ndarray]
        (energías de picos, intensidades de picos)
    """
    # Detectar picos
    peaks_idx, properties = find_peaks(
        spectrum.intensity,
        prominence=prominence,
        distance=10,  # Mínimo 10 puntos entre picos
    )

    if len(peaks_idx) == 0:
        return np.array([]), np.array([])

    peaks_energy = spectrum.binding_energy[peaks_idx]
    peaks_intensity = spectrum.intensity[peaks_idx]

    # Validar contra literatura si disponible
    expected = EXPECTED_PEAKS.get(region_name)
    if expected and len(peaks_energy) > 0:
        closest_idx = np.argmin(np.abs(peaks_energy - expected))
        closest_energy = peaks_energy[closest_idx]
        diff = abs(closest_energy - expected)

        if diff > 3.0:  # Tolerancia 3 eV
            print(
                f"  ⚠️  Pico en {region_name} detectado @ {closest_energy:.1f} eV, "
                f"esperado ~{expected:.1f} eV (diff: {diff:.1f} eV)"
            )
        else:
            print(
                f"  ✓ Pico en {region_name} @ {closest_energy:.1f} eV "
                f"(esperado ~{expected:.1f} eV)"
            )

    return peaks_energy, peaks_intensity


def analyze_spectrum(
    spectrum: XPSSpectrum, region_name: str
) -> tuple[FitResult | None, XPSSpectrum, np.ndarray]:
    """
    Analiza un espectro individual: fondo + fitting.

    Parámetros
    ----------
    spectrum : XPSSpectrum
        Espectro a analizar.
    region_name : str
        Nombre de la región.

    Retorna
    -------
    tuple[FitResult | None, XPSSpectrum, np.ndarray]
        (resultado de fitting, espectro sin fondo, array de fondo)
    """
    # 1. Restar fondo Shirley
    try:
        spectrum_nobg = shirley_background(spectrum, max_iter=100)
        background = spectrum.intensity - spectrum_nobg.intensity
    except Exception as e:
        print(f"  ❌ Error en sustracción de fondo: {e}")
        return None, spectrum, np.zeros_like(spectrum.intensity)

    # 2. Detectar picos
    peaks_energy, peaks_intensity = detect_peaks_hybrid(
        spectrum_nobg, region_name, prominence=np.std(spectrum_nobg.intensity) * 2
    )

    if len(peaks_energy) == 0:
        print(f"  ⚠️  No se detectaron picos en {region_name}")
        return None, spectrum_nobg, background

    # 3. Ajustar picos (simplificado: solo el pico más intenso por región)
    main_peak_idx = np.argmax(peaks_intensity)
    main_peak_energy = peaks_energy[main_peak_idx]

    # Parámetros iniciales para Voigt
    try:
        fit_result = fit_voigt(
            spectrum_nobg,
            initial_position=main_peak_energy,
            initial_amplitude=peaks_intensity[main_peak_idx],
            initial_sigma=1.0,
            initial_gamma=0.5,
        )

        if fit_result.success:
            print(f"  ✓ Fitting exitoso: R²={fit_result.r_squared:.4f}")
        else:
            print(f"  ⚠️  Fitting no convergió: {fit_result.message}")
            return None, spectrum_nobg, background
    except Exception as e:
        print(f"  ❌ Error en fitting: {e}")
        return None, spectrum_nobg, background

    return fit_result, spectrum_nobg, background


def plot_analysis_results(
    sample_name: str,
    spectrum_raw: XPSSpectrum,
    spectrum_nobg: XPSSpectrum,
    background: np.ndarray,
    fit_result: FitResult | None,
    output_path: Path,
) -> None:
    """
    Genera plot con análisis completo.

    Parámetros
    ----------
    sample_name : str
        Nombre de la muestra.
    spectrum_raw : XPSSpectrum
        Espectro original.
    spectrum_nobg : XPSSpectrum
        Espectro con fondo restado.
    background : np.ndarray
        Array del fondo calculado.
    fit_result : FitResult | None
        Resultado del fitting (puede ser None si falló).
    output_path : Path
        Path donde guardar el plot.
    """
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [3, 1]}
    )

    # Panel superior: datos + fondo + fit
    ax1.plot(
        spectrum_raw.binding_energy,
        spectrum_raw.intensity,
        "o",
        markersize=2,
        alpha=0.5,
        label="Datos originales",
        color="lightblue",
    )
    ax1.plot(
        spectrum_raw.binding_energy,
        background,
        "--",
        linewidth=2,
        label="Fondo (Shirley)",
        color="red",
    )
    ax1.plot(
        spectrum_nobg.binding_energy,
        spectrum_nobg.intensity,
        "o",
        markersize=3,
        alpha=0.7,
        label="Sin fondo",
        color="blue",
    )

    if fit_result and fit_result.success:
        ax1.plot(
            spectrum_nobg.binding_energy,
            fit_result.fitted_spectrum,
            "-",
            linewidth=2,
            label=f"Fit (Voigt, R²={fit_result.r_squared:.3f})",
            color="green",
        )

    ax1.set_ylabel("Intensity (a.u.)", fontsize=11)
    ax1.set_title(
        f"{sample_name} - {spectrum_raw.region_name}",
        fontsize=13,
        fontweight="bold",
    )
    ax1.invert_xaxis()
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Panel inferior: residuos
    if fit_result and fit_result.success:
        ax2.plot(
            spectrum_nobg.binding_energy,
            fit_result.residual,
            "o",
            markersize=2,
            color="gray",
            alpha=0.6,
        )
        ax2.axhline(0, color="black", linestyle="--", linewidth=1)
        ax2.set_ylabel("Residual", fontsize=10)
        ax2.set_xlabel("Binding Energy (eV)", fontsize=11)
        ax2.invert_xaxis()
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(
            0.5,
            0.5,
            "Fitting no exitoso",
            ha="center",
            va="center",
            transform=ax2.transAxes,
            fontsize=12,
            color="red",
        )
        ax2.set_xlabel("Binding Energy (eV)", fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_composition_bar(
    sample_name: str, composition: dict[str, float], output_path: Path
) -> None:
    """
    Genera gráfico de barras con composición atómica.

    Parámetros
    ----------
    sample_name : str
        Nombre de la muestra.
    composition : dict[str, float]
        Diccionario con composición {elemento: porcentaje}.
    output_path : Path
        Path donde guardar el plot.
    """
    if not composition:
        print("  ⚠️  No hay datos de composición para plotear")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    elements = list(composition.keys())
    percentages = list(composition.values())

    # Colores por elemento (simplificado)
    colors = plt.cm.Set3(np.linspace(0, 1, len(elements)))

    bars = ax.bar(elements, percentages, color=colors, edgecolor="black", linewidth=1.5)

    # Agregar valores sobre las barras
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{pct:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylabel("Atomic Concentration (%)", fontsize=12)
    ax.set_xlabel("Element", fontsize=12)
    ax.set_title(f"{sample_name} - Composición Atómica", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(percentages) * 1.15)  # 15% extra para labels
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    """Ejecuta pipeline completo de análisis."""
    parser = argparse.ArgumentParser(description="Analizar muestra XPS individual")
    parser.add_argument("--input", required=True, help="Archivo multiplex.txt")
    parser.add_argument("--survey", required=True, help="Archivo SURVEY.txt")
    parser.add_argument("--output", required=True, help="Directorio de salida")
    args = parser.parse_args()

    input_path = Path(args.input)
    survey_path = Path(args.survey)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Crear subdirectorio para plots
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    # Extraer nombre de muestra del path
    sample_name = input_path.parent.name

    print("=" * 70)
    print(f"ANÁLISIS DE MUESTRA: {sample_name}")
    print("=" * 70)

    # 1. Cargar datos
    print("\n1️⃣  Cargando datos...")
    try:
        dataset = load_single_file(input_path)
        dataset_survey = load_single_file(survey_path)
        print(
            f"  ✓ {len(dataset.list_regions())} regiones cargadas: {', '.join(dataset.list_regions())}"
        )
    except Exception as e:
        print(f"  ❌ Error al cargar datos: {e}")
        return

    # 2. Calibrar
    print("\n2️⃣  Calibrando energía...")
    try:
        shift = calibrate_dataset(dataset)
    except Exception as e:
        print(f"  ❌ Error en calibración: {e}")
        return

    # 3. Analizar cada región
    print("\n3️⃣  Analizando regiones...")
    results = {
        "sample": sample_name,
        "calibration_shift_eV": float(shift),
        "regions": {},
        "composition": {},
        "metadata": dataset.header,
    }

    peak_areas = {}
    peak_params_list = []
    element_names_list = []

    for region_name in dataset.list_regions():
        print(f"\n  📊 {region_name}")
        spectrum = dataset.get_spectrum(region_name)

        fit_result, spectrum_nobg, background = analyze_spectrum(spectrum, region_name)

        # Guardar resultados
        region_results = {
            "num_points": len(spectrum.binding_energy),
            "energy_range": [
                float(spectrum.binding_energy.min()),
                float(spectrum.binding_energy.max()),
            ],
            "fitting_success": fit_result is not None and fit_result.success,
        }

        if fit_result and fit_result.success:
            peak_param = fit_result.peaks[0]
            region_results["peak"] = {
                "position_eV": float(peak_param.position),
                "amplitude": float(peak_param.amplitude),
                "fwhm_eV": float(peak_param.width),
                "area": float(peak_param.area),
            }
            region_results["r_squared"] = float(fit_result.r_squared)
            region_results["chi_squared"] = float(fit_result.chi_squared)

            # Guardar área y parámetros para cuantificación
            peak_areas[region_name] = peak_param.area
            peak_params_list.append(peak_param)
            element_names_list.append(region_name)

        results["regions"][region_name] = region_results

        # Plot
        plot_path = (
            plots_dir / f"{sample_name}_{region_name.replace(' ', '_')}_analysis.png"
        )
        plot_analysis_results(
            sample_name, spectrum, spectrum_nobg, background, fit_result, plot_path
        )

    # 4. Cuantificar
    print("\n4️⃣  Cuantificando composición atómica...")
    if len(peak_params_list) > 0:
        rsf = load_sensitivity_factors(source="scofield", xray_source="mg_ka")

        # Filtrar solo elementos con RSF disponibles
        valid_peaks = []
        valid_names = []
        skipped = []

        for peak, name in zip(peak_params_list, element_names_list):
            if name in rsf:
                valid_peaks.append(peak)
                valid_names.append(name)
            else:
                skipped.append(name)

        if skipped:
            print(f"  ⚠️  RSF no disponible para: {', '.join(skipped)}")
            print(f"  ℹ️  Estos elementos se excluyen de la cuantificación")

        if len(valid_peaks) > 0:
            concentrations = calculate_atomic_concentration(
                valid_peaks, rsf, element_names=valid_names
            )
            concentrations_normalized = normalize_to_100(concentrations)

            results["composition"] = {
                "atomic_percent": {
                    k: float(v) for k, v in concentrations_normalized.items()
                },
                "raw_concentrations": {k: float(v) for k, v in concentrations.items()},
            }

            print("\n  Composición atómica (%):")
            for element, percent in sorted(
                concentrations_normalized.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"    {element:12s}: {percent:6.2f}%")

            # Plot de composición
            comp_plot_path = plots_dir / f"{sample_name}_composition.png"
            plot_composition_bar(sample_name, concentrations_normalized, comp_plot_path)
            print(f"  ✓ Plot de composición guardado: {comp_plot_path.name}")
        else:
            print("  ⚠️  No hay suficientes elementos con RSF para cuantificar")
    else:
        print("  ⚠️  No hay áreas de picos para cuantificar")

    # 5. Exportar
    print("\n5️⃣  Exportando resultados...")
    results_path = output_dir / "analysis_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Resultados: {results_path}")
    print(f"  ✓ Plots: {plots_dir} ({len(list(plots_dir.glob('*.png')))} archivos)")

    print("\n" + "=" * 70)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    main()
