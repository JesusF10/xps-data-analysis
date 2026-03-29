"""
Script de análisis comparativo para el dataset BN-SET-01.

Genera análisis estadístico profundo de las 4 muestras:
- Heatmap de R² por región/muestra
- Plots overlay de espectros
- Correlación SNR vs. éxito de pipeline
- Distribuciones de shifts de calibración
- Identificación de causas de fallas

Uso:
    uv run python scripts/compare_samples.py \\
        --results-dir "data/results/BN-SET-01" \\
        --output-dir "data/results/BN-SET-01/comparative"

Autor: Jesús Flores Lacarra
Fecha: Marzo 2026
Versión: XPS Analyzer v0.8.0-beta
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from xps_analyzer import load_single_file

# Configuración de estilo
plt.style.use("default")
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

SAMPLES = ["BN-BS-1", "BN-BS-2", "BN-BS-3", "BN-BS-4"]
REGIONS = ["Bi 4f", "C 1s", "Na 1s", "O 1s", "Sr 3d", "Ti 2p"]


def load_all_results(results_dir: Path) -> dict[str, dict]:
    """
    Carga todos los resultados de análisis.

    Parámetros
    ----------
    results_dir : Path
        Directorio con resultados de Fase C.

    Retorna
    -------
    dict[str, dict]
        Diccionario {sample_name: results}.
    """
    all_results = {}
    for sample in SAMPLES:
        results_file = results_dir / sample / "analysis_results.json"
        if results_file.exists():
            with open(results_file, encoding="utf-8") as f:
                all_results[sample] = json.load(f)
    return all_results


def load_exploration_stats(results_dir: Path) -> dict[str, dict]:
    """
    Carga estadísticas de exploración (Fase A) con SNR.

    Parámetros
    ----------
    results_dir : Path
        Directorio con resultados.

    Retorna
    -------
    dict[str, dict]
        Diccionario con estadísticas de SNR.
    """
    stats_file = results_dir / "exploration_stats.json"
    if stats_file.exists():
        with open(stats_file, encoding="utf-8") as f:
            return json.load(f)
    return {}


def create_r2_heatmap(all_results: dict, output_path: Path):
    """
    Crea heatmap de R² por región y muestra.

    Parámetros
    ----------
    all_results : dict
        Resultados de análisis de todas las muestras.
    output_path : Path
        Ruta donde guardar el plot.
    """
    # Crear matriz de R² (muestras × regiones)
    r2_matrix = np.full((len(SAMPLES), len(REGIONS)), np.nan)

    for i, sample in enumerate(SAMPLES):
        if sample not in all_results:
            continue
        for j, region in enumerate(REGIONS):
            if region in all_results[sample]["regions"]:
                region_data = all_results[sample]["regions"][region]
                if region_data.get("fitting_success", False):
                    r2_matrix[i, j] = region_data.get("r_squared", np.nan)

    # Crear heatmap
    fig, ax = plt.subplots(figsize=(10, 6))

    # Usar máscara para valores NaN
    mask = np.isnan(r2_matrix)

    # Crear heatmap manualmente con imshow
    cmap = plt.cm.RdYlGn
    im = ax.imshow(r2_matrix, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("R² (Coeficiente de Determinación)", fontsize=10)

    # Agregar anotaciones
    for i in range(len(SAMPLES)):
        for j in range(len(REGIONS)):
            if not mask[i, j]:
                text = ax.text(
                    j,
                    i,
                    f"{r2_matrix[i, j]:.3f}",
                    ha="center",
                    va="center",
                    color="black" if r2_matrix[i, j] < 0.5 else "white",
                    fontsize=10,
                )

    # Configurar ticks
    ax.set_xticks(np.arange(len(REGIONS)))
    ax.set_yticks(np.arange(len(SAMPLES)))
    ax.set_xticklabels(REGIONS)
    ax.set_yticklabels(SAMPLES)

    # Rotar labels del eje x
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Marcar celdas con NaN (fallas)
    for i in range(len(SAMPLES)):
        for j in range(len(REGIONS)):
            if mask[i, j]:
                ax.add_patch(
                    Rectangle(
                        (j - 0.5, i - 0.5),
                        1,
                        1,
                        fill=True,
                        facecolor="gray",
                        alpha=0.5,
                        zorder=0,
                    )
                )
                ax.text(
                    j,
                    i,
                    "FAIL",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="darkred",
                    weight="bold",
                )

    ax.set_title(
        "Calidad de Fitting por Región y Muestra\n(R² = bondad de ajuste, gris = fallo)",
        fontsize=14,
        pad=20,
    )
    ax.set_xlabel("Región XPS", fontsize=12)
    ax.set_ylabel("Muestra", fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  ✓ Heatmap R²: {output_path.name}")


def create_snr_vs_success_plot(all_results: dict, snr_stats: dict, output_path: Path):
    """
    Crea scatter plot de SNR vs. éxito de fitting.

    Parámetros
    ----------
    all_results : dict
        Resultados de análisis.
    snr_stats : dict
        Estadísticas de SNR (Fase A).
    output_path : Path
        Ruta donde guardar el plot.
    """
    # Recopilar datos
    snr_values = []
    success_values = []
    r2_values = []
    labels = []

    for sample in SAMPLES:
        if sample not in all_results or sample not in snr_stats:
            continue

        for region in REGIONS:
            # SNR de exploración
            if region not in snr_stats[sample]["regions"]:
                continue
            snr = snr_stats[sample]["regions"][region]["snr"]

            # Éxito de fitting
            if region in all_results[sample]["regions"]:
                region_data = all_results[sample]["regions"][region]
                success = region_data.get("fitting_success", False)
                r2 = region_data.get("r_squared", 0.0) if success else 0.0

                snr_values.append(snr)
                success_values.append(1 if success else 0)
                r2_values.append(r2 if success else 0.0)
                labels.append(f"{sample}-{region}")

    # Crear plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Panel 1: SNR vs. Success Rate
    success_array = np.array(success_values)
    snr_array = np.array(snr_values)

    colors = ["red" if s == 0 else "green" for s in success_values]

    ax1.scatter(
        snr_array, success_array, c=colors, s=100, alpha=0.6, edgecolors="black"
    )
    ax1.set_xlabel("SNR (Signal-to-Noise Ratio)", fontsize=12)
    ax1.set_ylabel("Fitting Success (0=Fallo, 1=Éxito)", fontsize=12)
    ax1.set_title("SNR vs. Éxito de Fitting", fontsize=13)
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(alpha=0.3)

    # Agregar threshold visual
    snr_success = snr_array[success_array == 1]
    snr_fail = snr_array[success_array == 0]

    if len(snr_success) > 0 and len(snr_fail) > 0:
        threshold_approx = (snr_success.min() + snr_fail.max()) / 2
        ax1.axvline(
            threshold_approx,
            color="orange",
            linestyle="--",
            label=f"Threshold ≈ {threshold_approx:.1f}",
        )
        ax1.legend()

    # Panel 2: SNR vs. R² (solo exitosos)
    r2_array = np.array(r2_values)
    successful_mask = success_array == 1

    if successful_mask.sum() > 0:
        ax2.scatter(
            snr_array[successful_mask],
            r2_array[successful_mask],
            c=r2_array[successful_mask],
            s=100,
            cmap="viridis",
            alpha=0.7,
            edgecolors="black",
        )
        ax2.set_xlabel("SNR", fontsize=12)
        ax2.set_ylabel("R² (Calidad de Fitting)", fontsize=12)
        ax2.set_title("SNR vs. R² (Solo Fittings Exitosos)", fontsize=13)
        ax2.grid(alpha=0.3)

        # Agregar colorbar
        sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax2)
        cbar.set_label("R²", fontsize=10)

        # Línea de tendencia
        if successful_mask.sum() > 2:
            z = np.polyfit(snr_array[successful_mask], r2_array[successful_mask], 1)
            p = np.poly1d(z)
            x_line = np.linspace(
                snr_array[successful_mask].min(), snr_array[successful_mask].max(), 100
            )
            ax2.plot(x_line, p(x_line), "r--", alpha=0.5, label="Tendencia lineal")
            ax2.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  ✓ SNR vs. Success: {output_path.name}")


def create_calibration_shift_plot(all_results: dict, output_path: Path):
    """
    Crea plot de distribución de shifts de calibración.

    Parámetros
    ----------
    all_results : dict
        Resultados de análisis.
    output_path : Path
        Ruta donde guardar el plot.
    """
    shifts = []
    samples = []

    for sample in SAMPLES:
        if sample in all_results:
            shift = all_results[sample].get("calibration_shift_eV", None)
            if shift is not None:
                shifts.append(shift)
                samples.append(sample)

    if not shifts:
        print("  ⚠️  No hay datos de calibración")
        return

    # Crear plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Bar plot de shifts
    colors = ["steelblue" if abs(s) > 2.0 else "lightblue" for s in shifts]
    bars = ax1.bar(samples, shifts, color=colors, alpha=0.8, edgecolor="black")

    # Agregar valores en barras
    for bar, shift in zip(bars, shifts):
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{shift:.2f}",
            ha="center",
            va="bottom" if height > 0 else "top",
            fontsize=10,
        )

    ax1.axhline(0, color="black", linewidth=0.8)
    ax1.set_xlabel("Muestra", fontsize=12)
    ax1.set_ylabel("Shift de Calibración (eV)", fontsize=12)
    ax1.set_title("Shifts de Calibración por Muestra", fontsize=13)
    ax1.grid(axis="y", alpha=0.3)

    # Panel 2: Histograma + estadísticas
    ax2.hist(shifts, bins=10, color="steelblue", alpha=0.7, edgecolor="black")
    ax2.axvline(
        np.mean(shifts),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Media: {np.mean(shifts):.2f} eV",
    )
    ax2.axvline(
        np.mean(shifts) - np.std(shifts),
        color="orange",
        linestyle=":",
        linewidth=1.5,
        label=f"±1σ: {np.std(shifts):.2f} eV",
    )
    ax2.axvline(
        np.mean(shifts) + np.std(shifts), color="orange", linestyle=":", linewidth=1.5
    )

    ax2.set_xlabel("Shift de Calibración (eV)", fontsize=12)
    ax2.set_ylabel("Frecuencia", fontsize=12)
    ax2.set_title("Distribución de Shifts", fontsize=13)
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  ✓ Calibration shifts: {output_path.name}")


def create_spectrum_overlay(results_dir: Path, region_name: str, output_path: Path):
    """
    Crea plot overlay de espectros de una región para las 4 muestras.

    Parámetros
    ----------
    results_dir : Path
        Directorio con datos raw.
    region_name : str
        Nombre de la región (ej: "O 1s").
    output_path : Path
        Ruta donde guardar el plot.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["blue", "green", "red", "purple"]
    found_any = False

    for sample, color in zip(SAMPLES, colors):
        # Buscar archivo multiplex
        sample_dir = results_dir.parent.parent / "raw" / "BN-SET-01" / sample
        multiplex_files = [
            f
            for f in sample_dir.glob("*[Mm][Uu][Ll][Tt][Ii]*")
            if f.suffix.lower() == ".txt"
        ]

        if not multiplex_files:
            continue

        try:
            dataset = load_single_file(multiplex_files[0])

            # Buscar región
            if region_name in dataset.list_regions():
                spectrum = dataset.get_spectrum(region_name)
                ax.plot(
                    spectrum.binding_energy,
                    spectrum.intensity,
                    label=sample,
                    color=color,
                    alpha=0.7,
                    linewidth=1.5,
                )
                found_any = True
        except Exception as e:
            print(f"  ⚠️  Error cargando {sample}/{region_name}: {e}")
            continue

    if not found_any:
        print(f"  ⚠️  No se encontraron datos para {region_name}")
        plt.close()
        return

    ax.set_xlabel("Binding Energy (eV)", fontsize=12)
    ax.set_ylabel("Intensity (a.u.)", fontsize=12)
    ax.set_title(f"Comparación de Espectros: {region_name}", fontsize=14)
    ax.legend()
    ax.invert_xaxis()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  ✓ Overlay {region_name}: {output_path.name}")


