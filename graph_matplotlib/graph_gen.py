# SPDX-FileCopyrightText: 2024-present Silvano Cerza <silvanocerza@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from dataclasses import dataclass, field
from typing import List

import networkx as nx


@dataclass
class NodeData:
    width: int = 1
    height: int = 1

    self_edges: List["EdgeData"] = field(default_factory=list)


@dataclass
class EdgeData:
    minlen: int = 1
    weight: int = 1
    width: int = 1
    height: int = 1
    labeloffset: int = 1
    labelpos: int = 1

    label: str = ""
    # If the edge has been reversed during cycle removal
    reversed: bool = False


def generate_graph(seed=13648) -> nx.MultiDiGraph:
    # graph = nx.random_k_out_graph(8, 2, 0.5, seed=seed)
    graph = nx.random_labeled_tree(8, seed=seed)
    # Add some default attributes that we'll need later
    nx.set_node_attributes(graph, NodeData(), "data")
    nx.set_edge_attributes(graph, EdgeData(), "data")
    return graph
