from core.cell import Cell


class GridGraph(object):
    def __init__(self, rows, cols):
        """
        Make a grid graph of "rows" rows and
        "cols" columns
        """
        self._rows = rows
        self._cols = cols
        self._grid = []
        for row in xrange(0, rows):
            line = []
            for col in xrange(0, cols):
                line.append(Cell(self, row, col))

            self._grid.append(line)

    def get_cell(self, row, col):
        return self._grid[row][col]

    def get_size(self):
        return self._rows * self._cols

    def get_rows(self):
        return self._rows

    def get_cols(self):
        return self._cols

    def cells(self):
        for row in xrange(0, self._rows):
            for col in xrange(0, self._cols):
                yield self.get_cell(row, col)