def create_success_rate_by_region(all_results: dict, output_path: Path):
    """
    Crea plot de tasa de éxito por región.

    Parámetros
    ----------
    all_results : dict
        Resultados de análisis.
    output_path : Path
        Ruta donde guardar el plot.
    """
    # Calcular tasas de éxito
    success_rates = {}
    total_samples = len(all_results)

    for region in REGIONS:
        success_count = 0
        for sample in all_results.values():
            if region in sample["regions"]:
                if sample["regions"][region].get("fitting_success", False):
                    success_count += 1
        success_rates[region] = (success_count / total_samples) * 100

    # Crear plot
    fig, ax = plt.subplots(figsize=(10, 6))

    regions_sorted = sorted(success_rates.items(), key=lambda x: x[1], reverse=True)
    regions_names = [r[0] for r in regions_sorted]
    rates = [r[1] for r in regions_sorted]

    colors = ["green" if r >= 75 else "orange" if r >= 50 else "red" for r in rates]
    bars = ax.barh(regions_names, rates, color=colors, alpha=0.7, edgecolor="black")

    # Agregar valores
    for bar, rate in zip(bars, rates):
        width = bar.get_width()
        ax.text(
            width + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{rate:.0f}%",
            ha="left",
            va="center",
            fontsize=10,
        )

    ax.axvline(75, color="green", linestyle="--", alpha=0.5, label="Objetivo: 75%")
    ax.set_xlabel("Tasa de Éxito (%)", fontsize=12)
    ax.set_ylabel("Región XPS", fontsize=12)
    ax.set_title("Tasa de Éxito de Fitting por Región (4 muestras)", fontsize=14)
    ax.set_xlim(0, 110)
    ax.legend()
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  ✓ Success rates: {output_path.name}")


