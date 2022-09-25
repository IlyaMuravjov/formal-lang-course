from typing import Iterable
from typing import Set
from typing import Tuple

import networkx as nx

from project.bool_decomposed_nfa import BoolDecomposedNFA
from project.fa_utils import graph_to_nfa
from project.fa_utils import regex_to_minimal_dfa

__all__ = ["regular_path_query"]


def regular_path_query(
    regex: str,
    graph: nx.DiGraph,
    start_states: Iterable[int] = None,
    final_states: Iterable[int] = None,
) -> Set[Tuple[int, int]]:
    return set(
        (s1.value[0].value, s2.value[0].value)
        for (s1, s2) in BoolDecomposedNFA.from_nfa(
            graph_to_nfa(graph, start_states, final_states)
        )
        .intersect(BoolDecomposedNFA.from_nfa(regex_to_minimal_dfa(regex)))
        .get_reachable()
    )
