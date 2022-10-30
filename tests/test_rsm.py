from project.ecfg import ECFG
from project.rsm import RSM
from tests.utils import assert_definitely_equivalent_rsms


def test_factory_methods(config_data: dict):
    assert_definitely_equivalent_rsms(
        RSM.from_ecfg(ECFG.from_data(config_data["ecfg"])),
        RSM.from_data(config_data["rsm"]),
    )


def test_minimize(config_data: dict):
    actual_rsm = RSM.from_data(config_data["rsm"]).minimize()
    expected_rsm = RSM.from_data(config_data["minimized-rsm"])
    assert_definitely_equivalent_rsms(actual_rsm, expected_rsm)
    for var, fa in actual_rsm.boxes.items():
        assert fa.is_deterministic()
        assert len(fa.states) == len(expected_rsm.boxes[var].states)
