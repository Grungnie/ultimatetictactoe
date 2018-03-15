from random import randint, choice

class Board(object):
    def start(self):
        # Returns a representation of the starting state of the game.
        self.starting_player = randint(0,1)+1
        return tuple([-1,-1,-1,-1,-1,-1,-1,-1,-1, self.starting_player])

    def current_player(self, state):
        # Takes the game state and returns the current player's
        # number.
        return state[9]

    def next_state(self, state, play):
        # Takes the game state, and the move to be applied.
        # Returns the new game state.
        state = list(state)
        current_player = self.current_player(state)
        state[play] = current_player
        state[9] = ((state[9] + 1) % 3)
        state[9] = 1 if state[9] == 0 else state[9]
        return tuple(state)

    def legal_plays(self, state_history):
        # Takes a sequence of game states representing the full
        # game history, and returns the full list of moves that
        # are legal plays for the current player.
        state = state_history[-1]
        legal_moves = []
        for i in range(9):
            if state[i] == -1:
                legal_moves.append(i)
        return legal_moves

    def winner(self, state_history):
        # Takes a sequence of game states representing the full
        # game history.  If the game is now won, return the player
        # number.  If the game is still ongoing, return zero.  If
        # the game is tied, return a different distinct value, e.g. -1.
        state = state_history[-1]

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
        row = ''
        for i, square in enumerate(state):
            row += '-' if square == -1 else str(square)
            if ((i+1) % 3)== 0:
                print(row)
                row = ''

        print()








if __name__ == '__main__':
    board = Board()
    state = board.start()
    print(state)
    print()

    for _ in range(9):
        legal_plays = board.legal_plays([state])
        play = choice(legal_plays)
        state = board.next_state(state, play)

        board.print(state)

        if board.winner([state]):
            print(board.winner([state]))
            break