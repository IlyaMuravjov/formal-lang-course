from project.cfg_utils import cfg_from_data
from project.context_free_path_query import filtered_cfpq_with_hellings
from project.context_free_path_query import filtered_cfpq_with_matrix
from project.context_free_path_query import filtered_cfpq_with_tensor
from project.graph_utils import graph_from_data


def _test_filtered_cfpq_impl(impl, config_data: dict):
    assert impl(
        cfg_from_data(config_data["cfg"]),
        graph_from_data(config_data["graph"]),
        start_nodes=set(config_data["start-nodes"])
        if "start-nodes" in config_data
        else None,
        final_nodes=set(config_data["final-nodes"])
        if "final-nodes" in config_data
        else None,
    ) == {(start, finish) for (start, finish) in config_data["expected-result"]}


def test_filtered_cfpq_with_hellings(config_data: dict):
    _test_filtered_cfpq_impl(filtered_cfpq_with_hellings, config_data)


def test_filtered_cfpq_with_matrix(config_data: dict):
    _test_filtered_cfpq_impl(filtered_cfpq_with_matrix, config_data)


def test_filtered_cfpq_with_tensor(config_data: dict):
    _test_filtered_cfpq_impl(filtered_cfpq_with_tensor, config_data)
