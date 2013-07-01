#!/usr/bin/python

import sys
import pygame
from math import ceil
from core import *
from walkers import *

WALKERS = {
    'A*': AStarWalker,
    'Dijkstra': DijkstraWalker,
    'BFS': BFSWalker
}

BRUSHES = ['Wall', 'Weight-1', 'Weight-2', 'Weight-3']


class Ring(object):
    """
    A very simle implementation of "right", i.e. a cyclic
    linked list with one "active" item and ability to
    switch it to next or previous item.
    """
    def __init__(self, collection):
        """Build a ring upon given collection"""
        self._idx = 0
        self._items = collection

    def get(self):
        """get active item"""
        return self._items[self._idx]

    def set_active(self, val):
        self._idx = self._items.index(val)

    def items(self):
        for i in self._items:
            yield i

    def next(self):
        self._idx += 1
        if self._idx >= len(self._items):
            self._idx = -len(self._items)

    def prev(self):
        self._idx -= 1
        if self._idx < -len(self._items):
            self._idx = len(self._items) - 1


class Menu(object):
    """
    Simple pygame configuration menu.
    """

    def __init__(self, surf, menu_dict):
        """
        Make a Menu() occupying the whole surface "surf".
        "menu_dict" is a dictionary describing configuration
        menu options and their possible values.
        Dictionary format:
           {
                "Option-1": ["value1", ..., "valueN"],
                ...,
                "Option-N": [ ... ]
           }
        """
        self._surf = surf
        self._font = pygame.font.SysFont(DEFAULT_FONT, MENU_FONT_SIZE,
                                         bold=True)
        self._mdict = {}
        for k, v in menu_dict.iteritems():
            self._mdict[k] = Ring(v)

        # Menu options should be sorted alphabetically
        moptions = self._mdict.keys()
        moptions.sort()
        self._menu = Ring(moptions)

        # self._active denotes whether user switched
        # focus to the menu
        self._active = False

        # Ensure that we have enough space on the surface
        # to display the longest possible variant of the menu
        self._check_size()

    def selected_items(self):
        """Get currently selected values of all options."""
        return {opt: self._mdict[opt].get() for opt in self._menu.items()}

    def select(self, option, value):
        """Select given value of the option (make it active)"""
        self._mdict[option].set_active(value)

    def draw(self):
        """Display the menu"""
        self._surf.fill(pygame.Color(MENU_BG_COLOR))
        pygame.draw.rect(self._surf, pygame.Color(MENU_FG_COLOR),
                         (0, 0, self._surf.get_width(),
                          self._surf.get_height()), 1)

        buttons = []
        buttons_width = 0
        for opt in self._menu.items():
            button = {}
            mval = self._mdict[opt].get()

            button['text'] = "%s: %s" % (opt, mval)
            button['fg'] = MENU_FG_COLOR
            button['bg'] = MENU_BG_COLOR

            # If focus is on the given option,
            # draw it with different colors.
            if self._is_selected(opt):
                button['fg'] = MENU_SEL_FG_COLOR
                button['bg'] = MENU_SEL_BG_COLOR

            buttons_width += self._font.size(button['text'])[0]
            buttons.append(button)

        # fspace - a width of space not occupied by buttons text
        fspace = (self._surf.get_width() - buttons_width) / len(buttons)
        offset = 1
        for i in xrange(0, len(buttons)):
            button = buttons[i]
            is_last = (i == len(buttons) - 1)
            img = self._font.render(button['text'], True,
                                    pygame.Color(button['fg']),
                                    pygame.Color(button['bg']))
            if is_last:
                fspace = self._surf.get_width() - (offset + img.get_width())

            width = img.get_width() + fspace

            # Prepare a rectangle for button
            pygame.draw.rect(self._surf, pygame.Color(button['bg']),
                             (offset, 1, width, self._surf.get_height() - 2))

            # Center text in the rectangle
            self._surf.blit(img, (offset + fspace / 2,
                            (MENU_HEIGHT - MENU_FONT_SIZE) / 2))
            offset += width

            # Draw a line to visually separate one button from another
            pygame.draw.line(self._surf,
                             pygame.Color(MENU_FG_COLOR), (offset - 1, 0),
                             (offset - 1, self._surf.get_height()), 1)

    def kbd_event(self, event):
        """Handle keyboard events"""

        # When user presses ESC, spdemo sets
        # focus to the menu. Further pressing
        # of ESC switches focus back.
        if event.key == pygame.K_ESCAPE:
            self._active = not self._active
        if not self._active:
            return

        if event.key == pygame.K_RIGHT:
            self._menu.next()
        elif event.key == pygame.K_LEFT:
            self._menu.prev()
        elif event.key == pygame.K_UP:
            self._mdict[self._menu.get()].next()
        elif event.key == pygame.K_DOWN:
            self._mdict[self._menu.get()].prev()

    def is_active(self):
        return self._active

    def _is_selected(self, mkey):
        if not self._active:
            return False

        return (mkey == self._menu.get())

    def _check_size(self):
        total_width = 0
        max_height = 0
        for mkey in self._menu.items():
            maxval = max(self._mdict[mkey].items(), key=len)
            w, h = self._font.size("%s: %s" % (mkey, maxval))
            total_width += w + 4
            if h > max_height:
                max_heigh = h

        if (total_width > self._surf.get_width()
                or max_heigh > self._surf.get_height()):
            raise ValueError(("Surface is too small to fit the menu. "
                              "Min size: %dx%d" %
                              (ceil(float(total_width)/DEFAULT_SQ_SIZE),
                               ceil(float(max_heigh)/DEFAULT_SQ_SIZE))))


