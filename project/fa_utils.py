from typing import Iterable

import networkx as nx
from pyformlang.finite_automaton import DeterministicFiniteAutomaton as DFA
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton as NFA
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex

__all__ = ["graph_to_nfa", "regex_to_minimal_dfa", "intersect_nfas"]

from project.bool_decomposed_nfa import BoolDecomposedNFA


def regex_to_minimal_dfa(regex_str: str) -> DFA:
    return Regex(regex_str).to_epsilon_nfa().minimize()


def graph_to_nfa(
    graph: nx.DiGraph,
    start_states: Iterable[int] = None,
    final_states: Iterable[int] = None,
) -> NFA:
    all_states = set(State(node) for node in graph.nodes)
    nfa = NFA(
        states=all_states,
        start_state=set(State(node) for node in start_states)
        if start_states
        else all_states,
        final_states=set(State(node) for node in final_states)
        if final_states
        else all_states,
    )
    for (source, target, attributes) in graph.edges.data():
        nfa.add_transition(
            State(source),
            Symbol(attributes["label"]),
            State(target),
        )
    return nfa


def intersect_nfas(nfa1: NFA, nfa2: NFA) -> NFA:
    return (
        BoolDecomposedNFA.from_nfa(nfa1)
        .intersect(BoolDecomposedNFA.from_nfa(nfa2))
        .to_nfa()
    )
