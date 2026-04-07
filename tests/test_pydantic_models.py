"""
Tests básicos para modelos Pydantic de XPS Analyzer.

Verifica validación automática y funcionalidad de los nuevos modelos
migrados desde dataclasses a Pydantic BaseModel.
"""

import numpy as np
import pytest

from xps_analyzer.models.reference import (
    PhotoelectronLine,
    CompoundReference,
    ElementReference,
    ReferenceDatabase,
)
from xps_analyzer.models.analysis import PeakParameters, FitResult


class TestPhotoelectronLine:
    """Tests para PhotoelectronLine Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de línea fotoeléctrica."""
        line = PhotoelectronLine(
            line="1s", binding_energy=284.8, x_ray_source="Al_Ka", type="core"
        )

        assert line.line == "1s"
        assert line.binding_energy == 284.8
        assert line.x_ray_source == "Al_Ka"
        assert line.type == "core"
        assert line.kinetic_energy is None

    def test_auger_line_requires_kinetic_energy(self):
        """Test que líneas Auger requieren energía cinética."""
        with pytest.raises(ValueError, match="Líneas Auger requieren kinetic_energy"):
            PhotoelectronLine(line="KLL", binding_energy=1200.0, type="Auger")

    def test_negative_binding_energy_fails(self):
        """Test que energías negativas fallan."""
        with pytest.raises(ValueError):
            PhotoelectronLine(line="1s", binding_energy=-100.0)

    def test_empty_line_fails(self):
        """Test que líneas vacías fallan."""
        with pytest.raises(ValueError, match="line no puede estar vacía"):
            PhotoelectronLine(line="   ", binding_energy=284.8)

    def test_invalid_type_fails(self):
        """Test que tipos inválidos fallan."""
        with pytest.raises(ValueError):
            PhotoelectronLine(line="1s", binding_energy=284.8, type="invalid")


class TestCompoundReference:
    """Tests para CompoundReference Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de referencia de compuesto."""
        compound = CompoundReference(
            orbital="1s",
            binding_energy_range=(284.0, 289.0),
            peak_position=286.5,
            chemical_shift=2.1,
        )

        assert compound.orbital == "1s"
        assert compound.binding_energy_range == (284.0, 289.0)
        assert compound.peak_position == 286.5
        assert compound.chemical_shift == 2.1

    def test_invalid_energy_range_fails(self):
        """Test que rangos inválidos fallan."""
        with pytest.raises(ValueError, match="min_energy .* debe ser menor"):
            CompoundReference(
                orbital="1s",
                binding_energy_range=(289.0, 284.0),  # min > max
            )

    def test_peak_outside_range_fails(self):
        """Test que picos fuera del rango fallan."""
        with pytest.raises(ValueError, match="peak_position .* debe estar en el rango"):
            CompoundReference(
                orbital="1s",
                binding_energy_range=(284.0, 289.0),
                peak_position=295.0,  # Fuera del rango
            )

    def test_negative_energies_fail(self):
        """Test que energías negativas fallan."""
        with pytest.raises(ValueError, match="deben ser positivas"):
            CompoundReference(orbital="1s", binding_energy_range=(-10.0, 5.0))


class TestElementReference:
    """Tests para ElementReference Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de referencia de elemento."""
        c1s_line = PhotoelectronLine(line="1s", binding_energy=284.8)

        element = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s_line],
            compounds={},
            binding_energy_most_useful=284.8,
        )

        assert element.symbol == "C"
        assert element.element == "Carbon"
        assert element.atomic_number == 6
        assert len(element.photoelectron_lines) == 1
        assert element.binding_energy_most_useful == 284.8

    def test_invalid_atomic_number_fails(self):
        """Test que números atómicos inválidos fallan."""
        with pytest.raises(ValueError):
            ElementReference(
                symbol="C",
                element="Carbon",
                atomic_number=0,  # Inválido
                photoelectron_lines=[
                    PhotoelectronLine(line="1s", binding_energy=284.8)
                ],
                compounds={},
            )

    def test_inconsistent_symbol_atomic_number_fails(self):
        """Test que símbolos inconsistentes con Z fallan."""
        with pytest.raises(ValueError, match="Número atómico inconsistente"):
            ElementReference(
                symbol="C",  # Carbono
                element="Carbon",
                atomic_number=8,  # Oxígeno - inconsistente
                photoelectron_lines=[
                    PhotoelectronLine(line="1s", binding_energy=284.8)
                ],
                compounds={},
            )

    def test_most_useful_energy_not_matching_lines_fails(self):
        """Test que energía más útil sin línea correspondiente falla."""
        with pytest.raises(ValueError, match="no corresponde a ninguna línea"):
            ElementReference(
                symbol="C",
                element="Carbon",
                atomic_number=6,
                photoelectron_lines=[
                    PhotoelectronLine(line="1s", binding_energy=284.8)
                ],
                compounds={},
                binding_energy_most_useful=500.0,  # No hay línea cerca
            )

    def test_empty_photoelectron_lines_fails(self):
        """Test que elementos sin líneas fallan."""
        with pytest.raises(ValueError):
            ElementReference(
                symbol="C",
                element="Carbon",
                atomic_number=6,
                photoelectron_lines=[],  # Vacía
                compounds={},
            )

    def test_get_main_line_with_most_useful(self):
        """Test obtención de línea principal con most_useful."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        c2s = PhotoelectronLine(line="2s", binding_energy=200.0)

        element = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s, c2s],
            compounds={},
            binding_energy_most_useful=284.8,
        )

        main_line = element.get_main_line()
        assert main_line.line == "1s"
        assert main_line.binding_energy == 284.8

    def test_get_line_by_orbital(self):
        """Test búsqueda por orbital específico."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        c2s = PhotoelectronLine(line="2s", binding_energy=200.0)

        element = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s, c2s],
            compounds={},
        )

        line_1s = element.get_line_by_orbital("1s")
        assert line_1s is not None
        assert line_1s.binding_energy == 284.8

        line_nonexistent = element.get_line_by_orbital("3p")
        assert line_nonexistent is None


