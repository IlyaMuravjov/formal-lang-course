import networkx as nx
import pytest

from project.graph_utils import GraphData
from project.graph_utils import get_graph_data
from project.graph_utils import to_graph_data
from project.graph_utils import write_labeled_two_cycles_graph_to_dot
from tests.utils import read_graph


@pytest.mark.skip(reason="cfpq_data fails to download graph by name")
def test_get_graph_data(config_data):
    expected_graph_data = GraphData(
        node_count=int(config_data["expected-node-count"]),
        edge_count=int(config_data["expected-edge-count"]),
        edge_labels=set(config_data["expected-edge-labels"]),
    )
    actual_graph_data = get_graph_data(config_data["graph-name"])
    assert actual_graph_data == expected_graph_data


def test_get_graph_data_on_unknown_graph():
    with pytest.raises(Exception):
        get_graph_data("Unknown graph name")


def test_to_graph_data_on_empty_graph():
    expected_graph_data = GraphData(node_count=0, edge_count=0, edge_labels=set())
    actual_graph_data = to_graph_data(nx.empty_graph())
    assert expected_graph_data == actual_graph_data


def test_write_labeled_two_cycles_graph_to_dot(config_data, tmp_path):
    expected_graph = read_graph(config_data["expected-graph"])
    path_to_actual = tmp_path / "actual_graph.dot"
    write_labeled_two_cycles_graph_to_dot(
        config_data["cycle-sizes"], config_data["labels"], path_to_actual
    )
    actual_graph = nx.DiGraph(nx.drawing.nx_pydot.read_dot(path_to_actual))
    assert nx.is_isomorphic(
        actual_graph, expected_graph, edge_match=dict.__eq__, node_match=dict.__eq__
    )


def test_write_labeled_two_cycles_graph_to_dot_with_zero_cycle_sizes(tmp_path):
    path_to_actual = tmp_path / "actual_graph.dot"
    with pytest.raises(Exception):
        write_labeled_two_cycles_graph_to_dot((0, 0), ("A", "B"), path_to_actual)
