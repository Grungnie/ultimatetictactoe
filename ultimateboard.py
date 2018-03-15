from random import randint, choice
import math

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
            print(row)
        print()
        for start in [x+81 for x in [0, 3, 6]]:
            row = ""
            for x in [start+x for x in [0, 1, 2, ]]:
                row += '-' if state[x] == -1 else str(state[x])
            print(row)
        print()






if __name__ == '__main__':
    board = Board()
    state = board.start()

    for _ in range(81):
        print(state)

        legal_plays = board.legal_plays([state])
        print(legal_plays)

        if len(legal_plays) == 0:
            break

        play = choice(legal_plays)
        state = board.next_state(state, play)

        board.print(state)

        if board.winner([state]):
            print(board.winner([state]))
            break