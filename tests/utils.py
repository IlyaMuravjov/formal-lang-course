import networkx as nx
import pydot
from pyformlang.finite_automaton import FiniteAutomaton as FA
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton as NFA

from project.fa_utils import graph_to_nfa

__all__ = [
    "read_graph",
    "read_nfa",
    "assert_equivalent_fas",
    "assert_isomorphic_fa_to_graph",
    "assert_isomorphic_fas",
]


def read_graph(dot_data: str) -> nx.DiGraph:
    return nx.nx_pydot.from_pydot(pydot.graph_from_dot_data(dot_data)[0])


def read_nfa(data: dict) -> NFA:
    return graph_to_nfa(
        graph=read_graph(data["graph"]),
        start_states=set(data["start-states"]) if "start-states" in data else None,
        final_states=set(data["final-states"]) if "final-states" in data else None,
    )


def assert_equivalent_fas(actual_fa: FA, expected_fa: FA):
    # empty DFA-s are equivalent but `is_equivalent_to` throws on empty DFA-s
    if len(actual_fa.states) == 0 or len(expected_fa.states) == 0:
        assert (
            len(actual_fa.to_deterministic().minimize()) == 0
            and len(expected_fa.to_deterministic().minimize()) == 0
        )
    else:
        assert actual_fa.is_equivalent_to(expected_fa)


def _fa_to_networkx_without_extra_starting_nodes(fa: FA) -> nx.DiGraph:
    fa_graph = fa.to_networkx()
    for node in list(fa_graph.nodes):
        if isinstance(node, str) and node.endswith("_starting"):
            fa_graph.remove_node(node)
    return fa_graph


def assert_isomorphic_fa_to_graph(actual_fa: FA, expected_fa_graph):
    actual_fa_graph = _fa_to_networkx_without_extra_starting_nodes(actual_fa)
    # here `node_match` ignores `key` attribute
    assert nx.is_isomorphic(
        actual_fa_graph,
        expected_fa_graph,
        edge_match=nx.classes.coreviews.AtlasView.__eq__,
        node_match=lambda n1, n2: str(n1["is_start"]) == str(n2["is_start"])
        and str(n1["is_final"]) == str(n2["is_final"]),
    )


def assert_isomorphic_fas(actual_fa: FA, expected_fa: FA):
    assert_isomorphic_fa_to_graph(
        actual_fa, _fa_to_networkx_without_extra_starting_nodes(expected_fa)
    )
