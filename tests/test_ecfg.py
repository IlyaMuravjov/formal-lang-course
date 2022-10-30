from project.cfg_utils import cfg_from_data
from project.ecfg import ECFG
from tests.utils import assert_definitely_equivalent_ecfgs


def test_factory_methods(config_data: dict):
    assert_definitely_equivalent_ecfgs(
        ECFG.from_cfg(cfg_from_data(config_data["cfg"])),
        ECFG.from_data(config_data["ecfg"]),
    )
