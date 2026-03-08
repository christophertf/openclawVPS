import pytest

from app.gates.evidentiary_gate import validate_claims


def test_gate_blocks_bad_claims():
    with pytest.raises(ValueError):
        validate_claims(["criminal_fraud"])
