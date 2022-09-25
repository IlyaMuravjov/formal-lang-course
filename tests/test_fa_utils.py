from project.fa_utils import regex_to_minimal_dfa
from tests.utils import assert_equivalent_fas
from tests.utils import assert_isomorphic_fa_to_graph
from tests.utils import read_graph
from tests.utils import read_nfa


def test_regex_to_minimal_dfa(config_data: dict):
    expected_dfa = read_nfa(config_data["expected-dfa"])
    actual_dfa = regex_to_minimal_dfa(config_data["regex"])
    assert actual_dfa.is_deterministic()
    assert len(actual_dfa.states) == len(expected_dfa.states)
    assert_equivalent_fas(actual_dfa, expected_dfa)


def test_graph_to_nfa(config_data: dict):
    expected_nfa_graph = read_graph(config_data["expected-nfa-graph"])
    actual_nfa = read_nfa(config_data["nfa"])  # uses graph_to_nfa
    assert_isomorphic_fa_to_graph(actual_nfa, expected_nfa_graph)
