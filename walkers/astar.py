import heapq
from core.cell import CellStatus
from core.config import DEFAULT_CELL_WEIGHT
from walkers.basic import BasicWalker


class AStarNode(object):
    def __init__(self, cell):
        self.cell = cell
        self.est_cost = 0
        self.exact_cost = 0

    def __str__(self):
        return "(%s, %s [%s, %s])" % (self.est_cost, self.exact_cost,
                                      self.cell.row, self.cell.col)

    def __cmp__(self, node):
        # For priority queue
        return cmp(self.est_cost + self.exact_cost,
                   node.est_cost + node.exact_cost)


class AStarWalker(BasicWalker):
    """
    A* shortest path finding algorithm with optional
    manhattan distance heuristic.
    """

    def __init__(self, graph, src_cell, dst_cell,
                 use_diags, use_heuristic=True):
        super(AStarWalker, self).__init__(graph, src_cell,
                                          dst_cell, use_diags)
        self._finished = False
        self._use_heuristic = use_heuristic

        self._nodes = []
        for c in self._graph.cells():
            self._nodes.append(AStarNode(c))

        start_node = self._cell_to_node(self._src_cell)
        start_node.exact_cost = 0
        self._to_visit = [start_node]

    def finished(self):
        return self._finished

    def step(self):
        if len(self._to_visit) == 0:
            self._finished = True
        if self._finished:
            return

        while len(self._to_visit) > 0:
            cnode = heapq.heappop(self._to_visit)
            cnode.cell.status = CellStatus.Visited
            if cnode.cell == self._dst_cell:
                self._finished = True
                return

            for c in cnode.cell.neighbours(diagonals=self._use_diags):
                n = self._cell_to_node(c)
                ex_c = c.weight + cnode.exact_cost
                if n.cell.status == CellStatus.Discovered:
                    if ex_c < n.exact_cost:
                        n.cell.parent = cnode.cell
                        n.exact_cost = ex_c
                        heapq.heapify(self._to_visit)
                elif n.cell.status == CellStatus.NotVisited:
                    n.exact_cost = ex_c
                    n.est_cost = self._heuristic(n.cell, self._dst_cell)
                    n.cell.status = CellStatus.Discovered
                    n.cell.parent = cnode.cell
                    heapq.heappush(self._to_visit, n)
            break

    def _cell_to_node(self, cell):
        return self._nodes[cell.row * self._graph.get_cols() + cell.col]

    def _heuristic(self, start, end):
        if not self._use_heuristic:
            return 0

        # manhattan distance
        return (DEFAULT_CELL_WEIGHT * 0.9 *
                (abs(end.row - start.row) + abs(end.col - start.col)))
