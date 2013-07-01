from walkers.astar import AStarWalker


class DijkstraWalker(AStarWalker):
    """
    Dijkstra shortest path finding algorithm is basically
    an A* algorithm without heuristic.
    """
    def __init__(self, graph, src_cell, dst_cell, use_diags):
        super(DijkstraWalker, self).__init__(graph, src_cell, 
                                             dst_cell, use_diags,
                                             use_heuristic=False)
