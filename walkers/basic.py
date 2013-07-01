class BasicWalker(object):
    """
    Basic abstract class for all "walkers"
    (i.e. shortest path finding algorithms).
    """
    def __init__(self, graph, src_cell, dst_cell, use_diags):
        """
        graph - GridGraph()
        src_cell - source Cell()
        dst_cell - destination Cell()
        use_diags - denotes whether diagonal moves are allowed
        """
        self._graph = graph
        self._src_cell = src_cell
        self._dst_cell = dst_cell
        self._use_diags = use_diags

    def finished(self):
        """
        Return True if shortest path finiding is finished
        """
        raise NotImplementedError

    def step(self):
        """Signle step of the algorithm"""
        raise NotImplementedError

    def get_path(self):
        """
        Get shortest path
        """
        n = self._dst_cell
        path = []
        while n:
            path.append(n)
            n = n.parent

        return path
