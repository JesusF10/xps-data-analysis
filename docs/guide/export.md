# Data Export

The `export` module serializes analysis results to three standard formats:
CSV (tabular), Excel (multi-sheet), and JSON (hierarchical).

## CSV Export

Flat tabular format suitable for import into spreadsheet software or statistical
tools like R and Origin.

```python
from xps_analyzer.export import export_to_csv

export_to_csv(
    data=dataset,
    filepath="results/spectra.csv",
    include_metadata=True
)
```

## Excel Export

Multi-sheet Excel workbook with organized content:

| Sheet | Content |
|-------|---------|
| `Spectra` | All spectral data (BE, intensity, region) |
| `Peak Fits` | Fitted peak parameters and statistics |
| `Quantification` | Atomic concentrations per element |
| `Metadata` | Instrument parameters and acquisition info |

```python
from xps_analyzer.export import export_to_excel

export_to_excel(
    data={"spectra": dataset, "fits": fit_results},
    filepath="results/analysis.xlsx"
)
```

## JSON Export

Hierarchical JSON format with full provenance tracking. Uses a custom
`NumpyEncoder` to serialize NumPy arrays and types natively.

```python
from xps_analyzer.export import export_to_json

export_to_json(
    data=dataset,
    filepath="results/dataset.json",
    indent=2
)
```

**JSON schema example:**

```json
{
  "filename": "BN-BS-3.vms",
  "header": {
    "instrument": "Kratos Axis Ultra",
    "source": "Al Kα",
    "pass_energy": 40.0
  },
  "spectra": {
    "C 1s": {
      "region_name": "C 1s",
      "binding_energy": [280.0, 279.9, ...],
      "intensity": [1200, 1180, ...],
      "metadata": {
        "acquisition_time": "2024-06-15T14:30:00",
        "scans": 5
      }
    }
  }
}
```

## Custom NumpyEncoder

The `NumpyEncoder` handles serialization of:

- `np.ndarray` → lists
- `np.integer` → Python `int`
- `np.floating` → Python `float`
- `np.bool_` → Python `bool`

All other fields use default JSON serialization, with `fallback` raising a
`TypeError` for non-serializable types.
