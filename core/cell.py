from core.config import DEFAULT_CELL_WEIGHT


class CellStatus:
    NotVisited = "NotVisited"
    Discovered = "Discovered"
    Visited = "Visited"
    Blocked = "Blocked"


class Cell(object):
    """
    A cell of the GraphGrid()
    """

    def __init__(self, graph, row, col):
        """
        Make a cell of a GridGraph "graph" at
        given row and column ("col").
        """
        self._graph = graph
        self.row = row
        self.col = col
        self.parent = None
        self.status = CellStatus.NotVisited
        self.weight = DEFAULT_CELL_WEIGHT

    def __str__(self):
        return ("([%s, %s], w: %s, status: %s)" %
                (self.row, self.col, self.weight, self.status))

    def neighbours(self, diagonals=False):
        """
        Get a list of neighbours of the given cell.
        If "diagonals" is Flase, get neighbours in 4-neighbourhood,
        otherwise get neighbours from 8-neighbourhood.
        NOTE: Cells with "Blocked" status are ignored.
        """
        def valid_coordinate(coord):
            return ((coord[0] >= 0 and coord[0] < self._graph.get_rows())
                    and (coord[1] >= 0 and coord[1] < self._graph.get_cols()))

        if diagonals:
            neighbours = [(self.row + rd, self.col + cd)
                          for rd in (1, 0, -1)
                          for cd in (1, 0, -1) if (rd != 0 or cd != 0)]
        else:
            neighbours = ([(self.row + rd, self.col) for rd in (-1, 1)] +
                          [(self.row, self.col + cd) for cd in (-1, 1)])

        ret = []
        for n in neighbours:
            if not valid_coordinate(n):
                continue

            cell = self._graph.get_cell(n[0], n[1])
            if cell.status == CellStatus.Blocked:
                continue

            ret.append(cell)

        return ret
