from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import Tuple

import cfpq_data
import networkx as nx

__all__ = [
    "GraphData",
    "get_graph_data",
    "get_graph",
    "to_graph_data",
    "write_labeled_two_cycles_graph_to_dot",
    "graph_from_data",
]

import pydot


@dataclass
class GraphData:
    node_count: int
    edge_count: int
    label_occurrences: Dict[str, int]


def get_graph_data(graph_name: str) -> GraphData:
    return to_graph_data(get_graph(graph_name))


def get_graph(graph_name: str) -> nx.MultiDiGraph:
    graph_path = cfpq_data.download(graph_name)
    return cfpq_data.graph_from_csv(graph_path)


def to_graph_data(graph: nx.Graph) -> GraphData:
    label_occurrences = dict()
    for (_, _, attributes) in graph.edges.data():
        label = attributes["label"]
        label_occurrences[label] = label_occurrences.get(label, 0) + 1
    return GraphData(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        label_occurrences,
    )


def write_labeled_two_cycles_graph_to_dot(
    cycle_sizes_without_common_node: Tuple[int, int],
    labels: Tuple[str, str],
    path: Path,
):
    graph = cfpq_data.labeled_two_cycles_graph(
        n=cycle_sizes_without_common_node[0],
        m=cycle_sizes_without_common_node[1],
        labels=labels,
    )
    _write_graph_to_dot(graph, path)


def _write_graph_to_dot(graph: nx.Graph, path: Path):
    with open(path, "w") as file:
        # removing "\n"-s because otherwise `read_dot` creates node called "\n"
        file.write(nx.drawing.nx_pydot.to_pydot(graph).to_string().replace("\n", ""))


def graph_from_data(dot_data: str) -> nx.DiGraph:
    return nx.nx_pydot.from_pydot(pydot.graph_from_dot_data(dot_data)[0])
