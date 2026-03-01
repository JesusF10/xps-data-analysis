"""
Tests para el módulo de datos de referencia XPS.
"""

from xps_analyzer.reference_data.elements import (
    CompoundReference,
    ElementReference,
    PhotoelectronLine,
    ReferenceDatabase,
)
from xps_analyzer.reference_data.identification import (
    _calculate_confidence,
    find_peaks_in_spectrum,
    identify_peaks,
    suggest_compounds,
)

import pytest

# ==================== Fixtures ====================


@pytest.fixture
def simple_photoelectron_line():
    """Crea una línea fotoeléctrica simple para testing."""
    return PhotoelectronLine(
        line="1s",
        binding_energy=284.8,
        x_ray_source="Al_Ka",
        type="core",
        kinetic_energy=None,
    )


@pytest.fixture
def simple_compound():
    """Crea una referencia de compuesto simple."""
    return CompoundReference(
        orbital="1s",
        binding_energy_range=(283.0, 286.0),
        peak_position=285.5,
        chemical_shift=0.7,
    )


@pytest.fixture
def carbon_element():
    """Crea un elemento Carbon con múltiples líneas."""
    return ElementReference(
        symbol="C",
        element="Carbon",
        atomic_number=6,
        photoelectron_lines=[
            PhotoelectronLine(
                line="1s", binding_energy=284.8, x_ray_source="Al_Ka", type="core"
            ),
            PhotoelectronLine(
                line="2s", binding_energy=24.0, x_ray_source="Al_Ka", type="core"
            ),
        ],
        compounds={
            "C-C": CompoundReference(
                orbital="1s",
                binding_energy_range=(284.0, 285.0),
                peak_position=284.8,
                chemical_shift=0.0,
            ),
            "C-O": CompoundReference(
                orbital="1s",
                binding_energy_range=(285.5, 286.5),
                peak_position=286.0,
                chemical_shift=1.2,
            ),
        },
        binding_energy_most_useful=284.8,
        spin_orbital_splitting=None,
    )


@pytest.fixture
def oxygen_element():
    """Crea un elemento Oxygen con una línea."""
    return ElementReference(
        symbol="O",
        element="Oxygen",
        atomic_number=8,
        photoelectron_lines=[
            PhotoelectronLine(
                line="1s", binding_energy=531.0, x_ray_source="Al_Ka", type="core"
            ),
        ],
        compounds={
            "O2": CompoundReference(
                orbital="1s",
                binding_energy_range=(530.0, 532.0),
                peak_position=531.0,
                chemical_shift=0.0,
            ),
        },
        binding_energy_most_useful=531.0,
    )


@pytest.fixture
def simple_database(carbon_element, oxygen_element):
    """Crea una base de datos simple con C y O."""
    return ReferenceDatabase(
        elements={"C": carbon_element, "O": oxygen_element},
        version="1.0-test",
        source="Test Database",
    )


# ==================== Tests para PhotoelectronLine ====================


def test_photoelectron_line_creation(simple_photoelectron_line):
    """Test creación básica de línea fotoeléctrica."""
    assert simple_photoelectron_line.line == "1s"
    assert simple_photoelectron_line.binding_energy == 284.8
    assert simple_photoelectron_line.x_ray_source == "Al_Ka"
    assert simple_photoelectron_line.type == "core"


def test_photoelectron_line_with_kinetic_energy():
    """Test línea Auger con energía cinética."""
    auger_line = PhotoelectronLine(
        line="KLL",
        binding_energy=0.0,
        x_ray_source="Al_Ka",
        type="auger",
        kinetic_energy=1220.0,
    )
    assert auger_line.type == "auger"
    assert auger_line.kinetic_energy == 1220.0


# ==================== Tests para CompoundReference ====================


def test_compound_reference_creation(simple_compound):
    """Test creación de referencia de compuesto."""
    assert simple_compound.orbital == "1s"
    assert simple_compound.binding_energy_range == (283.0, 286.0)
    assert simple_compound.peak_position == 285.5
    assert simple_compound.chemical_shift == 0.7


def test_compound_reference_optional_fields():
    """Test compuesto sin peak_position ni chemical_shift."""
    compound = CompoundReference(
        orbital="2p",
        binding_energy_range=(100.0, 105.0),
    )
    assert compound.peak_position is None
    assert compound.chemical_shift is None


