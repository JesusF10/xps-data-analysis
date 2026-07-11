# Quick Start

This guide walks through a complete analysis pipeline using real XPS data.

## Launch the GUI

The quickest way to explore your data is through the interactive Streamlit interface:

```bash
uv run streamlit run src/xps_analyzer/gui/app.py
```

## Programmatic Pipeline

### 1. Load Data

```python
from xps_analyzer import load_single_file, load_all_data

# Single file with automatic format detection
dataset = load_single_file("data/raw/samples/sample.txt")
print(f"File: {dataset.filename}")
print(f"Spectra: {list(dataset.spectra.keys())}")

# Batch load from directory
samples = load_all_data("data/raw/BN-SET-01")
```

### 2. Inspect a Spectrum

```python
c1s = dataset.get_spectrum("C 1s")
print(f"Binding energy range: {c1s.binding_energy.min():.1f} – {c1s.binding_energy.max():.1f} eV")
print(f"Number of data points: {len(c1s.binding_energy)}")
```

### 3. Calibrate Energy Scale

```python
from xps_analyzer.preprocessing import calibrate_spectrum

# Calibrate using a reference peak (e.g., C 1s at 284.8 eV)
c1s_calibrated = calibrate_spectrum(c1s, reference_element="C 1s", reference_energy=284.8)
```

### 4. Subtract Background

```python
from xps_analyzer.analysis import shirley_background, tougaard_background

# Shirley iterative background
c1s_nobg = shirley_background(c1s_calibrated, inplace=False)

# Alternative: Tougaard universal cross-section
# c1s_nobg = tougaard_background(c1s_calibrated, inplace=False)
```

### 5. Fit Peaks

```python
from xps_analyzer.analysis import fit_voigt, fit_multiple_peaks, fit_doublet

# Single Voigt profile
result = fit_voigt(c1s_nobg, position=284.8, fwhm=1.2)
print(f"R² = {result.r_squared:.4f}")

# Multiple peak deconvolution
peaks = fit_multiple_peaks(
    c1s_nobg,
    positions=[284.8, 286.2, 288.5],
    models=["voigt", "voigt", "voigt"]
)

# Spin-orbit doublet (e.g., Ti 2p)
doublet = fit_doublet(
    c1s_nobg,
    peak_position=458.7,
    separation=5.7,
    area_ratio=0.5  # p-orbital branching ratio
)
```

### 6. Quantify Composition

```python
from xps_analyzer.analysis import (
    load_sensitivity_factors,
    calculate_atomic_concentration,
    normalize_to_100
)

rsf = load_sensitivity_factors(database="scofield")
concentrations = calculate_atomic_concentration(
    dataset,
    rsf_database=rsf,
    corrections=["transmission", "imfp"]
)
normalized = normalize_to_100(concentrations)
print(normalized)
```

### 7. Export Results

```python
from xps_analyzer.export import export_to_csv, export_to_excel, export_to_json

export_to_csv(dataset, "results/spectra.csv")
export_to_excel({"c1s_fit": result}, "results/analysis.xlsx")
export_to_json(dataset, "results/dataset.json")
```

## Complete Script Example

See [`scripts/analyze_single_sample.py`](https://github.com/JesusF10/xps-data-analysis/blob/main/scripts/analyze_single_sample.py) for a complete batch analysis pipeline.
