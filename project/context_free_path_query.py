from collections import defaultdict
from collections import deque
from typing import Deque
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
import itertools

import pyformlang
import networkx as nx

from project.bool_decomposition import BoolDecomposition
from project.cfg_utils import cfg_to_weak_normal_form

__all__ = ["filtered_cfpq_with_hellings", "filtered_cfpq_with_matrix"]


def _filter_cfpq_result(
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
        match production.body:
            case [] | [pyformlang.cfg.Epsilon()]:
                for node in graph.nodes:
                    register_reachability(node, production.head, node)
            case [pyformlang.cfg.Terminal() as terminal]:
                for (start, finish) in edges_grouped_by_label[terminal.value]:
                    register_reachability(start, production.head, finish)
            case [pyformlang.cfg.Variable() as var1, pyformlang.cfg.Variable() as var2]:
                var_production_body_to_head[(var1, var2)].add(production.head)

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
    return _filter_cfpq_result(
        _cfpq_with_hellings(cfg, graph), cfg, start_nodes, final_nodes
    )


def _cfpq_with_matrix(
    cfg: pyformlang.cfg.CFG, graph: nx.DiGraph
) -> Set[Tuple[int, pyformlang.cfg.Variable, int]]:
    cfg = cfg_to_weak_normal_form(cfg)
    terminal_to_generating_vars: Dict[str, List[pyformlang.cfg.Variable]] = defaultdict(
        list
    )
    vars_generating_epsilon: List[pyformlang.cfg.Variable] = []
    variable_productions: List[
        Tuple[pyformlang.cfg.Variable, pyformlang.cfg.Variable, pyformlang.cfg.Variable]
    ] = []
    for production in cfg.productions:
        match production.body:
            case [] | [pyformlang.cfg.Epsilon()]:
                vars_generating_epsilon.append(production.head)
            case [pyformlang.cfg.Terminal() as terminal]:
                terminal_to_generating_vars[terminal.value].append(production.head)
            case [pyformlang.cfg.Variable() as var1, pyformlang.cfg.Variable() as var2]:
                variable_productions.append((production.head, var1, var2))
    node_to_idx = {node: idx for (idx, node) in enumerate(graph.nodes)}
    idx_to_node = {idx: node for (idx, node) in enumerate(graph.nodes)}
    is_reachable = BoolDecomposition(
        (graph.number_of_nodes(), graph.number_of_nodes()),
        content=itertools.chain(
            (
                (node_to_idx[start], node_to_idx[finish], var)
                for (start, finish, attributes) in graph.edges.data()
                for var in terminal_to_generating_vars[attributes["label"]]
            ),
            (
                (node_idx, node_idx, var)
                for node_idx in range(graph.number_of_nodes())
                for var in vars_generating_epsilon
            ),
        ),
    )
    prev_non_zeros = 0
    non_zeros = is_reachable.count_nonzero()
    while prev_non_zeros != non_zeros:
        for (head, var1, var2) in variable_productions:
            is_reachable[head] += is_reachable[var1] @ is_reachable[var2]
        prev_non_zeros = non_zeros
        non_zeros = is_reachable.count_nonzero()
    return {
        (idx_to_node[start_idx], var, idx_to_node[finish_idx])
        for (start_idx, finish_idx, var) in is_reachable
    }


def filtered_cfpq_with_matrix(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple[int, int]]:
    return _filter_cfpq_result(
        _cfpq_with_matrix(cfg, graph), cfg, start_nodes, final_nodes
    )
