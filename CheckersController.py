class CheckersController:
    def __init__(self, model, view, game_mode="agent"):
        self.model = model
        self.view = view
        self.game_mode = game_mode
        self.agent_color = "black" if game_mode == "agent" else None

        view.on_piece_click = self.select_piece
        view.on_move_click = self.make_move

        self.view.draw_board(self.model.board)

    def select_piece(self, row, col):
        piece = self.model.get_piece(row, col)
        if not piece:
            return

        if piece != self.model.turn:
            return

        moves = self.model.get_moves(row, col)
        if not moves:
            return

        self.model.selected = (row, col)
        self.view.show_moves(moves)

    def make_move(self, row, col):
        if not self.model.selected:
            return

        old_row, old_col = self.model.selected
        piece = self.model.get_piece(old_row, old_col)
        if piece != self.model.turn:
            return

        self.model.move_piece(old_row, old_col, row, col)
        self.model.selected = None
        self.view.draw_board(self.model.board)

        if self.game_mode == "agent" and self.model.turn == self.agent_color:
            self.agent_move()

    def agent_move(self):
        move = self.model.get_agent_move(self.agent_color)
        if not move:
            return

        old_row, old_col, new_row, new_col = move
        self.model.move_piece(old_row, old_col, new_row, new_col)
        self.view.draw_board(self.model.board)


