from math import sqrt
from math import log as math_log
from random import choice
import datetime
from copy import deepcopy
import sys

from ultimatetictactoe_online import Board

class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        self.board = board
        self.states = []
        seconds = kwargs.get('time', 0.01)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_games_simulated = 10000
        self.max_moves = kwargs.get('max_moves', 100)
        self.draws = {}
        self.draws_multi = 0.1
        self.wins = {}
        self.plays = {}
        self.C = kwargs.get('C', 5)

    def update(self, state):
        # Takes a game state, and appends it to the history.
        self.states.append(state)

    def get_play(self):
        # Causes the AI to calculate the best move from the
        # current game state and return it.
        self.max_depth = 0
        state = deepcopy(self.states[-1])
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while (datetime.datetime.utcnow() - begin < self.calculation_time) and (games < self.max_games_simulated):
            self.run_simulation()
            games += 1

        moves_states = [(p, self.board.next_state(state, p)) for p in legal]

        # Display the number of calls of `run_simulation` and the
        # time elapsed.
        log('games: {} time: {}'.format(games, datetime.datetime.utcnow() - begin))

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) / # + (self.draws.get((player, S), 0)*self.draws_multi)) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )

        # Display the stats for each possible play.
        for x in sorted(
            (100 * ((self.wins.get((player, S), 0) / # +self.draws.get((player, S), 0))
              self.plays.get((player, S), 1)),
              self.wins.get((player, S), 0), # +self.draws.get((player, S), 0))
              self.plays.get((player, S), 0), p)
             for p, S in moves_states),
            reverse=True
        ):
            log("{3}: {0:.2f}% ({1} / {2})".format(*x))

        log("Maximum depth searched: {}".format(self.max_depth))

        return move

    def run_simulation(self):
        # Plays out a "random" game from the current position,
        # then updates the statistics tables with the result.
        plays, wins, draws = self.plays, self.wins, self.draws

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        player = self.board.current_player(state)
        winner = 0

        expand = True
        for t in range(1, self.max_moves + 1):
            legal = self.board.legal_plays(states_copy)

            if len(legal) == 0:
                winner = -1
                break

            moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            if all(plays.get((player, S)) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                log_total = math_log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) + # + ((draws[(player, S)]/2) / plays[(player, S)])) +
                     self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                # Otherwise, just make an arbitrary decision.
                move, state = choice(moves_states)

            states_copy.append(state)

            # `player` here and below refers to the player
            # who moved into that particular state.
            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                draws[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner = self.board.winner(states_copy)
            if winner != 0:
                break

        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if winner > 0 and winner == self.states[0][90]:
                wins[(player, state)] += 1
            elif winner < 0:
                draws[(player, state)] += 1

def log(message):
    print(str(message), file=sys.stderr)

if __name__ == '__main__':
    total = 0
    wins = 0
    draws = 0

    for _ in range(100):
        winner = 0
        board = Board()
        state = board.start()

        for move in range(100):
            print(state)
            legal_plays = board.legal_plays([state])
            print(legal_plays)
            if len(legal_plays) == 0:
                break

            if board.current_player(state) == 1:
                monty_carlo = MonteCarlo(board, C=10, time=0.8)
                monty_carlo.update(state)
                play = monty_carlo.get_play()
                state = board.next_state(state, play)
            else:
                monty_carlo = MonteCarlo(board, C=0.5, time=0.8)
                monty_carlo.update(state)
                play = monty_carlo.get_play()
                state = board.next_state(state, play)

            print()
            board.print(state)
            print()

            if board.winner([state]) > 0:
                print('### Winner is {} ###'.format(board.winner([state])))
                winner = board.winner([state])
                break

            if total != 0:
                print('Wins: {0:.2f}% ({1}), Draws: {2:.2f}% ({3})'.format(wins/total, wins, draws/total, draws))

        if winner == 0:
            draws += 1
        elif winner == 2:
            wins += 1
        total += 1

        print('Wins: {0:.2f}% ({1}), Draws: {2:.2f}% ({3})'.format(wins/total, wins, draws/total, draws))
