import json
from os import PathLike
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple

import pyformlang.cfg

__all__ = [
    "cfg_to_weak_normal_form",
    "is_generated_by_cfg",
    "cfg_from_data",
    "read_cfg",
]


def cfg_to_weak_normal_form(cfg: pyformlang.cfg.CFG) -> pyformlang.cfg.CFG:
    # temporarily replace epsilon with a placeholder terminal
    # so `to_normal_form()` works as `to_weak_normal_form()`
    epsilon_placeholder = pyformlang.cfg.Terminal("CFG#EpsilonPlaceholder")
    while epsilon_placeholder in cfg.terminals or epsilon_placeholder in cfg.variables:
        epsilon_placeholder = pyformlang.cfg.Terminal(epsilon_placeholder.value + "_")
    cfg = pyformlang.cfg.CFG(
        start_symbol=cfg.start_symbol,
        productions={
            pyformlang.cfg.Production(
                production.head,
                [
                    epsilon_placeholder
                    if isinstance(cfg_object, pyformlang.cfg.Epsilon)
                    else cfg_object
                    for cfg_object in production.body
                ]
                if len(production.body) > 0
                else [epsilon_placeholder],
            )
            for production in cfg.productions
        },
    )
    cfg = cfg.to_normal_form()
    return pyformlang.cfg.CFG(
        start_symbol=cfg.start_symbol,
        productions={
            pyformlang.cfg.Production(
                production.head,
                [
                    pyformlang.cfg.Epsilon()
                    if cfg_object == epsilon_placeholder
                    else cfg_object
                    for cfg_object in production.body
                ],
            )
            for production in cfg.productions
        },
    )


def is_generated_by_cfg(
    cfg: pyformlang.cfg.CFG, word: List[pyformlang.cfg.Terminal] | str
) -> bool:
    if isinstance(word, str):
        word = [pyformlang.cfg.Terminal(ch) for ch in word]
    if len(word) == 0:
        return cfg.generate_epsilon()
    cfg = cfg.to_normal_form()
    var_to_idx = {var: i for (i, var) in enumerate(cfg.variables)}
    start_symbol_idx = var_to_idx[cfg.start_symbol]
    terminal_productions: Dict[int, Set[pyformlang.cfg.Terminal]] = dict()
    variable_productions: List[Tuple[int, int, int]] = []
    for production in cfg.productions:
        head_idx = var_to_idx[production.head]
        match len(production.body):
            case 1:
                terminal_productions.setdefault(head_idx, set()).add(production.body[0])
            case 2:
                variable_productions.append(
                    (
                        head_idx,
                        var_to_idx[production.body[0]],
                        var_to_idx[production.body[1]],
                    )
                )
    is_generated = [
        [
            [
                start_idx == end_idx
                and var_idx in terminal_productions
                and word[start_idx] in terminal_productions[var_idx]
                for var_idx in range(len(cfg.variables))
            ]
            for end_idx in range(len(word))
        ]
        for start_idx in range(len(word))
    ]
    for substr_len in range(2, len(word) + 1):
        for end_idx in range(substr_len - 1, len(word)):
            start_idx = end_idx - substr_len + 1
            for mid_idx in range(start_idx, end_idx):
                for (
                    head_var_idx,
                    body_var_idx1,
                    body_var_idx2,
                ) in variable_productions:
                    is_generated[start_idx][end_idx][head_var_idx] = is_generated[
                        start_idx
                    ][end_idx][head_var_idx] or (
                        is_generated[start_idx][mid_idx][body_var_idx1]
                        and is_generated[mid_idx + 1][end_idx][body_var_idx2]
                    )
    return is_generated[0][len(word) - 1][start_symbol_idx]


def cfg_from_data(data: dict) -> pyformlang.cfg.CFG:
    return pyformlang.cfg.CFG.from_text(
        start_symbol=pyformlang.cfg.Variable(
            data["start"] if "start" in data else None
        ),
        text=data["productions"] if "productions" in data else "",
    )


def read_cfg(path: PathLike) -> pyformlang.cfg.CFG:
    with open(path, "r") as fs:
        return cfg_from_data(json.load(fs))
