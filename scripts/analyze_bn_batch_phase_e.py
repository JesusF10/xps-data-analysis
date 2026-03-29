"""
Pipeline de análisis batch MEJORADO para validación de Fase E.

Este script re-procesa el dataset BN-SET-01 usando las 3 mejoras implementadas
en Fase E: Mejoras de Robustez. Compara con resultados de Fase C/D.

MEJORAS IMPLEMENTADAS:
1. Cascada de fallbacks para sustracción de fondo (Shirley → Tougaard → Linear)
2. Ajuste de dobletes con constraints físicos (Ti 2p, Bi 4f, Sr 3d)
3. RSF extendidos con Bi/Sr y fallback automático

DIFERENCIAS vs analyze_bn_batch.py (Fase C):
- background_with_fallback() en lugar de shirley_background()
- fit_doublet() para regiones Ti 2p, Bi 4f, Sr 3d
- load_sensitivity_factors(enable_fallback=True) para Bi/Sr

Uso:
    uv run python scripts/analyze_bn_batch_phase_e.py \\
        --input-dir "data/raw/BN-SET-01" \\
        --output-dir "data/results/BN-SET-01/phase_e"

Autor: Jesús Flores Lacarra
Fecha: Marzo 2026
Versión: XPS Analyzer 0.8.0-beta (Fase E)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from xps_analyzer import load_single_file
from xps_analyzer.analysis.background import (
    background_with_fallback,
    shirley_background,
)
from xps_analyzer.analysis.peak_fitting import (
    FitResult,
    fit_doublet,
    fit_voigt,
)
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

# Dobletes conocidos con parámetros físicos
DOUBLET_REGIONS = {
    "Ti 2p": {"splitting": 5.7, "ratio": 2.0, "profile": "voigt"},
    "Bi 4f": {"splitting": 5.3, "ratio": 1.33, "profile": "voigt"},
    "Sr 3d": {"splitting": 1.8, "ratio": 1.5, "profile": "voigt"},
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
    """Detecta picos usando scipy.signal.find_peaks."""
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


def is_doublet_region(region_name: str) -> bool:
    """Verifica si una región es un doblete conocido."""
    for doublet_name in DOUBLET_REGIONS:
        if doublet_name in region_name:
            return True
    return False


def get_doublet_params(region_name: str) -> dict[str, Any] | None:
    """Obtiene parámetros físicos del doblete."""
    for doublet_name, params in DOUBLET_REGIONS.items():
        if doublet_name in region_name:
            return params
    return None


def analyze_spectrum_phase_e(
    spectrum: XPSSpectrum, region_name: str
) -> tuple[FitResult | None, XPSSpectrum, np.ndarray, dict[str, Any]]:
    """
    Analiza un espectro usando mejoras de Fase E.

    MEJORA #1: background_with_fallback (Shirley → Tougaard → Linear)
    MEJORA #2: fit_doublet para Ti 2p, Bi 4f, Sr 3d

    Retorna
    -------
    tuple
        (fit_result, spectrum_nobg, background, metadata)
    """
    metadata: dict[str, Any] = {
        "region": region_name,
        "background_method": None,
        "fitting_method": None,
        "is_doublet": False,
        "background_attempts": [],
        "errors": [],
    }

    # MEJORA #1: Cascada de fallbacks para sustracción de fondo
    try:
        spectrum_nobg = background_with_fallback(
            spectrum,
            shirley_max_iter=50,
            shirley_tol=1e-6,
            inplace=False,
        )
        background = spectrum.intensity - spectrum_nobg.intensity

        # Metadata almacenada directamente en spectrum_nobg.metadata
        metadata["background_method"] = spectrum_nobg.metadata.get(
            "background_method", "unknown"
        )
        metadata["background_attempts"] = spectrum_nobg.metadata.get(
            "background_fallback_attempted", []
        )
    except Exception as e:
        metadata["errors"].append(f"Background failed: {str(e)}")
        return None, spectrum, np.zeros_like(spectrum.intensity), metadata

    # 2. Detectar picos
    peaks_energy, peaks_intensity = detect_peaks_hybrid(
        spectrum_nobg, region_name, prominence=np.std(spectrum_nobg.intensity) * 2
    )

    if len(peaks_energy) == 0:
        metadata["errors"].append("No peaks detected")
        return None, spectrum_nobg, background, metadata

    # 3. Decidir método de fitting: doblete vs. single peak
    main_peak_idx = np.argmax(peaks_intensity)
    main_peak_energy = peaks_energy[main_peak_idx]

    # MEJORA #2: Ajuste de dobletes con constraints físicos
    if is_doublet_region(region_name):
        doublet_params = get_doublet_params(region_name)
        if doublet_params is not None:
            try:
                metadata["is_doublet"] = True
                metadata["fitting_method"] = "fit_doublet"

                # Estimar ancho inicial del pico principal
                fwhm_estimate = 1.5  # eV típico para XPS

                fit_result = fit_doublet(
                    spectrum_nobg,
                    initial_position=main_peak_energy,
                    splitting=doublet_params["splitting"],
                    intensity_ratio=doublet_params["ratio"],
                    shape=doublet_params["profile"],
                    constrain_widths=True,  # Ancho compartido (físicamente esperado)
                )
                return fit_result, spectrum_nobg, background, metadata
            except Exception as e:
                metadata["errors"].append(f"Doublet fit failed: {str(e)}")
                # Fallback a single peak

    # Fallback: single peak Voigt
    try:
        metadata["fitting_method"] = "fit_voigt_single"
        fit_result = fit_voigt(
            spectrum_nobg,
            initial_position=main_peak_energy,
            initial_amplitude=peaks_intensity[main_peak_idx],
            initial_sigma=1.0,
            initial_gamma=0.5,
        )
        return fit_result, spectrum_nobg, background, metadata
    except Exception as e:
        metadata["errors"].append(f"Single peak fit failed: {str(e)}")
        return None, spectrum_nobg, background, metadata


def plot_analysis_results(
    sample_name: str,
    spectrum: XPSSpectrum,
    spectrum_nobg: XPSSpectrum,
    background: np.ndarray,
    fit_result: FitResult | None,
    metadata: dict[str, Any],
    output_path: Path,
) -> None:
    """Plotea resultados de análisis con metadata de Fase E."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot espectro original
    ax.plot(
        spectrum.binding_energy,
        spectrum.intensity,
        "o",
        markersize=3,
        alpha=0.5,
        label="Original",
    )

    # Plot fondo
    ax.plot(
        spectrum.binding_energy,
        background,
        "--",
        linewidth=2,
        color="orange",
        label=f"Fondo ({metadata['background_method']})",
    )

    # Plot espectro sin fondo
    ax.plot(
        spectrum.binding_energy,
        spectrum_nobg.intensity,
        "k-",
        linewidth=1.5,
        label="Sin fondo",
    )

    # Plot ajuste si disponible
    if fit_result is not None:
        ax.plot(
            spectrum_nobg.binding_energy,
            fit_result.fitted_spectrum,
            "r-",
            linewidth=2,
            label=f"Ajuste ({metadata['fitting_method']})",
        )

        # Agregar picos individuales si es doblete
        if metadata["is_doublet"] and len(fit_result.peaks) == 2:
            peak1, peak2 = fit_result.peaks
            # Evaluar picos individuales
            from xps_analyzer.analysis.peak_fitting import _voigt

            peak1_data = _voigt(
                spectrum_nobg.binding_energy,
                peak1.amplitude,
                peak1.position,
                peak1.width,
                peak1.gamma,
            )
            peak2_data = _voigt(
                spectrum_nobg.binding_energy,
                peak2.amplitude,
                peak2.position,
                peak2.width,
                peak2.gamma,
            )

            ax.plot(
                spectrum_nobg.binding_energy,
                peak1_data,
                "b--",
                alpha=0.7,
                label=f"Pico 1: {peak1.position:.1f} eV",
            )
            ax.plot(
                spectrum_nobg.binding_energy,
                peak2_data,
                "g--",
                alpha=0.7,
                label=f"Pico 2: {peak2.position:.1f} eV",
            )

    ax.set_xlabel("Binding Energy (eV)")
    ax.set_ylabel("Intensity (a.u.)")
    ax.set_title(f"{sample_name} - {spectrum.region_name}")
    ax.legend(fontsize=8)
    ax.invert_xaxis()
    ax.grid(True, alpha=0.3)

    # Agregar metadata como texto
    info_text = f"Background: {metadata['background_method']}\n"
    info_text += f"Fitting: {metadata['fitting_method']}\n"
    if fit_result is not None:
        info_text += f"R²: {fit_result.r_squared:.4f}\n"
        if metadata["is_doublet"]:
            info_text += f"Doblete: {len(fit_result.peaks)} picos"

    ax.text(
        0.02,
        0.98,
        info_text,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        fontsize=8,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def analyze_sample_phase_e(
    sample_name: str, input_dir: Path, output_dir: Path
) -> dict[str, Any]:
    """Analiza una muestra completa con mejoras de Fase E."""
    print(f"\n{'=' * 70}")
    print(f"Analizando muestra: {sample_name}")
    print(f"{'=' * 70}")

    sample_dir = input_dir / sample_name
    results_dir = output_dir / sample_name
    results_dir.mkdir(parents=True, exist_ok=True)

    # Cargar dataset (formato multiplex .txt, case-insensitive)
    multiplex_files = list(sample_dir.glob("*[Mm][Uu][Ll][Tt][Ii][Pp][Ll][Ee][Xx].txt"))
    if not multiplex_files:
        raise FileNotFoundError(
            f"No se encontraron archivos multiplex.txt en {sample_dir}"
        )

    dataset = load_single_file(str(multiplex_files[0]))

    # Calibrar
    try:
        shift = calibrate_dataset(dataset)
        print(f"✓ Calibración aplicada: {shift:+.2f} eV")
    except Exception as e:
        print(f"✗ Error en calibración: {e}")
        shift = 0.0

    # MEJORA #3: Cargar RSF con Bi/Sr y fallback habilitado
    rsf = load_sensitivity_factors(
        source="scofield", xray_source="mg_ka", enable_fallback=True
    )
    print(f"✓ RSF cargados: {len(rsf)} elementos (con fallback)")

    # Analizar cada región
    sample_results: dict[str, Any] = {
        "sample_name": sample_name,
        "calibration_shift_ev": float(shift),
        "regions": {},
        "summary": {
            "total_regions": 0,
            "successful_background": 0,
            "successful_fits": 0,
            "doublet_fits": 0,
            "background_methods": {},
            "fitting_methods": {},
        },
    }

    for region_name in dataset.list_regions():
        print(f"\n  Región: {region_name}")

        spectrum = dataset.get_spectrum(region_name)
        fit_result, spectrum_nobg, background, metadata = analyze_spectrum_phase_e(
            spectrum, region_name
        )

        # Actualizar estadísticas de summary
        sample_results["summary"]["total_regions"] += 1
        if metadata["background_method"] is not None:
            sample_results["summary"]["successful_background"] += 1
            bg_method = metadata["background_method"]
            sample_results["summary"]["background_methods"][bg_method] = (
                sample_results["summary"]["background_methods"].get(bg_method, 0) + 1
            )

        if fit_result is not None:
            sample_results["summary"]["successful_fits"] += 1
            fit_method = metadata["fitting_method"]
            sample_results["summary"]["fitting_methods"][fit_method] = (
                sample_results["summary"]["fitting_methods"].get(fit_method, 0) + 1
            )

            if metadata["is_doublet"]:
                sample_results["summary"]["doublet_fits"] += 1

        # Guardar resultados de región
        region_result: dict[str, Any] = {
            "region_name": region_name,
            "metadata": metadata,
        }

        if fit_result is not None:
            region_result["fit"] = {
                "r_squared": float(fit_result.r_squared),
                "num_peaks": len(fit_result.peaks),
                "peaks": [
                    {
                        "position": float(p.position),
                        "amplitude": float(p.amplitude),
                        "area": float(p.area),
                        "width": float(p.width),
                    }
                    for p in fit_result.peaks
                ],
            }
            print(
                f"    ✓ Ajuste exitoso: R²={fit_result.r_squared:.4f}, "
                f"{len(fit_result.peaks)} picos"
            )
        else:
            region_result["fit"] = None
            print(f"    ✗ Ajuste falló: {metadata['errors']}")

        sample_results["regions"][region_name] = region_result

        # Plot
        plot_path = results_dir / f"{region_name.replace(' ', '_')}.png"
        plot_analysis_results(
            sample_name,
            spectrum,
            spectrum_nobg,
            background,
            fit_result,
            metadata,
            plot_path,
        )

    # Calcular tasas de éxito
    total = sample_results["summary"]["total_regions"]
    bg_success = sample_results["summary"]["successful_background"]
    fit_success = sample_results["summary"]["successful_fits"]

    sample_results["summary"]["background_success_rate"] = (
        bg_success / total if total > 0 else 0.0
    )
    sample_results["summary"]["fit_success_rate"] = (
        fit_success / total if total > 0 else 0.0
    )

    # Guardar JSON
    json_path = results_dir / "analysis_results_phase_e.json"
    with open(json_path, "w") as f:
        json.dump(sample_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"RESUMEN - {sample_name}")
    print(f"{'=' * 70}")
    print(f"  Total regiones: {total}")
    print(
        f"  Background exitoso: {bg_success}/{total} "
        f"({sample_results['summary']['background_success_rate'] * 100:.1f}%)"
    )
    print(
        f"  Fits exitosos: {fit_success}/{total} "
        f"({sample_results['summary']['fit_success_rate'] * 100:.1f}%)"
    )
    print(f"  Fits de dobletes: {sample_results['summary']['doublet_fits']}")
    print(f"  Métodos de fondo: {sample_results['summary']['background_methods']}")
    print(f"  Métodos de ajuste: {sample_results['summary']['fitting_methods']}")

    return sample_results


def generate_comparative_summary(
    all_results: list[dict[str, Any]], output_dir: Path
) -> None:
    """Genera resumen comparativo de todas las muestras."""
    summary_path = output_dir / "comparative_summary_phase_e.json"

    comparative: dict[str, Any] = {
        "phase": "E",
        "improvements": [
            "Cascada de fallbacks para sustracción de fondo",
            "Ajuste de dobletes con constraints físicos",
            "RSF extendidos (Bi 4f, Sr 3d) con fallback automático",
        ],
        "samples": {},
        "overall_statistics": {
            "total_regions": 0,
            "successful_background": 0,
            "successful_fits": 0,
            "doublet_fits": 0,
            "background_methods": {},
            "fitting_methods": {},
        },
    }

    for result in all_results:
        sample_name = result["sample_name"]
        summary = result["summary"]

        comparative["samples"][sample_name] = {
            "background_success_rate": summary["background_success_rate"],
            "fit_success_rate": summary["fit_success_rate"],
            "total_regions": summary["total_regions"],
            "successful_fits": summary["successful_fits"],
            "doublet_fits": summary["doublet_fits"],
        }

        # Acumular estadísticas globales
        comparative["overall_statistics"]["total_regions"] += summary["total_regions"]
        comparative["overall_statistics"]["successful_background"] += summary[
            "successful_background"
        ]
        comparative["overall_statistics"]["successful_fits"] += summary[
            "successful_fits"
        ]
        comparative["overall_statistics"]["doublet_fits"] += summary["doublet_fits"]

        for method, count in summary["background_methods"].items():
            comparative["overall_statistics"]["background_methods"][method] = (
                comparative["overall_statistics"]["background_methods"].get(method, 0)
                + count
            )

        for method, count in summary["fitting_methods"].items():
            comparative["overall_statistics"]["fitting_methods"][method] = (
                comparative["overall_statistics"]["fitting_methods"].get(method, 0)
                + count
            )

    # Calcular tasas globales
    total = comparative["overall_statistics"]["total_regions"]
    bg_success = comparative["overall_statistics"]["successful_background"]
    fit_success = comparative["overall_statistics"]["successful_fits"]

    comparative["overall_statistics"]["background_success_rate"] = (
        bg_success / total if total > 0 else 0.0
    )
    comparative["overall_statistics"]["fit_success_rate"] = (
        fit_success / total if total > 0 else 0.0
    )

    with open(summary_path, "w") as f:
        json.dump(comparative, f, indent=2)

    print(f"\n{'=' * 70}")
    print("ESTADÍSTICAS GLOBALES - FASE E")
    print(f"{'=' * 70}")
    print(f"Total regiones procesadas: {total}")
    print(
        f"Background exitoso: {bg_success}/{total} "
        f"({comparative['overall_statistics']['background_success_rate'] * 100:.1f}%)"
    )
    print(
        f"Fits exitosos: {fit_success}/{total} "
        f"({comparative['overall_statistics']['fit_success_rate'] * 100:.1f}%)"
    )
    print(f"Fits de dobletes: {comparative['overall_statistics']['doublet_fits']}")
    print(
        f"Métodos de fondo usados: "
        f"{comparative['overall_statistics']['background_methods']}"
    )
    print(
        f"Métodos de ajuste usados: "
        f"{comparative['overall_statistics']['fitting_methods']}"
    )

    return comparative


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de análisis batch con mejoras de Fase E"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/raw/BN-SET-01",
        help="Directorio con muestras",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/results/BN-SET-01/phase_e",
        help="Directorio de salida",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("ANÁLISIS BATCH - FASE E: Mejoras de Robustez")
    print("=" * 70)
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print("\nMEJORAS APLICADAS:")
    print("  1. Cascada de fallbacks: Shirley → Tougaard → Linear")
    print("  2. Ajuste de dobletes con constraints físicos")
    print("  3. RSF extendidos (Bi 4f, Sr 3d) con fallback")

    all_results = []
    for sample_name in SAMPLES:
        try:
            result = analyze_sample_phase_e(sample_name, input_dir, output_dir)
            all_results.append(result)
        except Exception as e:
            print(f"\n✗ Error procesando {sample_name}: {e}")
            continue

    if all_results:
        generate_comparative_summary(all_results, output_dir)

    print(f"\n{'=' * 70}")
    print("✓ Análisis batch completado")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
