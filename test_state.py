__author__ = 'Matthew'

from ultimatetictactoe_online import MonteCarlo
from ultimatetictactoe_online import Board

state = (-1, -1, -1, -1, 2, 2, -1, -1, -1, -1, -1, -1, 1, 1, -1, -1, -1, 2, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1, 2, -1, -1, 2, 2, 2, -1, -1, 2, 2, -1, 1, 2, -1, 2, 2, -1, -1, -1, 1, 1, 1, 2, 1, -1, -1, 1, 2, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 2, -1, 1, -1, -1, -1, 1, 2, 1, -1, 2, -1, -1, 1, -1, 2, 1, -1, -1, -1, 2, 12)

board = Board()
montycarlo = MonteCarlo(board)
montycarlo.update(state)

board.print(state)

montycarlo.get_play()