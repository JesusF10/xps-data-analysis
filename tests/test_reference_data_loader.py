import pytest
import json
from xps_analyzer.reference_data.elements import (
    load_reference_database,
    _dict_to_element_reference,
    _reference_db_cache
)

def test_load_reference_database(tmp_path, monkeypatch):
    import xps_analyzer.reference_data.elements as elem_module
    monkeypatch.setattr(elem_module, "_reference_db_cache", None)
    
    data = {
        "version": "1.0",
        "source": "Test",
        "elements": {
            "C": {
                "atomic_number": 6,
                "symbol": "C",
                "element": "Carbon",
                "line_positions": {
                    "1s": [{"line": "1s", "binding_energy_eV": 284.8}],
                    "auger": [{"line": "auger", "kinetic_energy_eV": 250.0}]
                },
                "chemical_state_data": [
                    {
                        "compound_type": "C-C",
                        "orbital": "1s",
                        "binding_energy_eV": [284.8, 285.0],
                        "peak_position_eV": 284.8,
                        "chemical_shift_eV": 0.0
                    }
                ],
                "useful_lines": ["1s"]
            }
        }
    }
    
    json_path = tmp_path / "test_ref.json"
    json_path.write_text(json.dumps(data))
    
    db = load_reference_database(data_path=json_path)
    assert db.version == "1.0"
    assert "C" in db.elements
    
    db2 = load_reference_database(data_path=json_path)
    assert db2 is db
    
    monkeypatch.setattr(elem_module, "_reference_db_cache", None)
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{bad json")
    db_bad = load_reference_database(data_path=bad_json)
    assert len(db_bad.elements) == 0

    monkeypatch.setattr(elem_module, "_reference_db_cache", None)
    # default path coverage
    # we don't assert anything, just make sure it loads (or fails cleanly)
    db_def = load_reference_database()
    assert isinstance(db_def.elements, dict)

def test_dict_to_element_reference_defaults():
    data = {
        "atomic_number": 1,
        "symbol": "H",
        "element": "Hydrogen"
    }
    elem = _dict_to_element_reference(data)
    assert elem.atomic_number == 1
    assert len(elem.photoelectron_lines) == 0
    assert len(elem.compounds) == 0
