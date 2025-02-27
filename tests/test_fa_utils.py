from project.fa_utils import intersect_nfas
from project.fa_utils import regex_to_minimal_dfa
from tests.utils import assert_equivalent_fas
from tests.utils import assert_isomorphic_fa_to_graph
from project.graph_utils import graph_from_data
from project.fa_utils import nfa_from_data


def test_regex_to_minimal_dfa(config_data: dict):
    expected_dfa = nfa_from_data(config_data["expected-dfa"])
    actual_dfa = regex_to_minimal_dfa(config_data["regex"])
    assert actual_dfa.is_deterministic()
    assert len(actual_dfa.states) == len(expected_dfa.states)
    assert_equivalent_fas(actual_dfa, expected_dfa)


def test_graph_to_nfa(config_data: dict):
    expected_nfa_graph = graph_from_data(config_data["expected-nfa-graph"])
    actual_nfa = nfa_from_data(config_data["nfa"])  # uses graph_to_nfa
    assert_isomorphic_fa_to_graph(actual_nfa, expected_nfa_graph)


def test_intersect_nfas(config_data: dict):
    expected_nfa = nfa_from_data(config_data["intersection-nfa"])
    actual_nfa = intersect_nfas(
        nfa_from_data(config_data["nfa1"]), nfa_from_data(config_data["nfa2"])
    )
    assert_equivalent_fas(actual_nfa, expected_nfa)
