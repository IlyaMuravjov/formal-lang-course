import networkx as nx
import pydot

from project.task2 import graph_to_nfa
from project.task2 import regex_to_minimal_dfa


def test_regex_to_minimal_dfa(config_data: dict):
    expected_dfa = graph_to_nfa(
        graph=nx.nx_pydot.from_pydot(
            pydot.graph_from_dot_data(config_data["expected-dfa-graph"])[0]
        ),
        start_states=set(config_data["expected-start-states"]),
        final_states=set(config_data["expected-final-states"]),
    )
    actual_dfa = regex_to_minimal_dfa(config_data["regex"])
    assert actual_dfa.is_deterministic()
    assert len(actual_dfa.states) == len(expected_dfa.states)
    # empty DFA-s are equivalent but `is_equivalent_to` throws on empty DFA-s
    if len(expected_dfa) != 0:
        assert actual_dfa.is_equivalent_to(expected_dfa)


def test_graph_to_nfa(config_data: dict):
    expected_nfa_graph = nx.nx_pydot.from_pydot(
        pydot.graph_from_dot_data(config_data["expected-nfa-graph"])[0]
    )
    actual_nfa = graph_to_nfa(
        graph=nx.nx_pydot.from_pydot(
            pydot.graph_from_dot_data(config_data["graph"])[0]
        ),
        start_states=set(config_data["start-states"])
        if "start-states" in config_data
        else None,
        final_states=set(config_data["final-states"])
        if "final-states" in config_data
        else None,
    )
    actual_nfa_graph = actual_nfa.to_networkx()
    # remove "..._starting" nodes introduced by `to_networkx()`
    for node in list(actual_nfa_graph.nodes):
        if node.endswith("_starting"):
            actual_nfa_graph.remove_node(node)
    assert nx.is_isomorphic(
        actual_nfa_graph,
        expected_nfa_graph,
        edge_match=lambda e1, e2: e1.get("label", None) == e2.get("label", None),
        node_match=lambda n1, n2: str(n1["is_start"]) == str(n2["is_start"])
        and str(n1["is_final"]) == str(n2["is_final"]),
    )
