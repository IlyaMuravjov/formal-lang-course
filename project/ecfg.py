from dataclasses import dataclass
from typing import Dict
from typing import Set

import pyformlang.cfg

__all__ = ["ECFG"]


@dataclass
class ECFG:
    start_symbol: pyformlang.cfg.Variable
    productions: Dict[pyformlang.cfg.Variable, pyformlang.regular_expression.Regex]

    @property
    def variables(self) -> Set[pyformlang.cfg.Variable]:
        return set(self.productions.keys())

    @staticmethod
    def from_cfg(cfg: pyformlang.cfg.CFG) -> "ECFG":
        new_productions: Dict[
            pyformlang.cfg.Variable, pyformlang.regular_expression.Regex
        ] = dict()
        for production in cfg.productions:
            regex = pyformlang.regular_expression.Regex(
                " ".join(
                    "$" if isinstance(obj, pyformlang.cfg.Epsilon) else obj.value
                    for obj in production.body
                )
                if len(production.body) > 0
                else "$"
            )
            new_productions[production.head] = (
                new_productions[production.head].union(regex)
                if production.head in new_productions
                else regex
            )
        return ECFG(start_symbol=cfg.start_symbol, productions=new_productions)

    @staticmethod
    def from_data(data: dict):
        return ECFG(
            start_symbol=pyformlang.cfg.Variable(
                data["start"] if "start" in data else None
            ),
            productions={
                pyformlang.cfg.Variable(var): pyformlang.regular_expression.Regex(regex)
                for var, regex in data["productions"].items()
            }
            if "productions" in data
            else dict(),
        )

    @staticmethod
    def from_productions(productions: Dict[str, str]):
        return ECFG(
            start_symbol=pyformlang.cfg.Variable("S"),
            productions={
                pyformlang.cfg.Variable(var): pyformlang.regular_expression.Regex(regex)
                for var, regex in productions.items()
            },
        )
