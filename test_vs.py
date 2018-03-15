__author__ = 'Matthew'

import random
import sys
import os

from ultimatetictactoe_online import Board
from ultimatetictactoe_online import log

from ultimatetictactoe_online import MonteCarlo as MonteCarloCurrent
from montecarlo_base import MonteCarlo as MonteCarloBase
from montecarlo_new import MonteCarlo as MonteCarloNew

if __name__ == '__main__':
    random.seed(12345)

    total = 0
    wins = 0
    draws = 0

    for _ in range(100):
        winner = 0
        board = Board()
        state = board.start()

        for move in range(100):
            #log(state)
            legal_plays = board.legal_plays([state])
            #log(legal_plays)
            if len(legal_plays) == 0:
                break

            if board.current_player(state) == 1:
                monty_carlo = MonteCarloCurrent(board, time=0.08, silent=True)
                monty_carlo.update(state)
                play = monty_carlo.get_play()
                state = board.next_state(state, play)
            else:
                monty_carlo = MonteCarloNew(board, time=0.08, silent=True)
                monty_carlo.update(state)
                play = monty_carlo.get_play()
                state = board.next_state(state, play)

            #log()
            #board.print(state)
            #log()

            if board.winner([state]) > 0:
                #log('### Winner is {} ###'.format(board.winner([state])))
                winner = board.winner([state])
                break

            #if total != 0:
                #log('Wins: {0}% ({1}), Draws: {2}% ({3})'.format(int((wins/total)*100), wins, int((draws/total)*100), draws))

        if winner == 0:
            draws += 1
        elif winner == 2:
            wins += 1
        total += 1

        log('Wins: {0:.2f}% ({1}), Draws: {2:.2f}% ({3})'.format(wins/total, wins, draws/total, draws))
