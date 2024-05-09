import sys

from graph_matplotlib.graph_gen import generate_graph
from graph_matplotlib.processing import (
    Direction,
    create_nesting_graph,
    make_space_for_edge_labels,
    remove_cycles,
    remove_self_edges,
)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 13648
g = generate_graph(seed=seed)

make_space_for_edge_labels(g, Direction.TopBottom)
remove_self_edges(g)
# This thing here is not a reliable, it doesn't fully remove cycles.
# This happens cause we remove cycles by reversing the edge, though if the graph is complex
# enough it might also be that reversing creates cycles.
remove_cycles(g)


create_nesting_graph(g)

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

pos = nx.spring_layout(g, seed=seed)

node_sizes = [3 + 10 * i for i in range(len(g))]
M = g.number_of_edges()
edge_colors = range(2, M + 2)
edge_alphas = [(5 + i) / (M + 4) for i in range(M)]
cmap = plt.cm.plasma

nodes = nx.draw_networkx_nodes(g, pos, node_size=node_sizes, node_color="indigo")
edges = nx.draw_networkx_edges(
    g,
    pos,
    node_size=node_sizes,
    arrowstyle="->",
    arrowsize=10,
    edge_color=edge_colors,
    edge_cmap=cmap,
    width=2,
)
# set alpha value for each edge
for i in range(M):
    edges[i].set_alpha(edge_alphas[i])

pc = mpl.collections.PatchCollection(edges, cmap=cmap)
pc.set_array(edge_colors)

ax = plt.gca()
ax.set_axis_off()
plt.colorbar(pc, ax=ax)
plt.show()
