"""
Script de exploración de datos XPS - BN-SET-01

Funcionalidad:
1. Carga automática de 4 muestras (maneja inconsistencias en nombres)
2. Cálculo de estadísticas de calidad (SNR, rangos, intensidades)
3. Generación de plots exploratorios (15 figuras total)
4. Exportación de resultados en JSON

Uso:
    uv run python scripts/explore_bn_data.py
"""

from __future__ import annotations

import json
from pathlib import Path

from xps_analyzer import load_single_file
from xps_analyzer.data_loader import XPSDataset

import matplotlib.pyplot as plt
import numpy as np

# Configuración
SAMPLES = ["BN-BS-1", "BN-BS-2", "BN-BS-3", "BN-BS-4"]
DATA_DIR = Path("data/raw/BN-SET-01")
OUTPUT_DIR = Path("data/results/BN-SET-01/exploration")


def find_file_case_insensitive(directory: Path, pattern: str) -> Path | None:
    """
    Busca archivo ignorando mayúsculas/minúsculas.

    Parámetros
    ----------
    directory : Path
        Directorio donde buscar.
    pattern : str
        Nombre de archivo a buscar (será comparado case-insensitive).

    Retorna
    -------
    Path | None
        Path absoluto del archivo encontrado, o None si no existe.
    """
    pattern_lower = pattern.lower()
    for file in directory.iterdir():
        if file.name.lower() == pattern_lower:
            return file
    return None


def calculate_snr(intensity: np.ndarray) -> float:
    """
    Calcula relación señal/ruido estimada.

    El SNR se estima como el ratio entre el promedio del 10% de valores
    más altos (señal) y la desviación estándar del 10% de valores más bajos (ruido).

    Parámetros
    ----------
    intensity : np.ndarray
        Array de intensidades del espectro.

    Retorna
    -------
    float
        Relación señal/ruido. Retorna inf si el ruido es cero.
    """
    sorted_int = np.sort(intensity)
    n = len(sorted_int)

    # Signal: promedio de valores más altos (top 10%)
    signal = np.mean(sorted_int[int(n * 0.9) :])

    # Noise: desviación estándar de valores más bajos (bottom 10%)
    noise = np.std(sorted_int[: int(n * 0.1)])

    return signal / noise if noise > 0 else np.inf


def explore_sample(sample_name: str) -> tuple[dict, XPSDataset, XPSDataset] | None:
    """
    Explora una muestra individual.

    Carga archivos multiplex y survey, calcula estadísticas de calidad
    para cada región.

    Parámetros
    ----------
    sample_name : str
        Nombre de la muestra (ej: "BN-BS-1").

    Retorna
    -------
    tuple[dict, XPSDataset, XPSDataset] | None
        Tupla con (estadísticas, dataset_multiplex, dataset_survey),
        o None si hay error en la carga.
    """
    sample_dir = DATA_DIR / sample_name

    # Buscar archivos (case-insensitive para manejar inconsistencias)
    multiplex_path = find_file_case_insensitive(
        sample_dir, f"{sample_name} multiplex.txt"
    )
    survey_path = find_file_case_insensitive(sample_dir, f"{sample_name} survey.txt")

    if multiplex_path is None:
        print(f"  ❌ Archivo multiplex no encontrado en {sample_dir}")
        return None

    if survey_path is None:
        print(f"  ❌ Archivo survey no encontrado en {sample_dir}")
        return None

    print(f"  ✓ Archivos encontrados:")
    print(f"    - multiplex: {multiplex_path.name}")
    print(f"    - survey: {survey_path.name}")

    # Cargar datos
    try:
        dataset_multiplex = load_single_file(multiplex_path)
        dataset_survey = load_single_file(survey_path)
    except Exception as e:
        print(f"  ❌ Error al cargar datos: {e}")
        return None

    print(f"  ✓ Cargado: {len(dataset_multiplex.list_regions())} regiones + survey")

    # Estadísticas por región
    stats = {"sample": sample_name, "regions": {}, "survey": {}}

    # Procesar regiones multiplex
    for region_name in dataset_multiplex.list_regions():
        spectrum = dataset_multiplex.get_spectrum(region_name)
        stats["regions"][region_name] = {
            "num_points": len(spectrum.binding_energy),
            "energy_range": [
                float(spectrum.binding_energy.min()),
                float(spectrum.binding_energy.max()),
            ],
            "intensity_range": [
                float(spectrum.intensity.min()),
                float(spectrum.intensity.max()),
            ],
            "intensity_mean": float(spectrum.intensity.mean()),
            "intensity_std": float(spectrum.intensity.std()),
            "snr": float(calculate_snr(spectrum.intensity)),
        }

    # Procesar survey
    survey_spectrum = list(dataset_survey.spectra.values())[0]
    stats["survey"] = {
        "num_points": len(survey_spectrum.binding_energy),
        "energy_range": [
            float(survey_spectrum.binding_energy.min()),
            float(survey_spectrum.binding_energy.max()),
        ],
        "intensity_mean": float(survey_spectrum.intensity.mean()),
        "snr": float(calculate_snr(survey_spectrum.intensity)),
    }

    return stats, dataset_multiplex, dataset_survey


