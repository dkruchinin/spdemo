Intro
======

Shortest path finding algorithms visualised.
Inspired by the visualisation project by @qiao (http://qiao.github.io/PathFinding.js/visual/) and I decided to kill some time writing pretty similar stuff on python using pygame framework. Just for fun. I doubt this particular project can be useful, which makes it an ideal candidate for github. Kidding.


Description
======
Long story short, pick up the surface size, move source and destination points as you like, draw walls, set weights to cells (default weight of white cells is 10), select shortest path finding algorithm (A*, Dijkstra or Breadth First Search) and start the visualisation by pressing Space.


Example
=======
Create 20x30 (<Rows>x<Columns>) grid, draw some walls, set some weights and launch the Dijkstra shortest path finding algorithm:


    % ./spdemo.py 20x30
    =============================
    Help
    =============================
    Kyes:
       Space      - start,resume/pause the visualization
       c          - clean everything from the grid
       Esc        - enter to the menu mode, clean everything
                    from the grid except walls and weights
       Up/Down    - (in menu mode) swtich the value of selected option
       Left/Right - (in menu mode) switch current menu option

    Mouse:
       You can move source (green) and destination (red) points withing the grid
       using mouse. You can also draw walls and set weights to any
       non-busy cell on the grid. (note: default weight of "white"
       cells is 10)

    Menu:
      -> Algorithm: select shortest path finding algorithm
      -> Brush: switch between drawing walls and setting weights facilities
      -> Diagonals: enable/disable diagonal moves


![Sample](https://raw.github.com/dkruchinin/spdemo/master/misc/sample.jpg)
