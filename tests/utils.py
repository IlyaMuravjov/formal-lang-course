import networkx as nx
import pyformlang

__all__ = [
    "assert_equivalent_fas",
    "assert_isomorphic_fa_to_graph",
    "assert_isomorphic_fas",
]


def assert_equivalent_fas(
    actual_fa: pyformlang.finite_automaton.FiniteAutomaton,
    expected_fa: pyformlang.finite_automaton.FiniteAutomaton,
):
    # empty DFA-s are equivalent but `is_equivalent_to` throws on empty DFA-s
    if len(actual_fa.states) == 0 or len(expected_fa.states) == 0:
        assert (
            len(actual_fa.to_deterministic().minimize()) == 0
            and len(expected_fa.to_deterministic().minimize()) == 0
        )
    else:
        assert actual_fa.is_equivalent_to(expected_fa)


def _fa_to_networkx_without_extra_starting_nodes(
    fa: pyformlang.finite_automaton.FiniteAutomaton,
) -> nx.DiGraph:
    fa_graph = fa.to_networkx()
    for node in list(fa_graph.nodes):
        if isinstance(node, str) and node.endswith("_starting"):
            fa_graph.remove_node(node)
    return fa_graph


def assert_isomorphic_fa_to_graph(
    actual_fa: pyformlang.finite_automaton.FiniteAutomaton, expected_fa_graph
):
    actual_fa_graph = _fa_to_networkx_without_extra_starting_nodes(actual_fa)
    # here `node_match` ignores `key` attribute
    assert nx.is_isomorphic(
        actual_fa_graph,
        expected_fa_graph,
        edge_match=nx.classes.coreviews.AtlasView.__eq__,
        node_match=lambda n1, n2: str(n1["is_start"]) == str(n2["is_start"])
        and str(n1["is_final"]) == str(n2["is_final"]),
    )


def assert_isomorphic_fas(
    actual_fa: pyformlang.finite_automaton.FiniteAutomaton,
    expected_fa: pyformlang.finite_automaton.FiniteAutomaton,
):
    assert_isomorphic_fa_to_graph(
        actual_fa, _fa_to_networkx_without_extra_starting_nodes(expected_fa)
    )


def assert_equal_cfgs(
    actual_cfg: pyformlang.cfg.CFG,
    expected_cfg: pyformlang.cfg.CFG,
):
    assert actual_cfg.start_symbol == expected_cfg.start_symbol
    assert actual_cfg.productions == expected_cfg.productions
