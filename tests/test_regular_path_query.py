import pytest

from project.regular_path_query import regular_path_query_all_pairs
from project.regular_path_query import regular_path_query_multiple_source
from project.graph_utils import graph_from_data

import importlib


@pytest.mark.parametrize(
    "bool_decomposed_nfa_module",
    ["project.scipy_bool_decomposed_nfa", "project.pygraphblas_bool_decomposed_nfa"],
)
def test_regular_path_query_all_pairs(
    config_data: dict, bool_decomposed_nfa_module: str
):
    assert regular_path_query_all_pairs(
        regex=config_data["regex"],
        graph=graph_from_data(config_data["graph"]),
        start_states=set(config_data["start-states"])
        if "start-states" in config_data
        else None,
        final_states=set(config_data["final-states"])
        if "final-states" in config_data
        else None,
        bool_decomposed_nfa_cls=importlib.import_module(
            bool_decomposed_nfa_module
        ).BoolDecomposedNFA,
    ) == set((res[0], res[1]) for res in config_data["expected-result"])


@pytest.mark.parametrize(
    "bool_decomposed_nfa_module",
    ["project.scipy_bool_decomposed_nfa", "project.pygraphblas_bool_decomposed_nfa"],
)
def test_regular_path_query_multiple_source(
    config_data: dict, bool_decomposed_nfa_module: str
):
    expected_result = config_data["expected-result"]
    group_by_start = (
        config_data["group-by-start"] if "group-by-start" in config_data else False
    )
    assert regular_path_query_multiple_source(
        regex=config_data["regex"],
        graph=graph_from_data(config_data["graph"]),
        start_states=set(config_data["start-states"])
        if "start-states" in config_data
        else None,
        final_states=set(config_data["final-states"])
        if "final-states" in config_data
        else None,
        group_by_start=group_by_start,
        bool_decomposed_nfa_cls=importlib.import_module(
            bool_decomposed_nfa_module
        ).BoolDecomposedNFA,
    ) == (
        {start: set(ends) for start, ends in expected_result.items()}
        if group_by_start
        else set(expected_result)
    )
