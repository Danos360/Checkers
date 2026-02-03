from PySide6.QtCore import QTimer

class CheckersController:
    def __init__(self, model, view, game_mode="agent"):
        self.model = model
        self.view = view
        self.game_mode = game_mode
        self.agent_color = "black" if self.game_mode == "agent" else None
        self.timer = 0

        view.on_piece_click = self.select_piece
        view.on_move_click = self.player_move

        self.view.draw_board(self.model.board)

        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game_timer)
        self.game_timer.start(1000)

        self.update()

    def update(self):
        self.view.draw_board(self.model.board)
        self.view.turn_text.setText(f"Turn: {self.model.turn.upper()}")

    def update_game_timer(self):
        self.timer += 1
        minutes = self.timer // 60
        seconds = self.timer % 60
        self.view.timer_text.setText(f"Time: {minutes:02d}:{seconds:02d}")

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

    def end_agent_move(self, old_row, old_col, new_row, new_col):
        self.view.clear_shadows()
        became_king = self.model.move_piece(old_row, old_col, new_row, new_col)
        self.view.play_move_sound()

        if became_king:
            self.view.play_king_sound()

        self.make_move()

    def make_move(self):
        self.update()

        winner = self.model.check_winner()
        if winner:
            self.game_timer.stop()
            minutes = self.timer // 60
            seconds = self.timer % 60
            time = f"{minutes:02d}:{seconds:02d}"
            if (self.game_mode == "agent" and winner == "white") or (winner and self.game_mode == "1v1"):
                self.view.play_win_sound()
            else:
                self.view.play_lose_sound()

            self.view.show_end_screen(winner, time,
                on_restart=self.restart_game,
                on_menu=self.view.back_to_menu)
            return

        if self.game_mode == "agent" and self.model.turn == self.agent_color:
            self.agent_move()

    def restart_game(self):
        self.model.reset_game()
        self.view.play_start_sound()
        self.timer = 0
        self.view.timer_text.setText("Time: 00:00")
        self.game_timer.start()

        if self.view.end_screen:
            self.view.end_screen.deleteLater()

        self.update()