from dataclasses import dataclass
from typing import Dict

import pyformlang

from project.ecfg import ECFG
from project.fa_utils import nfa_from_data

__all__ = ["RSM"]


@dataclass
class RSM:
    start_symbol: pyformlang.cfg.Variable
    boxes: Dict[pyformlang.cfg.Variable, pyformlang.finite_automaton.EpsilonNFA]

    def minimize(self) -> "RSM":
        minimized_rsm = RSM(start_symbol=self.start_symbol, boxes=dict())
        for var, fa in self.boxes.items():
            minimized_rsm.boxes[var] = fa.minimize()
        return minimized_rsm

    def merge_boxes_to_single_nfa(self) -> pyformlang.finite_automaton.EpsilonNFA:
        result = pyformlang.finite_automaton.EpsilonNFA()
        for var, fa in self.boxes.items():
            for state in fa.start_states:
                result.add_start_state(
                    pyformlang.finite_automaton.State((var, state.value))
                )
            for state in fa.final_states:
                result.add_final_state(
                    pyformlang.finite_automaton.State((var, state.value))
                )
            for (start, symbol, finish) in fa:
                result.add_transition(
                    pyformlang.finite_automaton.State((var, start)),
                    symbol,
                    pyformlang.finite_automaton.State((var, finish)),
                )
        return result

    @staticmethod
    def from_ecfg(ecfg: ECFG) -> "RSM":
        return RSM(
            start_symbol=ecfg.start_symbol,
            boxes={
                var: regex.to_epsilon_nfa() for var, regex in ecfg.productions.items()
            },
        )

    @staticmethod
    def from_data(data: dict) -> "RSM":
        return RSM(
            start_symbol=pyformlang.cfg.Variable(
                data["start"] if "start" in data else None
            ),
            boxes={
                pyformlang.cfg.Variable(var): nfa_from_data(fa)
                for var, fa in data["boxes"].items()
            }
            if "boxes" in data
            else dict(),
        )
