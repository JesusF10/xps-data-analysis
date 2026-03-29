"""
Pipeline de análisis batch para el dataset completo BN-SET-01.

Este script procesa las 4 muestras del dataset (BN-BS-1 a BN-BS-4) usando
el pipeline completo de análisis XPS desarrollado en Fase B. Genera:
- Resultados individuales por muestra (JSON + plots)
- Resumen consolidado con tabla comparativa de composiciones
- Evaluación de reproducibilidad entre muestras

Uso:
    uv run python scripts/analyze_bn_batch.py \\
        --input-dir "data/raw/BN-SET-01" \\
        --output-dir "data/results/BN-SET-01"

Autor: Jesús Flores Lacarra
Fecha: Marzo 2026
Versión: XPS Analyzer 0.8.0-beta
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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

SAMPLES = ["BN-BS-1", "BN-BS-2", "BN-BS-3", "BN-BS-4"]


def calibrate_dataset(dataset: XPSDataset, reference_energy: float = 284.8) -> float:
    """
    Calibra dataset usando C 1s como referencia.

    Parámetros
    ----------
    dataset : XPSDataset
        Dataset a calibrar (será modificado in-place).
    reference_energy : float
        Energía de referencia para C 1s (default 284.8 eV).

    Retorna
    -------
    float
        Shift aplicado en eV.
    """
    c1s_spectrum = None
    for region_name in dataset.list_regions():
        if "C" in region_name and "1s" in region_name:
            c1s_spectrum = dataset.get_spectrum(region_name)
            break

    if c1s_spectrum is None:
        raise ValueError("No se encontró región C 1s para calibración")

    max_idx = np.argmax(c1s_spectrum.intensity)
    observed_energy = c1s_spectrum.binding_energy[max_idx]
    shift = reference_energy - observed_energy

    for region_name in dataset.list_regions():
        spectrum = dataset.get_spectrum(region_name)
        spectrum.binding_energy += shift

    return shift


def detect_peaks_hybrid(
    spectrum: XPSSpectrum, region_name: str, prominence: float = 100
) -> tuple[np.ndarray, np.ndarray]:
    """Detecta picos usando método híbrido."""
    peaks_idx, _ = find_peaks(
        spectrum.intensity,
        prominence=prominence,
        distance=10,
    )

    if len(peaks_idx) == 0:
        return np.array([]), np.array([])

    peaks_energy = spectrum.binding_energy[peaks_idx]
    peaks_intensity = spectrum.intensity[peaks_idx]

    return peaks_energy, peaks_intensity


def analyze_spectrum(
    spectrum: XPSSpectrum, region_name: str
) -> tuple[FitResult | None, XPSSpectrum, np.ndarray]:
    """Analiza un espectro: fondo + fitting."""
    # 1. Restar fondo Shirley
    try:
        spectrum_nobg = shirley_background(spectrum, max_iter=100)
        background = spectrum.intensity - spectrum_nobg.intensity
    except Exception:
        return None, spectrum, np.zeros_like(spectrum.intensity)

    # 2. Detectar picos
    peaks_energy, peaks_intensity = detect_peaks_hybrid(
        spectrum_nobg, region_name, prominence=np.std(spectrum_nobg.intensity) * 2
    )

    if len(peaks_energy) == 0:
        return None, spectrum_nobg, background

    # 3. Ajustar pico principal
    main_peak_idx = np.argmax(peaks_intensity)
    main_peak_energy = peaks_energy[main_peak_idx]

    try:
        fit_result = fit_voigt(
            spectrum_nobg,
            initial_position=main_peak_energy,
            initial_amplitude=peaks_intensity[main_peak_idx],
            initial_sigma=1.0,
            initial_gamma=0.5,
        )
    except Exception:
        return None, spectrum_nobg, background

    return fit_result, spectrum_nobg, background


def plot_analysis_results(
    sample_name: str,
    spectrum: XPSSpectrum,
    spectrum_nobg: XPSSpectrum,
    background: np.ndarray,
    fit_result: FitResult | None,
    output_path: Path,
):
    """Crea plot de análisis completo."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # Panel superior: datos + fondo + ajuste
    ax1 = axes[0]
    ax1.plot(
        spectrum.binding_energy,
        spectrum.intensity,
        "o-",
        markersize=2,
        label="Datos raw",
        alpha=0.7,
    )
    ax1.plot(spectrum.binding_energy, background, "--", label="Fondo Shirley", lw=2)

    if fit_result and fit_result.success:
        ax1.plot(
            spectrum_nobg.binding_energy,
            fit_result.fitted_spectrum,
            "-",
            label=f"Ajuste Voigt (R²={fit_result.r_squared:.3f})",
            lw=2,
        )

    ax1.set_xlabel("Binding Energy (eV)")
    ax1.set_ylabel("Intensity (a.u.)")
    ax1.set_title(f"{sample_name} - {spectrum.region_name}")
    ax1.legend()
    ax1.invert_xaxis()
    ax1.grid(alpha=0.3)

    # Panel inferior: residuos
    ax2 = axes[1]
    if fit_result and fit_result.success:
        residuals = spectrum_nobg.intensity - fit_result.fitted_spectrum
        ax2.plot(spectrum_nobg.binding_energy, residuals, "o-", markersize=2)
        ax2.axhline(0, color="red", linestyle="--", lw=1)
        ax2.set_xlabel("Binding Energy (eV)")
        ax2.set_ylabel("Residuos")
        ax2.invert_xaxis()
        ax2.grid(alpha=0.3)
    else:
        ax2.text(
            0.5,
            0.5,
            "Fitting no exitoso",
            ha="center",
            va="center",
            transform=ax2.transAxes,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_composition_bar(
    sample_name: str, composition: dict[str, float], output_path: Path
):
    """Crea gráfico de barras de composición."""
    fig, ax = plt.subplots(figsize=(8, 6))

    elements = list(composition.keys())
    percentages = list(composition.values())

    bars = ax.bar(elements, percentages, color="steelblue", alpha=0.8)

    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{pct:.1f}%",
            ha="center",
            va="bottom",
        )

    ax.set_xlabel("Elemento")
    ax.set_ylabel("Concentración Atómica (%)")
    ax.set_title(f"{sample_name} - Composición Atómica")
    ax.set_ylim(0, max(percentages) * 1.15)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def analyze_single_sample(
    sample_name: str, input_dir: Path, output_dir: Path
) -> dict[str, Any]:
    """
    Analiza una muestra individual.

    Retorna
    -------
    dict
        Resultados completos del análisis.
    """
    print(f"\n{'=' * 70}")
    print(f"📊 ANALIZANDO: {sample_name}")
    print(f"{'=' * 70}")

    # Buscar archivos multiplex y survey (case-insensitive, solo .txt)
    sample_dir = input_dir / sample_name
    multiplex_files = [
        f
        for f in sample_dir.glob("*[Mm][Uu][Ll][Tt][Ii]*")
        if f.suffix.lower() == ".txt"
    ]
    survey_files = [
        f
        for f in sample_dir.glob("*[Ss][Uu][Rr][Vv][Ee][Yy]*")
        if f.suffix.lower() == ".txt"
    ]

    if not multiplex_files:
        print(f"  ❌ No se encontró archivo MULTIPLEX en {sample_dir}")
        return {}
    if not survey_files:
        print(f"  ❌ No se encontró archivo SURVEY en {sample_dir}")
        return {}

    input_path = multiplex_files[0]
    survey_path = survey_files[0]

    # Crear directorio de salida
    sample_output_dir = output_dir / sample_name
    sample_output_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = sample_output_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    # 1. Cargar
    print("\n1️⃣  Cargando datos...")
    try:
        dataset = load_single_file(input_path)
        print(
            f"  ✓ {len(dataset.list_regions())} regiones: {', '.join(dataset.list_regions())}"
        )
    except Exception as e:
        print(f"  ❌ Error al cargar: {e}")
        return {}

    # 2. Calibrar
    print("\n2️⃣  Calibrando energía...")
    try:
        shift = calibrate_dataset(dataset)
        print(f"  ✓ Shift aplicado: {shift:+.2f} eV")
    except Exception as e:
        print(f"  ❌ Error en calibración: {e}")
        return {}

    # 3. Analizar regiones
    print("\n3️⃣  Analizando regiones...")
    results = {
        "sample": sample_name,
        "calibration_shift_eV": float(shift),
        "regions": {},
        "composition": {},
    }

    peak_params_list = []
    element_names_list = []

    for region_name in dataset.list_regions():
        print(f"\n  📊 {region_name}")
        spectrum = dataset.get_spectrum(region_name)
        fit_result, spectrum_nobg, background = analyze_spectrum(spectrum, region_name)

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

            peak_params_list.append(peak_param)
            element_names_list.append(region_name)

            print(
                f"    ✓ Pico @ {peak_param.position:.2f} eV (R²={fit_result.r_squared:.3f})"
            )

        results["regions"][region_name] = region_results

        # Plot
        plot_path = (
            plots_dir / f"{sample_name}_{region_name.replace(' ', '_')}_analysis.png"
        )
        plot_analysis_results(
            sample_name, spectrum, spectrum_nobg, background, fit_result, plot_path
        )

    # 4. Cuantificar
    print("\n4️⃣  Cuantificando composición...")
    if len(peak_params_list) > 0:
        rsf = load_sensitivity_factors(source="scofield", xray_source="mg_ka")

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

        if len(valid_peaks) > 0:
            concentrations = calculate_atomic_concentration(
                valid_peaks, rsf, element_names=valid_names
            )
            concentrations_normalized = normalize_to_100(concentrations)

            results["composition"] = {
                "atomic_percent": {
                    k: float(v) for k, v in concentrations_normalized.items()
                },
            }

            print("\n  Composición atómica (%):")
            for element, percent in sorted(
                concentrations_normalized.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"    {element:12s}: {percent:6.2f}%")

            # Plot composición
            comp_plot_path = plots_dir / f"{sample_name}_composition.png"
            plot_composition_bar(sample_name, concentrations_normalized, comp_plot_path)

    # 5. Exportar
    print("\n5️⃣  Exportando...")
    results_path = sample_output_dir / "analysis_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Resultados: {results_path.name}")
    print(f"  ✓ Plots: {len(list(plots_dir.glob('*.png')))} archivos")

    return results