def generate_comparative_summary(all_results: dict, snr_stats: dict, output_path: Path):
    """
    Genera documento JSON con resumen estadístico comparativo.

    Parámetros
    ----------
    all_results : dict
        Resultados de análisis.
    snr_stats : dict
        Estadísticas de SNR.
    output_path : Path
        Ruta donde guardar el resumen.
    """
    summary = {
        "dataset": "BN-SET-01",
        "num_samples": len(all_results),
        "num_regions": len(REGIONS),
        "calibration": {},
        "fitting_quality": {},
        "snr_analysis": {},
        "failure_analysis": {},
    }

    # 1. Calibración
    shifts = [
        r.get("calibration_shift_eV")
        for r in all_results.values()
        if "calibration_shift_eV" in r
    ]
    if shifts:
        summary["calibration"] = {
            "shifts_eV": {
                s: all_results[s].get("calibration_shift_eV")
                for s in SAMPLES
                if s in all_results
            },
            "mean_shift_eV": float(np.mean(shifts)),
            "std_shift_eV": float(np.std(shifts)),
            "cv_percent": float(np.std(shifts) / abs(np.mean(shifts)) * 100),
        }

    # 2. Calidad de fitting
    r2_values = []
    for sample in all_results.values():
        for region_data in sample["regions"].values():
            if region_data.get("fitting_success", False):
                r2_values.append(region_data.get("r_squared", 0.0))

    if r2_values:
        summary["fitting_quality"] = {
            "mean_r2": float(np.mean(r2_values)),
            "median_r2": float(np.median(r2_values)),
            "std_r2": float(np.std(r2_values)),
            "min_r2": float(np.min(r2_values)),
            "max_r2": float(np.max(r2_values)),
            "num_successful_fits": len(r2_values),
            "total_attempts": len(SAMPLES) * len(REGIONS),
            "success_rate_percent": float(
                len(r2_values) / (len(SAMPLES) * len(REGIONS)) * 100
            ),
        }

    # 3. Análisis SNR
    snr_by_region = {}
    for region in REGIONS:
        snr_vals = []
        for sample in SAMPLES:
            if sample in snr_stats and region in snr_stats[sample]["regions"]:
                snr_vals.append(snr_stats[sample]["regions"][region]["snr"])
        if snr_vals:
            snr_by_region[region] = {
                "mean": float(np.mean(snr_vals)),
                "std": float(np.std(snr_vals)),
                "min": float(np.min(snr_vals)),
                "max": float(np.max(snr_vals)),
            }

    summary["snr_analysis"] = snr_by_region

    # 4. Análisis de fallas
    failures_by_region = {region: [] for region in REGIONS}
    for sample_name, sample_data in all_results.items():
        for region in REGIONS:
            if region in sample_data["regions"]:
                if not sample_data["regions"][region].get("fitting_success", False):
                    failures_by_region[region].append(sample_name)

    summary["failure_analysis"] = {
        region: {
            "failed_samples": failures,
            "failure_rate_percent": float(len(failures) / len(SAMPLES) * 100),
        }
        for region, failures in failures_by_region.items()
    }

    # Guardar
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Summary JSON: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Análisis comparativo del dataset BN-SET-01"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("data/results/BN-SET-01"),
        help="Directorio con resultados de Fase C",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/results/BN-SET-01/comparative"),
        help="Directorio de salida para plots comparativos",
    )

    args = parser.parse_args()

    results_dir = args.results_dir
    output_dir = args.output_dir

    if not results_dir.exists():
        print(f"❌ Error: Directorio de resultados no existe: {results_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("🔬 FASE D: ANÁLISIS COMPARATIVO - XPS Analyzer v0.8.0-beta")
    print("=" * 70)
    print(f"\nInput:  {results_dir}")
    print(f"Output: {output_dir}")

    # Cargar datos
    print("\n1️⃣  Cargando datos...")
    all_results = load_all_results(results_dir)
    snr_stats = load_exploration_stats(results_dir)
    print(f"  ✓ {len(all_results)} muestras cargadas")
    print(f"  ✓ SNR stats: {'disponibles' if snr_stats else 'no encontradas'}")

    # Generar plots
    print("\n2️⃣  Generando plots comparativos...")

    # Heatmap R²
    create_r2_heatmap(all_results, output_dir / "r2_heatmap.png")

    # SNR vs. Success
    if snr_stats:
        create_snr_vs_success_plot(
            all_results, snr_stats, output_dir / "snr_vs_success.png"
        )

    # Calibration shifts
    create_calibration_shift_plot(all_results, output_dir / "calibration_shifts.png")

    # Success rates por región
    create_success_rate_by_region(
        all_results, output_dir / "success_rates_by_region.png"
    )

    # Overlays de espectros (regiones clave)
    print("\n3️⃣  Generando overlays de espectros...")
    for region in ["O 1s", "Ti 2p", "C 1s"]:
        create_spectrum_overlay(
            results_dir,
            region,
            output_dir / f"spectrum_overlay_{region.replace(' ', '_')}.png",
        )

    # Resumen estadístico
    print("\n4️⃣  Generando resumen estadístico...")
    generate_comparative_summary(
        all_results, snr_stats, output_dir / "comparative_summary.json"
    )

    print("\n" + "=" * 70)
    print("✅ FASE D COMPLETADA")
    print("=" * 70)
    print(f"\nPlots generados: {len(list(output_dir.glob('*.png')))}")
    print(f"Resumen: {output_dir / 'comparative_summary.json'}")


if __name__ == "__main__":
    main()