# ==================== Tests para ElementReference ====================


def test_element_reference_creation(carbon_element):
    """Test creación de referencia de elemento."""
    assert carbon_element.symbol == "C"
    assert carbon_element.element == "Carbon"
    assert carbon_element.atomic_number == 6
    assert len(carbon_element.photoelectron_lines) == 2
    assert len(carbon_element.compounds) == 2


def test_get_main_line_with_binding_energy_most_useful(carbon_element):
    """Test get_main_line() retorna PhotoelectronLine correcto."""
    main_line = carbon_element.get_main_line()

    # Debe ser PhotoelectronLine, no float
    assert isinstance(main_line, PhotoelectronLine)
    assert main_line.binding_energy == 284.8
    assert main_line.line == "1s"


def test_get_main_line_without_binding_energy_most_useful():
    """Test get_main_line() con binding_energy_most_useful=None."""
    element = ElementReference(
        symbol="N",
        element="Nitrogen",
        atomic_number=7,
        photoelectron_lines=[
            PhotoelectronLine(line="1s", binding_energy=399.0, type="core"),
        ],
        compounds={},
        binding_energy_most_useful=None,  # Sin valor
    )

    # Debe retornar la primera línea como fallback
    main_line = element.get_main_line()
    assert isinstance(main_line, PhotoelectronLine)
    assert main_line.binding_energy == 399.0


def test_get_main_line_raises_error_no_lines():
    """Test get_main_line() lanza error si no hay líneas."""
    element = ElementReference(
        symbol="X",
        element="Unknown",
        atomic_number=999,
        photoelectron_lines=[],  # Vacío
        compounds={},
    )

    with pytest.raises(ValueError) as excinfo:
        element.get_main_line()

    assert "No hay líneas fotoelectrónicas disponibles" in str(excinfo.value)


def test_get_compound(carbon_element):
    """Test búsqueda de compuesto por nombre."""
    compound = carbon_element.get_compound("C-O")
    assert compound is not None
    assert compound.peak_position == 286.0
    assert compound.chemical_shift == 1.2


def test_get_compound_not_found(carbon_element):
    """Test get_compound() retorna None si no existe."""
    compound = carbon_element.get_compound("C-N")
    assert compound is None


# ==================== Tests para ReferenceDatabase ====================


def test_reference_database_creation(simple_database):
    """Test creación de base de datos."""
    assert len(simple_database.elements) == 2
    assert "C" in simple_database.elements
    assert "O" in simple_database.elements
    assert simple_database.version == "1.0-test"


def test_get_element(simple_database):
    """Test obtención de elemento por símbolo."""
    carbon = simple_database.get_element("C")
    assert carbon is not None
    assert carbon.symbol == "C"
    assert carbon.atomic_number == 6


def test_get_element_case_insensitive(simple_database):
    """Test búsqueda de elemento es case-insensitive."""
    carbon_lower = simple_database.get_element("c")
    carbon_upper = simple_database.get_element("C")

    assert carbon_lower is not None
    assert carbon_upper is not None
    assert carbon_lower.symbol == carbon_upper.symbol


def test_get_element_not_found(simple_database):
    """Test get_element() retorna None si no existe."""
    nitrogen = simple_database.get_element("N")
    assert nitrogen is None


def test_search_by_binding_energy(simple_database):
    """Test búsqueda por energía de enlace."""
    # Buscar carbono 1s (284.8 eV)
    matches = simple_database.search_by_binding_energy(284.8, tolerance=1.0)

    assert len(matches) > 0
    # Debe encontrar C 1s
    assert ("C", "1s") in matches


def test_search_by_binding_energy_with_tolerance(simple_database):
    """Test búsqueda con diferentes tolerancias."""
    # Tolerancia amplia debe encontrar más matches
    matches_wide = simple_database.search_by_binding_energy(285.0, tolerance=5.0)
    matches_narrow = simple_database.search_by_binding_energy(285.0, tolerance=0.5)

    assert len(matches_wide) >= len(matches_narrow)


def test_search_by_binding_energy_includes_compounds(simple_database):
    """Test búsqueda incluye compuestos con peak_position."""
    # Buscar energía de compuesto C-O (286.0 eV)
    matches = simple_database.search_by_binding_energy(286.0, tolerance=0.5)

    # Debe encontrar el compuesto C-O
    assert ("C", "C-O") in matches


