
import sys
from pathlib import Path

from xps_analyzer.data_loader import load_single_file


def main():
    if len(sys.argv) < 2:
        print("Uso: xps-analyzer <directorio_de_muestreo>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    if not data_dir.exists():
        print(f"No se encontró {data_dir}")
        sys.exit(1)

    print(f"Analizando conjunto: {data_dir.name}")
    dataset = load_single_file(data_dir)
    print(dataset.header)
    print(dataset.spectra.get("survey").data)
    print(f"Registros cargados desde {data_dir.name}")