class Point(object):
    """
    A source or destination point of the SPdemoGrid.
    """
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return (self.row == other.row and
                self.col == other.col)


class SPDemoGrid(object):
    """
    SPDemoGrid() does all the visualization and grid
    related event handling.
    """

    def __init__(self, rows, cols, surface):
        """
        Initialise the grid of size "rows" x "cols"
        on the given surface.
        """
        self._rows = rows
        self._cols = cols

        if (surface.get_width() < (cols * DEFAULT_SQ_SIZE) or
                surface.get_height() < (rows * DEFAULT_SQ_SIZE)):
            raise ValueError("Surface is too small")

        self._surf = surface

        # Source and destination points
        self._srcp = Point(0, 0)
        self._dstp = Point(self._rows - 1, self._cols - 1)

        # The underneath graph
        self._graph = GridGraph(self._rows, self._cols)
        self._font = pygame.font.SysFont(DEFAULT_FONT, MENU_FONT_SIZE)

        # A name of current shortest path algorithm
        # (or "walker") the grid uses
        self._walker_class = DEFAULT_WALKER

        # current brush (either wall or one of predefined weights)
        self._brush = DEFAULT_BRUSH

        # denotes whether diagonal movements are possible
        self._use_diags = DEFAULT_USE_DIAGS

        self._spoint = None
        self._walker = None
        self._grid_changed = True

        # a list of points forming shortest path
        self._path = None

        # denotes whether visualization is started
        self._started = False

        # if True, user can draw walls or set weights
        # on the grid
        self._brush_enabled = False

    def set_walker(self, wname):
        assert wname in WALKERS.keys()
        self._walker_class = wname

    def set_brush(self, bname):
        assert bname in BRUSHES
        self._brush = bname

    def set_diagonals(self, dval):
        assert dval in ['On', 'Off']
        self._use_diags = (dval == 'On')

    def draw(self):
        if self._started:
            if not self._walker.finished():
                self._walker.step()
                self._grid_changed = True
            else:
                self._path = self._walker.get_path()

        self._draw_grid()
        self._draw_path()
        self._draw_points()

    def kbd_event(self, event):
        """
        Handle grid related keyboard events
        """
        if event.key == pygame.K_SPACE:
            # Pause/Resume the visualization
            self._started = not self._started
            if self._started and self._walker is None:
                # Setup the walker if it hasn't been set up yet
                src_cell = self._graph.get_cell(self._srcp.row, self._srcp.col)
                dst_cell = self._graph.get_cell(self._dstp.row, self._dstp.col)

                wclass = self._walker_class
                self._walker = WALKERS[wclass](self._graph, src_cell,
                                               dst_cell, self._use_diags)
        elif event.key == pygame.K_c:
            # Just clean everything from the grid
            self.clear()

    def mouse_event(self, event):
        """
        Handle grid related mouse event
        """
        if self._started or self._path is not None:
            # Ignore events if visualization is in progress
            # or has been finished.
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Select source or destination point to move
            self._spoint = self._point_on_mouse(event.pos)
            if self._spoint is None:
                # Or enter to the drawing mode
                self._brush_enabled = True
                self._do_brush(event.pos, click=True)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._spoint = None
            self._brush_enabled = False
        elif event.type == pygame.MOUSEMOTION:
            if self._spoint is not None:
                # Move the source/destination point to
                # another place on the grid
                row, col = self._pos_to_rowcol(event.pos)
                cell = self._graph.get_cell(row, col)
                if self._spoint is not None:
                    self._move_spoint_to_cell(cell)
            elif self._brush_enabled:
                # Or just draw walls/set weights to cells
                self._do_brush(event.pos)

    def clear(self, clear_walls=True):
        """
        Clear the grid.
        if "clear_walls" is False, everything will be
        cleaned up except walls and weights.
        """
        self._spoint = None
        self._walker = None
        self._path = None
        self._started = False
        self._brush_enabled = False

        for cell in self._graph.cells():
            cell.parent = None
            if clear_walls:
                cell.status = CellStatus.NotVisited
                cell.weight = DEFAULT_CELL_WEIGHT
            elif cell.status != CellStatus.Blocked:
                cell.status = CellStatus.NotVisited

        self._grid_changed = True

    def _draw_grid(self):
        if not self._grid_changed:
            return

        self._surf.fill(pygame.Color(GRID_BG_COLOR))
        for c in self._graph.cells():
            self._draw_square(c)

        self._grid_changed = False

    def _draw_points(self):
        def draw_point(point, color):
            x, y = self._get_square_xy(point.row, point.col)
            radius = DEFAULT_SQ_SIZE / 2
            pygame.draw.circle(self._surf, pygame.Color(color),
                               (x + radius, y + radius),
                               radius - 2)

        draw_point(self._srcp, SOURCE_POINT_COLOR)
        draw_point(self._dstp, DESTINATION_POINT_COLOR)

    def _draw_path(self):
        if self._path is None:
            return
        if len(self._path) == 1:
            # Shortest path does not exist, no luck...
            font = pygame.font.SysFont(DEFAULT_FONT, REPORT_FONT_SIZE,
                                       bold=True)
            img = font.render('Path not found', True,
                              pygame.Color(REPORT_FAIL_FONT_COLOR),
                              pygame.Color(REPORT_BG_COLOR))
            # center the text
            self._surf.blit(img, ((self._surf.get_width() - img.get_width())/2,
                            (self._surf.get_height() - img.get_height())/2))
            return

        # Draw a line connecting source and destination points
        # through the points included to "shortest path" array.
        pointlist = []
        total_weight = 0
        for c in self._path:
            left = c.col * DEFAULT_SQ_SIZE
            top = c.row * DEFAULT_SQ_SIZE
            total_weight += c.weight
            self._surf.fill(pygame.Color(PATH_CELL_COLOR),
                            (left, top, DEFAULT_SQ_SIZE - 1,
                             DEFAULT_SQ_SIZE - 1))
            pointlist.append((left + DEFAULT_SQ_SIZE / 2,
                             top + DEFAULT_SQ_SIZE / 2))

        pygame.draw.lines(self._surf, pygame.Color(PATH_LINE_COLOR),
                          False, pointlist, 3)

        # and write down some numbers
        font = pygame.font.SysFont(DEFAULT_FONT, REPORT_FONT_SIZE,
                                   bold=True)
        msg = ("Shortest path length: %s, weight %s"
               % (len(self._path), total_weight))

        img = font.render(msg, True, pygame.Color(REPORT_SUCCESS_FONT_COLOR),
                          # unfortunaly font looks very ugly if it doesn't
                          # have background :(
                          pygame.Color(REPORT_BG_COLOR))

        self._surf.blit(img, ((self._surf.get_width() - img.get_width())/2,
                              (self._surf.get_height() - img.get_height())/2))
        self._path = None

    def _do_brush(self, pos, click=False):
        if self._point_on_mouse(pos) is not None:
            return

        rc = self._pos_to_rowcol(pos)
        cell = self._graph.get_cell(rc[0], rc[1])
        if self._brush == 'Wall':
            if cell.status != CellStatus.Blocked:
                cell.status = CellStatus.Blocked
            elif click:
                cell.status = CellStatus.NotVisited

            cell.weight = DEFAULT_CELL_WEIGHT
        else:
            weight = int(self._brush[-1])
            if cell.weight != weight:
                cell.weight = weight
            elif click:
                cell.weight = DEFAULT_CELL_WEIGHT

            cell.status = CellStatus.NotVisited

        self._grid_changed = True

    def _draw_square(self, cell):
        color = self._cell_to_color(cell)
        rect = pygame.Rect((cell.col * DEFAULT_SQ_SIZE,
                            cell.row * DEFAULT_SQ_SIZE,
                            DEFAULT_SQ_SIZE, DEFAULT_SQ_SIZE))
        pygame.draw.rect(self._surf, pygame.Color(GRID_FG_COLOR), rect, 1)
        self._surf.fill(pygame.Color(color), (rect.left, rect.top,
                                              rect.width - 1, rect.height - 1))
        if cell.weight != DEFAULT_CELL_WEIGHT:
            img = self._font.render(str(cell.weight), True,
                                    pygame.Color(CELL_WEIGHT_COLOR),
                                    pygame.Color(color))
            self._surf.blit(img, (rect.left +
                            (rect.width - img.get_width())/2,
                            rect.top + (rect.height - img.get_height())/2))

    def _move_spoint_to_cell(self, cell):
        assert self._spoint is not None
        if (cell.status == CellStatus.Blocked or
                Point(cell.row, cell.col) in (self._srcp, self._dstp)):
            return

        self._spoint.row = cell.row
        self._spoint.col = cell.col
        self._grid_changed = True

    def _point_on_mouse(self, pos):
        rc = self._pos_to_rowcol(pos)
        point = Point(rc[0], rc[1])
        if point == self._srcp:
            return self._srcp
        elif point == self._dstp:
            return self._dstp
        else:
            return None

    def _pos_to_rowcol(self, pos):
        def divide_coord(coord, lim):
            return min(coord / DEFAULT_SQ_SIZE, lim - 1)

        return (divide_coord(pos[1], self._graph.get_rows()),
                divide_coord(pos[0], self._graph.get_cols()))

    def _get_square_xy(self, row, col):
        return (col * DEFAULT_SQ_SIZE, row * DEFAULT_SQ_SIZE)

    def _cell_to_color(self, cell):
        status = cell.status
        if status == CellStatus.Discovered:
            return DISCOVERED_CELL_COLOR
        elif status == CellStatus.Visited:
            return VISITED_CELL_COLOR
        elif status == CellStatus.Blocked:
            return BLOCKED_CELL_COLOR
        else:
            if cell.weight != DEFAULT_CELL_WEIGHT:
                return WEIGHTED_CELL_COLOR

            return NOTVISITED_CELL_COLOR


