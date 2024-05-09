# SPDX-FileCopyrightText: 2024-present Silvano Cerza <silvanocerza@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import enum

import networkx as nx

from .graph_gen import EdgeData, NodeData


class Direction(enum.Enum):
    """
    The direction of the graph.
    """

    LeftRight = "LeftRight"
    TopBottom = "TopBottom"
    RightLeft = "RightLeft"
    BottomTop = "BottomTop"


def make_space_for_edge_labels(graph: nx.MultiDiGraph, rank_direction: Direction):
    """
    This idea comes from the Gansner paper: to account for edge labels in our
    layout we split each rank in half by doubling minlen and halving ranksep.
    Then we can place labels at these mid-points between nodes.
    We also add some minimal padding to the width to push the label for the edge
    away from the edge itself a bit.
    """
    for v in graph.edges:
        if rank_direction in [Direction.LeftRight, Direction.RightLeft]:
            graph.edges[v]["data"].width += graph.edges[v]["data"].labeloffset
        else:
            graph.edges[v]["data"].height += graph.edges[v]["data"].labeloffset
    # for u, v, k in graph.edges:
    #     if rank_direction in [Direction.LeftRight, Direction.RightLeft]:
    #         graph.edges[u, v, k]["data"].width += graph.edges[u, v, k][
    #             "data"
    #         ].labeloffset
    #     else:
    #         graph.edges[u, v, k]["data"].height += graph.edges[u, v, k][
    #             "data"
    #         ].labeloffset


def remove_self_edges(graph: nx.MultiDiGraph):
    """
    Remove self edges from the graph and caches them in the node.
    We'll add them back later.
    """
    to_remove = []
    for u, v in graph.edges:
        if u != v:
            continue

        node = graph.nodes[u]

        node["data"].self_edges.append(graph.edges[u, v]["data"])
        to_remove.append((u, v))
    for v in to_remove:
        graph.remove_edge(**v)


def find_feedback_arc_set(graph: nx.MultiDiGraph):
    """
    Find the feedback arc set for the graph.
    Feedback arc set is a set of edges that can be removed to make a graph acyclic.
    """
    edges = set()
    nodes_stack = []
    nodes_visited = set()

    def dfs(node):
        if node in nodes_visited:
            return

        nodes_visited.add(node)
        nodes_stack.append(node)

        for edge in graph.edges(node):
            sender = edge[0]
            if sender in nodes_stack:
                edges.add(edge)
            else:
                dfs(sender)
        # for sender, receiver, k in graph.edges(node, keys=True):
        #     if sender in nodes_stack:
        #         edges.add((sender, receiver, k))
        #     else:
        #         dfs(sender)

        nodes_stack.remove(node)

    for node in graph.nodes:
        dfs(node)

    return edges


def remove_cycles(graph: nx.MultiDiGraph):
    """
    Remove cycles from the graph by reversing the edges in the feedback arc set.
    """
    edges = find_feedback_arc_set(graph)
    for edge in edges:
        label = graph.edges[*edge]["data"].label
        graph.remove_edge(*edge)
        # Let's assume label is a dict
        graph.add_edge(*edge, data=EdgeData(label=label, reversed=True))


# A nesting graph creates dummy nodes for the tops and bottoms of subgraphs,
# adds appropriate edges to ensure that all cluster nodes are placed between
# these boundaries, and ensures that the graph is connected.
#
# In addition we ensure, through the use of the minlen property, that nodes
# and subgraph border nodes to not end up on the same rank.
#
# Preconditions:
#
# 1. Input graph is a DAG
# 2. Nodes in the input graph has a minlen attribute
#
# Postconditions:
#
# 1. Input graph is connected.
# 2. Dummy nodes are added for the tops and bottoms of subgraphs.
# 3. The minlen attribute for nodes is adjusted to ensure nodes do not
#  get placed on the same rank as subgraph border nodes.
#
# The nesting graph idea comes from Sander, "Layout of Compound Directed
# Graphs."
def create_nesting_graph(graph: nx.MultiDiGraph):
    graph.add_node("_root", data=NodeData())
    depths = tree_depths(graph)
    height = max(depths.values()) - 1
    node_separation = 2 * height + 1

    weight = 1
    for sender, receiver, k in graph.edges:
        graph.edges[sender, receiver, k]["data"].minlen *= node_separation
        weight += graph.edges[sender, receiver, k]["data"].weight

    create_border_nodes(graph, node_separation)

    # We need this later one to undo this operation, so we return it
    return node_separation


def tree_depths(graph: nx.MultiDiGraph):
    # Maps each node to its depth in the tree
    depths = {}

    def dfs(node, depth):
        # Get the direct children of node
        descendants = nx.descendants_at_distance(graph, node, 1) or []
        for descendant in descendants:
            dfs(descendant, depth + 1)

        depths[node] = depth

    for node in graph.nodes:
        dfs(node, 1)
    return depths


def create_border_nodes(graph: nx.MultiDiGraph, node_separation: int):
    root = graph.nodes["_root"]
    for node in graph.nodes:
        descendants = nx.descendants(graph, node) or []
        if not descendants:
            if node != root:
                graph.add_edge("_root", node, data=EdgeData(minlen=node_separation))
            continue

        # graph.add_node("_bt", data=NodeData())
        # graph.add_node("_bb", data=NodeData())
        # graph.nodes["_bt"]
