from collections import defaultdict
from collections import deque
from typing import Deque
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple

import pyformlang
import networkx as nx

from project.cfg_utils import cfg_to_weak_normal_form

__all__ = ["filter_cfpq_result", "filtered_cfpq_with_hellings"]


def filter_cfpq_result(
    cfpq_result: Set[Tuple[int, pyformlang.cfg.Variable, int]],
    cfg: pyformlang.cfg.CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple[int, int]]:
    return {
        (start, finish)
        for (start, var, finish) in cfpq_result
        if var == cfg.start_symbol
        and (start_nodes is None or start in start_nodes)
        and (final_nodes is None or finish in final_nodes)
    }


def _cfpq_with_hellings(
    cfg: pyformlang.cfg.CFG, graph: nx.DiGraph
) -> Set[Tuple[int, pyformlang.cfg.Variable, int]]:
    cfg = cfg_to_weak_normal_form(cfg)

    var_production_body_to_head: Dict[
        Tuple[pyformlang.cfg.Variable, pyformlang.cfg.Variable],
        Set[pyformlang.cfg.Variable],
    ] = defaultdict(set)

    result: Set[Tuple[int, pyformlang.cfg.Variable, int]] = set()

    # dictionaries letting to iterate over `result` elements
    # with specified first or last component
    start_to_var_and_finish_pairs: Dict[
        int, Set[Tuple[pyformlang.cfg.Variable, int]]
    ] = defaultdict(set)
    finish_to_start_and_var_pairs: Dict[
        int, Set[Tuple[int, pyformlang.cfg.Variable]]
    ] = defaultdict(set)

    unhandled: Deque[Tuple[int, pyformlang.cfg.Variable, int]] = deque()

    def register_reachability(start, var, finish):
        triple = (start, var, finish)
        if triple not in result:
            result.add(triple)
            unhandled.append(triple)
            start_to_var_and_finish_pairs[start].add((var, finish))
            finish_to_start_and_var_pairs[finish].add((start, var))

    edges_grouped_by_label: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    for (start, finish, attributes) in graph.edges.data():
        edges_grouped_by_label[attributes["label"]].append((start, finish))

    for production in cfg.productions:
        if (
            len(production.body) == 0
            or len(production.body) == 1
            and isinstance(production.body[0], pyformlang.cfg.Epsilon)
        ):
            for node in graph.nodes:
                register_reachability(node, production.head, node)
        elif len(production.body) == 1 and isinstance(
            production.body[0], pyformlang.cfg.Terminal
        ):
            for (start, finish) in edges_grouped_by_label[production.body[0].value]:
                register_reachability(start, production.head, finish)
        else:
            assert (
                len(production.body) == 2
                and isinstance(production.body[0], pyformlang.cfg.Variable)
                and isinstance(production.body[1], pyformlang.cfg.Variable)
            )
            var_production_body_to_head[(production.body[0], production.body[1])].add(
                production.head
            )

    while unhandled:
        (node1, var1, node2) = unhandled.popleft()
        for (start, var, finish) in [
            (node0, var, node2)
            for (node0, var0) in finish_to_start_and_var_pairs[node1]
            for var in var_production_body_to_head[(var0, var1)]
        ] + [
            (node1, var, node3)
            for (var2, node3) in start_to_var_and_finish_pairs[node2]
            for var in var_production_body_to_head[(var1, var2)]
        ]:
            register_reachability(start, var, finish)
    return result


def filtered_cfpq_with_hellings(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple[int, int]]:
    return filter_cfpq_result(
        _cfpq_with_hellings(cfg, graph), cfg, start_nodes, final_nodes
    )