def generate_batch_summary(
    all_results: dict[str, dict], output_dir: Path
) -> dict[str, Any]:
    """
    Genera resumen consolidado del análisis batch.

    Parámetros
    ----------
    all_results : dict[str, dict]
        Diccionario {sample_name: results} con todos los resultados.
    output_dir : Path
        Directorio donde guardar el resumen.

    Retorna
    -------
    dict
        Resumen consolidado.
    """
    print(f"\n{'=' * 70}")
    print("📊 GENERANDO RESUMEN CONSOLIDADO")
    print(f"{'=' * 70}")

    summary = {
        "num_samples": len(all_results),
        "samples": list(all_results.keys()),
        "comparative_composition": {},
        "statistics": {},
    }

    # Recopilar composiciones
    compositions = {}
    for sample_name, results in all_results.items():
        if "composition" in results and "atomic_percent" in results["composition"]:
            compositions[sample_name] = results["composition"]["atomic_percent"]

    # Crear tabla comparativa
    all_elements = set()
    for comp in compositions.values():
        all_elements.update(comp.keys())

    summary["comparative_composition"] = {}
    for element in sorted(all_elements):
        summary["comparative_composition"][element] = {}
        values = []
        for sample_name in SAMPLES:
            if sample_name in compositions:
                value = compositions[sample_name].get(element, 0.0)
                summary["comparative_composition"][element][sample_name] = float(value)
                if value > 0:
                    values.append(value)

        # Calcular estadísticas
        if values:
            summary["comparative_composition"][element]["mean"] = float(np.mean(values))
            summary["comparative_composition"][element]["std"] = float(np.std(values))
            summary["comparative_composition"][element]["cv_percent"] = (
                float(np.std(values) / np.mean(values) * 100)
                if np.mean(values) > 0
                else 0.0
            )

    # Imprimir tabla comparativa
    print("\n📋 TABLA COMPARATIVA DE COMPOSICIONES")
    print("=" * 70)
    print(f"{'Elemento':<12} ", end="")
    for sample in SAMPLES:
        print(f"{sample:>12} ", end="")
    print(f"{'Media':>12} {'StdDev':>12} {'CV(%)':>12}")
    print("-" * 70)

    for element in sorted(all_elements):
        print(f"{element:<12} ", end="")
        for sample in SAMPLES:
            value = summary["comparative_composition"][element].get(sample, 0.0)
            if value > 0:
                print(f"{value:>11.2f}% ", end="")
            else:
                print(f"{'N/A':>12} ", end="")

        mean = summary["comparative_composition"][element].get("mean", 0.0)
        std = summary["comparative_composition"][element].get("std", 0.0)
        cv = summary["comparative_composition"][element].get("cv_percent", 0.0)

        if mean > 0:
            print(f"{mean:>11.2f}% {std:>11.2f}% {cv:>11.1f}%")
        else:
            print(f"{'N/A':>12} {'N/A':>12} {'N/A':>12}")

    # Guardar resumen
    summary_path = output_dir / "batch_analysis_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Resumen guardado: {summary_path}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Análisis batch del dataset BN-SET-01 (4 muestras)"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/raw/BN-SET-01"),
        help="Directorio con las 4 muestras",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/results/BN-SET-01"),
        help="Directorio de salida para resultados",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not input_dir.exists():
        print(f"❌ Error: Directorio de entrada no existe: {input_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("🚀 FASE C: BATCH PROCESSING - XPS Analyzer v0.8.0-beta")
    print("=" * 70)
    print(f"\nInput:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"\nMuestras a procesar: {', '.join(SAMPLES)}")

    # Procesar todas las muestras
    all_results = {}
    for sample_name in SAMPLES:
        results = analyze_single_sample(sample_name, input_dir, output_dir)
        if results:
            all_results[sample_name] = results

    # Generar resumen consolidado
    if all_results:
        generate_batch_summary(all_results, output_dir)

    print("\n" + "=" * 70)
    print("✅ FASE C COMPLETADA")
    print("=" * 70)
    print(f"\nMuestras procesadas exitosamente: {len(all_results)}/{len(SAMPLES)}")
    print(f"Resultados en: {output_dir}")


if __name__ == "__main__":
    main()
