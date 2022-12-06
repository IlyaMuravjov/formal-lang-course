import importlib

import pyformlang.cfg
import pytest

from project.cfg_utils import cfg_from_data
from project.context_free_path_query import filtered_cfpq_with_hellings
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


@pytest.mark.parametrize(
    "cfpq_module",
    [
        "project.with_scipy.context_free_path_query",
        "project.with_pygraphblas.context_free_path_query",
    ],
)
def test_filtered_cfpq_with_matrix(config_data: dict, cfpq_module: str):
    _test_filtered_cfpq_impl(
        importlib.import_module(cfpq_module).filtered_cfpq_with_matrix, config_data
    )


@pytest.mark.parametrize(
    "cfpq_module",
    [
        "project.with_scipy.context_free_path_query",
        "project.with_pygraphblas.context_free_path_query",
    ],
)
def test_filtered_cfpq_with_tensor(config_data: dict, cfpq_module: str):
    _test_filtered_cfpq_impl(
        importlib.import_module(cfpq_module).filtered_cfpq_with_tensor, config_data
    )


@pytest.mark.parametrize(
    "cfpq_module",
    [
        "project.with_scipy.context_free_path_query",
        "project.with_pygraphblas.context_free_path_query",
    ],
)
def test_cfpq_with_tensor(config_data: dict, cfpq_module: str):
    assert importlib.import_module(cfpq_module).cfpq_with_tensor(
        cfg_from_data(config_data["cfg"]), graph_from_data(config_data["graph"])
    ) == {
        (start, pyformlang.cfg.Variable(var), finish)
        for (start, var, finish) in config_data["expected-result"]
    }
