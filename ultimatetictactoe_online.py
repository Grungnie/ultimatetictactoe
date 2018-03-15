import sys
import random
from random import randint
import math
from math import sqrt
from math import log as math_log
from random import choice
import datetime
from copy import deepcopy

random.seed(10)


class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        self.silent = kwargs.get('silent', False)
        self.board = board
        self.states = []
        seconds = kwargs.get('time', 0.08)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_games_simulated = 10000
        self.max_moves = kwargs.get('max_moves', 100)
        self.draws = {}
        self.draws_multi = 0.1
        self.wins = {}
        self.losses = {}
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
        if not self.silent:
            log('games: {} time: {}'.format(games, datetime.datetime.utcnow() - begin))

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) / # + (self.draws.get((player, S), 0)*self.draws_multi)) /
             (0.1 + self.losses.get((player, S), 1) + self.wins.get((player, S), 0) + (self.draws_multi*(self.wins.get((player, S), 0)))),
             p)
            for p, S in moves_states
        )

        # Display the stats for each possible play.
        if not self.silent:
            for x in sorted(
                (100 * ((self.wins.get((player, S), 0) / # +self.draws.get((player, S), 0))
                  (0.1 + self.wins.get((player, S), 1) + self.losses.get((player, S), 1))),
                  self.wins.get((player, S), 0), # +self.draws.get((player, S), 0))
                  self.losses.get((player, S), 0), p)
                 for p, S in moves_states),
                reverse=True
            ):
                log("{3}: {0:.2f}% ({1} / {2})".format(*x))

        if not self.silent:
            log("Maximum depth searched: {}".format(self.max_depth))

        return move

    def run_simulation(self):
        # Plays out a "random" game from the current position,
        # then updates the statistics tables with the result.
        plays, wins, draws, losses = self.plays, self.wins, self.draws, self.losses

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

            if all(losses.get((player, S)) for p, S in moves_states):
                if all(losses.get((player, S)) for p, S in moves_states):
                    # If we have stats on all of the legal moves here, use them.
                    log_total = math_log(
                        sum(losses[(player, S)] for p, S in moves_states))
                    value, move, state = max(
                        ((wins[(player, S)] / ((draws[(player, S)]*self.draws_multi) + losses[(player, S)] + wins[(player, S)])) + # + ((draws[(player, S)]/2) / plays[(player, S)])) +
                         self.C * sqrt(log_total / ((draws[(player, S)]*self.draws_multi) + wins[(player, S)] + losses[(player, S)])), p, S)
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
                losses[(player, state)] = 0
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
            elif winner > 0 and winner != self.states[0][90]:
                losses[(player, state)] += 1
            elif winner < 0:
                draws[(player, state)] += 1


class Board(object):
    def start(self):
        # Returns a representation of the starting state of the game.
        self.starting_player = randint(0,1)+1
        return tuple([-1 for _ in range(9*9)] + [-1 for _ in range(9)] + [self.starting_player, -1])

    def current_player(self, state):
        # Takes the game state and returns the current player's
        # number.
        return state[90]

    def next_state(self, state, play):
        # Takes the game state, and the move to be applied.
        # Returns the new game state.
        state = list(state)
        current_player = self.current_player(state)
        state[play] = current_player

        quadrant = int(math.floor(play / 9))
        if self.sub_winner(state[(quadrant*9) : ((quadrant+1)*9)]) > 0:
            state[81+quadrant] = current_player

        if not self.plays_available(state[(quadrant*9) : ((quadrant+1)*9)]):
            state[81+quadrant] = 0

        state[91] = play

        state[90] = ((state[90] + 1) % 3)
        state[90] = 1 if state[90] == 0 else state[90]
        return tuple(state)

    def plays_available(self, state):
        for x in state:
            if x == -1:
                return True
        return False

    def legal_plays(self, state_history):
        # Takes a sequence of game states representing the full
        # game history, and returns the full list of moves that
        # are legal plays for the current player.
        state = state_history[-1]
        legal_moves = []
        for i in self.play_available(state):
            if state[i] == -1:
                legal_moves.append(i)
        return legal_moves

    def play_available(self, state):
        last_play = state[91]
        quadrant = last_play % 9

        if last_play == -1:
            return range(81)
        elif state[81 + quadrant] == -1:
            return range(quadrant*9, (quadrant+1)*9)
        else:
            available = []
            for quadrant in range(9):
                if state[81 + quadrant] == -1:
                    available = available + list(range(quadrant*9, (quadrant+1)*9))
            return available



    def winner(self, state_history):
        state = state_history[-1]
        return self.sub_winner(state[81:91])

    def sub_winner(self, state):
        # Takes a sequence of game states representing the full
        # game history.  If the game is now won, return the player
        # number.  If the game is still ongoing, return zero.  If
        # the game is tied, return a different distinct value, e.g. -1.

        winning_combos = [
            [0,1,2],
            [3,4,5],
            [6,7,8],
            [0,4,8],
            [2,4,6],
            [0,3,6],
            [1,4,7],
            [2,5,8]
        ]

        for combo in winning_combos:
            if state[combo[0]] != -1 and state[combo[0]] == state[combo[1]] and state[combo[0]] == state[combo[2]]:
                return state[combo[0]]

        return 0

    def print(self, state):
        for start in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
            row = ""
            for x in [start+x for x in [0, 1, 2, 9, 10, 11, 18, 19, 20]]:
                row += '-' if state[x] == -1 else str(state[x])
            log(row)
        log()
        for start in [x+81 for x in [0, 3, 6]]:
            row = ""
            for x in [start+x for x in [0, 1, 2, ]]:
                row += '-' if state[x] == -1 else str(state[x])
            log(row)
        log()



def log(message=None):
    if message is None:
        print(file=sys.stderr)
    else:
        print(str(message), file=sys.stderr)

def convert_to_int(row, col):
    return col + row * 9

def convert_to_row_col(num):
    return int(math.floor(num / 9)), num % 9


if __name__ == '__main__':
    board = Board()
    state = board.start()

    while True:
        options = []
        opponent_row, opponent_col = [int(i) for i in input().split()]
        valid_action_count = int(input())
        for i in range(valid_action_count):
            row, col = [int(j) for j in input().split()]
            options.append((row, col))
            log("{}, {}".format(row, col))

        # Take the middle
        if opponent_row == -1:
            print('4 4')
            continue

        # Upgrade state with play
        play = convert_to_int(opponent_row, opponent_col)
        state = board.next_state(state, play)

        monty_carlo = MonteCarlo(board)
        monty_carlo.update(state)
        play = monty_carlo.get_play()
        state = board.next_state(state, play)

        row, col = convert_to_row_col(play)

        print('{} {}'.format(row, col))



