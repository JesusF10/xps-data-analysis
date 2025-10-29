"""
CLI principal para XPS Analyzer.
"""

from pathlib import Path

from xps_analyzer.data_loader import load_single_file

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


def main():
    """Punto de entrada principal."""
    cli()
