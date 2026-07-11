# Energy Calibration

The `preprocessing` module corrects the binding energy axis using a reference peak
of known position. This compensates for charging effects and instrument drift.

## Theory

XPS binding energies are referenced to the Fermi level. Surface charging in insulating
samples causes an offset $\Delta E$ that must be corrected:

\[
E_b^{\text{(corrected)}} = E_b^{\text{(measured)}} + \Delta E
\]

where:

\[
\Delta E = E_{\text{ref}}^{\text{(literature)}} - E_{\text{ref}}^{\text{(observed)}}
\]

Common reference peaks:

| Reference | Literature Energy (eV) |
|-----------|----------------------|
| C 1s (adventitious) | 284.8 |
| Au 4f$\_{7/2}$ | 84.0 |
| Ag 3d$\_{5/2}$ | 368.2 |
| Cu 2p$\_{3/2}$ | 932.7 |

## API Reference

### calibrate_spectrum

```python
from xps_analyzer.preprocessing import calibrate_spectrum

calibrated = calibrate_spectrum(
    spectrum=c1s,
    reference_element="C 1s",
    reference_energy=284.8
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `spectrum` | `XPSSpectrum` | Spectrum to calibrate |
| `reference_element` | `str` | Region name of the reference peak |
| `reference_energy` | `float` | Literature binding energy in eV |

**Returns:** A new `XPSSpectrum` with shifted energy axis.

### calibrate_sample

```python
from xps_analyzer.preprocessing import calibrate_sample

calibrated_sample = calibrate_sample(
    sample=sample,
    reference_element="C 1s",
    reference_energy=284.8
)
```

Applies `calibrate_spectrum` to all spectra in a dataset or sample, propagating the
same energy shift throughout.