class TestPeakParameters:
    """Tests para PeakParameters Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de parámetros de pico."""
        params = PeakParameters(
            position=284.8, amplitude=1000.0, width=1.2, area=1500.0, shape="gaussian"
        )

        assert params.position == 284.8
        assert params.amplitude == 1000.0
        assert params.width == 1.2
        assert params.area == 1500.0
        assert params.shape == "gaussian"

    def test_voigt_requires_gamma(self):
        """Test que perfiles Voigt requieren gamma."""
        with pytest.raises(ValueError, match="Perfil Voigt requiere parámetro gamma"):
            PeakParameters(
                position=284.8,
                amplitude=1000.0,
                width=1.2,
                area=1500.0,
                shape="voigt",  # Sin gamma
            )

    def test_negative_parameters_fail(self):
        """Test que parámetros negativos fallan."""
        with pytest.raises(ValueError):
            PeakParameters(
                position=-284.8,  # Negativa
                amplitude=1000.0,
                width=1.2,
                area=1500.0,
                shape="gaussian",
            )

    def test_inconsistent_area_fails(self):
        """Test que áreas inconsistentes fallan."""
        with pytest.raises(ValueError, match="Área .* inconsistente"):
            PeakParameters(
                position=284.8,
                amplitude=1000.0,
                width=1.2,
                area=1.0,  # Muy pequeña para la amplitud/ancho
                shape="gaussian",
            )


class TestFitResult:
    """Tests para FitResult Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de resultado de ajuste."""
        peak = PeakParameters(
            position=284.8, amplitude=1000.0, width=1.2, area=1500.0, shape="gaussian"
        )

        result = FitResult(
            peaks=[peak],
            fitted_spectrum=np.array([100.0, 200.0, 150.0]),
            residual=np.array([5.0, -2.0, 1.0]),
            r_squared=0.95,
            chi_squared=1.2,
            success=True,
            message="Ajuste convergió exitosamente",
        )

        assert len(result.peaks) == 1
        assert len(result.fitted_spectrum) == 3
        assert len(result.residual) == 3
        assert result.r_squared == 0.95
        assert result.success is True

    def test_empty_peaks_fails(self):
        """Test que lista vacía de picos falla."""
        with pytest.raises(ValueError):
            FitResult(
                peaks=[],  # Vacía
                fitted_spectrum=np.array([100.0, 200.0]),
                residual=np.array([5.0, -2.0]),
                r_squared=0.95,
                chi_squared=1.2,
                success=True,
                message="Test",
            )

    def test_mismatched_array_lengths_fail(self):
        """Test que arrays de distinta longitud fallan."""
        peak = PeakParameters(
            position=284.8, amplitude=1000.0, width=1.2, area=1500.0, shape="gaussian"
        )

        with pytest.raises(ValueError):
            FitResult(
                peaks=[peak],
                fitted_spectrum=np.array([100.0, 200.0, 150.0]),
                residual=np.array([5.0, -2.0]),  # Longitud diferente
                r_squared=0.95,
                chi_squared=1.2,
                success=True,
                message="Test",
            )

    def test_invalid_r_squared_fails(self):
        """Test que R² inválido falla."""
        peak = PeakParameters(
            position=284.8, amplitude=1000.0, width=1.2, area=1500.0, shape="gaussian"
        )

        with pytest.raises(ValueError):
            FitResult(
                peaks=[peak],
                fitted_spectrum=np.array([100.0]),
                residual=np.array([5.0]),
                r_squared=1.5,  # > 1.0
                chi_squared=1.2,
                success=True,
                message="Test",
            )