class SPDemo(object):
    def __init__(self, rows, cols):
        if any([i <= 0 for i in (rows, cols)]):
            raise ValueError("rows and cols must be positive")

        pygame.init()
        self._width = cols * DEFAULT_SQ_SIZE
        self._height = rows * DEFAULT_SQ_SIZE

        sysinfo = pygame.display.Info()
        orig_rows = rows
        orig_cols = cols
        if self._width > sysinfo.current_w:
            self._width = sysinfo.current_w
            cols = self._width / DEFAULT_SQ_SIZE
        if (self._height + MENU_HEIGHT) > sysinfo.current_h:
            self._height = sysinfo.current_h - MENU_HEIGHT
            rows = self._height / DEFAULT_SQ_SIZE

        if orig_rows != rows or orig_cols != cols:
            sys.stderr.write(("[WARNING] %sx%s doesn't fit your screen, "
                             "reducing to %sx%s\n" %
                            (orig_rows, orig_cols, rows, cols)))

        self._surf = pygame.display.set_mode((self._width,
                                             self._height + MENU_HEIGHT))

        menu_surf = self._surf.subsurface((0, self._height,
                                          self._width, MENU_HEIGHT))
        menu_dict = {"Algorithm": WALKERS.keys(),
                     "Brush": BRUSHES,
                     "Diagonals": ["Off", "On"]}
        self._menu = Menu(menu_surf, menu_dict)

        self._menu.select('Algorithm', DEFAULT_WALKER)
        self._menu.select('Brush', DEFAULT_BRUSH)
        self._menu.select('Diagonals', 'On')

        grid_surf = self._surf.subsurface((0, 0, self._width, self._height))
        self._grid = SPDemoGrid(rows, cols, grid_surf)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if self._menu.is_active() or event.key == pygame.K_ESCAPE:
                        if event.key == pygame.K_ESCAPE:
                            self._grid.clear(clear_walls=False)

                        self._menu.kbd_event(event)
                        if not self._menu.is_active():
                            cfg = self._menu.selected_items()
                            self._grid.set_walker(cfg['Algorithm'])
                            self._grid.set_brush(cfg['Brush'])
                            self._grid.set_diagonals(cfg['Diagonals'])
                    else:
                        self._grid.kbd_event(event)
                elif (not self._menu.is_active() and
                        event.type in (pygame.MOUSEBUTTONDOWN,
                                        pygame.MOUSEBUTTONUP,
                                        pygame.MOUSEMOTION)):
                    self._grid.mouse_event(event)

            self._grid.draw()
            self._menu.draw()
            clock.tick(DEFAULT_FPS)
            pygame.display.flip()


