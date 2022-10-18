from typing import Iterable

import networkx as nx
import pyformlang
import pyformlang.finite_automaton
import pyformlang.regular_expression

from project.scipy_sparse_bool_decomposed_nfa import BoolDecomposedNFA

__all__ = ["graph_to_nfa", "regex_to_minimal_dfa", "intersect_nfas"]

from project.graph_utils import graph_from_data


def regex_to_minimal_dfa(
    regex_str: str,
) -> pyformlang.finite_automaton.DeterministicFiniteAutomaton:
    return pyformlang.regular_expression.Regex(regex_str).to_epsilon_nfa().minimize()


def graph_to_nfa(
    graph: nx.DiGraph,
    start_states: Iterable[int] = None,
    final_states: Iterable[int] = None,
) -> pyformlang.finite_automaton.NondeterministicFiniteAutomaton:
    all_states = set(pyformlang.finite_automaton.State(node) for node in graph.nodes)
    nfa = pyformlang.finite_automaton.NondeterministicFiniteAutomaton(
        states=all_states,
        start_state=all_states
        if start_states is None
        else set(pyformlang.finite_automaton.State(node) for node in start_states),
        final_states=all_states
        if final_states is None
        else set(pyformlang.finite_automaton.State(node) for node in final_states),
    )
    for (source, target, attributes) in graph.edges.data():
        nfa.add_transition(
            pyformlang.finite_automaton.State(source),
            pyformlang.finite_automaton.Symbol(attributes["label"]),
            pyformlang.finite_automaton.State(target),
        )
    return nfa


def intersect_nfas(
    nfa1: pyformlang.finite_automaton.NondeterministicFiniteAutomaton,
    nfa2: pyformlang.finite_automaton.NondeterministicFiniteAutomaton,
    bool_decomposed_nfa_cls=BoolDecomposedNFA,
) -> pyformlang.finite_automaton.NondeterministicFiniteAutomaton:
    return (
        bool_decomposed_nfa_cls.from_nfa(nfa1)
        .intersect(bool_decomposed_nfa_cls.from_nfa(nfa2))
        .to_nfa()
    )


def nfa_from_data(
    data: dict,
) -> pyformlang.finite_automaton.NondeterministicFiniteAutomaton:
    return graph_to_nfa(
        graph=graph_from_data(data["graph"]),
        start_states=set(data["start-states"]) if "start-states" in data else None,
        final_states=set(data["final-states"]) if "final-states" in data else None,
    )