class TestReferenceDatabase:
    """Tests para ReferenceDatabase Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de base de datos."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )

        db = ReferenceDatabase(
            elements={"C": carbon}, version="1.0", source="Test Database"
        )

        assert len(db.elements) == 1
        assert "C" in db.elements
        assert db.version == "1.0"
        assert db.source == "Test Database"

    def test_empty_elements_fails(self):
        """Test que base de datos vacía falla."""
        with pytest.raises(ValueError):
            ReferenceDatabase(
                elements={},  # Vacía
                version="1.0",
                source="Test",
            )

    def test_inconsistent_symbol_fails(self):
        """Test que símbolos inconsistentes fallan."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )

        with pytest.raises(ValueError, match="Inconsistencia de símbolo"):
            ReferenceDatabase(
                elements={"O": carbon},  # Clave "O" pero element.symbol="C"
                version="1.0",
                source="Test",
            )

    def test_duplicate_atomic_numbers_fails(self):
        """Test que números atómicos duplicados fallan."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        carbon1 = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )
        carbon2 = ElementReference(
            symbol="C2",  # Símbolo diferente
            element="Carbon Isotope",
            atomic_number=6,  # Mismo número atómico
            photoelectron_lines=[c1s],
            compounds={},
        )

        with pytest.raises(ValueError, match="Número atómico duplicado"):
            ReferenceDatabase(
                elements={"C": carbon1, "C2": carbon2}, version="1.0", source="Test"
            )

    def test_get_element(self):
        """Test obtención de elemento por símbolo."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )

        db = ReferenceDatabase(elements={"C": carbon}, version="1.0", source="Test")

        # Case-insensitive
        assert db.get_element("C") is not None
        assert db.get_element("c") is not None
        assert db.get_element("C").symbol == "C"
        assert db.get_element("O") is None

    def test_search_by_binding_energy(self):
        """Test búsqueda por energía de enlace."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        o1s = PhotoelectronLine(line="1s", binding_energy=531.0)

        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )
        oxygen = ElementReference(
            symbol="O",
            element="Oxygen",
            atomic_number=8,
            photoelectron_lines=[o1s],
            compounds={},
        )

        db = ReferenceDatabase(
            elements={"C": carbon, "O": oxygen}, version="1.0", source="Test"
        )

        # Búsqueda exacta
        matches = db.search_by_binding_energy(284.8, tolerance=0.1)
        assert ("C", "1s") in matches
        assert len(matches) == 1

        # Búsqueda con tolerancia
        matches = db.search_by_binding_energy(285.0, tolerance=1.0)
        assert ("C", "1s") in matches

    def test_invalid_search_parameters_fail(self):
        """Test que parámetros inválidos de búsqueda fallan."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )

        db = ReferenceDatabase(elements={"C": carbon}, version="1.0", source="Test")

        with pytest.raises(ValueError, match="energy debe ser positiva"):
            db.search_by_binding_energy(-100.0)

        with pytest.raises(ValueError, match="tolerance debe ser positiva"):
            db.search_by_binding_energy(284.8, tolerance=-1.0)

    def test_list_elements_ordered(self):
        """Test que elementos se listen ordenados por Z."""
        h1s = PhotoelectronLine(line="1s", binding_energy=13.6)  # Hidrógeno realista
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)

        hydrogen = ElementReference(
            symbol="H",
            element="Hydrogen",
            atomic_number=1,
            photoelectron_lines=[h1s],
            compounds={},
        )
        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s],
            compounds={},
        )

        db = ReferenceDatabase(
            elements={"C": carbon, "H": hydrogen},  # Orden aleatorio
            version="1.0",
            source="Test",
        )

        elements = db.list_elements()
        assert elements == ["H", "C"]  # Ordenados por Z

    def test_get_statistics(self):
        """Test estadísticas de base de datos."""
        c1s = PhotoelectronLine(line="1s", binding_energy=284.8)
        c2s = PhotoelectronLine(line="2s", binding_energy=200.0)

        oxide_compound = CompoundReference(
            orbital="1s", binding_energy_range=(286.0, 290.0)
        )

        carbon = ElementReference(
            symbol="C",
            element="Carbon",
            atomic_number=6,
            photoelectron_lines=[c1s, c2s],
            compounds={"oxide": oxide_compound},
        )

        db = ReferenceDatabase(elements={"C": carbon}, version="1.0", source="Test")

        stats = db.get_statistics()
        assert stats["total_elements"] == 1
        assert stats["total_photoelectron_lines"] == 2
        assert stats["total_compounds"] == 1
        assert stats["elements_with_compounds"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
