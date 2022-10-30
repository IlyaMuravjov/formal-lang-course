import json
from os import PathLike

import pyformlang.cfg

__all__ = ["cfg_to_weak_normal_form", "cfg_from_data", "read_cfg"]


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
