import torch
import os

engine_path=r"stockfish\stockfish-windows-x86-64-avx2.exe"



def explain_move(fen_before, fen_after,move):
    import chess.engine

    # Initialize boards
    board_before = chess.Board(fen_before)
    board_after = chess.Board(fen_after)

    # Check if the move is valid
    if not board_before.is_legal(move):
        return "The move provided is not legal for the given board state."

    # Get the piece being moved
    piece = board_before.piece_at(move.from_square)
    if piece is None:
        return "Error: No piece at the starting square. Please check the move."
    
    target_square = move.to_square
    target_piece = board_after.piece_at(target_square)

    # Basic explanation
    explanation = f"You moved your {piece.symbol().upper()} from {chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}."
    if target_piece and target_piece.color != piece.color:
        explanation += f" You captured your opponent's {target_piece.symbol().upper()}."

    # Specific advice based on the piece type
    if piece.symbol().lower() == 'p':  # Pawn
        if chess.square_rank(target_square) == 7:
            explanation += " Your pawn is close to promotion!"
        elif chess.square_file(target_square) in [3, 4]:  # d4, e4 control
            explanation += " This move controls the center, a key strategy in chess."
    elif piece.symbol().lower() == 'n':  # Knight
        explanation += " Knights are tricky pieces. Consider whether this move creates a tactical advantage, like a fork."
    elif piece.symbol().lower() == 'r':  # Rook
        if board_after.is_open_file(move.to_square):
            explanation += " Your rook is now on an open file, where it can control more space."
    elif piece.symbol().lower() == 'q':  # Queen
        explanation += " The queen is a powerful piece; ensure you are using it effectively to control the board."
    elif piece.symbol().lower() == 'k':  # King
        if board_after.is_checkmate():
            explanation += " Checkmate! You win the game."
        else:
            explanation += " Moving the king should always ensure its safety."

    # Engine analysis
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        before_eval = engine.analyse(board_before, chess.engine.Limit(time=0.1))['score']
        after_eval = engine.analyse(board_after, chess.engine.Limit(time=0.1))['score']

        # Difference in evaluations
        difference = after_eval.relative.score() - before_eval.relative.score()
        if difference < -300:
            explanation += " Blunder detected! You've lost a significant advantage."
        elif difference > 300:
            explanation += " Brilliant move! You've gained a strong advantage."
        elif -50 < difference < 50:
            explanation += " Solid move, but there might have been a stronger option."
        else:
            explanation += " Good move!"
    except (chess.engine.EngineTerminatedError, chess.engine.EngineError, KeyError):
        explanation += " Unable to evaluate the move quality due to engine limitations."
    finally:
        engine.quit()  # Ensure the engine is always closed

    # Early game advice
    if board_after.fullmove_number <= 10:
        if piece.symbol().lower() in ['n', 'b']:
            explanation += " Developing your minor pieces (knights and bishops) early helps control the center and prepares for castling."
        elif piece.symbol().lower() == 'p' and chess.square_rank(target_square) == 4:
            explanation += " Controlling the center with pawns is a key opening principle."

    # Opening advice for first moves
    if board_after.fullmove_number == 1:
        if move.to_square == chess.E4:
            explanation += " You've played 1. e4, leading to open games like the Ruy Lopez or Sicilian Defense."
        elif move.to_square == chess.D4:
            explanation += " You've played 1. d4, leading to closed games like the Queen's Gambit or King's Indian Defense."
        elif move.to_square == chess.C4:
            explanation += " You've played 1. c4, the English Opening, often leading to positional play."

    return explanation