def plot_sample_grid(sample_name: str, dataset: XPSDataset, output_path: Path) -> None:
    """
    Genera grid de plots de todas las regiones.

    Crea una figura con subplots 2x3 mostrando las 6 regiones de la muestra.

    Parámetros
    ----------
    sample_name : str
        Nombre de la muestra.
    dataset : XPSDataset
        Dataset con las regiones a plotear.
    output_path : Path
        Path donde guardar la figura PNG.
    """
    regions = dataset.list_regions()
    n_regions = len(regions)

    # Grid layout (2 filas x 3 columnas para 6 regiones)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, region_name in enumerate(regions):
        spectrum = dataset.get_spectrum(region_name)
        ax = axes[idx]

        ax.plot(spectrum.binding_energy, spectrum.intensity, "b-", linewidth=1)
        ax.set_xlabel("Binding Energy (eV)", fontsize=9)
        ax.set_ylabel("Intensity (a.u.)", fontsize=9)
        ax.set_title(region_name, fontsize=11, fontweight="bold")
        ax.invert_xaxis()
        ax.grid(True, alpha=0.3)

    # Ocultar ejes sobrantes si hay menos de 6 regiones
    for idx in range(n_regions, 6):
        axes[idx].axis("off")

    plt.suptitle(f"{sample_name} - Todas las Regiones", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_survey_comparison(surveys: dict, output_path: Path) -> None:
    """
    Compara espectros survey de las 4 muestras.

    Genera un plot overlay con los 4 espectros survey superpuestos.

    Parámetros
    ----------
    surveys : dict
        Diccionario {sample_name: XPSSpectrum} con los surveys.
    output_path : Path
        Path donde guardar la figura PNG.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ["blue", "red", "green", "orange"]
    for idx, (sample_name, spectrum) in enumerate(surveys.items()):
        ax.plot(
            spectrum.binding_energy,
            spectrum.intensity,
            label=sample_name,
            color=colors[idx],
            alpha=0.7,
            linewidth=1.5,
        )

    ax.set_xlabel("Binding Energy (eV)", fontsize=12)
    ax.set_ylabel("Intensity (a.u.)", fontsize=12)
    ax.set_title("Comparación de Espectros Survey - 4 Muestras", fontsize=14)
    ax.invert_xaxis()
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_region_comparison(region_name: str, spectra: dict, output_path: Path) -> None:
    """
    Compara una región específica entre las 4 muestras.

    Genera un plot overlay mostrando la misma región en las 4 muestras.

    Parámetros
    ----------
    region_name : str
        Nombre de la región a comparar.
    spectra : dict
        Diccionario {sample_name: XPSSpectrum} con los espectros de la región.
    output_path : Path
        Path donde guardar la figura PNG.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["blue", "red", "green", "orange"]
    for idx, (sample_name, spectrum) in enumerate(spectra.items()):
        ax.plot(
            spectrum.binding_energy,
            spectrum.intensity,
            label=sample_name,
            color=colors[idx],
            alpha=0.7,
            linewidth=1.5,
        )

    ax.set_xlabel("Binding Energy (eV)", fontsize=12)
    ax.set_ylabel("Intensity (a.u.)", fontsize=12)
    ax.set_title(f"Comparación {region_name} - 4 Muestras", fontsize=14)
    ax.invert_xaxis()
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    """Ejecuta exploración completa."""
    # Crear directorio de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXPLORACIÓN DE DATOS BN-SET-01")
    print("=" * 60)

    all_stats = {}
    all_surveys = {}
    all_regions_by_name = {}

    # Procesar cada muestra
    for sample_name in SAMPLES:
        print(f"\n📂 Procesando {sample_name}...")

        result = explore_sample(sample_name)
        if result is None:
            print(f"  ⚠️  Saltando {sample_name} debido a errores\n")
            continue

        stats, dataset_multiplex, dataset_survey = result
        all_stats[sample_name] = stats

        # Guardar survey para comparación
        all_surveys[sample_name] = list(dataset_survey.spectra.values())[0]

        # Guardar regiones para comparación
        for region_name in dataset_multiplex.list_regions():
            if region_name not in all_regions_by_name:
                all_regions_by_name[region_name] = {}
            all_regions_by_name[region_name][sample_name] = (
                dataset_multiplex.get_spectrum(region_name)
            )

        # Generar grid de plots
        plot_path = OUTPUT_DIR / f"{sample_name}_all_regions.png"
        plot_sample_grid(sample_name, dataset_multiplex, plot_path)
        print(f"  ✓ Grid de regiones guardado: {plot_path.name}")

        # Mostrar estadísticas
        print(f"\n  Regiones encontradas:")
        for region_name, region_stats in stats["regions"].items():
            print(
                f"    - {region_name:12s}: "
                f"{region_stats['num_points']:4d} puntos, "
                f"SNR={region_stats['snr']:6.1f}, "
                f"Range: {region_stats['energy_range'][0]:.1f}-"
                f"{region_stats['energy_range'][1]:.1f} eV"
            )

    # Verificar que tenemos datos para comparar
    if len(all_stats) == 0:
        print("\n❌ No se pudo cargar ninguna muestra. Abortando.")
        return

    # Plots comparativos
    print("\n📊 Generando plots comparativos...")

    # Survey comparison
    if len(all_surveys) > 0:
        survey_comp_path = OUTPUT_DIR / "survey_comparison.png"
        plot_survey_comparison(all_surveys, survey_comp_path)
        print(f"  ✓ Comparación survey: {survey_comp_path.name}")

    # Region comparisons
    for region_name, spectra in all_regions_by_name.items():
        safe_name = region_name.replace(" ", "_")
        region_comp_path = OUTPUT_DIR / f"region_{safe_name}_comparison.png"
        plot_region_comparison(region_name, spectra, region_comp_path)
        print(f"  ✓ Comparación {region_name}: {region_comp_path.name}")

    # Guardar estadísticas en JSON
    stats_path = OUTPUT_DIR.parent / "exploration_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Estadísticas guardadas: {stats_path}")

    # Calcular SNR promedio
    all_snrs = []
    for sample_stats in all_stats.values():
        for region_stats in sample_stats["regions"].values():
            all_snrs.append(region_stats["snr"])
    avg_snr = np.mean(all_snrs) if len(all_snrs) > 0 else 0

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE EXPLORACIÓN")
    print("=" * 60)
    print(f"✓ {len(all_stats)} muestras procesadas")
    if len(all_regions_by_name) > 0:
        print(
            f"✓ {len(all_regions_by_name)} regiones identificadas: "
            f"{', '.join(all_regions_by_name.keys())}"
        )
    print(
        f"✓ {len(all_stats) + len(all_regions_by_name) + 1} plots generados "
        f"({len(all_stats)} grids + {len(all_regions_by_name) + 1} comparaciones)"
    )
    print(
        f"✓ SNR promedio: {avg_snr:.1f} (calidad {'buena' if avg_snr > 15 else 'regular'} para análisis)"
    )
    print(f"✓ Resultados en: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