def test_get_chemical_shifts(simple_database):
    """Test obtención de desplazamientos químicos."""
    shifts = simple_database.get_chemical_shifts("C")

    # Debe tener desplazamientos de C-C y C-O
    assert "C-C" in shifts
    assert "C-O" in shifts
    assert shifts["C-C"] == 0.0
    assert shifts["C-O"] == 1.2


def test_get_chemical_shifts_filters_none(simple_database):
    """Test get_chemical_shifts() filtra compuestos sin chemical_shift."""
    # Agregar compuesto sin chemical_shift
    simple_database.elements["C"].compounds["C-H"] = CompoundReference(
        orbital="1s",
        binding_energy_range=(283.0, 284.0),
        peak_position=283.5,
        chemical_shift=None,  # Sin valor
    )

    shifts = simple_database.get_chemical_shifts("C")

    # No debe incluir C-H porque chemical_shift es None
    assert "C-H" not in shifts


def test_get_chemical_shifts_element_not_found(simple_database):
    """Test get_chemical_shifts() retorna dict vacío si elemento no existe."""
    shifts = simple_database.get_chemical_shifts("N")
    assert shifts == {}


def test_list_elements(simple_database):
    """Test listado de elementos disponibles."""
    elements = simple_database.list_elements()
    assert len(elements) == 2
    assert "C" in elements
    assert "O" in elements


# ==================== Tests para identification.py ====================


def test_identify_peaks(simple_database):
    """Test identificación de picos."""
    peak_energies = [284.8, 531.0]

    identifications = identify_peaks(peak_energies, simple_database, tolerance=1.0)

    assert len(identifications) == 2
    assert identifications[0]["peak_position"] == 284.8
    assert len(identifications[0]["possible_matches"]) > 0


def test_identify_peaks_no_matches(simple_database):
    """Test identificación con energías sin matches."""
    peak_energies = [1000.0, 2000.0]  # Energías fuera de rango

    identifications = identify_peaks(peak_energies, simple_database, tolerance=1.0)

    # No debe haber identificaciones
    assert len(identifications) == 0


def test_suggest_compounds(simple_database):
    """Test sugerencia de compuestos."""
    # Buscar compuestos de carbono cerca de 286.0 eV (C-O)
    candidates = suggest_compounds("C", 286.0, simple_database)

    assert len(candidates) > 0
    # Debe estar ordenado por proximidad
    assert candidates[0].peak_position == 286.0


def test_suggest_compounds_element_not_found(simple_database):
    """Test suggest_compounds() retorna lista vacía si elemento no existe."""
    candidates = suggest_compounds("N", 399.0, simple_database)
    assert len(candidates) == 0


def test_suggest_compounds_filters_none_peak_position(simple_database):
    """Test suggest_compounds() filtra compuestos sin peak_position."""
    # Agregar compuesto sin peak_position
    simple_database.elements["C"].compounds["C-unknown"] = CompoundReference(
        orbital="1s",
        binding_energy_range=(280.0, 290.0),
        peak_position=None,  # Sin valor
    )

    candidates = suggest_compounds("C", 285.0, simple_database)

    # No debe incluir C-unknown
    assert all(c.peak_position is not None for c in candidates)


def test_calculate_confidence():
    """Test cálculo de confianza básico."""
    matches = [("C", "1s"), ("O", "1s")]
    confidence = _calculate_confidence(285.0, matches, None)

    assert 0.0 <= confidence <= 1.0
    assert confidence > 0  # Debe haber alguna confianza con matches


def test_calculate_confidence_no_matches():
    """Test confianza es 0 sin matches."""
    confidence = _calculate_confidence(1000.0, [], None)
    assert confidence == 0.0


def test_find_peaks_in_spectrum():
    """Test detección de picos en espectro."""
    # Espectro simple con pico en índice 5
    binding_energy = [280.0, 282.0, 284.0, 286.0, 288.0, 290.0, 292.0]
    intensity = [100.0, 150.0, 200.0, 300.0, 250.0, 500.0, 400.0]

    peaks = find_peaks_in_spectrum(binding_energy, intensity, height_threshold=0.3)

    # Debe encontrar el pico en 290.0 eV (intensidad 500.0)
    assert len(peaks) > 0
    assert 290.0 in peaks
