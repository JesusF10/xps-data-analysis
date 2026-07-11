# Atomic Quantification

The `analysis.quantification` module converts peak intensities into atomic
concentrations using Relative Sensitivity Factors (RSF).

## Theory

Quantification is based on the fundamental XPS intensity equation:

\[
I_i = n_i \cdot \sigma_i \cdot \Phi \cdot T(E_i) \cdot \lambda(E_i) \cdot A
\]

where $I_i$ is the peak area for element $i$, $\sigma_i$ is the photoionization
cross-section (RSF), $\Phi$ is the X-ray flux, $T$ is the analyzer transmission
function, $\lambda$ is the inelastic mean free path, and $A$ is the analysis area.
The atomic concentration is:

\[
X_i = \frac{I_i / \text{RSF}_i}{\sum_j I_j / \text{RSF}_j} \times 100\%
\]

## RSF Databases

| Database | Source | Coverage |
|----------|--------|----------|
| **Scofield** | Scofield, 1976 | All elements, Al K$\alpha$ |
| **Wagner** | Wagner, 1983 | Empirical, common XPS lines |

```python
from xps_analyzer.analysis import load_sensitivity_factors

rsf = load_sensitivity_factors(database="scofield")
# rsf is a dict: {element_symbol: sensitivity_factor}
```

## API Reference

### calculate_atomic_concentration

```python
from xps_analyzer.analysis import calculate_atomic_concentration

concentrations = calculate_atomic_concentration(
    dataset=dataset,
    rsf_database=rsf,
    corrections=["transmission", "imfp"]
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset` | `XPSDataset` | Calibrated dataset with fitted peaks |
| `rsf_database` | `dict` | Element RSF values |
| `corrections` | `list[str]` | Optional corrections: `transmission`, `imfp` |

**Returns:** `dict[str, float]` — atomic percentages keyed by element.

### normalize_to_100

```python
from xps_analyzer.analysis import normalize_to_100

normalized = normalize_to_100(concentrations)
```

Normalizes concentrations to sum to 100%. Detected elements below detection
threshold (configurable, default 0.1 at.%) are excluded.

### quantify_dataset

Runs the full quantification pipeline on an entire dataset:

```python
from xps_analyzer.analysis import quantify_dataset

summary = quantify_dataset(dataset, rsf_database="scofield")
# summary is a DataFrame with elements, peak areas, RSF, and at.%
```

## Correction Factors

### Transmission Function Correction

The analyzer transmission function $T(E)$ depends on the pass energy and lens mode.
Correction factors are loaded from `config/instrument_profiles.toml`:

```toml
[instrument.profiles.thermo_k_alpha]
transmission_function = "E^-0.7"
pass_energy = 50.0
```

### IMFP Correction

The inelastic mean free path $\lambda(E)$ is energy-dependent. The correction uses
the TPP-2M formula (Tanuma, Powell, Penn):

\[
\lambda(E) = \frac{E}{E_p^2 [\beta \ln(\gamma E) - (C/E) + (D/E^2)]}
\]

where $E_p$ is the free-electron plasmon energy and $\beta, \gamma, C, D$ are
material-dependent parameters.
