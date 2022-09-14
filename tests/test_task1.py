import networkx as nx
import pytest

from project.task1 import GraphData
from project.task1 import get_graph_data
from project.task1 import to_graph_data
from project.task1 import write_labeled_two_cycles_graph_to_dot


def test_get_graph_data_on_wc_graph():
    graph_name = "wc"
    expected_graph_data = GraphData(
        node_count=332, edge_count=269, edge_labels={"A", "D"}
    )
    actual_graph_data = get_graph_data(graph_name)
    assert actual_graph_data == expected_graph_data


def test_get_graph_data_on_go_graph():
    graph_name = "go"
    expected_graph_data = GraphData(
        node_count=582929,
        edge_count=1437437,
        edge_labels={
            "type",
            "hasDbXref",
            "annotatedTarget",
            "annotatedSource",
            "annotatedProperty",
            "subClassOf",
            "hasExactSynonym",
            "label",
            "hasOBONamespace",
            "id",
            "IAO_0000115",
            "someValuesFrom",
            "onProperty",
            "rest",
            "first",
            "hasNarrowSynonym",
            "creation_date",
            "created_by",
            "hasRelatedSynonym",
            "equivalentClass",
            "intersectionOf",
            "comment",
            "deprecated",
            "hasBroadSynonym",
            "IAO_0100001",
            "hasAlternativeId",
            "IAO_0000231",
            "inSubset",
            "consider",
            "hasSynonymType",
            "disjointWith",
            "subPropertyOf",
            "shorthand",
            "propertyChainAxiom",
            "inverseOf",
            "hasScope",
            "SynonymTypeProperty",
            "IAO_0000589",
            "hasOBOFormatVersion",
            "default-namespace",
            "license",
            "versionIRI",
            "creator",
            "date",
            "IAO_0000425",
            "is_metadata_tag",
            "is_class_level",
        },
    )
    actual_graph_data = get_graph_data(graph_name)
    assert actual_graph_data == expected_graph_data


def test_get_graph_data_on_unknown_graph():
    with pytest.raises(Exception):
        get_graph_data("Unknown graph name")


def test_to_graph_data_on_empty_graph():
    expected_graph_data = GraphData(node_count=0, edge_count=0, edge_labels=set())
    actual_graph_data = to_graph_data(nx.empty_graph())
    assert expected_graph_data == actual_graph_data


def test_write_labeled_two_cycles_graph_to_dot_with_positive_cycle_sizes(tmp_path):
    expected_graph = nx.DiGraph(
        [
            (0, 1, dict(label="A")),
            (1, 0, dict(label="A")),
            (0, 2, dict(label="B")),
            (2, 3, dict(label="B")),
            (3, 0, dict(label="B")),
        ]
    )
    path_to_actual = tmp_path / "actual_graph.dot"
    write_labeled_two_cycles_graph_to_dot((1, 2), ("A", "B"), path_to_actual)
    actual_graph = nx.DiGraph(nx.drawing.nx_pydot.read_dot(path_to_actual))
    assert nx.is_isomorphic(
        actual_graph, expected_graph, edge_match=dict.__eq__, node_match=dict.__eq__
    )


def test_write_labeled_two_cycles_graph_to_dot_with_zero_cycle_sizes(tmp_path):
    path_to_actual = tmp_path / "actual_graph.dot"
    with pytest.raises(Exception):
        write_labeled_two_cycles_graph_to_dot((0, 0), ("A", "B"), path_to_actual)
