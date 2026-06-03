# Simple Chess AI using Minimax
# Install library first:
# pip install python-chess

import chess
import math

# Piece values
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# Evaluate board
def evaluate(board):
    score = 0

    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

    return score

# Minimax algorithm
def minimax(board, depth, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        max_eval = -math.inf

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()

            max_eval = max(max_eval, eval)

        return max_eval

    else:
        min_eval = math.inf

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()

            min_eval = min(min_eval, eval)

        return min_eval

# Find best move
def best_move(board, depth):
    best = None
    best_value = -math.inf

    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, False)
        board.pop()

        if value > best_value:
            best_value = value
            best = move

    return best

# Start game
board = chess.Board()

while not board.is_game_over():
    print(board)
    print("\n")

    # Player move
    user_move = input("Enter your move (example e2e4): ")

    try:
        board.push_uci(user_move)
    except:
        print("Invalid move!")
        continue

    # AI move
    ai_move = best_move(board, 2)

    if ai_move:
        board.push(ai_move)
        print("AI played:", ai_move)

print("Game Over!")