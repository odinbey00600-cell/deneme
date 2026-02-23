import networkx as nx


class LineageTracker:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_generation(self, parent_id: int | None, generation_id: int, score: float):
        self.graph.add_node(generation_id, score=score)
        if parent_id is not None:
            self.graph.add_edge(parent_id, generation_id)

    def as_edges(self):
        return list(self.graph.edges())
