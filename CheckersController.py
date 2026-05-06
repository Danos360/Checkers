from PySide6.QtCore import QTimer

class CheckersController:

    """
    Initialize the controller that connects the model and the view.

    :param model - The model Game logic.
    :type model: CheckersModel

    :param view - The view UI component responsible for rendering the game.
    :type view: CheckersView

    :param game_mode - "agent" for player vs agent, "1v1" for player vs player.
    :type game_mode: str
    """
    def __init__(self, model, view, game_mode="agent"):
        self.model = model
        self.view = view
        self.game_mode = game_mode
        self.agent_color = "white" if self.game_mode == "agent" else None
        self.timer = 0

        view.on_piece_click = self.select_piece
        view.on_move_click = self.player_move

        self.view.draw_board(self.model.board)

        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game_timer)
        self.game_timer.start(1000)

        self.update()

        if self.game_mode == "agent" and self.model.turn == self.agent_color:
            self.agent_move()

    """
    Refresh the board display and update the turn indicator in the UI.
    """
    def update(self):
        self.view.draw_board(self.model.board)
        self.view.turn_text.setText(f"Turn: {self.model.turn.upper()}")

    """
    Update the in-game timer every second and display it in MM:SS format.
    """
    def update_game_timer(self):
        self.timer += 1
        minutes = self.timer // 60
        seconds = self.timer % 60
        self.view.timer_text.setText(f"Time: {minutes:02d}:{seconds:02d}")

    """
    Handle user clicking on a piece.
        
    Validates that: 
    - The game ins not currently the agent turn
    - A piece exists at the provided position
    - The piece belongs to the current player 
    - The piece has valid moves
        
    If valid highlights the selected piece and its possible moves.
        
    :param row - The row index of the clicked square on the board.
    :type row: int
        
    :param col - The column index of the clicked square on the board.
    :type col: int
    """
    def select_piece(self, row, col):

        if self.game_mode == "agent" and self.model.turn == self.agent_color:
            return

        piece = self.model.get_piece(row, col)
        if not piece or piece["color"] != self.model.turn:
            return

        moves = self.model.get_moves(row, col)
        if not moves:
            return

        self.view.clear_shadows()
        self.model.selected = (row, col)
        self.view.show_moves(moves)
        self.view.draw_shadow(row, col)


    """
    Handle player move after selecting a destination squere.
    
    Validates that: 
    - A piece is currently selecred
    - The chosen move is legal
    
    Executes the move, play sounds, clears selection, continues game.
    
    :param row - The target row index where the player want to move.
    :type row: int
    
    :param col - The target column index where the player want to move.
    :type col: int
    """
    def player_move(self, row, col):
        if not self.model.selected:
            return

        old_row, old_col = self.model.selected
        valid_moves = self.model.get_moves(old_row, old_col)

        if (row, col) not in valid_moves:
            return

        became_king = self.model.move_piece(old_row, old_col, row, col)
        self.view.play_move_sound()

        if became_king:
            self.view.play_king_sound()

        self.model.selected = None
        self.view.clear_shadows()

        self.make_move()

    """
    Handle the agent move.
    
    Retrieves the best move from the model and schedules its execution.
    """
    def agent_move(self):
        move = self.model.get_greedy_nn_move(self.agent_color)
        if not move:
            return

        old_row, old_col, new_row, new_col = move

        self.view.clear_shadows()
        self.view.draw_board(self.model.board)

        QTimer.singleShot(
            1000, lambda: self.end_agent_move(old_row, old_col, new_row, new_col)
        )


    """
    Execute the agent's move.
    
    Moves the piece on the board, plays sounds, continues game.
    
    :param old_row - Original row of the piece.
    :type old_row: int
    
    :param old_col - Original column of the piece.
    :type old_col: int
    
    :param new_row - The destination row of the piece.
    :type new_row: int
    
    :param new_col - The destination column of the piece.
    :type new_col: int
    """
    def end_agent_move(self, old_row, old_col, new_row, new_col):
        self.view.clear_shadows()
        became_king = self.model.move_piece(old_row, old_col, new_row, new_col)
        self.view.play_move_sound()

        if became_king:
            self.view.play_king_sound()

        self.make_move()

    """
    Handle post-move game logic.
    
    Responsibilities:
    - Update the board UI
    - Check for a winner
    - Stop the timer
    - Play sounds
    - Show end screen
    - Trigger agent move
    
    """
    def make_move(self):
        self.update()

        winner = self.model.check_winner()
        if winner:
            self.game_timer.stop()
            minutes = self.timer // 60
            seconds = self.timer % 60
            time = f"{minutes:02d}:{seconds:02d}"
            if self.game_mode == "agent":
                if winner == self.agent_color:
                    self.view.play_lose_sound()
                else:
                    self.view.play_win_sound()
            else:
                self.view.play_win_sound()

            self.view.show_end_screen(winner, time,
                on_restart=self.restart_game,
                on_menu=self.view.back_to_menu)
            return

        if self.game_mode == "agent" and self.model.turn == self.agent_color:
            self.agent_move()

    """
    Restart the game to its initial state. (Game model, Timer, UI elements, redraws the board)
    """
    def restart_game(self):
        self.model.reset_game()
        self.view.play_start_sound()
        self.timer = 0
        self.view.timer_text.setText("Time: 00:00")
        self.game_timer.start()

        if self.view.end_screen:
            self.view.end_screen.deleteLater()
            self.view.end_screen = None

        self.update()

        if self.game_mode == "agent" and self.model.turn == self.agent_color:
            self.agent_move()