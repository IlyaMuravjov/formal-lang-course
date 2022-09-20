import networkx as nx

from typing import Set

from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton as DFA
from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.finite_automaton import Epsilon

__all__ = ["graph_to_nfa", "regex_to_minimal_dfa"]


def regex_to_minimal_dfa(regex_str: str) -> DFA:
    return Regex(regex_str).to_epsilon_nfa().to_deterministic().minimize()


def graph_to_nfa(
    graph: nx.DiGraph, start_states: Set[int] = None, final_states: Set[int] = None
) -> EpsilonNFA:
    all_states = set(State(node) for node in graph.nodes)
    nfa = EpsilonNFA(
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
            Symbol(attributes["label"]) if "label" in attributes else Epsilon(),
            State(target),
        )
    return nfa
