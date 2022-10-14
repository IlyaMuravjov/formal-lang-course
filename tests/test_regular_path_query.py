from project.regular_path_query import regular_path_query_all_pairs
from project.regular_path_query import regular_path_query_multiple_source
from tests.utils import read_graph


def test_regular_path_query_all_pairs(config_data: dict):
    assert regular_path_query_all_pairs(
        regex=config_data["regex"],
        graph=read_graph(config_data["graph"]),
        start_states=set(config_data["start-states"])
        if "start-states" in config_data
        else None,
        final_states=set(config_data["final-states"])
        if "final-states" in config_data
        else None,
    ) == set((res[0], res[1]) for res in config_data["expected-result"])


def test_regular_path_query_multiple_source(config_data: dict):
    expected_result = config_data["expected-result"]
    group_by_start = (
        config_data["group-by-start"] if "group-by-start" in config_data else False
    )
    assert regular_path_query_multiple_source(
        regex=config_data["regex"],
        graph=read_graph(config_data["graph"]),
        start_states=set(config_data["start-states"])
        if "start-states" in config_data
        else None,
        final_states=set(config_data["final-states"])
        if "final-states" in config_data
        else None,
        group_by_start=group_by_start,
    ) == (
        {start: set(ends) for start, ends in expected_result.items()}
        if group_by_start
        else set(expected_result)
    )