def usage():
    sys.stderr.write("USAGE: %s: ROWSxCOLUNMS\n" % sys.argv[0])
    sys.exit(1)


def show_help():
    # just too lazy to draw it in pygame...
    print "============================="
    print "Help"
    print "============================="
    print "Kyes:"
    print "   Space      - start,resume/pause the visualization"
    print "   c          - clean everything from the grid"
    print "   Esc        - enter to the menu mode, clean everything"
    print "                from the grid except walls and weights"
    print "   Up/Down    - (in menu mode) swtich the value of selected option"
    print "   Left/Right - (in menu mode) switch current menu option"
    print ""
    print "Mouse:"
    print ("   You can move source (%s) and destination (%s) points withing the grid"
           % (SOURCE_POINT_COLOR, DESTINATION_POINT_COLOR))
    print "   using mouse. You can also draw walls and set weights to any"
    print "   non-busy cell on the grid. (note: default weight of \"white\""
    print "   cells is %d)" % DEFAULT_CELL_WEIGHT
    print ""
    print "Menu:"
    print "  -> Algorithm: select shortest path finding algorithm"
    print "  -> Brush: switch between drawing walls and setting weights facilities"
    print "  -> Diagonals: enable/disable diagonal moves"


def main():
    if len(sys.argv) != 2:
        usage()

    try:
        rows, cols = [int(i) for i in sys.argv[1].split('x')]
    except ValueError:
        usage()

    show_help()
    try:
        spd = SPDemo(rows, cols)
        spd.run()
    except ValueError as err:
        sys.stderr.write("Error: " + str(err) + "\n")


if __name__ == '__main__':
    main()
