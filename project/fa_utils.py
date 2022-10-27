from typing import Iterable

import networkx as nx
import pyformlang.finite_automaton
import pyformlang.regular_expression

from project.scipy_sparse_bool_decomposed_nfa import BoolDecomposedNFA

__all__ = ["graph_to_nfa", "regex_to_minimal_dfa", "intersect_nfas"]


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
        start_state=set(
            pyformlang.finite_automaton.State(node) for node in start_states
        )
        if start_states
        else all_states,
        final_states=set(
            pyformlang.finite_automaton.State(node) for node in final_states
        )
        if final_states
        else all_states,
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
