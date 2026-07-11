# Installation

## Requirements

- Python &ge; 3.10
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

## Using uv (Recommended)

```bash
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis
uv sync --group dev --group jupyter
```

Verify the installation:

```bash
uv run xps-analyzer --version
```

## Using pip

```bash
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis
pip install -e .
pip install -e ".[docs]"   # optional: documentation dependencies
```

## Using conda

```bash
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis
conda env create -f environment.yml
conda activate xps-analysis
pip install -e .
```

## Docker

A Dockerfile is provided for containerized usage:

```bash
docker build -t xps-analyzer .
docker run --rm -v $(pwd)/data:/app/data xps-analyzer xps-analyzer analyze /app/data
```

## Verify Installation

```bash
uv run python verify_installation.py
```

## Dependencies

| Category | Packages |
|----------|----------|
| **Core** | numpy &ge; 1.21, pandas &ge; 1.3, scipy &ge; 1.7, matplotlib &ge; 3.4 |
| **Analysis** | lmfit &ge; 1.0, scikit-learn &ge; 1.0 |
| **Validation** | pydantic &ge; 2.12 |
| **CLI** | click &ge; 8.0, tqdm &ge; 4.60 |
| **GUI** | streamlit &ge; 1.31 |
| **I/O** | openpyxl &ge; 3.1, PyYAML &ge; 6.0 |
| **Dev** | pytest, pytest-cov, ruff, pre-commit |
| **Docs** | mkdocs-material, mkdocstrings |

For detailed installation instructions, see the full [INSTALLATION.md](https://github.com/JesusF10/xps-data-analysis/blob/main/INSTALLATION.md) on GitHub.
