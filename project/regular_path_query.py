from typing import Dict
from typing import Iterable
from typing import Set
from typing import Tuple
from typing import Union

import networkx as nx

from project.scipy_bool_decomposed_nfa import BoolDecomposedNFA
from project.fa_utils import graph_to_nfa
from project.fa_utils import regex_to_minimal_dfa

__all__ = ["regular_path_query_all_pairs", "regular_path_query_multiple_source"]


def regular_path_query_all_pairs(
    regex: str,
    graph: nx.DiGraph,
    start_states: Iterable[int] = None,
    final_states: Iterable[int] = None,
    bool_decomposed_nfa_cls=BoolDecomposedNFA,
) -> Set[Tuple[int, int]]:
    return set(
        (s1.value[0].value, s2.value[0].value)
        for (s1, s2) in bool_decomposed_nfa_cls.from_nfa(
            graph_to_nfa(graph, start_states, final_states)
        )
        .intersect(bool_decomposed_nfa_cls.from_nfa(regex_to_minimal_dfa(regex)))
        .get_reachable()
    )


def regular_path_query_multiple_source(
    regex: str,
    graph: nx.DiGraph,
    start_states: Iterable[int] = None,
    final_states: Iterable[int] = None,
    group_by_start: bool = False,
    bool_decomposed_nfa_cls=BoolDecomposedNFA,
) -> Union[Set[int], Dict[int, Set[int]]]:
    result = bool_decomposed_nfa_cls.from_nfa(
        graph_to_nfa(graph, start_states, final_states)
    ).sync_bfs(
        bool_decomposed_nfa_cls.from_nfa(regex_to_minimal_dfa(regex)),
        group_by_start=group_by_start,
    )
    return (
        {start.value: {end.value for end in ends} for (start, ends) in result.items()}
        if group_by_start
        else {end.value for end in result}
    )
