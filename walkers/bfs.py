from core.cell import CellStatus
from walkers.basic import BasicWalker


class BFSWalker(BasicWalker):
    """
    Breadth first search algorithm.
    """

    def __init__(self, graph, src_cell, dst_cell, use_diags):
        super(BFSWalker, self).__init__(graph, src_cell, dst_cell, use_diags)
        self._queue = [self._src_cell]
        self._finished = False

    def finished(self):
        return self._finished

    def step(self):
        if len(self._queue) == 0:
            self._finished = True
        if self._finished:
            return

        while len(self._queue) > 0:
            cur_cell = self._queue.pop(0)
            cur_cell.status = CellStatus.Visited
            if cur_cell == self._dst_cell:
                self._finished = True
                return

            for c in cur_cell.neighbours(diagonals=self._use_diags):
                if c.status == CellStatus.NotVisited:
                    c.status = CellStatus.Discovered
                    c.parent = cur_cell
                    self._queue.append(c)
            break
