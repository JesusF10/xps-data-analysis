# Contributing

Contributions to XPS Analyzer are welcome. The project is in active development
and follows a structured contribution process.

## Development Priorities

1. GUI interactivity improvements (Streamlit)
2. Advanced visualization (Plotly integration planned)
3. API documentation

## Process

1. **Fork** the repository
2. **Create a feature branch** from `main`
3. **Implement** your changes with tests
4. **Run tests** — all 355 tests must pass
5. **Submit a pull request** with a clear description

## Code Standards

- **Language:** Python &ge; 3.10 with type hints
- **Style:** ruff (line length 88, PEP 8 compatible)
- **Validation:** Pydantic v2 for all data models
- **Immutability:** `model_copy(deep=True)` for spectral modifications
- **Testing:** pytest with coverage > 90%

## Pull Request Guidelines

- Keep PRs focused on single concern
- Include test coverage for new functionality
- Update documentation (API_DOCS.md) if public API changes
- Reference any related issues

## Reporting Issues

Report bugs or feature requests at:
[https://github.com/JesusF10/xps-data-analysis/issues](https://github.com/JesusF10/xps-data-analysis/issues)

---

Full details in [CONTRIBUTING.md](https://github.com/JesusF10/xps-data-analysis/blob/main/CONTRIBUTING.md) on GitHub.
