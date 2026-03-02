"""
Módulo de exportación de datos XPS.

Este módulo proporciona funciones para exportar espectros XPS y datasets
a formatos estándar (CSV, Excel, JSON) con metadata completa.

Funciones Principales
--------------------
export_to_csv : Exporta datos a archivos CSV
export_to_excel : Exporta datos a archivos Excel (.xlsx)
export_to_json : Exporta datos a archivos JSON

Ejemplos
--------
>>> from xps_analyzer.export import export_to_csv, export_to_excel
>>> from xps_analyzer import load_single_file
>>>
>>> # Cargar datos
>>> dataset = load_single_file("data.txt")
>>> spectrum = dataset.get_spectrum("C 1s")
>>>
>>> # Exportar a diferentes formatos
>>> export_to_csv(spectrum, "output/c1s_spectrum.csv")
>>> export_to_excel(dataset, "output/dataset.xlsx")
>>> export_to_json(spectrum, "output/spectrum.json")
"""

from .exporters import export_to_csv, export_to_excel, export_to_json

__all__ = ["export_to_csv", "export_to_excel", "export_to_json"]
