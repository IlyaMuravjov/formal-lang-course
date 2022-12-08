from collections import defaultdict
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
import itertools
from typing import Union

import pyformlang
import networkx as nx
import scipy

from project.with_scipy.bool_decomposed_nfa import BoolDecomposedNFA
from project.with_scipy.bool_decomposition import BoolDecomposition
from project.context_free_path_query import filter_cfpq_result
from project.cfg_utils import cfg_to_weak_normal_form
from project.ecfg import ECFG
from project.fa_utils import graph_to_nfa
from project.rsm import RSM

__all__ = [
    "filtered_cfpq_with_matrix",
    "filtered_cfpq_with_tensor",
    "cfpq_with_tensor",
]


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
        if (
            len(production.body) == 0
            or len(production.body) == 1
            and isinstance(production.body[0], pyformlang.cfg.Epsilon)
        ):
            vars_generating_epsilon.append(production.head)
        elif len(production.body) == 1 and isinstance(
            production.body[0], pyformlang.cfg.Terminal
        ):
            terminal_to_generating_vars[production.body[0].value].append(
                production.head
            )
        else:
            assert (
                len(production.body) == 2
                and isinstance(production.body[0], pyformlang.cfg.Variable)
                and isinstance(production.body[1], pyformlang.cfg.Variable)
            )
            variable_productions.append(
                (production.head, production.body[0], production.body[1])
            )
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
    return filter_cfpq_result(
        _cfpq_with_matrix(cfg, graph), cfg, start_nodes, final_nodes
    )


def cfpq_with_tensor(
    cfg: Union[pyformlang.cfg.CFG, ECFG], graph: nx.DiGraph
) -> Set[Tuple[int, pyformlang.cfg.Variable, int]]:
    bool_decomposed_rsm = BoolDecomposedNFA.from_nfa(
        RSM.from_ecfg(cfg if isinstance(cfg, ECFG) else ECFG.from_cfg(cfg))
        .minimize()
        .merge_boxes_to_single_nfa()
    )
    bool_decomposed_graph = BoolDecomposedNFA.from_nfa(graph_to_nfa(graph))
    if isinstance(cfg, pyformlang.cfg.CFG):
        identity_matrix = scipy.sparse.eye(
            bool_decomposed_graph.state_count, dtype=bool, format="csr"
        )
        for var in cfg.get_nullable_symbols():
            bool_decomposed_graph.adj_bool_decomposition[
                pyformlang.finite_automaton.Symbol(var.value)
            ] += identity_matrix
    last_transitive_closure_len = 0
    while True:
        transitive_closure = bool_decomposed_rsm.intersect(
            bool_decomposed_graph
        ).get_reachable()
        if len(transitive_closure) == last_transitive_closure_len:
            break
        last_transitive_closure_len = len(transitive_closure)
        added_transitions: Dict[
            pyformlang.finite_automaton.Symbol, scipy.sparse.dok_matrix
        ] = defaultdict(
            lambda: scipy.sparse.dok_matrix(
                (bool_decomposed_graph.state_count, bool_decomposed_graph.state_count),
                dtype=bool,
            )
        )
        for (start, finish) in transitive_closure:
            start_rsm_state, start_graph_state = start.value
            start_var, _ = start_rsm_state.value
            finish_rsm_state, finish_graph_state = finish.value
            finish_var, _ = finish_rsm_state.value
            assert start_var == finish_var
            added_transitions[pyformlang.finite_automaton.Symbol(start_var.value)][
                bool_decomposed_graph.state_to_idx(start_graph_state),
                bool_decomposed_graph.state_to_idx(finish_graph_state),
            ] = True
        for (symbol, matrix) in added_transitions.items():
            bool_decomposed_graph.adj_bool_decomposition[symbol] += matrix
    return {
        (start.value, pyformlang.cfg.Variable(symbol.value), finish.value)
        for start, symbol, finish in bool_decomposed_graph
        if pyformlang.cfg.Variable(symbol.value) in cfg.variables
    }


def filtered_cfpq_with_tensor(
    cfg: Union[pyformlang.cfg.CFG, ECFG],
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple[int, int]]:
    return filter_cfpq_result(
        cfpq_with_tensor(cfg, graph), cfg, start_nodes, final_nodes
    )
