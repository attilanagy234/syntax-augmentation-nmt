import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


class DependencyGraphWrapper:
    def __init__(self, config, graph):
        self._config = config
        self._graph = graph

    def get_root(self):
        # since dep parsing always yields a tree, it should always have one element
        return [n for n, d in self._graph.in_degree() if d == 0][0]

    def get_distances_from_root(self):
        return nx.shortest_path_length(self._graph, self.get_root())

    def display_graph(self):
        labels = {e: self._graph.get_edge_data(e[0], e[1])["dep"] for e in self._graph.edges()}
        pos = graphviz_layout(self._graph, prog="dot",
                              root=1000,
                              args='-Gsplines=true -Gnodesep=0.6 -Goverlap=scalexy'
                              )
        nx.draw(self._graph, pos,
                with_labels=True,
                alpha=0.6,
                node_size=1000,
                font_size=8
                )
        nx.draw_networkx_edge_labels(self._graph, pos, edge_labels=labels)
        plt.show()

    def get_nodes_with_property(self, attribute_key, attribute_value):
        return [x for x, y in self._graph.nodes(data=True) if y[attribute_key] == attribute_value]

    def get_edges_with_property(self, attribute_key, attribute_value):
        edges_with_property = []
        for source_node, target_node, edge in self._graph.edges(data=True):
            if edge[attribute_key] == attribute_value:
                edges_with_property.append((source_node, target_node, edge))
        return edges_with_property
