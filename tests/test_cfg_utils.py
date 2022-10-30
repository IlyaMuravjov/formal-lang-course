from pathlib import Path

import pyformlang.cfg
import pytest

from project.cfg_utils import cfg_to_weak_normal_form
from project.cfg_utils import cfg_from_data
from project.cfg_utils import read_cfg
from tests.utils import assert_equal_cfgs


# Not loading test data from json here because data loading itself is being tested
# Otherwise test would have to reimplement tested function
@pytest.mark.parametrize(
    "input,expected_output",
    [
        ("{}", pyformlang.cfg.CFG()),
        ('{"productions": ""}', pyformlang.cfg.CFG()),
        (
            '{"productions": "S -> a b"}',
            pyformlang.cfg.CFG(
                productions={
                    pyformlang.cfg.Production(
                        pyformlang.cfg.Variable("S"),
                        [pyformlang.cfg.Terminal("a"), pyformlang.cfg.Terminal("b")],
                    )
                }
            ),
        ),
        (
            '{"start": "S"}',
            pyformlang.cfg.CFG(start_symbol=pyformlang.cfg.Variable("S")),
        ),
        (
            '{"start": "S", "productions": "S -> A b | epsilon \\n A -> a S a"}',
            pyformlang.cfg.CFG(
                start_symbol=pyformlang.cfg.Variable("S"),
                productions={
                    pyformlang.cfg.Production(
                        pyformlang.cfg.Variable("S"),
                        [pyformlang.cfg.Variable("A"), pyformlang.cfg.Terminal("b")],
                    ),
                    pyformlang.cfg.Production(
                        pyformlang.cfg.Variable("S"), [pyformlang.cfg.Epsilon()]
                    ),
                    pyformlang.cfg.Production(
                        pyformlang.cfg.Variable("A"),
                        [
                            pyformlang.cfg.Terminal("a"),
                            pyformlang.cfg.Variable("S"),
                            pyformlang.cfg.Terminal("a"),
                        ],
                    ),
                },
            ),
        ),
    ],
)
def test_read_cfg(input: str, expected_output: pyformlang.cfg.CFG, tmp_path: Path):
    input_file_path = tmp_path / "cfg.json"
    with open(input_file_path, "w") as fs:
        fs.write(input)
    actual_output = read_cfg(input_file_path)
    assert_equal_cfgs(actual_output, expected_output)


def test_cfg_to_weak_normal_form(config_data: dict):
    assert_equal_cfgs(
        cfg_to_weak_normal_form(cfg_from_data(config_data["cfg"])),
        cfg_from_data(config_data["expected-result"]),
    )
