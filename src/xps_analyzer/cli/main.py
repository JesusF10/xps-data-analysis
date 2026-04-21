"""
CLI principal para XPS Analyzer.
"""

from pathlib import Path

from xps_analyzer.data_loader import load_single_file
from xps_analyzer.reference_data import load_reference_database
from xps_analyzer.preprocessing import calibrate_sample

import click


@click.group()
@click.version_option()
def cli():
    """
    XPS Analyzer - Software para análisis de datos XPS.

    Herramienta de línea de comandos para análisis de espectros XPS.
    """
    pass


@cli.command()
@click.argument("data_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format", "file_format", help="Formato de archivo (auto-detectado por defecto)"
)
@click.option("--output", "-o", help="Directorio de salida para resultados")
def analyze(data_dir: Path, file_format: str, output: str):
    """
    Analiza archivos XPS en el directorio especificado.

    DATA_DIR: Directorio que contiene los archivos XPS a analizar
    """
    click.echo(f"Analizando conjunto: {data_dir.name}")

    db = load_reference_database()

    try:
        dataset = load_single_file(data_dir)
        click.echo("Archivo cargado exitosamente")
        click.echo(f"Metadatos: {dataset.header}")

        # Mostrar espectros disponibles
        if dataset.spectra:
            click.echo(f"Espectros encontrados: {list(dataset.spectra.keys())}")

        click.echo(f"Análisis completado para {data_dir.name}")

    except Exception as e:
        click.echo(f"Error al procesar {data_dir}: {e}", err=True)
        raise click.ClickException(str(e))


@cli.command()
@click.argument("element", type=str)
@click.option("--verbose", "-v", is_flag=True, help="Muestra información detallada")
def show_element(element: str, verbose: bool):
    """
    Muestra información de referencia para un elemento químico.

    ELEMENT: Símbolo del elemento (e.g., 'C', 'O', 'Fe')
    """
    db = load_reference_database()
    elem_ref = db.elements.get(element)

    if not elem_ref:
        click.echo(f"Elemento '{element}' no encontrado en la base de datos.", err=True)
        raise click.ClickException(f"Elemento '{element}' no encontrado.")

    click.echo(f"Información para el elemento: {element}")
    click.echo(f"Símbolo: {elem_ref.symbol}")
    click.echo(f"Nombre: {elem_ref.element}")
    click.echo(f"Número atómico: {elem_ref.atomic_number}")
    click.echo("Energías de enlace disponibles:")
    for line in elem_ref.photoelectron_lines:
        click.echo(f"- {line}")
    click.echo("Compuestos de referencia:")
    for comp_name, comp in elem_ref.compounds.items():
        click.echo(
            f"- {comp_name}: Posición pico = {comp.binding_energy_range} eV"
            f" Orbital = {comp.orbital}"
        )


def main():
    """Punto de entrada principal."""
    cli()
